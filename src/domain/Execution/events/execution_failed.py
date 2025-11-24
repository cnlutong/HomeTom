"""执行失败事件"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ExecutionFailed:
    """执行失败领域事件"""
    execution_id: str
    scene_id: str
    error_message: str
    error_code: Optional[str] = None
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """验证事件数据"""
        if not self.execution_id:
            raise ValueError("执行ID不能为空")
        if not self.scene_id:
            raise ValueError("场景ID不能为空")
        if not self.error_message:
            raise ValueError("错误信息不能为空")

