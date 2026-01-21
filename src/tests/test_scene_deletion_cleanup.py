import asyncio
import sys
import os
from datetime import datetime
import uuid

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.infrastructure.persistence.database import get_current_session_factory, create_all_tables, init_database, DatabaseConfig
from src.infrastructure.persistence.repositories.scene_repository_impl import SceneRepositoryImpl
from src.infrastructure.persistence.repositories.device_repository_impl import DeviceRepositoryImpl
from src.infrastructure.persistence.repositories.executor_repository_impl import ExecutorRepositoryImpl
from src.infrastructure.persistence.repositories.execution_repository_impl import ExecutionRepositoryImpl
from src.application.scene.SceneService import SceneService
from src.application.handlers.scene_lifecycle_handler import SceneLifecycleHandler
from src.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
from src.domain.Scene.aggregates.scene_aggregate import SceneAggregate, SceneStatus
from src.domain.Scene.value_objects.scene_definition import SceneDefinition
from src.domain.Scene.value_objects.trigger import Trigger
from src.domain.Scene.value_objects.action import Action
from src.domain.Scene.services.scene_validator_impl import SceneValidator

async def test_scene_deletion_cleanup():
    print("Starting scene deletion cleanup verification...")
    
    # Initialize DB (Use SQLite for testing)
    os.makedirs("./data", exist_ok=True)
    config = DatabaseConfig.sqlite(db_path="./data/test_cleanup.db")
    await init_database(config)
    await create_all_tables()
    session_factory = get_current_session_factory()
    
    # 1. Setup Services
    event_bus = InMemoryEventBus()
    lifecycle_handler = SceneLifecycleHandler(session_factory)
    
    # Register events to lifecycle handler
    from src.domain.Scene.events.scene_created import SceneCreated
    from src.domain.Scene.events.scene_published import ScenePublished
    from src.domain.Scene.events.scene_deleted import SceneDeleted
    
    event_bus.subscribe(SceneCreated, lifecycle_handler.on_scene_created)
    event_bus.subscribe(ScenePublished, lifecycle_handler.on_scene_published)
    event_bus.subscribe(SceneDeleted, lifecycle_handler.on_scene_deleted)
    
    # Start the event bus
    await event_bus.start()
    
    async with session_factory() as session:
        scene_repo = SceneRepositoryImpl(session)
        device_repo = DeviceRepositoryImpl(session)
        executor_repo = ExecutorRepositoryImpl(session)
        execution_repo = ExecutionRepositoryImpl(session)
        
        validator = SceneValidator(device_repo)
        scene_service = SceneService(scene_repo, validator, event_bus)
        
        # 2. Create a Scene
        print("Creating Scene...")
        name = "Cleanup Test Scene"
        scene_id = await scene_service.create_scene(name=name)
        await session.commit()
        
        # Give events time to be processed
        await event_bus.wait_until_empty()
        
        # Verify executor created via event handler
        executor = await executor_repo.find_by_scene_id(scene_id)
        if executor:
            print(f"SUCCESS: Executor created for scene {scene_id}")
        else:
            print("FAILURE: Executor not created")
            await event_bus.stop()
            return

        # 3. Create an Execution Record
        print("Creating Execution Record...")
        from src.domain.Execution.aggregates.execution_aggregate import ExecutionAggregate
        from src.domain.Execution.value_objects.execution_context import ExecutionContext
        
        exec_id = str(uuid.uuid4())
        context = ExecutionContext(scene_id=scene_id, trigger_source="test_trigger")
        execution = ExecutionAggregate(exec_id, context)
        await execution_repo.save(execution)
        await session.commit()
        
        # Verify execution record exists
        executions = await execution_repo.find_by_scene_id(scene_id)
        if len(executions) > 0:
            print(f"SUCCESS: {len(executions)} execution record(s) created")
        else:
            print("FAILURE: Execution record not created")
            await event_bus.stop()
            return

        # 4. Delete the Scene
        print("Deleting Scene...")
        await scene_service.delete_scene(scene_id)
        await session.commit()
        
        # Wait for deletion event to be processed
        await event_bus.wait_until_empty()
        
        print("Scene deleted and events processed.")
        
        # 5. Verify Cleanup
        # Check scene is gone
        deleted_scene = await scene_repo.find_by_id(scene_id)
        if deleted_scene is None:
            print("SUCCESS: Scene record deleted")
        else:
            print("FAILURE: Scene record still exists")
            
        # Check executor is gone
        deleted_executor = await executor_repo.find_by_scene_id(scene_id)
        if deleted_executor is None:
            print("SUCCESS: Executor record cleaned up")
        else:
            print("FAILURE: Executor record still exists")
            
        # Check executions are gone
        remaining_executions = await execution_repo.find_by_scene_id(scene_id)
        if len(remaining_executions) == 0:
            print("SUCCESS: Execution history cleaned up")
        else:
            print(f"FAILURE: {len(remaining_executions)} execution records still exist")

    # Stop the event bus
    await event_bus.stop()

if __name__ == "__main__":
    asyncio.run(test_scene_deletion_cleanup())
