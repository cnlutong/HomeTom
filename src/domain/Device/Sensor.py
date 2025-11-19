from abc import ABC, abstractmethod
from .BaseDevice import BaseDevice


class Sensor(BaseDevice):
    """传感类设备基类 - 只负责读取数据，通常是只读的"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._value = None
        self._unit = None
    
    def get_value(self):
        """获取传感器数值"""
        return self._value
    
    def get_unit(self):
        """获取数值单位"""
        return self._unit
    
    @abstractmethod
    def update_state(self):
        """抽象方法：子类需要实现状态更新逻辑"""
        pass

