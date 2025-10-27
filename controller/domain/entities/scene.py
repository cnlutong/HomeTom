"""
场景实体模型
使用 Pydantic 进行 JSON 定义验证
"""
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


# ========== 触发器定义 ==========

class DeviceStateTrigger(BaseModel):
    """设备状态触发器"""
    type: Literal["device_state"] = "device_state"
    device_id: str
    condition: Dict[str, Any]  # {"operator": "eq", "attribute": "state", "value": "open"}


class TimeTrigger(BaseModel):
    """时间触发器（cron 表达式）"""
    type: Literal["time"] = "time"
    cron: str  # 例如: "0 18 * * *"


class ManualTrigger(BaseModel):
    """手动触发器"""
    type: Literal["manual"] = "manual"


# ========== 条件定义 ==========

class DeviceStateCondition(BaseModel):
    """设备状态条件"""
    type: Literal["device_state"] = "device_state"
    device_id: str
    condition: Dict[str, Any]  # {"operator": "lt", "attribute": "brightness", "value": 50}


class TimeRangeCondition(BaseModel):
    """时间范围条件"""
    type: Literal["time_range"] = "time_range"
    start: str  # "18:00"
    end: str    # "23:00"


class ConditionGroup(BaseModel):
    """条件组（支持 AND/OR）"""
    operator: Literal["and", "or"]
    items: List[Dict[str, Any]]  # 条件列表


# ========== 动作定义 ==========

class DeviceControlAction(BaseModel):
    """设备控制动作"""
    type: Literal["device_control"] = "device_control"
    device_id: str
    command: Dict[str, Any]  # {"state": "on", "brightness": 80}


class DelayAction(BaseModel):
    """延迟动作"""
    type: Literal["delay"] = "delay"
    seconds: int


class SceneDefinition(BaseModel):
    """
    场景定义模型
    包含触发器、条件和动作
    """
    triggers: List[Dict[str, Any]] = Field(default_factory=list)
    conditions: Optional[ConditionGroup] = None
    actions: List[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "triggers": [
                    {
                        "type": "device_state",
                        "device_id": "door_sensor_01",
                        "condition": {"operator": "eq", "attribute": "state", "value": "open"}
                    }
                ],
                "conditions": {
                    "operator": "and",
                    "items": [
                        {
                            "type": "device_state",
                            "device_id": "light_sensor_01",
                            "condition": {"operator": "lt", "attribute": "brightness", "value": 50}
                        }
                    ]
                },
                "actions": [
                    {
                        "type": "device_control",
                        "device_id": "light_01",
                        "command": {"state": "on", "brightness": 80}
                    }
                ]
            }
        }


class Scene(BaseModel):
    """场景实体"""
    id: str
    name: str
    description: Optional[str] = None
    definition: SceneDefinition
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "Scene":
        """从数据库行创建场景实体"""
        import json
        definition_data = json.loads(row["definition"]) if isinstance(row["definition"], str) else row["definition"]
        
        return cls(
            id=row["id"],
            name=row["name"],
            description=row.get("description"),
            definition=SceneDefinition(**definition_data),
            is_active=bool(row["is_active"]),
            created_at=datetime.fromisoformat(row["created_at"]) if isinstance(row["created_at"], str) else row["created_at"],
        )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "scene_001",
                "name": "回家模式",
                "description": "回家时自动开灯",
                "is_active": True
            }
        }

