from ..BaseDevice import BaseDevice
from ..Capabilities import FanMixin, SwitchableMixin


class Fan(BaseDevice, SwitchableMixin, FanMixin):
    """风扇设备 - 风扇开关、风速、摆风"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._speed_list = ["off", "low", "medium", "high"]  # 预设风速档位
    
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
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        pass

