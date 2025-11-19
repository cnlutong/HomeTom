from ..MediaSecurityBase import MediaSecurityBase as MediaSecurity


class MediaPlayer(MediaSecurity):
    """媒体播放器设备 - 电视、音响、流媒体盒子（控制播放、暂停、音量）"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._state = "off"  # 状态：off, on, playing, paused, idle
        self._volume_level = 0.0  # 音量 0.0-1.0
        self._is_muted = False  # 是否静音
        self._media_title = None  # 当前媒体标题
        self._media_artist = None  # 当前媒体艺术家
        self._media_content_type = None  # 媒体类型：music, video, tvshow等
    
    def turn_on(self):
        """打开设备"""
        self._state = "on"
        self.attributes['state'] = "on"
    
    def turn_off(self):
        """关闭设备"""
        self._state = "off"
        self.attributes['state'] = "off"
    
    def play(self):
        """播放"""
        self._state = "playing"
        self.attributes['state'] = "playing"
    
    def pause(self):
        """暂停"""
        self._state = "paused"
        self.attributes['state'] = "paused"
    
    def stop(self):
        """停止"""
        self._state = "idle"
        self.attributes['state'] = "idle"
    
    def set_volume_level(self, volume: float):
        """设置音量 (0.0-1.0)"""
        if 0.0 <= volume <= 1.0:
            self._volume_level = volume
            self.attributes['volume_level'] = volume
    
    def get_volume_level(self) -> float:
        """获取音量"""
        return self._volume_level
    
    def mute(self):
        """静音"""
        self._is_muted = True
        self.attributes['is_muted'] = True
    
    def unmute(self):
        """取消静音"""
        self._is_muted = False
        self.attributes['is_muted'] = False
    
    def is_muted(self) -> bool:
        """是否静音"""
        return self._is_muted
    
    def set_media_info(self, title: str = None, artist: str = None, content_type: str = None):
        """设置媒体信息"""
        if title:
            self._media_title = title
            self.attributes['media_title'] = title
        if artist:
            self._media_artist = artist
            self.attributes['media_artist'] = artist
        if content_type:
            self._media_content_type = content_type
            self.attributes['media_content_type'] = content_type
    
    def get_media_info(self) -> dict:
        """获取媒体信息"""
        return {
            'title': self._media_title,
            'artist': self._media_artist,
            'content_type': self._media_content_type
        }
    
    def update_state(self):
        """更新设备状态（需要从实际硬件获取）"""
        # 子类或适配器需要实现具体的状态获取逻辑
        pass

