import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import device_router, scene_router, execution_router, device_log_router

app = FastAPI(title="HomeTom API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:5178",
        "http://localhost:5179",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:5177",
        "http://127.0.0.1:5178",
        "http://127.0.0.1:5179",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(device_router.router)
app.include_router(scene_router.router)
app.include_router(execution_router.router)
app.include_router(device_log_router.router)


@app.on_event("startup")
async def startup_event():
    """应用启动事件处理
    
    使用 SystemBootstrap 执行分阶段初始化:
    1. 基础设施: 数据库、事件总线、调度器
    2. 依赖注入: 硬件客户端、工作流引擎、事件处理器
    3. 数据恢复: 设备同步、场景种子数据
    4. 运行时设置: 执行器同步、调度器任务加载
    5. 触发就绪: always_on 场景触发、健康检查
    """
    import logging
    from src.application.bootstrap import SystemBootstrap
    
    logger = logging.getLogger(__name__)
    
    bootstrap = SystemBootstrap()
    result = await bootstrap.initialize()
    
    if not result.success:
        logger.error("=" * 60)
        logger.error("SYSTEM INITIALIZATION FAILED")
        for error in result.errors:
            logger.error(f"  - {error}")
        logger.error("=" * 60)
        # 可选: 在严重错误时终止启动
        # raise RuntimeError("System initialization failed")
    
    # 存储依赖容器供路由使用
    app.state.container = result.container
    app.state.event_bus = result.container.event_bus
    app.state.scheduler = result.container.scheduler
    
    # 记录警告信息
    if result.warnings:
        logger.warning("Initialization completed with warnings:")
        for warning in result.warnings:
            logger.warning(f"  - {warning}")


@app.get("/")
async def root():
    return {"message": "Welcome to HomeTom API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

