"""基础设施层 - 提供技术实现，如持久化、消息传递、外部服务适配"""

from .config import setup_logging, get_logger

__all__ = ["setup_logging", "get_logger"]
