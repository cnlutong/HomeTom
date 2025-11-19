from ..Actuator import Actuator


class Vacuum(Actuator):
    """吸尘器设备 - 扫地机器人"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._battery_level = 100  # 电池电量 0-100
        self._cleaning_mode = "auto"  # 清洁模式：auto, spot, edge, single_room
        self._fan_speed = "normal"  # 吸力档位
        self._status = "docked"  # 状态：cleaning, paused, returning, docked, error
    
    def start(self):
        """开始清洁"""
        self._status = "cleaning"
        self._state = "cleaning"
        self.turn_on()
        self.attributes['status'] = "cleaning"
    
    def pause(self):
        """暂停清洁"""
        self._status = "paused"
        self._state = "paused"
        self.attributes['status'] = "paused"
    
    def stop(self):
        """停止清洁"""
        self._status = "docked"
        self._state = "docked"
        self.turn_off()
        self.attributes['status'] = "docked"
    
    def return_to_base(self):
        """返回充电座"""
        self._status = "returning"
        self._state = "returning"
        self.attributes['status'] = "returning"
    
    def get_battery_level(self) -> int:
        """获取电池电量"""
        return self._battery_level
    
    def set_cleaning_mode(self, mode: str):
        """设置清洁模式"""
        valid_modes = ["auto", "spot", "edge", "single_room"]
        if mode in valid_modes:
            self._cleaning_mode = mode
            self.attributes['cleaning_mode'] = mode
    
    def get_cleaning_mode(self) -> str:
        """获取清洁模式"""
        return self._cleaning_mode
    
    def set_fan_speed(self, speed: str):
        """设置吸力档位"""
        self._fan_speed = speed
        self.attributes['fan_speed'] = speed
    
    def get_fan_speed(self) -> str:
        """获取吸力档位"""
        return self._fan_speed
    
    def get_status(self) -> str:
        """获取当前状态"""
        return self._status
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        # 子类或适配器需要实现具体的状态获取逻辑
        pass

