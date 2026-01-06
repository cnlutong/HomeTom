"""Home Assistant HTTP 客户端

实现 IHardwareClient 接口，通过 HTTP REST API 与 Home Assistant 系统通信。
基于官方文档: https://developers.home-assistant.io/docs/api/rest/
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode

import httpx

from ...domain.Device.services.hardware_client import IHardwareClient, HardwareResponse
from .response_types import (
    HAStateObject,
    HAServiceDomain,
    HAEventType,
    HAConfig,
    HAHistoryEntry,
    HALogbookEntry,
)


logger = logging.getLogger(__name__)


class HomeAssistantClientError(Exception):
    """Home Assistant 客户端错误基类"""
    pass


class HomeAssistantAuthError(HomeAssistantClientError):
    """认证错误 (401)"""
    pass


class HomeAssistantNotFoundError(HomeAssistantClientError):
    """资源未找到错误 (404)"""
    pass


class HomeAssistantClient(IHardwareClient):
    """Home Assistant REST API 客户端
    
    通过 HTTP REST API 与 Home Assistant 系统通信。
    
    使用示例:
        async with HomeAssistantClient(
            base_url="http://homeassistant.local:8123",
            access_token="your_long_lived_access_token"
        ) as client:
            # 检查连接
            if await client.check_connection():
                # 获取所有状态
                response = await client.get_all_states()
                if response.success:
                    for state in response.data["states"]:
                        print(f"{state.entity_id}: {state.state}")
                        
                # 调用服务
                await client.call_service(
                    domain="light",
                    service="turn_on",
                    entity_id="light.living_room",
                    data={"brightness": 128}
                )
    
    也可以手动管理生命周期:
        client = HomeAssistantClient(base_url, access_token)
        await client.connect()
        try:
            # 使用客户端...
        finally:
            await client.disconnect()
    """
    
    ADAPTER_TYPE = "homeassistant"
    
    def __init__(
        self,
        base_url: str,
        access_token: Optional[str] = None,
        timeout: float = 30.0,
        verify_ssl: bool = True,
    ):
        """初始化 Home Assistant 客户端
        
        Args:
            base_url: Home Assistant API 基础 URL，如 "http://homeassistant.local:8123"
            access_token: Long-Lived Access Token（从 HA 用户配置页面获取）
            timeout: 请求超时时间（秒），默认 30 秒
            verify_ssl: 是否验证 SSL 证书，默认 True
        """
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def adapter_type(self) -> str:
        """获取适配器类型标识"""
        return self.ADAPTER_TYPE
    
    @property
    def is_connected(self) -> bool:
        """检查客户端是否已连接"""
        return self._client is not None and not self._client.is_closed
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json",
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    async def connect(self) -> None:
        """建立 HTTP 连接
        
        创建一个持久的 httpx.AsyncClient 实例，
        可复用连接以提高性能。
        """
        if self._client is not None and not self._client.is_closed:
            logger.debug("客户端已连接，跳过重复连接")
            return
        
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._get_headers(),
            timeout=httpx.Timeout(self.timeout),
            verify=self.verify_ssl,
        )
        logger.info(f"已连接到 Home Assistant: {self.base_url}")
    
    async def disconnect(self) -> None:
        """断开 HTTP 连接
        
        关闭并释放 httpx.AsyncClient 资源。
        """
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.info("已断开 Home Assistant 连接")
    
    async def __aenter__(self) -> "HomeAssistantClient":
        """异步上下文管理器入口"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """异步上下文管理器出口"""
        await self.disconnect()
    
    async def _ensure_connected(self) -> httpx.AsyncClient:
        """确保客户端已连接，返回 HTTP 客户端实例"""
        if self._client is None or self._client.is_closed:
            await self.connect()
        return self._client  # type: ignore
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> HardwareResponse:
        """执行 HTTP 请求
        
        Args:
            method: HTTP 方法 (GET, POST, DELETE)
            endpoint: API 端点路径 (如 "/api/states")
            json_data: 请求体 JSON 数据
            params: URL 查询参数
            
        Returns:
            HardwareResponse: 统一响应对象
        """
        client = await self._ensure_connected()
        
        try:
            response = await client.request(
                method=method,
                url=endpoint,
                json=json_data,
                params=params,
            )
            
            # 根据状态码处理响应
            if response.status_code in (200, 201):
                # 成功响应
                try:
                    data = response.json()
                except Exception:
                    # 某些端点返回纯文本（如 /api/error_log）
                    data = {"text": response.text}
                return HardwareResponse.ok(data)
            
            elif response.status_code == 401:
                error_msg = "认证失败：请检查 Access Token 是否正确"
                logger.error(error_msg)
                return HardwareResponse.failed(error_msg, 401)
            
            elif response.status_code == 404:
                error_msg = f"资源未找到: {endpoint}"
                logger.warning(error_msg)
                return HardwareResponse.failed(error_msg, 404)
            
            elif response.status_code == 400:
                error_msg = f"请求无效: {response.text}"
                logger.warning(error_msg)
                return HardwareResponse.failed(error_msg, 400)
            
            elif response.status_code == 405:
                error_msg = f"方法不允许: {method} {endpoint}"
                logger.warning(error_msg)
                return HardwareResponse.failed(error_msg, 405)
            
            else:
                error_msg = f"请求失败 ({response.status_code}): {response.text}"
                logger.error(error_msg)
                return HardwareResponse.failed(error_msg, response.status_code)
        
        except httpx.TimeoutException as e:
            error_msg = f"请求超时: {endpoint}"
            logger.error(f"{error_msg} - {e}")
            return HardwareResponse.failed(error_msg, 408)
        
        except httpx.ConnectError as e:
            error_msg = f"连接失败: {self.base_url}"
            logger.error(f"{error_msg} - {e}")
            return HardwareResponse.failed(error_msg, 503)
        
        except Exception as e:
            error_msg = f"请求异常: {e}"
            logger.exception(error_msg)
            return HardwareResponse.failed(error_msg, 500)

    # ==================== IHardwareClient 接口实现 ====================
    
    async def call_service(
        self,
        domain: str,
        service: str,
        entity_id: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> HardwareResponse:
        """调用 Home Assistant 服务
        
        POST /api/services/{domain}/{service}
        
        Args:
            domain: 服务域，如 "light", "switch", "climate"
            service: 服务名，如 "turn_on", "turn_off", "set_temperature"
            entity_id: 实体 ID，如 "light.living_room"
            data: 附加服务数据，如 {"brightness": 128}
            
        Returns:
            HardwareResponse: 响应包含 changed_states 列表
            
        示例:
            # 开灯并设置亮度
            await client.call_service(
                "light", "turn_on", "light.living_room",
                {"brightness": 200, "color_temp": 300}
            )
            
            # 关闭开关
            await client.call_service("switch", "turn_off", "switch.bedroom_fan")
        """
        endpoint = f"/api/services/{domain}/{service}"
        
        payload: Dict[str, Any] = {"entity_id": entity_id}
        if data:
            payload.update(data)
        
        logger.info(f"调用服务: {domain}.{service} -> {entity_id}")
        logger.debug(f"服务数据: {payload}")
        
        return await self._request("POST", endpoint, json_data=payload)
    
    async def get_state(self, entity_id: str) -> HardwareResponse:
        """获取单个实体状态
        
        GET /api/states/{entity_id}
        
        Args:
            entity_id: 实体 ID，如 "sensor.temperature"
            
        Returns:
            HardwareResponse: 成功时 data 包含 HAStateObject 字段
        """
        endpoint = f"/api/states/{entity_id}"
        logger.debug(f"获取状态: {entity_id}")
        
        response = await self._request("GET", endpoint)
        
        if response.success and response.data:
            # 转换为类型化对象
            state_obj = HAStateObject.from_dict(response.data)
            response.data["state_object"] = state_obj
        
        return response
    
    async def get_all_states(self) -> HardwareResponse:
        """获取所有实体状态
        
        GET /api/states
        
        Returns:
            HardwareResponse: 成功时 data["states"] 包含 HAStateObject 列表
        """
        endpoint = "/api/states"
        logger.debug("获取所有实体状态")
        
        response = await self._request("GET", endpoint)
        
        if response.success and response.data:
            # 转换为类型化对象列表
            states = [HAStateObject.from_dict(s) for s in response.data]
            response.data = {"states": states, "count": len(states)}
        
        return response
    
    async def check_connection(self) -> bool:
        """检查与 Home Assistant 的连接状态
        
        GET /api/
        
        Returns:
            bool: 连接正常返回 True，否则返回 False
        """
        response = await self._request("GET", "/api/")
        
        if response.success:
            message = response.data.get("message", "") if response.data else ""
            logger.info(f"Home Assistant 连接正常: {message}")
            return True
        else:
            logger.warning(f"Home Assistant 连接检查失败: {response.error}")
            return False

    # ==================== Home Assistant 扩展方法 ====================
    
    async def get_config(self) -> HardwareResponse:
        """获取 Home Assistant 系统配置
        
        GET /api/config
        
        Returns:
            HardwareResponse: 成功时 data["config"] 包含 HAConfig 对象
        """
        endpoint = "/api/config"
        response = await self._request("GET", endpoint)
        
        if response.success and response.data:
            config = HAConfig.from_dict(response.data)
            response.data["config"] = config
        
        return response
    
    async def get_services(self) -> HardwareResponse:
        """获取所有可用服务
        
        GET /api/services
        
        Returns:
            HardwareResponse: 成功时 data["services"] 包含 HAServiceDomain 列表
        """
        endpoint = "/api/services"
        response = await self._request("GET", endpoint)
        
        if response.success and response.data:
            services = [HAServiceDomain.from_dict(s) for s in response.data]
            response.data = {"services": services, "count": len(services)}
        
        return response
    
    async def get_events(self) -> HardwareResponse:
        """获取所有事件类型
        
        GET /api/events
        
        Returns:
            HardwareResponse: 成功时 data["events"] 包含 HAEventType 列表
        """
        endpoint = "/api/events"
        response = await self._request("GET", endpoint)
        
        if response.success and response.data:
            events = [HAEventType.from_dict(e) for e in response.data]
            response.data = {"events": events, "count": len(events)}
        
        return response
    
    async def fire_event(
        self,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None,
    ) -> HardwareResponse:
        """触发自定义事件
        
        POST /api/events/{event_type}
        
        Args:
            event_type: 事件类型名称
            event_data: 事件数据
            
        Returns:
            HardwareResponse: 成功时返回确认消息
        """
        endpoint = f"/api/events/{event_type}"
        logger.info(f"触发事件: {event_type}")
        
        return await self._request("POST", endpoint, json_data=event_data or {})
    
    async def set_state(
        self,
        entity_id: str,
        state: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> HardwareResponse:
        """设置实体状态
        
        POST /api/states/{entity_id}
        
        注意: 这只更新 Home Assistant 中的状态表示，
        不会实际控制物理设备。要控制设备请使用 call_service。
        
        Args:
            entity_id: 实体 ID
            state: 状态值
            attributes: 状态属性
            
        Returns:
            HardwareResponse: 成功时返回更新后的状态
        """
        endpoint = f"/api/states/{entity_id}"
        
        payload: Dict[str, Any] = {"state": state}
        if attributes:
            payload["attributes"] = attributes
        
        logger.info(f"设置状态: {entity_id} = {state}")
        
        return await self._request("POST", endpoint, json_data=payload)
    
    async def delete_state(self, entity_id: str) -> HardwareResponse:
        """删除实体状态
        
        DELETE /api/states/{entity_id}
        
        Args:
            entity_id: 实体 ID
            
        Returns:
            HardwareResponse: 操作结果
        """
        endpoint = f"/api/states/{entity_id}"
        logger.info(f"删除状态: {entity_id}")
        
        return await self._request("DELETE", endpoint)
    
    async def get_history(
        self,
        entity_ids: List[str],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        minimal_response: bool = True,
        no_attributes: bool = False,
        significant_changes_only: bool = False,
    ) -> HardwareResponse:
        """获取实体历史状态
        
        GET /api/history/period/{timestamp}
        
        Args:
            entity_ids: 实体 ID 列表
            start_time: 开始时间（默认为 1 天前）
            end_time: 结束时间（默认为当前时间）
            minimal_response: 是否返回精简响应（更快）
            no_attributes: 是否跳过属性（更快）
            significant_changes_only: 只返回显著变化
            
        Returns:
            HardwareResponse: 成功时 data["history"] 包含历史记录
        """
        # 构建 URL
        if start_time:
            timestamp = start_time.isoformat()
            endpoint = f"/api/history/period/{timestamp}"
        else:
            endpoint = "/api/history/period"
        
        # 构建查询参数
        params: Dict[str, Any] = {
            "filter_entity_id": ",".join(entity_ids),
        }
        if end_time:
            params["end_time"] = end_time.isoformat()
        if minimal_response:
            params["minimal_response"] = ""
        if no_attributes:
            params["no_attributes"] = ""
        if significant_changes_only:
            params["significant_changes_only"] = ""
        
        response = await self._request("GET", endpoint, params=params)
        
        if response.success and response.data:
            # 响应是实体历史的嵌套列表
            history_by_entity: Dict[str, List[HAHistoryEntry]] = {}
            for entity_history in response.data:
                if entity_history:
                    entries = [HAHistoryEntry.from_dict(h) for h in entity_history]
                    if entries:
                        history_by_entity[entries[0].entity_id] = entries
            response.data = {"history": history_by_entity}
        
        return response
    
    async def get_logbook(
        self,
        entity_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> HardwareResponse:
        """获取日志记录
        
        GET /api/logbook/{timestamp}
        
        Args:
            entity_id: 可选，筛选特定实体
            start_time: 开始时间（默认为 1 天前）
            end_time: 结束时间
            
        Returns:
            HardwareResponse: 成功时 data["entries"] 包含日志条目列表
        """
        if start_time:
            timestamp = start_time.isoformat()
            endpoint = f"/api/logbook/{timestamp}"
        else:
            endpoint = "/api/logbook"
        
        params: Dict[str, Any] = {}
        if entity_id:
            params["entity"] = entity_id
        if end_time:
            params["end_time"] = end_time.isoformat()
        
        response = await self._request("GET", endpoint, params=params if params else None)
        
        if response.success and response.data:
            entries = [HALogbookEntry.from_dict(e) for e in response.data]
            response.data = {"entries": entries, "count": len(entries)}
        
        return response
    
    async def render_template(self, template: str) -> HardwareResponse:
        """渲染 Jinja2 模板
        
        POST /api/template
        
        Args:
            template: Jinja2 模板字符串，如 "{{ states('sensor.temperature') }}°C"
            
        Returns:
            HardwareResponse: 成功时 data["result"] 包含渲染结果
        """
        endpoint = "/api/template"
        logger.debug(f"渲染模板: {template[:50]}...")
        
        response = await self._request("POST", endpoint, json_data={"template": template})
        
        if response.success and response.data:
            # 模板渲染返回纯文本
            result = response.data.get("text", str(response.data))
            response.data = {"result": result}
        
        return response
    
    async def get_error_log(self) -> HardwareResponse:
        """获取错误日志
        
        GET /api/error_log
        
        Returns:
            HardwareResponse: 成功时 data["log"] 包含错误日志文本
        """
        endpoint = "/api/error_log"
        response = await self._request("GET", endpoint)
        
        if response.success and response.data:
            log_text = response.data.get("text", "")
            response.data = {"log": log_text}
        
        return response
    
    async def check_config(self) -> HardwareResponse:
        """检查配置文件有效性
        
        POST /api/config/core/check_config
        
        Returns:
            HardwareResponse: data 包含 {"result": "valid"/"invalid", "errors": ...}
        """
        endpoint = "/api/config/core/check_config"
        return await self._request("POST", endpoint)


# 保留旧类名作为别名以保持向后兼容
HttpHardwareClient = HomeAssistantClient
