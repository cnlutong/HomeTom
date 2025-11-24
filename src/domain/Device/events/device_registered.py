"""设备注册事件"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class DeviceRegistered:
    """设备注册领域事件"""
    device_id: str
    entity_id: str
    name: str
    manufacturer: Optional[str]
    adapter_type: str
    occurred_at: datetime
    
    def __post_init__(self):
        """验证事件数据"""
        if not self.device_id:
            raise ValueError("设备ID不能为空")
        if not self.entity_id:
            raise ValueError("实体ID不能为空")
        if not self.name:
            raise ValueError("设备名称不能为空")
        if not self.adapter_type:
            raise ValueError("适配器类型不能为空")

