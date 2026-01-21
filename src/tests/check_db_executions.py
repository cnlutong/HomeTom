import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.infrastructure.persistence.database import init_database, DatabaseConfig, get_current_session_factory
from src.infrastructure.persistence.models.execution_model import ExecutionModel
from sqlalchemy import select

async def check_executions():
    # Use the same PostgreSQL config as in main.py
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
        stmt = select(ExecutionModel)
        result = await session.execute(stmt)
        executions = result.scalars().all()
        
        print(f"Total execution records found: {len(executions)}")
        for i, exec_record in enumerate(executions):
            print(f"{i+1}. ID: {exec_record.id}, Scene: {exec_record.scene_id}, Status: {exec_record.status}, Started: {exec_record.started_at}")

if __name__ == "__main__":
    asyncio.run(check_executions())
