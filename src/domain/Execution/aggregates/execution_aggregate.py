"""执行聚合根"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from ..value_objects.execution_context import ExecutionContext
from ..value_objects.execution_result import ExecutionResult, ExecutionStatus
from ..value_objects.retry_policy import RetryPolicy
from ..entities.execution_log import ExecutionLog
from ..entities.execution_record import ExecutionRecord, ExecutionRecordStatus
from ..events.execution_started import ExecutionStarted
from ..events.execution_succeeded import ExecutionSucceeded
from ..events.execution_failed import ExecutionFailed

logger = logging.getLogger(__name__)


class ExecutionAggregate:
    """执行聚合根
    
    封装场景执行的核心业务逻辑，维护执行的一致性边界。
    包含执行日志列表和执行记录，支持完整的执行历史持久化。
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
        
        # 执行状态
        self._retry_count = 0
        self._is_completed = False
        self._result: Optional[ExecutionResult] = None
        
        # 时间戳
        self._started_at = datetime.utcnow()
        self._ended_at: Optional[datetime] = None
        
        # 执行日志列表
        self._logs: List[ExecutionLog] = []
        
        # 场景名称
        self._scene_name: Optional[str] = None
        
        # 领域事件列表
        self._domain_events: List[object] = []
        
        # 发布执行开始事件
        event = ExecutionStarted(
            execution_id=execution_id,
            scene_id=context.scene_id,
            occurred_at=self._started_at
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
    
    @property
    def result(self) -> Optional[ExecutionResult]:
        """获取执行结果"""
        return self._result
    
    @property
    def started_at(self) -> datetime:
        """获取开始时间"""
        return self._started_at
    
    @property
    def ended_at(self) -> Optional[datetime]:
        """获取结束时间"""
        return self._ended_at
    
    @property
    def logs(self) -> List[ExecutionLog]:
        """获取执行日志列表"""
        return list(self._logs)
    
    @property
    def scene_name(self) -> Optional[str]:
        """获取场景名称"""
        return self._scene_name
    
    @scene_name.setter
    def scene_name(self, value: str) -> None:
        """设置场景名称"""
        self._scene_name = value
    
    def start(self) -> None:
        """开始执行"""
        logger.info(f"开始执行场景: {self._context.scene_id} (ExecutionID: {self._execution_id})")
    
    def add_log(
        self,
        step_number: int,
        action_type: str,
        target: str,
        command: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ExecutionLog:
        """添加执行日志
        
        创建一个新的 ExecutionLog 实体并添加到日志列表。
        
        Args:
            step_number: 步骤序号
            action_type: 动作类型
            target: 目标设备或场景
            command: 命令名称
            parameters: 命令参数
            
        Returns:
            创建的执行日志实体
        """
        log = ExecutionLog.create(
            execution_id=self._execution_id,
            step_number=step_number,
            action_type=action_type,
            target=target,
            command=command,
            parameters=parameters
        )
        self._logs.append(log)
        
        log_msg = f"步骤 {step_number}: {action_type} -> {target} | Cmd: {command} | Params: {parameters}"
        logger.info(f"[{self._execution_id}] {log_msg}")
        
        return log
    
    def update_log(
        self,
        log_id: str,
        success: bool,
        response: Optional[Dict[str, Any]] = None,
        duration_ms: int = 0,
        error_message: Optional[str] = None
    ) -> None:
        """更新执行日志的完成状态
        
        Args:
            log_id: 日志ID
            success: 是否成功
            response: 执行响应
            duration_ms: 执行耗时
            error_message: 错误信息
        """
        for i, log in enumerate(self._logs):
            if log.log_id == log_id:
                self._logs[i] = log.complete(
                    success=success,
                    response=response,
                    duration_ms=duration_ms,
                    error_message=error_message
                )
                break
    
    def get_logs(self) -> List[ExecutionLog]:
        """获取所有执行日志
        
        Returns:
            执行日志列表的副本
        """
        return list(self._logs)
    
    def get_record(self) -> ExecutionRecord:
        """获取执行记录
        
        根据当前聚合根状态生成执行记录实体。
        
        Returns:
            执行记录实体
        """
        if not self._is_completed:
            # 执行中
            return ExecutionRecord(
                execution_id=self._execution_id,
                scene_id=self._context.scene_id,
                status=ExecutionRecordStatus.RUNNING,
                started_at=self._started_at,
                total_steps=len(self._logs),
                completed_steps=sum(1 for log in self._logs if log.success)
            )
        
        # 已完成
        if self._result and self._result.is_success():
            status = ExecutionRecordStatus.SUCCESS
            error_message = None
            error_code = None
        else:
            status = ExecutionRecordStatus.FAILED
            error_message = self._result.error_message if self._result else "未知错误"
            error_code = self._result.error_code if self._result else None
        
        return ExecutionRecord(
            execution_id=self._execution_id,
            scene_id=self._context.scene_id,
            status=status,
            started_at=self._started_at,
            ended_at=self._ended_at,
            error_message=error_message,
            error_code=error_code,
            total_steps=len(self._logs),
            completed_steps=sum(1 for log in self._logs if log.success)
        )
    
    def complete(self, result: ExecutionResult) -> None:
        """完成执行"""
        if self._is_completed:
            raise ValueError("执行已经完成")
        
        self._is_completed = True
        self._result = result
        self._ended_at = datetime.utcnow()
        
        logger.info(f"执行完成: {self._execution_id} | 结果: {'成功' if result.is_success() else '失败'}")
        
        # 发布领域事件
        if result.is_success():
            event = ExecutionSucceeded(
                execution_id=self._execution_id,
                scene_id=self._context.scene_id,
                occurred_at=self._ended_at
            )
        else:
            event = ExecutionFailed(
                execution_id=self._execution_id,
                scene_id=self._context.scene_id,
                error_message=result.error_message,
                occurred_at=self._ended_at
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


