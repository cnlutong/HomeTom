from abc import ABC, abstractmethod
from typing import Dict, Any, List
from .value_objects.device_capability import DeviceCapabilities, DeviceCapability

class BaseDevice(ABC):
    """设备类的基类，定义所有设备共有的属性和基础方法"""
    
    def __init__(self, entity_id: str, name: str):
        self._entity_id = entity_id
        self.name = name
        self._state = "unavailable"
        self.attributes = {}
        self._capabilities = DeviceCapabilities([])

    def get_entity_id(self):
        return self._entity_id

    @abstractmethod
    def update_state(self):
        """抽象方法：强制子类实现获取最新状态的逻辑"""
        pass

    def get_state(self):
        """通用方法：返回当前已知状态"""
        return self._state

    def get_capabilities(self) -> DeviceCapabilities:
        """获取设备具备的能力"""
        return self._capabilities

    def update_attributes(self, new_attributes: Dict[str, Any]):
        """更新设备属性并触发可能的状态变更"""
        self.attributes.update(new_attributes)