"""
场景服务
提供场景管理和执行的业务逻辑
"""
from typing import List, Dict, Any

from domain.entities.scene import Scene, SceneDefinition
from domain.scene_engine import SceneParser, SceneExecutor, SceneScheduler
from infrastructure.database.repositories import SceneRepository
from application.event_bus import EventBus, EventTypes
from exceptions import SceneNotFoundError, SceneDefinitionError


class SceneService:
    """场景服务"""
    
    def __init__(
        self,
        scene_repo: SceneRepository,
        scene_executor: SceneExecutor,
        scene_scheduler: SceneScheduler,
        event_bus: EventBus
    ):
        self.scene_repo = scene_repo
        self.scene_executor = scene_executor
        self.scene_scheduler = scene_scheduler
        self.event_bus = event_bus
    
    async def get_all_scenes(self, active_only: bool = False) -> List[Scene]:
        """
        获取所有场景
        
        Args:
            active_only: 是否只获取激活的场景
        """
        return await self.scene_repo.get_all(active_only=active_only)
    
    async def get_scene(self, scene_id: str) -> Scene:
        """
        获取场景详情
        
        Args:
            scene_id: 场景 ID
            
        Returns:
            Scene: 场景实体
            
        Raises:
            SceneNotFoundError: 场景不存在
        """
        scene = await self.scene_repo.get_by_id(scene_id)
        if not scene:
            raise SceneNotFoundError(scene_id)
        return scene
    
    async def create_scene(self, scene_data: Dict[str, Any]) -> Scene:
        """
        创建场景
        
        Args:
            scene_data: 场景数据
            
        Returns:
            Scene: 创建的场景
            
        Raises:
            SceneDefinitionError: 场景定义错误
        """
        # 解析场景定义
        definition = SceneParser.parse(scene_data["definition"])
        
        # 创建场景实体
        scene = Scene(
            id=scene_data["id"],
            name=scene_data["name"],
            description=scene_data.get("description"),
            definition=definition,
            is_active=scene_data.get("is_active", True)
        )
        
        # 保存到数据库
        await self.scene_repo.save(scene)
        
        # 如果激活，注册到调度器
        if scene.is_active:
            self.scene_scheduler.register_scene(
                scene,
                lambda s: self.trigger_scene(s.id, "auto")
            )
        
        # 发布事件
        await self.event_bus.publish(
            EventTypes.SCENE_ADDED,
            {"scene_id": scene.id, "scene": scene.model_dump()}
        )
        
        return scene
    
    async def update_scene(
        self,
        scene_id: str,
        scene_data: Dict[str, Any]
    ) -> Scene:
        """
        更新场景
        
        Args:
            scene_id: 场景 ID
            scene_data: 场景数据
            
        Returns:
            Scene: 更新后的场景
        """
        # 检查场景是否存在
        existing = await self.scene_repo.get_by_id(scene_id)
        if not existing:
            raise SceneNotFoundError(scene_id)
        
        # 解析新的定义
        definition = SceneParser.parse(scene_data["definition"])
        
        # 更新场景
        scene = Scene(
            id=scene_id,
            name=scene_data.get("name", existing.name),
            description=scene_data.get("description", existing.description),
            definition=definition,
            is_active=scene_data.get("is_active", existing.is_active),
            created_at=existing.created_at
        )
        
        # 保存到数据库
        await self.scene_repo.save(scene)
        
        # 重新注册调度器
        self.scene_scheduler.unregister_scene(scene_id)
        if scene.is_active:
            self.scene_scheduler.register_scene(
                scene,
                lambda s: self.trigger_scene(s.id, "auto")
            )
        
        # 发布事件
        await self.event_bus.publish(
            EventTypes.SCENE_UPDATED,
            {"scene_id": scene.id, "scene": scene.model_dump()}
        )
        
        return scene
    
    async def delete_scene(self, scene_id: str) -> bool:
        """
        删除场景
        
        Args:
            scene_id: 场景 ID
            
        Returns:
            bool: 是否成功
        """
        scene = await self.scene_repo.get_by_id(scene_id)
        if not scene:
            raise SceneNotFoundError(scene_id)
        
        # 从调度器移除
        self.scene_scheduler.unregister_scene(scene_id)
        
        # 从数据库删除
        success = await self.scene_repo.delete(scene_id)
        
        if success:
            # 发布事件
            await self.event_bus.publish(
                EventTypes.SCENE_REMOVED,
                {"scene_id": scene_id}
            )
        
        return success
    
    async def activate_scene(self, scene_id: str, is_active: bool) -> Scene:
        """
        激活/停用场景
        
        Args:
            scene_id: 场景 ID
            is_active: 是否激活
            
        Returns:
            Scene: 更新后的场景
        """
        scene = await self.scene_repo.get_by_id(scene_id)
        if not scene:
            raise SceneNotFoundError(scene_id)
        
        # 更新激活状态
        await self.scene_repo.update_active_status(scene_id, is_active)
        scene.is_active = is_active
        
        # 更新调度器
        if is_active:
            self.scene_scheduler.register_scene(
                scene,
                lambda s: self.trigger_scene(s.id, "auto")
            )
        else:
            self.scene_scheduler.unregister_scene(scene_id)
        
        return scene
    
    async def trigger_scene(
        self,
        scene_id: str,
        triggered_by: str = "manual"
    ) -> Dict[str, Any]:
        """
        触发场景执行
        
        Args:
            scene_id: 场景 ID
            triggered_by: 触发来源
            
        Returns:
            Dict: 执行结果
        """
        scene = await self.scene_repo.get_by_id(scene_id)
        if not scene:
            raise SceneNotFoundError(scene_id)
        
        if not scene.is_active:
            return {
                "status": "skipped",
                "message": "Scene is not active"
            }
        
        # 发布触发事件
        await self.event_bus.publish(
            EventTypes.SCENE_TRIGGERED,
            {
                "scene_id": scene_id,
                "triggered_by": triggered_by
            }
        )
        
        # 执行场景
        result = await self.scene_executor.execute_scene(scene, triggered_by)
        
        # 发布完成或失败事件
        if result.status == "success":
            await self.event_bus.publish(
                EventTypes.SCENE_COMPLETED,
                result.to_dict()
            )
        elif result.status == "failed":
            await self.event_bus.publish(
                EventTypes.SCENE_FAILED,
                result.to_dict()
            )
        
        return result.to_dict()

