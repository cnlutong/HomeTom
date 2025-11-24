"""执行记录实体"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ..value_objects.execution_result import ExecutionResult


@dataclass
class ExecutionRecord:
    """执行记录实体
    
    记录单次场景执行的元数据
    """
    execution_id: str
    scene_id: str
    scene_version: int
    trigger_source: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    result: Optional[ExecutionResult] = None
    retry_count: int = 0
    
    def __post_init__(self):
        """验证执行记录数据"""
        if not self.execution_id:
            raise ValueError("执行ID不能为空")
        if not self.scene_id:
            raise ValueError("场景ID不能为空")
        if self.scene_version < 1:
            raise ValueError("场景版本号必须大于0")
        if not self.trigger_source:
            raise ValueError("触发来源不能为空")
        if self.retry_count < 0:
            raise ValueError("重试次数不能为负数")
    
    def complete(self, result: ExecutionResult) -> None:
        """完成执行"""
        if self.ended_at:
            raise ValueError("执行已经完成")
        self.result = result
        self.ended_at = datetime.utcnow()
    
    def increment_retry(self) -> None:
        """增加重试次数"""
        self.retry_count += 1
    
    def get_duration(self) -> Optional[float]:
        """获取执行耗时（秒）"""
        if not self.ended_at:
            return None
        delta = self.ended_at - self.started_at
        return delta.total_seconds()
    
    def is_completed(self) -> bool:
        """判断是否已完成"""
        return self.ended_at is not None

