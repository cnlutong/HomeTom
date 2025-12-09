"""设备领域服务模块"""

from .device_service import IDeviceService
from .device_service_impl import DeviceService, default_device_service
from .hardware_client import IHardwareClient, HardwareResponse

__all__ = [
    'IDeviceService',
    'DeviceService',
    'default_device_service',
    'IHardwareClient',
    'HardwareResponse',
]

