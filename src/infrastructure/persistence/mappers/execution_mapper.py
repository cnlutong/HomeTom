"""执行聚合根与 ORM 模型的映射器"""

from datetime import datetime, timedelta
from src.domain.Execution.aggregates.execution_aggregate import ExecutionAggregate
from src.domain.Execution.value_objects.execution_context import ExecutionContext
from src.domain.Execution.value_objects.retry_policy import RetryPolicy
from ..models.execution_model import ExecutionModel


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
        
        return ExecutionModel(
            id=aggregate.execution_id,
            scene_id=context.scene_id,
            scene_version=context.scene_version,
            trigger_source=context.trigger_source,
            input_parameters=context.input_parameters,
            call_chain=context.call_chain,
            max_retries=retry_policy.max_retries,
            retry_interval_seconds=int(retry_policy.retry_interval.total_seconds()),
            retry_count=aggregate._retry_count,
            is_completed=aggregate.is_completed,
            created_at=datetime.utcnow(),
        )
    
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
            scene_version=model.scene_version,
            trigger_source=model.trigger_source,
            input_parameters=model.input_parameters,
            call_chain=model.call_chain,
        )
        
        # 重建重试策略（从秒数转换为 timedelta）
        retry_policy = RetryPolicy(
            max_retries=model.max_retries,
            retry_interval=timedelta(seconds=model.retry_interval_seconds),
        )
        
        # 使用 __new__ 创建实例，绕过 __init__ 避免触发事件
        aggregate = object.__new__(ExecutionAggregate)
        
        # 手动设置所有属性
        aggregate._execution_id = model.id
        aggregate._context = context
        aggregate._retry_policy = retry_policy
        aggregate._retry_count = model.retry_count
        aggregate._is_completed = model.is_completed
        aggregate._domain_events = []  # 恢复时不包含事件
        
        return aggregate
    
    @staticmethod
    def update_model(model: ExecutionModel, aggregate: ExecutionAggregate) -> None:
        """用聚合根数据更新 ORM 模型（就地更新）
        
        Args:
            model: 需要更新的 ORM 模型
            aggregate: 聚合根数据源
        """
        model.retry_count = aggregate._retry_count
        model.is_completed = aggregate.is_completed
