from ..BaseDevice import BaseDevice
from ..Capabilities import SensorMixin


class GenericSensor(BaseDevice, SensorMixin):
    """通用传感器 - 返回具体数值或状态文本（如：温度 24.5、湿度 60、功率 100W）"""
    
    def __init__(self, entity_id: str, name: str, sensor_type: str = "generic"):
        super().__init__(entity_id, name)
        self._sensor_type = sensor_type  # 传感器类型：temperature, humidity, power等
    
    def get_sensor_type(self) -> str:
        """获取传感器类型"""
        return self._sensor_type
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        pass

