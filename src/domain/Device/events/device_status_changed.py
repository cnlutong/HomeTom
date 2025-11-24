"""设备状态变更事件"""

from dataclasses import dataclass
from datetime import datetime
from ..value_objects.device_status import DeviceStatus


@dataclass(frozen=True)
class DeviceStatusChanged:
    """设备状态变更领域事件"""
    device_id: str
    entity_id: str
    old_status: DeviceStatus
    new_status: DeviceStatus
    occurred_at: datetime
    
    def __post_init__(self):
        """验证事件数据"""
        if not self.device_id:
            raise ValueError("设备ID不能为空")
        if not self.entity_id:
            raise ValueError("实体ID不能为空")
        if self.old_status == self.new_status:
            raise ValueError("新旧状态不能相同")

