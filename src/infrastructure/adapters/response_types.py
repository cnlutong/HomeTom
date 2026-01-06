"""Home Assistant API 响应类型定义

定义 Home Assistant REST API 返回数据的类型化数据类。
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class HAStateObject:
    """Home Assistant 实体状态对象
    
    对应 GET /api/states/{entity_id} 返回的数据结构。
    """
    entity_id: str
    state: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    last_changed: Optional[str] = None
    last_updated: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HAStateObject":
        """从字典创建实例"""
        return cls(
            entity_id=data.get("entity_id", ""),
            state=data.get("state", ""),
            attributes=data.get("attributes", {}),
            last_changed=data.get("last_changed"),
            last_updated=data.get("last_updated"),
        )


@dataclass
class HAServiceDomain:
    """Home Assistant 服务域对象
    
    对应 GET /api/services 返回的单个域数据。
    """
    domain: str
    services: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HAServiceDomain":
        """从字典创建实例"""
        return cls(
            domain=data.get("domain", ""),
            services=list(data.get("services", {}).keys()) if isinstance(data.get("services"), dict) else data.get("services", []),
        )


@dataclass
class HAEventType:
    """Home Assistant 事件类型对象
    
    对应 GET /api/events 返回的单个事件数据。
    """
    event: str
    listener_count: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HAEventType":
        """从字典创建实例"""
        return cls(
            event=data.get("event", ""),
            listener_count=data.get("listener_count", 0),
        )


@dataclass  
class HAConfig:
    """Home Assistant 系统配置对象
    
    对应 GET /api/config 返回的数据结构。
    """
    components: List[str] = field(default_factory=list)
    config_dir: Optional[str] = None
    elevation: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    location_name: str = ""
    time_zone: str = ""
    version: str = ""
    unit_system: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HAConfig":
        """从字典创建实例"""
        return cls(
            components=data.get("components", []),
            config_dir=data.get("config_dir"),
            elevation=data.get("elevation", 0.0),
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
            location_name=data.get("location_name", ""),
            time_zone=data.get("time_zone", ""),
            version=data.get("version", ""),
            unit_system=data.get("unit_system", {}),
        )


@dataclass
class HAHistoryEntry:
    """Home Assistant 历史记录条目
    
    对应 GET /api/history/period 返回的单条历史数据。
    """
    entity_id: str
    state: str
    last_changed: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    last_updated: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HAHistoryEntry":
        """从字典创建实例"""
        return cls(
            entity_id=data.get("entity_id", ""),
            state=data.get("state", ""),
            last_changed=data.get("last_changed", ""),
            attributes=data.get("attributes", {}),
            last_updated=data.get("last_updated"),
        )


@dataclass
class HALogbookEntry:
    """Home Assistant 日志条目
    
    对应 GET /api/logbook 返回的单条日志数据。
    """
    name: str
    message: str
    entity_id: str
    domain: str
    when: str
    context_user_id: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HALogbookEntry":
        """从字典创建实例"""
        return cls(
            name=data.get("name", ""),
            message=data.get("message", ""),
            entity_id=data.get("entity_id", ""),
            domain=data.get("domain", ""),
            when=data.get("when", ""),
            context_user_id=data.get("context_user_id"),
        )
