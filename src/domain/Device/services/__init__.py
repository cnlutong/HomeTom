"""设备领域服务模块"""

from .device_service import IDeviceService
from .device_service_impl import DeviceService, default_device_service

__all__ = [
    'IDeviceService',
    'DeviceService',
    'default_device_service',
]

