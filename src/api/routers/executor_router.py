"""执行器路由模块

提供执行器 (Orchestrator/Executor) 的 REST API 端点。
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.database import get_current_session_factory
from src.infrastructure.persistence.repositories.executor_repository_impl import ExecutorRepositoryImpl
from src.infrastructure.persistence.repositories.scene_repository_impl import SceneRepositoryImpl

router = APIRouter(prefix="/api/executors", tags=["executors"])


async def get_db():
    session_factory = get_current_session_factory()
    async with session_factory() as session:
        yield session


@router.get("")
async def list_executors(session: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """获取所有执行器列表
    
    Returns:
        执行器列表，包含关联的场景名称
    """
    executor_repo = ExecutorRepositoryImpl(session)
    scene_repo = SceneRepositoryImpl(session)
    
    executors = await executor_repo.find_all()
    
    # 构建场景 ID 到场景对象的映射
    scenes = await scene_repo.find_all()
    scene_map = {scene.scene_id: scene for scene in scenes}
    
    def get_trigger_info(scene):
        """Extract t0 trigger type and config summary from scene definition"""
        if not scene or not scene.definition or not scene.definition.triggers:
            return "Unknown", ""
        
        t0 = scene.definition.triggers[0]
        trigger_type = t0.type.value
        config = t0.config
        
        # Build human-readable config summary
        if trigger_type == "timer":
            schedule = config.get("schedule", "")
            days = config.get("days")
            if days:
                day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                days_str = ", ".join(day_names[d] for d in days if 0 <= d <= 6)
                return trigger_type, f"{schedule} ({days_str})"
            return trigger_type, schedule
        elif trigger_type == "device_event":
            entity = config.get("entity_id", "")
            event = config.get("event_type", "")
            return trigger_type, f"{entity}: {event}"
        elif trigger_type == "manual":
            return trigger_type, "Manual trigger"
        elif trigger_type == "always_on":
            return trigger_type, "Always active"
        
        return trigger_type, str(config) if config else ""
    
    result = []
    for executor in executors:
        scene = scene_map.get(executor.scene_id)
        trigger_type, trigger_config = get_trigger_info(scene)
        
        result.append({
            "id": executor.executor_id,
            "sceneId": executor.scene_id,
            "sceneName": scene.name if scene else "Unknown Scene",
            "triggerType": trigger_type,
            "triggerConfig": trigger_config,
            "status": executor.status.value,
            "createdAt": executor.created_at.isoformat() if executor.created_at else None,
            "updatedAt": executor.updated_at.isoformat() if executor.updated_at else None,
            "lastTriggeredAt": executor.last_triggered_at.isoformat() if executor.last_triggered_at else None,
            "triggerCount": executor.trigger_count,
            "errorMessage": executor.error_message,
            "hasFlow": bool(executor.execution_flow)
        })
    
    return result


@router.get("/stats/today")
async def get_executor_stats(session: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """获取执行器统计信息
    
    Returns:
        执行器统计：总数、活跃数、停止数、错误数
    """
    executor_repo = ExecutorRepositoryImpl(session)
    
    executors = await executor_repo.find_all()
    
    total = len(executors)
    active = sum(1 for e in executors if e.status.value == "active")
    stopped = sum(1 for e in executors if e.status.value == "stopped")
    error = sum(1 for e in executors if e.status.value == "error")
    
    return {
        "total": total,
        "active": active,
        "stopped": stopped,
        "error": error
    }


@router.get("/{executor_id}")
async def get_executor(
    executor_id: str,
    session: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """获取单个执行器详情
    
    Args:
        executor_id: 执行器ID
        
    Returns:
        执行器详情，包含执行流程
    """
    executor_repo = ExecutorRepositoryImpl(session)
    scene_repo = SceneRepositoryImpl(session)
    
    executor = await executor_repo.find_by_id(executor_id)
    if not executor:
        raise HTTPException(status_code=404, detail=f"Executor not found: {executor_id}")
    
    scene = await scene_repo.find_by_id(executor.scene_id)
    scene_name = scene.name if scene else "Unknown Scene"
    
    return {
        "id": executor.executor_id,
        "sceneId": executor.scene_id,
        "sceneName": scene_name,
        "status": executor.status.value,
        "createdAt": executor.created_at.isoformat() if executor.created_at else None,
        "updatedAt": executor.updated_at.isoformat() if executor.updated_at else None,
        "lastTriggeredAt": executor.last_triggered_at.isoformat() if executor.last_triggered_at else None,
        "triggerCount": executor.trigger_count,
        "errorMessage": executor.error_message,
        "executionFlow": executor.execution_flow
    }
