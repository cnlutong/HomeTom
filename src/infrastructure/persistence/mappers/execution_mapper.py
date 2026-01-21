"""执行聚合根与 ORM 模型的映射器"""

from datetime import datetime, timedelta
from typing import List
from src.domain.Execution.aggregates.execution_aggregate import ExecutionAggregate
from src.domain.Execution.value_objects.execution_context import ExecutionContext
from src.domain.Execution.value_objects.execution_result import ExecutionResult, ExecutionStatus
from src.domain.Execution.value_objects.retry_policy import RetryPolicy
from src.domain.Execution.entities.execution_log import ExecutionLog
from ..models.execution_model import ExecutionModel
from ..models.execution_log_model import ExecutionLogModel


class ExecutionMapper:
    """执行映射器
    
    负责 ExecutionAggregate 与 ExecutionModel 之间的双向转换
    保持领域层的纯净性，转换逻辑在此处理
    
    Note:
        ExecutionAggregate 在构造函数中会自动发布 ExecutionStarted 事件，
        因此从数据库恢复时需要使用特殊方法，避免重复发布事件
    """
    
    @staticmethod
    def to_model(aggregate: ExecutionAggregate) -> ExecutionModel:
        """将聚合根转换为 ORM 模型
        
        Args:
            aggregate: 执行聚合根
            
        Returns:
            执行 ORM 模型
        """
        context = aggregate.context
        retry_policy = aggregate.retry_policy
        
        # 确定状态字符串
        if not aggregate.is_completed:
            status = "running"
        elif aggregate.result and aggregate.result.is_success():
            status = "success"
        else:
            status = "failed"
        
        # 获取错误信息
        error_message = None
        error_code = None
        if aggregate.result and aggregate.result.is_failed():
            error_message = aggregate.result.error_message
            error_code = aggregate.result.error_code
        
        model = ExecutionModel(
            id=aggregate.execution_id,
            scene_id=context.scene_id,
            trigger_source=context.trigger_source,
            input_parameters=context.input_parameters,
            call_chain=context.call_chain,
            max_retries=retry_policy.max_retries,
            retry_interval_seconds=int(retry_policy.retry_interval.total_seconds()),
            status=status,
            retry_count=aggregate._retry_count,
            is_completed=aggregate.is_completed,
            error_message=error_message,
            error_code=error_code,
            started_at=aggregate.started_at,
            ended_at=aggregate.ended_at,
            created_at=datetime.utcnow(),
        )
        
        # 转换日志
        model.logs = [ExecutionMapper.log_to_model(log) for log in aggregate.logs]
        
        return model
    
    @staticmethod
    def to_aggregate(model: ExecutionModel) -> ExecutionAggregate:
        """将 ORM 模型转换为聚合根
        
        Args:
            model: 执行 ORM 模型
            
        Returns:
            执行聚合根
            
        Note:
            从数据库恢复时，需要绕过构造函数避免重复发布事件
        """
        # 重建执行上下文
        context = ExecutionContext(
            scene_id=model.scene_id,
            trigger_source=model.trigger_source,
            input_parameters=model.input_parameters,
            call_chain=model.call_chain,
        )
        
        # 重建重试策略（从秒数转换为 timedelta）
        retry_policy = RetryPolicy(
            max_retries=model.max_retries,
            retry_interval=timedelta(seconds=model.retry_interval_seconds),
        )
        
        # 重建执行结果
        result = None
        if model.is_completed:
            if model.status == "success":
                result = ExecutionResult.success()
            elif model.status == "failed":
                result = ExecutionResult.failed(
                    error_message=model.error_message or "未知错误",
                    error_code=model.error_code
                )
        
        # 使用 __new__ 创建实例，绕过 __init__ 避免触发事件
        aggregate = object.__new__(ExecutionAggregate)
        
        # 手动设置所有属性
        aggregate._execution_id = model.id
        aggregate._context = context
        aggregate._retry_policy = retry_policy
        aggregate._retry_count = model.retry_count
        aggregate._is_completed = model.is_completed
        aggregate._result = result
        aggregate._started_at = model.started_at
        aggregate._ended_at = model.ended_at
        if hasattr(model, 'scene') and model.scene:
            aggregate._scene_name = model.scene.name
        elif not hasattr(aggregate, '_scene_name'):
             aggregate._scene_name = "Unknown Scene"
        else:
             aggregate._scene_name = "Unknown Scene"

        aggregate._domain_events = []  # 恢复时不包含事件
        
        # 恢复日志
        aggregate._logs = [ExecutionMapper.log_to_entity(log_model) for log_model in model.logs]
        
        return aggregate
    
    @staticmethod
    def update_model(model: ExecutionModel, aggregate: ExecutionAggregate) -> None:
        """用聚合根数据更新 ORM 模型（就地更新）
        
        Args:
            model: 需要更新的 ORM 模型
            aggregate: 聚合根数据源
        """
        # 确定状态字符串
        if not aggregate.is_completed:
            model.status = "running"
        elif aggregate.result and aggregate.result.is_success():
            model.status = "success"
        else:
            model.status = "failed"
        
        model.retry_count = aggregate._retry_count
        model.is_completed = aggregate.is_completed
        model.ended_at = aggregate.ended_at
        
        # 更新错误信息
        if aggregate.result and aggregate.result.is_failed():
            model.error_message = aggregate.result.error_message
            model.error_code = aggregate.result.error_code
        
        # 更新日志（清除旧的，添加新的）
        model.logs.clear()
        for log in aggregate.logs:
            model.logs.append(ExecutionMapper.log_to_model(log))
    
    @staticmethod
    def log_to_model(log: ExecutionLog) -> ExecutionLogModel:
        """将执行日志实体转换为 ORM 模型
        
        Args:
            log: 执行日志实体
            
        Returns:
            执行日志 ORM 模型
        """
        return ExecutionLogModel(
            id=log.log_id,
            execution_id=log.execution_id,
            step_number=log.step_number,
            action_type=log.action_type,
            target=log.target,
            command=log.command,
            parameters=log.parameters,
            response=log.response,
            duration_ms=log.duration_ms,
            success=log.success,
            error_message=log.error_message,
            created_at=log.created_at
        )
    
    @staticmethod
    def log_to_entity(model: ExecutionLogModel) -> ExecutionLog:
        """将执行日志 ORM 模型转换为实体
        
        Args:
            model: 执行日志 ORM 模型
            
        Returns:
            执行日志实体
        """
        return ExecutionLog(
            log_id=model.id,
            execution_id=model.execution_id,
            step_number=model.step_number,
            action_type=model.action_type,
            target=model.target,
            command=model.command,
            parameters=model.parameters,
            response=model.response,
            duration_ms=model.duration_ms,
            success=model.success,
            error_message=model.error_message,
            created_at=model.created_at
        )

