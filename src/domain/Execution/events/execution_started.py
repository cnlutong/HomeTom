"""执行开始事件"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ExecutionStarted:
    """执行开始领域事件"""
    execution_id: str
    scene_id: str
    occurred_at: datetime
    
    def __post_init__(self):
        """验证事件数据"""
        if not self.execution_id:
            raise ValueError("执行ID不能为空")
        if not self.scene_id:
            raise ValueError("场景ID不能为空")

