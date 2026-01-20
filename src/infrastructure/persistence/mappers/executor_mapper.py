"""执行器聚合根与 ORM 模型的映射器"""

from datetime import datetime
from src.domain.Execution.aggregates.scene_executor import SceneExecutor, ExecutorStatus
from ..models.executor_model import ExecutorModel


class ExecutorMapper:
    """执行器映射器
    
    负责 SceneExecutor 与 ExecutorModel 之间的双向转换
    """
    
    @staticmethod
    def to_model(executor: SceneExecutor) -> ExecutorModel:
        """将聚合根转换为 ORM 模型
        
        Args:
            executor: 场景执行器聚合根
            
        Returns:
            执行器 ORM 模型
        """
        return ExecutorModel(
            id=executor.executor_id,
            scene_id=executor.scene_id,
            status=executor.status.value,
            trigger_count=executor.trigger_count,
            last_triggered_at=executor.last_triggered_at,
            error_message=executor.error_message,
            created_at=executor.created_at,
            updated_at=executor.updated_at
        )
    
    @staticmethod
    def to_aggregate(model: ExecutorModel) -> SceneExecutor:
        """将 ORM 模型转换为聚合根
        
        Args:
            model: 执行器 ORM 模型
            
        Returns:
            场景执行器聚合根
        """
        return SceneExecutor(
            executor_id=model.id,
            scene_id=model.scene_id,
            status=ExecutorStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_triggered_at=model.last_triggered_at,
            trigger_count=model.trigger_count,
            error_message=model.error_message
        )
    
    @staticmethod
    def update_model(model: ExecutorModel, executor: SceneExecutor) -> None:
        """用聚合根数据更新 ORM 模型（就地更新）
        
        Args:
            model: 需要更新的 ORM 模型
            executor: 聚合根数据源
        """
        model.status = executor.status.value
        model.trigger_count = executor.trigger_count
        model.last_triggered_at = executor.last_triggered_at
        model.error_message = executor.error_message
        model.updated_at = executor.updated_at
