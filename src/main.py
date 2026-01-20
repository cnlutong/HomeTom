import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import device_router, scene_router
from src.infrastructure.persistence.database import init_database, create_all_tables

app = FastAPI(title="HomeTom API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:5178",
        "http://localhost:5179",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:5177",
        "http://127.0.0.1:5178",
        "http://127.0.0.1:5179",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(device_router.router)
app.include_router(scene_router.router)

@app.on_event("startup")
async def startup_event():
    # 初始化数据库为 PostgreSQL 并创建表
    from src.infrastructure.persistence.database import DatabaseConfig, get_current_session_factory
    from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
    from src.domain.Scene.events.scene_published import ScenePublished
    from src.domain.Scene.events.scene_disabled import SceneDisabled
    from src.domain.Scene.events.scene_created import SceneCreated
    from src.domain.Scene.events.scene_definition_updated import SceneDefinitionUpdated
    from src.application.handlers.scene_lifecycle_handler import SceneLifecycleHandler
    
    config = DatabaseConfig.postgresql(
        host="10.0.3.10",
        port=5432,
        user="user_s4DTX3",
        password="password_yrHKAp",
        database="user_s4DTX3"
    )
    
    await init_database(config)
    await create_all_tables()
    
    # 初始化全局事件总线
    global_event_bus = InMemoryEventBus()
    await global_event_bus.start()
    app.state.event_bus = global_event_bus
    
    # 注册场景生命周期事件处理器
    session_factory = get_current_session_factory()
    scene_handler = SceneLifecycleHandler(session_factory)
    global_event_bus.subscribe(SceneCreated, scene_handler.on_scene_created)
    global_event_bus.subscribe(SceneDefinitionUpdated, scene_handler.on_scene_definition_updated)
    global_event_bus.subscribe(ScenePublished, scene_handler.on_scene_published)
    global_event_bus.subscribe(SceneDisabled, scene_handler.on_scene_disabled)
    
    print("Global EventBus initialized and SceneLifecycleHandler registered.")
    
    await sync_initial_devices()
    await sync_initial_scenes()


async def sync_initial_scenes():
    """初始化样板场景"""
    from src.infrastructure.persistence.database import get_current_session_factory
    from src.infrastructure.persistence.repositories.scene_repository_impl import SceneRepositoryImpl
    from src.infrastructure.persistence.repositories.device_repository_impl import DeviceRepositoryImpl
    from src.domain.Scene.aggregates.scene_aggregate import SceneAggregate, SceneStatus
    from src.domain.Scene.value_objects.scene_definition import SceneDefinition
    from src.domain.Scene.value_objects.trigger import Trigger, TriggerType
    from src.domain.Scene.value_objects.action import Action, ActionType
    from src.domain.Scene.value_objects.condition import Condition

    session_factory = get_current_session_factory()
    async with session_factory() as session:
        scene_repo = SceneRepositoryImpl(session)
        device_repo = DeviceRepositoryImpl(session)
        
        # 检查是否已有场景
        existing_scenes = await scene_repo.find_all()
        if existing_scenes:
            print(f"Database already has {len(existing_scenes)} scenes. Skipping seed.")
            return

        print("Seeding sample scene...")
        
        # 获取一些设备用于样板
        devices = await device_repo.find_all()
        if not devices:
            print("No devices found. Cannot seed scene.")
            return

        # 找到一个灯和一个传感器（如果有）
        light = next((d for d in devices if "light" in d.entity_id), devices[0])
        sensor = next((d for d in devices if "sensor" in d.entity_id or "binary_sensor" in d.entity_id), devices[0])

        # 创建样板场景：当传感器检测到动作时，打开灯
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
        print("Sample scene seeded successfully.")

async def sync_initial_devices():
    """从模拟 HASS 服务器同步初始设备"""
    from src.infrastructure.persistence.database import get_current_session_factory
    from src.infrastructure.persistence.repositories.device_repository_impl import DeviceRepositoryImpl
    from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
    from src.domain.Device.services.device_service_impl import DeviceService as DomainDeviceService
    from src.application.device.DeviceService import DeviceService as AppDeviceService
    from src.infrastructure.adapters.hardware_adapter import HomeAssistantClient
    from src.infrastructure.adapters.hardware_client_registry import HardwareClientRegistry
    
    # 1. 配置硬件客户端
    # 注意：模拟服务器默认运行在 8123 端口
    ha_client = HomeAssistantClient(
        base_url="http://localhost:8123",
        access_token="test_token"
    )
    
    registry = HardwareClientRegistry()
    registry.register(ha_client)
    
    # 2. 初始化应用服务
    session_factory = get_current_session_factory()
    async with session_factory() as session:
        repo = DeviceRepositoryImpl(session)
        domain_service = DomainDeviceService()
        event_bus = InMemoryEventBus()
        
        app_service = AppDeviceService(repo, domain_service, event_bus)
        
        # 3. 执行同步
        print("Starting device sync from Mock HA Server...")
        new_ids = await app_service.sync_devices_from_hardware("homeassistant", registry)
        
        await session.commit()
        print(f"Device sync completed. Added {len(new_ids)} new devices.")

@app.get("/")
async def root():
    return {"message": "Welcome to HomeTom API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
