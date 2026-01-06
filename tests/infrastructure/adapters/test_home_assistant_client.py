"""Home Assistant 客户端单元测试

使用 pytest 和 httpx mock 测试 HomeAssistantClient 的所有功能。
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

import httpx

from src.infrastructure.adapters.hardware_adapter import HomeAssistantClient
from src.infrastructure.adapters.response_types import (
    HAStateObject,
    HAServiceDomain,
    HAEventType,
    HAConfig,
    HAHistoryEntry,
    HALogbookEntry,
)


# ==================== Fixtures ====================

@pytest.fixture
def client():
    """创建测试客户端实例"""
    return HomeAssistantClient(
        base_url="http://localhost:8123",
        access_token="test_token_123",
        timeout=10.0,
    )


@pytest.fixture
def mock_response():
    """创建 mock HTTP 响应工厂"""
    def _make_response(status_code: int, json_data=None, text=""):
        response = MagicMock(spec=httpx.Response)
        response.status_code = status_code
        response.text = text
        if json_data is not None:
            response.json.return_value = json_data
        else:
            response.json.side_effect = Exception("No JSON")
        return response
    return _make_response


# ==================== 初始化测试 ====================

class TestHomeAssistantClientInit:
    """测试客户端初始化"""
    
    def test_init_with_required_params(self):
        """测试必需参数初始化"""
        client = HomeAssistantClient(base_url="http://ha.local:8123")
        assert client.base_url == "http://ha.local:8123"
        assert client.access_token is None
        assert client.timeout == 30.0
        assert client.verify_ssl is True
    
    def test_init_with_all_params(self):
        """测试所有参数初始化"""
        client = HomeAssistantClient(
            base_url="https://ha.local:8123/",
            access_token="my_token",
            timeout=60.0,
            verify_ssl=False,
        )
        assert client.base_url == "https://ha.local:8123"  # 尾部斜杠被移除
        assert client.access_token == "my_token"
        assert client.timeout == 60.0
        assert client.verify_ssl is False
    
    def test_adapter_type(self, client):
        """测试适配器类型"""
        assert client.adapter_type == "homeassistant"
    
    def test_initial_connection_state(self, client):
        """测试初始连接状态"""
        assert client.is_connected is False


class TestHomeAssistantClientHeaders:
    """测试请求头构建"""
    
    def test_headers_with_token(self, client):
        """测试带 token 的请求头"""
        headers = client._get_headers()
        assert headers["Content-Type"] == "application/json"
        assert headers["Authorization"] == "Bearer test_token_123"
    
    def test_headers_without_token(self):
        """测试无 token 的请求头"""
        client = HomeAssistantClient(base_url="http://localhost:8123")
        headers = client._get_headers()
        assert headers["Content-Type"] == "application/json"
        assert "Authorization" not in headers


# ==================== 连接管理测试 ====================

class TestHomeAssistantClientConnection:
    """测试连接生命周期"""
    
    @pytest.mark.asyncio
    async def test_connect(self, client):
        """测试建立连接"""
        await client.connect()
        assert client.is_connected is True
        await client.disconnect()
    
    @pytest.mark.asyncio
    async def test_disconnect(self, client):
        """测试断开连接"""
        await client.connect()
        await client.disconnect()
        assert client.is_connected is False
    
    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """测试上下文管理器"""
        async with client:
            assert client.is_connected is True
        assert client.is_connected is False


# ==================== API 请求测试 ====================

class TestHomeAssistantClientCheckConnection:
    """测试连接检查"""
    
    @pytest.mark.asyncio
    async def test_check_connection_success(self, client, mock_response):
        """测试连接检查成功"""
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_req:
            from src.domain.Device.services.hardware_client import HardwareResponse
            mock_req.return_value = HardwareResponse.ok({"message": "API running."})
            
            result = await client.check_connection()
            
            assert result is True
            mock_req.assert_called_once_with("GET", "/api/")
    
    @pytest.mark.asyncio
    async def test_check_connection_failure(self, client):
        """测试连接检查失败"""
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_req:
            from src.domain.Device.services.hardware_client import HardwareResponse
            mock_req.return_value = HardwareResponse.failed("Connection refused", 503)
            
            result = await client.check_connection()
            
            assert result is False


class TestHomeAssistantClientGetState:
    """测试获取实体状态"""
    
    @pytest.mark.asyncio
    async def test_get_state_success(self, client):
        """测试获取状态成功"""
        state_data = {
            "entity_id": "sensor.temperature",
            "state": "23.5",
            "attributes": {"unit_of_measurement": "°C", "friendly_name": "温度"},
            "last_changed": "2024-01-01T12:00:00+00:00",
            "last_updated": "2024-01-01T12:00:00+00:00",
        }
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_req:
            from src.domain.Device.services.hardware_client import HardwareResponse
            mock_req.return_value = HardwareResponse.ok(state_data.copy())
            
            response = await client.get_state("sensor.temperature")
            
            assert response.success is True
            assert response.data["entity_id"] == "sensor.temperature"
            assert response.data["state"] == "23.5"
            assert "state_object" in response.data
            assert isinstance(response.data["state_object"], HAStateObject)
            mock_req.assert_called_once_with("GET", "/api/states/sensor.temperature")
    
    @pytest.mark.asyncio
    async def test_get_state_not_found(self, client):
        """测试获取不存在的实体"""
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_req:
            from src.domain.Device.services.hardware_client import HardwareResponse
            mock_req.return_value = HardwareResponse.failed("资源未找到: /api/states/sensor.nonexistent", 404)
            
            response = await client.get_state("sensor.nonexistent")
            
            assert response.success is False
            assert response.status_code == 404


class TestHomeAssistantClientGetAllStates:
    """测试获取所有实体状态"""
    
    @pytest.mark.asyncio
    async def test_get_all_states_success(self, client):
        """测试获取所有状态成功"""
        states_data = [
            {"entity_id": "sensor.temp", "state": "23", "attributes": {}, "last_changed": None, "last_updated": None},
            {"entity_id": "light.bedroom", "state": "on", "attributes": {"brightness": 255}, "last_changed": None, "last_updated": None},
        ]
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_req:
            from src.domain.Device.services.hardware_client import HardwareResponse
            mock_req.return_value = HardwareResponse.ok(states_data)
            
            response = await client.get_all_states()
            
            assert response.success is True
            assert response.data["count"] == 2
            assert len(response.data["states"]) == 2
            assert all(isinstance(s, HAStateObject) for s in response.data["states"])


class TestHomeAssistantClientCallService:
    """测试调用服务"""
    
    @pytest.mark.asyncio
    async def test_call_service_success(self, client):
        """测试调用服务成功"""
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_req:
            from src.domain.Device.services.hardware_client import HardwareResponse
            mock_req.return_value = HardwareResponse.ok([])
            
            response = await client.call_service(
                domain="light",
                service="turn_on",
                entity_id="light.living_room",
                data={"brightness": 200}
            )
            
            assert response.success is True
            mock_req.assert_called_once_with(
                "POST",
                "/api/services/light/turn_on",
                json_data={"entity_id": "light.living_room", "brightness": 200}
            )
    
    @pytest.mark.asyncio
    async def test_call_service_without_data(self, client):
        """测试调用服务无附加数据"""
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_req:
            from src.domain.Device.services.hardware_client import HardwareResponse
            mock_req.return_value = HardwareResponse.ok([])
            
            response = await client.call_service(
                domain="switch",
                service="turn_off",
                entity_id="switch.bedroom_fan"
            )
            
            assert response.success is True
            mock_req.assert_called_once_with(
                "POST",
                "/api/services/switch/turn_off",
                json_data={"entity_id": "switch.bedroom_fan"}
            )


class TestHomeAssistantClientExtendedMethods:
    """测试扩展方法"""
    
    @pytest.mark.asyncio
    async def test_get_config(self, client):
        """测试获取配置"""
        config_data = {
            "components": ["light", "switch"],
            "location_name": "Home",
            "latitude": 37.0,
            "longitude": -122.0,
            "version": "2024.1.0",
        }
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_req:
            from src.domain.Device.services.hardware_client import HardwareResponse
            mock_req.return_value = HardwareResponse.ok(config_data.copy())
            
            response = await client.get_config()
            
            assert response.success is True
            assert "config" in response.data
            assert isinstance(response.data["config"], HAConfig)
    
    @pytest.mark.asyncio
    async def test_get_services(self, client):
        """测试获取服务列表"""
        services_data = [
            {"domain": "light", "services": {"turn_on": {}, "turn_off": {}}},
            {"domain": "switch", "services": {"toggle": {}}},
        ]
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_req:
            from src.domain.Device.services.hardware_client import HardwareResponse
            mock_req.return_value = HardwareResponse.ok(services_data)
            
            response = await client.get_services()
            
            assert response.success is True
            assert response.data["count"] == 2
            assert all(isinstance(s, HAServiceDomain) for s in response.data["services"])
    
    @pytest.mark.asyncio
    async def test_fire_event(self, client):
        """测试触发事件"""
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_req:
            from src.domain.Device.services.hardware_client import HardwareResponse
            mock_req.return_value = HardwareResponse.ok({"message": "Event my_event fired."})
            
            response = await client.fire_event("my_event", {"key": "value"})
            
            assert response.success is True
            mock_req.assert_called_once_with(
                "POST",
                "/api/events/my_event",
                json_data={"key": "value"}
            )
    
    @pytest.mark.asyncio
    async def test_set_state(self, client):
        """测试设置状态"""
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_req:
            from src.domain.Device.services.hardware_client import HardwareResponse
            mock_req.return_value = HardwareResponse.ok({
                "entity_id": "sensor.custom",
                "state": "42",
                "attributes": {"unit": "items"}
            })
            
            response = await client.set_state(
                entity_id="sensor.custom",
                state="42",
                attributes={"unit": "items"}
            )
            
            assert response.success is True
            mock_req.assert_called_once_with(
                "POST",
                "/api/states/sensor.custom",
                json_data={"state": "42", "attributes": {"unit": "items"}}
            )
    
    @pytest.mark.asyncio
    async def test_render_template(self, client):
        """测试渲染模板"""
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_req:
            from src.domain.Device.services.hardware_client import HardwareResponse
            mock_req.return_value = HardwareResponse.ok({"text": "Temperature is 23°C"})
            
            response = await client.render_template("Temperature is {{ states('sensor.temp') }}°C")
            
            assert response.success is True
            assert response.data["result"] == "Temperature is 23°C"


class TestHomeAssistantClientErrorHandling:
    """测试错误处理"""
    
    @pytest.mark.asyncio
    async def test_auth_error(self, client):
        """测试认证错误"""
        async with client:
            with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_req:
                mock_resp = MagicMock()
                mock_resp.status_code = 401
                mock_resp.text = "Unauthorized"
                mock_req.return_value = mock_resp
                
                response = await client._request("GET", "/api/")
                
                assert response.success is False
                assert response.status_code == 401
                assert "认证失败" in response.error
    
    @pytest.mark.asyncio
    async def test_timeout_error(self, client):
        """测试超时错误"""
        async with client:
            with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_req:
                mock_req.side_effect = httpx.TimeoutException("Connection timed out")
                
                response = await client._request("GET", "/api/")
                
                assert response.success is False
                assert response.status_code == 408
                assert "超时" in response.error
    
    @pytest.mark.asyncio
    async def test_connection_error(self, client):
        """测试连接错误"""
        async with client:
            with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_req:
                mock_req.side_effect = httpx.ConnectError("Connection refused")
                
                response = await client._request("GET", "/api/")
                
                assert response.success is False
                assert response.status_code == 503
                assert "连接失败" in response.error


# ==================== 响应类型测试 ====================

class TestResponseTypes:
    """测试响应类型数据类"""
    
    def test_ha_state_object_from_dict(self):
        """测试 HAStateObject.from_dict"""
        data = {
            "entity_id": "light.test",
            "state": "on",
            "attributes": {"brightness": 255},
            "last_changed": "2024-01-01T00:00:00Z",
            "last_updated": "2024-01-01T00:00:00Z",
        }
        obj = HAStateObject.from_dict(data)
        
        assert obj.entity_id == "light.test"
        assert obj.state == "on"
        assert obj.attributes["brightness"] == 255
    
    def test_ha_config_from_dict(self):
        """测试 HAConfig.from_dict"""
        data = {
            "components": ["light", "switch"],
            "location_name": "Home",
            "version": "2024.1.0",
        }
        obj = HAConfig.from_dict(data)
        
        assert obj.location_name == "Home"
        assert obj.version == "2024.1.0"
        assert "light" in obj.components
    
    def test_ha_service_domain_from_dict(self):
        """测试 HAServiceDomain.from_dict"""
        data = {
            "domain": "light",
            "services": {"turn_on": {}, "turn_off": {}, "toggle": {}},
        }
        obj = HAServiceDomain.from_dict(data)
        
        assert obj.domain == "light"
        assert "turn_on" in obj.services
        assert "turn_off" in obj.services
    
    def test_ha_logbook_entry_from_dict(self):
        """测试 HALogbookEntry.from_dict"""
        data = {
            "name": "Living Room Light",
            "message": "turned on",
            "entity_id": "light.living_room",
            "domain": "light",
            "when": "2024-01-01T12:00:00Z",
        }
        obj = HALogbookEntry.from_dict(data)
        
        assert obj.name == "Living Room Light"
        assert obj.message == "turned on"
        assert obj.entity_id == "light.living_room"
