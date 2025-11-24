"""动作值对象"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional


class ActionType(Enum):
    """动作类型"""
    DEVICE_CONTROL = "device_control"  # 设备控制
    SCENE_CALL = "scene_call"  # 子场景调用（MVP阶段暂不支持）


@dataclass(frozen=True)
class Action:
    """动作值对象
    
    定义场景执行的具体动作
    """
    type: ActionType
    target: str  # 目标（设备entity_id或场景ID）
    command: str  # 命令（如 "turn_on", "set_brightness"）
    parameters: Optional[Dict[str, Any]] = None  # 命令参数
    
    def __post_init__(self):
        """验证动作数据"""
        if not isinstance(self.type, ActionType):
            raise ValueError("动作类型必须是ActionType枚举")
        if not self.target:
            raise ValueError("目标不能为空")
        if not self.command:
            raise ValueError("命令不能为空")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "type": self.type.value,
            "target": self.target,
            "command": self.command
        }
        if self.parameters:
            result["parameters"] = self.parameters
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Action":
        """从字典创建"""
        return cls(
            type=ActionType(data["type"]),
            target=data["target"],
            command=data["command"],
            parameters=data.get("parameters")
        )
    
    @classmethod
    def create_device_control(
        cls,
        entity_id: str,
        command: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> "Action":
        """创建设备控制动作"""
        return cls(
            type=ActionType.DEVICE_CONTROL,
            target=entity_id,
            command=command,
            parameters=parameters
        )
    
    @classmethod
    def create_scene_call(cls, scene_id: str) -> "Action":
        """创建子场景调用动作（MVP阶段暂不支持）"""
        return cls(
            type=ActionType.SCENE_CALL,
            target=scene_id,
            command="execute",
            parameters=None
        )

