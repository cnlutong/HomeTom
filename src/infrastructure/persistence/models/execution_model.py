"""执行 ORM 模型"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, JSON, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ExecutionModel(Base):
    """执行数据库模型
    
    对应领域层的 ExecutionAggregate，但不包含业务逻辑
    """
    
    __tablename__ = "executions"
    
    # 主键
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    
    # 执行上下文
    scene_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    scene_version: Mapped[int] = mapped_column(Integer, nullable=False)
    trigger_source: Mapped[str] = mapped_column(String(32), nullable=False)
    input_parameters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    call_chain: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # 重试策略
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    retry_interval_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # 执行状态
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<ExecutionModel(id={self.id}, scene_id={self.scene_id}, completed={self.is_completed})>"
