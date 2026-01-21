from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.database import get_current_session_factory
from src.infrastructure.persistence.repositories.device_log_repository_impl import DeviceLogRepositoryImpl

router = APIRouter(prefix="/api/device-logs", tags=["device-logs"])

async def get_db():
    session_factory = get_current_session_factory()
    async with session_factory() as session:
        yield session

async def get_device_log_repo(session: AsyncSession = Depends(get_db)):
    return DeviceLogRepositoryImpl(session)

@router.get("/stats/today")
async def get_today_stats(
    repo: DeviceLogRepositoryImpl = Depends(get_device_log_repo)
) -> Dict[str, int]:
    """获取今日设备日志统计"""
    count = await repo.count_today_logs()
    return {"count": count}

@router.get("")
async def list_device_logs(
    page: int = 1,
    page_size: int = 50,
    repo: DeviceLogRepositoryImpl = Depends(get_device_log_repo)
) -> Dict[str, Any]:
    """分页获取设备日志"""
    if page < 1: page = 1
    if page_size < 1: page_size = 50
    if page_size > 100: page_size = 100
        
    skip = (page - 1) * page_size
    logs = await repo.find_all_paginated(skip=skip, limit=page_size)
    
    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "execution_id": log.execution_id,
            "step_number": log.step_number,
            "action_type": log.action_type,
            "target": log.target,
            "command": log.command,
            "parameters": log.parameters,
            "response": log.response,
            "duration_ms": log.duration_ms,
            "success": log.success,
            "error_message": log.error_message,
            "scene_name": log.execution.scene.name if log.execution and log.execution.scene else "Unknown Scene",
            "created_at": log.created_at.isoformat() if log.created_at else None
        })
        
    return {
        "items": result,
        "page": page,
        "page_size": page_size
    }
