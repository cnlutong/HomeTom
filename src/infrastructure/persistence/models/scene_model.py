"""场景 ORM 模型"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class SceneModel(Base):
    """场景数据库模型
    
    对应领域层的 SceneAggregate，但不包含业务逻辑
    """
    
    __tablename__ = "scenes"
    
    # 主键
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 状态：draft / published / disabled
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft", index=True)
    
    # 场景定义（JSON 存储触发器、条件、动作）
    definition: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<SceneModel(id={self.id}, name={self.name}, status={self.status})>"
