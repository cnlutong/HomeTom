"""场景发布事件"""

from dataclasses import dataclass
from datetime import datetime
from ..value_objects.scene_definition import SceneDefinition


@dataclass(frozen=True)
class ScenePublished:
    """场景发布领域事件"""
    scene_id: str
    version_number: int
    definition: SceneDefinition
    occurred_at: datetime
    
    def __post_init__(self):
        """验证事件数据"""
        if not self.scene_id:
            raise ValueError("场景ID不能为空")
        if self.version_number < 1:
            raise ValueError("版本号必须大于0")
        if not self.definition:
            raise ValueError("场景定义不能为空")

