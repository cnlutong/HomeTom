"""应用依赖容器

提供应用程序的依赖注入容器，集中管理所有核心服务和仓储实例。
"""

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from src.infrastructure.messaging.event_bus import IEventBus
    from src.infrastructure.adapters.hardware_client import IHardwareClient
    from src.domain.Scene.repositories.scene_repository import ISceneRepository
    from src.domain.Device.repositories.device_repository import IDeviceRepository
    from src.domain.Execution.repositories.execution_repository import IExecutionRepository
    from src.domain.Execution.repositories.executor_repository import IExecutorRepository
    from src.application.orchestration.OrchestrationService import OrchestrationService
    from src.application.device.DeviceService import DeviceService
    from src.application.scene.SceneService import SceneService
    from src.domain.Execution.services.workflow_engine import IWorkflowEngine


@dataclass
class AppContainer:
    """应用依赖容器
    
    集中管理应用程序的所有核心依赖，包括:
    - 基础设施层: 数据库会话工厂、事件总线、调度器、硬件客户端
    - 仓储层: 场景、设备、执行、执行器仓储
    - 服务层: 编排服务、设备服务、工作流引擎
    
    Attributes:
        session_factory: 异步数据库会话工厂
        event_bus: 事件总线
        scheduler: 异步调度器
        hardware_client: 硬件客户端 (如 Home Assistant)
        
        scene_repository_factory: 场景仓储工厂函数
        device_repository_factory: 设备仓储工厂函数
        execution_repository_factory: 执行仓储工厂函数
        executor_repository_factory: 执行器仓储工厂函数
        
        workflow_engine: 工作流引擎
        orchestration_service: 编排服务 (可选，延迟初始化)
    """
    
    # 基础设施层
    session_factory: "async_sessionmaker[AsyncSession]"
    event_bus: "IEventBus"
    scheduler: "AsyncIOScheduler"
    hardware_client: Optional["IHardwareClient"] = None
    
    # 工作流引擎
    workflow_engine: Optional["IWorkflowEngine"] = None
    
    # 编排服务 (延迟初始化)
    orchestration_service: Optional["OrchestrationService"] = None
    
    def create_scene_repository(self, session: "AsyncSession") -> "ISceneRepository":
        """创建场景仓储实例
        
        Args:
            session: 数据库会话
            
        Returns:
            场景仓储实例
        """
        from src.infrastructure.persistence.repositories.scene_repository_impl import SceneRepositoryImpl
        return SceneRepositoryImpl(session)
    
    def create_device_repository(self, session: "AsyncSession") -> "IDeviceRepository":
        """创建设备仓储实例
        
        Args:
            session: 数据库会话
            
        Returns:
            设备仓储实例
        """
        from src.infrastructure.persistence.repositories.device_repository_impl import DeviceRepositoryImpl
        return DeviceRepositoryImpl(session)
    
    def create_execution_repository(self, session: "AsyncSession") -> "IExecutionRepository":
        """创建执行仓储实例
        
        Args:
            session: 数据库会话
            
        Returns:
            执行仓储实例
        """
        from src.infrastructure.persistence.repositories.execution_repository_impl import ExecutionRepositoryImpl
        return ExecutionRepositoryImpl(session)
    
    def create_executor_repository(self, session: "AsyncSession") -> "IExecutorRepository":
        """创建执行器仓储实例
        
        Args:
            session: 数据库会话
            
        Returns:
            执行器仓储实例
        """
        from src.infrastructure.persistence.repositories.executor_repository_impl import ExecutorRepositoryImpl
        return ExecutorRepositoryImpl(session)
    
    def create_orchestration_service(self, session: "AsyncSession") -> "OrchestrationService":
        """创建编排服务实例
        
        Args:
            session: 数据库会话
            
        Returns:
            编排服务实例
        """
        from src.application.orchestration.OrchestrationService import OrchestrationService
        
        return OrchestrationService(
            scene_repository=self.create_scene_repository(session),
            device_repository=self.create_device_repository(session),
            execution_repository=self.create_execution_repository(session),
            executor_repository=self.create_executor_repository(session),
            workflow_engine=self.workflow_engine,
            event_bus=self.event_bus,
            scheduler=self.scheduler
        )


# 全局容器实例
_container: Optional[AppContainer] = None


def get_container() -> AppContainer:
    """获取全局容器实例
    
    Returns:
        应用依赖容器
        
    Raises:
        RuntimeError: 如果容器未初始化
    """
    if _container is None:
        raise RuntimeError("应用容器未初始化，请先调用 SystemBootstrap.initialize()")
    return _container


def set_container(container: AppContainer) -> None:
    """设置全局容器实例
    
    Args:
        container: 应用依赖容器
    """
    global _container
    _container = container
