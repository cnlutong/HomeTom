from ..BaseDevice import BaseDevice
from ..Capabilities import BinaryStateMixin


class BinarySensor(BaseDevice, BinaryStateMixin):
    """二元传感器 - 只有两种状态：开/关、有/无（如：人体传感器、门窗传感器、漏水传感器）"""
    
    def __init__(self, entity_id: str, name: str, sensor_type: str = "generic"):
        super().__init__(entity_id, name)
        self._sensor_type = sensor_type  # 类型：motion, door, window, leak等
    
    def get_sensor_type(self) -> str:
        """获取传感器类型"""
        return self._sensor_type
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        pass

