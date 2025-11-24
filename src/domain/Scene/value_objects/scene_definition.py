"""场景定义值对象"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from .trigger import Trigger
from .condition import Condition
from .action import Action


@dataclass(frozen=True)
class SceneDefinition:
    """场景定义值对象
    
    封装场景的完整定义，包括触发器、条件和动作
    """
    triggers: List[Trigger]  # 触发器列表
    conditions: Optional[List[Condition]] = None  # 条件列表（可选）
    actions: List[Action] = None  # 动作列表
    
    def __post_init__(self):
        """验证场景定义"""
        if not self.triggers:
            raise ValueError("场景必须至少有一个触发器")
        if not self.actions:
            raise ValueError("场景必须至少有一个动作")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于JSON序列化）"""
        result = {
            "triggers": [t.to_dict() for t in self.triggers],
            "actions": [a.to_dict() for a in self.actions]
        }
        if self.conditions:
            result["conditions"] = [c.to_dict() for c in self.conditions]
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneDefinition":
        """从字典创建（用于JSON反序列化）"""
        triggers = [Trigger.from_dict(t) for t in data["triggers"]]
        actions = [Action.from_dict(a) for a in data["actions"]]
        conditions = None
        if "conditions" in data and data["conditions"]:
            conditions = [Condition.from_dict(c) for c in data["conditions"]]
        
        return cls(
            triggers=triggers,
            conditions=conditions,
            actions=actions
        )
    
    def get_referenced_scenes(self) -> List[str]:
        """获取引用的子场景ID列表"""
        scene_ids = []
        for action in self.actions:
            if action.type.value == "scene_call":
                scene_ids.append(action.target)
        return scene_ids
    
    def get_referenced_devices(self) -> List[str]:
        """获取引用的设备实体ID列表"""
        device_ids = set()
        
        # 从触发器中提取
        for trigger in self.triggers:
            if trigger.type.value == "device_event":
                device_ids.add(trigger.config.get("entity_id"))
        
        # 从条件中提取
        if self.conditions:
            for condition in self.conditions:
                device_ids.add(condition.entity_id)
        
        # 从动作中提取
        for action in self.actions:
            if action.type.value == "device_control":
                device_ids.add(action.target)
        
        return list(device_ids)

