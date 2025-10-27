"""
状态管理器（优化版）
纯内存状态，应用重启时从 HAL 重新加载
"""
import asyncio
from typing import Dict, Optional
from datetime import datetime

from domain.entities.device import DeviceState
from exceptions import StateManagerError


class StateManager:
    """
    内存状态管理器
    优化建议 #3：纯内存，不与数据库同步
    """
    
    def __init__(self):
        self._states: Dict[str, DeviceState] = {}
        self._lock = asyncio.Lock()
    
    async def get_state(self, device_id: str) -> Optional[DeviceState]:
        """
        获取设备状态
        
        Args:
            device_id: 设备 ID
            
        Returns:
            Optional[DeviceState]: 设备状态，不存在返回 None
        """
        async with self._lock:
            return self._states.get(device_id)
    
    async def set_state(self, device_id: str, state: DeviceState) -> None:
        """
        设置设备状态
        
        Args:
            device_id: 设备 ID
            state: 设备状态
        """
        async with self._lock:
            state.last_updated = datetime.now()
            self._states[device_id] = state
    
    async def update_state_attributes(
        self,
        device_id: str,
        attributes: Dict[str, any]
    ) -> None:
        """
        更新设备状态属性（部分更新）
        
        Args:
            device_id: 设备 ID
            attributes: 要更新的属性
        """
        async with self._lock:
            if device_id in self._states:
                self._states[device_id].attributes.update(attributes)
                self._states[device_id].last_updated = datetime.now()
            else:
                raise StateManagerError(f"Device state not found: {device_id}")
    
    async def has_state(self, device_id: str) -> bool:
        """
        检查设备状态是否存在
        
        Args:
            device_id: 设备 ID
            
        Returns:
            bool: 是否存在
        """
        async with self._lock:
            return device_id in self._states
    
    async def remove_state(self, device_id: str) -> None:
        """
        移除设备状态
        
        Args:
            device_id: 设备 ID
        """
        async with self._lock:
            if device_id in self._states:
                del self._states[device_id]
    
    async def get_all_states(self) -> Dict[str, DeviceState]:
        """
        获取所有设备状态
        
        Returns:
            Dict[str, DeviceState]: 所有设备状态
        """
        async with self._lock:
            return self._states.copy()
    
    async def clear(self) -> None:
        """清空所有状态"""
        async with self._lock:
            self._states.clear()
    
    def get_device_count(self) -> int:
        """获取设备数量"""
        return len(self._states)

