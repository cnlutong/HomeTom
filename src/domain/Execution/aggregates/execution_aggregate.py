"""执行聚合根"""

from datetime import datetime
from typing import List, Optional
from ..value_objects.execution_context import ExecutionContext
from ..value_objects.execution_result import ExecutionResult, ExecutionStatus
from ..value_objects.retry_policy import RetryPolicy
from ..entities.execution_record import ExecutionRecord
from ..entities.execution_log import ExecutionLog
from ..events.execution_started import ExecutionStarted
from ..events.execution_succeeded import ExecutionSucceeded
from ..events.execution_failed import ExecutionFailed


class ExecutionAggregate:
    """执行聚合根
    
    封装场景执行的核心业务逻辑，维护执行的一致性边界
    """
    
    def __init__(
        self,
        execution_id: str,
        context: ExecutionContext,
        retry_policy: Optional[RetryPolicy] = None
    ):
        """初始化执行聚合根
        
        Args:
            execution_id: 执行唯一标识
            context: 执行上下文
            retry_policy: 重试策略
        """
        if not execution_id:
            raise ValueError("执行ID不能为空")
        if not context:
            raise ValueError("执行上下文不能为空")
        
        self._execution_id = execution_id
        self._context = context
        self._retry_policy = retry_policy or RetryPolicy.default()
        
        # 执行记录
        self._record = ExecutionRecord(
            execution_id=execution_id,
            scene_id=context.scene_id,
            scene_version=context.scene_version,
            trigger_source=context.trigger_source,
            started_at=datetime.utcnow()
        )
        
        # 执行日志列表
        self._logs: List[ExecutionLog] = []
        
        # 领域事件列表
        self._domain_events: List[object] = []
        
        # 发布执行开始事件
        event = ExecutionStarted(
            execution_id=execution_id,
            scene_id=context.scene_id,
            scene_version=context.scene_version,
            occurred_at=datetime.utcnow()
        )
        self._add_domain_event(event)
    
    @property
    def execution_id(self) -> str:
        """获取执行ID"""
        return self._execution_id
    
    @property
    def context(self) -> ExecutionContext:
        """获取执行上下文"""
        return self._context
    
    @property
    def record(self) -> ExecutionRecord:
        """获取执行记录"""
        return self._record
    
    @property
    def retry_policy(self) -> RetryPolicy:
        """获取重试策略"""
        return self._retry_policy
    
    def start(self) -> None:
        """开始执行"""
        # 执行记录已经在初始化时创建，这里可以添加额外的逻辑
        pass
    
    def add_log(
        self,
        step_number: int,
        action_type: str,
        target: str,
        command: str,
        parameters: Optional[dict] = None
    ) -> ExecutionLog:
        """添加执行日志"""
        log = ExecutionLog(
            log_id=f"{self._execution_id}_step_{step_number}",
            execution_id=self._execution_id,
            step_number=step_number,
            action_type=action_type,
            target=target,
            command=command,
            parameters=parameters
        )
        self._logs.append(log)
        return log
    
    def get_logs(self) -> List[ExecutionLog]:
        """获取所有执行日志"""
        return list(self._logs)
    
    def complete(self, result: ExecutionResult) -> None:
        """完成执行"""
        if self._record.is_completed():
            raise ValueError("执行已经完成")
        
        self._record.complete(result)
        
        # 发布领域事件
        if result.is_success():
            event = ExecutionSucceeded(
                execution_id=self._execution_id,
                scene_id=self._context.scene_id,
                occurred_at=datetime.utcnow()
            )
        else:
            event = ExecutionFailed(
                execution_id=self._execution_id,
                scene_id=self._context.scene_id,
                error_message=result.error_message,
                occurred_at=datetime.utcnow()
            )
        self._add_domain_event(event)
    
    def fail(self, error_message: str, error_code: Optional[str] = None) -> None:
        """标记执行失败"""
        result = ExecutionResult.failed(
            error_message=error_message,
            error_code=error_code
        )
        self.complete(result)
    
    def succeed(self, details: Optional[dict] = None) -> None:
        """标记执行成功"""
        result = ExecutionResult.success(details=details)
        self.complete(result)
    
    def retry(self) -> bool:
        """重试执行
        
        Returns:
            如果允许重试返回True，否则返回False
        """
        if not self._retry_policy.should_retry(self._record.retry_count):
            return False
        
        self._record.increment_retry()
        return True
    
    def get_domain_events(self) -> List[object]:
        """获取领域事件列表"""
        return list(self._domain_events)
    
    def clear_domain_events(self) -> None:
        """清除领域事件列表"""
        self._domain_events.clear()
    
    def _add_domain_event(self, event: object) -> None:
        """添加领域事件"""
        self._domain_events.append(event)
    
    def __eq__(self, other) -> bool:
        """相等性比较"""
        if not isinstance(other, ExecutionAggregate):
            return False
        return self._execution_id == other._execution_id
    
    def __hash__(self) -> int:
        """哈希值"""
        return hash(self._execution_id)

