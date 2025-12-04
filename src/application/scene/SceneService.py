"""场景应用服务"""

import uuid
from typing import List, Optional

from ...domain.Scene.aggregates.scene_aggregate import SceneAggregate, SceneStatus
from ...domain.Scene.repositories.scene_repository import ISceneRepository
from ...domain.Scene.services.scene_validator import ISceneValidator
from ...domain.Scene.value_objects.scene_definition import SceneDefinition
from ...infrastructure.messaging.event_bus import IEventBus


class SceneService:
    """场景应用服务
    
    协调场景相关的业务流程，管理场景生命周期。
    负责：
    - 场景创建、更新、发布、禁用
    - 场景定义校验
    - 发布领域事件
    """
    
    def __init__(
        self,
        scene_repository: ISceneRepository,
        scene_validator: ISceneValidator,
        event_bus: IEventBus
    ):
        """初始化场景应用服务
        
        Args:
            scene_repository: 场景仓储接口
            scene_validator: 场景校验器接口
            event_bus: 事件总线接口
        """
        self._scene_repository = scene_repository
        self._scene_validator = scene_validator
        self._event_bus = event_bus
    
    async def create_scene(
        self,
        name: str,
        description: Optional[str] = None
    ) -> str:
        """创建场景（草稿状态）
        
        Args:
            name: 场景名称
            description: 场景描述（可选）
            
        Returns:
            新场景的ID
        """
        # 生成场景ID
        scene_id = str(uuid.uuid4())
        
        # 使用工厂方法创建场景聚合根
        scene = SceneAggregate.create(
            scene_id=scene_id,
            name=name,
            description=description
        )
        
        # 持久化场景
        await self._scene_repository.save(scene)
        
        return scene_id
    
    async def update_scene(
        self,
        scene_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> None:
        """更新场景基本信息
        
        Args:
            scene_id: 场景ID
            name: 新的场景名称（可选）
            description: 新的场景描述（可选）
            
        Raises:
            ValueError: 场景不存在
        """
        scene = await self._scene_repository.find_by_id(scene_id)
        if not scene:
            raise ValueError(f"场景不存在: {scene_id}")
        
        if name:
            scene.update_name(name)
        if description is not None:
            scene.update_description(description)
        
        await self._scene_repository.save(scene)
    
    async def update_scene_definition(
        self,
        scene_id: str,
        definition: SceneDefinition
    ) -> List[str]:
        """更新场景定义
        
        Args:
            scene_id: 场景ID
            definition: 新的场景定义
            
        Returns:
            校验错误列表，如果为空则更新成功
            
        Raises:
            ValueError: 场景不存在
        """
        scene = await self._scene_repository.find_by_id(scene_id)
        if not scene:
            raise ValueError(f"场景不存在: {scene_id}")
        
        # 校验场景定义
        validation_errors = await self._scene_validator.validate_definition(definition)
        if validation_errors:
            return validation_errors
        
        # 检查循环依赖
        all_scenes = await self._scene_repository.find_all()
        existing_scene_ids = [s.scene_id for s in all_scenes]
        
        has_circular_dep = await self._scene_validator.check_circular_dependency(
            scene_id=scene_id,
            definition=definition,
            existing_scenes=existing_scene_ids
        )
        if has_circular_dep:
            return ["检测到循环依赖，请检查场景定义"]
        
        # 更新场景定义
        scene.update_definition(definition)
        await self._scene_repository.save(scene)
        
        return []
    
    async def publish_scene(self, scene_id: str) -> List[str]:
        """发布场景
        
        Args:
            scene_id: 场景ID
            
        Returns:
            错误列表，如果为空则发布成功
            
        Raises:
            ValueError: 场景不存在
        """
        scene = await self._scene_repository.find_by_id(scene_id)
        if not scene:
            raise ValueError(f"场景不存在: {scene_id}")
        
        # 检查是否有定义
        if not scene.definition:
            return ["场景必须有定义才能发布"]
        
        # 校验场景定义
        validation_errors = await self._scene_validator.validate_definition(scene.definition)
        if validation_errors:
            return validation_errors
        
        try:
            scene.publish()
        except ValueError as e:
            return [str(e)]
        
        await self._scene_repository.save(scene)
        
        # 发布领域事件
        events = scene.get_domain_events()
        await self._event_bus.publish_all(events)
        scene.clear_domain_events()
        
        return []
    
    async def disable_scene(self, scene_id: str) -> None:
        """禁用场景
        
        Args:
            scene_id: 场景ID
            
        Raises:
            ValueError: 场景不存在
        """
        scene = await self._scene_repository.find_by_id(scene_id)
        if not scene:
            raise ValueError(f"场景不存在: {scene_id}")
        
        scene.disable()
        
        await self._scene_repository.save(scene)
        
        # 发布领域事件
        events = scene.get_domain_events()
        await self._event_bus.publish_all(events)
        scene.clear_domain_events()
    
    async def get_scene(self, scene_id: str) -> Optional[SceneAggregate]:
        """获取场景详情
        
        Args:
            scene_id: 场景ID
            
        Returns:
            场景聚合根，如果不存在则返回None
        """
        return await self._scene_repository.find_by_id(scene_id)
    
    async def get_scene_definition(self, scene_id: str) -> Optional[SceneDefinition]:
        """获取场景定义
        
        Args:
            scene_id: 场景ID
            
        Returns:
            场景定义，如果不存在则返回None
        """
        scene = await self._scene_repository.find_by_id(scene_id)
        if not scene:
            return None
        return scene.definition
    
    async def list_scenes(
        self,
        status: Optional[SceneStatus] = None
    ) -> List[SceneAggregate]:
        """查询场景列表
        
        Args:
            status: 可选的状态过滤器
            
        Returns:
            场景列表
        """
        if status:
            return await self._scene_repository.find_by_status(status)
        return await self._scene_repository.find_all()
    
    async def list_published_scenes(self) -> List[SceneAggregate]:
        """获取所有已发布的场景
        
        Returns:
            已发布的场景列表
        """
        return await self._scene_repository.find_by_status(SceneStatus.PUBLISHED)
    
    async def delete_scene(self, scene_id: str) -> None:
        """删除场景
        
        Args:
            scene_id: 场景ID
            
        Raises:
            ValueError: 场景不存在
        """
        scene = await self._scene_repository.find_by_id(scene_id)
        if not scene:
            raise ValueError(f"场景不存在: {scene_id}")
        
        await self._scene_repository.delete(scene_id)
