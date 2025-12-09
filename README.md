# HomeTom 🏠

<img width="249" height="264" alt="HomeTom Logo" src="https://github.com/user-attachments/assets/fc280e62-298f-4553-821a-2701eda85fec" />

**HomeTom** 是一个基于 **DDD（领域驱动设计）** 和 **洋葱架构** 的智能家居自动化控制系统，专注于场景编排和设备控制。

## ✨ 特性

- 🏗️ **清晰的架构设计**：严格遵循 DDD 和洋葱架构原则
- 🔌 **多设备支持**：支持灯光、空调、窗帘、风扇、门锁、扫地机等多种设备
- 📡 **多平台适配**：可扩展支持 Home Assistant、涂鸦、米家等智能家居平台
- 🎬 **场景自动化**：支持触发器、条件判断和动作编排
- ⚡ **异步执行**：基于 Python asyncio 的高性能异步架构

---

## 🏛️ 系统架构

项目采用**洋葱架构**，依赖方向从外层指向内层：

```
┌─────────────────────────────────────────────────────────────┐
│                     Controller 接口层                        │
│                    (FastAPI REST API)                        │
├─────────────────────────────────────────────────────────────┤
│                     Application 应用层                       │
│         (DeviceService, SceneService, OrchestrationService)  │
├─────────────────────────────────────────────────────────────┤
│                       Domain 领域层                          │
│    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│    │   Device    │  │    Scene    │  │  Execution  │        │
│    │   设备上下文 │  │   场景上下文 │  │  执行上下文  │        │
│    └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                   Infrastructure 基础设施层                   │
│            (Persistence, Adapters, Messaging)                │
└─────────────────────────────────────────────────────────────┘
```

### 三大限界上下文

| 上下文 | 职责 | 核心组件 |
|--------|------|----------|
| **Device** | 设备管理与状态同步 | DeviceAggregate, DeviceCapability, DeviceManager |
| **Scene** | 场景定义与验证 | SceneAggregate, Trigger, Condition, Action |
| **Execution** | 场景执行与工作流编排 | ExecutionAggregate, WorkflowEngine, ExecutionContext |

---

## 📁 目录结构

```
src/
├── application/                 # 应用层
│   ├── device/                  # 设备应用服务
│   ├── scene/                   # 场景应用服务
│   └── orchestration/           # 编排应用服务
│
├── domain/                      # 领域层
│   ├── Device/                  # 设备限界上下文
│   │   ├── aggregates/          # 聚合根
│   │   ├── Actuators/           # 执行器 (Light, Climate, Cover, Fan, Lock, Switch, Vacuum)
│   │   ├── Sensors/             # 传感器 (BinarySensor, DeviceTracker, GenericSensor, Weather)
│   │   ├── services/            # 领域服务
│   │   ├── events/              # 领域事件
│   │   └── repositories/        # 仓储接口
│   │
│   ├── Scene/                   # 场景限界上下文
│   │   ├── aggregates/          # SceneAggregate
│   │   ├── value_objects/       # Trigger, Condition, Action, SceneDefinition
│   │   ├── services/            # SceneValidator, SceneStateMachine
│   │   └── events/              # 场景领域事件
│   │
│   └── Execution/               # 执行限界上下文
│       ├── aggregates/          # ExecutionAggregate
│       ├── value_objects/       # ExecutionContext, ExecutionResult, RetryPolicy
│       ├── services/            # WorkflowEngine, ConditionEvaluator
│       └── events/              # 执行领域事件
│
└── infrastructure/              # 基础设施层
    ├── persistence/             # 数据持久化
    │   ├── models/              # SQLAlchemy ORM 模型
    │   ├── mappers/             # 聚合-模型映射器
    │   ├── repositories/        # 仓储实现
    │   └── unit_of_work.py      # 工作单元
    ├── adapters/                # 外部系统适配器
    │   ├── hardware_adapter.py  # HTTP 硬件客户端
    │   └── hardware_client_registry.py  # 客户端注册表
    ├── messaging/               # 消息与事件
    │   └── event_bus.py         # 内存事件总线
    └── config/                  # 配置管理
```

---

## 🔌 支持的设备类型

### 执行器 (Actuators)

| 设备类型 | 类名 | 主要能力 |
|----------|------|----------|
| 灯光 | `Light` | 开关、亮度调节、色温调节 |
| 空调 | `Climate` | 开关、温度设置、模式切换 |
| 窗帘 | `Cover` | 开合、位置设置、倾斜调节 |
| 风扇 | `Fan` | 开关、风速调节、摇头控制 |
| 门锁 | `Lock` | 上锁、解锁 |
| 开关 | `Switch` | 开关控制 |
| 扫地机 | `Vacuum` | 启动、暂停、返回充电座、定点清扫 |

### 传感器 (Sensors)

| 设备类型 | 类名 | 用途 |
|----------|------|------|
| 二元传感器 | `BinarySensor` | 门窗、移动侦测、烟雾报警等 |
| 设备追踪器 | `DeviceTracker` | 人员/设备位置追踪 |
| 通用传感器 | `GenericSensor` | 温度、湿度、光照等数值传感器 |
| 天气 | `Weather` | 天气状态获取 |

---

## 🛠️ 技术栈

| 类别 | 技术选型 |
|------|----------|
| Web 框架 | FastAPI |
| 数据库 ORM | SQLAlchemy 2.0 |
| 数据库 | SQLite (开发) / PostgreSQL (生产) |
| 数据验证 | Pydantic 2.0 |
| 测试框架 | pytest + pytest-asyncio |
| 异步驱动 | aiosqlite / asyncpg |

---

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行开发服务器

```bash
uvicorn src.main:app --reload
```

---

## 📊 看板

项目进度看板：https://fb.tonglu.de/

---

## 📝 许可证

MIT License
