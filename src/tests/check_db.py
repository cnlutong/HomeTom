import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.infrastructure.persistence.database import DatabaseConfig, init_database, get_current_session_factory

async def check_db():
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
        from sqlalchemy import text
        
        print("--- scene_executors ---")
        result = await session.execute(text("SELECT * FROM scene_executors"))
        rows = result.fetchall()
        for row in rows:
            print(row)
        if not rows:
            print("(no rows)")
            
        print("\n--- scenes (last 3) ---")
        result = await session.execute(text("SELECT id, name, status FROM scenes ORDER BY created_at DESC LIMIT 3"))
        rows = result.fetchall()
        for row in rows:
            print(row)

if __name__ == "__main__":
    asyncio.run(check_db())
