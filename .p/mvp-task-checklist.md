# MVP 任务清单（按优先级排序）

## 🔴 P0 - 核心基础设施（必须先完成）

### 项目基础
- [ ] 创建标准目录结构
- [ ] 配置 `pyproject.toml` 或 `requirements.txt`
- [ ] 配置数据库连接（PostgreSQL + SQLAlchemy）
- [ ] 配置环境变量管理（.env文件）
- [ ] 创建主应用入口（main.py）

### 领域层 - Device Context
- [ ] `DeviceAggregate` 聚合根
- [ ] `DeviceCapability` 值对象
- [ ] `DeviceStatus` 值对象/枚举
- [ ] `IDeviceRepository` 仓储接口
- [ ] `DeviceService` 领域服务接口
- [ ] 领域事件：`DeviceRegistered`, `DeviceStatusChanged`

### 领域层 - Scene Context
- [ ] `SceneAggregate` 聚合根
- [ ] `SceneVersion` 实体
- [ ] `Trigger`, `Condition`, `Action` 值对象
- [ ] `SceneDefinition` 值对象
- [ ] `ISceneRepository` 仓储接口
- [ ] `ISceneVersionRepository` 仓储接口
- [ ] `SceneValidator` 领域服务接口
- [ ] `SceneStateMachine` 领域服务接口
- [ ] 领域事件：`ScenePublished`, `SceneDisabled`

### 领域层 - Execution Context
- [ ] `ExecutionAggregate` 聚合根
- [ ] `ExecutionRecord` 实体
- [ ] `ExecutionLog` 实体
- [ ] `ExecutionContext`, `ExecutionResult`, `RetryPolicy` 值对象
- [ ] `IExecutionRepository` 仓储接口
- [ ] `WorkflowEngine` 领域服务接口
- [ ] 领域事件：`ExecutionStarted`, `ExecutionSucceeded`, `ExecutionFailed`

---

## 🟠 P1 - 基础设施实现（依赖P0完成）

### 数据库层
- [ ] SQLAlchemy模型：`DeviceModel`
- [ ] SQLAlchemy模型：`DeviceStateModel`
- [ ] SQLAlchemy模型：`SceneModel`
- [ ] SQLAlchemy模型：`SceneVersionModel`
- [ ] SQLAlchemy模型：`SceneDependencyModel`
- [ ] SQLAlchemy模型：`ExecutionModel`
- [ ] SQLAlchemy模型：`ExecutionLogModel`
- [ ] Alembic初始化
- [ ] 创建初始迁移脚本

### 仓储实现
- [ ] `DeviceRepository` 实现
- [ ] `SceneRepository` 实现
- [ ] `SceneVersionRepository` 实现
- [ ] `ExecutionRepository` 实现

### 设备适配器
- [ ] `IDeviceAdapter` 接口定义
- [ ] `HttpDeviceAdapter` 实现（基础版本）

### 事件总线
- [ ] `IEventBus` 接口定义
- [ ] `InMemoryEventBus` 实现

### 工作单元
- [ ] `IUnitOfWork` 接口定义
- [ ] `UnitOfWork` 实现（SQLAlchemy）

---

## 🟡 P2 - 应用层实现（依赖P1完成）

### DeviceAppService
- [ ] `register_device()` 方法
- [ ] `enable_device()` 方法
- [ ] `disable_device()` 方法
- [ ] `sync_device_state()` 方法
- [ ] `list_devices()` 方法
- [ ] 事件发布逻辑

### SceneAppService
- [ ] `create_scene()` 方法
- [ ] `update_scene()` 方法
- [ ] `publish_scene()` 方法
- [ ] `disable_scene()` 方法
- [ ] `get_scene_definition()` 方法
- [ ] `list_scenes()` 方法
- [ ] 事件发布逻辑

### OrchestrationAppService
- [ ] `trigger_execution()` 方法
- [ ] `execute_scene()` 方法
- [ ] `get_execution_details()` 方法
- [ ] 事件监听逻辑

### 领域服务实现
- [ ] `DeviceService` 实现
- [ ] `SceneValidator` 实现（基础版本）
- [ ] `SceneStateMachine` 实现
- [ ] `WorkflowEngine` 实现（顺序执行）
- [ ] `ConcurrencyCoordinator` 实现（串行执行）

---

## 🟢 P3 - 接口层实现（依赖P2完成）

### DTO定义
- [ ] `DeviceDTO` 及相关请求/响应模型
- [ ] `SceneDTO` 及相关请求/响应模型
- [ ] `ExecutionDTO` 及相关请求/响应模型

### DeviceController
- [ ] `POST /api/devices` 端点
- [ ] `PUT /api/devices/{id}/status` 端点
- [ ] `GET /api/devices` 端点
- [ ] `POST /api/devices/{id}/sync` 端点

### SceneController
- [ ] `POST /api/scenes` 端点
- [ ] `PUT /api/scenes/{id}` 端点
- [ ] `POST /api/scenes/{id}/publish` 端点
- [ ] `POST /api/scenes/{id}/disable` 端点
- [ ] `GET /api/scenes` 端点
- [ ] `GET /api/scenes/{id}` 端点

### ExecutionController
- [ ] `POST /api/executions` 端点
- [ ] `GET /api/executions/{id}` 端点
- [ ] `GET /api/executions` 端点

### FastAPI应用配置
- [ ] 创建FastAPI应用实例
- [ ] 注册所有路由
- [ ] 配置依赖注入
- [ ] 配置异常处理
- [ ] 配置CORS（如需要）

---

## 🔵 P4 - 测试与文档（依赖P3完成）

### 单元测试
- [ ] `DeviceAggregate` 测试
- [ ] `SceneAggregate` 测试
- [ ] `SceneValidator` 测试
- [ ] `SceneStateMachine` 测试
- [ ] `WorkflowEngine` 测试
- [ ] 仓储实现测试

### 集成测试
- [ ] 设备注册流程测试
- [ ] 场景创建和发布流程测试
- [ ] 场景执行流程测试
- [ ] 事件总线集成测试

### 端到端测试
- [ ] 完整业务流程测试

### 文档
- [ ] API文档（FastAPI自动生成）
- [ ] 架构说明文档更新
- [ ] 开发指南

---

## 📋 开发顺序建议

### Week 1
1. 完成P0中的项目基础和Device Context领域层
2. 完成P0中的Scene Context领域层（基础版本）

### Week 2
1. 完成P0中的Execution Context领域层
2. 开始P1的数据库层和仓储实现

### Week 3
1. 完成P1的所有基础设施实现
2. 开始P2的应用层实现

### Week 4
1. 完成P2的应用层实现
2. 开始P3的接口层实现

### Week 5
1. 完成P3的接口层实现
2. 开始P4的测试

### Week 6
1. 完成P4的测试和文档
2. MVP交付

---

## 🎯 关键决策点

### 决策1：设备适配器策略
- **MVP选择**：仅实现HTTP适配器
- **扩展性**：通过`IDeviceAdapter`接口，后续可添加MQTT、Zigbee等

### 决策2：事件总线策略
- **MVP选择**：内存事件总线（`asyncio.Queue`）
- **扩展性**：通过`IEventBus`接口，后续可替换为Kafka/RabbitMQ

### 决策3：工作流引擎策略
- **MVP选择**：顺序执行，不支持并行和条件分支
- **扩展性**：`WorkflowEngine`接口支持后续扩展

### 决策4：并发控制策略
- **MVP选择**：串行执行，同一时间只执行一个场景
- **扩展性**：`ConcurrencyCoordinator`接口支持后续扩展

### 决策5：场景嵌套策略
- **MVP选择**：不支持子场景调用
- **扩展性**：`Action`值对象已预留`SceneCall`类型，后续可扩展

---

## ⚠️ 风险与应对

### 风险1：领域模型设计不当
- **应对**：先完成领域模型设计评审，再开始实现
- **检查点**：Week 1结束时进行领域模型评审

### 风险2：接口定义不清晰
- **应对**：先定义所有接口，再实现
- **检查点**：P0完成后进行接口评审

### 风险3：测试覆盖不足
- **应对**：每个层次完成后立即编写测试
- **检查点**：P2完成后进行测试覆盖率检查

### 风险4：性能问题
- **应对**：MVP阶段暂不考虑性能优化，关注功能正确性
- **后续**：在增强阶段进行性能优化

---

## 📝 开发规范

### 代码组织
- 每个限界上下文独立目录
- 每个层次独立目录
- 接口和实现分离

### 命名规范
- 聚合根：`XxxAggregate`
- 实体：`XxxEntity` 或直接命名
- 值对象：`XxxValue` 或直接命名
- 仓储接口：`IXxxRepository`
- 仓储实现：`XxxRepository`
- 应用服务：`XxxAppService`
- 领域服务：`XxxService`
- 控制器：`XxxController`

### 依赖注入
- 使用FastAPI的`Depends`机制
- 在应用启动时注册所有依赖

### 错误处理
- 领域层抛出领域异常
- 应用层捕获并转换为应用异常
- 接口层捕获并返回HTTP错误响应

