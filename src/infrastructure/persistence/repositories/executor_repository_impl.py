"""执行器仓储实现"""

from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.Execution.aggregates.scene_executor import SceneExecutor, ExecutorStatus
from src.domain.Execution.repositories.executor_repository import IExecutorRepository
from ..models.executor_model import ExecutorModel
from ..mappers.executor_mapper import ExecutorMapper


class ExecutorRepositoryImpl(IExecutorRepository):
    """执行器仓储实现
    
    实现 IExecutorRepository 接口，使用 SQLAlchemy 进行数据持久化
    """
    
    def __init__(self, session: AsyncSession):
        """初始化仓储
        
        Args:
            session: 异步数据库会话
        """
        self._session = session
        self._mapper = ExecutorMapper
    
    async def save(self, executor: SceneExecutor) -> None:
        """保存执行器
        
        如果执行器已存在则更新，否则新增
        """
        existing = await self._session.get(ExecutorModel, executor.executor_id)
        
        if existing:
            # 更新现有记录
            self._mapper.update_model(existing, executor)
        else:
            # 新增记录
            model = self._mapper.to_model(executor)
            self._session.add(model)
    
    async def find_by_id(self, executor_id: str) -> Optional[SceneExecutor]:
        """根据 ID 查找执行器"""
        model = await self._session.get(ExecutorModel, executor_id)
        
        if model is None:
            return None
        
        return self._mapper.to_aggregate(model)
    
    async def find_by_scene_id(self, scene_id: str) -> Optional[SceneExecutor]:
        """根据场景 ID 查找执行器"""
        stmt = select(ExecutorModel).where(ExecutorModel.scene_id == scene_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is None:
            return None
        
        return self._mapper.to_aggregate(model)
    
    async def find_all_active(self) -> List[SceneExecutor]:
        """查找所有激活状态的执行器"""
        stmt = select(ExecutorModel).where(ExecutorModel.status == ExecutorStatus.ACTIVE.value)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        return [self._mapper.to_aggregate(m) for m in models]
    
    async def find_all(self) -> List[SceneExecutor]:
        """查找所有执行器"""
        stmt = select(ExecutorModel)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        return [self._mapper.to_aggregate(m) for m in models]
    
    async def delete(self, executor_id: str) -> None:
        """删除执行器"""
        model = await self._session.get(ExecutorModel, executor_id)
        if model:
            await self._session.delete(model)

    async def delete_by_scene_id(self, scene_id: str) -> None:
        """根据场景 ID 删除执行器"""
        stmt = delete(ExecutorModel).where(ExecutorModel.scene_id == scene_id)
        await self._session.execute(stmt)
