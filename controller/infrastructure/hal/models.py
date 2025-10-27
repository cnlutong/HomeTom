"""
HAL 数据模型
定义与 HAL 层交互的数据结构
"""
from typing import Dict, Any
from pydantic import BaseModel


class HALDeviceState(BaseModel):
    """HAL 设备状态模型"""
    device_id: str
    state: str
    attributes: Dict[str, Any] = {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "light_01",
                "state": "on",
                "attributes": {"brightness": 80}
            }
        }


class HALControlCommand(BaseModel):
    """HAL 控制命令模型"""
    device_id: str
    command: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "light_01",
                "command": {"state": "on", "brightness": 100}
            }
        }

