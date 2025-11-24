"""场景版本仓储接口"""

from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.scene_version import SceneVersion


class ISceneVersionRepository(ABC):
    """场景版本仓储接口
    
    定义场景版本持久化的抽象接口，由基础设施层实现
    """
    
    @abstractmethod
    async def save(self, version: SceneVersion) -> None:
        """保存场景版本"""
        pass
    
    @abstractmethod
    async def find_by_scene_id(self, scene_id: str) -> List[SceneVersion]:
        """根据场景ID查找所有版本"""
        pass
    
    @abstractmethod
    async def find_by_scene_and_version(
        self,
        scene_id: str,
        version_number: int
    ) -> Optional[SceneVersion]:
        """根据场景ID和版本号查找版本"""
        pass
    
    @abstractmethod
    async def find_latest_version(self, scene_id: str) -> Optional[SceneVersion]:
        """查找场景的最新版本"""
        pass

