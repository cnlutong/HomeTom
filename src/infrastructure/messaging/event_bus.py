"""事件总线接口"""

from abc import ABC, abstractmethod
from typing import Callable, Type, List


class IEventBus(ABC):
    """事件总线接口
    
    定义事件发布/订阅的抽象接口，由基础设施层实现。
    MVP阶段可使用内存实现，后续可替换为Kafka/RabbitMQ等。
    """
    
    @abstractmethod
    async def publish(self, event: object) -> None:
        """发布事件
        
        Args:
            event: 领域事件对象
        """
        pass
    
    @abstractmethod
    async def publish_all(self, events: List[object]) -> None:
        """批量发布事件
        
        Args:
            events: 领域事件对象列表
        """
        pass
    
    @abstractmethod
    def subscribe(self, event_type: Type, handler: Callable) -> None:
        """订阅事件
        
        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: Type, handler: Callable) -> None:
        """取消订阅
        
        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        pass
