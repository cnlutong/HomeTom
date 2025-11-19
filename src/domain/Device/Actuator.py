from abc import ABC, abstractmethod
from .BaseDevice import BaseDevice


class Actuator(BaseDevice):
    """控制类设备基类 - 可以被控制、开关或调节的设备"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._is_on = False
    
    def turn_on(self):
        """打开设备"""
        self._is_on = True
        self._state = "on"
    
    def turn_off(self):
        """关闭设备"""
        self._is_on = False
        self._state = "off"
    
    def is_on(self) -> bool:
        """检查设备是否开启"""
        return self._is_on
    
    @abstractmethod
    def update_state(self):
        """抽象方法：子类需要实现状态更新逻辑"""
        pass

