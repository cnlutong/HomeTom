"""设备管理器接口

定义设备管理的领域接口，用于场景执行时调用设备方法。
通过 IHardwareClient 与实际硬件系统通信。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import logging

from ...Device.services.hardware_client import IHardwareClient, HardwareResponse


logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """命令执行结果"""
    success: bool
    entity_id: str
    command: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    
    @classmethod
    def ok(cls, entity_id: str, command: str, data: Optional[Dict[str, Any]] = None) -> "CommandResult":
        return cls(success=True, entity_id=entity_id, command=command, data=data)
    
    @classmethod
    def failed(cls, entity_id: str, command: str, message: str) -> "CommandResult":
        return cls(success=False, entity_id=entity_id, command=command, message=message)


class IDeviceManager(ABC):
    """设备管理器接口
    
    负责管理设备实例，通过硬件客户端执行设备命令。
    """
    
    @abstractmethod
    async def execute_command(
        self,
        entity_id: str,
        command: str,
        params: Optional[Dict[str, Any]] = None
    ) -> CommandResult:
        """执行设备命令"""
        pass
    
    @abstractmethod
    async def get_device_state(self, entity_id: str) -> Optional[str]:
        """获取设备主状态"""
        pass
    
    @abstractmethod
    async def get_device_attributes(self, entity_id: str) -> Dict[str, Any]:
        """获取设备属性"""
        pass


class DeviceManager(IDeviceManager):
    """设备管理器实现
    
    通过 IHardwareClient 与硬件交互执行设备命令。
    """
    
    # 命令到 Home Assistant 服务的映射
    COMMAND_SERVICE_MAP = {
        "turn_on": ("turn_on", {}),
        "turn_off": ("turn_off", {}),
        "toggle": ("toggle", {}),
        "set_brightness": ("turn_on", lambda p: {"brightness": p.get("brightness", 255)}),
        "set_color_rgb": ("turn_on", lambda p: {"rgb_color": [p.get("r", 255), p.get("g", 255), p.get("b", 255)]}),
        "set_color_temp": ("turn_on", lambda p: {"color_temp": p.get("color_temp", 300)}),
        "set_temperature": ("set_temperature", lambda p: {"temperature": p.get("temperature", 22)}),
        "set_hvac_mode": ("set_hvac_mode", lambda p: {"hvac_mode": p.get("mode", "auto")}),
        "set_fan_mode": ("set_fan_mode", lambda p: {"fan_mode": p.get("mode", "auto")}),
        "set_value": ("turn_on", lambda p: p),  # 通用值设置
    }
    
    def __init__(self, hardware_client: IHardwareClient):
        """初始化设备管理器
        
        Args:
            hardware_client: 硬件客户端接口
        """
        self._client = hardware_client
    
    def _get_domain_from_entity_id(self, entity_id: str) -> str:
        """从 entity_id 中提取域名
        
        例如: "light.living_room" -> "light"
        """
        if "." in entity_id:
            return entity_id.split(".")[0]
        # 默认猜测
        if "light" in entity_id or "lamp" in entity_id:
            return "light"
        elif "switch" in entity_id:
            return "switch"
        elif "climate" in entity_id or "conditioner" in entity_id:
            return "climate"
        elif "sensor" in entity_id:
            return "sensor"
        return "homeassistant"
    
    def _map_command_to_service(
        self, 
        command: str, 
        params: Optional[Dict[str, Any]]
    ) -> tuple[str, Dict[str, Any]]:
        """将命令映射为 Home Assistant 服务名和数据
        
        Args:
            command: 命令名 (如 "turn_on", "set_brightness")
            params: 命令参数
            
        Returns:
            (service_name, service_data) 元组
        """
        mapping = self.COMMAND_SERVICE_MAP.get(command)
        
        if mapping is None:
            # 未知命令，尝试直接使用命令名作为服务名
            return (command, params or {})
        
        service_name, data_builder = mapping
        
        if callable(data_builder):
            service_data = data_builder(params or {})
        else:
            service_data = data_builder.copy() if data_builder else {}
        
        return (service_name, service_data)

    async def execute_command(
        self,
        entity_id: str,
        command: str,
        params: Optional[Dict[str, Any]] = None
    ) -> CommandResult:
        """执行设备命令
        
        将命令转换为 Home Assistant 服务调用。
        例如：command="turn_on" 会调用 /api/services/{domain}/turn_on
              command="set_brightness", params={"brightness": 128}
              会调用 /api/services/light/turn_on with data={"brightness": 128}
        """
        domain = self._get_domain_from_entity_id(entity_id)
        service_name, service_data = self._map_command_to_service(command, params)
        
        logger.info(f"执行命令: {entity_id}.{command}({params}) -> {domain}.{service_name}({service_data})")
        
        try:
            response: HardwareResponse = await self._client.call_service(
                domain=domain,
                service=service_name,
                entity_id=entity_id,
                data=service_data if service_data else None
            )
            
            if response.success:
                logger.info(f"命令执行成功: {entity_id}.{command}")
                return CommandResult.ok(
                    entity_id, command,
                    data=response.data
                )
            else:
                logger.warning(f"命令执行失败: {entity_id}.{command} - {response.error}")
                return CommandResult.failed(
                    entity_id, command,
                    message=response.error or "Unknown error"
                )
                
        except Exception as e:
            logger.exception(f"命令执行异常: {entity_id}.{command}")
            return CommandResult.failed(entity_id, command, str(e))
    
    async def get_device_state(self, entity_id: str) -> Optional[str]:
        """获取设备主状态"""
        try:
            response = await self._client.get_state(entity_id)
            if response.success and response.data:
                return response.data.get("state")
            return None
        except Exception as e:
            logger.exception(f"获取设备状态异常: {entity_id}")
            return None
    
    async def get_device_attributes(self, entity_id: str) -> Dict[str, Any]:
        """获取设备属性"""
        try:
            response = await self._client.get_state(entity_id)
            if response.success and response.data:
                return response.data.get("attributes", {})
            return {}
        except Exception as e:
            logger.exception(f"获取设备属性异常: {entity_id}")
            return {}
