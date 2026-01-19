from ..BaseDevice import BaseDevice
from ..Capabilities import MediaPlayerMixin, SwitchableMixin


class MediaPlayer(BaseDevice, SwitchableMixin, MediaPlayerMixin):
    """媒体播放器设备 - 电视、音响、流媒体盒子（控制播放、暂停、音量）"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
        self._media_title = None  # 当前媒体标题
        self._media_artist = None  # 当前媒体艺术家
        self._media_content_type = None  # 媒体类型：music, video, tvshow等
    
    def set_volume_level(self, volume: float):
        """设置音量 (0.0-1.0)"""
        if 0.0 <= volume <= 1.0:
            self.attributes['volume_level'] = volume
    
    def mute(self):
        """静音"""
        self.attributes['is_muted'] = True
    
    def unmute(self):
        """取消静音"""
        self.attributes['is_muted'] = False
    
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
        pass

