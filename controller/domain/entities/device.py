"""
设备实体模型
"""
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DeviceState(BaseModel):
    """设备状态模型"""
    state: str  # on, off, etc.
    attributes: Dict[str, Any] = Field(default_factory=dict)  # 其他属性（亮度、温度等）
    last_updated: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "state": "on",
                "attributes": {"brightness": 80, "color": "warm"},
                "last_updated": "2024-01-01T12:00:00"
            }
        }


class Device(BaseModel):
    """设备实体"""
    id: str
    name: str
    type: str  # light, sensor, switch, etc.
    config: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "Device":
        """从数据库行创建设备实体"""
        import json
        return cls(
            id=row["id"],
            name=row["name"],
            type=row["type"],
            config=json.loads(row["config"]) if row.get("config") else None,
            created_at=datetime.fromisoformat(row["created_at"]) if isinstance(row["created_at"], str) else row["created_at"],
        )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "light_01",
                "name": "客厅灯",
                "type": "light",
                "config": {"hal_endpoint": "/devices/light_01"}
            }
        }

