"""条件评估器

用于评估场景执行前的条件是否满足。
直接从设备的 attributes 读取属性值进行比较。
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import operator as op
import logging

from ...Scene.value_objects.condition import Condition
from .device_manager import IDeviceManager


logger = logging.getLogger(__name__)


class IConditionEvaluator(ABC):
    """条件评估器接口"""
    
    @abstractmethod
    async def evaluate_all(self, conditions: List[Condition]) -> bool:
        """评估所有条件（AND 逻辑）"""
        pass
    
    @abstractmethod
    async def evaluate_any(self, conditions: List[Condition]) -> bool:
        """评估所有条件（OR 逻辑）"""
        pass
    
    @abstractmethod
    async def evaluate_single(self, condition: Condition) -> bool:
        """评估单个条件"""
        pass


class ConditionEvaluator(IConditionEvaluator):
    """条件评估器实现
    
    直接从设备的 attributes 读取属性值进行比较。
    
    支持的操作符：
    - "==" : 相等
    - "!=" : 不等
    - ">" : 大于
    - "<" : 小于
    - ">=" : 大于等于
    - "<=" : 小于等于
    - "in" : 包含于
    - "not_in" : 不包含于
    """
    
    OPERATORS = {
        "==": op.eq,
        "!=": op.ne,
        ">": op.gt,
        "<": op.lt,
        ">=": op.ge,
        "<=": op.le,
    }
    
    def __init__(self, device_manager: IDeviceManager):
        self._device_manager = device_manager
    
    async def evaluate_all(self, conditions: List[Condition]) -> bool:
        """评估所有条件（AND 逻辑）"""
        if not conditions:
            return True
        
        for condition in conditions:
            if not await self.evaluate_single(condition):
                return False
        return True
    
    async def evaluate_any(self, conditions: List[Condition]) -> bool:
        """评估所有条件（OR 逻辑）"""
        if not conditions:
            return True
        
        for condition in conditions:
            if await self.evaluate_single(condition):
                return True
        return False
    
    async def evaluate_single(self, condition: Condition) -> bool:
        """评估单个条件
        
        从设备的 attributes 或 state 读取实际值进行比较。
        特殊处理 $system.time 用于时间范围条件。
        """
        entity_id = condition.entity_id
        attribute = condition.attribute
        
        # 特殊处理：时间条件
        if entity_id == "$system.time":
            return self._evaluate_time_condition(condition)
        
        # 获取实际值
        if attribute == "state":
            # 主状态
            actual_value = await self._device_manager.get_device_state(entity_id)
        else:
            # 从 attributes 读取
            attributes = await self._device_manager.get_device_attributes(entity_id)
            actual_value = attributes.get(attribute)
        
        if actual_value is None:
            logger.debug(f"条件评估: {entity_id}.{attribute} 不存在")
            return False
        
        # 执行比较
        expected_value = condition.value
        result = self._compare(actual_value, condition.operator, expected_value)
        
        print(f"DEBUG: Condition Evaluation: {entity_id}.{attribute} {condition.operator} {expected_value}")
        print(f"DEBUG:   Actual value: {actual_value} (type: {type(actual_value)})")
        print(f"DEBUG:   Result: {result}")
        
        return result
    
    def _evaluate_time_condition(self, condition: Condition) -> bool:
        """评估时间条件
        
        检查当前时间是否在指定范围内。
        """
        from datetime import datetime
        
        if condition.operator != "in_range":
            logger.warning(f"不支持的时间条件操作符: {condition.operator}")
            return False
        
        time_value = condition.value
        if not isinstance(time_value, dict):
            logger.warning(f"时间条件值格式错误: {time_value}")
            return False
        
        now = datetime.now().time()
        after_str = time_value.get("after")
        before_str = time_value.get("before")
        
        try:
            if after_str:
                after_time = datetime.strptime(after_str, "%H:%M").time()
                if now < after_time:
                    print(f"DEBUG: Time condition failed: {now} < after {after_time}")
                    return False
            
            if before_str:
                before_time = datetime.strptime(before_str, "%H:%M").time()
                if now > before_time:
                    print(f"DEBUG: Time condition failed: {now} > before {before_time}")
                    return False
            
            print(f"DEBUG: Time condition satisfied: {after_str} <= {now} <= {before_str}")
            return True
        except ValueError as e:
            print(f"DEBUG: Time parse error: {e}")
            logger.error(f"时间格式解析错误: {e}")
            return False
    
    def _compare(self, actual: Any, operator: str, expected: Any) -> bool:
        """执行比较操作"""
        if actual is None:
            return False
        
        # 处理 in 和 not_in
        if operator == "in":
            return actual in expected if isinstance(expected, (list, tuple, set)) else str(actual) in str(expected)
        
        if operator == "not_in":
            return actual not in expected if isinstance(expected, (list, tuple, set)) else str(actual) not in str(expected)
        
        # 标准比较
        compare_func = self.OPERATORS.get(operator)
        if compare_func is None:
            raise ValueError(f"不支持的操作符: {operator}")
        
        # 类型转换
        try:
            if isinstance(expected, (int, float)) and isinstance(actual, str):
                actual = float(actual)
            elif isinstance(actual, (int, float)) and isinstance(expected, str):
                expected = float(expected)
        except (ValueError, TypeError):
            pass
        
        return compare_func(actual, expected)
