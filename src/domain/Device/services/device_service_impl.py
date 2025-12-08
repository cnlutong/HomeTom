"""设备领域服务实现

提供设备相关的领域逻辑，如状态同步策略、能力更新、配置验证。
"""

import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime

from .device_service import IDeviceService
from ..aggregates.device_aggregate import DeviceAggregate
from ..value_objects.device_capability import DeviceCapabilities, DeviceCapability
from ..value_objects.device_status import DeviceStatus


logger = logging.getLogger(__name__)


class DeviceService(IDeviceService):
    """设备领域服务实现
    
    负责设备相关的领域逻辑：
    - 状态同步：根据外部状态数据更新设备状态
    - 能力更新：验证并更新设备能力
    - 配置验证：根据适配器类型验证设备配置
    """
    
    # 常见适配器类型及其必需配置
    ADAPTER_REQUIRED_CONFIG: Dict[str, Set[str]] = {
        "http": {"base_url"},
        "mqtt": {"broker_host", "topic_prefix"},
        "homeassistant": {"host", "access_token"},
        "websocket": {"url"},
    }
    
    # 常见设备类型及其标准能力
    DEVICE_TYPE_CAPABILITIES: Dict[str, List[str]] = {
        "light": ["turn_on", "turn_off", "toggle", "set_brightness"],
        "switch": ["turn_on", "turn_off", "toggle"],
        "cover": ["open", "close", "stop", "set_position"],
        "climate": ["set_temperature", "set_hvac_mode", "set_fan_mode"],
        "fan": ["turn_on", "turn_off", "set_speed"],
        "lock": ["lock", "unlock"],
        "sensor": [],  # 传感器通常只读
        "binary_sensor": [],
    }
    
    def __init__(self):
        """初始化设备领域服务"""
        pass
    
    async def sync_device_state(
        self, 
        device: DeviceAggregate,
        state_data: Dict[str, Any]
    ) -> None:
        """同步设备状态
        
        根据外部获取的状态数据更新设备聚合根。
        
        Args:
            device: 设备聚合根
            state_data: 从外部获取的状态数据
            
        状态数据格式示例：
        {
            "state": "on",
            "available": True,
            "attributes": {
                "brightness": 128,
                "color_temp": 4000
            },
            "last_updated": "2024-01-01T12:00:00Z"
        }
        """
        if not state_data:
            logger.warning(f"状态数据为空: device_id={device.device_id}")
            return
        
        # 检查设备可用性
        is_available = state_data.get("available", True)
        if not is_available:
            logger.info(f"设备不可用，标记为 UNAVAILABLE: device_id={device.device_id}")
            device.mark_as_unavailable()
            return
        
        # 设备可用，但当前状态是 UNAVAILABLE，恢复为 ENABLED
        if device.status == DeviceStatus.UNAVAILABLE:
            logger.info(f"设备恢复可用: device_id={device.device_id}")
            device.enable()
        
        # 调用聚合根的状态同步方法
        device.sync_state(state_data)
        
        logger.debug(
            f"设备状态同步完成: device_id={device.device_id}, "
            f"state={state_data.get('state')}"
        )
    
    async def update_capabilities(
        self,
        device: DeviceAggregate,
        capabilities: DeviceCapabilities
    ) -> None:
        """更新设备能力
        
        验证并更新设备的能力集合。
        
        Args:
            device: 设备聚合根
            capabilities: 新的能力集合
        """
        if not capabilities or len(capabilities) == 0:
            logger.warning(f"能力集合为空: device_id={device.device_id}")
            return
        
        # 获取旧能力用于比较
        old_capabilities = device.capabilities
        old_names = set(cap.name for cap in old_capabilities)
        new_names = set(cap.name for cap in capabilities)
        
        # 记录能力变化
        added = new_names - old_names
        removed = old_names - new_names
        
        if added:
            logger.info(f"新增能力: device_id={device.device_id}, added={added}")
        if removed:
            logger.info(f"移除能力: device_id={device.device_id}, removed={removed}")
        
        # 更新聚合根
        device.update_capabilities(capabilities)
        
        logger.debug(f"设备能力更新完成: device_id={device.device_id}")
    
    async def validate_device_config(
        self,
        adapter_type: str,
        config: Dict[str, Any]
    ) -> bool:
        """验证设备配置
        
        根据适配器类型验证配置是否包含必需项。
        
        Args:
            adapter_type: 适配器类型
            config: 设备配置
            
        Returns:
            配置是否有效
        """
        if not adapter_type:
            logger.error("适配器类型不能为空")
            return False
        
        if not config:
            logger.error("配置不能为空")
            return False
        
        # 获取该适配器类型的必需配置
        required = self.ADAPTER_REQUIRED_CONFIG.get(adapter_type.lower(), set())
        
        # 检查必需配置是否存在
        config_keys = set(config.keys())
        missing = required - config_keys
        
        if missing:
            logger.error(
                f"配置缺少必需项: adapter_type={adapter_type}, "
                f"missing={missing}"
            )
            return False
        
        logger.debug(f"配置验证通过: adapter_type={adapter_type}")
        return True
    
    def get_default_capabilities(self, device_type: str) -> DeviceCapabilities:
        """获取设备类型的默认能力
        
        Args:
            device_type: 设备类型（如 "light", "switch"）
            
        Returns:
            默认能力集合
        """
        capability_names = self.DEVICE_TYPE_CAPABILITIES.get(
            device_type.lower(), []
        )
        
        capabilities = [
            DeviceCapability(name=name) for name in capability_names
        ]
        
        return DeviceCapabilities(capabilities)
    
    def detect_device_type(self, entity_id: str) -> Optional[str]:
        """根据实体ID推断设备类型
        
        Home Assistant 风格的实体ID格式：domain.name
        例如：light.living_room, switch.bedroom_lamp
        
        Args:
            entity_id: 设备实体ID
            
        Returns:
            设备类型，如果无法推断返回 None
        """
        if not entity_id or "." not in entity_id:
            return None
        
        domain = entity_id.split(".")[0]
        
        # 映射 HA domain 到设备类型
        domain_type_map = {
            "light": "light",
            "switch": "switch",
            "cover": "cover",
            "climate": "climate",
            "fan": "fan",
            "lock": "lock",
            "sensor": "sensor",
            "binary_sensor": "binary_sensor",
            "button": "switch",
            "input_boolean": "switch",
        }
        
        return domain_type_map.get(domain)


# 单例实例
default_device_service = DeviceService()
