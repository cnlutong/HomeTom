"""场景仓储接口模块"""

from .scene_repository import ISceneRepository
from .scene_version_repository import ISceneVersionRepository

__all__ = [
    'ISceneRepository',
    'ISceneVersionRepository',
]

