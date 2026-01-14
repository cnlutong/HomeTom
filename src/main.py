import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import device_router
from src.infrastructure.persistence.database import init_database, create_all_tables

app = FastAPI(title="HomeTom API", version="1.0.0")

# 配置 CORS，允许前端开发服务器跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段允许所有源，生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(device_router.router)

@app.on_event("startup")
async def startup_event():
    # 初始化数据库为 PostgreSQL 并创建表
    from src.infrastructure.persistence.database import DatabaseConfig
    
    config = DatabaseConfig.postgresql(
        host="10.0.3.10",
        port=5432,
        user="user_s4DTX3",
        password="password_yrHKAp",
        database="user_s4DTX3"
    )
    
    await init_database(config)
    await create_all_tables()
    await sync_initial_devices()

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
