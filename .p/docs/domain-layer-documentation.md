# 领域层说明文档

## 概述

领域层（Domain Layer）是 HomeTom 智能家居系统的核心业务逻辑层，采用领域驱动设计（Domain-Driven Design, DDD）架构模式。领域层完全独立于基础设施和技术实现，专注于表达业务规则和领域概念。

## 架构设计

### 设计模式

领域层遵循以下 DDD 核心概念：

- **聚合根（Aggregate Root）**：维护业务一致性的边界
- **实体（Entity）**：具有唯一标识的对象
- **值对象（Value Object）**：不可变的对象，通过值进行比较
- **领域服务（Domain Service）**：跨聚合的业务逻辑
- **仓储接口（Repository Interface）**：定义持久化抽象
- **领域事件（Domain Event）**：记录领域中发生的重要事件
- **异常（Exception）**：领域特定的异常类型

### 目录结构

```
src/domain/
├── Device/          # 设备领域
├── Scene/           # 场景领域
└── Execution/       # 执行领域
```

每个领域都包含以下标准目录结构：
- `aggregates/` - 聚合根
- `entities/` - 实体
- `value_objects/` - 值对象
- `services/` - 领域服务接口
- `repositories/` - 仓储接口
- `events/` - 领域事件
- `exceptions.py` - 领域异常

## 核心领域

### 1. Device（设备）领域

设备领域负责管理智能家居系统中的所有设备及其能力。

#### 1.1 聚合根

**DeviceAggregate** - 设备聚合根

封装设备的核心业务逻辑，维护设备的一致性边界。

**核心属性：**
- `device_id` - 设备唯一标识
- `entity_id` - 设备实体ID（如 HomeAssistant 的 entity_id）
- `name` - 设备名称
- `adapter_type` - 适配器类型（如 "http", "mqtt"）
- `manufacturer` - 制造商（可选）
- `capabilities` - 设备能力集合
- `status` - 设备状态（ENABLED/DISABLED/UNAVAILABLE）
- `created_at` / `updated_at` - 时间戳

**核心行为：**
- `create()` - 工厂方法，创建设备并发布 DeviceRegistered 事件
- `enable()` / `disable()` - 启用/禁用设备
- `update_capabilities()` / `add_capability()` - 更新设备能力
- `has_capability()` - 检查是否支持某个能力
- `mark_as_unavailable()` - 标记设备为不可用
- `sync_state()` - 同步设备状态

**领域事件：**
- `DeviceRegistered` - 设备注册时发布
- `DeviceStatusChanged` - 设备状态变更时发布

#### 1.2 值对象

**DeviceStatus** - 设备状态枚举
```python
ENABLED = "enabled"      # 已启用
DISABLED = "disabled"    # 已禁用
UNAVAILABLE = "unavailable"  # 不可用
```

**DeviceCapability** - 设备能力值对象
- `name` - 能力名称（如 "turn_on", "set_brightness"）
- `parameters` - 能力参数（可选，如 `{"min": 0, "max": 255}`）

**DeviceCapabilities** - 设备能力集合
提供能力查询和管理的便捷方法。

#### 1.3 领域服务

**IDeviceService** - 设备领域服务接口

定义设备相关的领域逻辑：
- `sync_device_state()` - 同步设备状态策略
- `update_capabilities()` - 更新设备能力逻辑
- `validate_device_config()` - 验证设备配置

#### 1.4 仓储接口

**IDeviceRepository** - 设备仓储接口

定义设备持久化操作：
- `save()` - 保存设备
- `find_by_id()` - 根据ID查找
- `find_by_entity_id()` - 根据实体ID查找
- `find_all()` - 查找所有设备
- `find_by_status()` - 根据状态查找
- `delete()` - 删除设备

#### 1.5 设备类型继承体系

**BaseDevice** - 设备基类（抽象类）
- 定义所有设备共有的属性和基础方法
- 核心属性：`entity_id`（实体ID）、`name`（名称）、`state`（状态）、`attributes`（属性字典）
- 提供 `update_state()` 抽象方法，强制子类实现获取最新状态的逻辑
- 提供 `get_state()` 方法返回当前已知状态

**设备分类：**

1. **执行器（Actuators）** - 可被控制的设备
   - `Actuator` - 执行器基类
     - 继承自 `BaseDevice`
     - 提供 `turn_on()`, `turn_off()`, `is_on()` 方法
     - 子类包括：
       - `Climate` - 气候控制设备（空调、温控器等）
       - `Cover` - 遮阳设备（窗帘、卷帘门、车库门等）
       - `Fan` - 风扇设备
       - `Light` - 灯光设备
       - `Lock` - 门锁设备
       - `Switch` - 开关设备
       - `Vacuum` - 吸尘器设备

2. **传感器（Sensors）** - 用于读取状态的设备
   - `Sensor` - 传感器基类
     - 继承自 `BaseDevice`
     - 主要用于读取和监控环境或设备状态
     - 子类包括：
       - `BinarySensor` - 二进制传感器（开关状态传感器，如门窗传感器）
       - `DeviceTracker` - 设备追踪器（追踪设备位置）
       - `GenericSensor` - 通用传感器
       - `Weather` - 天气传感器

3. **媒体与安全（MediaSecurity）** - 媒体播放和安全相关设备
   - `MediaSecurityBase` - 媒体安全设备基类
     - 继承自 `BaseDevice`
     - 子类包括：
       - `AlarmControlPanel` - 报警控制面板
       - `Camera` - 摄像头设备
       - `MediaPlayer` - 媒体播放器

**注意：** 这些设备类型类主要用于类型定义和基础方法实现。实际的设备管理和业务逻辑由 `DeviceAggregate` 聚合根处理。

#### 1.6 领域异常

- `DeviceDomainException` - 设备领域异常基类
- `DeviceNotFoundException` - 设备未找到异常
- `DeviceAlreadyExistsException` - 设备已存在异常
- `InvalidDeviceStatusException` - 无效的设备状态异常
- `InvalidCapabilityException` - 无效的设备能力异常

---

### 2. Scene（场景）领域

场景领域负责管理智能家居场景的定义、版本控制和生命周期。

#### 2.1 聚合根

**SceneAggregate** - 场景聚合根

封装场景的核心业务逻辑，维护场景的一致性边界。

**核心属性：**
- `scene_id` - 场景唯一标识
- `name` - 场景名称
- `description` - 场景描述（可选）
- `status` - 场景状态（DRAFT/PUBLISHED/DISABLED）
- `current_version` - 当前版本号
- `created_at` / `updated_at` - 时间戳

**核心行为：**
- `create()` - 工厂方法，创建新场景（默认状态为草稿）
- `update_name()` / `update_description()` - 更新场景信息
- `create_version()` - 创建新版本
- `get_latest_version()` / `get_version()` - 获取版本信息
- `publish()` - 发布场景（从草稿迁移到已发布）
- `disable()` - 禁用场景

**状态迁移规则：**
- DRAFT → PUBLISHED（必须至少有一个版本）
- PUBLISHED → DISABLED
- DISABLED → PUBLISHED（需要先启用）

**领域事件：**
- `ScenePublished` - 场景发布时发布
- `SceneDisabled` - 场景禁用时发布

#### 2.2 实体

**SceneVersion** - 场景版本实体

存储场景的版本历史：
- `version_number` - 版本号（必须大于0）
- `scene_id` - 所属场景ID
- `definition` - 场景定义值对象
- `created_at` - 创建时间
- `operator` - 操作者（可选）
- `change_summary` - 变更摘要（可选）

**方法：**
- `to_dict()` - 转换为字典（用于序列化）

#### 2.3 值对象

**SceneDefinition** - 场景定义值对象

封装场景的完整定义，不可变：
- `triggers` - 触发器列表（必填）
- `conditions` - 条件列表（可选）
- `actions` - 动作列表（必填）

**方法：**
- `get_referenced_scenes()` - 获取引用的子场景ID列表
- `get_referenced_devices()` - 获取引用的设备实体ID列表

**Trigger** - 触发器值对象
定义场景的触发条件，不可变：

- `type` - 触发器类型（MANUAL/TIMER/DEVICE_EVENT）
- `config` - 触发器配置（根据类型不同而不同）

**触发器类型：**
- `MANUAL` - 手动触发（配置为空）
- `TIMER` - 定时器触发（配置包含 `schedule` 定时表达式）
- `DEVICE_EVENT` - 设备事件触发（配置包含 `entity_id`, `event_type`, `condition`）

**工厂方法：**
- `create_manual()` - 创建手动触发器
- `create_timer(schedule)` - 创建定时器触发器
- `create_device_event(entity_id, event_type, condition)` - 创建设备事件触发器

**Condition** - 条件值对象
定义场景执行的前置条件，不可变：

- `entity_id` - 设备实体ID
- `attribute` - 属性名（如 "state", "brightness"）
- `operator` - 操作符（如 "==", ">", "<", "in"）
- `value` - 比较值

**工厂方法：**
- `create_state_equals(entity_id, state)` - 创建状态等于条件
- `create_attribute_equals(entity_id, attribute, value)` - 创建属性等于条件

**Action** - 动作值对象
定义场景执行的具体动作：
- `type` - 动作类型（DEVICE_CONTROL/SCENE_CALL）
- `target` - 目标（设备entity_id或场景ID）
- `command` - 命令（如 "turn_on", "set_brightness"）
- `parameters` - 命令参数（可选）

#### 2.4 领域服务

**ISceneStateMachine** - 场景状态机接口

定义场景状态迁移规则：
- `can_transition()` - 检查状态迁移是否允许
- `get_allowed_transitions()` - 获取允许的状态迁移列表

**ISceneValidator** - 场景验证器接口

定义场景验证规则，确保场景定义的合法性。

#### 2.5 仓储接口

**ISceneRepository** - 场景仓储接口

定义场景持久化操作：
- `save()` - 保存场景
- `find_by_id()` - 根据ID查找
- `find_all()` - 查找所有场景
- `find_by_status()` - 根据状态查找
- `delete()` - 删除场景

**ISceneVersionRepository** - 场景版本仓储接口

定义场景版本的持久化操作（用于版本历史管理）。

---

### 3. Execution（执行）领域

执行领域负责管理场景的执行过程、日志记录和结果跟踪。

#### 3.1 聚合根

**ExecutionAggregate** - 执行聚合根

封装场景执行的核心业务逻辑，维护执行的一致性边界。

**核心属性：**
- `execution_id` - 执行唯一标识
- `context` - 执行上下文值对象
- `retry_policy` - 重试策略值对象
- `record` - 执行记录实体
- `logs` - 执行日志列表

**核心行为：**
- 初始化时自动创建执行记录并发布 `ExecutionStarted` 事件
- `start()` - 开始执行
- `add_log()` - 添加执行日志
- `complete()` - 完成执行（发布成功或失败事件）
- `succeed()` / `fail()` - 标记执行成功/失败
- `retry()` - 重试执行（根据重试策略判断）

**领域事件：**
- `ExecutionStarted` - 执行开始时发布
- `ExecutionSucceeded` - 执行成功时发布
- `ExecutionFailed` - 执行失败时发布

#### 3.2 实体

**ExecutionRecord** - 执行记录实体

记录执行的基本信息：
- `execution_id` - 执行ID
- `scene_id` - 场景ID
- `scene_version` - 场景版本号
- `trigger_source` - 触发源
- `started_at` - 开始时间
- `ended_at` - 结束时间（可选）
- `result` - 执行结果（可选）
- `retry_count` - 重试次数

**核心方法：**
- `complete(result)` - 完成执行并设置结果
- `increment_retry()` - 增加重试次数
- `get_duration()` - 获取执行耗时（秒）
- `is_completed()` - 判断是否已完成

**ExecutionLog** - 执行日志实体

记录执行的详细步骤：
- `log_id` - 日志ID
- `execution_id` - 执行ID
- `step_number` - 步骤序号（必须大于0）
- `action_type` - 动作类型（device_control, scene_call等）
- `target` - 目标（设备entity_id或场景ID）
- `command` - 命令（如 "turn_on", "set_brightness"）
- `parameters` - 命令参数（可选）
- `response` - 响应数据（可选）
- `success` - 是否成功（默认True）
- `error_message` - 错误信息（失败时使用）
- `duration_ms` - 耗时（毫秒，可选）
- `created_at` - 创建时间（自动设置为当前时间）

**核心方法：**
- `mark_success(response, duration_ms)` - 标记为成功
- `mark_failed(error_message, duration_ms)` - 标记为失败

#### 3.3 值对象

**ExecutionContext** - 执行上下文值对象

封装执行的上下文信息，不可变：
- `scene_id` - 场景ID（必填）
- `scene_version` - 场景版本号（必须大于0）
- `trigger_source` - 触发来源（manual, timer, device_event）
- `input_parameters` - 输入参数（可选）
- `call_chain` - 调用链（父场景ID列表，用于场景嵌套，MVP阶段暂不支持）

**方法：**
- `to_dict()` / `from_dict()` - 序列化/反序列化
- `add_to_call_chain(scene_id)` - 添加到调用链（返回新实例）

**ExecutionResult** - 执行结果值对象

封装执行结果，不可变：
- `status` - 执行状态（RUNNING/SUCCESS/FAILED/CANCELLED）
- `error_message` - 错误信息（失败时必填）
- `error_code` - 错误代码（可选）
- `details` - 详细信息（可选）

**RetryPolicy** - 重试策略值对象

定义重试策略，不可变：
- `max_retries` - 最大重试次数（不能为负数）
- `retry_interval` - 重试间隔（timedelta类型）
- `backoff_multiplier` - 退避乘数（用于指数退避，默认1.0，不能小于1.0）

**方法：**
- `should_retry(current_retry_count)` - 判断是否应该重试
- `get_retry_delay(current_retry_count)` - 获取重试延迟时间（支持指数退避）

**工厂方法：**
- `default()` - 创建默认重试策略（重试3次，间隔1秒）
- `no_retry()` - 创建不重试策略

#### 3.4 领域服务

**IWorkflowEngine** - 工作流引擎接口

定义工作流执行逻辑（MVP阶段仅支持顺序执行）：
- `execute()` - 执行工作流
- `execute_action()` - 执行单个动作

**IConcurrencyCoordinator** - 并发协调器接口

定义并发执行的控制逻辑（MVP阶段暂不实现）。

#### 3.5 仓储接口

**IExecutionRepository** - 执行仓储接口

定义执行持久化操作：
- `save()` - 保存执行聚合
- `find_by_id()` - 根据ID查找
- `find_by_scene_id()` - 根据场景ID查找
- `find_all()` - 查找所有执行记录

---

## 领域事件系统

### 事件设计原则

1. **不可变性**：领域事件一旦创建即不可修改
2. **自包含性**：事件包含足够的信息，无需查询其他聚合
3. **时间戳**：所有事件都包含 `occurred_at` 时间戳

### 事件列表

**Device 领域事件：**
- `DeviceRegistered` - 设备注册
- `DeviceStatusChanged` - 设备状态变更

**Scene 领域事件：**
- `ScenePublished` - 场景发布
- `SceneDisabled` - 场景禁用

**Execution 领域事件：**
- `ExecutionStarted` - 执行开始
- `ExecutionSucceeded` - 执行成功
- `ExecutionFailed` - 执行失败

### 事件发布机制

聚合根维护一个内部领域事件列表：
- `get_domain_events()` - 获取所有未发布的事件
- `clear_domain_events()` - 清除已发布的事件（由应用服务调用）

应用服务负责：
1. 调用聚合根的业务方法
2. 获取并发布领域事件
3. 清除已发布的事件

---

## 领域规则与约束

### Device 领域规则

1. **设备ID唯一性**：每个设备必须拥有唯一的 `device_id`
2. **实体ID唯一性**：每个设备必须拥有唯一的 `entity_id`
3. **状态约束**：设备状态只能通过 `enable()`, `disable()`, `mark_as_unavailable()` 方法修改
4. **能力验证**：添加能力时必须验证能力的合法性

### Scene 领域规则

1. **场景ID唯一性**：每个场景必须拥有唯一的 `scene_id`
2. **发布前置条件**：场景必须有至少一个版本才能发布
3. **状态迁移约束**：已禁用的场景不能直接发布，需要先启用
4. **版本递增**：版本号自动递增，不可手动指定
5. **定义完整性**：场景定义必须包含至少一个触发器和至少一个动作

### Execution 领域规则

1. **执行ID唯一性**：每次执行必须拥有唯一的 `execution_id`
2. **状态一致性**：执行状态必须与结果一致
3. **重试限制**：重试次数不能超过重试策略定义的最大值
4. **完成唯一性**：执行只能完成一次

---

## 领域模型关系

### 领域间依赖

```
Scene ──依赖──> Device（通过 entity_id 引用）
Execution ──依赖──> Scene（通过 scene_id 引用）
Execution ──依赖──> Device（执行动作时控制设备）
```

### 聚合边界

1. **DeviceAggregate**：独立的设备聚合，不直接依赖其他聚合
2. **SceneAggregate**：独立的场景聚合，通过ID引用设备，但不持有设备对象
3. **ExecutionAggregate**：独立的执行聚合，通过ID引用场景和设备

---

## 设计原则与最佳实践

### 1. 领域层独立性

- 领域层**不依赖**任何基础设施组件（数据库、消息队列等）
- 领域层**不依赖**应用层或表现层
- 领域层只定义接口，由基础设施层实现

### 2. 聚合设计原则

- **单一职责**：每个聚合只负责一个明确的业务概念
- **最小化边界**：聚合边界尽可能小，只包含必须保持一致的对象
- **通过ID引用**：聚合之间通过ID引用，不直接持有其他聚合的对象

### 3. 值对象设计

- **不可变性**：值对象一旦创建即不可修改
- **自验证**：值对象在创建时验证自身合法性
- **值比较**：值对象通过值进行比较，而非引用

### 4. 领域服务使用场景

- 跨聚合的业务逻辑
- 复杂的计算逻辑
- 不适合放在实体或值对象中的业务规则

### 5. 仓储接口设计

- 只定义接口，不包含实现
- 接口方法名称使用领域语言
- 返回领域对象，而非数据模型

---

## 扩展点

### MVP 阶段限制

1. **场景执行**：仅支持顺序执行，不支持并行或条件分支
2. **场景调用**：暂不支持子场景调用（SCENE_CALL 动作类型已定义但未实现）
3. **并发控制**：暂不实现并发协调器
4. **条件执行**：条件定义已存在，但条件检查逻辑在应用层实现

### 未来扩展方向

1. **复杂工作流**：支持并行执行、条件分支、循环等
2. **场景嵌套**：支持场景调用其他场景
3. **执行优先级**：支持执行优先级管理
4. **执行回滚**：支持执行失败后的回滚机制
5. **执行调度**：支持定时执行、延时执行等

---

## 总结

领域层是 HomeTom 系统的核心，采用领域驱动设计模式，清晰地表达了智能家居系统的业务概念和规则。通过聚合根、值对象、领域服务等概念的运用，确保了业务逻辑的清晰性和可维护性。

三个核心领域（Device、Scene、Execution）各司其职，通过领域事件实现松耦合的领域间通信，为系统的扩展和维护奠定了坚实的基础。

