"""编排应用服务"""

import uuid
from typing import Optional, List, Dict, Any

from ...domain.Scene.aggregates.scene_aggregate import SceneAggregate, SceneStatus
from ...domain.Scene.repositories.scene_repository import ISceneRepository
from ...domain.Device.repositories.device_repository import IDeviceRepository
from ...domain.Execution.aggregates.execution_aggregate import ExecutionAggregate
from ...domain.Execution.repositories.execution_repository import IExecutionRepository
from ...domain.Execution.services.workflow_engine import IWorkflowEngine
from ...domain.Execution.value_objects.execution_context import ExecutionContext
from ...domain.Execution.value_objects.retry_policy import RetryPolicy
from ...infrastructure.messaging.event_bus import IEventBus


class OrchestrationService:
    """编排应用服务
    
    协调场景执行，是三个上下文（Device、Scene、Execution）的协调者。
    负责：
    - 触发场景执行
    - 协调工作流引擎执行场景
    - 查询执行状态和详情
    - 发布领域事件
    """
    
    def __init__(
        self,
        scene_repository: ISceneRepository,
        device_repository: IDeviceRepository,
        execution_repository: IExecutionRepository,
        workflow_engine: IWorkflowEngine,
        event_bus: IEventBus
    ):
        """初始化编排应用服务
        
        Args:
            scene_repository: 场景仓储接口
            device_repository: 设备仓储接口
            execution_repository: 执行仓储接口
            workflow_engine: 工作流引擎接口
            event_bus: 事件总线接口
        """
        self._scene_repository = scene_repository
        self._device_repository = device_repository
        self._execution_repository = execution_repository
        self._workflow_engine = workflow_engine
        self._event_bus = event_bus
    
    async def trigger_execution(
        self,
        scene_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        retry_policy: Optional[RetryPolicy] = None
    ) -> str:
        """手动触发场景执行
        
        Args:
            scene_id: 场景ID
            parameters: 执行参数（可选）
            retry_policy: 重试策略（可选）
            
        Returns:
            新执行的ID
            
        Raises:
            ValueError: 场景不存在或未发布
        """
        # 获取场景
        scene = await self._scene_repository.find_by_id(scene_id)
        if not scene:
            raise ValueError(f"场景不存在: {scene_id}")
        
        if scene.status != SceneStatus.PUBLISHED:
            raise ValueError(f"只能执行已发布的场景，当前状态: {scene.status.value}")
        
        if not scene.definition:
            raise ValueError(f"场景缺少定义: {scene_id}")
        
        # 生成执行ID
        execution_id = str(uuid.uuid4())
        
        # 创建执行上下文
        context = ExecutionContext(
            scene_id=scene_id,
            scene_version=1,  # MVP阶段始终为版本1
            parameters=parameters or {},
            call_chain=[scene_id]  # 初始调用链包含当前场景
        )
        
        # 创建执行聚合根
        execution = ExecutionAggregate(
            execution_id=execution_id,
            context=context,
            retry_policy=retry_policy
        )
        
        # 持久化执行
        await self._execution_repository.save(execution)
        
        # 发布执行开始事件
        events = execution.get_domain_events()
        await self._event_bus.publish_all(events)
        execution.clear_domain_events()
        
        return execution_id
    
    async def execute_scene(self, execution_id: str) -> Dict[str, Any]:
        """执行场景工作流
        
        Args:
            execution_id: 执行ID
            
        Returns:
            执行结果
            
        Raises:
            ValueError: 执行不存在或已完成
        """
        # 获取执行
        execution = await self._execution_repository.find_by_id(execution_id)
        if not execution:
            raise ValueError(f"执行不存在: {execution_id}")
        
        if execution.is_completed:
            raise ValueError(f"执行已完成: {execution_id}")
        
        # 获取场景定义
        scene = await self._scene_repository.find_by_id(execution.context.scene_id)
        if not scene or not scene.definition:
            execution.fail("场景不存在或缺少定义")
            await self._execution_repository.save(execution)
            return {"success": False, "error": "场景不存在或缺少定义"}
        
        # 开始执行
        execution.start()
        
        try:
            # 委托给工作流引擎执行
            await self._workflow_engine.execute(execution, scene.definition)
            
            # 标记执行成功
            execution.succeed()
            result = {"success": True, "execution_id": execution_id}
            
        except Exception as e:
            # 尝试重试
            if execution.retry():
                # 保存重试状态，稍后可再次调用 execute_scene
                await self._execution_repository.save(execution)
                return {"success": False, "error": str(e), "retry_available": True}
            
            # 标记执行失败
            execution.fail(str(e))
            result = {"success": False, "error": str(e), "retry_available": False}
        
        # 持久化执行结果
        await self._execution_repository.save(execution)
        
        # 发布领域事件
        events = execution.get_domain_events()
        await self._event_bus.publish_all(events)
        execution.clear_domain_events()
        
        return result
    
    async def trigger_and_execute(
        self,
        scene_id: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """触发并立即执行场景（便捷方法）
        
        Args:
            scene_id: 场景ID
            parameters: 执行参数（可选）
            
        Returns:
            执行结果
        """
        execution_id = await self.trigger_execution(scene_id, parameters)
        return await self.execute_scene(execution_id)
    
    async def get_execution(self, execution_id: str) -> Optional[ExecutionAggregate]:
        """获取执行详情
        
        Args:
            execution_id: 执行ID
            
        Returns:
            执行聚合根，如果不存在则返回None
        """
        return await self._execution_repository.find_by_id(execution_id)
    
    async def get_execution_details(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """获取执行详情（结构化格式）
        
        Args:
            execution_id: 执行ID
            
        Returns:
            执行详情字典，如果不存在则返回None
        """
        execution = await self._execution_repository.find_by_id(execution_id)
        if not execution:
            return None
        
        return {
            "execution_id": execution.execution_id,
            "scene_id": execution.context.scene_id,
            "scene_version": execution.context.scene_version,
            "parameters": execution.context.parameters,
            "is_completed": execution.is_completed,
            "retry_policy": {
                "max_retries": execution.retry_policy.max_retries,
                "retry_interval": execution.retry_policy.retry_interval
            }
        }
    
    async def list_executions(
        self,
        scene_id: Optional[str] = None
    ) -> List[ExecutionAggregate]:
        """查询执行列表
        
        Args:
            scene_id: 可选的场景ID过滤器
            
        Returns:
            执行列表
        """
        if scene_id:
            return await self._execution_repository.find_by_scene_id(scene_id)
        return await self._execution_repository.find_all()
    
    async def list_executions_for_scene(self, scene_id: str) -> List[ExecutionAggregate]:
        """获取场景的所有执行记录
        
        Args:
            scene_id: 场景ID
            
        Returns:
            执行列表
        """
        return await self._execution_repository.find_by_scene_id(scene_id)
