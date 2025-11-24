"""场景校验器接口"""

from abc import ABC, abstractmethod
from typing import List
from ..value_objects.scene_definition import SceneDefinition


class ISceneValidator(ABC):
    """场景校验器接口
    
    定义场景结构校验、循环依赖检测等逻辑
    """
    
    @abstractmethod
    async def validate_definition(self, definition: SceneDefinition) -> List[str]:
        """校验场景定义
        
        Args:
            definition: 场景定义
            
        Returns:
            错误信息列表，如果为空则表示校验通过
        """
        pass
    
    @abstractmethod
    async def check_circular_dependency(
        self,
        scene_id: str,
        definition: SceneDefinition,
        existing_scenes: List[str]
    ) -> bool:
        """检查循环依赖
        
        Args:
            scene_id: 当前场景ID
            definition: 场景定义
            existing_scenes: 已存在的场景ID列表（用于检查依赖）
            
        Returns:
            如果存在循环依赖返回True，否则返回False
        """
        pass

