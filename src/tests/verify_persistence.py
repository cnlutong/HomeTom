import asyncio
import sys
import os
from datetime import datetime
import uuid

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.infrastructure.persistence.database import get_current_session_factory, create_all_tables, init_database
from src.infrastructure.persistence.repositories.scene_repository_impl import SceneRepositoryImpl
from src.infrastructure.persistence.repositories.device_repository_impl import DeviceRepositoryImpl
from src.infrastructure.persistence.repositories.executor_repository_impl import ExecutorRepositoryImpl
from src.infrastructure.persistence.repositories.execution_repository_impl import ExecutionRepositoryImpl
from src.domain.Execution.services.workflow_engine_impl import WorkflowEngine
from src.application.orchestration.OrchestrationService import OrchestrationService
from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
from src.domain.Scene.aggregates.scene_aggregate import SceneAggregate, SceneStatus
from src.domain.Scene.value_objects.scene_definition import SceneDefinition
from src.domain.Scene.value_objects.trigger import Trigger
from src.domain.Scene.value_objects.action import Action
from src.domain.Execution.aggregates.scene_executor import SceneExecutor
from src.infrastructure.persistence.database import get_current_session_factory, create_all_tables, init_database, DatabaseConfig
from src.domain.Execution.services.device_manager import IDeviceManager, CommandResult

# Mock DeviceManager
class MockDeviceManager(IDeviceManager):
    async def get_device(self, entity_id: str):
        return None
    async def execute_command(self, entity_id: str, command: str, params=None):
        return CommandResult.ok(entity_id, command, {"mock": True})
    async def get_device_state(self, entity_id: str):
        return "off"
    async def get_device_attributes(self, entity_id: str):
        return {}

async def verify_persistence():
    print("Starting persistence verification...")
    
    # Initialize DB (Use SQLite for testing)
    os.makedirs("./data", exist_ok=True)
    config = DatabaseConfig.sqlite(db_path="./data/test_persistence.db")
    await init_database(config)
    await create_all_tables()
    session_factory = get_current_session_factory()
    
    async with session_factory() as session:
        # Repositories
        scene_repo = SceneRepositoryImpl(session)
        device_repo = DeviceRepositoryImpl(session)
        executor_repo = ExecutorRepositoryImpl(session)
        execution_repo = ExecutionRepositoryImpl(session)
        
        # Services
        event_bus = InMemoryEventBus()
        device_manager = MockDeviceManager()
        workflow_engine = WorkflowEngine(device_manager, event_bus)
        orchestration_service = OrchestrationService(
            scene_repo,
            device_repo,
            execution_repo,
            executor_repo,
            workflow_engine,
            event_bus
        )
        
        # 1. Create a Scene
        print("Creating Scene...")
        scene_id = str(uuid.uuid4())
        scene = SceneAggregate(
            scene_id=scene_id,
            name="Test Persistence Scene",
            description="Testing executor stats persistence",
            status=SceneStatus.PUBLISHED, # Must be published to generate executor
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Add basic definition
        definition = SceneDefinition(
            triggers=[Trigger.create_manual()],
            actions=[
                Action.create_device_control("device_1", "turn_on")
            ]
        )
        scene.update_definition(definition)
        await scene_repo.save(scene)
        
        # 2. Create Executor (Simulating the Event Handler)
        print("Creating SceneExecutor...")
        executor = SceneExecutor.create(scene_id)
        executor.activate() # Make sure it's active
        await executor_repo.save(executor)
        
        # Commit to save scene and executor
        await session.commit()
        
        # 3. Trigger Execution
        print("Triggering execution...")
        try:
            execution_id = await orchestration_service.trigger_execution(scene_id)
            print(f"Execution triggered with ID: {execution_id}")
            
            # Commit to ensure execution is visible to next call (since autoflush=False)
            await session.commit()
            
            # Execute the scene workflow associated with the execution
            print("Executing workflow...")
            await orchestration_service.execute_scene(execution_id)
            
        except Exception as e:
            print(f"Execution failed: {e}")
            raise
            
        # Commit execution changes
        await session.commit()
        
        # 4. Verify Executor Stats
        print("Verifying Executor Stats...")
        # Re-fetch executor
        updated_executor = await executor_repo.find_by_scene_id(scene_id)
        
        if updated_executor.trigger_count == 1:
            print("SUCCESS: Trigger count incremented to 1")
        else:
            print(f"FAILURE: Trigger count is {updated_executor.trigger_count}, expected 1")
            
        if updated_executor.last_triggered_at is not None:
             print(f"SUCCESS: Last triggered at is set: {updated_executor.last_triggered_at}")
        else:
            print("FAILURE: Last triggered at is None")

        # 5. Verify Execution Logs
        print("Verifying Execution Logs...")
        execution = await execution_repo.find_by_id(execution_id)
        if execution:
            print(f"SUCCESS: Execution record found. Status: {execution.get_record().status.value}")
            # Check logs
            logs = execution.get_logs()
            if logs:
                 print(f"SUCCESS: {len(logs)} logs found.")
                 for log in logs:
                     print(f" - Log: {log.action_type} {log.command} success={log.success}")
            else:
                 print("WARNING: No logs found (might be expected if mock engine doesn't log)")
        else:
            print("FAILURE: Execution record not found")

if __name__ == "__main__":
    asyncio.run(verify_persistence())
