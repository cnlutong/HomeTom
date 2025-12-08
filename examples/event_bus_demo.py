"""事件总线高级演示脚本

模拟真实智能家居场景：
1. 多个IoT设备控制与状态变更
2. 场景联动（设备事件触发其他设备动作）
3. 多场景并行执行
4. 高并发压力测试

运行方式：
    cd d:/code/HomeTom
    python examples/event_bus_demo.py
"""

import asyncio
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.messaging import InMemoryEventBus, EventPriority
from src.domain.Device.events import DeviceRegistered, DeviceStatusChanged
from src.domain.Device.value_objects.device_status import DeviceStatus
from src.domain.Scene.events import ScenePublished, SceneDisabled
from src.domain.Execution.events import ExecutionStarted, ExecutionSucceeded, ExecutionFailed


# ==================== 模拟设备与场景数据 ====================

IOT_DEVICES = [
    {"id": "light-001", "entity_id": "light.living_room", "name": "客厅主灯", "type": "light"},
    {"id": "light-002", "entity_id": "light.bedroom", "name": "卧室灯", "type": "light"},
    {"id": "light-003", "entity_id": "light.kitchen", "name": "厨房灯", "type": "light"},
    {"id": "sensor-001", "entity_id": "sensor.door", "name": "门窗传感器", "type": "sensor"},
    {"id": "sensor-002", "entity_id": "sensor.motion", "name": "人体感应器", "type": "sensor"},
    {"id": "switch-001", "entity_id": "switch.air_conditioner", "name": "空调开关", "type": "switch"},
    {"id": "lock-001", "entity_id": "lock.front_door", "name": "智能门锁", "type": "lock"},
    {"id": "curtain-001", "entity_id": "cover.living_room", "name": "客厅窗帘", "type": "curtain"},
]

SCENES = [
    {"id": "scene-001", "name": "回家模式", "devices": ["light-001", "switch-001", "curtain-001"]},
    {"id": "scene-002", "name": "离家模式", "devices": ["light-001", "light-002", "light-003", "switch-001"]},
    {"id": "scene-003", "name": "睡眠模式", "devices": ["light-001", "light-002", "curtain-001"]},
    {"id": "scene-004", "name": "影院模式", "devices": ["light-001", "curtain-001"]},
]


# ==================== 统计与状态追踪 ====================

class DemoStats:
    """演示统计"""
    def __init__(self):
        self.events_published = 0
        self.events_processed = 0
        self.handlers_invoked = 0
        self.errors_caught = 0
        self.device_states: Dict[str, str] = {}
        self.scene_executions: List[str] = []
        self.linkage_triggered: List[str] = []
    
    def summary(self) -> str:
        return f"""
📊 演示统计
{'='*50}
  发布事件数: {self.events_published}
  处理事件数: {self.events_processed}
  处理器调用: {self.handlers_invoked}
  捕获错误数: {self.errors_caught}
  设备状态变更: {len(self.device_states)}
  场景执行次数: {len(self.scene_executions)}
  联动触发次数: {len(self.linkage_triggered)}
"""

stats = DemoStats()


# ==================== 事件处理器 ====================

async def device_state_tracker(event):
    """设备状态追踪器"""
    stats.handlers_invoked += 1
    if isinstance(event, DeviceStatusChanged):
        stats.device_states[event.entity_id] = event.new_status.name
        stats.events_processed += 1

async def execution_logger(event):
    """执行日志记录器"""
    stats.handlers_invoked += 1
    if isinstance(event, ExecutionStarted):
        print(f"    🎬 场景执行开始: {event.scene_id}")
        stats.events_processed += 1
    elif isinstance(event, ExecutionSucceeded):
        print(f"    ✅ 场景执行成功: {event.scene_id}")
        stats.scene_executions.append(event.scene_id)
        stats.events_processed += 1
    elif isinstance(event, ExecutionFailed):
        print(f"    ❌ 场景执行失败: {event.scene_id} - {event.error_message}")
        stats.events_processed += 1
        stats.errors_caught += 1

async def linkage_handler(event):
    """设备联动处理器 - 模拟设备间联动"""
    stats.handlers_invoked += 1
    if isinstance(event, DeviceStatusChanged):
        # 门锁开启 -> 自动开灯
        if event.entity_id == "lock.front_door" and event.new_status == DeviceStatus.ENABLED:
            stats.linkage_triggered.append("门锁开启->客厅灯")
            print(f"    🔗 联动触发: 门锁开启 → 自动开启客厅灯")
            await asyncio.sleep(0.05)  # 模拟联动延迟
        
        # 人体感应 -> 自动开灯
        if event.entity_id == "sensor.motion" and event.new_status == DeviceStatus.ENABLED:
            stats.linkage_triggered.append("人体感应->开灯")
            print(f"    🔗 联动触发: 人体感应 → 自动开启区域灯光")

async def debug_logger(event):
    """调试日志（通配符订阅）"""
    stats.handlers_invoked += 1
    event_name = type(event).__name__
    # 只记录，不打印（避免输出过多）
    stats.events_processed += 1


# ==================== 场景模拟器 ====================

class SceneSimulator:
    """场景模拟器"""
    
    def __init__(self, event_bus: InMemoryEventBus):
        self.event_bus = event_bus
    
    async def execute_scene(self, scene: dict, execution_id: str):
        """执行单个场景"""
        scene_id = scene["id"]
        
        # 发布执行开始事件
        await self.event_bus.publish(
            ExecutionStarted(
                execution_id=execution_id,
                scene_id=scene_id,
                scene_version=1,
                occurred_at=datetime.now(timezone.utc)
            ),
            EventPriority.HIGH
        )
        stats.events_published += 1
        
        # 模拟控制每个设备
        for device_id in scene["devices"]:
            device = next((d for d in IOT_DEVICES if d["id"] == device_id), None)
            if device:
                await self._control_device(device)
                await asyncio.sleep(random.uniform(0.02, 0.08))  # 模拟设备响应时间
        
        # 发布执行成功事件
        await self.event_bus.publish(
            ExecutionSucceeded(
                execution_id=execution_id,
                scene_id=scene_id,
                occurred_at=datetime.now(timezone.utc)
            )
        )
        stats.events_published += 1
    
    async def _control_device(self, device: dict):
        """控制单个设备"""
        # 发布设备状态变更事件
        await self.event_bus.publish(
            DeviceStatusChanged(
                device_id=device["id"],
                entity_id=device["entity_id"],
                old_status=DeviceStatus.DISABLED,
                new_status=DeviceStatus.ENABLED,
                occurred_at=datetime.now(timezone.utc)
            )
        )
        stats.events_published += 1


# ==================== 测试场景 ====================

async def test_device_registration(event_bus: InMemoryEventBus):
    """场景1: 批量设备注册"""
    print("\n" + "="*60)
    print("📌 场景1: 批量设备注册 (8个IoT设备)")
    print("="*60)
    
    for device in IOT_DEVICES:
        event = DeviceRegistered(
            device_id=device["id"],
            entity_id=device["entity_id"],
            name=device["name"],
            manufacturer="HomeTom",
            adapter_type="http",
            occurred_at=datetime.now(timezone.utc)
        )
        await event_bus.publish(event)
        stats.events_published += 1
    
    await event_bus.wait_until_empty(timeout=5.0)
    print(f"  ✅ 已注册 {len(IOT_DEVICES)} 个设备")


async def test_sequential_scene_execution(event_bus: InMemoryEventBus):
    """场景2: 顺序执行多个场景"""
    print("\n" + "="*60)
    print("📌 场景2: 顺序执行场景 (回家模式 → 影院模式)")
    print("="*60)
    
    simulator = SceneSimulator(event_bus)
    
    # 顺序执行两个场景
    scenes_to_run = [SCENES[0], SCENES[3]]  # 回家模式, 影院模式
    
    for i, scene in enumerate(scenes_to_run):
        print(f"\n  ▶️ 执行场景 {i+1}: {scene['name']}")
        await simulator.execute_scene(scene, f"exec-seq-{i+1}")
        await event_bus.wait_until_empty(timeout=3.0)
    
    print(f"\n  ✅ 顺序执行完成")


async def test_parallel_scene_execution(event_bus: InMemoryEventBus):
    """场景3: 并行执行多个场景"""
    print("\n" + "="*60)
    print("📌 场景3: 并行执行场景 (4个场景同时执行)")
    print("="*60)
    
    simulator = SceneSimulator(event_bus)
    
    # 并行执行所有场景
    tasks = []
    for i, scene in enumerate(SCENES):
        print(f"  ⏳ 启动场景: {scene['name']}")
        task = asyncio.create_task(
            simulator.execute_scene(scene, f"exec-parallel-{i+1}")
        )
        tasks.append(task)
    
    # 等待所有场景完成
    await asyncio.gather(*tasks)
    await event_bus.wait_until_empty(timeout=5.0)
    
    print(f"\n  ✅ 并行执行完成 ({len(SCENES)} 个场景)")


async def test_device_linkage(event_bus: InMemoryEventBus):
    """场景4: 设备联动测试"""
    print("\n" + "="*60)
    print("📌 场景4: 设备联动 (门锁/传感器 → 自动控制)")
    print("="*60)
    
    # 模拟门锁开启
    print("\n  🔓 模拟: 门锁开启")
    await event_bus.publish(
        DeviceStatusChanged(
            device_id="lock-001",
            entity_id="lock.front_door",
            old_status=DeviceStatus.DISABLED,
            new_status=DeviceStatus.ENABLED,
            occurred_at=datetime.now(timezone.utc)
        ),
        EventPriority.HIGH  # 安全相关，高优先级
    )
    stats.events_published += 1
    
    await asyncio.sleep(0.2)
    
    # 模拟人体感应触发
    print("\n  👤 模拟: 人体感应触发")
    await event_bus.publish(
        DeviceStatusChanged(
            device_id="sensor-002",
            entity_id="sensor.motion",
            old_status=DeviceStatus.DISABLED,
            new_status=DeviceStatus.ENABLED,
            occurred_at=datetime.now(timezone.utc)
        )
    )
    stats.events_published += 1
    
    await event_bus.wait_until_empty(timeout=3.0)
    print(f"\n  ✅ 联动测试完成 (触发 {len(stats.linkage_triggered)} 次联动)")


async def test_high_concurrency(event_bus: InMemoryEventBus):
    """场景5: 高并发压力测试"""
    print("\n" + "="*60)
    print("📌 场景5: 高并发测试 (100个事件并发发布)")
    print("="*60)
    
    start_time = asyncio.get_event_loop().time()
    
    # 并发发布100个事件
    tasks = []
    for i in range(100):
        device = random.choice(IOT_DEVICES)
        event = DeviceStatusChanged(
            device_id=device["id"],
            entity_id=device["entity_id"],
            old_status=DeviceStatus.DISABLED,
            new_status=DeviceStatus.ENABLED,
            occurred_at=datetime.now(timezone.utc)
        )
        task = asyncio.create_task(event_bus.publish(event))
        tasks.append(task)
        stats.events_published += 1
    
    await asyncio.gather(*tasks)
    print(f"  ⚡ 100个事件发布完成")
    
    # 等待处理完成
    await event_bus.wait_until_empty(timeout=10.0)
    
    elapsed = asyncio.get_event_loop().time() - start_time
    print(f"  ⏱️ 处理耗时: {elapsed:.3f}s")
    print(f"  📈 吞吐量: {100/elapsed:.1f} 事件/秒")


async def test_priority_ordering(event_bus: InMemoryEventBus):
    """场景6: 优先级排序验证"""
    print("\n" + "="*60)
    print("📌 场景6: 优先级排序验证")
    print("="*60)
    
    order_tracker = []
    
    async def track_order(event):
        if isinstance(event, DeviceStatusChanged):
            order_tracker.append(event.device_id)
    
    event_bus.subscribe(DeviceStatusChanged, track_order)
    
    # 同时发布不同优先级的事件
    await event_bus.publish(
        DeviceStatusChanged(
            device_id="LOW-priority",
            entity_id="test.low",
            old_status=DeviceStatus.DISABLED,
            new_status=DeviceStatus.ENABLED,
            occurred_at=datetime.now(timezone.utc)
        ),
        EventPriority.LOW
    )
    await event_bus.publish(
        DeviceStatusChanged(
            device_id="HIGH-priority",
            entity_id="test.high",
            old_status=DeviceStatus.DISABLED,
            new_status=DeviceStatus.ENABLED,
            occurred_at=datetime.now(timezone.utc)
        ),
        EventPriority.HIGH
    )
    await event_bus.publish(
        DeviceStatusChanged(
            device_id="NORMAL-priority",
            entity_id="test.normal",
            old_status=DeviceStatus.DISABLED,
            new_status=DeviceStatus.ENABLED,
            occurred_at=datetime.now(timezone.utc)
        ),
        EventPriority.NORMAL
    )
    stats.events_published += 3
    
    await event_bus.wait_until_empty(timeout=3.0)
    
    # 验证顺序
    expected = ["HIGH-priority", "NORMAL-priority", "LOW-priority"]
    # 只取最后3个（之前可能有其他事件）
    actual = [x for x in order_tracker if x in expected]
    
    print(f"  预期顺序: {' → '.join(expected)}")
    print(f"  实际顺序: {' → '.join(actual)}")
    
    if actual == expected:
        print("  ✅ 优先级排序正确!")
    else:
        print("  ⚠️ 顺序可能因并发略有差异")
    
    event_bus.unsubscribe(DeviceStatusChanged, track_order)


# ==================== 主程序 ====================

async def main():
    print("\n" + "🏠"*30)
    print("       HomeTom 智能家居事件总线高级演示")
    print("🏠"*30)
    
    # 创建并配置事件总线
    event_bus = InMemoryEventBus(max_queue_size=500)
    
    # 注册处理器
    event_bus.subscribe(DeviceStatusChanged, device_state_tracker)
    event_bus.subscribe(DeviceStatusChanged, linkage_handler)
    event_bus.subscribe(ExecutionStarted, execution_logger)
    event_bus.subscribe(ExecutionSucceeded, execution_logger)
    event_bus.subscribe(ExecutionFailed, execution_logger)
    event_bus.subscribe_all(debug_logger)
    
    print("\n✅ 事件处理器已注册")
    
    # 启动事件总线
    await event_bus.start()
    print("✅ 事件总线已启动\n")
    
    try:
        # 执行所有测试场景
        await test_device_registration(event_bus)
        await test_sequential_scene_execution(event_bus)
        await test_parallel_scene_execution(event_bus)
        await test_device_linkage(event_bus)
        await test_high_concurrency(event_bus)
        await test_priority_ordering(event_bus)
        
    finally:
        # 优雅关闭
        print("\n" + "="*60)
        print("📌 关闭事件总线")
        print("="*60)
        await event_bus.stop()
        print("  ✅ 事件总线已安全关闭")
    
    # 打印统计
    print(stats.summary())
    
    print("\n" + "🎉"*20)
    print("       演示完成!")
    print("🎉"*20 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
