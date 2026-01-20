"""场景创建事件"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SceneCreated:
    """场景创建领域事件"""
    scene_id: str
    name: str
    occurred_at: datetime
    
    def __post_init__(self):
        """验证事件数据"""
        if not self.scene_id:
            raise ValueError("场景ID不能为空")
        if not self.name:
            raise ValueError("场景名称不能为空")
