from ..Sensor import Sensor


class DeviceTracker(Sensor):
    """设备追踪器 - 用于定位人或设备是否在家（基于 GPS 或路由器连接）"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._is_home = False  # 是否在家
        self._latitude = None  # 纬度
        self._longitude = None  # 经度
        self._source_type = "gps"  # 来源类型：gps, router, bluetooth等
    
    def set_location(self, latitude: float, longitude: float, is_home: bool = None):
        """设置位置信息"""
        self._latitude = latitude
        self._longitude = longitude
        self.attributes['latitude'] = latitude
        self.attributes['longitude'] = longitude
        
        if is_home is not None:
            self.set_home_status(is_home)
        else:
            # 可以根据经纬度判断是否在家（需要配置家的位置）
            self._is_home = False
    
    def set_home_status(self, is_home: bool):
        """设置是否在家状态"""
        self._is_home = is_home
        self._state = "home" if is_home else "not_home"
        self.attributes['is_home'] = is_home
    
    def is_home(self) -> bool:
        """检查是否在家"""
        return self._is_home
    
    def get_location(self) -> tuple:
        """获取位置坐标 (latitude, longitude)"""
        return (self._latitude, self._longitude)
    
    def set_source_type(self, source_type: str):
        """设置位置来源类型"""
        self._source_type = source_type
        self.attributes['source_type'] = source_type
    
    def get_source_type(self) -> str:
        """获取位置来源类型"""
        return self._source_type
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        # 子类或适配器需要实现具体的状态获取逻辑
        pass

