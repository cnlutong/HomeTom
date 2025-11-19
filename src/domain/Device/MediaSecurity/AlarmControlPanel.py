from ..MediaSecurityBase import MediaSecurityBase as MediaSecurity


class AlarmControlPanel(MediaSecurity):
    """安防面板设备 - 家庭安防系统的布防/撤防"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._state = "disarmed"  # 状态：disarmed, armed_home, armed_away, armed_night, pending, triggered
        self._code_arm_required = False  # 布防是否需要密码
        self._code_format = "number"  # 密码格式：number, text
    
    def arm_away(self, code: str = None):
        """外出布防"""
        if self._code_arm_required and not code:
            raise ValueError("布防需要密码")
        self._state = "armed_away"
        self.attributes['state'] = "armed_away"
    
    def arm_home(self, code: str = None):
        """在家布防"""
        if self._code_arm_required and not code:
            raise ValueError("布防需要密码")
        self._state = "armed_home"
        self.attributes['state'] = "armed_home"
    
    def arm_night(self, code: str = None):
        """夜间布防"""
        if self._code_arm_required and not code:
            raise ValueError("布防需要密码")
        self._state = "armed_night"
        self.attributes['state'] = "armed_night"
    
    def disarm(self, code: str = None):
        """撤防"""
        if self._code_arm_required and not code:
            raise ValueError("撤防需要密码")
        self._state = "disarmed"
        self.attributes['state'] = "disarmed"
    
    def trigger(self):
        """触发告警"""
        self._state = "triggered"
        self.attributes['state'] = "triggered"
    
    def set_pending(self):
        """设置待触发状态（延迟告警）"""
        self._state = "pending"
        self.attributes['state'] = "pending"
    
    def get_state(self) -> str:
        """获取当前状态"""
        return self._state
    
    def is_armed(self) -> bool:
        """检查是否已布防"""
        return self._state in ["armed_away", "armed_home", "armed_night"]
    
    def is_triggered(self) -> bool:
        """检查是否已触发告警"""
        return self._state == "triggered"
    
    def set_code_arm_required(self, required: bool):
        """设置布防是否需要密码"""
        self._code_arm_required = required
        self.attributes['code_arm_required'] = required
    
    def is_code_arm_required(self) -> bool:
        """检查布防是否需要密码"""
        return self._code_arm_required
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        # 子类或适配器需要实现具体的状态获取逻辑
        pass

