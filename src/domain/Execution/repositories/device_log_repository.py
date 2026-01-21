"""设备日志仓储接口"""

from abc import ABC, abstractmethod
from typing import List, Any
from src.infrastructure.persistence.models.execution_log_model import ExecutionLogModel

class IDeviceLogRepository(ABC):
    """设备日志仓储接口"""
    
    @abstractmethod
    async def find_all_paginated(self, skip: int = 0, limit: int = 50) -> List[ExecutionLogModel]:
        """分页查找所有设备日志"""
        pass

    @abstractmethod
    async def count_today_logs(self) -> int:
        """统计今日设备日志数量"""
        pass
