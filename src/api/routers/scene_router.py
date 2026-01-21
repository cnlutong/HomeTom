from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import os

from src.infrastructure.persistence.database import get_current_session_factory
from src.infrastructure.persistence.repositories.scene_repository_impl import SceneRepositoryImpl
from src.infrastructure.persistence.repositories.device_repository_impl import DeviceRepositoryImpl
from src.infrastructure.persistence.repositories.execution_repository_impl import ExecutionRepositoryImpl
from src.infrastructure.persistence.repositories.executor_repository_impl import ExecutorRepositoryImpl
from src.infrastructure.messaging.event_bus import IEventBus
from src.infrastructure.adapters.hardware_adapter import HomeAssistantClient
from src.application.scene.SceneService import SceneService
from src.application.orchestration.OrchestrationService import OrchestrationService
from src.domain.Scene.services.scene_validator_impl import SceneValidator
from src.domain.Scene.value_objects.scene_definition import SceneDefinition
from src.domain.Scene.value_objects.trigger import Trigger, TriggerType
from src.domain.Scene.value_objects.condition import Condition
from src.domain.Scene.value_objects.action import Action, ActionType
from src.domain.Scene.aggregates.scene_aggregate import SceneStatus
from src.domain.Execution.services.device_manager import DeviceManager
from src.domain.Execution.services.condition_evaluator import ConditionEvaluator
from src.domain.Execution.services.workflow_engine_impl import WorkflowEngine
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/api/scenes", tags=["scenes"])

class AutomationTrigger(BaseModel):
    type: str  # "manual", "auto", "always_on", "deviceState"
    deviceId: Optional[str] = None
    capability: Optional[str] = None
    state: Optional[Any] = None
    schedule: Optional[str] = None  # For timer triggers (HH:MM format)
    days: Optional[List[int]] = None  # For weekly triggers (0=Mon, 1=Tue, ..., 6=Sun)

class AutomationCondition(BaseModel):
    type: str
    deviceId: Optional[str] = None
    capability: Optional[str] = None
    state: Optional[Any] = None
    after: Optional[str] = None
    before: Optional[str] = None
    time: Optional[str] = None
    # Structured fields for robust parsing
    operator: Optional[str] = None  # e.g., ">=", "<=", "=="
    value: Optional[Any] = None     # e.g., 20, "on", etc.

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

# 依赖项：获取事件总线
async def get_event_bus(request: Request) -> IEventBus:
    if not hasattr(request.app.state, "event_bus"):
        raise HTTPException(status_code=500, detail="EventBus not initialized")
    return request.app.state.event_bus

# 依赖项：初始化 SceneService
async def get_scene_service(
    session: AsyncSession = Depends(get_db),
    event_bus: IEventBus = Depends(get_event_bus)
):
    repo = SceneRepositoryImpl(session)
    device_repo = DeviceRepositoryImpl(session)
    validator = SceneValidator(device_repo)
    return SceneService(repo, validator, event_bus)

# 依赖项：初始化 OrchestrationService (完整依赖链)
async def get_orchestration_service(
    session: AsyncSession = Depends(get_db),
    event_bus: IEventBus = Depends(get_event_bus)
):
    """组装完整的服务依赖链
    
    HardwareClient -> DeviceManager -> ConditionEvaluator
                                    -> WorkflowEngine -> OrchestrationService
    """
    # 硬件客户端 (连接到 test_API_server)
    ha_base_url = os.environ.get("HA_BASE_URL", "http://localhost:8123")
    ha_token = os.environ.get("HA_TOKEN", "test_token")
    hardware_client = HomeAssistantClient(
        base_url=ha_base_url,
        access_token=ha_token
    )
    
    # 设备管理器
    device_manager = DeviceManager(hardware_client)
    
    # 条件评估器
    condition_evaluator = ConditionEvaluator(device_manager)
    
    # 工作流引擎
    workflow_engine = WorkflowEngine(
        condition_evaluator=condition_evaluator,
        device_manager=device_manager
    )
    
    # 仓储
    scene_repo = SceneRepositoryImpl(session)
    device_repo = DeviceRepositoryImpl(session)
    execution_repo = ExecutionRepositoryImpl(session)
    executor_repo = ExecutorRepositoryImpl(session)
    
    # 编排服务
    return OrchestrationService(
        scene_repository=scene_repo,
        device_repository=device_repo,
        execution_repository=execution_repo,
        executor_repository=executor_repo,
        workflow_engine=workflow_engine,
        event_bus=event_bus
    )

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
                # Handle different trigger types
                if t.type == TriggerType.MANUAL:
                    triggers.append({
                        "type": "manual"
                    })
                elif t.type == TriggerType.TIMER:
                    # Timer trigger (auto/scheduled)
                    triggers.append({
                        "type": "auto",
                        "schedule": t.config.get("schedule", "08:00"),
                        "days": t.config.get("days", [])
                    })
                elif t.type == TriggerType.ALWAYS_ON:
                    triggers.append({
                        "type": "always_on"
                    })
                elif t.type == TriggerType.DEVICE_EVENT:
                    # Device event trigger
                    entity_id = t.config.get("entity_id", "sensor_unknown_01")
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
            # 设备状态触发器
            triggers.append(Trigger.create_device_event(
                entity_id=t.deviceId,
                event_type="state_changed",
                condition={"state": t.state}
            ))
        elif t.type == "auto" and t.schedule:
            # 自动定时触发器
            triggers.append(Trigger.create_timer(
                schedule=t.schedule,
                days=t.days  # 可选：每周特定天
            ))
        elif t.type == "always_on":
            # 常开触发器
            triggers.append(Trigger.create_always_on())
        elif t.type == "timer" and t.schedule:
            # 兼容旧的 timer 类型
            triggers.append(Trigger.create_timer(
                schedule=t.schedule,
                days=t.days
            ))
        else:
            # 默认手动触发器 (type == "manual" 或其他)
            triggers.append(Trigger.create_manual())
            
    # 2. 转换条件
    conditions = []
    for c in data.conditions:
        if c.type == "time":
            # 时间范围条件
            conditions.append(Condition.create_time_range(
                after=c.after,
                before=c.before
            ))
        elif c.type == "deviceState" and c.deviceId:
            # 设备状态条件 - 优先使用结构化字段
            if c.operator is not None and c.value is not None:
                # 使用新的结构化字段
                operator = c.operator
                value = c.value
            else:
                # 回退到旧的字符串解析逻辑
                operator = "=="
                value = str(c.state) if c.state is not None else ""
                if " >= " in str(c.state):
                    operator = ">="
                    value = str(c.state).split(" >= ")[1]
                elif " <= " in str(c.state):
                    operator = "<="
                    value = str(c.state).split(" <= ")[1]
                elif " > " in str(c.state):
                    operator = ">"
                    value = str(c.state).split(" > ")[1]
                elif " < " in str(c.state):
                    operator = "<"
                    value = str(c.state).split(" < ")[1]
                elif " != " in str(c.state):
                    operator = "!="
                    value = str(c.state).split(" != ")[1]
                    
            conditions.append(Condition(
                entity_id=c.deviceId,
                attribute=c.capability or "state",
                operator=operator,
                value=value
            ))
            
    # 3. 转换动作 (保留 capability 信息用于精确命令映射)
    actions = []
    for a in data.actions:
        if a.type == "deviceCommand":
            # 根据 capability 和 value 类型决定具体命令
            if a.value is True:
                command = "turn_on"
                params = {}
            elif a.value is False:
                command = "turn_off"
                params = {}
            else:
                # 根据 capability 决定具体的设置命令
                capability = a.capability.lower() if a.capability else "value"
                if capability in ("brightness", "onoff"):
                    command = "set_brightness"
                    params = {"brightness": int(a.value) if isinstance(a.value, (int, float)) else 255}
                elif capability == "temperature":
                    command = "set_temperature"
                    params = {"temperature": float(a.value)}
                elif capability == "color":
                    command = "set_color_rgb"
                    params = a.value if isinstance(a.value, dict) else {"r": 255, "g": 255, "b": 255}
                elif capability == "colortemp":
                    command = "set_color_temp"
                    params = {"color_temp": int(a.value)}
                else:
                    # 通用值设置
                    command = "set_value"
                    params = {"value": a.value, "capability": capability}
            
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


@router.post("/{scene_id}/execute")
async def execute_scene(
    scene_id: str,
    orchestration: OrchestrationService = Depends(get_orchestration_service),
    session: AsyncSession = Depends(get_db)
):
    """手动触发执行场景
    
    触发已发布的场景执行，通过 OrchestrationService 协调
    WorkflowEngine 和 DeviceManager 完成设备控制。
    
    Args:
        scene_id: 要执行的场景ID
        
    Returns:
        执行结果，包括成功状态和执行ID
    """
    try:
        result = await orchestration.trigger_and_execute(scene_id)
        await session.commit()
        return {
            "status": "success" if result.get("success") else "failed",
            "scene_id": scene_id,
            **result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

