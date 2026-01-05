"""设备状态 ORM 模型

存储设备的实时状态（如开关状态、亮度、温度等），与 DeviceModel 分离。
MVP 阶段采用方案 A：一个设备只保留一条最新状态记录。
"""

from datetime import datetime
from sqlalchemy import String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class DeviceStateModel(Base):
    """设备状态数据库模型
    
    存储设备的实时状态，与设备基本信息分离。
    一个设备只有一条状态记录，每次更新覆盖。
    
    Attributes:
        entity_id: 设备实体 ID（主键，与 Home Assistant entity_id 对应）
        state: 设备状态（如 on/off/unavailable）
        attributes: 设备属性（JSON 格式，如亮度、温度等）
        last_updated: 最后更新时间（任何属性变化）
        last_changed: 最后改变时间（state 值变化）
    """
    
    __tablename__ = "device_states"
    
    # 主键：使用 entity_id，一个设备只有一条状态记录
    entity_id: Mapped[str] = mapped_column(
        String(128), 
        primary_key=True,
        comment="设备实体 ID"
    )
    
    # 状态数据
    state: Mapped[str] = mapped_column(
        String(32), 
        nullable=False,
        comment="设备状态（on/off/unavailable 等）"
    )
    
    attributes: Mapped[dict] = mapped_column(
        JSON, 
        nullable=False, 
        default=dict,
        comment="设备属性（亮度、温度、颜色等）"
    )
    
    # 时间戳
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False,
        comment="最后更新时间（任何变化）"
    )
    
    last_changed: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False,
        comment="最后改变时间（state 值变化）"
    )
    
    def __repr__(self) -> str:
        return f"<DeviceStateModel(entity_id={self.entity_id}, state={self.state})>"
