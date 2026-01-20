"""触发器值对象"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime


class TriggerType(Enum):
    """触发器类型"""
    MANUAL = "manual"  # 手动触发
    TIMER = "timer"  # 定时器触发
    ALWAYS_ON = "always_on"  # 常开触发（类似 bypass）
    DEVICE_EVENT = "device_event"  # 设备事件触发


@dataclass(frozen=True)
class Trigger:
    """触发器值对象
    
    定义场景的触发条件
    """
    type: TriggerType
    config: Dict[str, Any]  # 触发器配置，根据类型不同而不同
    
    def __post_init__(self):
        """验证触发器数据"""
        if not isinstance(self.type, TriggerType):
            raise ValueError("触发器类型必须是TriggerType枚举")
        if not isinstance(self.config, dict):
            raise ValueError("触发器配置必须是字典")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "type": self.type.value,
            "config": self.config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Trigger":
        """从字典创建"""
        return cls(
            type=TriggerType(data["type"]),
            config=data.get("config", {})
        )
    
    @classmethod
    def create_manual(cls) -> "Trigger":
        """创建手动触发器"""
        return cls(
            type=TriggerType.MANUAL,
            config={}
        )
    
    @classmethod
    def create_timer(
        cls, 
        schedule: str,
        days: Optional[List[int]] = None  # For weekly triggers (0=Mon, 1=Tue, ..., 6=Sun)
    ) -> "Trigger":
        """创建定时器触发器
        
        Args:
            schedule: 时间表达式（如 "08:00" 或 cron 表达式）
            days: 可选，每周执行的天数列表（0=周一，1=周二，...，6=周日）
                  如果为 None 或空，则表示每天执行
        """
        config = {"schedule": schedule}
        if days:
            config["days"] = days
        return cls(
            type=TriggerType.TIMER,
            config=config
        )
    
    @classmethod
    def create_always_on(cls) -> "Trigger":
        """创建常开触发器
        
        该触发器始终处于激活状态，类似 bypass
        """
        return cls(
            type=TriggerType.ALWAYS_ON,
            config={}
        )
    
    @classmethod
    def create_device_event(
        cls,
        entity_id: str,
        event_type: str,
        condition: Optional[Dict[str, Any]] = None
    ) -> "Trigger":
        """创建设备事件触发器
        
        Args:
            entity_id: 设备实体ID
            event_type: 事件类型（如 "state_changed", "turned_on"）
            condition: 触发条件（如 {"new_state": "on"}）
        """
        config = {
            "entity_id": entity_id,
            "event_type": event_type
        }
        if condition:
            config["condition"] = condition
        
        return cls(
            type=TriggerType.DEVICE_EVENT,
            config=config
        )

