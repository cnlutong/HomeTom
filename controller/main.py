"""
HomeTom 控制器主入口
FastAPI 应用程序
"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from exceptions import ControllerException

# 导入路由
from api.routes import devices, scenes, system
from api.websocket import websocket_endpoint, setup_websocket_events

# 导入依赖
from dependencies import (
    get_hal_client,
    get_state_manager,
    get_event_bus,
    get_scene_scheduler,
    startup_handler,
    shutdown_handler
)


# ========== 生命周期管理 ==========

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("\n" + "="*50)
    print("🚀 HomeTom 控制器启动中...")
    print("="*50)
    
    await startup_handler()
    
    yield
    
    # 关闭时
    print("\n" + "="*50)
    print("🛑 HomeTom 控制器关闭中...")
    print("="*50)
    
    await shutdown_handler()


# ========== FastAPI 应用 ==========

app = FastAPI(
    title="HomeTom Controller",
    description="智能家居控制器 API",
    version="1.0.0",
    lifespan=lifespan
)


# ========== 中间件配置 ==========

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 统一错误处理（优化建议 #11）==========

@app.exception_handler(ControllerException)
async def controller_exception_handler(request, exc: ControllerException):
    """控制器异常处理器"""
    return JSONResponse(
        status_code=500,
        content={"error": exc.message, "type": exc.__class__.__name__}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """通用异常处理器"""
    print(f"⚠ 未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# ========== 路由注册 ==========

app.include_router(devices.router)
app.include_router(scenes.router)
app.include_router(system.router)


# ========== WebSocket 路由 ==========

@app.websocket("/ws")
async def websocket_route(websocket):
    """WebSocket 端点"""
    await websocket_endpoint(websocket)


# ========== 根路径 ==========

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "HomeTom Controller",
        "version": "1.0.0",
        "status": "running"
    }


# ========== 主函数 ==========

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式
        log_level=config.LOG_LEVEL.lower()
    )

