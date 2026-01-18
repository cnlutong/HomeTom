"""场景仓储实现"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.Scene.aggregates.scene_aggregate import SceneAggregate, SceneStatus
from src.domain.Scene.repositories.scene_repository import ISceneRepository
from ..models.scene_model import SceneModel
from ..mappers.scene_mapper import SceneMapper


class SceneRepositoryImpl(ISceneRepository):
    """场景仓储实现
    
    实现 ISceneRepository 接口，使用 SQLAlchemy 进行数据持久化
    
    使用示例:
        async with SqlAlchemyUnitOfWork() as uow:
            repo = SceneRepositoryImpl(uow.session)
            scene = await repo.find_by_id("scene-123")
    """
    
    def __init__(self, session: AsyncSession):
        """初始化仓储
        
        Args:
            session: 异步数据库会话
        """
        self._session = session
        self._mapper = SceneMapper
    
    async def save(self, scene: SceneAggregate) -> None:
        """保存场景聚合根
        
        如果场景已存在则更新，否则新增
        """
        existing = await self._session.get(SceneModel, scene.scene_id)
        
        if existing:
            # 更新现有记录
            self._mapper.update_model(existing, scene)
        else:
            # 新增记录
            model = self._mapper.to_model(scene)
            self._session.add(model)
            await self._session.flush() # Ensure it has an identity and is visible to get()
    
    async def find_by_id(self, scene_id: str) -> Optional[SceneAggregate]:
        """根据 ID 查找场景"""
        model = await self._session.get(SceneModel, scene_id)
        
        if model is None:
            return None
        
        return self._mapper.to_aggregate(model)
    
    async def find_all(self) -> List[SceneAggregate]:
        """查找所有场景"""
        stmt = select(SceneModel)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        return [self._mapper.to_aggregate(m) for m in models]
    
    async def find_by_status(self, status: SceneStatus) -> List[SceneAggregate]:
        """根据状态查找场景"""
        stmt = select(SceneModel).where(SceneModel.status == status.value)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        return [self._mapper.to_aggregate(m) for m in models]
    
    async def delete(self, scene_id: str) -> None:
        """删除场景"""
        model = await self._session.get(SceneModel, scene_id)
        
        if model:
            await self._session.delete(model)
