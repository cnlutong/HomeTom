"""执行仓储接口"""

from abc import ABC, abstractmethod
from typing import Optional, List
from ..aggregates.execution_aggregate import ExecutionAggregate
from ..entities.execution_log import ExecutionLog


class IExecutionRepository(ABC):
    """执行仓储接口
    
    定义执行持久化的抽象接口，由基础设施层实现
    """
    
    @abstractmethod
    async def save(self, execution: ExecutionAggregate) -> None:
        """保存执行聚合根"""
        pass
    
    @abstractmethod
    async def find_by_id(self, execution_id: str) -> Optional[ExecutionAggregate]:
        """根据ID查找执行"""
        pass
    
    @abstractmethod
    async def find_by_scene_id(self, scene_id: str) -> List[ExecutionAggregate]:
        """根据场景ID查找所有执行"""
        pass
    
    @abstractmethod
    async def find_all(self) -> List[ExecutionAggregate]:
        """查找所有执行"""
        pass
    
    @abstractmethod
    async def save_log(self, log: ExecutionLog) -> None:
        """保存执行日志"""
        pass
    
    @abstractmethod
    async def find_logs_by_execution_id(self, execution_id: str) -> List[ExecutionLog]:
        """根据执行ID查找所有日志"""
        pass

