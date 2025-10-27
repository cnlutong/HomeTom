"""
配置管理模块（优化版）
使用 Pydantic Settings 进行配置管理
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""
    
    # HAL 配置
    HAL_ENDPOINT: str = "http://localhost:8080"
    HAL_TIMEOUT: int = 5
    HAL_MAX_CONNECTIONS: int = 10
    HAL_MAX_KEEPALIVE: int = 5
    HAL_RETRY_TIMES: int = 2
    
    # 数据库配置
    DATABASE_PATH: str = "./data/controller.db"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/controller.log"
    
    # WebSocket 配置
    WS_PING_INTERVAL: int = 30
    
    # 测试模式（用于依赖注入优化）
    TESTING: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# 全局配置实例
config = Settings()

