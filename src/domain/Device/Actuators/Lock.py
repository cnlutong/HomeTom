from ..BaseDevice import BaseDevice
from ..Capabilities import LockMixin, SwitchableMixin


class Lock(BaseDevice, SwitchableMixin, LockMixin):
    """智能门锁设备 - 上锁/解锁"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
    
    def turn_on(self):
        """重写：上锁"""
        self.lock()
    
    def turn_off(self):
        """重写：解锁"""
        self.unlock()
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        pass

