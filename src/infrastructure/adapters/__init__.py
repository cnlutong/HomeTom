"""基础设施适配器模块

提供与外部硬件系统通信的客户端和注册表。
"""

from .hardware_adapter import HttpHardwareClient
from .hardware_client_registry import HardwareClientRegistry
from ...domain.Device.services.hardware_client import IHardwareClient, HardwareResponse

__all__ = [
    # 接口
    'IHardwareClient',
    'HardwareResponse',
    # 注册表
    'HardwareClientRegistry',
    # 实现
    'HttpHardwareClient',
]
