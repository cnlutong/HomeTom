from ..Actuator import Actuator


class Lock(Actuator):
    """智能门锁设备 - 上锁/解锁"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._is_locked = True  # 是否已上锁
        self._lock_state = "locked"  # locked, unlocked, locking, unlocking
    
    def lock(self):
        """上锁"""
        self._is_locked = True
        self._lock_state = "locked"
        self._state = "locked"
        self.attributes['lock_state'] = "locked"
    
    def unlock(self):
        """解锁"""
        self._is_locked = False
        self._lock_state = "unlocked"
        self._state = "unlocked"
        self.attributes['lock_state'] = "unlocked"
    
    def is_locked(self) -> bool:
        """检查是否已上锁"""
        return self._is_locked
    
    def get_lock_state(self) -> str:
        """获取锁的状态"""
        return self._lock_state
    
    def turn_on(self):
        """重写：上锁"""
        self.lock()
    
    def turn_off(self):
        """重写：解锁"""
        self.unlock()
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        # 子类或适配器需要实现具体的状态获取逻辑
        pass

