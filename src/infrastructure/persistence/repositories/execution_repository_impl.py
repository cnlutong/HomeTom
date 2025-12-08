"""执行仓储实现"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.Execution.aggregates.execution_aggregate import ExecutionAggregate
from src.domain.Execution.repositories.execution_repository import IExecutionRepository
from ..models.execution_model import ExecutionModel
from ..mappers.execution_mapper import ExecutionMapper


class ExecutionRepositoryImpl(IExecutionRepository):
    """执行仓储实现
    
    实现 IExecutionRepository 接口，使用 SQLAlchemy 进行数据持久化
    
    使用示例:
        async with SqlAlchemyUnitOfWork() as uow:
            repo = ExecutionRepositoryImpl(uow.session)
            execution = await repo.find_by_id("exec-123")
    """
    
    def __init__(self, session: AsyncSession):
        """初始化仓储
        
        Args:
            session: 异步数据库会话
        """
        self._session = session
        self._mapper = ExecutionMapper
    
    async def save(self, execution: ExecutionAggregate) -> None:
        """保存执行聚合根
        
        如果执行记录已存在则更新，否则新增
        """
        existing = await self._session.get(ExecutionModel, execution.execution_id)
        
        if existing:
            # 更新现有记录
            self._mapper.update_model(existing, execution)
        else:
            # 新增记录
            model = self._mapper.to_model(execution)
            self._session.add(model)
    
    async def find_by_id(self, execution_id: str) -> Optional[ExecutionAggregate]:
        """根据 ID 查找执行记录"""
        model = await self._session.get(ExecutionModel, execution_id)
        
        if model is None:
            return None
        
        return self._mapper.to_aggregate(model)
    
    async def find_by_scene_id(self, scene_id: str) -> List[ExecutionAggregate]:
        """根据场景 ID 查找所有执行记录"""
        stmt = select(ExecutionModel).where(ExecutionModel.scene_id == scene_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        return [self._mapper.to_aggregate(m) for m in models]
    
    async def find_all(self) -> List[ExecutionAggregate]:
        """查找所有执行记录"""
        stmt = select(ExecutionModel)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        return [self._mapper.to_aggregate(m) for m in models]
