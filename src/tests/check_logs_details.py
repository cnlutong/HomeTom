import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.infrastructure.persistence.database import init_database, DatabaseConfig, get_current_session_factory
from src.infrastructure.persistence.models.execution_model import ExecutionModel
from sqlalchemy import select

async def check_logs_and_details():
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
        stmt = select(ExecutionModel).order_by(ExecutionModel.started_at.desc()).limit(10)
        result = await session.execute(stmt)
        executions = result.scalars().all()
        
        print(f"Recent Executions:")
        for e in executions:
            # Note: logs relationship is lazy loaded, but in model it says lazy='selectin'
            num_logs = len(e.logs)
            print(f"ID: {e.id} | Scene: {e.scene_id} | Status: {e.status} | Logs: {num_logs}")
            if num_logs > 0:
                print(f"  First Log step: {e.logs[0].step_number} {e.logs[0].command}")

if __name__ == "__main__":
    asyncio.run(check_logs_and_details())
