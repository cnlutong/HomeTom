"""
依赖注入配置（优化版）
优化建议 #13：改进依赖注入，支持测试
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import aiosqlite

from config import config
from infrastructure.hal.client import HALClient, MockHALClient
from infrastructure.state_manager import StateManager
from infrastructure.database.connection import get_db_connection, init_database
from infrastructure.database.repositories import DeviceRepository, SceneRepository
from application.event_bus import EventBus
from application.device_service import DeviceService
from application.scene_service import SceneService
from domain.scene_engine import ConditionEvaluator, SceneExecutor, SceneScheduler


# ========== 全局单例 ==========

_hal_client: HALClient = None
_state_manager: StateManager = None
_event_bus: EventBus = None
_scene_scheduler: SceneScheduler = None


# ========== HAL 客户端 ==========

def get_hal_client() -> HALClient:
    """
    获取 HAL 客户端（单例）
    支持测试模式（优化建议 #13）
    """
    global _hal_client
    
    if _hal_client is None:
        if config.TESTING:
            _hal_client = MockHALClient()
        else:
            _hal_client = HALClient()
    
    return _hal_client


# ========== 状态管理器 ==========

def get_state_manager() -> StateManager:
    """获取状态管理器（单例）"""
    global _state_manager
    
    if _state_manager is None:
        _state_manager = StateManager()
    
    return _state_manager


# ========== 事件总线 ==========

def get_event_bus() -> EventBus:
    """获取事件总线（单例）"""
    global _event_bus
    
    if _event_bus is None:
        _event_bus = EventBus()
    
    return _event_bus


# ========== 场景调度器 ==========

def get_scene_scheduler() -> SceneScheduler:
    """获取场景调度器（单例）"""
    global _scene_scheduler
    
    if _scene_scheduler is None:
        _scene_scheduler = SceneScheduler()
    
    return _scene_scheduler


# ========== 数据库依赖 ==========

async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """获取数据库连接"""
    async for db in get_db_connection():
        yield db


def get_device_repository(db: aiosqlite.Connection = Depends(get_db)) -> DeviceRepository:
    """获取设备仓储"""
    return DeviceRepository(db)


def get_scene_repository(db: aiosqlite.Connection = Depends(get_db)) -> SceneRepository:
    """获取场景仓储"""
    return SceneRepository(db)


# ========== 服务依赖 ==========

def get_device_service(
    db: aiosqlite.Connection = Depends(get_db)
) -> DeviceService:
    """获取设备服务"""
    device_repo = DeviceRepository(db)
    hal_client = get_hal_client()
    state_manager = get_state_manager()
    event_bus = get_event_bus()
    
    return DeviceService(
        device_repo=device_repo,
        hal_client=hal_client,
        state_manager=state_manager,
        event_bus=event_bus
    )


def get_scene_service(
    db: aiosqlite.Connection = Depends(get_db)
) -> SceneService:
    """获取场景服务"""
    scene_repo = SceneRepository(db)
    hal_client = get_hal_client()
    state_manager = get_state_manager()
    event_bus = get_event_bus()
    scene_scheduler = get_scene_scheduler()
    
    # 创建场景执行器
    condition_evaluator = ConditionEvaluator()
    scene_executor = SceneExecutor(
        hal_client=hal_client,
        condition_evaluator=condition_evaluator,
        state_manager=state_manager
    )
    
    return SceneService(
        scene_repo=scene_repo,
        scene_executor=scene_executor,
        scene_scheduler=scene_scheduler,
        event_bus=event_bus
    )


# ========== 启动和关闭处理 ==========

async def startup_handler():
    """应用启动处理"""
    try:
        # 1. 初始化数据库
        print("📦 初始化数据库...")
        await init_database()
        
        # 2. 初始化全局组件
        print("🔧 初始化全局组件...")
        hal_client = get_hal_client()
        state_manager = get_state_manager()
        event_bus = get_event_bus()
        scene_scheduler = get_scene_scheduler()
        
        # 3. 检查 HAL 连接
        print("🔌 检查 HAL 连接...")
        if await hal_client.health_check():
            print("✓ HAL 连接成功")
        else:
            print("⚠ HAL 连接失败，将使用 Mock 模式")
        
        # 4. 加载设备并初始化状态
        print("📱 加载设备状态...")
        async for db in get_db_connection():
            device_repo = DeviceRepository(db)
            devices = await device_repo.get_all()
            
            for device in devices:
                try:
                    state = await hal_client.get_device_state(device.id)
                    await state_manager.set_state(device.id, state)
                except Exception as e:
                    print(f"⚠ 加载设备状态失败 {device.id}: {e}")
            
            print(f"✓ 已加载 {len(devices)} 个设备")
            
            # 5. 加载并启动场景
            print("🎬 加载活动场景...")
            scene_repo = SceneRepository(db)
            active_scenes = await scene_repo.get_all(active_only=True)
            
            # 创建场景执行器
            condition_evaluator = ConditionEvaluator()
            scene_executor = SceneExecutor(
                hal_client=hal_client,
                condition_evaluator=condition_evaluator,
                state_manager=state_manager
            )
            
            # 注册场景到调度器
            for scene in active_scenes:
                try:
                    # 创建临时 scene_service 来触发场景
                    async def trigger_callback(s):
                        scene_service = SceneService(
                            scene_repo=scene_repo,
                            scene_executor=scene_executor,
                            scene_scheduler=scene_scheduler,
                            event_bus=event_bus
                        )
                        await scene_service.trigger_scene(s.id, "auto")
                    
                    scene_scheduler.register_scene(scene, trigger_callback)
                except Exception as e:
                    print(f"⚠ 注册场景失败 {scene.name}: {e}")
            
            print(f"✓ 已加载 {len(active_scenes)} 个活动场景")
        
        # 6. 启动调度器
        print("⏰ 启动场景调度器...")
        scene_scheduler.start()
        
        # 7. 设置 WebSocket 事件
        print("🌐 设置 WebSocket 事件...")
        from api.websocket import setup_websocket_events
        setup_websocket_events(event_bus)
        
        print("\n" + "="*50)
        print("✅ HomeTom 控制器启动成功！")
        print(f"📍 API 地址: http://0.0.0.0:8000")
        print(f"📍 文档地址: http://0.0.0.0:8000/docs")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        raise


async def shutdown_handler():
    """应用关闭处理"""
    try:
        # 1. 关闭调度器
        scene_scheduler = get_scene_scheduler()
        scene_scheduler.shutdown()
        
        # 2. 关闭 HAL 客户端
        hal_client = get_hal_client()
        await hal_client.close()
        
        # 3. 清空状态
        state_manager = get_state_manager()
        await state_manager.clear()
        
        print("✓ 控制器已安全关闭")
        
    except Exception as e:
        print(f"⚠ 关闭时出错: {e}")


# 导入 Depends（用于 FastAPI）
from fastapi import Depends

