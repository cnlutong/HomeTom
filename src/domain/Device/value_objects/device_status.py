"""设备状态值对象"""

from enum import Enum
from typing import Final


class DeviceStatus(Enum):
    """设备状态枚举"""
    ENABLED = "enabled"  # 已启用
    DISABLED = "disabled"  # 已禁用
    UNAVAILABLE = "unavailable"  # 不可用（设备离线或无法连接）

    @classmethod
    def from_string(cls, status: str) -> "DeviceStatus":
        """从字符串创建状态"""
        try:
            return cls(status.lower())
        except ValueError:
            return cls.UNAVAILABLE

    def __str__(self) -> str:
        return self.value


# 常量定义
ENABLED: Final[DeviceStatus] = DeviceStatus.ENABLED
DISABLED: Final[DeviceStatus] = DeviceStatus.DISABLED
UNAVAILABLE: Final[DeviceStatus] = DeviceStatus.UNAVAILABLE

