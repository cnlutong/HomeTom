"""场景执行器聚合根"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class ExecutorStatus(Enum):
    """执行器状态枚举"""
    ACTIVE = "active"      # 激活状态，正在监听触发器
    STOPPED = "stopped"    # 停止状态，不监听触发器
    ERROR = "error"        # 错误状态，执行过程中出现异常


@dataclass
class SceneExecutor:
    """场景执行器聚合根
    
    负责管理场景的运行时状态和调度。
    当场景发布时创建执行器，场景禁用时停止执行器。
    
    Attributes:
        executor_id: 执行器唯一标识
        scene_id: 关联的场景ID
        status: 执行器状态
        created_at: 创建时间
        updated_at: 更新时间
        last_triggered_at: 最后触发时间
        trigger_count: 触发次数统计
        error_message: 错误信息（当状态为ERROR时）
    """
    executor_id: str
    scene_id: str
    status: ExecutorStatus
    created_at: datetime
    updated_at: datetime
    last_triggered_at: Optional[datetime] = None
    trigger_count: int = 0
    error_message: Optional[str] = None
    
    @classmethod
    def create(cls, scene_id: str) -> "SceneExecutor":
        """创建新的执行器
        
        Args:
            scene_id: 关联的场景ID
            
        Returns:
            新创建的执行器实例，状态为 ACTIVE
        """
        now = datetime.utcnow()
        return cls(
            executor_id=str(uuid.uuid4()),
            scene_id=scene_id,
            status=ExecutorStatus.STOPPED,
            created_at=now,
            updated_at=now,
            last_triggered_at=None,
            trigger_count=0,
            error_message=None
        )
    
    def activate(self) -> None:
        """激活执行器"""
        if self.status == ExecutorStatus.ACTIVE:
            return
        self.status = ExecutorStatus.ACTIVE
        self.error_message = None
        self.updated_at = datetime.utcnow()
    
    def stop(self) -> None:
        """停止执行器"""
        if self.status == ExecutorStatus.STOPPED:
            return
        self.status = ExecutorStatus.STOPPED
        self.updated_at = datetime.utcnow()
    
    def mark_error(self, error_message: str) -> None:
        """标记执行器为错误状态
        
        Args:
            error_message: 错误信息
        """
        self.status = ExecutorStatus.ERROR
        self.error_message = error_message
        self.updated_at = datetime.utcnow()
    
    def record_trigger(self) -> None:
        """记录一次触发"""
        self.trigger_count += 1
        self.last_triggered_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    @property
    def is_active(self) -> bool:
        """执行器是否处于激活状态"""
        return self.status == ExecutorStatus.ACTIVE
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, SceneExecutor):
            return False
        return self.executor_id == other.executor_id
    
    def __hash__(self) -> int:
        return hash(self.executor_id)
