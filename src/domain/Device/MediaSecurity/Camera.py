from ..BaseDevice import BaseDevice
from ..Capabilities import CameraMixin, SwitchableMixin


class Camera(BaseDevice, SwitchableMixin, CameraMixin):
    """摄像头设备 - 视频流、静态图像"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._stream_url = None  # 视频流URL
        self._image_url = None  # 静态图像URL
    
    def set_image_url(self, image_url: str):
        """设置静态图像URL"""
        self._image_url = image_url
        self.attributes['image_url'] = image_url
    
    def get_image_url(self) -> str:
        """获取静态图像URL"""
        return self._image_url
    
    def get_stream_url(self) -> str:
        """获取视频流URL"""
        return self._stream_url
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        pass

