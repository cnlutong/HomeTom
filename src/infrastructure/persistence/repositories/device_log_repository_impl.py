"""设备日志仓储实现"""

from typing import List
from datetime import datetime, time
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.Execution.repositories.device_log_repository import IDeviceLogRepository
from src.infrastructure.persistence.models.execution_model import ExecutionModel
from src.infrastructure.persistence.models.execution_log_model import ExecutionLogModel

class DeviceLogRepositoryImpl(IDeviceLogRepository):
    """设备日志仓储实现"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def find_all_paginated(self, skip: int = 0, limit: int = 50) -> List[ExecutionLogModel]:
        """分页查找所有设备日志，按时间倒序"""
        stmt = select(ExecutionLogModel).options(
            selectinload(ExecutionLogModel.execution).selectinload(ExecutionModel.scene)
        ).order_by(
            desc(ExecutionLogModel.created_at)
        ).offset(skip).limit(limit)
        
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def count_today_logs(self) -> int:
        """统计今日设备日志数量"""
        today_start = datetime.combine(datetime.now().date(), time.min)
        
        stmt = select(func.count()).select_from(ExecutionLogModel).where(
            ExecutionLogModel.created_at >= today_start
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0
