"""场景生命周期事件处理器"""

import logging
from typing import TYPE_CHECKING

from src.domain.Scene.events.scene_published import ScenePublished
from src.domain.Scene.events.scene_disabled import SceneDisabled
from src.domain.Scene.events.scene_created import SceneCreated
from src.domain.Scene.events.scene_definition_updated import SceneDefinitionUpdated
from src.domain.Execution.aggregates.scene_executor import SceneExecutor
from src.domain.Execution.repositories.executor_repository import IExecutorRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import async_sessionmaker

logger = logging.getLogger(__name__)


class SceneLifecycleHandler:
    """场景生命周期事件处理器
    
    监听场景发布和禁用事件，自动创建/管理场景执行器。
    
    职责：
    - 当场景发布时，创建或激活对应的执行器
    - 当场景禁用时，停止对应的执行器
    """
    
    def __init__(self, session_factory: "async_sessionmaker"):
        """初始化处理器
        
        Args:
            session_factory: 数据库会话工厂
        """
        self._session_factory = session_factory
    
    async def on_scene_created(self, event: SceneCreated) -> None:
        """处理场景创建事件
        
        当场景创建时，同步创建对应的执行器（默认为停止状态）
        
        Args:
            event: 场景创建事件
        """
        from src.infrastructure.persistence.repositories.executor_repository_impl import ExecutorRepositoryImpl
        
        scene_id = event.scene_id
        logger.info(f"处理场景创建事件: {scene_id}")
        
        async with self._session_factory() as session:
            repo = ExecutorRepositoryImpl(session)
            
            # 检查是否已存在（幂等处理）
            executor = await repo.find_by_scene_id(scene_id)
            if not executor:
                executor = SceneExecutor.create(scene_id)
                await repo.save(executor)
                await session.commit()
                logger.info(f"已为新场景创建执行器: {executor.executor_id} (场景: {scene_id})")
            else:
                logger.info(f"执行器已存在，跳过创建: {executor.executor_id}")

    async def on_scene_definition_updated(self, event: SceneDefinitionUpdated) -> None:
        """处理场景定义更新事件
        
        当场景定义更新时，重置执行器状态为 STOPPED（等待重新发布）
        
        Args:
            event: 场景定义更新事件
        """
        from src.infrastructure.persistence.repositories.executor_repository_impl import ExecutorRepositoryImpl
        
        scene_id = event.scene_id
        logger.info(f"处理场景定义更新事件: {scene_id}")
        
        async with self._session_factory() as session:
            repo = ExecutorRepositoryImpl(session)
            
            executor = await repo.find_by_scene_id(scene_id)
            
            if executor:
                # 场景定义已更新，执行器重置为停止状态（等待重新发布）
                executor.stop()
                await repo.save(executor)
                await session.commit()
                logger.info(f"执行器已重置: {executor.executor_id} (场景: {scene_id})")
            else:
                # 如果不存在，创建新的执行器
                executor = SceneExecutor.create(scene_id)
                await repo.save(executor)
                await session.commit()
                logger.info(f"执行器不存在，已创建: {executor.executor_id} (场景: {scene_id})")

    async def on_scene_published(self, event: ScenePublished) -> None:
        """处理场景发布事件
        
        当场景发布时，检查是否已存在执行器：
        - 存在则激活
        - 不存在则创建新的执行器
        
        Args:
            event: 场景发布事件
        """
        from src.infrastructure.persistence.repositories.executor_repository_impl import ExecutorRepositoryImpl
        
        scene_id = event.scene_id
        logger.info(f"处理场景发布事件: {scene_id}")
        
        async with self._session_factory() as session:
            repo = ExecutorRepositoryImpl(session)
            
            # 检查是否已存在执行器
            executor = await repo.find_by_scene_id(scene_id)
            
            if executor:
                # 已存在，激活执行器
                executor.activate()
                logger.info(f"激活现有执行器: {executor.executor_id} (场景: {scene_id})")
            else:
                # 不存在，创建新执行器
                executor = SceneExecutor.create(scene_id)
                logger.info(f"创建新执行器: {executor.executor_id} (场景: {scene_id})")
            
            await repo.save(executor)
            await session.commit()
            
            logger.info(f"执行器已保存到数据库: {executor.executor_id}")
    
    async def on_scene_disabled(self, event: SceneDisabled) -> None:
        """处理场景禁用事件
        
        当场景禁用时，停止对应的执行器
        
        Args:
            event: 场景禁用事件
        """
        from src.infrastructure.persistence.repositories.executor_repository_impl import ExecutorRepositoryImpl
        
        scene_id = event.scene_id
        logger.info(f"处理场景禁用事件: {scene_id}")
        
        async with self._session_factory() as session:
            repo = ExecutorRepositoryImpl(session)
            
            executor = await repo.find_by_scene_id(scene_id)
            
            if executor:
                executor.stop()
                await repo.save(executor)
                await session.commit()
                logger.info(f"执行器已停止: {executor.executor_id} (场景: {scene_id})")
            else:
                logger.warning(f"未找到场景 {scene_id} 对应的执行器")
