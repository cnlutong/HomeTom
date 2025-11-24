"""设备领域事件模块"""

from .device_registered import DeviceRegistered
from .device_status_changed import DeviceStatusChanged

__all__ = [
    'DeviceRegistered',
    'DeviceStatusChanged',
]

