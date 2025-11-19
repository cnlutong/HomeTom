from ..Actuator import Actuator


class Light(Actuator):
    """灯光设备 - 控制开关、亮度、颜色 (RGB/色温)"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._brightness = 0  # 0-255
        self._color_rgb = (255, 255, 255)  # RGB颜色
        self._color_temp = None  # 色温值
    
    def set_brightness(self, brightness: int):
        """设置亮度 (0-255)"""
        if 0 <= brightness <= 255:
            self._brightness = brightness
            self.attributes['brightness'] = brightness
    
    def get_brightness(self) -> int:
        """获取当前亮度"""
        return self._brightness
    
    def set_color_rgb(self, r: int, g: int, b: int):
        """设置RGB颜色"""
        if all(0 <= c <= 255 for c in [r, g, b]):
            self._color_rgb = (r, g, b)
            self.attributes['rgb_color'] = [r, g, b]
    
    def get_color_rgb(self) -> tuple:
        """获取RGB颜色"""
        return self._color_rgb
    
    def set_color_temp(self, color_temp: int):
        """设置色温"""
        self._color_temp = color_temp
        self.attributes['color_temp'] = color_temp
    
    def get_color_temp(self):
        """获取色温"""
        return self._color_temp
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        # 子类或适配器需要实现具体的状态获取逻辑
        pass

