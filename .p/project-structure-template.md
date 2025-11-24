# 项目结构模板

## 完整目录结构

```
HomeTom/
├── .env                    # 环境变量配置
├── .env.example            # 环境变量示例
├── .gitignore
├── README.md
├── pyproject.toml          # 或 requirements.txt
├── alembic.ini             # Alembic配置
├── main.py                 # 应用入口
│
├── src/
│   ├── __init__.py
│   │
│   ├── interface/          # 接口层（洋葱架构最外层）
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── device_controller.py
│   │   │   ├── scene_controller.py
│   │   │   └── execution_controller.py
│   │   ├── dto/
│   │   │   ├── __init__.py
│   │   │   ├── device_dto.py
│   │   │   ├── scene_dto.py
│   │   │   └── execution_dto.py
│   │   └── exceptions.py   # HTTP异常处理
│   │
│   ├── application/        # 应用层
│   │   ├── __init__.py
│   │   ├── device_app_service.py
│   │   ├── scene_app_service.py
│   │   └── orchestration_app_service.py
│   │
│   ├── domain/             # 领域层（洋葱架构核心）
│   │   ├── __init__.py
│   │   │
│   │   ├── Device/         # 设备管理上下文
│   │   │   ├── __init__.py
│   │   │   ├── aggregates/
│   │   │   │   ├── __init__.py
│   │   │   │   └── device_aggregate.py
│   │   │   ├── entities/
│   │   │   │   └── __init__.py
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── device_capability.py
│   │   │   │   └── device_status.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   └── device_service.py
│   │   │   ├── events/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── device_registered.py
│   │   │   │   └── device_status_changed.py
│   │   │   ├── repositories/
│   │   │   │   ├── __init__.py
│   │   │   │   └── device_repository.py  # 接口定义
│   │   │   └── exceptions.py
│   │   │
│   │   ├── Scene/          # 场景设计上下文
│   │   │   ├── __init__.py
│   │   │   ├── aggregates/
│   │   │   │   ├── __init__.py
│   │   │   │   └── scene_aggregate.py
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   └── scene_version.py
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── trigger.py
│   │   │   │   ├── condition.py
│   │   │   │   ├── action.py
│   │   │   │   └── scene_definition.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── scene_validator.py
│   │   │   │   └── scene_state_machine.py
│   │   │   ├── events/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── scene_published.py
│   │   │   │   └── scene_disabled.py
│   │   │   ├── repositories/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── scene_repository.py
│   │   │   │   └── scene_version_repository.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── Execution/       # 场景执行上下文
│   │   │   ├── __init__.py
│   │   │   ├── aggregates/
│   │   │   │   ├── __init__.py
│   │   │   │   └── execution_aggregate.py
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── execution_record.py
│   │   │   │   └── execution_log.py
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── execution_context.py
│   │   │   │   ├── execution_result.py
│   │   │   │   └── retry_policy.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── workflow_engine.py
│   │   │   │   └── concurrency_coordinator.py
│   │   │   ├── events/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── execution_started.py
│   │   │   │   ├── execution_succeeded.py
│   │   │   │   └── execution_failed.py
│   │   │   ├── repositories/
│   │   │   │   ├── __init__.py
│   │   │   │   └── execution_repository.py
│   │   │   └── exceptions.py
│   │   │
│   │   └── shared/         # 共享内核（如需要）
│   │       ├── __init__.py
│   │       └── value_objects/
│   │
│   └── infrastructure/     # 基础设施层（洋葱架构最外层）
│       ├── __init__.py
│       │
│       ├── persistence/    # 持久化实现
│       │   ├── __init__.py
│       │   ├── database.py         # 数据库连接
│       │   ├── models/              # SQLAlchemy模型
│       │   │   ├── __init__.py
│       │   │   ├── device_model.py
│       │   │   ├── device_state_model.py
│       │   │   ├── scene_model.py
│       │   │   ├── scene_version_model.py
│       │   │   ├── scene_dependency_model.py
│       │   │   ├── execution_model.py
│       │   │   └── execution_log_model.py
│       │   └── repositories/       # 仓储实现
│       │       ├── __init__.py
│       │       ├── device_repository_impl.py
│       │       ├── scene_repository_impl.py
│       │       ├── scene_version_repository_impl.py
│       │       └── execution_repository_impl.py
│       │
│       ├── adapters/       # 设备适配器
│       │   ├── __init__.py
│       │   ├── device_adapter.py   # 接口定义
│       │   ├── http_device_adapter.py
│       │   └── factory.py          # 适配器工厂
│       │
│       ├── messaging/      # 消息/事件
│       │   ├── __init__.py
│       │   ├── event_bus.py        # 接口定义
│       │   └── in_memory_event_bus.py
│       │
│       ├── config/         # 配置管理
│       │   ├── __init__.py
│       │   └── settings.py
│       │
│       └── unit_of_work/   # 工作单元
│           ├── __init__.py
│           └── unit_of_work.py
│
├── alembic/                # Alembic迁移脚本
│   ├── versions/
│   └── env.py
│
├── tests/                   # 测试
│   ├── __init__.py
│   ├── unit/
│   │   ├── domain/
│   │   └── application/
│   ├── integration/
│   │   └── api/
│   └── fixtures/
│
└── docs/                    # 文档
    ├── architecture.md
    └── api.md
```

## 关键文件说明

### main.py
应用入口，负责：
- 创建FastAPI应用实例
- 配置依赖注入
- 注册路由
- 启动应用

### src/infrastructure/config/settings.py
配置管理，从环境变量读取：
- 数据库连接字符串
- 日志级别
- 其他配置项

### src/infrastructure/persistence/database.py
数据库连接管理：
- 创建SQLAlchemy引擎
- 创建会话工厂
- 提供数据库会话依赖

## 依赖方向说明

```
Interface Layer
    ↓ (依赖)
Application Layer
    ↓ (依赖)
Domain Layer
    ↑ (实现)
Infrastructure Layer
```

- **Interface** 依赖 **Application**
- **Application** 依赖 **Domain**（接口）
- **Infrastructure** 实现 **Domain** 定义的接口
- **Application** 通过依赖注入获得 **Infrastructure** 的实现

## 注意事项

1. **Domain层不依赖任何外部库**（除了Python标准库和类型提示）
2. **Infrastructure层实现Domain层定义的接口**
3. **Application层协调Domain和Infrastructure**
4. **Interface层只负责HTTP请求/响应转换**

