from ..Sensor import Sensor


class BinarySensor(Sensor):
    """二元传感器 - 只有两种状态：开/关、有/无（如：人体传感器、门窗传感器、漏水传感器）"""
    
    def __init__(self, entity_id: str, name: str, sensor_type: str = "generic"):
        super().__init__(entity_id, name)
        self._sensor_type = sensor_type  # 类型：motion, door, window, leak等
        self._is_on = False  # True表示检测到，False表示未检测到
    
    def set_state(self, is_on: bool):
        """设置传感器状态"""
        self._is_on = is_on
        self._state = "on" if is_on else "off"
        self.attributes['is_on'] = is_on
    
    def is_on(self) -> bool:
        """检查是否检测到（开/有）"""
        return self._is_on
    
    def is_off(self) -> bool:
        """检查是否未检测到（关/无）"""
        return not self._is_on
    
    def get_sensor_type(self) -> str:
        """获取传感器类型"""
        return self._sensor_type
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        # 子类或适配器需要实现具体的状态获取逻辑
        pass

