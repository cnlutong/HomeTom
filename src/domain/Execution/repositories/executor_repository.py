"""执行器仓储接口"""

from abc import ABC, abstractmethod
from typing import Optional, List
from ..aggregates.scene_executor import SceneExecutor


class IExecutorRepository(ABC):
    """执行器仓储接口
    
    定义执行器持久化的抽象接口，由基础设施层实现
    """
    
    @abstractmethod
    async def save(self, executor: SceneExecutor) -> None:
        """保存执行器"""
        pass
    
    @abstractmethod
    async def find_by_id(self, executor_id: str) -> Optional[SceneExecutor]:
        """根据ID查找执行器"""
        pass
    
    @abstractmethod
    async def find_by_scene_id(self, scene_id: str) -> Optional[SceneExecutor]:
        """根据场景ID查找执行器（一个场景对应一个执行器）"""
        pass
    
    @abstractmethod
    async def find_all_active(self) -> List[SceneExecutor]:
        """查找所有激活状态的执行器"""
        pass
    
    @abstractmethod
    async def find_all(self) -> List[SceneExecutor]:
        """查找所有执行器"""
        pass
    
    @abstractmethod
    async def delete(self, executor_id: str) -> None:
        """删除执行器"""
        pass

    @abstractmethod
    async def delete_by_scene_id(self, scene_id: str) -> None:
        """根据场景 ID 删除执行器"""
        pass
