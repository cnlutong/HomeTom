import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.infrastructure.persistence.database import init_database, DatabaseConfig, get_current_session_factory
from src.infrastructure.persistence.models.scene_model import SceneModel
from sqlalchemy import select

async def check_scenes():
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
        stmt = select(SceneModel)
        result = await session.execute(stmt)
        scenes = result.scalars().all()
        
        print(f"Total scenes found: {len(scenes)}")
        for scene in scenes:
            print(f"ID: {scene.id}, Name: {scene.name}, Status: {scene.status}")

if __name__ == "__main__":
    asyncio.run(check_scenes())
