"""
系统 API 路由
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any

from infrastructure.state_manager import StateManager
from infrastructure.hal.client import HALClient


router = APIRouter(prefix="/api/system", tags=["system"])


# ========== 响应模型 ==========

class SystemStatusResponse(BaseModel):
    status: str
    hal_connected: bool
    device_count: int
    version: str = "1.0.0"


# ========== 路由处理器 ==========

@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(
    state_manager: StateManager = Depends(),
    hal_client: HALClient = Depends()
):
    """获取系统状态"""
    try:
        hal_connected = await hal_client.health_check()
        device_count = state_manager.get_device_count()
        
        return SystemStatusResponse(
            status="running",
            hal_connected=hal_connected,
            device_count=device_count
        )
    except Exception as e:
        return SystemStatusResponse(
            status="error",
            hal_connected=False,
            device_count=0
        )


@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}

