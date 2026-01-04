"""执行日志 ORM 模型"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, JSON, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ExecutionLogModel(Base):
    """执行日志数据库模型
    
    对应领域层的 ExecutionLog 实体
    """
    
    __tablename__ = "execution_logs"
    
    # 主键
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    
    # 外键：关联执行记录
    execution_id: Mapped[str] = mapped_column(
        String(64), 
        ForeignKey("executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 步骤信息
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    action_type: Mapped[str] = mapped_column(String(32), nullable=False)
    target: Mapped[str] = mapped_column(String(128), nullable=False)
    command: Mapped[str] = mapped_column(String(64), nullable=False)
    parameters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 执行结果
    response: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<ExecutionLogModel(id={self.id}, execution_id={self.execution_id}, step={self.step_number}, success={self.success})>"
