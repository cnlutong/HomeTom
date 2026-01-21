import asyncio
import sys
import os
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.infrastructure.persistence.database import init_database, DatabaseConfig, get_current_session_factory
from src.infrastructure.persistence.models.scene_model import SceneModel
from sqlalchemy import select

async def check_scene_definition():
    scene_id = "670aff49-9907-4356-8f15-846978584791"
    
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
        stmt = select(SceneModel).where(SceneModel.id == scene_id)
        result = await session.execute(stmt)
        scene = result.scalars().first()
        
        if scene:
            print(f"Name: {scene.name}")
            print(f"Status: {scene.status}")
            print(f"Definition: {scene.definition}")
        else:
            print("Scene NOT FOUND")

if __name__ == "__main__":
    asyncio.run(check_scene_definition())
