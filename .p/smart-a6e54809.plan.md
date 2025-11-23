# 智能家居后端架构方案（Domain-Driven Onion Architecture）

## 1. 项目定位与总体目标

- **目标用户**：面向普通家庭用户与智能家居爱好者，提供常见家庭场景（照明、安防、环境舒适等）的编排与执行能力。
- **业务目标**：让用户以图形化方式设计/导入场景，调度多品牌 IoT 设备，实现实时控制与自动化，支持场景之间互相调用与并发执行。
- **技术原则**：洋葱架构 + 领域驱动设计，保持内核纯净、模块高内聚低耦合；确保架构可渐进演进而不过度复杂；优先使用 Python 生态与标准库，减少外部依赖。

## 2. 限界上下文划分

为降低耦合并清晰界定职责，系统在单服务内部划分三个限界上下文，每个上下文拥有独立的领域模型与应用服务，通过明确定义的契约交互：

1. **设备管理上下文（Device Context）**

- 覆盖设备注册、启停、能力描述、状态同步。
- 暴露查询设备列表、查看能力、手动同步等接口。

2. **场景设计上下文（Scene Design Context）**

- 包含场景建模、合法性校验、版本管理、依赖图维护。
- 支持 JSON 导入/导出、版本比对、状态迁移（草稿/已发布/禁用）。

3. **场景执行上下文（Scene Orchestration Context）**

- 负责场景调度、工作流执行、并发控制、子场景调用、执行记录与告警。
- 支持事件触发、手动触发以及执行过程监控。

上下文之间只通过应用服务提供的接口交互，禁止越层访问彼此仓储或实体。例如执行上下文需要使用场景定义时，通过 `SceneAppService` 暴露的查询接口获取，避免跨越限界访问数据库。

## 3. 分层结构与模块说明

系统采用典型洋葱分层：Interface → Application → Domain → Infrastructure。依赖方向始终从外层指向内层，领域层对外仅暴露接口，不感知基础设施细节。

### 3.1 接口层（Interface Layer）

**职责**：接收外部请求、处理认证/参数校验、完成 DTO ↔ 命令/查询对象转换，并调用应用层服务。
**主要模块**：

- `DeviceController`
- `POST /devices`：注册新设备。
- `PUT /devices/{id}/status`：启停设备。
- `GET /devices`：查询设备列表及状态。
- `SceneController`
- `POST /scenes`：新建或导入场景。
- `PUT /scenes/{id}`：编辑场景定义。
- `POST /scenes/{id}/publish`：发布场景（草稿→已发布）。
- `POST /scenes/{id}/disable`：禁用场景。
- `GET /scenes/{id}/versions`：查看版本记录与差异。
- `ExecutionController`
- `POST /executions`：手动触发场景或复合场景执行。
- `GET /executions/{id}`：查询执行详情、耗时、设备反馈。
- `POST /executions/{id}/terminate`：终止正在运行的实例。
- `GET /alerts`：获取告警与失败记录。

**依赖关系**：控制器仅依赖应用服务接口，不直接访问领域对象或基础设施。

### 3.2 应用层（Application Layer）

**职责**：编排用例流程、控制事务边界、调用领域聚合与服务、触发领域事件、协调上下文交互。每个上下文对应一个或多个应用服务。

- `DeviceAppService`
- 协调注册、启停、状态同步流程。
- 调用 `DeviceService`（领域服务）处理状态策略；使用 `DeviceRepository` 持久化。
- 发布设备注册/状态变更事件供其他上下文使用。
- `SceneAppService`
- 执行场景 CRUD、发布/禁用、版本管理。
- 调用 `SceneValidator`、`SceneStateMachine`（领域服务）确保结构合法与状态迁移正确。
- 维护 `scene_dependencies` 图，暴露查询接口给执行上下文。
- `OrchestrationAppService`
- 从 `EventBus` 消费触发事件（定时器、设备事件、手动指令）。
- 调用 `WorkflowEngine` 执行工作流，处理 `SceneCall`（子场景调用）。
- 控制重试、回滚策略，记录 `ExecutionRecord`、`ExecutionLog`、`Alert`。

**依赖关系**：应用层依赖领域层的聚合、领域服务和仓储接口；通过依赖注入获得基础设施实现。上下文之间通过应用服务数据契约交互。

### 3.3 领域层（Domain Layer）

**职责**：封装核心业务概念与规则，保持纯净，不依赖基础设施。主要组成包括聚合、实体、值对象、领域服务、领域事件。

- **聚合与实体**：
- `DeviceAggregate`：包含设备元数据、能力集合、状态；负责设备启停与状态同步。
- `SceneAggregate`：包含场景触发器、条件、动作、子场景引用、版本集合；维护合法性和依赖关系。
- `SceneVersion`：记录每次变更的内容、操作者、时间戳。
- `ExecutionAggregate`：跟踪单次执行上下文（输入参数、执行状态、调用链、重试次数）。
- `ExecutionRecord`、`ExecutionLog`、`Alert`：记录执行结果、日志与告警。
- **值对象**：`Trigger`、`Condition`、`Action`、`SceneCall`、`WorkflowStep`、`ExecutionContext`、`ExecutionResult`、`RetryPolicy`、`ConcurrencyPolicy`。
- **领域服务**：
- `DeviceService`：统一设备状态同步、能力更新策略。
- `SceneValidator`：校验场景结构、子场景引用、循环依赖。
- `SceneStateMachine`：控制场景状态迁移（草稿→已发布→执行中→成功/失败；任意状态可禁用）。
- `WorkflowEngine`：解析并执行工作流步骤，支持并行、条件、子场景调用。
- `RollbackStrategy`：定义异常回滚方式（如反向执行补偿动作）。
- `ConcurrencyCoordinator`：控制并发策略（串行、限流、并行）。
- **领域事件**：
- `DeviceRegistered`、`DeviceStatusChanged`
- `ScenePublished`、`SceneDisabled`
- `ExecutionStarted`、`ExecutionSucceeded`、`ExecutionFailed`、`ChildSceneInvoked`
- 事件仅在领域层定义契约，应用层监听事件并通过基础设施发布或执行业务补充操作。

### 3.4 基础设施层（Infrastructure Layer）

**职责**：实现领域层定义的仓储、适配器、消息发布等接口，负责与数据库、外部设备 API、消息系统等交互。

- **设备适配器（Device Adapter）**
- 抽象接口 `DeviceAdapter`：统一 `turn_on`、`turn_off`、`set_property`、`read_state` 方法。
- 实现：`HttpDeviceAdapter`（对接 REST/HTTP 设备）、`MqttDeviceAdapter`、`ZigbeeDeviceAdapter` 等。初期可选择一个主要协议实现。
- **仓储实现（Repositories）**
- `DeviceRepository`、`SceneRepository`、`SceneVersionRepository`、`SceneDependencyRepository`、`ExecutionRepository`、`ExecutionLogRepository`、`AlertRepository`、`UserRepository`（单租户信息）。
- 使用 ORM 或 SQL 访问 PostgreSQL，严格实现领域层接口。
- **消息队列封装**
- 基于 Python `queue.Queue`/`asyncio.Queue` 实现 `EventBus`，支持发布/订阅、重试队列、优先级，用于场景执行调度。
- 若未来需要跨进程/服务扩展，可无缝替换为 Kafka/RabbitMQ，因应用层仅依赖 `EventBus` 接口。
- **技术基础服务**
- `UnitOfWork` 与事务管理：确保应用服务内操作的一致性。
- 配置中心、日志与链路追踪：记录执行链路、耗时、异常。
- 时间服务、ID 生成器：供领域层使用，保证一致性。
- 健康检查与监控（可在部署阶段引入）。

**依赖关系**：基础设施层依赖外部资源；实现领域层接口；不得反向依赖领域或应用层具体实现。

## 4. 核心业务流程

1. **设备注册/状态同步**
2. 前端调用 `DeviceController` → `DeviceAppService`。
3. `DeviceAggregate` 校验设备信息，调用 `DeviceRepository` 持久化。
4. `DeviceAdapter` 与硬件 API 通信，完成真实注册或状态读取。
5. `DeviceAppService` 发布 `DeviceRegistered` 或 `DeviceStatusChanged` 事件，供场景模块更新能力缓存。

2. **场景创建/发布流程**
3. 前端上传 JSON → `SceneController` → `SceneAppService`。
4. `SceneValidator` 校验触发器、条件、动作、子场景引用，检查循环依赖。
5. `SceneAggregate` 更新并生成新版本，`SceneRepository` 与 `SceneVersionRepository` 持久化。
6. 状态机将场景标记为草稿；用户发布时，状态迁移至已发布，并写入 `scene_dependencies`。
7. 发布触发 `ScenePublished` 事件，执行上下文可据此预热或缓存场景定义。

3. **场景执行与编排**
4. 定时器、设备事件或手动触发 → 封装事件推入 `EventBus`。
5. `OrchestrationAppService` 并发消费事件，加载场景定义（通过 `SceneAppService` 查询）并创建 `ExecutionAggregate`。
6. `WorkflowEngine` 按步骤执行动作和子场景，依据 `ConcurrencyPolicy` 控制并行度。
7. 每个动作通过 `DeviceAdapter` 调用对应设备；`ExecutionRecord`、`ExecutionLog` 记录结果与耗时。
8. 失败时根据 `RetryPolicy` 重试；超过阈值执行 `RollbackStrategy` 并创建 `Alert`。
9. 执行结果同步写入仓储，供查询与审计。

4. **执行反馈与追踪**
5. 前端查询 `ExecutionController`，由 `OrchestrationAppService` 汇总 `ExecutionRepository`、`ExecutionLogRepository`、`AlertRepository` 数据。
6. 返回执行调用链（父场景→子场景）、每步耗时、设备响应、失败原因。
7. 告警列表支持筛选、确认、关闭等操作（由后续版本扩展）。

## 5. 数据模型与持久化

- **核心表结构**（PostgreSQL）
- `devices`：设备基础信息、所属厂商、适配器类型。
- `device_states`：设备实时状态、最后一次同步时间、状态来源。
- `scenes`：场景主表，包含名称、描述、当前版本、状态（草稿/已发布/禁用）。
- `scene_versions`：存储 JSON 定义、版本号、发布人、差异摘要、创建时间。
- `scene_dependencies`：记录场景调用关系（父场景 ID、子场景 ID），用于循环检测与调用链查询。
- `scene_executions`：记录每次执行的场景 ID、版本、触发来源、执行状态、开始/结束时间。
- `execution_logs`：逐步记录执行步骤、动作类型、目标设备、响应、耗时。
- `alerts`：告警信息（关联执行、告警类型、严重级别、处理状态）。
- `users`：单租户用户信息及偏好配置（初期可简化为单用户模式）。
- **审计字段**：所有表应包含 `created_at`、`updated_at`、`operator`、`trace_id` 等字段；日志表额外记录执行耗时、异常堆栈。
- **版本与历史管理**：场景每次改动生成新版本；执行记录关联具体版本；支持按版本回滚或比较。

## 6. 非功能要求与设计原则

- **依赖方向**：Interface → Application → Domain → Infrastructure 单向依赖；领域层仅依赖自身与基础接口。
- **并发策略**：`ConcurrencyCoordinator` 定义单场景最大并发数、同一设备同时执行策略（队列/拒绝/并行），可通过配置调整。
- **可测试性**：
- 领域层单元测试覆盖状态机、工作流引擎、回滚策略等核心逻辑。
- 应用层用例测试确保业务流程正确。
- 适配器契约测试验证外部 API 交互。
- 集成测试覆盖典型多场景并行执行、回滚路径。
- **扩展性**：
- `DeviceAdapter` 可新增厂商实现；
- `EventBus` 可替换为 Kafka/RabbitMQ；
- 上下文可在未来拆分为独立微服务；
- 场景执行可对接 AI/规则引擎做智能推荐（后续增强）。
- **性能与可靠性**：
- 基于标准库队列实现异步调度，轻量又易维护；
- 通过执行日志与告警监控失败率，提供告警阈值配置；
- 采用统一错误处理与重试机制，确保设备操作一致性。

## 7. 实施路线建议

1. **MVP 阶段（核心功能验证）**

- 实现设备 REST 适配器、基础场景建模、单场景执行、执行日志。
- 使用同步队列和简单重试策略。

2. **增强阶段（稳定性与并发）**

- 引入并发控制、场景嵌套、回滚策略、告警系统。
- 优化 UI 与执行反馈接口。

3. **扩展阶段（生态与智能）**

- 支持更多设备协议、外部通知通道。
- 引入 AI 分析、推荐场景模板。

该架构在保证轻量的前提下维持专业度与扩展性：领域模型聚焦核心业务，基础设施以接口实现，允许后续演进为更复杂的分布式或微服务形态，同时当前阶段也便于小团队快速实现与迭代。