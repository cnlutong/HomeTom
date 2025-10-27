"""
仓储模式实现
提供数据访问抽象层
"""
import json
from typing import List, Optional
import aiosqlite

from domain.entities.device import Device
from domain.entities.scene import Scene
from exceptions import DatabaseError


class DeviceRepository:
    """设备仓储"""
    
    def __init__(self, db: aiosqlite.Connection):
        self.db = db
    
    async def get_all(self) -> List[Device]:
        """获取所有设备"""
        try:
            async with self.db.execute("SELECT * FROM devices") as cursor:
                rows = await cursor.fetchall()
                return [Device.from_db_row(dict(row)) for row in rows]
        except Exception as e:
            raise DatabaseError(f"Failed to get all devices: {e}")
    
    async def get_by_id(self, device_id: str) -> Optional[Device]:
        """根据 ID 获取设备"""
        try:
            async with self.db.execute(
                "SELECT * FROM devices WHERE id = ?", (device_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return Device.from_db_row(dict(row)) if row else None
        except Exception as e:
            raise DatabaseError(f"Failed to get device {device_id}: {e}")
    
    async def save(self, device: Device) -> None:
        """保存设备（插入或更新）"""
        try:
            await self.db.execute(
                """
                INSERT INTO devices (id, name, type, config, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    type = excluded.type,
                    config = excluded.config
                """,
                (
                    device.id,
                    device.name,
                    device.type,
                    json.dumps(device.config) if device.config else None,
                    device.created_at,
                ),
            )
            await self.db.commit()
        except Exception as e:
            raise DatabaseError(f"Failed to save device {device.id}: {e}")
    
    async def delete(self, device_id: str) -> bool:
        """删除设备"""
        try:
            cursor = await self.db.execute(
                "DELETE FROM devices WHERE id = ?", (device_id,)
            )
            await self.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            raise DatabaseError(f"Failed to delete device {device_id}: {e}")


class SceneRepository:
    """场景仓储"""
    
    def __init__(self, db: aiosqlite.Connection):
        self.db = db
    
    async def get_all(self, active_only: bool = False) -> List[Scene]:
        """
        获取所有场景
        
        Args:
            active_only: 是否只获取激活的场景
        """
        try:
            query = "SELECT * FROM scenes"
            if active_only:
                query += " WHERE is_active = 1"
            
            async with self.db.execute(query) as cursor:
                rows = await cursor.fetchall()
                return [Scene.from_db_row(dict(row)) for row in rows]
        except Exception as e:
            raise DatabaseError(f"Failed to get scenes: {e}")
    
    async def get_by_id(self, scene_id: str) -> Optional[Scene]:
        """根据 ID 获取场景"""
        try:
            async with self.db.execute(
                "SELECT * FROM scenes WHERE id = ?", (scene_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return Scene.from_db_row(dict(row)) if row else None
        except Exception as e:
            raise DatabaseError(f"Failed to get scene {scene_id}: {e}")
    
    async def save(self, scene: Scene) -> None:
        """保存场景（插入或更新）"""
        try:
            await self.db.execute(
                """
                INSERT INTO scenes (id, name, description, definition, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    description = excluded.description,
                    definition = excluded.definition,
                    is_active = excluded.is_active
                """,
                (
                    scene.id,
                    scene.name,
                    scene.description,
                    scene.definition.model_dump_json(),
                    scene.is_active,
                    scene.created_at,
                ),
            )
            await self.db.commit()
        except Exception as e:
            raise DatabaseError(f"Failed to save scene {scene.id}: {e}")
    
    async def delete(self, scene_id: str) -> bool:
        """删除场景"""
        try:
            cursor = await self.db.execute(
                "DELETE FROM scenes WHERE id = ?", (scene_id,)
            )
            await self.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            raise DatabaseError(f"Failed to delete scene {scene_id}: {e}")
    
    async def update_active_status(self, scene_id: str, is_active: bool) -> None:
        """更新场景激活状态"""
        try:
            await self.db.execute(
                "UPDATE scenes SET is_active = ? WHERE id = ?",
                (is_active, scene_id),
            )
            await self.db.commit()
        except Exception as e:
            raise DatabaseError(f"Failed to update scene status {scene_id}: {e}")

