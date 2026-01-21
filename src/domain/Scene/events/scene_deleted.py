"""场景删除事件"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SceneDeleted:
    """场景删除领域事件"""
    scene_id: str
    occurred_at: datetime
    
    def __post_init__(self):
        """验证事件数据"""
        if not self.scene_id:
            raise ValueError("场景ID不能为空")
