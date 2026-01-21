import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.infrastructure.persistence.database import init_database, DatabaseConfig, get_current_session_factory
from src.infrastructure.persistence.models.execution_model import ExecutionModel
from sqlalchemy import select

async def check_specific_executions():
    ids_to_check = [
        "fdc64c74-5199-4d0b-9813-15fe1d64d453",
        "cb934e89-8b4d-40e8-8e33-e240cae776a0",
        "34d5a445-8031-44e1-aedd-0569fac83fdb"
    ]
    
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
        for exec_id in ids_to_check:
            stmt = select(ExecutionModel).where(ExecutionModel.id == exec_id)
            result = await session.execute(stmt)
            exec_record = result.scalars().first()
            if exec_record:
                print(f"FOUND: {exec_id} | Status: {exec_record.status}")
            else:
                print(f"NOT FOUND: {exec_id}")

if __name__ == "__main__":
    asyncio.run(check_specific_executions())
