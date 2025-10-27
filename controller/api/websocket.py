"""
WebSocket 处理器
提供实时状态推送
"""
from typing import List, Set
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket):
        """接受新连接"""
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        print(f"✓ WebSocket 连接建立，当前连接数: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """断开连接"""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        print(f"✓ WebSocket 连接断开，当前连接数: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"⚠ 发送消息失败: {e}")
            await self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """广播消息给所有连接"""
        async with self._lock:
            disconnected = []
            
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"⚠ 广播失败: {e}")
                    disconnected.append(connection)
            
            # 移除失败的连接
            for conn in disconnected:
                if conn in self.active_connections:
                    self.active_connections.remove(conn)
    
    def get_connection_count(self) -> int:
        """获取当前连接数"""
        return len(self.active_connections)


# 全局连接管理器实例
connection_manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 端点处理器
    
    消息格式：
    {
        "type": "device_state_changed" | "scene_triggered" | "scene_completed",
        "data": {...}
    }
    """
    await connection_manager.connect(websocket)
    
    try:
        while True:
            # 接收客户端消息（心跳检测）
            data = await websocket.receive_text()
            
            # 回复心跳
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket)
    except Exception as e:
        print(f"⚠ WebSocket 错误: {e}")
        await connection_manager.disconnect(websocket)


def setup_websocket_events(event_bus):
    """
    设置 WebSocket 事件订阅
    将事件总线的事件推送到 WebSocket 客户端
    """
    from application.event_bus import EventTypes
    
    async def on_device_state_changed(data: dict):
        """设备状态变更事件"""
        await connection_manager.broadcast({
            "type": EventTypes.DEVICE_STATE_CHANGED,
            "data": data
        })
    
    async def on_scene_triggered(data: dict):
        """场景触发事件"""
        await connection_manager.broadcast({
            "type": EventTypes.SCENE_TRIGGERED,
            "data": data
        })
    
    async def on_scene_completed(data: dict):
        """场景完成事件"""
        await connection_manager.broadcast({
            "type": EventTypes.SCENE_COMPLETED,
            "data": data
        })
    
    async def on_scene_failed(data: dict):
        """场景失败事件"""
        await connection_manager.broadcast({
            "type": EventTypes.SCENE_FAILED,
            "data": data
        })
    
    # 订阅事件
    event_bus.subscribe(EventTypes.DEVICE_STATE_CHANGED, on_device_state_changed)
    event_bus.subscribe(EventTypes.SCENE_TRIGGERED, on_scene_triggered)
    event_bus.subscribe(EventTypes.SCENE_COMPLETED, on_scene_completed)
    event_bus.subscribe(EventTypes.SCENE_FAILED, on_scene_failed)
    
    print("✓ WebSocket 事件订阅已设置")

