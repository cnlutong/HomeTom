# MVP 最小化开发计划

## 目标
实现核心功能，建立完整的DDD+洋葱架构基础，为后续扩展奠定坚实基础。

## 开发原则
1. **保持架构纯净**：严格遵循洋葱架构依赖方向（Interface → Application → Domain → Infrastructure）
2. **领域驱动**：三个限界上下文独立演进，通过应用服务接口交互
3. **渐进式实现**：先实现核心路径，再逐步增强
4. **接口优先**：领域层定义接口，基础设施层实现，便于测试和替换

---

## 阶段一：基础设施与领域核心（Week 1-2）

### 1.1 项目结构与依赖管理
- [ ] 创建标准目录结构（按洋葱架构分层）
- [ ] 配置 `requirements.txt`（最小依赖：FastAPI、SQLAlchemy、pydantic）
- [ ] 配置数据库连接（PostgreSQL，使用SQLAlchemy ORM）
- [ ] 建立基础配置管理（环境变量、配置类）

**目录结构（参考）**：
```
src/
├── controller/          # 接口层
│   ├── api/
│   │   ├── device_controller.py
│   │   ├── scene_controller.py
│   │   └── execution_controller.py
│   └── dto/            # 数据传输对象
├── application/        # 应用层
│   ├── device_app_service.py
│   ├── scene_app_service.py
│   └── orchestration_app_service.py
├── domain/             # 领域层（已存在部分）
│   ├── device/
│   │   ├── aggregates/     # 聚合根
│   │   ├── entities/       # 实体
│   │   ├── value_objects/  # 值对象
│   │   ├── services/       # 领域服务
│   │   ├── events/         # 领域事件
│   │   └── repositories/   # 仓储接口
│   ├── scene/
│   │   └── (同上结构)
│   └── execution/
│       └── (同上结构)
└── infrastructure/     # 基础设施层
    ├── persistence/     # 仓储实现
    ├── adapters/       # 设备适配器
    ├── messaging/      # 事件总线
    └── config/         # 配置
```

### 1.2 领域层核心模型（Device Context）

#### 1.2.1 设备聚合根
- [ ] `DeviceAggregate`：设备聚合根
  - 属性：entity_id, name, manufacturer, adapter_type, capabilities, status (enabled/disabled)
  - 方法：enable(), disable(), sync_state(), update_capabilities()
  - 领域事件：DeviceRegistered, DeviceStatusChanged

#### 1.2.2 设备值对象
- [ ] `DeviceCapability`：设备能力描述（turn_on, turn_off, set_brightness等）
- [ ] `DeviceStatus`：设备状态枚举（enabled, disabled, unavailable）

#### 1.2.3 设备仓储接口
- [ ] `IDeviceRepository`：定义查询、保存、删除接口（领域层）

#### 1.2.4 设备领域服务
- [ ] `DeviceService`：设备状态同步策略、能力更新逻辑

### 1.3 领域层核心模型（Scene Context）

#### 1.3.1 场景聚合根
- [ ] `SceneAggregate`：场景聚合根
  - 属性：scene_id, name, description, status (draft/published/disabled), definition
  - 方法：publish(), disable(), update_definition()
  - 领域事件：ScenePublished, SceneDisabled

#### 1.3.2 场景值对象
- [ ] `Trigger`：触发器（定时器、设备事件、手动）
- [ ] `Condition`：条件（设备状态判断）
- [ ] `Action`：动作（设备控制、子场景调用）
- [ ] `SceneDefinition`：场景定义（包含触发器、条件、动作的JSON结构）

#### 1.3.3 场景仓储接口
- [ ] `ISceneRepository`：场景CRUD接口

#### 1.3.5 场景领域服务
- [ ] `SceneValidator`：场景结构校验、循环依赖检测（基础版本）
- [ ] `SceneStateMachine`：状态迁移逻辑（draft → published → disabled）

### 1.4 领域层核心模型（Execution Context）

#### 1.4.1 执行聚合根
- [ ] `ExecutionAggregate`：执行聚合根
  - 属性：execution_id, scene_id, status (running/success/failed), started_at, ended_at
  - 方法：start(), complete(), fail(), retry()
  - 领域事件：ExecutionStarted, ExecutionSucceeded, ExecutionFailed

#### 1.4.2 执行值对象
- [ ] `ExecutionContext`：执行上下文（输入参数、调用链）
- [ ] `ExecutionResult`：执行结果（成功/失败、错误信息）
- [ ] `RetryPolicy`：重试策略（最大次数、间隔）

#### 1.4.3 执行记录实体
- [ ] `ExecutionRecord`：执行记录（关联执行聚合）
- [ ] `ExecutionLog`：执行日志（步骤、设备、响应、耗时）

#### 1.4.4 执行仓储接口
- [ ] `IExecutionRepository`：执行记录查询接口

#### 1.4.5 执行领域服务
- [ ] `WorkflowEngine`：工作流引擎（基础版本：顺序执行动作）
- [ ] `ConcurrencyCoordinator`：并发控制（基础版本：串行执行）

---

## 阶段二：基础设施实现（Week 2-3）

### 2.1 数据库模型与仓储实现

#### 2.1.1 SQLAlchemy模型
- [ ] `DeviceModel`：设备表模型
- [ ] `DeviceStateModel`：设备状态表模型
- [ ] `SceneModel`：场景表模型
- [ ] `SceneDependencyModel`：场景依赖表模型
- [ ] `ExecutionModel`：执行表模型
- [ ] `ExecutionLogModel`：执行日志表模型

#### 2.1.2 仓储实现
- [ ] `DeviceRepository`：实现 `IDeviceRepository`
- [ ] `SceneRepository`：实现 `ISceneRepository`
- [ ] `ExecutionRepository`：实现 `IExecutionRepository`

#### 2.1.3 数据库（如果需要）
- [ ] 创建数据库初始化脚本

### 2.2 设备通信层实现

> **设计说明**：由于不同设备具有不同的能力（如灯光有 `set_brightness`，空调有 `set_temperature`），
> 且不同智能家居平台（Home Assistant、米家、涂鸦）的 API 各不相同，
> 因此采用**分层设计**而非固定接口的适配器模式。

#### 2.2.1 设备能力层（已在 Domain 层实现）
- [x] `BaseDevice`：设备基类，定义通用属性（entity_id, state, attributes）
- [x] `Actuator` / `Sensor`：设备分类基类
- [x] 具体设备类（`Light`, `Climate`, `Cover` 等）：
  - 每个设备类定义自己的方法（如 `Light.set_brightness()`）
  - 通过 `attributes` 字典暴露设备能力和状态

#### 2.2.2 设备管理器（执行层调用入口）
- [x] `IDeviceManager`：设备管理接口
  - `get_device(entity_id)`: 获取设备实例
  - `execute_command(entity_id, command, params)`: 动态方法调用
  - `get_device_state(entity_id)`: 获取设备状态
  - `get_device_attributes(entity_id)`: 获取设备属性
- [x] `DeviceManager`：使用反射机制动态调用设备方法

#### 2.2.3 硬件通信层接口（领域层）
- [x] `IHardwareClient`：定义通用通信能力
  - `call_service(domain, service, entity_id, data)`: 调用服务
  - `get_state(entity_id)`: 获取设备状态
  - `check_connection()`: 检查连接状态

#### 2.2.4 硬件客户端注册表（基础设施层）
- [x] `HardwareClientRegistry`：客户端注册表，根据 `adapter_type` 路由到正确的客户端
  - `register(adapter_type, client)`: 注册客户端
  - `get_client(adapter_type)`: 获取客户端
  - 支持的 adapter_type：`homeassistant`, `tuya`, `mijia` 等

#### 2.2.5 平台实现（基础设施层）
- [x] `HttpHardwareClient`：HTTP REST 通信实现（如 Home Assistant API）
  - 支持 Bearer Token 认证
  - 错误处理和日志记录
  - 可扩展支持重试机制
- [ ] 未来可扩展：`TuyaCloudClient`、`MiHomeClient` 等

**客户端路由机制**：
```
DeviceAggregate.adapter_type  →  HardwareClientRegistry  →  IHardwareClient 实现
       "homeassistant"        →        注册表查找        →   HttpHardwareClient
       "tuya"                 →        注册表查找        →   TuyaCloudClient
       "mijia"                →        注册表查找        →   MiHomeClient
```

**完整架构图**：
```
┌────────────────────────────────────────────────────────────────┐
│                  DeviceAggregate (聚合根)                       │
│  adapter_type: "homeassistant" / "tuya" / "mijia"              │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│              HardwareClientRegistry (客户端注册表)              │
│  "homeassistant" → HttpHardwareClient                          │
│  "tuya"          → TuyaCloudClient                             │
│  "mijia"         → MiHomeClient                                │
└────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│HttpHardwareClient│ │  TuyaCloudClient │ │   MiHomeClient   │
│  (Home Assistant)│ │    (涂鸦云)      │ │    (米家)        │
│                  │ │                  │ │                  │
│ call_service()   │ │ call_service()   │ │ call_service()   │
│ get_state()      │ │ get_state()      │ │ get_state()      │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

### 2.3 事件总线实现

#### 2.3.1 事件总线接口
- [ ] `IEventBus`：定义发布/订阅接口

#### 2.3.2 内存事件总线
- [ ] `InMemoryEventBus`：基于 `asyncio.Queue` 实现
  - 支持事件发布
  - 支持事件订阅
  - 支持优先级队列

### 2.4 工作单元与事务管理

- [ ] `UnitOfWork`：实现事务管理接口
- [ ] 集成SQLAlchemy会话管理

---

## 阶段三：应用层实现（Week 3-4）

### 3.1 设备应用服务

- [ ] `DeviceAppService`：
  - `register_device()`：注册设备
  - `enable_device()` / `disable_device()`：启停设备
  - `sync_device_state()`：同步设备状态
  - `list_devices()`：查询设备列表
  - 发布领域事件（DeviceRegistered, DeviceStatusChanged）

### 3.2 场景应用服务

- [ ] `SceneAppService`：
  - `create_scene()`：创建场景（草稿状态）
  - `update_scene()`：更新场景（生成新版本）
  - `publish_scene()`：发布场景（状态迁移）
  - `disable_scene()`：禁用场景
  - `get_scene_definition()`：查询场景定义（供执行上下文使用）
  - `list_scenes()`：查询场景列表
  - 发布领域事件（ScenePublished, SceneDisabled）

### 3.3 编排应用服务

- [ ] `OrchestrationAppService`：
  - `trigger_execution()`：触发场景执行（手动/事件）
  - `execute_scene()`：执行场景工作流
  - `get_execution_details()`：查询执行详情
  - `terminate_execution()`：终止执行（基础版本可延后）
  - 监听领域事件，触发执行

---

## 阶段四：接口层实现（Week 4-5）

### 4.1 DTO定义

- [ ] `DeviceDTO`：设备数据传输对象
- [ ] `SceneDTO`：场景数据传输对象
- [ ] `ExecutionDTO`：执行数据传输对象
- [ ] 请求/响应模型（使用pydantic）

### 4.2 REST API控制器

#### 4.2.1 设备控制器
- [ ] `POST /api/devices`：注册设备
- [ ] `PUT /api/devices/{id}/status`：启停设备
- [ ] `GET /api/devices`：查询设备列表
- [ ] `POST /api/devices/{id}/sync`：同步设备状态

#### 4.2.2 场景控制器
- [ ] `POST /api/scenes`：创建/导入场景
- [ ] `PUT /api/scenes/{id}`：更新场景
- [ ] `POST /api/scenes/{id}/publish`：发布场景
- [ ] `POST /api/scenes/{id}/disable`：禁用场景
- [ ] `GET /api/scenes`：查询场景列表
- [ ] `GET /api/scenes/{id}`：查询场景详情

#### 4.2.3 执行控制器
- [ ] `POST /api/executions`：手动触发执行
- [ ] `GET /api/executions/{id}`：查询执行详情
- [ ] `GET /api/executions`：查询执行列表

### 4.3 FastAPI应用配置

- [ ] 创建FastAPI应用实例
- [ ] 配置路由注册
- [ ] 配置依赖注入（使用FastAPI的Depends）
- [ ] 配置异常处理中间件
- [ ] 配置CORS（如需要）

---

## 阶段五：集成与测试（Week 5-6）

### 5.1 单元测试

- [ ] 领域层单元测试：
  - `DeviceAggregate` 测试
  - `SceneAggregate` 测试
  - `SceneValidator` 测试
  - `SceneStateMachine` 测试
  - `WorkflowEngine` 测试

### 5.2 集成测试

- [ ] 设备注册流程测试
- [ ] 场景创建和发布流程测试
- [ ] 场景执行流程测试（单场景、单动作）
- [ ] 事件总线集成测试

### 5.3 端到端测试

- [ ] 完整业务流程测试：
  1. 注册设备 → 创建场景 → 发布场景 → 触发执行 → 查询结果

### 5.4 文档

- [ ] API文档（使用FastAPI自动生成）
- [ ] 架构说明文档
- [ ] 开发指南

---

## MVP功能范围

### ✅ 包含的功能
1. **设备管理**：设备注册、启停、状态同步（HTTP适配器）
2. **场景设计**：场景创建、编辑、发布、禁用
3. **场景执行**：手动触发、顺序执行动作、执行记录
4. **基础校验**：场景结构校验、状态机校验

### ❌ 暂不包含（后续增强）
1. 子场景调用（场景嵌套）
2. 回滚策略
3. 告警系统
4. 定时器触发（仅支持手动触发）
5. 设备事件触发（仅支持手动触发）
6. 执行终止功能

---

## 技术栈选择

### 核心框架
- **Web框架**：FastAPI（异步、自动文档、类型提示）
- **ORM**：SQLAlchemy（成熟、灵活）
- **数据库**：PostgreSQL（关系型、支持JSON字段）
- **迁移工具**：Alembic（SQLAlchemy官方工具）

### 依赖管理
- **包管理**：poetry 或 pip + requirements.txt
- **类型检查**：mypy（可选）
- **代码格式化**：black（可选）

### 测试框架
- **单元测试**：pytest
- **异步测试**：pytest-asyncio

---


## 扩展性设计要点

### 1. 接口抽象
- 所有外部依赖通过接口定义（仓储、适配器、事件总线）
- 基础设施层实现接口，应用层依赖接口

### 2. 依赖注入
- 使用FastAPI的Depends机制实现依赖注入
- 便于测试时替换实现

### 3. 领域事件
- 通过事件解耦上下文之间的交互
- 未来可替换为Kafka/RabbitMQ

### 4. 配置化
- 设备适配器类型可配置
- 重试策略可配置
- 并发策略可配置（未来）

### 5. 未来扩展
- 场景版本管理可在后续版本中添加（如需回滚、比对功能）

---

## 下一步行动

1. **立即开始**：创建项目结构，配置依赖
2. **优先实现**：Device Context（已有部分领域模型基础）
3. **并行开发**：领域层和基础设施层可并行（通过接口契约）
4. **迭代验证**：每完成一个上下文，进行集成测试

---

## 注意事项

1. **保持架构纯净**：严格遵循依赖方向，避免循环依赖
2. **接口优先**：先定义接口，再实现，便于测试和替换
3. **最小实现**：MVP阶段只实现核心路径，复杂功能延后
4. **可测试性**：每个层次都要便于单元测试
5. **文档同步**：代码变更时同步更新架构文档

