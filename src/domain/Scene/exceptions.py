"""场景领域异常"""


class SceneDomainException(Exception):
    """场景领域异常基类"""
    pass


class SceneNotFoundException(SceneDomainException):
    """场景未找到异常"""
    pass


class SceneAlreadyExistsException(SceneDomainException):
    """场景已存在异常"""
    pass


class InvalidSceneDefinitionException(SceneDomainException):
    """无效的场景定义异常"""
    pass


class CircularDependencyException(SceneDomainException):
    """循环依赖异常"""
    pass


class InvalidSceneStatusException(SceneDomainException):
    """无效的场景状态异常"""
    pass

