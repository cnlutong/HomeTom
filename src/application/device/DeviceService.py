"""设备应用服务"""

import uuid
from typing import List, Optional, Dict, Any

from ...domain.Device.aggregates.device_aggregate import DeviceAggregate
from ...domain.Device.repositories.device_repository import IDeviceRepository
from ...domain.Device.services.device_service import IDeviceService
from ...domain.Device.value_objects.device_status import DeviceStatus
from ...domain.Device.value_objects.device_capability import DeviceCapabilities
from ...infrastructure.messaging.event_bus import IEventBus


class DeviceService:
    """设备应用服务
    
    协调设备相关的业务流程，作为接口层和领域层之间的中介。
    负责：
    - 设备注册、启停
    - 设备状态同步
    - 发布领域事件
    """
    
    def __init__(
        self,
        device_repository: IDeviceRepository,
        device_service: IDeviceService,
        event_bus: IEventBus
    ):
        """初始化设备应用服务
        
        Args:
            device_repository: 设备仓储接口
            device_service: 设备领域服务接口
            event_bus: 事件总线接口
        """
        self._device_repository = device_repository
        self._device_service = device_service
        self._event_bus = event_bus
    
    async def register_device(
        self,
        entity_id: str,
        name: str,
        adapter_type: str,
        manufacturer: Optional[str] = None,
        capabilities: Optional[DeviceCapabilities] = None
    ) -> str:
        """注册新设备
        
        Args:
            entity_id: 设备实体ID（如 homeassistant 的 entity_id）
            name: 设备名称
            adapter_type: 适配器类型
            manufacturer: 制造商（可选）
            capabilities: 设备能力（可选）
            
        Returns:
            新设备的ID
        """
        # 生成设备ID
        device_id = str(uuid.uuid4())
        
        # 使用工厂方法创建设备聚合根
        device = DeviceAggregate.create(
            device_id=device_id,
            entity_id=entity_id,
            name=name,
            adapter_type=adapter_type,
            manufacturer=manufacturer,
            capabilities=capabilities
        )
        
        # 持久化设备
        await self._device_repository.save(device)
        
        # 发布领域事件
        events = device.get_domain_events()
        await self._event_bus.publish_all(events)
        device.clear_domain_events()
        
        return device_id
    
    async def enable_device(self, device_id: str) -> None:
        """启用设备
        
        Args:
            device_id: 设备ID
            
        Raises:
            ValueError: 设备不存在
        """
        device = await self._device_repository.find_by_id(device_id)
        if not device:
            raise ValueError(f"设备不存在: {device_id}")
        
        device.enable()
        
        await self._device_repository.save(device)
        
        # 发布领域事件
        events = device.get_domain_events()
        await self._event_bus.publish_all(events)
        device.clear_domain_events()
    
    async def disable_device(self, device_id: str) -> None:
        """禁用设备
        
        Args:
            device_id: 设备ID
            
        Raises:
            ValueError: 设备不存在
        """
        device = await self._device_repository.find_by_id(device_id)
        if not device:
            raise ValueError(f"设备不存在: {device_id}")
        
        device.disable()
        
        await self._device_repository.save(device)
        
        # 发布领域事件
        events = device.get_domain_events()
        await self._event_bus.publish_all(events)
        device.clear_domain_events()
    
    async def sync_device_state(
        self,
        device_id: str,
        state_data: Dict[str, Any]
    ) -> None:
        """同步设备状态
        
        Args:
            device_id: 设备ID
            state_data: 从外部获取的状态数据
            
        Raises:
            ValueError: 设备不存在
        """
        device = await self._device_repository.find_by_id(device_id)
        if not device:
            raise ValueError(f"设备不存在: {device_id}")
        
        # 委托给领域服务处理状态同步逻辑
        await self._device_service.sync_device_state(device, state_data)
        
        await self._device_repository.save(device)
    
    async def get_device(self, device_id: str) -> Optional[DeviceAggregate]:
        """获取设备详情
        
        Args:
            device_id: 设备ID
            
        Returns:
            设备聚合根，如果不存在则返回None
        """
        return await self._device_repository.find_by_id(device_id)
    
    async def get_device_by_entity_id(self, entity_id: str) -> Optional[DeviceAggregate]:
        """根据实体ID获取设备
        
        Args:
            entity_id: 设备实体ID
            
        Returns:
            设备聚合根，如果不存在则返回None
        """
        return await self._device_repository.find_by_entity_id(entity_id)
    
    async def list_devices(
        self,
        status: Optional[DeviceStatus] = None
    ) -> List[DeviceAggregate]:
        """查询设备列表
        
        Args:
            status: 可选的状态过滤器
            
        Returns:
            设备列表
        """
        if status:
            return await self._device_repository.find_by_status(status)
        return await self._device_repository.find_all()
    
    async def delete_device(self, device_id: str) -> None:
        """删除设备
        
        Args:
            device_id: 设备ID
            
        Raises:
            ValueError: 设备不存在
        """
        device = await self._device_repository.find_by_id(device_id)
        if not device:
            raise ValueError(f"设备不存在: {device_id}")
        
        await self._device_repository.delete(device_id)

    async def sync_devices_from_hardware(
        self,
        adapter_type: str,
        hardware_registry: Any
    ) -> List[str]:
        """从硬件适配器同步全部设备
        
        获取外部系统的所有实体，并将其注册到本地数据库（如果尚未存在）。
        
        Args:
            adapter_type: 适配器类型（如 "homeassistant"）
            hardware_registry: 硬件客户端注册表实例
            
        Returns:
            新注册的设备ID列表
        """
        try:
            client = hardware_registry.get_client_or_raise(adapter_type)
            response = await client.get_all_states()
            
            if not response.success:
                print(f"[{adapter_type}] 获取状态失败: {response.message}")
                return []
            
            new_device_ids = []
            skipped_count = 0
            states = response.data.get("states", [])
            
            for state in states:
                # 检查是否已存在
                existing = await self._device_repository.find_by_entity_id(state.entity_id)
                if not existing:
                    # 获取友好名称，如果没有则使用 entity_id
                    friendly_name = state.attributes.get("friendly_name") or state.entity_id
                    
                    # 注册新设备
                    device_id = await self.register_device(
                        entity_id=state.entity_id,
                        name=friendly_name,
                        adapter_type=adapter_type
                    )
                    new_device_ids.append(device_id)
                else:
                    skipped_count += 1
            
            print(f"[{adapter_type}] 设备同步完成: 新增 {len(new_device_ids)} 个，跳过 {skipped_count} 个已存在设备。")
            return new_device_ids
        except Exception as e:
            print(f"[{adapter_type}] 同步设备失败: {e}")
            return []
