"""工作流引擎接口"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ...Scene.value_objects.scene_definition import SceneDefinition
from ..aggregates.execution_aggregate import ExecutionAggregate


class IWorkflowEngine(ABC):
    """工作流引擎接口
    
    定义工作流执行逻辑，MVP阶段仅支持顺序执行
    """
    
    @abstractmethod
    async def execute(
        self,
        execution: ExecutionAggregate,
        definition: SceneDefinition
    ) -> None:
        """执行工作流
        
        Args:
            execution: 执行聚合根
            definition: 场景定义
        """
        pass
    
    @abstractmethod
    async def execute_action(
        self,
        execution: ExecutionAggregate,
        action,
        step_number: int
    ) -> Dict[str, Any]:
        """执行单个动作
        
        Args:
            execution: 执行聚合根
            action: 动作对象
            step_number: 步骤序号
            
        Returns:
            执行结果
        """
        pass

