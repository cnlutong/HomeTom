"""工作单元模式实现

提供事务管理，确保一组操作要么全部成功，要么全部回滚
"""

from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_session


class IUnitOfWork(ABC):
    """工作单元接口
    
    定义事务边界，确保业务操作的原子性
    """
    
    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        """进入上下文"""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出上下文"""
        pass
    
    @abstractmethod
    async def commit(self) -> None:
        """提交事务"""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """回滚事务"""
        pass


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """SQLAlchemy 工作单元实现
    
    使用示例:
        async with SqlAlchemyUnitOfWork() as uow:
            device_repo = DeviceRepositoryImpl(uow.session)
            await device_repo.save(device)
            await uow.commit()
    """
    
    def __init__(self, session: Optional[AsyncSession] = None):
        """初始化工作单元
        
        Args:
            session: 可选的外部会话。如果不提供，将创建新会话
        """
        self._session = session
        self._owns_session = session is None
    
    @property
    def session(self) -> AsyncSession:
        """获取当前会话"""
        if self._session is None:
            raise RuntimeError("工作单元未进入上下文")
        return self._session
    
    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        """进入上下文，创建会话"""
        if self._owns_session:
            self._session = get_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出上下文，处理事务并关闭会话"""
        if exc_type is not None:
            # 发生异常，回滚事务
            await self.rollback()
        
        if self._owns_session and self._session:
            await self._session.close()
            self._session = None
    
    async def commit(self) -> None:
        """提交事务"""
        if self._session:
            await self._session.commit()
    
    async def rollback(self) -> None:
        """回滚事务"""
        if self._session:
            await self._session.rollback()
