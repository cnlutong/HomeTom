import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.infrastructure.persistence.database import init_database, DatabaseConfig, get_current_session_factory
from src.infrastructure.persistence.models.scene_model import SceneModel
from sqlalchemy import select

async def check_all_scenes():
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
        
        for scene in scenes:
            print(f"--- Scene: {scene.name} ({scene.id}) ---")
            print(f"Status: {scene.status}")
            print(f"Triggers: {len(scene.definition.get('triggers', [])) if scene.definition else 0}")
            print(f"Conditions: {len(scene.definition.get('conditions', [])) if scene.definition else 0}")
            print(f"Actions: {len(scene.definition.get('actions', [])) if scene.definition else 0}")
            if scene.definition and scene.definition.get('conditions'):
                print(f"Conditions Data: {scene.definition['conditions']}")

if __name__ == "__main__":
    asyncio.run(check_all_scenes())
