"""场景生命周期事件处理器"""

import logging
from typing import TYPE_CHECKING

from src.domain.Scene.events.scene_published import ScenePublished
from src.domain.Scene.events.scene_disabled import SceneDisabled
from src.domain.Scene.events.scene_created import SceneCreated
from src.domain.Scene.events.scene_definition_updated import SceneDefinitionUpdated
from src.domain.Scene.events.scene_deleted import SceneDeleted
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
        print(f"[SceneLifecycleHandler] on_scene_created called: {scene_id}")
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
        
        当场景定义更新时，确保执行器存在且状态与场景状态一致，
        同时编译场景定义为可执行的执行流程。
        
        Args:
            event: 场景定义更新事件
        """
        from src.infrastructure.persistence.repositories.executor_repository_impl import ExecutorRepositoryImpl
        from src.infrastructure.persistence.repositories.scene_repository_impl import SceneRepositoryImpl
        from src.domain.Scene.aggregates.scene_aggregate import SceneStatus
        
        scene_id = event.scene_id
        logger.info(f"处理场景定义更新事件: {scene_id}")
        
        async with self._session_factory() as session:
            executor_repo = ExecutorRepositoryImpl(session)
            scene_repo = SceneRepositoryImpl(session)
            
            # 获取场景当前状态和定义
            scene = await scene_repo.find_by_id(scene_id)
            if not scene:
                logger.warning(f"场景不存在，跳过执行器更新: {scene_id}")
                return
            
            # 编译场景定义为执行流程
            execution_flow = self._compile_execution_flow(scene)
            
            executor = await executor_repo.find_by_scene_id(scene_id)
            
            if executor:
                # 执行器已存在，更新执行流程和状态
                executor.update_execution_flow(execution_flow)
                if scene.status == SceneStatus.PUBLISHED:
                    executor.activate()
                    logger.info(f"执行器已同步为激活状态: {executor.executor_id} (场景: {scene_id})")
                else:
                    executor.stop()
                    logger.info(f"执行器已同步为停止状态: {executor.executor_id} (场景: {scene_id})")
                await executor_repo.save(executor)
            else:
                # 如果不存在，创建新的执行器
                executor = SceneExecutor.create(scene_id, execution_flow)
                if scene.status == SceneStatus.PUBLISHED:
                    executor.activate()
                await executor_repo.save(executor)
                logger.info(f"执行器不存在，已创建: {executor.executor_id} (场景: {scene_id}, 状态: {executor.status.value})")
            
            await session.commit()
    
    def _compile_execution_flow(self, scene) -> dict:
        """编译场景定义为可执行的执行流程
        
        Args:
            scene: 场景聚合根
            
        Returns:
            执行流程字典，可直接被调度器使用
        """
        if not scene.definition:
            return {
                "triggers": [],
                "conditions": [],
                "actions": [],
                "scene_id": scene.scene_id,
                "scene_name": scene.name
            }
        
        definition = scene.definition
        
        return {
            "scene_id": scene.scene_id,
            "scene_name": scene.name,
            "triggers": [t.to_dict() for t in definition.triggers],
            "conditions": [c.to_dict() for c in definition.conditions] if definition.conditions else [],
            "actions": [a.to_dict() for a in definition.actions]
        }



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

    async def on_scene_deleted(self, event: SceneDeleted) -> None:
        """处理场景删除事件
        
        当场景删除时，清理：
        1. 关联的执行器
        2. 关联的执行记录
        
        Args:
            event: 场景删除事件
        """
        from src.infrastructure.persistence.repositories.executor_repository_impl import ExecutorRepositoryImpl
        from src.infrastructure.persistence.repositories.execution_repository_impl import ExecutionRepositoryImpl
        
        scene_id = event.scene_id
        logger.info(f"处理场景删除事件，清理相关数据: {scene_id}")
        
        async with self._session_factory() as session:
            # 1. 物理删除执行器记录
            executor_repo = ExecutorRepositoryImpl(session)
            await executor_repo.delete_by_scene_id(scene_id)
            
            # 2. 物理删除执行历史记录
            execution_repo = ExecutionRepositoryImpl(session)
            await execution_repo.delete_by_scene_id(scene_id)
            
            await session.commit()
            logger.info(f"已清理场景 {scene_id} 相关的执行器和执行历史记录")
