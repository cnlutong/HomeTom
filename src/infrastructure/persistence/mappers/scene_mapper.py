"""场景聚合根与 ORM 模型的映射器"""

from src.domain.Scene.aggregates.scene_aggregate import SceneAggregate, SceneStatus
from src.domain.Scene.value_objects.scene_definition import SceneDefinition
from ..models.scene_model import SceneModel


class SceneMapper:
    """场景映射器
    
    负责 SceneAggregate 与 SceneModel 之间的双向转换
    保持领域层的纯净性，转换逻辑在此处理
    """
    
    @staticmethod
    def to_model(aggregate: SceneAggregate) -> SceneModel:
        """将聚合根转换为 ORM 模型
        
        Args:
            aggregate: 场景聚合根
            
        Returns:
            场景 ORM 模型
        """
        # 将场景定义序列化为 JSON
        definition_data = None
        if aggregate.definition:
            definition_data = aggregate.definition.to_dict()
        
        return SceneModel(
            id=aggregate.scene_id,
            name=aggregate.name,
            description=aggregate.description,
            status=aggregate.status.value,
            definition=definition_data,
            ui_metadata=aggregate.ui_metadata,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
    
    @staticmethod
    def to_aggregate(model: SceneModel) -> SceneAggregate:
        """将 ORM 模型转换为聚合根
        
        Args:
            model: 场景 ORM 模型
            
        Returns:
            场景聚合根
            
        Note:
            从数据库恢复时，不会触发领域事件
        """
        # 从 JSON 反序列化场景定义
        definition = None
        if model.definition:
            definition = SceneDefinition.from_dict(model.definition)
        
        # 直接构造聚合根，绕过工厂方法（不触发创建事件）
        return SceneAggregate(
            scene_id=model.id,
            name=model.name,
            description=model.description,
            status=SceneStatus(model.status),
            definition=definition,
            ui_metadata=model.ui_metadata,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def update_model(model: SceneModel, aggregate: SceneAggregate) -> None:
        """用聚合根数据更新 ORM 模型（就地更新）
        
        Args:
            model: 需要更新的 ORM 模型
            aggregate: 聚合根数据源
        """
        definition_data = None
        if aggregate.definition:
            definition_data = aggregate.definition.to_dict()
        
        model.name = aggregate.name
        model.description = aggregate.description
        model.status = aggregate.status.value
        model.definition = definition_data
        model.ui_metadata = aggregate.ui_metadata
        model.updated_at = aggregate.updated_at
