"""执行领域异常"""


class ExecutionDomainException(Exception):
    """执行领域异常基类"""
    pass


class ExecutionNotFoundException(ExecutionDomainException):
    """执行未找到异常"""
    pass


class ExecutionAlreadyRunningException(ExecutionDomainException):
    """执行已在运行异常"""
    pass


class InvalidExecutionContextException(ExecutionDomainException):
    """无效的执行上下文异常"""
    pass


class WorkflowExecutionException(ExecutionDomainException):
    """工作流执行异常"""
    pass

