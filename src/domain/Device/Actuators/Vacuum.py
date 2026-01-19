from ..BaseDevice import BaseDevice
from ..Capabilities import VacuumMixin, SwitchableMixin


class Vacuum(BaseDevice, SwitchableMixin, VacuumMixin):
    """吸尘器设备 - 扫地机器人"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._cleaning_mode = "auto"  # 清洁模式：auto, spot, edge, single_room
        self._fan_speed = "normal"  # 吸力档位
    
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
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        pass

