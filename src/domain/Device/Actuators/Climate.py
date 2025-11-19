from ..Actuator import Actuator


class Climate(Actuator):
    """气候/温控设备 - 空调、恒温器、地暖"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._temperature = 20.0  # 目标温度
        self._current_temperature = 20.0  # 当前温度
        self._mode = "auto"  # 模式：auto, cool, heat, fan_only, dry, off
        self._fan_mode = "auto"  # 风扇模式
        self._swing_mode = "off"  # 摆风模式
    
    def set_temperature(self, temperature: float):
        """设置目标温度"""
        self._temperature = temperature
        self.attributes['temperature'] = temperature
    
    def get_temperature(self) -> float:
        """获取目标温度"""
        return self._temperature
    
    def get_current_temperature(self) -> float:
        """获取当前温度"""
        return self._current_temperature
    
    def set_mode(self, mode: str):
        """设置运行模式"""
        valid_modes = ["auto", "cool", "heat", "fan_only", "dry", "off"]
        if mode in valid_modes:
            self._mode = mode
            self.attributes['mode'] = mode
            if mode == "off":
                self.turn_off()
            else:
                self.turn_on()
    
    def get_mode(self) -> str:
        """获取运行模式"""
        return self._mode
    
    def set_fan_mode(self, fan_mode: str):
        """设置风扇模式"""
        self._fan_mode = fan_mode
        self.attributes['fan_mode'] = fan_mode
    
    def get_fan_mode(self) -> str:
        """获取风扇模式"""
        return self._fan_mode
    
    def set_swing_mode(self, swing_mode: str):
        """设置摆风模式"""
        self._swing_mode = swing_mode
        self.attributes['swing_mode'] = swing_mode
    
    def get_swing_mode(self) -> str:
        """获取摆风模式"""
        return self._swing_mode
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        # 子类或适配器需要实现具体的状态获取逻辑
        pass

