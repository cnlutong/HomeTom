"""设备领域服务接口"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from ..aggregates.device_aggregate import DeviceAggregate
from ..value_objects.device_capability import DeviceCapabilities


class IDeviceService(ABC):
    """设备领域服务接口
    
    定义设备相关的领域逻辑，如状态同步策略、能力更新逻辑
    """
    
    @abstractmethod
    async def sync_device_state(
        self, 
        device: DeviceAggregate,
        state_data: Dict[str, Any]
    ) -> None:
        """同步设备状态
        
        Args:
            device: 设备聚合根
            state_data: 从外部获取的状态数据
        """
        pass
    
    @abstractmethod
    async def update_capabilities(
        self,
        device: DeviceAggregate,
        capabilities: DeviceCapabilities
    ) -> None:
        """更新设备能力
        
        Args:
            device: 设备聚合根
            capabilities: 新的能力集合
        """
        pass
    
    @abstractmethod
    async def validate_device_config(
        self,
        adapter_type: str,
        config: Dict[str, Any]
    ) -> bool:
        """验证设备配置
        
        Args:
            adapter_type: 适配器类型
            config: 设备配置
            
        Returns:
            配置是否有效
        """
        pass

