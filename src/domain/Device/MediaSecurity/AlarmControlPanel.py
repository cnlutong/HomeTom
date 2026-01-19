from ..BaseDevice import BaseDevice
from ..Capabilities import AlarmMixin, SwitchableMixin


class AlarmControlPanel(BaseDevice, SwitchableMixin, AlarmMixin):
    """安防面板设备 - 家庭安防系统的布防/撤防"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._code_arm_required = False  # 布防是否需要密码
        self._code_format = "number"  # 密码格式：number, text
    
    def trigger(self):
        """触发告警"""
        self.attributes["alarm_state"] = "triggered"
        self._state = "triggered"
    
    def set_pending(self):
        """设置待触发状态（延迟告警）"""
        self.attributes["alarm_state"] = "pending"
        self._state = "pending"
    
    def set_code_arm_required(self, required: bool):
        """设置布防是否需要密码"""
        self._code_arm_required = required
        self.attributes['code_arm_required'] = required
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        pass

