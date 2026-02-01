"""应用配置管理

从根目录的 config.yaml 加载配置，提供类型安全的配置访问。
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class DatabaseSettings:
    """数据库配置"""
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = ""
    name: str = "hometom"
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False


@dataclass
class HomeAssistantSettings:
    """Home Assistant 配置"""
    base_url: str = "http://localhost:8123"
    token: str = ""


@dataclass
class AppSettings:
    """应用配置"""
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    homeassistant: HomeAssistantSettings = field(default_factory=HomeAssistantSettings)


def _find_config_file() -> Optional[Path]:
    """查找配置文件
    
    按以下顺序查找:
    1. 环境变量 CONFIG_PATH
    2. 项目根目录下的 config.yaml
    """
    # 优先使用环境变量
    env_path = os.environ.get("CONFIG_PATH")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path
    
    # 查找项目根目录下的 config.yaml
    # 从当前文件向上查找
    current = Path(__file__).resolve()
    for parent in current.parents:
        config_path = parent / "config.yaml"
        if config_path.exists():
            return config_path
    
    return None


def load_settings() -> AppSettings:
    """加载应用配置
    
    Returns:
        AppSettings 配置对象
        
    Raises:
        FileNotFoundError: 找不到配置文件时抛出
    """
    config_path = _find_config_file()
    
    if not config_path:
        raise FileNotFoundError(
            "找不到配置文件 config.yaml。"
            "请在项目根目录创建配置文件，或设置环境变量 CONFIG_PATH。"
        )
    
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    
    # 解析数据库配置
    db_data = config_data.get("database", {})
    database = DatabaseSettings(
        host=db_data.get("host", "localhost"),
        port=db_data.get("port", 5432),
        user=db_data.get("user", "postgres"),
        password=db_data.get("password", ""),
        name=db_data.get("name", "hometom"),
        pool_size=db_data.get("pool_size", 5),
        max_overflow=db_data.get("max_overflow", 10),
        echo=db_data.get("echo", False),
    )
    
    # 解析 Home Assistant 配置
    ha_data = config_data.get("homeassistant", {})
    homeassistant = HomeAssistantSettings(
        base_url=os.environ.get("HA_BASE_URL", ha_data.get("base_url", "http://localhost:8123")),
        token=os.environ.get("HA_TOKEN", ha_data.get("token", "")),
    )
    
    return AppSettings(database=database, homeassistant=homeassistant)


# 全局配置单例
_settings: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """获取全局配置
    
    首次调用时加载配置，后续调用返回缓存的配置。
    """
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings


def reload_settings() -> AppSettings:
    """重新加载配置
    
    强制重新读取配置文件。
    """
    global _settings
    _settings = load_settings()
    return _settings
