"""硬件客户端接口

定义与外部硬件系统通信的抽象接口。
不同平台（Home Assistant、涂鸦、米家等）实现此接口。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class HardwareResponse:
    """硬件通信响应"""
    success: bool
    status_code: int
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    @classmethod
    def ok(cls, data: Optional[Dict[str, Any]] = None) -> "HardwareResponse":
        """创建成功响应"""
        return cls(success=True, status_code=200, data=data)
    
    @classmethod
    def failed(cls, error: str, status_code: int = 500) -> "HardwareResponse":
        """创建失败响应"""
        return cls(success=False, status_code=status_code, error=error)


class IHardwareClient(ABC):
    """硬件客户端接口
    
    定义与外部智能家居平台通信的通用能力。
    不同平台实现此接口，通过 HardwareClientRegistry 进行路由。
    
    实现类示例：
    - HttpHardwareClient：Home Assistant REST API
    - TuyaCloudClient：涂鸦云 API
    - MiHomeClient：米家 API
    """
    
    @abstractmethod
    async def call_service(
        self,
        domain: str,
        service: str,
        entity_id: str,
        data: Optional[Dict[str, Any]] = None
    ) -> HardwareResponse:
        """调用服务
        
        Args:
            domain: 服务域，如 "light", "switch", "climate"
            service: 服务名，如 "turn_on", "turn_off", "set_temperature"
            entity_id: 实体ID
            data: 附加数据
            
        Returns:
            HardwareResponse: 通信响应
            
        示例：
            call_service("light", "turn_on", "light.living_room", {"brightness": 128})
        """
        pass
    
    @abstractmethod
    async def get_state(self, entity_id: str) -> HardwareResponse:
        """获取设备状态
        
        Args:
            entity_id: 实体ID
            
        Returns:
            HardwareResponse: 包含 state 和 attributes 的响应
        """
        pass
    
    @abstractmethod
    async def check_connection(self) -> bool:
        """检查连接状态
        
        Returns:
            bool: 连接是否正常
        """
        pass
    
    @property
    @abstractmethod
    def adapter_type(self) -> str:
        """获取适配器类型标识
        
        Returns:
            str: 如 "homeassistant", "tuya", "mijia"
        """
        pass

