"""硬件客户端注册表

根据 adapter_type 路由到正确的硬件客户端。
"""

import logging
from typing import Dict, Optional

from ...domain.Device.services.hardware_client import IHardwareClient


logger = logging.getLogger(__name__)


class HardwareClientRegistry:
    """硬件客户端注册表
    
    管理不同平台的硬件客户端，根据 adapter_type 进行路由。
    
    使用示例：
        registry = HardwareClientRegistry()
        registry.register(ha_client)  # adapter_type="homeassistant"
        registry.register(tuya_client)  # adapter_type="tuya"
        
        # 根据设备的 adapter_type 获取客户端
        client = registry.get_client("homeassistant")
    """
    
    def __init__(self):
        """初始化注册表"""
        self._clients: Dict[str, IHardwareClient] = {}
    
    def register(self, client: IHardwareClient) -> None:
        """注册客户端
        
        Args:
            client: 实现 IHardwareClient 接口的客户端实例
        """
        adapter_type = client.adapter_type
        if adapter_type in self._clients:
            logger.warning(f"覆盖已存在的客户端: {adapter_type}")
        
        self._clients[adapter_type] = client
        logger.info(f"注册硬件客户端: {adapter_type}")
    
    def unregister(self, adapter_type: str) -> None:
        """注销客户端
        
        Args:
            adapter_type: 适配器类型
        """
        if adapter_type in self._clients:
            del self._clients[adapter_type]
            logger.info(f"注销硬件客户端: {adapter_type}")
    
    def get_client(self, adapter_type: str) -> Optional[IHardwareClient]:
        """获取客户端
        
        Args:
            adapter_type: 适配器类型，如 "homeassistant", "tuya", "mijia"
            
        Returns:
            对应的硬件客户端，若不存在则返回 None
        """
        client = self._clients.get(adapter_type)
        if client is None:
            logger.warning(f"未找到硬件客户端: {adapter_type}")
        return client
    
    def get_client_or_raise(self, adapter_type: str) -> IHardwareClient:
        """获取客户端，不存在时抛出异常
        
        Args:
            adapter_type: 适配器类型
            
        Returns:
            对应的硬件客户端
            
        Raises:
            ValueError: 客户端不存在
        """
        client = self.get_client(adapter_type)
        if client is None:
            raise ValueError(f"未注册的硬件客户端类型: {adapter_type}")
        return client
    
    def list_adapter_types(self) -> list:
        """列出所有已注册的适配器类型
        
        Returns:
            适配器类型列表
        """
        return list(self._clients.keys())
    
    def has_client(self, adapter_type: str) -> bool:
        """检查是否存在指定类型的客户端
        
        Args:
            adapter_type: 适配器类型
            
        Returns:
            是否存在
        """
        return adapter_type in self._clients
    
    def __len__(self) -> int:
        """返回已注册的客户端数量"""
        return len(self._clients)

