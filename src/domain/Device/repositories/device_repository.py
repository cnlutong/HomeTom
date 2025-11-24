"""设备仓储接口"""

from abc import ABC, abstractmethod
from typing import Optional, List
from ..aggregates.device_aggregate import DeviceAggregate


class IDeviceRepository(ABC):
    """设备仓储接口
    
    定义设备持久化的抽象接口，由基础设施层实现
    """
    
    @abstractmethod
    async def save(self, device: DeviceAggregate) -> None:
        """保存设备聚合根"""
        pass
    
    @abstractmethod
    async def find_by_id(self, device_id: str) -> Optional[DeviceAggregate]:
        """根据ID查找设备"""
        pass
    
    @abstractmethod
    async def find_by_entity_id(self, entity_id: str) -> Optional[DeviceAggregate]:
        """根据实体ID查找设备"""
        pass
    
    @abstractmethod
    async def find_all(self) -> List[DeviceAggregate]:
        """查找所有设备"""
        pass
    
    @abstractmethod
    async def find_by_status(self, status) -> List[DeviceAggregate]:
        """根据状态查找设备"""
        pass
    
    @abstractmethod
    async def delete(self, device_id: str) -> None:
        """删除设备"""
        pass

