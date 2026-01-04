"""执行记录实体

记录场景执行的最终状态和结果信息。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class ExecutionRecordStatus(Enum):
    """执行记录状态枚举"""
    RUNNING = "running"  # 执行中
    SUCCESS = "success"  # 成功
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消


@dataclass
class ExecutionRecord:
    """执行记录实体
    
    记录场景执行的最终状态，包括：
    - 执行状态（成功/失败/取消）
    - 开始和结束时间
    - 错误信息（如有）
    """
    
    execution_id: str
    scene_id: str
    status: ExecutionRecordStatus
    started_at: datetime
    ended_at: Optional[datetime] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    total_steps: int = 0  # 总步骤数
    completed_steps: int = 0  # 已完成步骤数
    
    def __post_init__(self):
        """验证记录数据"""
        if not self.execution_id:
            raise ValueError("执行ID不能为空")
        if not self.scene_id:
            raise ValueError("场景ID不能为空")
        if not isinstance(self.status, ExecutionRecordStatus):
            raise ValueError("状态必须是ExecutionRecordStatus枚举")
    
    @classmethod
    def create(
        cls,
        execution_id: str,
        scene_id: str
    ) -> "ExecutionRecord":
        """工厂方法：创建新的执行记录（初始状态为 RUNNING）
        
        Args:
            execution_id: 执行ID
            scene_id: 场景ID
            
        Returns:
            新的执行记录实例
        """
        return cls(
            execution_id=execution_id,
            scene_id=scene_id,
            status=ExecutionRecordStatus.RUNNING,
            started_at=datetime.utcnow()
        )
    
    def mark_success(
        self,
        completed_steps: int = 0,
        total_steps: int = 0
    ) -> "ExecutionRecord":
        """标记执行成功
        
        Returns:
            更新后的执行记录实例
        """
        return ExecutionRecord(
            execution_id=self.execution_id,
            scene_id=self.scene_id,
            status=ExecutionRecordStatus.SUCCESS,
            started_at=self.started_at,
            ended_at=datetime.utcnow(),
            total_steps=total_steps or self.total_steps,
            completed_steps=completed_steps or total_steps or self.total_steps
        )
    
    def mark_failed(
        self,
        error_message: str,
        error_code: Optional[str] = None,
        completed_steps: int = 0,
        total_steps: int = 0
    ) -> "ExecutionRecord":
        """标记执行失败
        
        Args:
            error_message: 错误信息
            error_code: 错误代码
            completed_steps: 已完成步骤数
            total_steps: 总步骤数
            
        Returns:
            更新后的执行记录实例
        """
        return ExecutionRecord(
            execution_id=self.execution_id,
            scene_id=self.scene_id,
            status=ExecutionRecordStatus.FAILED,
            started_at=self.started_at,
            ended_at=datetime.utcnow(),
            error_message=error_message,
            error_code=error_code,
            total_steps=total_steps or self.total_steps,
            completed_steps=completed_steps
        )
    
    def mark_cancelled(self) -> "ExecutionRecord":
        """标记执行已取消
        
        Returns:
            更新后的执行记录实例
        """
        return ExecutionRecord(
            execution_id=self.execution_id,
            scene_id=self.scene_id,
            status=ExecutionRecordStatus.CANCELLED,
            started_at=self.started_at,
            ended_at=datetime.utcnow(),
            total_steps=self.total_steps,
            completed_steps=self.completed_steps
        )
    
    @property
    def is_completed(self) -> bool:
        """是否已完成（成功、失败或取消）"""
        return self.status != ExecutionRecordStatus.RUNNING
    
    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.status == ExecutionRecordStatus.SUCCESS
    
    @property
    def is_failed(self) -> bool:
        """是否失败"""
        return self.status == ExecutionRecordStatus.FAILED
    
    @property
    def duration_ms(self) -> Optional[int]:
        """执行时长（毫秒）"""
        if self.ended_at is None:
            return None
        delta = self.ended_at - self.started_at
        return int(delta.total_seconds() * 1000)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        result = {
            "execution_id": self.execution_id,
            "scene_id": self.scene_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps
        }
        if self.ended_at:
            result["ended_at"] = self.ended_at.isoformat()
            result["duration_ms"] = self.duration_ms
        if self.error_message:
            result["error_message"] = self.error_message
        if self.error_code:
            result["error_code"] = self.error_code
        return result
    
    def __eq__(self, other) -> bool:
        """相等性比较"""
        if not isinstance(other, ExecutionRecord):
            return False
        return self.execution_id == other.execution_id
    
    def __hash__(self) -> int:
        """哈希值"""
        return hash(self.execution_id)
