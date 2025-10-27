"""
场景 API 路由
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from domain.entities.scene import Scene
from application.scene_service import SceneService
from exceptions import SceneNotFoundError, SceneDefinitionError


router = APIRouter(prefix="/api/scenes", tags=["scenes"])


# ========== 请求/响应模型 ==========

class SceneCreateRequest(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    definition: Dict[str, Any]
    is_active: bool = True


class SceneUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class SceneActivateRequest(BaseModel):
    is_active: bool


class SceneResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    definition: Dict[str, Any]
    is_active: bool
    created_at: str


# ========== 路由处理器 ==========

@router.get("", response_model=List[SceneResponse])
async def get_scenes(
    active_only: bool = False,
    scene_service: SceneService = Depends()
):
    """获取所有场景"""
    try:
        scenes = await scene_service.get_all_scenes(active_only=active_only)
        return [
            SceneResponse(
                id=s.id,
                name=s.name,
                description=s.description,
                definition=s.definition.model_dump(),
                is_active=s.is_active,
                created_at=s.created_at.isoformat()
            )
            for s in scenes
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{scene_id}", response_model=SceneResponse)
async def get_scene(
    scene_id: str,
    scene_service: SceneService = Depends()
):
    """获取场景详情"""
    try:
        scene = await scene_service.get_scene(scene_id)
        return SceneResponse(
            id=scene.id,
            name=scene.name,
            description=scene.description,
            definition=scene.definition.model_dump(),
            is_active=scene.is_active,
            created_at=scene.created_at.isoformat()
        )
    except SceneNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scene not found: {scene_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=SceneResponse, status_code=status.HTTP_201_CREATED)
async def create_scene(
    request: SceneCreateRequest,
    scene_service: SceneService = Depends()
):
    """创建场景"""
    try:
        scene_data = {
            "id": request.id,
            "name": request.name,
            "description": request.description,
            "definition": request.definition,
            "is_active": request.is_active
        }
        scene = await scene_service.create_scene(scene_data)
        return SceneResponse(
            id=scene.id,
            name=scene.name,
            description=scene.description,
            definition=scene.definition.model_dump(),
            is_active=scene.is_active,
            created_at=scene.created_at.isoformat()
        )
    except SceneDefinitionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{scene_id}", response_model=SceneResponse)
async def update_scene(
    scene_id: str,
    request: SceneUpdateRequest,
    scene_service: SceneService = Depends()
):
    """更新场景"""
    try:
        # 获取现有场景
        existing = await scene_service.get_scene(scene_id)
        
        # 构建更新数据
        scene_data = {
            "name": request.name if request.name else existing.name,
            "description": request.description if request.description is not None else existing.description,
            "definition": request.definition if request.definition else existing.definition.model_dump(),
            "is_active": request.is_active if request.is_active is not None else existing.is_active
        }
        
        scene = await scene_service.update_scene(scene_id, scene_data)
        return SceneResponse(
            id=scene.id,
            name=scene.name,
            description=scene.description,
            definition=scene.definition.model_dump(),
            is_active=scene.is_active,
            created_at=scene.created_at.isoformat()
        )
    except SceneNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scene not found: {scene_id}"
        )
    except SceneDefinitionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{scene_id}")
async def delete_scene(
    scene_id: str,
    scene_service: SceneService = Depends()
):
    """删除场景"""
    try:
        success = await scene_service.delete_scene(scene_id)
        return {"success": success, "scene_id": scene_id}
    except SceneNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scene not found: {scene_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{scene_id}/trigger")
async def trigger_scene(
    scene_id: str,
    scene_service: SceneService = Depends()
):
    """手动触发场景"""
    try:
        result = await scene_service.trigger_scene(scene_id, triggered_by="manual")
        return result
    except SceneNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scene not found: {scene_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{scene_id}/activate", response_model=SceneResponse)
async def activate_scene(
    scene_id: str,
    request: SceneActivateRequest,
    scene_service: SceneService = Depends()
):
    """激活/停用场景"""
    try:
        scene = await scene_service.activate_scene(scene_id, request.is_active)
        return SceneResponse(
            id=scene.id,
            name=scene.name,
            description=scene.description,
            definition=scene.definition.model_dump(),
            is_active=scene.is_active,
            created_at=scene.created_at.isoformat()
        )
    except SceneNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scene not found: {scene_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

