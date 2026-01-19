#!/usr/bin/env python3
"""清除设备表并重新同步设备（带正确的能力）"""

import asyncio
from sqlalchemy import text
from src.infrastructure.persistence.database import DatabaseConfig, init_database, get_current_session_factory

async def main():
    # 初始化数据库连接
    config = DatabaseConfig.postgresql(
        host="10.0.3.10",
        port=5432,
        user="user_s4DTX3",
        password="password_yrHKAp",
        database="user_s4DTX3"
    )
    
    await init_database(config)
    session_factory = get_current_session_factory()
    
    async with session_factory() as session:
        # 1. 清除所有设备
        print("正在清除 devices 表...")
        result = await session.execute(text("DELETE FROM devices"))
        await session.commit()
        print(f"已删除 {result.rowcount} 条设备记录")
        
    print("\n设备表已清空！请重启服务器以重新同步设备。")
    print("新同步的设备将自动根据 entity_id 前缀获取正确的能力。")

if __name__ == "__main__":
    asyncio.run(main())
