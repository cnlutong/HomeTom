"""
设备服务
提供设备管理的业务逻辑
"""
from typing import List, Optional, Dict, Any

from domain.entities.device import Device, DeviceState
from infrastructure.database.repositories import DeviceRepository
from infrastructure.hal.client import HALClient
from infrastructure.state_manager import StateManager
from application.event_bus import EventBus, EventTypes
from exceptions import DeviceNotFoundError, HALCommunicationError


class DeviceService:
    """设备服务"""
    
    def __init__(
        self,
        device_repo: DeviceRepository,
        hal_client: HALClient,
        state_manager: StateManager,
        event_bus: EventBus
    ):
        self.device_repo = device_repo
        self.hal_client = hal_client
        self.state_manager = state_manager
        self.event_bus = event_bus
    
    async def get_all_devices(self) -> List[Device]:
        """获取所有设备"""
        return await self.device_repo.get_all()
    
    async def get_device(self, device_id: str) -> Device:
        """
        获取设备详情
        
        Args:
            device_id: 设备 ID
            
        Returns:
            Device: 设备实体
            
        Raises:
            DeviceNotFoundError: 设备不存在
        """
        device = await self.device_repo.get_by_id(device_id)
        if not device:
            raise DeviceNotFoundError(device_id)
        return device
    
    async def get_device_state(self, device_id: str) -> DeviceState:
        """
        获取设备状态（优先从内存读取）
        
        Args:
            device_id: 设备 ID
            
        Returns:
            DeviceState: 设备状态
        """
        # 先从内存获取
        state = await self.state_manager.get_state(device_id)
        
        # 如果内存中没有，从 HAL 获取
        if not state:
            state = await self.hal_client.get_device_state(device_id)
            await self.state_manager.set_state(device_id, state)
        
        return state
    
    async def control_device(
        self,
        device_id: str,
        command: Dict[str, Any]
    ) -> bool:
        """
        控制设备
        
        Args:
            device_id: 设备 ID
            command: 控制命令
            
        Returns:
            bool: 是否成功
        """
        # 检查设备是否存在
        device = await self.device_repo.get_by_id(device_id)
        if not device:
            raise DeviceNotFoundError(device_id)
        
        # 发送控制命令到 HAL
        success = await self.hal_client.control_device(device_id, command)
        
        if success:
            # 更新内存状态
            new_state = await self.hal_client.get_device_state(device_id)
            await self.state_manager.set_state(device_id, new_state)
            
            # 发布状态变更事件
            await self.event_bus.publish(
                EventTypes.DEVICE_STATE_CHANGED,
                {
                    "device_id": device_id,
                    "state": new_state.model_dump(),
                    "command": command
                }
            )
        
        return success
    
    async def add_device(self, device: Device) -> Device:
        """
        添加设备
        
        Args:
            device: 设备实体
            
        Returns:
            Device: 添加后的设备
        """
        await self.device_repo.save(device)
        
        # 初始化设备状态
        try:
            state = await self.hal_client.get_device_state(device.id)
            await self.state_manager.set_state(device.id, state)
        except HALCommunicationError:
            # HAL 通信失败，使用默认状态
            default_state = DeviceState(state="unknown", attributes={})
            await self.state_manager.set_state(device.id, default_state)
        
        # 发布设备添加事件
        await self.event_bus.publish(
            EventTypes.DEVICE_ADDED,
            {"device_id": device.id, "device": device.model_dump()}
        )
        
        return device
    
    async def update_device(self, device: Device) -> Device:
        """更新设备配置"""
        existing = await self.device_repo.get_by_id(device.id)
        if not existing:
            raise DeviceNotFoundError(device.id)
        
        await self.device_repo.save(device)
        return device
    
    async def remove_device(self, device_id: str) -> bool:
        """
        移除设备
        
        Args:
            device_id: 设备 ID
            
        Returns:
            bool: 是否成功
        """
        device = await self.device_repo.get_by_id(device_id)
        if not device:
            raise DeviceNotFoundError(device_id)
        
        # 从数据库删除
        success = await self.device_repo.delete(device_id)
        
        if success:
            # 从状态管理器删除
            await self.state_manager.remove_state(device_id)
            
            # 发布设备移除事件
            await self.event_bus.publish(
                EventTypes.DEVICE_REMOVED,
                {"device_id": device_id}
            )
        
        return success
    
    async def sync_device_state(self, device_id: str) -> DeviceState:
        """
        同步设备状态（从 HAL 强制刷新）
        
        Args:
            device_id: 设备 ID
            
        Returns:
            DeviceState: 最新状态
        """
        state = await self.hal_client.get_device_state(device_id)
        await self.state_manager.set_state(device_id, state)
        
        # 发布状态变更事件
        await self.event_bus.publish(
            EventTypes.DEVICE_STATE_CHANGED,
            {
                "device_id": device_id,
                "state": state.model_dump(),
                "source": "sync"
            }
        )
        
        return state

