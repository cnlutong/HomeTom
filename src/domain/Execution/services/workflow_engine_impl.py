"""工作流引擎实现

MVP 阶段实现顺序执行动作的工作流引擎。
执行过程中发布领域事件到事件总线。
"""

import logging
from typing import Dict, Any, Optional, List, Protocol, runtime_checkable
from datetime import datetime

from .workflow_engine import IWorkflowEngine
from .device_manager import IDeviceManager, CommandResult
from .condition_evaluator import IConditionEvaluator
from ..aggregates.execution_aggregate import ExecutionAggregate
from ..events.execution_started import ExecutionStarted
from ..events.execution_succeeded import ExecutionSucceeded
from ..events.execution_failed import ExecutionFailed
from ..events.action_executed import ActionExecuted
from ...Scene.value_objects.scene_definition import SceneDefinition
from ...Scene.value_objects.action import Action, ActionType


logger = logging.getLogger(__name__)


@runtime_checkable
class EventPublisher(Protocol):
    """事件发布者协议 - 用于类型提示，符合 IEventBus 接口"""
    async def publish(self, event: object) -> None: ...


class WorkflowEngine(IWorkflowEngine):
    """工作流引擎实现
    
    负责执行场景定义中的动作序列，并发布执行事件到事件总线。
    
    MVP 阶段特性：
    - 顺序执行所有动作
    - 条件评估（可选）
    - 执行事件发布（开始、成功、失败）
    - 动作执行失败时可选择继续或终止
    """
    
    def __init__(
        self,
        device_manager: IDeviceManager,
        event_bus: Optional[EventPublisher] = None,
        condition_evaluator: Optional[IConditionEvaluator] = None,
        stop_on_error: bool = True
    ):

        """初始化工作流引擎
        
        Args:
            device_manager: 设备管理器，用于执行设备命令
            event_bus: 事件总线，用于发布执行事件
            condition_evaluator: 条件评估器，用于评估执行前置条件
            stop_on_error: 遇到错误时是否停止执行
        """
        self._device_manager = device_manager
        self._event_bus = event_bus
        self._condition_evaluator = condition_evaluator
        self._stop_on_error = stop_on_error
    
    async def execute(
        self,
        execution: ExecutionAggregate,
        definition: SceneDefinition
    ) -> None:
        """执行工作流
        
        Args:
            execution: 执行聚合根
            definition: 场景定义
        """
        logger.info(
            f"开始执行工作流: execution_id={execution.execution_id}, "
            f"scene_id={execution.context.scene_id}"
        )
        
        execution.start()
        
        # 发布执行开始事件
        await self._publish_event(ExecutionStarted(
            execution_id=execution.execution_id,
            scene_id=execution.context.scene_id,
            scene_version=execution.context.scene_version,
            occurred_at=datetime.utcnow()
        ))
        
        try:
            # 评估前置条件
            if definition.conditions and self._condition_evaluator:
                conditions_met = await self._condition_evaluator.evaluate_all(
                    definition.conditions
                )
                if not conditions_met:
                    logger.info(f"条件不满足，跳过执行: {execution.execution_id}")
                    execution.succeed({"skipped": True, "reason": "conditions_not_met"})
                    await self._publish_succeeded_event(execution)
                    return
            
            # 顺序执行所有动作
            action_results: List[Dict[str, Any]] = []
            failed_actions: List[Dict[str, Any]] = []
            
            for step_number, action in enumerate(definition.actions, start=1):
                result = await self.execute_action(execution, action, step_number)
                action_results.append(result)
                
                if not result.get("success", False):
                    failed_actions.append(result)
                    if self._stop_on_error:
                        logger.error(
                            f"动作执行失败，停止工作流: step={step_number}, "
                            f"error={result.get('error')}"
                        )
                        break
            
            # 判断整体执行结果
            if failed_actions:
                error_messages = [f.get("error", "Unknown error") for f in failed_actions]
                error_msg = f"部分动作执行失败: {'; '.join(error_messages)}"
                execution.fail(error_message=error_msg, error_code="ACTION_FAILED")
                await self._publish_failed_event(execution, error_msg, "ACTION_FAILED")
            else:
                execution.succeed({
                    "total_actions": len(definition.actions),
                    "executed_actions": len(action_results),
                    "results": action_results
                })
                await self._publish_succeeded_event(execution)
            
        except Exception as e:
            logger.exception(f"工作流执行异常: {execution.execution_id}")
            error_msg = str(e)
            execution.fail(error_message=error_msg, error_code="WORKFLOW_EXCEPTION")
            await self._publish_failed_event(execution, error_msg, "WORKFLOW_EXCEPTION")
    
    async def execute_action(
        self,
        execution: ExecutionAggregate,
        action: Action,
        step_number: int
    ) -> Dict[str, Any]:
        """执行单个动作并发布事件"""
        start_time = datetime.utcnow()
        
        execution.add_log(
            step_number=step_number,
            action_type=action.type.value,
            target=action.target,
            command=action.command,
            parameters=action.parameters
        )
        
        logger.info(
            f"执行动作: step={step_number}, type={action.type.value}, "
            f"target={action.target}, command={action.command}"
        )
        
        try:
            result = await self._execute_action_by_type(action)
            elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            if result.success:
                logger.info(f"动作执行成功: step={step_number}, elapsed={elapsed_ms:.2f}ms")
                
                # 发布动作执行成功事件
                await self._publish_action_event(
                    execution, action, step_number, elapsed_ms, True, None
                )
                
                return {
                    "success": True,
                    "step": step_number,
                    "action_type": action.type.value,
                    "target": action.target,
                    "command": action.command,
                    "elapsed_ms": elapsed_ms,
                    "response": result.data
                }
            else:
                logger.warning(f"动作执行失败: step={step_number}, error={result.message}")
                
                # 发布动作执行失败事件
                await self._publish_action_event(
                    execution, action, step_number, elapsed_ms, False, result.message
                )
                
                return {
                    "success": False,
                    "step": step_number,
                    "action_type": action.type.value,
                    "target": action.target,
                    "command": action.command,
                    "elapsed_ms": elapsed_ms,
                    "error": result.message
                }
                
        except Exception as e:
            elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.exception(f"动作执行异常: step={step_number}")
            
            # 发布动作执行异常事件
            await self._publish_action_event(
                execution, action, step_number, elapsed_ms, False, str(e)
            )
            
            return {
                "success": False,
                "step": step_number,
                "action_type": action.type.value,
                "target": action.target,
                "command": action.command,
                "elapsed_ms": elapsed_ms,
                "error": str(e)
            }

    
    async def _execute_action_by_type(self, action: Action) -> CommandResult:
        """根据动作类型执行"""
        if action.type == ActionType.DEVICE_CONTROL:
            return await self._execute_device_control(action)
        elif action.type == ActionType.SCENE_CALL:
            return await self._execute_scene_call(action)
        else:
            return CommandResult.failed(
                entity_id=action.target,
                command=action.command,
                message=f"不支持的动作类型: {action.type.value}"
            )
    
    async def _execute_device_control(self, action: Action) -> CommandResult:
        """执行设备控制动作"""
        return await self._device_manager.execute_command(
            entity_id=action.target,
            command=action.command,
            params=action.parameters
        )
    
    async def _execute_scene_call(self, action: Action) -> CommandResult:
        """执行子场景调用动作（MVP 阶段暂不支持）"""
        return CommandResult.failed(
            entity_id=action.target,
            command=action.command,
            message="子场景调用功能暂未实现"
        )
    
    # === 事件发布辅助方法 ===
    
    async def _publish_event(self, event: object) -> None:
        """发布事件到事件总线"""
        if self._event_bus:
            try:
                await self._event_bus.publish(event)
                logger.debug(f"事件发布成功: {type(event).__name__}")
            except Exception as e:
                logger.error(f"事件发布失败: {e}")
    
    async def _publish_succeeded_event(self, execution: ExecutionAggregate) -> None:
        """发布执行成功事件"""
        await self._publish_event(ExecutionSucceeded(
            execution_id=execution.execution_id,
            scene_id=execution.context.scene_id,
            occurred_at=datetime.utcnow()
        ))
    
    async def _publish_failed_event(
        self,
        execution: ExecutionAggregate,
        error_message: str,
        error_code: Optional[str] = None
    ) -> None:
        """发布执行失败事件"""
        await self._publish_event(ExecutionFailed(
            execution_id=execution.execution_id,
            scene_id=execution.context.scene_id,
            error_message=error_message,
            error_code=error_code,
            occurred_at=datetime.utcnow()
        ))
    
    async def _publish_action_event(
        self,
        execution: ExecutionAggregate,
        action: Action,
        step_number: int,
        elapsed_ms: float,
        success: bool,
        error_message: Optional[str]
    ) -> None:
        """发布动作执行事件
        
        每个动作执行后发布，如灯开、灯关、设置温度等。
        """
        await self._publish_event(ActionExecuted(
            execution_id=execution.execution_id,
            scene_id=execution.context.scene_id,
            step_number=step_number,
            entity_id=action.target,
            command=action.command,
            success=success,
            elapsed_ms=elapsed_ms,
            parameters=action.parameters,
            error_message=error_message,
            occurred_at=datetime.utcnow()
        ))
