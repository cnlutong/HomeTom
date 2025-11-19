from ..Sensor import Sensor


class Weather(Sensor):
    """天气传感器 - 集成的天气预报信息"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._temperature = None  # 温度
        self._humidity = None  # 湿度
        self._pressure = None  # 气压
        self._wind_speed = None  # 风速
        self._wind_direction = None  # 风向
        self._condition = None  # 天气状况：sunny, cloudy, rainy等
        self._forecast = []  # 天气预报列表
    
    def set_current_weather(self, temperature: float, humidity: float = None, 
                           pressure: float = None, condition: str = None):
        """设置当前天气信息"""
        self._temperature = temperature
        self._humidity = humidity
        self._pressure = pressure
        self._condition = condition
        
        self.attributes['temperature'] = temperature
        if humidity is not None:
            self.attributes['humidity'] = humidity
        if pressure is not None:
            self.attributes['pressure'] = pressure
        if condition:
            self.attributes['condition'] = condition
            self._state = condition
    
    def set_wind(self, speed: float, direction: str = None):
        """设置风速和风向"""
        self._wind_speed = speed
        self._wind_direction = direction
        self.attributes['wind_speed'] = speed
        if direction:
            self.attributes['wind_direction'] = direction
    
    def get_temperature(self) -> float:
        """获取温度"""
        return self._temperature
    
    def get_humidity(self) -> float:
        """获取湿度"""
        return self._humidity
    
    def get_pressure(self) -> float:
        """获取气压"""
        return self._pressure
    
    def get_condition(self) -> str:
        """获取天气状况"""
        return self._condition
    
    def set_forecast(self, forecast: list):
        """设置天气预报列表"""
        self._forecast = forecast
        self.attributes['forecast'] = forecast
    
    def get_forecast(self) -> list:
        """获取天气预报列表"""
        return self._forecast
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        # 子类或适配器需要实现具体的状态获取逻辑
        pass

