"""日志配置模块

提供统一的日志配置，基于 Python 标准库 logging 模块。
简单易用，输出到控制台，通过环境变量配置日志级别。
"""

import logging
import os
import sys
from typing import Optional


# 默认日志格式
DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    level: Optional[str] = None,
    format_string: Optional[str] = None,
    date_format: Optional[str] = None
) -> None:
    """初始化日志配置
    
    应在应用启动时调用此函数进行日志初始化。
    
    Args:
        level: 日志级别，可选值: DEBUG, INFO, WARNING, ERROR, CRITICAL
               默认从环境变量 LOG_LEVEL 读取，若未设置则为 INFO
        format_string: 日志格式字符串，默认为 DEFAULT_FORMAT
        date_format: 日期格式字符串，默认为 DEFAULT_DATE_FORMAT
    
    Example:
        >>> from src.infrastructure.config.logging_config import setup_logging
        >>> setup_logging()  # 使用默认配置
        >>> setup_logging(level="DEBUG")  # 设置为 DEBUG 级别
    """
    # 从环境变量获取日志级别，默认 INFO
    log_level_str = level or os.getenv("LOG_LEVEL", "INFO")
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    # 使用默认格式或自定义格式
    fmt = format_string or DEFAULT_FORMAT
    datefmt = date_format or DEFAULT_DATE_FORMAT
    
    # 配置根日志器
    logging.basicConfig(
        level=log_level,
        format=fmt,
        datefmt=datefmt,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True  # 强制重新配置，覆盖已有配置
    )
    
    # 设置第三方库的日志级别为 WARNING，避免过多噪音
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # 记录日志初始化完成
    logger = logging.getLogger(__name__)
    logger.info("日志系统初始化完成，级别: %s", log_level_str.upper())


def get_logger(name: str) -> logging.Logger:
    """获取日志器
    
    便捷方法，等同于 logging.getLogger(name)。
    推荐在模块中使用 logging.getLogger(__name__)。
    
    Args:
        name: 日志器名称，通常使用 __name__
        
    Returns:
        配置好的日志器实例
    """
    return logging.getLogger(name)
