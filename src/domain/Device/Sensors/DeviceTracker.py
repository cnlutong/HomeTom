from ..BaseDevice import BaseDevice
from ..Capabilities import LocationMixin


class DeviceTracker(BaseDevice, LocationMixin):
    """设备追踪器 - 用于定位人或设备是否在家（基于 GPS 或路由器连接）"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._source_type = "gps"  # 来源类型：gps, router, bluetooth等
    
    def set_home_status(self, is_home: bool):
        """设置是否在家状态"""
        self.attributes['is_home'] = is_home
        self._state = "home" if is_home else "not_home"
    
    def set_source_type(self, source_type: str):
        """设置位置来源类型"""
        self._source_type = source_type
        self.attributes['source_type'] = source_type
    
    def get_source_type(self) -> str:
        """获取位置来源类型"""
        return self._source_type
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        pass

