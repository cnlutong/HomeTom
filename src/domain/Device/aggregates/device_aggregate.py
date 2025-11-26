"""设备聚合根"""

from datetime import datetime
from typing import Optional, List
from ..value_objects.device_status import DeviceStatus
from ..value_objects.device_capability import DeviceCapabilities, DeviceCapability
from ..events.device_registered import DeviceRegistered
from ..events.device_status_changed import DeviceStatusChanged


class DeviceAggregate:
    """设备聚合根
    
    封装设备的核心业务逻辑，维护设备的一致性边界
    """
    
    def __init__(
        self,
        device_id: str,
        entity_id: str,
        name: str,
        adapter_type: str,
        manufacturer: Optional[str] = None,
        capabilities: Optional[DeviceCapabilities] = None,
        status: DeviceStatus = DeviceStatus.ENABLED,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """初始化设备聚合根
        
        Args:
            device_id: 设备唯一标识
            entity_id: 设备实体ID（如 homeassistant 的 entity_id）
            name: 设备名称
            adapter_type: 适配器类型（如 "http", "mqtt"）
            manufacturer: 制造商
            capabilities: 设备能力集合
            status: 设备状态
            created_at: 创建时间
            updated_at: 更新时间
        """
        if not device_id:
            raise ValueError("设备ID不能为空")
        if not entity_id:
            raise ValueError("实体ID不能为空")
        if not name:
            raise ValueError("设备名称不能为空")
        if not adapter_type:
            raise ValueError("适配器类型不能为空")
        
        self._device_id = device_id
        self._entity_id = entity_id
        self._name = name
        self._adapter_type = adapter_type
        self._manufacturer = manufacturer
        self._capabilities = capabilities or DeviceCapabilities([])
        self._status = status
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        
        # 领域事件列表
        self._domain_events: List[object] = []
    
    @property
    def device_id(self) -> str:
        """获取设备ID"""
        return self._device_id
    
    @property
    def entity_id(self) -> str:
        """获取实体ID"""
        return self._entity_id
    
    @property
    def name(self) -> str:
        """获取设备名称"""
        return self._name
    
    @property
    def adapter_type(self) -> str:
        """获取适配器类型"""
        return self._adapter_type
    
    @property
    def manufacturer(self) -> Optional[str]:
        """获取制造商"""
        return self._manufacturer
    
    @property
    def capabilities(self) -> DeviceCapabilities:
        """获取设备能力"""
        return self._capabilities
    
    @property
    def status(self) -> DeviceStatus:
        """获取设备状态"""
        return self._status
    
    @property
    def created_at(self) -> datetime:
        """获取创建时间"""
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        """获取更新时间"""
        return self._updated_at
    
    def enable(self) -> None:
        """启用设备"""
        if self._status == DeviceStatus.ENABLED:
            return  # 已经是启用状态，无需操作
        
        old_status = self._status
        self._status = DeviceStatus.ENABLED
        self._updated_at = datetime.utcnow()
        
        # 发布领域事件
        event = DeviceStatusChanged(
            device_id=self._device_id,
            entity_id=self._entity_id,
            old_status=old_status,
            new_status=self._status,
            occurred_at=datetime.utcnow()
        )
        self._add_domain_event(event)
    
    def disable(self) -> None:
        """禁用设备"""
        if self._status == DeviceStatus.DISABLED:
            return  # 已经是禁用状态，无需操作
        
        old_status = self._status
        self._status = DeviceStatus.DISABLED
        self._updated_at = datetime.utcnow()
        
        # 发布领域事件
        event = DeviceStatusChanged(
            device_id=self._device_id,
            entity_id=self._entity_id,
            old_status=old_status,
            new_status=self._status,
            occurred_at=datetime.utcnow()
        )
        self._add_domain_event(event)
    
    def update_capabilities(self, capabilities: DeviceCapabilities) -> None:
        """更新设备能力"""
        if not capabilities:
            raise ValueError("能力集合不能为空")
        
        self._capabilities = capabilities
        self._updated_at = datetime.utcnow()
    
    def add_capability(self, capability: DeviceCapability) -> None:
        """添加单个能力"""
        if not capability:
            raise ValueError("能力不能为空")
        
        # 创建新的能力集合
        current_caps = list(self._capabilities.get_all())
        current_caps.append(capability)
        self._capabilities = DeviceCapabilities(current_caps)
        self._updated_at = datetime.utcnow()
    
    def has_capability(self, capability_name: str) -> bool:
        """检查是否支持某个能力"""
        return self._capabilities.has_capability(capability_name)
    
    def mark_as_unavailable(self) -> None:
        """标记设备为不可用"""
        if self._status == DeviceStatus.UNAVAILABLE:
            return
        
        old_status = self._status
        self._status = DeviceStatus.UNAVAILABLE
        self._updated_at = datetime.utcnow()
        
        # 发布领域事件
        event = DeviceStatusChanged(
            device_id=self._device_id,
            entity_id=self._entity_id,
            old_status=old_status,
            new_status=self._status,
            occurred_at=datetime.utcnow()
        )
        self._add_domain_event(event)
    
    def sync_state(self, state_data: dict) -> None:
        """同步设备状态（由领域服务调用）"""
        # 这里只更新更新时间，实际的状态同步逻辑由领域服务处理
        self._updated_at = datetime.utcnow()
    
    def get_domain_events(self) -> List[object]:
        """获取领域事件列表"""
        return list(self._domain_events)
    
    def clear_domain_events(self) -> None:
        """清除领域事件列表"""
        self._domain_events.clear()
    
    def _add_domain_event(self, event: object) -> None:
        """添加领域事件"""
        self._domain_events.append(event)
    

    # 构建新的设备对象
    @classmethod
    def create(
        cls,
        device_id: str,
        entity_id: str,
        name: str,
        adapter_type: str,
        manufacturer: Optional[str] = None,
        capabilities: Optional[DeviceCapabilities] = None
    ) -> "DeviceAggregate":
        """工厂方法：创建新设备
        
        创建设备时会自动发布 DeviceRegistered 事件
        """
        device = cls(
            device_id=device_id,
            entity_id=entity_id,
            name=name,
            adapter_type=adapter_type,
            manufacturer=manufacturer,
            capabilities=capabilities,
            status=DeviceStatus.ENABLED
        )
        
        # 发布设备注册事件
        event = DeviceRegistered(
            device_id=device_id,
            entity_id=entity_id,
            name=name,
            manufacturer=manufacturer,
            adapter_type=adapter_type,
            occurred_at=datetime.utcnow()
        )
        device._add_domain_event(event)
        
        return device
    
    def __eq__(self, other) -> bool:
        """相等性比较"""
        if not isinstance(other, DeviceAggregate):
            return False
        return self._device_id == other._device_id
    
    def __hash__(self) -> int:
        """哈希值"""
        return hash(self._device_id)

