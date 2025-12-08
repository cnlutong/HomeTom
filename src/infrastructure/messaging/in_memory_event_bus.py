"""内存事件总线实现

基于 asyncio.Queue 的事件总线实现，用于 MVP 阶段。
支持异步事件发布/订阅，优先级队列，以及优雅的生命周期管理。

设计要点：
- 遵循 IEventBus 接口契约
- 支持后台协程处理事件
- Handler 错误隔离
- 易于替换为 RabbitMQ/Kafka
"""

import asyncio
import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import IntEnum
from typing import Awaitable, Callable, Dict, List, Optional, Set, Type, Union

from .event_bus import IEventBus

# 模块日志器
logger = logging.getLogger(__name__)


class EventPriority(IntEnum):
    """事件优先级
    
    数值越高，优先级越高，越先被处理。
    """
    LOW = 0
    NORMAL = 1
    HIGH = 2


@dataclass(order=True)
class PrioritizedEvent:
    """带优先级的事件包装器
    
    用于 PriorityQueue 排序。priority 取负值是因为 PriorityQueue 是最小堆。
    """
    priority: int
    sequence: int  # 保证 FIFO 顺序（相同优先级时）
    event: object = field(compare=False)
    event_id: str = field(compare=False, default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(compare=False, default_factory=lambda: datetime.now(timezone.utc))


# Handler 类型定义：可以是同步函数或异步函数
EventHandler = Callable[[object], Union[None, Awaitable[None]]]


class InMemoryEventBus(IEventBus):
    """内存事件总线
    
    基于 asyncio.PriorityQueue 的事件总线实现，支持：
    - 异步事件发布与处理
    - 事件优先级（HIGH > NORMAL > LOW）
    - 多个 Handler 订阅同一事件
    - 通配符订阅（订阅所有事件）
    - 后台事件处理器
    - 优雅关闭
    
    使用示例：
        ```python
        event_bus = InMemoryEventBus()
        
        # 订阅事件
        event_bus.subscribe(DeviceRegistered, handle_device_registered)
        
        # 启动事件处理器
        await event_bus.start()
        
        # 发布事件
        await event_bus.publish(device_registered_event)
        
        # 关闭
        await event_bus.stop()
        ```
    
    Notes:
        - 必须调用 start() 启动后台处理器后，事件才会被处理
        - stop() 会等待队列中所有事件处理完毕
        - Handler 抛出异常不会影响其他 Handler 和后续事件处理
    """
    
    # 特殊类型：匹配所有事件
    ALL_EVENTS = type("ALL_EVENTS", (), {})
    
    def __init__(self, max_queue_size: int = 1000):
        """初始化事件总线
        
        Args:
            max_queue_size: 事件队列最大容量，防止内存溢出。默认 1000。
        """
        # 事件队列（优先级队列）
        self._queue: asyncio.PriorityQueue[PrioritizedEvent] = asyncio.PriorityQueue(
            maxsize=max_queue_size
        )
        
        # 事件处理器映射：事件类型 -> 处理器集合
        self._handlers: Dict[Type, Set[EventHandler]] = defaultdict(set)
        
        # 事件序列号（用于 FIFO 保证）
        self._sequence: int = 0
        
        # 后台处理器任务
        self._processor_task: Optional[asyncio.Task] = None
        
        # 运行状态
        self._running: bool = False
        
        # 关闭事件
        self._shutdown_event: asyncio.Event = asyncio.Event()
        
        logger.debug("InMemoryEventBus 初始化完成")
    
    # ==================== IEventBus 接口实现 ====================
    
    async def publish(self, event: object, priority: EventPriority = EventPriority.NORMAL) -> None:
        """发布事件
        
        Args:
            event: 领域事件对象
            priority: 事件优先级，默认 NORMAL
            
        Raises:
            asyncio.QueueFull: 队列已满时抛出
        """
        if event is None:
            raise ValueError("事件对象不能为 None")
        
        # 包装为带优先级的事件
        self._sequence += 1
        prioritized = PrioritizedEvent(
            priority=-priority.value,  # 取负值，使高优先级排在前面
            sequence=self._sequence,
            event=event
        )
        
        try:
            # 使用 put_nowait 避免阻塞，队列满时立即抛出异常
            self._queue.put_nowait(prioritized)
            logger.debug(
                f"事件已发布: {type(event).__name__} "
                f"(id={prioritized.event_id}, priority={priority.name})"
            )
        except asyncio.QueueFull:
            logger.error(f"事件队列已满，丢弃事件: {type(event).__name__}")
            raise
    
    async def publish_all(self, events: List[object], priority: EventPriority = EventPriority.NORMAL) -> None:
        """批量发布事件
        
        Args:
            events: 领域事件对象列表
            priority: 事件优先级，默认 NORMAL
        """
        for event in events:
            await self.publish(event, priority)
    
    def subscribe(self, event_type: Type, handler: EventHandler) -> None:
        """订阅事件
        
        Args:
            event_type: 事件类型。使用 InMemoryEventBus.ALL_EVENTS 订阅所有事件。
            handler: 事件处理函数，可以是同步或异步函数
        """
        if handler is None:
            raise ValueError("处理器不能为 None")
        
        self._handlers[event_type].add(handler)
        logger.debug(f"已订阅事件: {event_type.__name__} -> {handler.__name__}")
    
    def unsubscribe(self, event_type: Type, handler: EventHandler) -> None:
        """取消订阅
        
        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        if event_type in self._handlers:
            self._handlers[event_type].discard(handler)
            logger.debug(f"已取消订阅: {event_type.__name__} -> {handler.__name__}")
    
    # ==================== 生命周期管理 ====================
    
    async def start(self) -> None:
        """启动事件总线
        
        启动后台事件处理器。必须调用此方法后事件才会被处理。
        """
        if self._running:
            logger.warning("事件总线已在运行中")
            return
        
        self._running = True
        self._shutdown_event.clear()
        self._processor_task = asyncio.create_task(
            self._process_events(),
            name="EventBusProcessor"
        )
        logger.info("InMemoryEventBus 已启动")
    
    async def stop(self, timeout: float = 5.0) -> None:
        """停止事件总线
        
        优雅关闭：等待队列中的事件处理完毕后再停止。
        
        Args:
            timeout: 等待超时时间（秒），超时后强制停止
        """
        if not self._running:
            return
        
        logger.info("正在停止 InMemoryEventBus...")
        self._running = False
        self._shutdown_event.set()
        
        if self._processor_task:
            try:
                await asyncio.wait_for(self._processor_task, timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning(f"事件处理超时 ({timeout}s)，强制停止")
                self._processor_task.cancel()
                try:
                    await self._processor_task
                except asyncio.CancelledError:
                    pass
        
        logger.info("InMemoryEventBus 已停止")
    
    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._running
    
    @property
    def pending_count(self) -> int:
        """待处理事件数量"""
        return self._queue.qsize()
    
    # ==================== 私有方法 ====================
    
    async def _process_events(self) -> None:
        """后台事件处理循环"""
        logger.debug("事件处理器已启动")
        
        while self._running or not self._queue.empty():
            try:
                # 使用超时获取，以便定期检查 _running 状态
                prioritized = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=0.5
                )
            except asyncio.TimeoutError:
                # 超时后继续循环，检查是否应该退出
                if self._shutdown_event.is_set() and self._queue.empty():
                    break
                continue
            
            await self._dispatch_event(prioritized)
            self._queue.task_done()
        
        logger.debug("事件处理器已退出")
    
    async def _dispatch_event(self, prioritized: PrioritizedEvent) -> None:
        """分发事件到所有订阅者
        
        Args:
            prioritized: 带优先级的事件包装器
        """
        event = prioritized.event
        event_type = type(event)
        
        # 收集所有匹配的处理器
        handlers: Set[EventHandler] = set()
        
        # 精确类型匹配
        if event_type in self._handlers:
            handlers.update(self._handlers[event_type])
        
        # 通配符订阅
        if self.ALL_EVENTS in self._handlers:
            handlers.update(self._handlers[self.ALL_EVENTS])
        
        if not handlers:
            logger.debug(f"事件无订阅者: {event_type.__name__}")
            return
        
        # 调用所有处理器（错误隔离）
        for handler in handlers:
            await self._invoke_handler(handler, event, prioritized.event_id)
    
    async def _invoke_handler(
        self, 
        handler: EventHandler, 
        event: object, 
        event_id: str
    ) -> None:
        """调用单个处理器
        
        处理器执行时的异常会被捕获并记录，不会影响其他处理器。
        
        Args:
            handler: 事件处理函数
            event: 事件对象
            event_id: 事件ID（用于日志追踪）
        """
        event_type_name = type(event).__name__
        handler_name = handler.__name__
        
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
            
            logger.debug(
                f"事件处理完成: {event_type_name} -> {handler_name} (id={event_id})"
            )
        except Exception as e:
            logger.error(
                f"事件处理失败: {event_type_name} -> {handler_name} (id={event_id}): {e}",
                exc_info=True
            )
    
    # ==================== 便捷方法 ====================
    
    def subscribe_all(self, handler: EventHandler) -> None:
        """订阅所有事件
        
        用于日志记录、调试等场景。
        
        Args:
            handler: 事件处理函数
        """
        self.subscribe(self.ALL_EVENTS, handler)
    
    def clear_handlers(self) -> None:
        """清除所有订阅
        
        主要用于测试场景。
        """
        self._handlers.clear()
        logger.debug("已清除所有事件订阅")
    
    async def wait_until_empty(self, timeout: float = 10.0) -> bool:
        """等待队列清空
        
        主要用于测试场景，确保所有事件都已处理。
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            True 如果队列已清空，False 如果超时
        """
        try:
            await asyncio.wait_for(self._queue.join(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False
