"""设备 ORM 模型"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class DeviceModel(Base):
    """设备数据库模型
    
    对应领域层的 DeviceAggregate，但不包含业务逻辑
    """
    
    __tablename__ = "devices"
    
    # 主键
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    
    # 基本信息
    entity_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    adapter_type: Mapped[str] = mapped_column(String(32), nullable=False)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    # 能力列表（JSON 存储）
    capabilities: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    
    # 状态
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="enabled", index=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<DeviceModel(id={self.id}, entity_id={self.entity_id}, name={self.name})>"
