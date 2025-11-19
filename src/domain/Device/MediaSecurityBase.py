from abc import ABC, abstractmethod
from .BaseDevice import BaseDevice


class MediaSecurityBase(BaseDevice):
    """多媒体与监控类设备基类 - 媒体播放器和安防设备"""
    
    def __init__(self, entity_id: str, name: str):
        super().__init__(entity_id, name)
    
    @abstractmethod
    def update_state(self):
        """抽象方法：子类需要实现状态更新逻辑"""
        pass

# 为了向后兼容，保留别名
MediaSecurity = MediaSecurityBase

