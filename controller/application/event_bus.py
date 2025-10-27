"""
事件总线（简化版）
优化建议 #2：使用简单的观察者模式
"""
import asyncio
from typing import Dict, List, Callable, Any


class EventBus:
    """
    简单的发布-订阅事件总线
    使用观察者模式实现模块间解耦
    """
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        订阅事件
        
        Args:
            event_type: 事件类型
            handler: 事件处理函数（可以是同步或异步）
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """
        取消订阅
        
        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    async def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        发布事件（非阻塞）
        
        Args:
            event_type: 事件类型
            data: 事件数据
        """
        handlers = self._handlers.get(event_type, [])
        
        for handler in handlers:
            # 使用 create_task 实现非阻塞
            if asyncio.iscoroutinefunction(handler):
                asyncio.create_task(handler(data))
            else:
                # 如果是同步函数，在线程池中执行
                asyncio.create_task(
                    asyncio.to_thread(handler, data)
                )
    
    def get_event_types(self) -> List[str]:
        """获取所有已注册的事件类型"""
        return list(self._handlers.keys())
    
    def get_handler_count(self, event_type: str) -> int:
        """获取某个事件类型的处理器数量"""
        return len(self._handlers.get(event_type, []))


# 预定义的事件类型常量
class EventTypes:
    """事件类型常量"""
    
    # 设备事件
    DEVICE_STATE_CHANGED = "device_state_changed"
    DEVICE_ADDED = "device_added"
    DEVICE_REMOVED = "device_removed"
    
    # 场景事件
    SCENE_TRIGGERED = "scene_triggered"
    SCENE_COMPLETED = "scene_completed"
    SCENE_FAILED = "scene_failed"
    SCENE_ADDED = "scene_added"
    SCENE_UPDATED = "scene_updated"
    SCENE_REMOVED = "scene_removed"
    
    # 系统事件
    SYSTEM_READY = "system_ready"
    SYSTEM_SHUTDOWN = "system_shutdown"

