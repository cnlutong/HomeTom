"""
场景执行器
负责执行场景中的动作序列
"""
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from domain.entities.scene import Scene
from exceptions import SceneExecutionError


class ExecutionResult:
    """执行结果"""
    
    def __init__(
        self,
        status: str,
        scene_id: str,
        message: Optional[str] = None,
        executed_at: datetime = None
    ):
        self.status = status  # success, failed, skipped
        self.scene_id = scene_id
        self.message = message
        self.executed_at = executed_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "scene_id": self.scene_id,
            "message": self.message,
            "executed_at": self.executed_at.isoformat()
        }


class SceneExecutor:
    """场景执行器"""
    
    def __init__(self, hal_client, condition_evaluator, state_manager):
        self.hal_client = hal_client
        self.condition_evaluator = condition_evaluator
        self.state_manager = state_manager
    
    async def execute_scene(
        self,
        scene: Scene,
        triggered_by: str = "auto"
    ) -> ExecutionResult:
        """
        执行场景
        
        Args:
            scene: 场景实体
            triggered_by: 触发来源（auto, manual, user_id）
            
        Returns:
            ExecutionResult: 执行结果
        """
        try:
            # 1. 准备评估上下文
            context = await self._prepare_context(scene)
            
            # 2. 评估条件
            condition_met = await self.condition_evaluator.evaluate(
                scene.definition.conditions.model_dump() if scene.definition.conditions else None,
                context
            )
            
            if not condition_met:
                return ExecutionResult(
                    status="skipped",
                    scene_id=scene.id,
                    message="Conditions not met"
                )
            
            # 3. 执行动作序列
            for action in scene.definition.actions:
                await self._execute_action(action)
            
            return ExecutionResult(
                status="success",
                scene_id=scene.id,
                message=f"Executed {len(scene.definition.actions)} actions"
            )
            
        except Exception as e:
            return ExecutionResult(
                status="failed",
                scene_id=scene.id,
                message=str(e)
            )
    
    async def _prepare_context(self, scene: Scene) -> Dict[str, Any]:
        """准备评估上下文"""
        # 获取所有相关设备的状态
        device_states = {}
        
        # 从场景定义中提取需要的设备 ID
        device_ids = self._extract_device_ids(scene)
        
        for device_id in device_ids:
            state = await self.state_manager.get_state(device_id)
            if state:
                device_states[device_id] = state
        
        return {
            "device_states": device_states,
            "scene_id": scene.id,
            "current_time": datetime.now()
        }
    
    def _extract_device_ids(self, scene: Scene) -> set:
        """从场景定义中提取设备 ID"""
        device_ids = set()
        
        # 从触发器中提取
        for trigger in scene.definition.triggers:
            if trigger.get("type") == "device_state":
                device_ids.add(trigger["device_id"])
        
        # 从条件中提取
        if scene.definition.conditions:
            for item in scene.definition.conditions.items:
                if item.get("type") == "device_state":
                    device_ids.add(item["device_id"])
        
        # 从动作中提取
        for action in scene.definition.actions:
            if action.get("type") == "device_control":
                device_ids.add(action["device_id"])
        
        return device_ids
    
    async def _execute_action(self, action: Dict[str, Any]) -> None:
        """执行单个动作"""
        action_type = action.get("type")
        
        if action_type == "device_control":
            await self._execute_device_control(action)
        elif action_type == "delay":
            await self._execute_delay(action)
        else:
            raise SceneExecutionError("unknown", f"Unknown action type: {action_type}")
    
    async def _execute_device_control(self, action: Dict[str, Any]) -> None:
        """执行设备控制动作"""
        device_id = action["device_id"]
        command = action["command"]
        
        try:
            await self.hal_client.control_device(device_id, command)
        except Exception as e:
            raise SceneExecutionError(
                "device_control",
                f"Failed to control device {device_id}: {e}"
            )
    
    async def _execute_delay(self, action: Dict[str, Any]) -> None:
        """执行延迟动作"""
        seconds = action.get("seconds", 0)
        await asyncio.sleep(seconds)

