"""场景版本实体"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ..value_objects.scene_definition import SceneDefinition


@dataclass
class SceneVersion:
    """场景版本实体
    
    记录场景的每次变更历史
    """
    version_number: int
    scene_id: str
    definition: SceneDefinition
    created_at: datetime
    operator: Optional[str] = None  # 操作者
    change_summary: Optional[str] = None  # 变更摘要
    
    def __post_init__(self):
        """验证版本数据"""
        if self.version_number < 1:
            raise ValueError("版本号必须大于0")
        if not self.scene_id:
            raise ValueError("场景ID不能为空")
        if not self.definition:
            raise ValueError("场景定义不能为空")
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "version_number": self.version_number,
            "scene_id": self.scene_id,
            "definition": self.definition.to_dict(),
            "created_at": self.created_at.isoformat(),
            "operator": self.operator,
            "change_summary": self.change_summary
        }

