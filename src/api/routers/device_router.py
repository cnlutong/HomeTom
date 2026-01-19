from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.database import get_current_session_factory
from src.infrastructure.persistence.repositories.device_repository_impl import DeviceRepositoryImpl
from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
from src.application.device.DeviceService import DeviceService

router = APIRouter(prefix="/api/devices", tags=["devices"])

# 依赖项：获取数据库会话
async def get_db():
    session_factory = get_current_session_factory()
    async with session_factory() as session:
        yield session

# 依赖项：初始化 DeviceService
async def get_device_service(session: AsyncSession = Depends(get_db)):
    from src.domain.Device.services.device_service_impl import DeviceService as DomainDeviceService
    repo = DeviceRepositoryImpl(session)
    domain_service = DomainDeviceService()
    event_bus = InMemoryEventBus()  # 实际应用中应从全局配置获取
    return DeviceService(repo, domain_service, event_bus)

@router.get("/equipment")
async def get_equipment(service: DeviceService = Depends(get_device_service)) -> List[Dict[str, Any]]:
    """获取所有已启用的设备列表，格式化为前端所需的格式"""
    from src.domain.Device.value_objects.device_status import DeviceStatus
    devices = await service.list_devices(status=DeviceStatus.ENABLED)
    
    result = []
    for device in devices:
        # 简单的图标映射逻辑
        icon = "💡"  # 默认灯光
        if "sensor" in device.entity_id:
            icon = "📡"
        elif "switch" in device.entity_id:
            icon = "🔌"
            
        result.append({
            "id": device.device_id,
            "entity_id": device.entity_id,
            "label": device.name,
            "icon": icon,
            "type": "equipment" if "sensor" not in device.entity_id else "sensor",
            "adapter_type": device.adapter_type,
            "manufacturer": device.manufacturer,
            "capabilities": [cap.to_dict() for cap in device.capabilities.get_all()] if device.capabilities else [],
            "status": device.status.value if hasattr(device.status, 'value') else device.status,
            "created_at": device.created_at.isoformat() if hasattr(device.created_at, 'isoformat') else str(device.created_at)
        })
    
    return result
