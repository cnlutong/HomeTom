"""
HAL 客户端（优化版）
使用 httpx 实现异步 HTTP 调用，配置连接池
"""
import httpx
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from config import config
from domain.entities.device import DeviceState
from exceptions import HALCommunicationError
from .models import HALDeviceState


class HALClient:
    """HAL 客户端封装"""
    
    def __init__(
        self,
        base_url: str = None,
        timeout: int = None,
        max_connections: int = None,
        max_keepalive: int = None
    ):
        self.base_url = base_url or config.HAL_ENDPOINT
        
        # 配置连接池（优化建议 #8）
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout or config.HAL_TIMEOUT,
            limits=httpx.Limits(
                max_connections=max_connections or config.HAL_MAX_CONNECTIONS,
                max_keepalive_connections=max_keepalive or config.HAL_MAX_KEEPALIVE
            ),
            transport=httpx.AsyncHTTPTransport(
                retries=config.HAL_RETRY_TIMES
            )
        )
    
    async def get_device_state(self, device_id: str) -> DeviceState:
        """
        获取设备状态
        
        Args:
            device_id: 设备 ID
            
        Returns:
            DeviceState: 设备状态
            
        Raises:
            HALCommunicationError: 通信失败
        """
        try:
            response = await self._client.get(f"/devices/{device_id}/state")
            response.raise_for_status()
            
            data = response.json()
            
            return DeviceState(
                state=data.get("state", "unknown"),
                attributes=data.get("attributes", {}),
                last_updated=datetime.now()
            )
            
        except httpx.HTTPStatusError as e:
            raise HALCommunicationError(
                f"Failed to get device state: {device_id}, status: {e.response.status_code}"
            )
        except httpx.RequestError as e:
            raise HALCommunicationError(
                f"Failed to connect to HAL: {e}"
            )
        except Exception as e:
            raise HALCommunicationError(
                f"Unexpected error getting device state: {e}"
            )
    
    async def control_device(self, device_id: str, command: Dict[str, Any]) -> bool:
        """
        控制设备
        
        Args:
            device_id: 设备 ID
            command: 控制命令
            
        Returns:
            bool: 是否成功
            
        Raises:
            HALCommunicationError: 通信失败
        """
        try:
            response = await self._client.post(
                f"/devices/{device_id}/control",
                json=command
            )
            response.raise_for_status()
            
            return response.json().get("success", False)
            
        except httpx.HTTPStatusError as e:
            raise HALCommunicationError(
                f"Failed to control device: {device_id}, status: {e.response.status_code}"
            )
        except httpx.RequestError as e:
            raise HALCommunicationError(
                f"Failed to connect to HAL: {e}"
            )
        except Exception as e:
            raise HALCommunicationError(
                f"Unexpected error controlling device: {e}"
            )
    
    async def subscribe_events(self, callback: Callable) -> None:
        """
        订阅 HAL 事件（WebSocket）
        
        注：初期可选实现，可用轮询代替
        
        Args:
            callback: 事件回调函数
        """
        # TODO: 实现 WebSocket 订阅
        # 这里预留接口，后续可根据 HAL 实际情况实现
        pass
    
    async def close(self):
        """关闭客户端连接"""
        await self._client.aclose()
    
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: HAL 是否可用
        """
        try:
            response = await self._client.get("/health")
            return response.status_code == 200
        except Exception:
            return False


class MockHALClient(HALClient):
    """
    Mock HAL 客户端（用于测试）
    优化建议 #13：依赖注入改进
    """
    
    def __init__(self):
        # 不初始化真实的 httpx 客户端
        self.base_url = "mock://hal"
        self._mock_states: Dict[str, DeviceState] = {}
    
    async def get_device_state(self, device_id: str) -> DeviceState:
        """返回 mock 状态"""
        return self._mock_states.get(
            device_id,
            DeviceState(state="unknown", attributes={})
        )
    
    async def control_device(self, device_id: str, command: Dict[str, Any]) -> bool:
        """Mock 控制设备"""
        # 更新 mock 状态
        current_state = self._mock_states.get(
            device_id,
            DeviceState(state="off", attributes={})
        )
        current_state.state = command.get("state", current_state.state)
        current_state.attributes.update(command)
        current_state.last_updated = datetime.now()
        
        self._mock_states[device_id] = current_state
        return True
    
    async def close(self):
        """Mock 关闭"""
        pass
    
    async def health_check(self) -> bool:
        """Mock 健康检查"""
        return True

