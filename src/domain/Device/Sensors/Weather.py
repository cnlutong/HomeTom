from ..BaseDevice import BaseDevice
from ..Capabilities import WeatherMixin


class Weather(BaseDevice, WeatherMixin):
    """天气传感器 - 集成的天气预报信息"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._wind_speed = None  # 风速
        self._wind_direction = None  # 风向
        self._forecast = []  # 天气预报列表
    
    def set_wind(self, speed: float, direction: str = None):
        """设置风速和风向"""
        self._wind_speed = speed
        self._wind_direction = direction
        self.attributes['wind_speed'] = speed
        if direction:
            self.attributes['wind_direction'] = direction
    
    def set_forecast(self, forecast: list):
        """设置天气预报列表"""
        self._forecast = forecast
        self.attributes['forecast'] = forecast
    
    def get_forecast(self) -> list:
        """获取天气预报列表"""
        return self._forecast
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        pass

