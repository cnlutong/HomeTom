from ..Actuator import Actuator


class Cover(Actuator):
    """遮蔽/覆盖设备 - 窗帘、车库门、百叶窗、遮阳棚"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._position = 0  # 0-100，0表示完全关闭，100表示完全打开
        self._cover_type = "generic"  # 类型：curtain, garage_door, blind, awning等
    
    def set_position(self, position: int):
        """设置位置 (0-100)"""
        if 0 <= position <= 100:
            self._position = position
            self.attributes['position'] = position
            if position == 0:
                self._state = "closed"
            elif position == 100:
                self._state = "open"
            else:
                self._state = "opening" if position > self._position else "closing"
    
    def get_position(self) -> int:
        """获取当前位置"""
        return self._position
    
    def open_cover(self):
        """打开"""
        self.set_position(100)
        self.turn_on()
    
    def close_cover(self):
        """关闭"""
        self.set_position(0)
        self.turn_off()
    
    def set_cover_type(self, cover_type: str):
        """设置覆盖类型"""
        self._cover_type = cover_type
        self.attributes['cover_type'] = cover_type
    
    def get_cover_type(self) -> str:
        """获取覆盖类型"""
        return self._cover_type
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        # 子类或适配器需要实现具体的状态获取逻辑
        pass

