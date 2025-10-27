"""
条件评估器（策略模式）
支持多种条件类型的评估
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, time


class Condition(ABC):
    """条件基类（策略接口）"""
    
    @abstractmethod
    async def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        评估条件
        
        Args:
            context: 评估上下文（包含设备状态等）
            
        Returns:
            bool: 条件是否满足
        """
        pass


class DeviceStateCondition(Condition):
    """设备状态条件"""
    
    def __init__(self, device_id: str, condition: Dict[str, Any]):
        self.device_id = device_id
        self.operator = condition.get("operator", "eq")
        self.attribute = condition.get("attribute", "state")
        self.value = condition.get("value")
    
    async def evaluate(self, context: Dict[str, Any]) -> bool:
        """评估设备状态条件"""
        device_state = context.get("device_states", {}).get(self.device_id)
        
        if not device_state:
            return False
        
        # 获取属性值
        if self.attribute == "state":
            actual_value = device_state.state
        else:
            actual_value = device_state.attributes.get(self.attribute)
        
        if actual_value is None:
            return False
        
        # 根据运算符比较
        return self._compare(actual_value, self.value, self.operator)
    
    @staticmethod
    def _compare(actual: Any, expected: Any, operator: str) -> bool:
        """比较值"""
        if operator == "eq":
            return actual == expected
        elif operator == "ne":
            return actual != expected
        elif operator == "gt":
            return actual > expected
        elif operator == "ge":
            return actual >= expected
        elif operator == "lt":
            return actual < expected
        elif operator == "le":
            return actual <= expected
        else:
            return False


class TimeRangeCondition(Condition):
    """时间范围条件"""
    
    def __init__(self, start: str, end: str):
        self.start = datetime.strptime(start, "%H:%M").time()
        self.end = datetime.strptime(end, "%H:%M").time()
    
    async def evaluate(self, context: Dict[str, Any]) -> bool:
        """评估时间范围条件"""
        now = datetime.now().time()
        
        if self.start <= self.end:
            # 同一天的时间范围（例如 09:00 - 17:00）
            return self.start <= now <= self.end
        else:
            # 跨天的时间范围（例如 22:00 - 06:00）
            return now >= self.start or now <= self.end


class ConditionGroup(Condition):
    """条件组（支持 AND/OR）"""
    
    def __init__(self, operator: str, items: list):
        self.operator = operator.lower()
        self.conditions = items
    
    async def evaluate(self, context: Dict[str, Any]) -> bool:
        """评估条件组"""
        results = []
        
        for cond_data in self.conditions:
            condition = ConditionFactory.create(cond_data)
            result = await condition.evaluate(context)
            results.append(result)
        
        if self.operator == "and":
            return all(results)
        elif self.operator == "or":
            return any(results)
        else:
            return False


class ConditionFactory:
    """条件工厂（工厂模式）"""
    
    _registry: Dict[str, type] = {
        "device_state": DeviceStateCondition,
        "time_range": TimeRangeCondition,
    }
    
    @classmethod
    def create(cls, condition_data: Dict[str, Any]) -> Condition:
        """
        创建条件实例
        
        Args:
            condition_data: 条件定义数据
            
        Returns:
            Condition: 条件实例
        """
        cond_type = condition_data.get("type")
        
        if cond_type not in cls._registry:
            raise ValueError(f"Unknown condition type: {cond_type}")
        
        condition_class = cls._registry[cond_type]
        
        # 根据不同类型创建实例
        if cond_type == "device_state":
            return condition_class(
                device_id=condition_data["device_id"],
                condition=condition_data["condition"]
            )
        elif cond_type == "time_range":
            return condition_class(
                start=condition_data["start"],
                end=condition_data["end"]
            )
        
        raise ValueError(f"Cannot create condition for type: {cond_type}")
    
    @classmethod
    def register(cls, cond_type: str, condition_class: type):
        """注册新的条件类型（扩展点）"""
        cls._registry[cond_type] = condition_class


class ConditionEvaluator:
    """条件评估器（外观模式）"""
    
    async def evaluate(
        self,
        condition_data: Optional[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> bool:
        """
        评估条件
        
        Args:
            condition_data: 条件定义
            context: 评估上下文
            
        Returns:
            bool: 条件是否满足
        """
        if not condition_data:
            return True  # 无条件时默认通过
        
        # 检查是否为条件组
        if "operator" in condition_data and "items" in condition_data:
            condition = ConditionGroup(
                operator=condition_data["operator"],
                items=condition_data["items"]
            )
        else:
            condition = ConditionFactory.create(condition_data)
        
        return await condition.evaluate(context)

