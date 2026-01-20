"""场景定义更新事件"""

from dataclasses import dataclass
from datetime import datetime
from ..value_objects.scene_definition import SceneDefinition


@dataclass(frozen=True)
class SceneDefinitionUpdated:
    """场景定义更新领域事件
    
    当场景定义被编辑保存时触发
    """
    scene_id: str
    definition: SceneDefinition
    occurred_at: datetime
    
    def __post_init__(self):
        """验证事件数据"""
        if not self.scene_id:
            raise ValueError("场景ID不能为空")
        if not self.definition:
            raise ValueError("场景定义不能为空")
