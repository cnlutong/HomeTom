"""执行器 ORM 模型"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ExecutorModel(Base):
    """执行器数据库模型
    
    对应领域层的 SceneExecutor 聚合根
    """
    
    __tablename__ = "scene_executors"
    
    # 主键
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    
    # 关联的场景ID（唯一约束，一个场景只有一个执行器）
    scene_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    
    # 执行器状态：active, stopped, error
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    
    # 触发统计
    trigger_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 错误信息
    error_message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<ExecutorModel(id={self.id}, scene_id={self.scene_id}, status={self.status})>"
