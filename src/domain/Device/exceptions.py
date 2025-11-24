"""设备领域异常"""


class DeviceDomainException(Exception):
    """设备领域异常基类"""
    pass


class DeviceNotFoundException(DeviceDomainException):
    """设备未找到异常"""
    pass


class DeviceAlreadyExistsException(DeviceDomainException):
    """设备已存在异常"""
    pass


class InvalidDeviceStatusException(DeviceDomainException):
    """无效的设备状态异常"""
    pass


class InvalidCapabilityException(DeviceDomainException):
    """无效的设备能力异常"""
    pass

