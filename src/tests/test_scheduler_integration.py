
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.application.orchestration.OrchestrationService import OrchestrationService
from src.domain.Execution.aggregates.scene_executor import SceneExecutor, ExecutorStatus
from src.domain.Scene.aggregates.scene_aggregate import SceneAggregate

@pytest.fixture
def mock_scheduler():
    return MagicMock(spec=AsyncIOScheduler)

@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.find_all = AsyncMock(return_value=[])
    return repo

@pytest.fixture
def service(mock_repo, mock_scheduler):
    return OrchestrationService(
        scene_repository=None,
        device_repository=None,
        execution_repository=None,
        executor_repository=mock_repo,
        workflow_engine=None,
        event_bus=None,
        scheduler=mock_scheduler
    )

def test_register_executor_timer(service, mock_scheduler):
    # Setup executor with timer trigger
    executor = SceneExecutor(
        executor_id="exec-1", 
        scene_id="scene-1", 
        status=ExecutorStatus.ACTIVE,
        created_at=None, updated_at=None,
        execution_flow={
            "triggers": [
                {
                    "type": "timer",
                    "config": {"schedule": "* * * * *"}
                }
            ]
        }
    )
    
    # Call register
    service.register_executor(executor)
    
    # Verify add_job called
    mock_scheduler.add_job.assert_called_once()
    args, kwargs = mock_scheduler.add_job.call_args
    assert kwargs['id'] == "scene_scene-1_timer"
    # check trigger type
    assert isinstance(args[1], CronTrigger)

def test_register_executor_inactive(service, mock_scheduler):
    # Setup inactive executor
    executor = SceneExecutor(
        executor_id="exec-1", 
        scene_id="scene-1", 
        status=ExecutorStatus.STOPPED,
        created_at=None, updated_at=None,
        execution_flow={
            "triggers": [{"type": "timer", "config": {"schedule": "* * * * *"}}]
        }
    )
    
    # Call register
    service.register_executor(executor)
    
    # Verify add_job NOT called
    mock_scheduler.add_job.assert_not_called()

def test_unregister_executor(service, mock_scheduler):
    # Setup internal state
    service._execution_jobs["scene-1"] = ["job-1"]
    
    # Call unregister
    service.unregister_executor("scene-1")
    
    # Verify remove_job called
    mock_scheduler.remove_job.assert_called_with("job-1")
    assert "scene-1" not in service._execution_jobs

@pytest.mark.asyncio
async def test_load_active_executors(service, mock_repo, mock_scheduler):
    # Setup repo to return one active executor
    executor = SceneExecutor(
        executor_id="exec-1", 
        scene_id="scene-1", 
        status=ExecutorStatus.ACTIVE, 
        created_at=None, updated_at=None,
        execution_flow={"triggers": [{"type": "timer", "config": {"schedule": "* * * * *"}}]}
    )
    mock_repo.find_all.return_value = [executor]
    
    # Call load
    await service.load_active_executors()
    
    # Verify register called (via add_job)
    mock_scheduler.add_job.assert_called_once()
