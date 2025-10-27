"""
统一错误处理模块
定义所有自定义异常类型
"""


class ControllerException(Exception):
    """控制器基础异常类"""
    def __init__(self, message: str = "Controller error occurred"):
        self.message = message
        super().__init__(self.message)


class HALCommunicationError(ControllerException):
    """HAL 通信异常"""
    def __init__(self, message: str = "HAL communication failed"):
        super().__init__(message)


class DeviceNotFoundError(ControllerException):
    """设备未找到异常"""
    def __init__(self, device_id: str):
        super().__init__(f"Device not found: {device_id}")
        self.device_id = device_id


class SceneNotFoundError(ControllerException):
    """场景未找到异常"""
    def __init__(self, scene_id: str):
        super().__init__(f"Scene not found: {scene_id}")
        self.scene_id = scene_id


class SceneExecutionError(ControllerException):
    """场景执行异常"""
    def __init__(self, scene_id: str, reason: str):
        super().__init__(f"Scene execution failed: {scene_id}, reason: {reason}")
        self.scene_id = scene_id
        self.reason = reason


class SceneDefinitionError(ControllerException):
    """场景定义错误"""
    def __init__(self, message: str = "Invalid scene definition"):
        super().__init__(message)


class DatabaseError(ControllerException):
    """数据库操作异常"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message)


class StateManagerError(ControllerException):
    """状态管理异常"""
    def __init__(self, message: str = "State manager operation failed"):
        super().__init__(message)

