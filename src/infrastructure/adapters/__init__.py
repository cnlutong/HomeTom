"""基础设施适配器模块

提供与外部硬件系统通信的 HTTP 客户端。
"""

from .hardware_adapter import HttpHardwareClient, HttpResponse

__all__ = [
    'HttpHardwareClient',
    'HttpResponse',
]
