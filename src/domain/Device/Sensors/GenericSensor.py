from ..Sensor import Sensor


class GenericSensor(Sensor):
    """通用传感器 - 返回具体数值或状态文本（如：温度 24.5、湿度 60、功率 100W）"""
    
    def __init__(self, entity_id: str, name: str, sensor_type: str = "generic"):
        super().__init__(entity_id, name)
        self._sensor_type = sensor_type  # 传感器类型：temperature, humidity, power等
        self._value = None
        self._unit = None
    
    def set_value(self, value, unit: str = None):
        """设置传感器数值和单位"""
        self._value = value
        self._unit = unit
        self.attributes['value'] = value
        if unit:
            self.attributes['unit'] = unit
        self._state = f"{value}{unit if unit else ''}"
    
    def get_value(self):
        """获取传感器数值"""
        return self._value
    
    def get_unit(self):
        """获取数值单位"""
        return self._unit
    
    def get_sensor_type(self) -> str:
        """获取传感器类型"""
        return self._sensor_type
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        # 子类或适配器需要实现具体的状态获取逻辑
        pass

