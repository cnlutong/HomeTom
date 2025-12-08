"""设备仓储实现"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.Device.aggregates.device_aggregate import DeviceAggregate
from src.domain.Device.value_objects.device_status import DeviceStatus
from src.domain.Device.repositories.device_repository import IDeviceRepository
from ..models.device_model import DeviceModel
from ..mappers.device_mapper import DeviceMapper


class DeviceRepositoryImpl(IDeviceRepository):
    """设备仓储实现
    
    实现 IDeviceRepository 接口，使用 SQLAlchemy 进行数据持久化
    
    使用示例:
        async with SqlAlchemyUnitOfWork() as uow:
            repo = DeviceRepositoryImpl(uow.session)
            device = await repo.find_by_id("device-123")
    """
    
    def __init__(self, session: AsyncSession):
        """初始化仓储
        
        Args:
            session: 异步数据库会话
        """
        self._session = session
        self._mapper = DeviceMapper
    
    async def save(self, device: DeviceAggregate) -> None:
        """保存设备聚合根
        
        如果设备已存在则更新，否则新增
        """
        existing = await self._session.get(DeviceModel, device.device_id)
        
        if existing:
            # 更新现有记录
            self._mapper.update_model(existing, device)
        else:
            # 新增记录
            model = self._mapper.to_model(device)
            self._session.add(model)
    
    async def find_by_id(self, device_id: str) -> Optional[DeviceAggregate]:
        """根据 ID 查找设备"""
        model = await self._session.get(DeviceModel, device_id)
        
        if model is None:
            return None
        
        return self._mapper.to_aggregate(model)
    
    async def find_by_entity_id(self, entity_id: str) -> Optional[DeviceAggregate]:
        """根据实体 ID 查找设备"""
        stmt = select(DeviceModel).where(DeviceModel.entity_id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is None:
            return None
        
        return self._mapper.to_aggregate(model)
    
    async def find_all(self) -> List[DeviceAggregate]:
        """查找所有设备"""
        stmt = select(DeviceModel)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        return [self._mapper.to_aggregate(m) for m in models]
    
    async def find_by_status(self, status: DeviceStatus) -> List[DeviceAggregate]:
        """根据状态查找设备"""
        stmt = select(DeviceModel).where(DeviceModel.status == status.value)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        return [self._mapper.to_aggregate(m) for m in models]
    
    async def delete(self, device_id: str) -> None:
        """删除设备"""
        model = await self._session.get(DeviceModel, device_id)
        
        if model:
            await self._session.delete(model)
