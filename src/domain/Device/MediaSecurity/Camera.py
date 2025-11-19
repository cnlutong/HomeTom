from ..MediaSecurityBase import MediaSecurityBase as MediaSecurity


class Camera(MediaSecurity):
    """摄像头设备 - 视频流、静态图像"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._state = "idle"  # 状态：idle, recording, streaming
        self._is_recording = False  # 是否正在录制
        self._is_streaming = False  # 是否正在推流
        self._stream_url = None  # 视频流URL
        self._image_url = None  # 静态图像URL
        self._motion_detected = False  # 是否检测到运动
    
    def start_recording(self):
        """开始录制"""
        self._is_recording = True
        self._state = "recording"
        self.attributes['is_recording'] = True
        self.attributes['state'] = "recording"
    
    def stop_recording(self):
        """停止录制"""
        self._is_recording = False
        if self._is_streaming:
            self._state = "streaming"
        else:
            self._state = "idle"
        self.attributes['is_recording'] = False
        self.attributes['state'] = self._state
    
    def start_streaming(self, stream_url: str = None):
        """开始推流"""
        self._is_streaming = True
        if stream_url:
            self._stream_url = stream_url
            self.attributes['stream_url'] = stream_url
        self._state = "streaming"
        self.attributes['is_streaming'] = True
        self.attributes['state'] = "streaming"
    
    def stop_streaming(self):
        """停止推流"""
        self._is_streaming = False
        if self._is_recording:
            self._state = "recording"
        else:
            self._state = "idle"
        self.attributes['is_streaming'] = False
        self.attributes['state'] = self._state
    
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
    
    def set_motion_detected(self, detected: bool):
        """设置运动检测状态"""
        self._motion_detected = detected
        self.attributes['motion_detected'] = detected
    
    def is_motion_detected(self) -> bool:
        """是否检测到运动"""
        return self._motion_detected
    
    def is_recording(self) -> bool:
        """是否正在录制"""
        return self._is_recording
    
    def is_streaming(self) -> bool:
        """是否正在推流"""
        return self._is_streaming
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        # 子类或适配器需要实现具体的状态获取逻辑
        pass

