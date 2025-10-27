"""
数据库连接管理模块
使用 aiosqlite 实现异步 SQLite 操作
"""
import aiosqlite
import os
from typing import AsyncGenerator
from pathlib import Path

from config import config
from exceptions import DatabaseError


async def get_db_connection() -> AsyncGenerator[aiosqlite.Connection, None]:
    """
    获取数据库连接（依赖注入使用）
    
    Yields:
        aiosqlite.Connection: 数据库连接
    """
    db_path = Path(config.DATABASE_PATH)
    
    # 确保数据目录存在
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        async with aiosqlite.connect(db_path) as db:
            # 启用外键约束
            await db.execute("PRAGMA foreign_keys = ON")
            # 设置行工厂，返回字典形式的行
            db.row_factory = aiosqlite.Row
            yield db
    except Exception as e:
        raise DatabaseError(f"Failed to connect to database: {e}")


async def init_database() -> None:
    """
    初始化数据库
    创建表结构
    """
    schema_path = Path(__file__).parent / "schema.sql"
    
    try:
        # 读取 SQL 模式文件
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        
        # 执行建表语句
        async with aiosqlite.connect(config.DATABASE_PATH) as db:
            await db.executescript(schema_sql)
            await db.commit()
            
        print(f"✓ 数据库初始化成功: {config.DATABASE_PATH}")
        
    except FileNotFoundError:
        raise DatabaseError(f"Schema file not found: {schema_path}")
    except Exception as e:
        raise DatabaseError(f"Failed to initialize database: {e}")

