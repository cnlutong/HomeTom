"""并发协调器接口"""

from abc import ABC, abstractmethod
from typing import List


class IConcurrencyCoordinator(ABC):
    """并发协调器接口
    
    定义并发控制策略，MVP阶段仅支持串行执行
    """
    
    @abstractmethod
    async def can_execute(self, scene_id: str) -> bool:
        """检查是否可以执行场景
        
        Args:
            scene_id: 场景ID
            
        Returns:
            如果可以执行返回True，否则返回False
        """
        pass
    
    @abstractmethod
    async def acquire_lock(self, scene_id: str) -> bool:
        """获取执行锁
        
        Args:
            scene_id: 场景ID
            
        Returns:
            如果成功获取锁返回True，否则返回False
        """
        pass
    
    @abstractmethod
    async def release_lock(self, scene_id: str) -> None:
        """释放执行锁
        
        Args:
            scene_id: 场景ID
        """
        pass
    
    @abstractmethod
    async def get_running_executions(self) -> List[str]:
        """获取正在执行的场景ID列表
        
        Returns:
            正在执行的场景ID列表
        """
        pass

