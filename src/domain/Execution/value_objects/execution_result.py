"""执行结果值对象"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any
from datetime import timedelta


class ExecutionStatus(Enum):
    """执行状态枚举"""
    RUNNING = "running"  # 执行中
    SUCCESS = "success"  # 成功
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消


@dataclass(frozen=True)
class ExecutionResult:
    """执行结果值对象"""
    status: ExecutionStatus
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None  # 详细信息
    
    def __post_init__(self):
        """验证执行结果数据"""
        if not isinstance(self.status, ExecutionStatus):
            raise ValueError("执行状态必须是ExecutionStatus枚举")
        if self.status == ExecutionStatus.FAILED and not self.error_message:
            raise ValueError("失败状态必须提供错误信息")
    
    def is_success(self) -> bool:
        """判断是否成功"""
        return self.status == ExecutionStatus.SUCCESS
    
    def is_failed(self) -> bool:
        """判断是否失败"""
        return self.status == ExecutionStatus.FAILED
    
    def is_running(self) -> bool:
        """判断是否执行中"""
        return self.status == ExecutionStatus.RUNNING
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "status": self.status.value
        }
        if self.error_message:
            result["error_message"] = self.error_message
        if self.error_code:
            result["error_code"] = self.error_code
        if self.details:
            result["details"] = self.details
        return result
    
    @classmethod
    def success(cls, details: Optional[Dict[str, Any]] = None) -> "ExecutionResult":
        """创建成功结果"""
        return cls(
            status=ExecutionStatus.SUCCESS,
            details=details
        )
    
    @classmethod
    def failed(
        cls,
        error_message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> "ExecutionResult":
        """创建失败结果"""
        return cls(
            status=ExecutionStatus.FAILED,
            error_message=error_message,
            error_code=error_code,
            details=details
        )
    
    @classmethod
    def running(cls) -> "ExecutionResult":
        """创建执行中结果"""
        return cls(status=ExecutionStatus.RUNNING)

