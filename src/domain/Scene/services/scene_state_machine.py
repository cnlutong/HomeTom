"""场景状态机接口"""

from abc import ABC, abstractmethod
from typing import List
from ..aggregates.scene_aggregate import SceneStatus


class ISceneStateMachine(ABC):
    """场景状态机接口
    
    定义场景状态迁移逻辑（draft → published → disabled）
    """
    
    @abstractmethod
    def can_transition(self, from_status: SceneStatus, to_status: SceneStatus) -> bool:
        """检查是否可以进行状态迁移
        
        Args:
            from_status: 当前状态
            to_status: 目标状态
            
        Returns:
            是否可以迁移
        """
        pass
    
    @abstractmethod
    def get_allowed_transitions(self, current_status: SceneStatus) -> List[SceneStatus]:
        """获取允许的迁移目标状态列表
        
        Args:
            current_status: 当前状态
            
        Returns:
            允许迁移到的状态列表
        """
        pass
