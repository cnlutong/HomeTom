"""场景状态机接口"""

from abc import ABC, abstractmethod
from ..aggregates.scene_aggregate import SceneStatus


class ISceneStateMachine(ABC):
    """场景状态机接口
    
    定义场景状态迁移规则
    """
    
    @abstractmethod
    def can_transition(self, from_status: SceneStatus, to_status: SceneStatus) -> bool:
        """检查状态迁移是否允许
        
        Args:
            from_status: 当前状态
            to_status: 目标状态
            
        Returns:
            如果允许迁移返回True，否则返回False
        """
        pass
    
    @abstractmethod
    def get_allowed_transitions(self, current_status: SceneStatus) -> List[SceneStatus]:
        """获取允许的状态迁移列表
        
        Args:
            current_status: 当前状态
            
        Returns:
            允许迁移到的状态列表
        """
        pass

