from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.database import get_current_session_factory
from src.infrastructure.persistence.repositories.scene_repository_impl import SceneRepositoryImpl
from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
from src.application.scene.SceneService import SceneService
from src.domain.Scene.services.scene_validator_impl import SceneValidator
from src.domain.Scene.value_objects.scene_definition import SceneDefinition
from src.domain.Scene.value_objects.trigger import Trigger, TriggerType
from src.domain.Scene.value_objects.condition import Condition
from src.domain.Scene.value_objects.action import Action, ActionType
from src.domain.Scene.aggregates.scene_aggregate import SceneStatus
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/api/scenes", tags=["scenes"])

class AutomationTrigger(BaseModel):
    type: str
    deviceId: str
    capability: str
    state: Any

class AutomationCondition(BaseModel):
    type: str
    deviceId: Optional[str] = None
    capability: Optional[str] = None
    state: Optional[Any] = None
    after: Optional[str] = None
    before: Optional[str] = None
    time: Optional[str] = None

class AutomationAction(BaseModel):
    type: str
    deviceId: str
    capability: str
    value: Any

class AutomationData(BaseModel):
    automationId: Optional[str] = None
    name: str
    isEnabled: bool = True
    triggers: List[AutomationTrigger]
    conditions: List[AutomationCondition]
    actions: List[AutomationAction]
    uiMetadata: Optional[Dict[str, Any]] = None

# 依赖项：获取数据库会话
async def get_db():
    session_factory = get_current_session_factory()
    async with session_factory() as session:
        yield session

# 依赖项：初始化 SceneService
async def get_scene_service(session: AsyncSession = Depends(get_db)):
    repo = SceneRepositoryImpl(session)
    validator = SceneValidator()
    event_bus = InMemoryEventBus()  # 实际应用中应从全局配置获取
    return SceneService(repo, validator, event_bus)

@router.get("")
async def list_scenes(service: SceneService = Depends(get_scene_service)) -> List[Dict[str, Any]]:
    """获取所有场景列表，格式化为前端所需的格式"""
    scenes = await service.list_scenes()
    
    result = []
    for scene in scenes:
        # 统计触发器、条件、动作数量
        trigger_count = len(scene.definition.triggers) if scene.definition and scene.definition.triggers else 0
        condition_count = len(scene.definition.conditions) if scene.definition and scene.definition.conditions else 0
        action_count = len(scene.definition.actions) if scene.definition and scene.definition.actions else 0
        
        # 转换定义为前端通用的 automationData 格式，以便编辑器加载
        automation_data = None
        if scene.definition:
            triggers = []
            for t in scene.definition.triggers:
                entity_id = t.config.get("entity_id", "sensor_unknown_01")
                # 尝试从 entity_id 推断能力
                capability = "motion" if "motion" in entity_id else "temp" if "temp" in entity_id else "sound" if "sound" in entity_id else "state"
                triggers.append({
                    "type": "deviceState",
                    "deviceId": entity_id,
                    "capability": capability,
                    "state": "detected"
                })
            
            conditions = []
            if scene.definition.conditions:
                for c in scene.definition.conditions:
                    # 简单转换
                    conditions.append({
                        "type": "deviceState",
                        "deviceId": c.entity_id,
                        "capability": c.attribute,
                        "state": f"{c.operator} {c.value}"
                    })
            
            actions_list = []
            for a in scene.definition.actions:
                entity_id = a.target
                capability = "onOff"
                if "light" in entity_id or "lamp" in entity_id:
                    capability = "onOff"
                elif "conditioner" in entity_id:
                    capability = "temperature"
                
                actions_list.append({
                    "type": "deviceCommand",
                    "deviceId": entity_id,
                    "capability": capability,
                    "value": True
                })
            
            automation_data = {
                "automationId": scene.scene_id,
                "name": scene.name,
                "isEnabled": scene.status.value == "published",
                "triggers": triggers,
                "conditions": conditions,
                "actions": actions_list,
                "uiMetadata": scene.ui_metadata
            }

        result.append({
            "id": scene.scene_id,
            "name": scene.name,
            "description": scene.description or f"Automation with {trigger_count} trigger(s), {condition_count} condition(s), and {action_count} action(s)",
            "icon": "🏠", # 默认图标
            "isEnabled": scene.status.value == "published",
            "triggerCount": trigger_count,
            "conditionCount": condition_count,
            "actionCount": action_count,
            "nodeCount": trigger_count + condition_count + action_count,
            "activeCount": 1 if scene.status.value == "published" else 0,
            "createdAt": scene.created_at.isoformat() if hasattr(scene.created_at, 'isoformat') else str(scene.created_at),
            "status": scene.status.value,
            "automationData": automation_data
        })
    
    return result

@router.put("/{scene_id}/status")
async def update_scene_status(
    scene_id: str,
    status: str = Query(..., description="Target status: published, disabled, or draft"),
    service: SceneService = Depends(get_scene_service),
    session: AsyncSession = Depends(get_db)
):
    """更新场景状态"""
    try:
        # Normalize status
        status = status.lower()
        
        if status == "published":
            errors = await service.publish_scene(scene_id)
            if errors:
                raise HTTPException(status_code=400, detail=errors[0])
        elif status == "disabled":
            await service.disable_scene(scene_id)
        elif status == "draft":
            # 根据当前状态选择调用 enable_scene 或 revert_to_draft
            scene = await service.get_scene(scene_id)
            if not scene:
                raise HTTPException(status_code=404, detail=f"场景不存在: {scene_id}")
            
            if scene.status == SceneStatus.PUBLISHED:
                await service.revert_to_draft(scene_id)
            elif scene.status == SceneStatus.DISABLED:
                await service.enable_scene(scene_id)
            elif scene.status == SceneStatus.DRAFT:
                pass # Already draft
        else:
            raise HTTPException(status_code=400, detail=f"不支持的状态: {status}")
            
        await session.commit()
        return {"id": scene_id, "status": "success", "new_status": status}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")
@router.post("")
async def save_scene(
    data: AutomationData, 
    service: SceneService = Depends(get_scene_service),
    session: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    # 1. 转换触发器
    triggers = []
    for t in data.triggers:
        if t.type == "deviceState":
            triggers.append(Trigger.create_device_event(
                entity_id=t.deviceId,
                event_type="state_changed",
                condition={"state": t.state}
            ))
        else:
            # 默认手动触发器（如果前端有特殊类型可在此扩展）
            triggers.append(Trigger.create_manual())
            
    # 2. 转换条件
    conditions = []
    for c in data.conditions:
        if c.type == "time":
            # 简单映射：目前 Condition 模型似乎不支持时间条件？
            # 查阅 condition.py 发现主要是针对实体的
            # 这里先跳过或存储为特殊格式，MVP 阶段重点是设备状态
            continue
        elif c.type == "deviceState" and c.deviceId:
            # 解析 state 字符串，如 ">= 20"
            operator = "=="
            value = str(c.state)
            if " >= " in str(c.state):
                operator = ">="
                value = str(c.state).split(" >= ")[1]
            elif " <= " in str(c.state):
                operator = "<="
                value = str(c.state).split(" <= ")[1]
                
            conditions.append(Condition(
                entity_id=c.deviceId,
                attribute=c.capability or "state",
                operator=operator,
                value=value
            ))
            
    # 3. 转换动作
    actions = []
    for a in data.actions:
        if a.type == "deviceCommand":
            command = "turn_on" if a.value is True else "turn_off" if a.value is False else "set_value"
            params = {"value": a.value} if command == "set_value" else {}
            actions.append(Action.create_device_control(
                entity_id=a.deviceId,
                command=command,
                parameters=params
            ))
            
    try:
        definition = SceneDefinition(
            triggers=triggers,
            conditions=conditions if conditions else None,
            actions=actions
        )
        
        # 4. 创建或更新
        scene_id = data.automationId if data.automationId else None
        
        # 首先检查场景是否存在
        existing_scene = None
        if scene_id:
            existing_scene = await service.get_scene(scene_id)
        
        if existing_scene:
            # 更新现有场景
            errors = await service.update_scene_definition(scene_id, definition)
            if errors:
                raise HTTPException(status_code=400, detail=errors[0])
            # 更新 UI 元数据
            await service.update_ui_metadata(scene_id, data.uiMetadata)
        else:
            # 创建新场景
            scene_id = await service.create_scene(
                name=data.name,
                description=f"Generated from editor: {data.name}",
                ui_metadata=data.uiMetadata
            )
            # 更新定义
            errors = await service.update_scene_definition(scene_id, definition)
            if errors:
                raise HTTPException(status_code=400, detail=errors[0])
            
        # 如果 isEnabled 为 True，发布场景
        if data.isEnabled:
            await service.publish_scene(scene_id)
            
        await session.commit()
        return {"id": scene_id, "status": "success"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
@router.delete("/{scene_id}")
async def delete_scene(
    scene_id: str,
    service: SceneService = Depends(get_scene_service),
    session: AsyncSession = Depends(get_db)
):
    """删除场景"""
    try:
        await service.delete_scene(scene_id)
        await session.commit()
        return {"status": "success", "message": f"Scene {scene_id} deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete scene: {str(e)}")
