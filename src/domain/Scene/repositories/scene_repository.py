"""场景仓储接口"""

from abc import ABC, abstractmethod
from typing import Optional, List
from ..aggregates.scene_aggregate import SceneAggregate


class ISceneRepository(ABC):
    """场景仓储接口
    
    定义场景持久化的抽象接口，由基础设施层实现
    """
    
    @abstractmethod
    async def save(self, scene: SceneAggregate) -> None:
        """保存场景聚合根"""
        pass
    
    @abstractmethod
    async def find_by_id(self, scene_id: str) -> Optional[SceneAggregate]:
        """根据ID查找场景"""
        pass
    
    @abstractmethod
    async def find_all(self) -> List[SceneAggregate]:
        """查找所有场景"""
        pass
    
    @abstractmethod
    async def find_by_status(self, status) -> List[SceneAggregate]:
        """根据状态查找场景"""
        pass
    
    @abstractmethod
    async def delete(self, scene_id: str) -> None:
        """删除场景"""
        pass

