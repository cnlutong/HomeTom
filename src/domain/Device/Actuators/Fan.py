from ..Actuator import Actuator


class Fan(Actuator):
    """风扇设备 - 风扇开关、风速、摆风"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._speed = 0  # 风速等级 0-100
        self._speed_list = ["off", "low", "medium", "high"]  # 预设风速档位
        self._oscillating = False  # 是否摆风
    
    def set_speed(self, speed: int):
        """设置风速 (0-100)"""
        if 0 <= speed <= 100:
            self._speed = speed
            self.attributes['speed'] = speed
            if speed > 0:
                self.turn_on()
            else:
                self.turn_off()
    
    def get_speed(self) -> int:
        """获取风速"""
        return self._speed
    
    def set_speed_level(self, level: str):
        """设置预设风速档位"""
        if level in self._speed_list:
            speed_map = {
                "off": 0,
                "low": 25,
                "medium": 50,
                "high": 100
            }
            self.set_speed(speed_map.get(level, 0))
            self.attributes['speed_level'] = level
    
    def set_oscillating(self, oscillating: bool):
        """设置摆风状态"""
        self._oscillating = oscillating
        self.attributes['oscillating'] = oscillating
    
    def is_oscillating(self) -> bool:
        """是否正在摆风"""
        return self._oscillating
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        # 子类或适配器需要实现具体的状态获取逻辑
        pass

