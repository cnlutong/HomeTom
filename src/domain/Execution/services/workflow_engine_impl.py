"""工作流引擎实现

MVP 阶段实现顺序执行动作的工作流引擎。
后续可扩展支持并行执行、条件分支等高级特性。
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .workflow_engine import IWorkflowEngine
from .device_manager import IDeviceManager, CommandResult
from .condition_evaluator import IConditionEvaluator
from ..aggregates.execution_aggregate import ExecutionAggregate
from ..value_objects.execution_result import ExecutionResult
from ...Scene.value_objects.scene_definition import SceneDefinition
from ...Scene.value_objects.action import Action, ActionType


logger = logging.getLogger(__name__)


class WorkflowEngine(IWorkflowEngine):
    """工作流引擎实现
    
    负责执行场景定义中的动作序列。
    
    MVP 阶段特性：
    - 顺序执行所有动作
    - 条件评估（可选）
    - 动作执行失败时可选择继续或终止
    - 详细的执行日志
    
    后续扩展：
    - 并行执行
    - 条件分支
    - 循环
    - 子场景调用
    """
    
    def __init__(
        self,
        device_manager: IDeviceManager,
        condition_evaluator: Optional[IConditionEvaluator] = None,
        stop_on_error: bool = True
    ):
        """初始化工作流引擎
        
        Args:
            device_manager: 设备管理器，用于执行设备命令
            condition_evaluator: 条件评估器，用于评估执行前置条件
            stop_on_error: 遇到错误时是否停止执行
        """
        self._device_manager = device_manager
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
        
        try:
            # 评估前置条件
            if definition.conditions and self._condition_evaluator:
                conditions_met = await self._condition_evaluator.evaluate_all(
                    definition.conditions
                )
                if not conditions_met:
                    logger.info(f"条件不满足，跳过执行: {execution.execution_id}")
                    execution.succeed({"skipped": True, "reason": "conditions_not_met"})
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
                execution.fail(
                    error_message=f"部分动作执行失败: {'; '.join(error_messages)}",
                    error_code="ACTION_FAILED"
                )
            else:
                execution.succeed({
                    "total_actions": len(definition.actions),
                    "executed_actions": len(action_results),
                    "results": action_results
                })
            
        except Exception as e:
            logger.exception(f"工作流执行异常: {execution.execution_id}")
            execution.fail(
                error_message=str(e),
                error_code="WORKFLOW_EXCEPTION"
            )
    
    async def execute_action(
        self,
        execution: ExecutionAggregate,
        action: Action,
        step_number: int
    ) -> Dict[str, Any]:
        """执行单个动作
        
        Args:
            execution: 执行聚合根
            action: 动作对象
            step_number: 步骤序号
            
        Returns:
            执行结果字典
        """
        start_time = datetime.utcnow()
        
        # 记录执行日志
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
                logger.info(
                    f"动作执行成功: step={step_number}, elapsed={elapsed_ms:.2f}ms"
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
                logger.warning(
                    f"动作执行失败: step={step_number}, error={result.message}"
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
        """根据动作类型执行
        
        Args:
            action: 动作对象
            
        Returns:
            命令执行结果
        """
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
        """执行设备控制动作
        
        通过设备管理器调用设备方法
        """
        return await self._device_manager.execute_command(
            entity_id=action.target,
            command=action.command,
            params=action.parameters
        )
    
    async def _execute_scene_call(self, action: Action) -> CommandResult:
        """执行子场景调用动作（MVP 阶段暂不支持）"""
        # TODO: 实现子场景调用
        # 需要注入场景仓储和递归调用工作流引擎
        return CommandResult.failed(
            entity_id=action.target,
            command=action.command,
            message="子场景调用功能暂未实现"
        )
