"""系统引导模块

提供系统启动时的完整初始化流程，分为五个阶段:
1. 基础设施初始化: 数据库、事件总线、调度器
2. 依赖注入: 创建仓储和服务实例
3. 数据恢复: 设备同步、场景种子数据
4. 运行时设置: 执行器同步、调度器加载
5. 触发就绪: always_on 场景触发、健康检查
"""

import logging
import os
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class InitPhase(Enum):
    """初始化阶段枚举"""
    INFRASTRUCTURE = "infrastructure"
    DEPENDENCY_INJECTION = "dependency_injection"
    DATA_RECOVERY = "data_recovery"
    RUNTIME_SETUP = "runtime_setup"
    TRIGGER_READY = "trigger_ready"


@dataclass
class PhaseResult:
    """阶段执行结果"""
    phase: InitPhase
    success: bool
    message: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class BootstrapResult:
    """引导执行结果"""
    success: bool
    container: Optional["AppContainer"] = None
    phase_results: List[PhaseResult] = field(default_factory=list)
    
    @property
    def errors(self) -> List[str]:
        """获取所有错误"""
        errors = []
        for pr in self.phase_results:
            errors.extend(pr.errors)
        return errors
    
    @property
    def warnings(self) -> List[str]:
        """获取所有警告"""
        warnings = []
        for pr in self.phase_results:
            warnings.extend(pr.warnings)
        return warnings


class SystemBootstrap:
    """系统引导类
    
    管理应用程序的完整初始化流程，确保各组件按正确顺序初始化。
    
    使用示例:
        bootstrap = SystemBootstrap()
        result = await bootstrap.initialize()
        if result.success:
            app.state.container = result.container
    """
    
    def __init__(
        self,
        db_host: str = None,
        db_port: int = None,
        db_user: str = None,
        db_password: str = None,
        db_name: str = None,
        ha_base_url: str = None,
        ha_token: str = None
    ):
        """初始化引导器
        
        优先使用传入的参数，如果未传入则从配置文件读取。
        
        Args:
            db_host: 数据库主机
            db_port: 数据库端口
            db_user: 数据库用户
            db_password: 数据库密码
            db_name: 数据库名称
            ha_base_url: Home Assistant API URL
            ha_token: Home Assistant 访问令牌
        """
        # 从配置文件加载配置
        from src.infrastructure.config.settings import get_settings
        settings = get_settings()
        
        # 优先使用传入的参数，否则使用配置文件中的值
        self.db_host = db_host if db_host is not None else settings.database.host
        self.db_port = db_port if db_port is not None else settings.database.port
        self.db_user = db_user if db_user is not None else settings.database.user
        self.db_password = db_password if db_password is not None else settings.database.password
        self.db_name = db_name if db_name is not None else settings.database.name
        self.ha_base_url = ha_base_url if ha_base_url is not None else settings.homeassistant.base_url
        self.ha_token = ha_token if ha_token is not None else settings.homeassistant.token
        
        self._container: Optional["AppContainer"] = None
        self._phase_results: List[PhaseResult] = []
    
    async def initialize(self) -> BootstrapResult:
        """执行完整的系统初始化
        
        按顺序执行五个初始化阶段，任何致命错误将立即终止。
        
        Returns:
            BootstrapResult: 包含初始化状态、容器实例和错误信息
        """
        logger.info("=" * 60)
        logger.info("Starting HomeTom System Initialization...")
        logger.info("=" * 60)
        
        try:
            # Phase 1: 基础设施
            phase1 = await self._phase1_infrastructure()
            self._phase_results.append(phase1)
            if not phase1.success:
                return self._create_failure_result()
            
            # Phase 2: 依赖注入
            phase2 = await self._phase2_dependency_injection()
            self._phase_results.append(phase2)
            if not phase2.success:
                return self._create_failure_result()
            
            # Phase 3: 数据恢复
            phase3 = await self._phase3_data_recovery()
            self._phase_results.append(phase3)
            # Phase 3 失败不终止，继续执行
            
            # Phase 4: 运行时设置
            phase4 = await self._phase4_runtime_setup()
            self._phase_results.append(phase4)
            # Phase 4 失败不终止，继续执行
            
            # Phase 5: 触发就绪
            phase5 = await self._phase5_trigger_ready()
            self._phase_results.append(phase5)
            
            # 设置全局容器
            from .container import set_container
            set_container(self._container)
            
            logger.info("=" * 60)
            logger.info("HomeTom System Initialization COMPLETED")
            logger.info("=" * 60)
            
            return BootstrapResult(
                success=True,
                container=self._container,
                phase_results=self._phase_results
            )
            
        except Exception as e:
            logger.error(f"Fatal error during initialization: {e}", exc_info=True)
            return BootstrapResult(
                success=False,
                container=None,
                phase_results=self._phase_results
            )
    
    def _create_failure_result(self) -> BootstrapResult:
        """创建失败结果"""
        return BootstrapResult(
            success=False,
            container=None,
            phase_results=self._phase_results
        )
    
    async def _phase1_infrastructure(self) -> PhaseResult:
        """Phase 1: 基础设施初始化
        
        初始化数据库、事件总线和调度器。
        这些是系统运行的基础，失败将导致启动终止。
        """
        logger.info("[Phase 1] Initializing infrastructure...")
        errors = []
        
        try:
            # 1.1 数据库连接
            from src.infrastructure.persistence.database import (
                DatabaseConfig, init_database, create_all_tables, get_current_session_factory
            )
            
            config = DatabaseConfig.postgresql(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            
            await init_database(config)
            logger.info("  [1.1] Database connection initialized")
            
            # 1.2 创建表
            await create_all_tables()
            logger.info("  [1.2] Database tables created/verified")
            
            # 1.3 事件总线
            from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
            
            event_bus = InMemoryEventBus()
            await event_bus.start()
            logger.info("  [1.3] Event bus started")
            
            # 1.4 调度器
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            
            scheduler = AsyncIOScheduler()
            scheduler.start()
            logger.info("  [1.4] Scheduler started")
            
            # 创建容器 (部分初始化)
            from .container import AppContainer
            
            self._container = AppContainer(
                session_factory=get_current_session_factory(),
                event_bus=event_bus,
                scheduler=scheduler
            )
            
            logger.info("[Phase 1] Infrastructure initialization COMPLETED")
            return PhaseResult(
                phase=InitPhase.INFRASTRUCTURE,
                success=True,
                message="Infrastructure initialized successfully"
            )
            
        except Exception as e:
            error_msg = f"Infrastructure initialization failed: {e}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
            return PhaseResult(
                phase=InitPhase.INFRASTRUCTURE,
                success=False,
                message="Infrastructure initialization failed",
                errors=errors
            )
    
    async def _phase2_dependency_injection(self) -> PhaseResult:
        """Phase 2: 依赖注入
        
        创建硬件客户端、工作流引擎，注册事件处理器。
        """
        logger.info("[Phase 2] Setting up dependency injection...")
        warnings = []
        
        try:
            # 2.1 硬件客户端
            from src.infrastructure.adapters.hardware_adapter import HomeAssistantClient
            
            try:
                hardware_client = HomeAssistantClient(
                    base_url=self.ha_base_url,
                    access_token=self.ha_token
                )
                self._container.hardware_client = hardware_client
                logger.info("  [2.1] Hardware client created")
            except Exception as e:
                warnings.append(f"Hardware client creation failed: {e}")
                logger.warning(f"  [2.1] Hardware client creation failed (degraded mode): {e}")
            
            # 2.2 工作流引擎组件
            from src.domain.Execution.services.device_manager import DeviceManager
            from src.domain.Execution.services.condition_evaluator import ConditionEvaluator
            from src.domain.Execution.services.workflow_engine_impl import WorkflowEngine
            
            if self._container.hardware_client:
                device_manager = DeviceManager(self._container.hardware_client)
                condition_evaluator = ConditionEvaluator(device_manager)
                workflow_engine = WorkflowEngine(device_manager, condition_evaluator=condition_evaluator)
                self._container.workflow_engine = workflow_engine
                logger.info("  [2.2] Workflow engine initialized")
            else:
                logger.warning("  [2.2] Workflow engine skipped (no hardware client)")
            
            # 2.3 注册事件处理器
            from src.domain.Scene.events.scene_published import ScenePublished
            from src.domain.Scene.events.scene_disabled import SceneDisabled
            from src.domain.Scene.events.scene_created import SceneCreated
            from src.domain.Scene.events.scene_definition_updated import SceneDefinitionUpdated
            from src.domain.Scene.events.scene_deleted import SceneDeleted
            from src.application.handlers.scene_lifecycle_handler import SceneLifecycleHandler
            from src.application.orchestration.OrchestrationService import OrchestrationService
            
            # 创建一个基础的编排服务用于生命周期回调
            orchestration_service = OrchestrationService(
                scene_repository=None,
                device_repository=None,
                execution_repository=None,
                executor_repository=None,
                workflow_engine=None,
                event_bus=None,
                scheduler=self._container.scheduler
            )
            self._container.orchestration_service = orchestration_service
            
            scene_handler = SceneLifecycleHandler(
                self._container.session_factory,
                orchestration_service=orchestration_service
            )
            
            self._container.event_bus.subscribe(SceneCreated, scene_handler.on_scene_created)
            self._container.event_bus.subscribe(SceneDefinitionUpdated, scene_handler.on_scene_definition_updated)
            self._container.event_bus.subscribe(ScenePublished, scene_handler.on_scene_published)
            self._container.event_bus.subscribe(SceneDisabled, scene_handler.on_scene_disabled)
            self._container.event_bus.subscribe(SceneDeleted, scene_handler.on_scene_deleted)
            
            logger.info("  [2.3] Event handlers registered")
            
            logger.info("[Phase 2] Dependency injection COMPLETED")
            return PhaseResult(
                phase=InitPhase.DEPENDENCY_INJECTION,
                success=True,
                message="Dependency injection completed",
                warnings=warnings
            )
            
        except Exception as e:
            error_msg = f"Dependency injection failed: {e}"
            logger.error(error_msg, exc_info=True)
            return PhaseResult(
                phase=InitPhase.DEPENDENCY_INJECTION,
                success=False,
                message="Dependency injection failed",
                errors=[error_msg]
            )
    
    async def _phase3_data_recovery(self) -> PhaseResult:
        """Phase 3: 数据恢复
        
        从 Home Assistant 同步设备，检查并播种示例场景。
        失败不会导致启动终止。
        """
        logger.info("[Phase 3] Recovering data...")
        warnings = []
        
        # 3.1 设备同步
        try:
            await self._sync_devices()
            logger.info("  [3.1] Device sync completed")
        except Exception as e:
            warnings.append(f"Device sync failed: {e}")
            logger.warning(f"  [3.1] Device sync failed (using cached data): {e}")
        
        # 3.2 场景种子数据
        try:
            await self._seed_sample_scenes()
            logger.info("  [3.2] Sample scenes checked/seeded")
        except Exception as e:
            warnings.append(f"Scene seeding failed: {e}")
            logger.warning(f"  [3.2] Scene seeding failed: {e}")
        
        logger.info("[Phase 3] Data recovery COMPLETED")
        return PhaseResult(
            phase=InitPhase.DATA_RECOVERY,
            success=True,
            message="Data recovery completed",
            warnings=warnings
        )
    
    async def _phase4_runtime_setup(self) -> PhaseResult:
        """Phase 4: 运行时设置
        
        同步场景执行器，将激活的执行器注册到调度器。
        """
        logger.info("[Phase 4] Setting up runtime...")
        warnings = []
        
        # 4.1 同步场景执行器
        try:
            await self._sync_scene_executors()
            logger.info("  [4.1] Scene executors synchronized")
        except Exception as e:
            warnings.append(f"Executor sync failed: {e}")
            logger.warning(f"  [4.1] Executor sync failed: {e}")
        
        # 4.2 加载调度器任务
        try:
            await self._load_scheduler_tasks()
            logger.info("  [4.2] Scheduler tasks loaded")
        except Exception as e:
            warnings.append(f"Scheduler task loading failed: {e}")
            logger.warning(f"  [4.2] Scheduler task loading failed: {e}")
        
        logger.info("[Phase 4] Runtime setup COMPLETED")
        return PhaseResult(
            phase=InitPhase.RUNTIME_SETUP,
            success=True,
            message="Runtime setup completed",
            warnings=warnings
        )
    
    async def _phase5_trigger_ready(self) -> PhaseResult:
        """Phase 5: 触发就绪
        
        触发 always_on 类型的场景，执行健康检查，标记系统就绪。
        """
        logger.info("[Phase 5] Triggering ready state...")
        warnings = []
        
        # 5.1 触发 always_on 场景
        try:
            triggered_count = await self._trigger_always_on_scenes()
            logger.info(f"  [5.1] Triggered {triggered_count} always-on scenes")
        except Exception as e:
            warnings.append(f"Always-on trigger failed: {e}")
            logger.warning(f"  [5.1] Always-on trigger failed: {e}")
        
        # 5.2 健康检查
        try:
            health_status = await self._perform_health_check()
            if health_status:
                logger.info("  [5.2] Health check passed")
            else:
                warnings.append("Health check reported issues")
                logger.warning("  [5.2] Health check reported issues")
        except Exception as e:
            warnings.append(f"Health check failed: {e}")
            logger.warning(f"  [5.2] Health check failed: {e}")
        
        logger.info("[Phase 5] System is READY")
        return PhaseResult(
            phase=InitPhase.TRIGGER_READY,
            success=True,
            message="System is ready",
            warnings=warnings
        )
    
    # === 辅助方法 ===
    
    async def _sync_devices(self) -> None:
        """从 Home Assistant 同步设备"""
        from src.infrastructure.persistence.repositories.device_repository_impl import DeviceRepositoryImpl
        from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
        from src.domain.Device.services.device_service_impl import DeviceService as DomainDeviceService
        from src.application.device.DeviceService import DeviceService as AppDeviceService
        from src.infrastructure.adapters.hardware_client_registry import HardwareClientRegistry
        
        if not self._container.hardware_client:
            logger.warning("No hardware client available, skipping device sync")
            return
        
        registry = HardwareClientRegistry()
        registry.register(self._container.hardware_client)
        
        async with self._container.session_factory() as session:
            repo = DeviceRepositoryImpl(session)
            domain_service = DomainDeviceService()
            event_bus = InMemoryEventBus()
            
            app_service = AppDeviceService(repo, domain_service, event_bus)
            
            new_ids = await app_service.sync_devices_from_hardware("homeassistant", registry)
            await session.commit()
            
            logger.info(f"Device sync: {len(new_ids)} new devices added")
    
    async def _seed_sample_scenes(self) -> None:
        """检查并播种示例场景"""
        from src.infrastructure.persistence.repositories.scene_repository_impl import SceneRepositoryImpl
        from src.infrastructure.persistence.repositories.device_repository_impl import DeviceRepositoryImpl
        from src.domain.Scene.aggregates.scene_aggregate import SceneAggregate, SceneStatus
        from src.domain.Scene.value_objects.scene_definition import SceneDefinition
        from src.domain.Scene.value_objects.trigger import Trigger, TriggerType
        from src.domain.Scene.value_objects.action import Action, ActionType
        
        async with self._container.session_factory() as session:
            scene_repo = SceneRepositoryImpl(session)
            device_repo = DeviceRepositoryImpl(session)
            
            # 检查是否已有场景
            existing_scenes = await scene_repo.find_all()
            if existing_scenes:
                logger.info(f"Database has {len(existing_scenes)} scenes, skipping seed")
                return
            
            # 获取设备
            devices = await device_repo.find_all()
            if not devices:
                logger.warning("No devices found, cannot seed sample scene")
                return
            
            # 创建示例场景
            light = next((d for d in devices if "light" in d.entity_id), devices[0])
            sensor = next((d for d in devices if "sensor" in d.entity_id or "binary_sensor" in d.entity_id), devices[0])
            
            trigger = Trigger(
                type=TriggerType.DEVICE_EVENT,
                config={
                    "entity_id": sensor.entity_id,
                    "event_type": "state_changed",
                    "to_state": "on"
                }
            )
            
            action = Action(
                type=ActionType.DEVICE_CONTROL,
                target=light.entity_id,
                command="turn_on",
                parameters={"brightness": 255}
            )
            
            definition = SceneDefinition(
                triggers=[trigger],
                actions=[action],
                conditions=[]
            )
            
            scene = SceneAggregate(
                scene_id="sample-scene-001",
                name="Sample: Light on Motion",
                description="Automatically turn on the light when motion is detected.",
                status=SceneStatus.PUBLISHED,
                definition=definition
            )
            
            await scene_repo.save(scene)
            await session.commit()
            logger.info("Sample scene seeded successfully")
    
    async def _sync_scene_executors(self) -> None:
        """同步场景执行器"""
        from src.infrastructure.persistence.repositories.scene_repository_impl import SceneRepositoryImpl
        from src.infrastructure.persistence.repositories.executor_repository_impl import ExecutorRepositoryImpl
        from src.domain.Scene.aggregates.scene_aggregate import SceneStatus
        from src.domain.Execution.aggregates.scene_executor import SceneExecutor
        from src.application.scene.scene_compiler import compile_execution_flow
        
        async with self._container.session_factory() as session:
            scene_repo = SceneRepositoryImpl(session)
            executor_repo = ExecutorRepositoryImpl(session)
            
            scenes = await scene_repo.find_all()
            
            created_count = 0
            synced_count = 0
            
            for scene in scenes:
                execution_flow = compile_execution_flow(scene)
                executor = await executor_repo.find_by_scene_id(scene.scene_id)
                
                if not executor:
                    # 创建新执行器
                    executor = SceneExecutor.create(scene.scene_id, execution_flow)
                    if scene.status == SceneStatus.PUBLISHED:
                        executor.activate()
                    await executor_repo.save(executor)
                    created_count += 1
                else:
                    # 同步现有执行器
                    executor.update_execution_flow(execution_flow)
                    expected_active = scene.status == SceneStatus.PUBLISHED
                    if expected_active and not executor.is_active:
                        executor.activate()
                        synced_count += 1
                    elif not expected_active and executor.is_active:
                        executor.stop()
                        synced_count += 1
                    await executor_repo.save(executor)
            
            await session.commit()
            logger.info(f"Executor sync: created={created_count}, synced={synced_count}")
    
    async def _load_scheduler_tasks(self) -> None:
        """加载调度器任务"""
        from src.infrastructure.persistence.repositories.executor_repository_impl import ExecutorRepositoryImpl
        
        async with self._container.session_factory() as session:
            executor_repo = ExecutorRepositoryImpl(session)
            
            if self._container.orchestration_service:
                # 临时设置 executor_repository
                self._container.orchestration_service._executor_repository = executor_repo
                await self._container.orchestration_service.load_active_executors()
    
    async def _trigger_always_on_scenes(self) -> int:
        """触发 always_on 类型的场景
        
        Returns:
            触发的场景数量
        """
        from src.infrastructure.persistence.repositories.executor_repository_impl import ExecutorRepositoryImpl
        from src.application.orchestration.OrchestrationService import run_scheduled_job
        import asyncio
        
        triggered_count = 0
        
        async with self._container.session_factory() as session:
            executor_repo = ExecutorRepositoryImpl(session)
            active_executors = await executor_repo.find_all_active()
            
            for executor in active_executors:
                flow = executor.execution_flow
                if not flow or "triggers" not in flow:
                    continue
                
                triggers = flow.get("triggers", [])
                if not triggers:
                    continue
                
                # 检查第一个触发器是否是 always_on
                first_trigger = triggers[0]
                if first_trigger.get("type") == "always_on":
                    asyncio.create_task(run_scheduled_job(executor.scene_id, "always_on"))
                    triggered_count += 1
        
        return triggered_count
    
    async def _perform_health_check(self) -> bool:
        """执行健康检查
        
        Returns:
            True 如果所有检查通过
        """
        checks_passed = True
        
        # 检查数据库连接
        try:
            async with self._container.session_factory() as session:
                from sqlalchemy import text
                await session.execute(text("SELECT 1"))
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            checks_passed = False
        
        # 检查硬件客户端连接
        if self._container.hardware_client:
            try:
                is_connected = await self._container.hardware_client.check_connection()
                if not is_connected:
                    logger.warning("Hardware client connection check failed")
                    checks_passed = False
            except Exception as e:
                logger.warning(f"Hardware client health check failed: {e}")
                checks_passed = False
        
        # 检查调度器状态
        if not self._container.scheduler.running:
            logger.warning("Scheduler is not running")
            checks_passed = False
        
        # 检查事件总线状态
        if not self._container.event_bus.is_running:
            logger.warning("Event bus is not running")
            checks_passed = False
        
        return checks_passed
