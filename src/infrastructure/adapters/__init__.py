"""基础设施适配器模块

提供与外部硬件系统通信的客户端和注册表。
"""

from .hardware_adapter import (
    HomeAssistantClient,
    HttpHardwareClient,  # 别名，保持向后兼容
    HomeAssistantClientError,
    HomeAssistantAuthError,
    HomeAssistantNotFoundError,
)
from .hardware_client_registry import HardwareClientRegistry
from .response_types import (
    HAStateObject,
    HAServiceDomain,
    HAEventType,
    HAConfig,
    HAHistoryEntry,
    HALogbookEntry,
)
from ...domain.Device.services.hardware_client import IHardwareClient, HardwareResponse

__all__ = [
    # 接口
    'IHardwareClient',
    'HardwareResponse',
    # 注册表
    'HardwareClientRegistry',
    # Home Assistant 客户端
    'HomeAssistantClient',
    'HttpHardwareClient',  # 别名
    # 异常类
    'HomeAssistantClientError',
    'HomeAssistantAuthError',
    'HomeAssistantNotFoundError',
    # 响应类型
    'HAStateObject',
    'HAServiceDomain',
    'HAEventType',
    'HAConfig',
    'HAHistoryEntry',
    'HALogbookEntry',
]
