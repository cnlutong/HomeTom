"""数据库配置与会话管理

提供异步数据库引擎创建和会话工厂，支持 SQLite 和 PostgreSQL
"""

from dataclasses import dataclass, field
from typing import Optional
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine as sa_create_async_engine,
)


@dataclass
class DatabaseConfig:
    """数据库配置
    
    Attributes:
        url: 数据库连接 URL
            - SQLite: sqlite+aiosqlite:///./data/hometom.db
            - PostgreSQL: postgresql+asyncpg://user:pass@localhost/hometom
        echo: 是否打印 SQL 语句（调试用）
        pool_size: 连接池大小（仅 PostgreSQL 有效）
        max_overflow: 连接池最大溢出数（仅 PostgreSQL 有效）
    """
    url: str
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    
    @classmethod
    def sqlite(cls, db_path: str = "./data/hometom.db", echo: bool = False) -> "DatabaseConfig":
        """创建 SQLite 配置（开发环境）"""
        return cls(url=f"sqlite+aiosqlite:///{db_path}", echo=echo)
    
    @classmethod
    def postgresql(
        cls,
        host: str = "localhost",
        port: int = 5432,
        database: str = "hometom",
        user: str = "postgres",
        password: str = "",
        echo: bool = False,
    ) -> "DatabaseConfig":
        """创建 PostgreSQL 配置（生产环境）"""
        url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
        return cls(url=url, echo=echo)


def create_async_engine(config: DatabaseConfig) -> AsyncEngine:
    """创建异步数据库引擎
    
    Args:
        config: 数据库配置
        
    Returns:
        异步数据库引擎
    """
    # SQLite 不支持连接池参数
    is_sqlite = config.url.startswith("sqlite")
    
    engine_kwargs = {
        "echo": config.echo,
    }
    
    if not is_sqlite:
        engine_kwargs.update({
            "pool_size": config.pool_size,
            "max_overflow": config.max_overflow,
        })
    
    return sa_create_async_engine(config.url, **engine_kwargs)


def get_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """获取异步会话工厂
    
    Args:
        engine: 异步数据库引擎
        
    Returns:
        异步会话工厂
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,  # 防止提交后访问属性时触发隐式查询
        autoflush=False,
    )


# 全局引擎和会话工厂（由应用启动时初始化）
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


async def init_database(config: Optional[DatabaseConfig] = None) -> None:
    """初始化数据库连接
    
    应在应用启动时调用。如果未提供 config，则默认使用 SQLite。
    """
    global _engine, _session_factory
    if config is None:
        config = DatabaseConfig.sqlite()
    _engine = create_async_engine(config)
    _session_factory = get_session_factory(_engine)


def get_current_session_factory() -> async_sessionmaker[AsyncSession]:
    """导出全局会话工厂"""
    if _session_factory is None:
        raise RuntimeError("数据库未初始化，请先调用 init_database()")
    return _session_factory


async def close_database() -> None:
    """关闭数据库连接
    
    应在应用关闭时调用
    """
    global _engine, _session_factory
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None


async def create_all_tables() -> None:
    """创建所有数据库表
    
    MVP 阶段使用此函数快速建表，无需 Alembic 迁移。
    应在 init_database() 之后调用。
    
    Raises:
        RuntimeError: 如果数据库未初始化
    """
    if _engine is None:
        raise RuntimeError("数据库未初始化，请先调用 init_database()")
    
    from .models import Base
    from sqlalchemy import text
    
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # 手动添加缺失的列（MVP 阶段简单迁移）
        # 检查并添加 execution_flow 列到 scene_executors 表
        try:
            await conn.execute(text(
                "ALTER TABLE scene_executors ADD COLUMN IF NOT EXISTS execution_flow TEXT"
            ))
            print("Migration: execution_flow column added or already exists.")
        except Exception as e:
            # 如果是 SQLite 或其他不支持 ADD COLUMN IF NOT EXISTS 的数据库，忽略错误
            print(f"Migration note: {e}")



def get_session() -> AsyncSession:
    """获取数据库会话
    
    Returns:
        新的异步数据库会话
        
    Raises:
        RuntimeError: 如果数据库未初始化
    """
    if _session_factory is None:
        raise RuntimeError("数据库未初始化，请先调用 init_database()")
    return _session_factory()
