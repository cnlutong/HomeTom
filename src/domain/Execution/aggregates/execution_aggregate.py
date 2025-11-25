"""执行聚合根"""

import logging
from datetime import datetime
from typing import List, Optional
from ..value_objects.execution_context import ExecutionContext
from ..value_objects.execution_result import ExecutionResult, ExecutionStatus
from ..value_objects.retry_policy import RetryPolicy
from ..events.execution_started import ExecutionStarted
from ..events.execution_succeeded import ExecutionSucceeded
from ..events.execution_failed import ExecutionFailed

logger = logging.getLogger(__name__)


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
        
        # 简单的重试计数
        self._retry_count = 0
        self._is_completed = False
        
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
    def is_completed(self) -> bool:
        """是否已完成"""
        return self._is_completed
    
    @property
    def retry_policy(self) -> RetryPolicy:
        """获取重试策略"""
        return self._retry_policy
    
    def start(self) -> None:
        """开始执行"""
        logger.info(f"开始执行场景: {self._context.scene_id} (ExecutionID: {self._execution_id})")
        pass
    
    def add_log(
        self,
        step_number: int,
        action_type: str,
        target: str,
        command: str,
        parameters: Optional[dict] = None
    ) -> None:
        """添加执行日志"""
        log_msg = f"步骤 {step_number}: {action_type} -> {target} | Cmd: {command} | Params: {parameters}"
        logger.info(f"[{self._execution_id}] {log_msg}")
    
    def complete(self, result: ExecutionResult) -> None:
        """完成执行"""
        if self._is_completed:
            raise ValueError("执行已经完成")
        
        self._is_completed = True
        logger.info(f"执行完成: {self._execution_id} | 结果: {'成功' if result.is_success() else '失败'}")
        
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
        if not self._retry_policy.should_retry(self._retry_count):
            return False
        
        self._retry_count += 1
        logger.warning(f"执行重试: {self._execution_id} | 第 {self._retry_count} 次")
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

