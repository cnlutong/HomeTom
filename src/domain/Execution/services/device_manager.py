"""设备管理器接口

定义设备管理的领域接口，用于场景执行时调用设备方法。
使用动态方法调用，根据命令名反射调用设备类方法。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import logging

from ...Device import BaseDevice


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
    
    负责管理设备实例，通过动态方法调用执行设备命令。
    """
    
    @abstractmethod
    async def get_device(self, entity_id: str) -> Optional[BaseDevice]:
        """获取设备实例"""
        pass
    
    @abstractmethod
    async def execute_command(
        self,
        entity_id: str,
        command: str,
        params: Optional[Dict[str, Any]] = None
    ) -> CommandResult:
        """执行设备命令（动态调用设备方法）"""
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
    
    通过动态方法调用执行设备命令。
    设备能力由设备类自身定义，不在此处硬编码。
    """
    
    def __init__(self, device_registry: Optional[Dict[str, BaseDevice]] = None):
        """初始化设备管理器
        
        Args:
            device_registry: 设备注册表 {entity_id: device}
        """
        self._devices: Dict[str, BaseDevice] = device_registry or {}
    
    def register_device(self, device: BaseDevice) -> None:
        """注册设备"""
        self._devices[device.get_entity_id()] = device
    
    def unregister_device(self, entity_id: str) -> None:
        """注销设备"""
        self._devices.pop(entity_id, None)
    
    async def get_device(self, entity_id: str) -> Optional[BaseDevice]:
        """获取设备实例"""
        return self._devices.get(entity_id)
    
    async def execute_command(
        self,
        entity_id: str,
        command: str,
        params: Optional[Dict[str, Any]] = None
    ) -> CommandResult:
        """执行设备命令
        
        使用反射机制动态调用设备方法。
        例如：command="turn_on" 会调用 device.turn_on()
              command="set_brightness", params={"brightness": 128}
              会调用 device.set_brightness(brightness=128)
        """
        device = await self.get_device(entity_id)
        
        if device is None:
            return CommandResult.failed(entity_id, command, f"设备不存在: {entity_id}")
        
        # 检查设备是否有该方法
        method = getattr(device, command, None)
        
        if method is None:
            return CommandResult.failed(
                entity_id, command, 
                f"设备 {entity_id} 不支持命令: {command}"
            )
        
        if not callable(method):
            return CommandResult.failed(
                entity_id, command,
                f"{command} 不是可调用的方法"
            )
        
        try:
            # 动态调用设备方法
            if params:
                result = method(**params)
            else:
                result = method()
            
            logger.info(f"命令执行成功: {entity_id}.{command}({params or ''})")
            
            return CommandResult.ok(
                entity_id, command,
                data={"result": result, "attributes": device.attributes}
            )
            
        except TypeError as e:
            # 参数错误
            return CommandResult.failed(entity_id, command, f"参数错误: {e}")
        except Exception as e:
            logger.exception(f"命令执行异常: {entity_id}.{command}")
            return CommandResult.failed(entity_id, command, str(e))
    
    async def get_device_state(self, entity_id: str) -> Optional[str]:
        """获取设备主状态"""
        device = await self.get_device(entity_id)
        if device:
            return device.get_state()
        return None
    
    async def get_device_attributes(self, entity_id: str) -> Dict[str, Any]:
        """获取设备属性（从 device.attributes 读取）"""
        device = await self.get_device(entity_id)
        if device:
            return device.attributes.copy()
        return {}
