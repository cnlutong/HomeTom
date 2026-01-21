from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.database import get_current_session_factory
from src.infrastructure.persistence.repositories.execution_repository_impl import ExecutionRepositoryImpl

router = APIRouter(prefix="/api/executions", tags=["executions"])

# 依赖项：获取数据库会话
async def get_db():
    session_factory = get_current_session_factory()
    async with session_factory() as session:
        yield session

# 依赖项：获取执行仓储
async def get_execution_repo(session: AsyncSession = Depends(get_db)):
    return ExecutionRepositoryImpl(session)

@router.get("/stats/today")
async def get_today_stats(
    repo: ExecutionRepositoryImpl = Depends(get_execution_repo)
) -> Dict[str, int]:
    """获取今日执行统计"""
    count = await repo.count_today_executions()
    return {"count": count}

@router.get("")
async def list_executions(
    page: int = 1,
    page_size: int = 20,
    repo: ExecutionRepositoryImpl = Depends(get_execution_repo)
) -> Dict[str, Any]:
    """分页获取执行记录"""
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20
    if page_size > 100:
        page_size = 100
        
    skip = (page - 1) * page_size
    executions = await repo.find_all_paginated(skip=skip, limit=page_size)
    
    # 转换为前端友好的格式
    result = []
    for exec in executions:
        result_payload = {
            "id": exec.execution_id,
            "scene_id": exec.context.scene_id,
            "status": exec.result.status.value if exec.result else "running",
            "started_at": exec.started_at.isoformat() if exec.started_at else None,
            "ended_at": exec.ended_at.isoformat() if exec.ended_at else None,
            "duration": (exec.ended_at - exec.started_at).total_seconds() if exec.ended_at and exec.started_at else None,
            "error_code": exec.result.error_code if exec.result else None,
            "error_message": exec.result.error_message if exec.result else None,
            "trigger_source": exec.context.trigger_source,
            "scene_name": exec.scene_name or "Unknown Scene",
            "logs_count": len(exec.logs) if exec.logs else 0
        }
        result.append(result_payload)
        
    return {
        "items": result,
        "page": page,
        "page_size": page_size
        # Total count could be added if needed, but keeping it simple for now
    }
