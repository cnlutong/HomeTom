"""
设备 API 路由
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from domain.entities.device import Device, DeviceState
from application.device_service import DeviceService
from exceptions import DeviceNotFoundError, HALCommunicationError


router = APIRouter(prefix="/api/devices", tags=["devices"])


# ========== 请求/响应模型 ==========

class DeviceCreateRequest(BaseModel):
    id: str
    name: str
    type: str
    config: Dict[str, Any] = None


class DeviceControlRequest(BaseModel):
    command: Dict[str, Any]


class DeviceResponse(BaseModel):
    id: str
    name: str
    type: str
    config: Dict[str, Any] = None
    created_at: str


class DeviceStateResponse(BaseModel):
    state: str
    attributes: Dict[str, Any]
    last_updated: str


# ========== 路由处理器 ==========

@router.get("", response_model=List[DeviceResponse])
async def get_devices(
    device_service: DeviceService = Depends()
):
    """获取所有设备"""
    try:
        devices = await device_service.get_all_devices()
        return [
            DeviceResponse(
                id=d.id,
                name=d.name,
                type=d.type,
                config=d.config,
                created_at=d.created_at.isoformat()
            )
            for d in devices
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    device_service: DeviceService = Depends()
):
    """获取设备详情"""
    try:
        device = await device_service.get_device(device_id)
        return DeviceResponse(
            id=device.id,
            name=device.name,
            type=device.type,
            config=device.config,
            created_at=device.created_at.isoformat()
        )
    except DeviceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device not found: {device_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{device_id}/state", response_model=DeviceStateResponse)
async def get_device_state(
    device_id: str,
    device_service: DeviceService = Depends()
):
    """获取设备状态"""
    try:
        state = await device_service.get_device_state(device_id)
        return DeviceStateResponse(
            state=state.state,
            attributes=state.attributes,
            last_updated=state.last_updated.isoformat()
        )
    except DeviceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device not found: {device_id}"
        )
    except HALCommunicationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{device_id}/control")
async def control_device(
    device_id: str,
    request: DeviceControlRequest,
    device_service: DeviceService = Depends()
):
    """控制设备"""
    try:
        success = await device_service.control_device(
            device_id,
            request.command
        )
        return {"success": success, "device_id": device_id}
    except DeviceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device not found: {device_id}"
        )
    except HALCommunicationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    request: DeviceCreateRequest,
    device_service: DeviceService = Depends()
):
    """添加设备"""
    try:
        device = Device(
            id=request.id,
            name=request.name,
            type=request.type,
            config=request.config
        )
        created = await device_service.add_device(device)
        return DeviceResponse(
            id=created.id,
            name=created.name,
            type=created.type,
            config=created.config,
            created_at=created.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{device_id}")
async def delete_device(
    device_id: str,
    device_service: DeviceService = Depends()
):
    """删除设备"""
    try:
        success = await device_service.remove_device(device_id)
        return {"success": success, "device_id": device_id}
    except DeviceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device not found: {device_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{device_id}/sync")
async def sync_device_state(
    device_id: str,
    device_service: DeviceService = Depends()
):
    """同步设备状态"""
    try:
        state = await device_service.sync_device_state(device_id)
        return DeviceStateResponse(
            state=state.state,
            attributes=state.attributes,
            last_updated=state.last_updated.isoformat()
        )
    except DeviceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device not found: {device_id}"
        )
    except HALCommunicationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

