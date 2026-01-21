"""编排应用服务"""

import uuid
import logging
import asyncio
from typing import Optional, List, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from ...domain.Scene.aggregates.scene_aggregate import SceneAggregate, SceneStatus
from ...domain.Scene.repositories.scene_repository import ISceneRepository
from ...domain.Device.repositories.device_repository import IDeviceRepository
from ...domain.Execution.aggregates.execution_aggregate import ExecutionAggregate
from ...domain.Execution.repositories.execution_repository import IExecutionRepository
from ...domain.Execution.repositories.executor_repository import IExecutorRepository
from ...domain.Execution.services.workflow_engine import IWorkflowEngine
from ...domain.Execution.value_objects.execution_context import ExecutionContext
from ...domain.Execution.value_objects.retry_policy import RetryPolicy
from ...infrastructure.messaging.event_bus import IEventBus

logger = logging.getLogger(__name__)


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
        executor_repository: IExecutorRepository,
        workflow_engine: IWorkflowEngine,
        event_bus: IEventBus,
        scheduler: Optional[AsyncIOScheduler] = None
    ):
        """初始化编排应用服务
        
        Args:
            scene_repository: 场景仓储接口
            device_repository: 设备仓储接口
            execution_repository: 执行仓储接口
            executor_repository: 执行器仓储接口
            workflow_engine: 工作流引擎接口
            event_bus: 事件总线接口
        """
        self._scene_repository = scene_repository
        self._device_repository = device_repository
        self._execution_repository = execution_repository
        self._executor_repository = executor_repository
        self._workflow_engine = workflow_engine
        self._event_bus = event_bus
        self._scheduler = scheduler if scheduler else AsyncIOScheduler()
        self._execution_jobs: Dict[str, List[str]] = {}  # scene_id -> [job_ids]

    async def start(self) -> None:
        """启动编排服务"""
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("Orchestration Scheduler started.")
        
        await self.load_active_executors()

    async def load_active_executors(self) -> None:
        """加载所有激活的执行器"""
        logger.info("Loading active executors from database...")
        # 注意: 这里的 find_all 可能会返回大量数据，实际生产环境应该有专门的方法只查询 active 的
        # 但考虑到当前仓储接口限制，先获取全部再过滤，或者假设 executor 数量不多
        # TODO: 在 ExecutorRepository 中增加 find_all_active 方法
        all_executors = await self._executor_repository.find_all()
        active_executors = [e for e in all_executors if e.is_active]
        
        count = 0
        for executor in active_executors:
            self.register_executor(executor)
            count += 1
            
        logger.info(f"Loaded {count} active executors.")

    def register_executor(self, executor) -> None:
        """注册执行器到调度器
        
        解析执行器的触发器配置，注册相应的调度任务。
        目前仅支持第一个触发器为 Timer 或 AlwaysOn 的情况。
        """
        scene_id = executor.scene_id
        
        # 先清理旧的任务
        self.unregister_executor(scene_id)
        
        if not executor.is_active:
            logger.warning(f"Executor {executor.executor_id} is not active, skipping registration.")
            return

        flow = executor.execution_flow
        if not flow or "triggers" not in flow:
            return

        triggers = flow["triggers"]
        if not triggers:
            return
            
        # MVP: 仅处理第一个触发器
        t0 = triggers[0]
        trigger_type = t0.get("type")
        config = t0.get("config", {})
        
        logger.info(f"Registering trigger for scene {scene_id}: {trigger_type}")

        if trigger_type == "always_on":
            # Always On: 启动即运行 (异步执行一次)
            # 这是一个一次性的动作，当系统启动或场景发布时触发
            asyncio.create_task(run_scheduled_job(scene_id, "always_on"))
            logger.info(f"Triggered 'always_on' execution for scene {scene_id}")
            
        elif trigger_type == "timer":
            # Timer: 添加调度任务
            schedule = config.get("schedule")
            if not schedule:
                logger.error(f"Timer trigger missing schedule config for scene {scene_id}")
                return

            try:
                # 简单解析：如果是 cron 格式 (5位或6位) 则用 CronTrigger
                # 否则尝试作为 Interval (尚未实现复杂 interval 解析，这里假设 schedule 是 cron 表达式)
                # 实际项目中应该有更严谨的解析逻辑
                
                # 这里直接假设 schedule 是 cron 表达式
                # 格式: "minute hour day month day_of_week"
                job = self._scheduler.add_job(
                    run_scheduled_job, 
                    CronTrigger.from_crontab(schedule),
                    args=[scene_id, "timer"],
                    id=f"scene_{scene_id}_timer",
                    replace_existing=True
                )
                
                if scene_id not in self._execution_jobs:
                    self._execution_jobs[scene_id] = []
                self._execution_jobs[scene_id].append(job.id)
                
                logger.info(f"Scheduled timer job for scene {scene_id}: {schedule}")
                
            except Exception as e:
                logger.error(f"Failed to schedule timer for scene {scene_id}: {e}")

    def unregister_executor(self, scene_id: str) -> None:
        """移除执行器的调度任务"""
        if scene_id in self._execution_jobs:
            for job_id in self._execution_jobs[scene_id]:
                try:
                    self._scheduler.remove_job(job_id)
                    logger.debug(f"Removed job {job_id} for scene {scene_id}")
                except Exception:
                    # Job 可能已经不存在
                    pass
            del self._execution_jobs[scene_id]
    
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
            
        # 检查对应执行器的状态（Phase 3 Persistence）
        executor = await self._executor_repository.find_by_scene_id(scene_id)
        if not executor:
            # 理论上发布场景时必然会创建执行器，如果不存在则属于异常数据
            # 但为了鲁棒性，这里可以尝试创建，或者直接报错
            # 这里选择严格模式：
            raise ValueError(f"场景对应的执行器不存在: {scene_id}")
            
        if executor.status.value != "active":
            # 只有 active 状态的执行器才能运行
            # 除非此处是强制执行（manual），目前暂定 manual 也需要 active 状态
            # 或者我们可以认为 manual 允许执行，但这里按照计划要求检查状态
            raise ValueError(f"执行器未激活，当前状态: {executor.status.value}")
        
        # 更新执行器统计信息
        executor.record_trigger()
        await self._executor_repository.save(executor)
        
        # 生成执行ID
        execution_id = str(uuid.uuid4())
        
        # 创建执行上下文
        context = ExecutionContext(
            scene_id=scene_id,
            trigger_source="manual",
            input_parameters=parameters or {},
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
            
            # 获取执行日志并转换为字典
            logs = [log.to_dict() for log in execution.logs]
            
            # 执行结果已由工作流引擎设置
            result = {
                "success": execution.is_completed and execution.result.is_success() if execution.result else False, 
                "execution_id": execution_id,
                "logs": logs
            }
            
        except Exception as e:
            # 尝试重试
            if execution.retry():
                # 保存重试状态，稍后可再次调用 execute_scene
                await self._execution_repository.save(execution)
                return {"success": False, "error": str(e), "retry_available": True}
            
            # 获取执行日志并转换为字典
            logs = [log.to_dict() for log in execution.logs]
            
            # 标记执行失败
            execution.fail(str(e))
            result = {
                "success": False, 
                "error": str(e), 
                "retry_available": False,
                "logs": logs
            }
        
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
            "trigger_source": execution.context.trigger_source,
            "input_parameters": execution.context.input_parameters,
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


async def run_scheduled_job(scene_id: str, source: str = "timer"):
    """独立的任务执行函数
    
    尝试从全局容器获取依赖，如果容器不可用则回退到创建临时依赖。
    """
    try:
        # 尝试使用全局容器
        from ...application.container import get_container
        
        try:
            container = get_container()
            
            async with container.session_factory() as session:
                service = container.create_orchestration_service(session)
                
                logger.info(f"Executing scheduled job for scene {scene_id} (source: {source})")
                await service.trigger_and_execute(scene_id, {"source": source})
                await session.commit()
                
            return
        except RuntimeError:
            # 容器未初始化，回退到创建临时依赖
            logger.warning("Global container not available, creating temporary dependencies")
        
        # 回退逻辑：创建临时依赖
        from ...infrastructure.persistence.database import get_current_session_factory
        from ...infrastructure.persistence.repositories.scene_repository_impl import SceneRepositoryImpl
        from ...infrastructure.persistence.repositories.device_repository_impl import DeviceRepositoryImpl
        from ...infrastructure.persistence.repositories.execution_repository_impl import ExecutionRepositoryImpl
        from ...infrastructure.persistence.repositories.executor_repository_impl import ExecutorRepositoryImpl
        from ...infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
        from ...domain.Execution.services.workflow_engine_impl import WorkflowEngine
        from ...domain.Execution.services.device_manager import DeviceManager
        from ...domain.Execution.services.condition_evaluator import ConditionEvaluator
        from ...infrastructure.adapters.hardware_adapter import HomeAssistantClient
        import os

        session_factory = get_current_session_factory()
        
        event_bus = InMemoryEventBus() 

        # Hardware Client setup
        ha_base_url = os.environ.get("HA_BASE_URL", "http://localhost:8123")
        ha_token = os.environ.get("HA_TOKEN", "test_token")
        hardware_client = HomeAssistantClient(base_url=ha_base_url, access_token=ha_token)
        device_manager = DeviceManager(hardware_client)
        condition_evaluator = ConditionEvaluator(device_manager)
        workflow_engine = WorkflowEngine(device_manager, condition_evaluator=condition_evaluator)

        async with session_factory() as session:
            service = OrchestrationService(
                scene_repository=SceneRepositoryImpl(session),
                device_repository=DeviceRepositoryImpl(session),
                execution_repository=ExecutionRepositoryImpl(session),
                executor_repository=ExecutorRepositoryImpl(session),
                workflow_engine=workflow_engine,
                event_bus=event_bus,
                scheduler=None
            )
            
            logger.info(f"Executing scheduled job for scene {scene_id} (source: {source})")
            await service.trigger_and_execute(scene_id, {"source": source})
            await session.commit()
            
    except Exception as e:
        logger.error(f"Error executing scheduled job for scene {scene_id}: {e}")
