"""Home Assistant REST API 测试服务器

模拟 Home Assistant REST API，专注于提供各种硬件设备接口测试。
设备状态持久化存储在 devices/ 目录的 JSON 文件中。

运行方式：
    python3 -m uvicorn test_API_server.main:app --port 8123 --reload

测试端点：
    http://localhost:8123/api/ - API 状态检查
    http://localhost:8123/docs - Swagger UI 文档
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Header, Request, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

# ==================== 配置 ====================

DEVICES_DIR = Path(__file__).parent / "devices"
VALID_TOKENS = {"test_token", "long_lived_access_token"}

# ==================== 日志配置 ====================

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("ha_test_server")

# ==================== JSON 文件存储 ====================

class JsonDeviceStore:
    """基于 JSON 文件的设备存储
    
    每个设备存储为单独的 JSON 文件：
        devices/{domain}/{device_name}.json
    
    设备状态的增删改查直接操作 JSON 文件，实现持久化。
    """
    
    def __init__(self, devices_dir: Path):
        self.devices_dir = devices_dir
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._service_calls: List[Dict[str, Any]] = []
        self._events_fired: List[Dict[str, Any]] = []
    
    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
    
    def _get_file_path(self, entity_id: str) -> Path:
        """获取设备 JSON 文件路径"""
        domain, name = entity_id.split(".", 1)
        return self.devices_dir / domain / f"{name}.json"
    
    def _read_json(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """读取 JSON 文件"""
        try:
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"读取 JSON 失败: {file_path} - {e}")
        return None
    
    def _write_json(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """写入 JSON 文件"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"写入 JSON 失败: {file_path} - {e}")
            return False
    
    def _delete_json(self, file_path: Path) -> bool:
        """删除 JSON 文件"""
        try:
            if file_path.exists():
                file_path.unlink()
                return True
        except Exception as e:
            logger.error(f"删除 JSON 失败: {file_path} - {e}")
        return False
    
    def load_all(self) -> int:
        """从 JSON 文件加载所有设备到缓存"""
        self._cache.clear()
        count = 0
        
        if not self.devices_dir.exists():
            logger.warning(f"设备目录不存在: {self.devices_dir}")
            return 0
        
        for domain_dir in self.devices_dir.iterdir():
            if domain_dir.is_dir() and not domain_dir.name.startswith("."):
                for json_file in domain_dir.glob("*.json"):
                    data = self._read_json(json_file)
                    if data and "entity_id" in data:
                        self._cache[data["entity_id"]] = data
                        count += 1
        
        logger.info(f"📂 从 JSON 文件加载了 {count} 个设备")
        return count
    
    def get_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """获取设备状态（优先从缓存，否则从文件）"""
        if entity_id in self._cache:
            return self._cache[entity_id]
        
        file_path = self._get_file_path(entity_id)
        data = self._read_json(file_path)
        if data:
            self._cache[entity_id] = data
        return data
    
    def get_all_states(self) -> List[Dict[str, Any]]:
        """获取所有设备状态"""
        return list(self._cache.values())
    
    def get_states_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """按域获取设备列表"""
        return [s for s in self._cache.values() if s["entity_id"].startswith(f"{domain}.")]
    
    def set_state(
        self, 
        entity_id: str, 
        state: str, 
        attributes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """设置设备状态（同时更新缓存和文件）"""
        now = self._now()
        
        existing = self.get_state(entity_id)
        if existing:
            old_state = existing.get("state")
            existing["state"] = state
            existing["last_updated"] = now
            if old_state != state:
                existing["last_changed"] = now
            if attributes:
                existing["attributes"].update(attributes)
            data = existing
        else:
            data = {
                "entity_id": entity_id,
                "state": state,
                "attributes": attributes or {},
                "last_changed": now,
                "last_updated": now,
            }
        
        # 写入文件
        file_path = self._get_file_path(entity_id)
        if self._write_json(file_path, data):
            self._cache[entity_id] = data
        
        return data
    
    def delete_state(self, entity_id: str) -> bool:
        """删除设备（同时删除缓存和文件）"""
        file_path = self._get_file_path(entity_id)
        if self._delete_json(file_path):
            self._cache.pop(entity_id, None)
            return True
        return False
    
    def record_service_call(self, domain: str, service: str, data: Dict[str, Any]):
        """记录服务调用"""
        self._service_calls.append({
            "domain": domain,
            "service": service,
            "data": data,
            "timestamp": self._now(),
        })
        # 只保留最近 100 条
        if len(self._service_calls) > 100:
            self._service_calls = self._service_calls[-100:]
    
    def record_event(self, event_type: str, event_data: Dict[str, Any]):
        """记录事件"""
        self._events_fired.append({
            "event_type": event_type,
            "data": event_data,
            "timestamp": self._now(),
        })
        if len(self._events_fired) > 100:
            self._events_fired = self._events_fired[-100:]
    
    @property
    def service_calls(self) -> List[Dict[str, Any]]:
        return self._service_calls
    
    @property
    def events_fired(self) -> List[Dict[str, Any]]:
        return self._events_fired


# 全局数据存储
store = JsonDeviceStore(DEVICES_DIR)

# ==================== Pydantic 模型 ====================

class StatePayload(BaseModel):
    state: str
    attributes: Optional[Dict[str, Any]] = None

class ServiceCallPayload(BaseModel):
    entity_id: Optional[str] = None
    class Config:
        extra = "allow"

class TemplatePayload(BaseModel):
    template: str

class EventPayload(BaseModel):
    class Config:
        extra = "allow"

# ==================== FastAPI 应用 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    count = store.load_all()
    logger.info("🚀 Home Assistant 测试服务器启动")
    logger.info(f"📖 Swagger 文档: http://localhost:8123/docs")
    logger.info(f"🏠 已加载 {count} 个设备 (JSON 持久化)")
    yield
    logger.info("👋 服务器关闭")

app = FastAPI(
    title="Home Assistant Hardware API Test Server",
    description="模拟 Home Assistant REST API，专注于硬件设备接口（JSON 持久化）",
    version="3.0.0",
    lifespan=lifespan,
)

async def verify_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization[7:]
    if token not in VALID_TOKENS:
        raise HTTPException(status_code=401, detail="Invalid access token")
    return token

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = datetime.now()
    
    # 获取请求体以供记录日志（如果是 POST/PUT/DELETE）
    request_body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body_bytes = await request.body()
            if body_bytes:
                request_body = json.loads(body_bytes)
        except Exception:
            pass

    response = await call_next(request)
    ms = (datetime.now() - start).total_seconds() * 1000
    emoji = "✅" if response.status_code < 400 else "❌"
    
    # 记录基本请求信息
    logger.info(f"{emoji} {request.method:6} {request.url.path:<50} {response.status_code} ({ms:.0f}ms)")
    
    # 如果有请求体且是非 GET 请求，则记录请求体
    if request_body:
        logger.info(f"   📥 请求 Payload: {json.dumps(request_body, ensure_ascii=False)}")
        
    return response

# ==================== API 端点 ====================

@app.get("/api/")
async def api_root(authorization: str = Header(None)):
    await verify_token(authorization)
    return {"message": "API running."}

@app.get("/api/config")
async def get_config(authorization: str = Header(None)):
    await verify_token(authorization)
    return {
        "components": ["light", "switch", "cover", "climate", "fan", "lock", "vacuum",
                       "sensor", "binary_sensor", "device_tracker", "weather",
                       "media_player", "camera", "alarm_control_panel"],
        "config_dir": "/config",
        "elevation": 10,
        "latitude": 31.2304,
        "longitude": 121.4737,
        "location_name": "测试智能家居",
        "time_zone": "Asia/Shanghai",
        "version": "2024.1.0",
        "unit_system": {"length": "km", "mass": "kg", "temperature": "°C", "volume": "L"},
    }

@app.get("/api/services")
async def get_services(authorization: str = Header(None)):
    await verify_token(authorization)
    return [
        {"domain": "light", "services": {"turn_on": {}, "turn_off": {}, "toggle": {}}},
        {"domain": "switch", "services": {"turn_on": {}, "turn_off": {}, "toggle": {}}},
        {"domain": "cover", "services": {"open_cover": {}, "close_cover": {}, "set_cover_position": {}, "stop_cover": {}}},
        {"domain": "climate", "services": {"set_temperature": {}, "set_hvac_mode": {}, "set_fan_mode": {}, "turn_on": {}, "turn_off": {}}},
        {"domain": "fan", "services": {"turn_on": {}, "turn_off": {}, "set_percentage": {}, "oscillate": {}}},
        {"domain": "lock", "services": {"lock": {}, "unlock": {}}},
        {"domain": "vacuum", "services": {"start": {}, "stop": {}, "pause": {}, "return_to_base": {}, "set_fan_speed": {}}},
        {"domain": "media_player", "services": {"turn_on": {}, "turn_off": {}, "play_media": {}, "media_play": {}, "media_pause": {}, "media_stop": {}, "volume_set": {}, "volume_mute": {}}},
        {"domain": "camera", "services": {"turn_on": {}, "turn_off": {}, "enable_motion_detection": {}, "disable_motion_detection": {}}},
        {"domain": "alarm_control_panel", "services": {"alarm_arm_home": {}, "alarm_arm_away": {}, "alarm_arm_night": {}, "alarm_disarm": {}, "alarm_trigger": {}}},
    ]

@app.get("/api/events")
async def get_events(authorization: str = Header(None)):
    await verify_token(authorization)
    return [
        {"event": "state_changed", "listener_count": 10},
        {"event": "call_service", "listener_count": 5},
    ]

@app.get("/api/states")
async def get_all_states(authorization: str = Header(None)):
    await verify_token(authorization)
    return store.get_all_states()

@app.get("/api/states/{entity_id:path}")
async def get_state(entity_id: str, authorization: str = Header(None)):
    await verify_token(authorization)
    state = store.get_state(entity_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Entity not found: {entity_id}")
    return state

@app.post("/api/states/{entity_id:path}")
async def set_state(entity_id: str, payload: StatePayload, authorization: str = Header(None)):
    await verify_token(authorization)
    is_new = store.get_state(entity_id) is None
    result = store.set_state(entity_id, payload.state, payload.attributes)
    logger.info(f"{'✨ 创建' if is_new else '📝 更新'} {entity_id} = {payload.state}")
    logger.info(f"   📤 返回结果: {json.dumps(result, ensure_ascii=False)}")
    return result

@app.delete("/api/states/{entity_id:path}")
async def delete_state(entity_id: str, authorization: str = Header(None)):
    await verify_token(authorization)
    if not store.delete_state(entity_id):
        raise HTTPException(status_code=404, detail=f"Entity not found: {entity_id}")
    logger.info(f"🗑️  删除 {entity_id} [已删除 JSON 文件]")
    return {"message": f"Entity {entity_id} deleted"}

@app.post("/api/services/{domain}/{service}")
async def call_service(domain: str, service: str, payload: ServiceCallPayload, authorization: str = Header(None)):
    await verify_token(authorization)
    data = payload.model_dump()
    entity_id = data.get("entity_id")
    
    store.record_service_call(domain, service, data)
    logger.info(f"🔧 服务调用: {domain}.{service}" + (f" -> {entity_id}" if entity_id else ""))
    
    changed_states = []
    if entity_id and (state := store.get_state(entity_id)):
        old = state["state"]
        new_state = old
        new_attrs = {}
        
        # 通用服务处理
        if service == "turn_on":
            new_state = "on"
            if "brightness" in data: new_attrs["brightness"] = data["brightness"]
            if "color_temp" in data: new_attrs["color_temp"] = data["color_temp"]
            if "percentage" in data: new_attrs["percentage"] = data["percentage"]
        elif service == "turn_off":
            new_state = "off"
        elif service == "toggle":
            new_state = "off" if old == "on" else "on"
        
        # Cover 服务
        elif service == "open_cover":
            new_state = "open"
            new_attrs["position"] = 100
        elif service == "close_cover":
            new_state = "closed"
            new_attrs["position"] = 0
        elif service == "set_cover_position":
            pos = data.get("position", 50)
            new_state = "open" if pos > 0 else "closed"
            new_attrs["position"] = pos
        
        # Climate 服务
        elif service == "set_temperature":
            new_attrs["temperature"] = data.get("temperature", 24)
        elif service == "set_hvac_mode":
            new_state = data.get("hvac_mode", "auto")
        elif service == "set_fan_mode":
            new_attrs["fan_mode"] = data.get("fan_mode", "auto")
        
        # Lock 服务
        elif service == "lock":
            new_state = "locked"
            new_attrs["is_locked"] = True
        elif service == "unlock":
            new_state = "unlocked"
            new_attrs["is_locked"] = False
        
        # Media Player 服务
        elif service == "media_play":
            new_state = "playing"
        elif service == "media_pause":
            new_state = "paused"
        elif service == "media_stop":
            new_state = "idle"
        elif service == "volume_set":
            new_attrs["volume_level"] = data.get("volume_level", 0.5)
        elif service == "volume_mute":
            new_attrs["is_volume_muted"] = data.get("is_volume_muted", True)
        
        # Vacuum 服务
        elif service == "start":
            new_state = "cleaning"
        elif service == "pause":
            new_state = "paused"
        elif service == "return_to_base":
            new_state = "returning"
        elif service == "set_fan_speed":
            new_attrs["fan_speed"] = data.get("fan_speed", "standard")
        
        # Alarm 服务
        elif service == "alarm_arm_home":
            new_state = "armed_home"
        elif service == "alarm_arm_away":
            new_state = "armed_away"
        elif service == "alarm_arm_night":
            new_state = "armed_night"
        elif service == "alarm_disarm":
            new_state = "disarmed"
        elif service == "alarm_trigger":
            new_state = "triggered"
        
        # Fan 服务
        elif service == "set_percentage":
            new_attrs["percentage"] = data.get("percentage", 50)
        elif service == "oscillate":
            new_attrs["oscillating"] = data.get("oscillating", True)
        
        store.set_state(entity_id, new_state, new_attrs if new_attrs else None)
        if old != new_state:
            logger.info(f"   📍 {entity_id}: {old} -> {new_state}")
        
        updated_state = store.get_state(entity_id)
        changed_states.append(updated_state)
    
    logger.info(f"   📤 调用结果: {json.dumps(changed_states, ensure_ascii=False)}")
    return changed_states

@app.post("/api/events/{event_type}")
async def fire_event(event_type: str, payload: EventPayload, authorization: str = Header(None)):
    await verify_token(authorization)
    store.record_event(event_type, payload.model_dump())
    logger.info(f"🎉 事件: {event_type}")
    return {"message": f"Event {event_type} fired."}

@app.get("/api/history/period")
@app.get("/api/history/period/{timestamp}")
async def get_history(
    filter_entity_id: str = Query(...),
    timestamp: Optional[str] = None,
    authorization: str = Header(None),
    **kwargs
):
    await verify_token(authorization)
    result = []
    for eid in filter_entity_id.split(","):
        if state := store.get_state(eid.strip()):
            result.append([state])
    return result

@app.get("/api/logbook")
@app.get("/api/logbook/{timestamp}")
async def get_logbook(timestamp: Optional[str] = None, authorization: str = Header(None), **kwargs):
    await verify_token(authorization)
    return [
        {"name": "客厅灯", "message": "turned on", "entity_id": "light.living_room", "domain": "light", "when": store._now()},
    ]

@app.post("/api/template")
async def render_template(payload: TemplatePayload, authorization: str = Header(None)):
    await verify_token(authorization)
    import re
    result = payload.template
    for eid in re.findall(r"\{\{\s*states\(['\"]([^'\"]+)['\"]\)\s*\}\}", payload.template):
        state = store.get_state(eid)
        result = re.sub(rf"\{{\{{\s*states\(['\"]" + re.escape(eid) + r"['\"]\)\s*\}}\}}", 
                       state["state"] if state else "unknown", result)
    return PlainTextResponse(result)

@app.get("/api/error_log")
async def get_error_log(authorization: str = Header(None)):
    await verify_token(authorization)
    return PlainTextResponse("No errors logged.")

@app.post("/api/config/core/check_config")
async def check_config(authorization: str = Header(None)):
    await verify_token(authorization)
    return {"result": "valid", "errors": None}

# ==================== 测试辅助端点 ====================

@app.post("/test/reload")
async def reload_devices():
    """重新加载所有设备 JSON 文件"""
    count = store.load_all()
    logger.info(f"🔄 重新加载了 {count} 个设备")
    return {"message": "Reload OK", "device_count": count}

@app.get("/test/service-calls")
async def get_service_calls():
    """获取服务调用记录"""
    return store.service_calls

@app.get("/test/events")
async def get_fired_events():
    """获取已触发事件"""
    return store.events_fired

@app.get("/test/devices/{domain}")
async def get_devices_by_domain(domain: str):
    """按域获取设备列表"""
    return store.get_states_by_domain(domain)

# ==================== 主入口 ====================

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("🏠 Home Assistant 测试 API 服务器 (JSON 持久化)")
    print("=" * 60)
    print(f"\n有效 Token: {', '.join(VALID_TOKENS)}")
    print(f"设备目录: {DEVICES_DIR}")
    print("\n访问地址:")
    print("  • API: http://localhost:8123/api/")
    print("  • 文档: http://localhost:8123/docs")
    print("=" * 60 + "\n")
    
    uvicorn.run("test_API_server.main:app", host="0.0.0.0", port=8123, reload=True)
