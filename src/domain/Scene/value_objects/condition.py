"""条件值对象"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List


@dataclass(frozen=True)
class Condition:
    """条件值对象
    
    定义场景执行的条件判断
    """
    entity_id: str  # 设备实体ID
    attribute: str  # 属性名（如 "state", "brightness"）
    operator: str  # 操作符（如 "==", ">", "<", "in"）
    value: Any  # 比较值
    
    def __post_init__(self):
        """验证条件数据"""
        if not self.entity_id:
            raise ValueError("实体ID不能为空")
        if not self.attribute:
            raise ValueError("属性名不能为空")
        if not self.operator:
            raise ValueError("操作符不能为空")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "entity_id": self.entity_id,
            "attribute": self.attribute,
            "operator": self.operator,
            "value": self.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Condition":
        """从字典创建"""
        return cls(
            entity_id=data["entity_id"],
            attribute=data["attribute"],
            operator=data["operator"],
            value=data["value"]
        )
    
    @classmethod
    def create_state_equals(cls, entity_id: str, state: str) -> "Condition":
        """创建状态等于条件"""
        return cls(
            entity_id=entity_id,
            attribute="state",
            operator="==",
            value=state
        )
    
    @classmethod
    def create_attribute_equals(
        cls,
        entity_id: str,
        attribute: str,
        value: Any
    ) -> "Condition":
        """创建属性等于条件"""
        return cls(
            entity_id=entity_id,
            attribute=attribute,
            operator="==",
            value=value
        )

    @classmethod
    def create_time_range(
        cls,
        after: Optional[str] = None,
        before: Optional[str] = None
    ) -> "Condition":
        """创建时间范围条件
        
        Args:
            after: 起始时间 (HH:MM 格式，如 "08:00")
            before: 结束时间 (HH:MM 格式，如 "22:00")
        """
        time_value = {}
        if after:
            time_value["after"] = after
        if before:
            time_value["before"] = before
        
        return cls(
            entity_id="$system.time",
            attribute="current",
            operator="in_range",
            value=time_value
        )

