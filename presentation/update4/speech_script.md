
# Presentation Speech Script

## Slide 1: Overview of Work in the Past Two Weeks

**English:**
Hello everyone. I am representing Team 2 to report on our progress for Update 4.
Over the past two weeks, we have worked on two main layers: the Application Layer and the Infrastructure Layer.
In the Application Layer, we implemented three major services. First, the **DeviceService**, which handles device registration, enabling and disabling devices, and state synchronization. Second, the **SceneService**, responsible for scene creation, editing, publishing, and disabling. And third, the **OrchestrationService**, which manages scene execution coordination and workflow management.
In the Infrastructure Layer, we focused on four areas. We built the **Data Persistence** module using SQLAlchemy ORM and Repositories. We implemented an **Event Bus** using asyncio for in-memory pub/sub. We developed **Hardware Communication** support with an HTTP Client and Client Registry. Finally, we established a unified **Logging Module**.

**Chinese:**
大家好。我代表第二小组进行 Update 4 的进度汇报。
在过去的两周里，我们主要在两个层面上开展工作：应用层和基础设施层。
在应用层，我们实现了三个主要服务。首先是**设备服务**，它处理设备注册、启用和禁用设备以及状态同步。其次是**场景服务**，负责场景的创建、编辑、发布和禁用。第三是**编排服务**，负责场景执行协调和工作流管理。
在基础设施层，我们就四个方面进行了工作。我们使用 SQLAlchemy ORM 和仓储模式构建了**数据持久化**模块。我们使用 asyncio 实现了一个内存发布/订阅的**事件总线**。我们开发了支持 HTTP 客户端和客户端注册表的**硬件通信**模块。最后，我们建立了一个统一的**日志模块**。

---

## Slide 2: Demo Video

**English:**
Before we discuss the details, let's watch a demo video.
(Play Video)
The video demonstrates that our system can successfully execute scenes and control devices as expected.

**Chinese:**
在讨论细节之前，让我们看一段演示视频。
(播放视频)
视频演示表明，我们的系统可以按预期成功执行场景并控制设备。

---

## Slide 3: Application Layer - Device Service

**English:**
Let's start with the Application Layer and the **Device Service**.
This service provides unified management of the smart device lifecycle, including registration, state synchronization, and control capabilities. Its core design concept is to act as a mediator that encapsulates device management flows, coordinates domain objects, and publishes events.
Looking at the dependencies diagram on the left, the `DeviceService` interacts with the `IDeviceRepository` for data access, implements the `IDeviceService` interface, and publishes events to the `IEventBus`.
On the right, we have the functional list. The `register_device` method registers a new device, generates a UUID, and publishes an event. The `enable` and `disable` methods toggle the device state and publish status changes. `sync_device_state` delegates to the domain service to sync state. We also have `get_device` to retrieve details, `list_devices` to query lists with filters, and `delete_device` to remove a device.

**Chinese:**
让我们从应用层和**设备服务**开始。
该服务提供智能设备生命周期的统一管理，包括注册、状态同步和控制功能。其核心设计理念是作为一个中介者，封装设备管理流程，协调领域对象并发布事件。
看左边的依赖关系图，`DeviceService` 与 `IDeviceRepository` 交互以进行数据访问，实现了 `IDeviceService` 接口，并将事件发布到 `IEventBus`。
右边是功能列表。`register_device` 方法注册新设备，生成 UUID 并发布事件。`enable`（启用）和 `disable`（禁用）方法切换设备状态并发布状态变更。`sync_device_state` 委托领域服务同步状态。我们还有 `get_device` 用于获取详细信息，`list_devices` 用于带过滤器查询列表，以及 `delete_device` 用于删除设备。

---

## Slide 4: Application Layer - Scene Service

**English:**
Next is the **Scene Service**.
It manages the full lifecycle of scenes and validates scene definitions.
On the left, you can see the Scene State Machine. A scene begins in the **Draft** state after creation. From there, it can be **Published**. A published scene can be **Disabled**. If needed, a disabled scene can be **Republished** back to the Published state.
On the right is the functional list matching this lifecycle. `create_scene` creates a draft. `update_scene` updates the info or definition with validation. `publish_scene` publishes the scene and triggers an event. `disable_scene` disables it, also triggering an event. Additionally, we have `get_scene` to get details or definitions, `list_scenes` to query the list, and `delete_scene` to delete a scene.

**Chinese:**
接下来是**场景服务**。
它管理场景的完整生命周期并验证场景定义。
在左侧，您可以看到场景状态机。场景在创建后处于**草稿**状态。从那里，它可以被**发布**。已发布的场景可以被**禁用**。如果需要，禁用的场景可以**重新发布**回已发布状态。
右侧是与此生命周期相对应的功能列表。`create_scene` 创建草稿。`update_scene` 在验证的情况下更新信息或定义。`publish_scene` 发布场景并触发事件。`disable_scene` 禁用它，同样也会触发事件。此外，我们有 `get_scene` 来获取详细信息或定义，`list_scenes` 来查询列表，以及 `delete_scene` 来删除场景。

---

## Slide 5: Application Layer - Orchestration Service

**English:**
The **Orchestration Service** acts as the coordinator of three contexts, triggers execution, and drives the workflow.
The Execution Flow diagram details the process.
In **Phase 1: Create Scene Executor**, the `OrchestrationService` calls `find_by_id` on the `SceneRepository`, then calls `save` on the `ExecutionRepository` to create a record, and finally calls `publish_all` on the `EventBus`.
In **Phase 2: Execute Scene**, it retrieves the execution record using `find_by_id` from the `ExecutionRepository` and the scene from the `SceneRepository`. Then, it calls `execute` on the `WorkflowEngine` and reports the result via `publish_all` on the `EventBus`.
The functional list includes `trigger_execution` to create the record, `execute_scene` to invoke the engine, and `trigger_and_execute` to do both immediately. It also provides methods to `get_execution` records, get structured `execution_details`, `list_executions`, and `list_executions_for_scene`.

**Chinese:**
**编排服务**充当三个上下文的协调者，触发执行并驱动工作流。
执行流程图详细说明了这个过程。
在**第一阶段：创建场景执行器**中，`OrchestrationService` 调用 `SceneRepository` 的 `find_by_id`，然后调用 `ExecutionRepository` 的 `save` 创建记录，最后调用 `EventBus` 的 `publish_all`。
在**第二阶段：执行场景**中，它使用 `find_by_id` 从 `ExecutionRepository` 获取执行记录，并从 `SceneRepository` 获取场景。然后，它调用 `WorkflowEngine` 的 `execute`，并通过 `EventBus` 的 `publish_all` 报告结果。
功能列表包括 `trigger_execution` 创建记录，`execute_scene` 调用引擎，以及 `trigger_and_execute` 立即执行两者。它还提供了 `get_execution` 获取记录，获取结构化 `execution_details`，`list_executions` 以及 `list_executions_for_scene` 的方法。

---

## Slide 6: Infrastructure Layer - Data Persistence

**English:**
Moving to the Infrastructure Layer, we implemented **Data Persistence** based on SQLAlchemy, supporting both SQLite and PostgreSQL.
As shown in the diagram, our architecture defines three distinct layers.
The top **Domain** layer contains the `DeviceAggregate`, `SceneAggregate`, and `ExecutionAggregate`.
The middle **Mapper** layer contains the corresponding `DeviceMapper`, `SceneMapper`, and `ExecutionMapper`, which handle bidirectional conversion.
The bottom **ORM** layer contains the `DeviceModel`, `SceneModel`, and `ExecutionModel`, which interact with the Database.
The key features are strict **Isolation** between layers, explicit **Mapping** between Domain and ORM objects, and the use of the **Repository** pattern to encapsulate data access.

**Chinese:**
转到基础设施层，我们基于 SQLAlchemy 实现了**数据持久化**，支持 SQLite 和 PostgreSQL。
如图所示，我们的架构定义了三个明显的层级。
顶部的**领域**层包含 `DeviceAggregate`（设备聚合）、`SceneAggregate`（场景聚合）和 `ExecutionAggregate`（执行聚合）。
中间的**映射**层包含相应的 `DeviceMapper`、`SceneMapper` 和 `ExecutionMapper`，负责双向转换。
底部的 **ORM** 层包含 `DeviceModel`、`SceneModel` 和 `ExecutionModel`，它们与数据库进行交互。
主要特性包括层与层之间的严格**隔离**，领域对象和 ORM 对象之间的显式**映射**，以及使用**仓储**模式封装数据访问。

---

## Slide 7: Infrastructure Layer - Event Bus

**English:**
The **Event Bus** decouples context communication and is based on Python's `asyncio.PriorityQueue`.
Its main functionalities include three priority levels: **HIGH**, **NORMAL**, and **LOW**. It has a manageable lifecycle with `start()` and `stop()` methods. It supports both synchronous and asynchronous handlers and is designed with an interface ready for future Message Queue extensions.
The Core Interface Definition shows methods to `publish` a single event with priority, `publish_all` for a batch of events, `subscribe` a handler to an event type, and `unsubscribe` a handler.

**Chinese:**
**事件总线**解耦了上下文通信，基于 Python 的 `asyncio.PriorityQueue`。
其主要功能包括三个优先级：**高**、**普通**和**低**。它具有可管理的生命周期，包括 `start()` 和 `stop()` 方法。它支持同步和异步处理程序，并通过接口设计为支持未来的消息队列扩展。
核心接口定义显示了发布带优先级的单个事件的 `publish` 方法，批量发布事件的 `publish_all` 方法，订阅事件类型的 `subscribe` 方法，以及取消订阅的 `unsubscribe` 方法。

---

## Slide 8: Infrastructure Layer - Hardware Communication

**English:**
The **Hardware Communication** layer abstracts platform differences and provides a unified control interface.
The diagram illustrates the layered design architecture. The **DeviceAggregate** (located in the Domain layer) uses the **HardwareClientRegistry** to find the appropriate client. The Registry delegates to the specific `HttpHardwareClient`, which can communicate with external platforms like Tuya Cloud or Mi Home.
The table details the `HttpHardwareClient`. It handles the specific **Platform** API, manages **Auth** tokens, and provides standard methods like `call` and `get`.

**Chinese:**
**硬件通信**层抽象了平台差异，并提供了统一的控制接口。
图表展示了分层设计架构。**DeviceAggregate**（位于领域层）使用 **HardwareClientRegistry** 来查找合适的客户端。注册表委托给特定的 `HttpHardwareClient`，后者可以与 Tuya Cloud 或 Mi Home 等外部平台进行通信。
表格详细介绍了 `HttpHardwareClient`。它处理特定的**平台** API，管理**认证**令牌，并提供诸如 `call` 和 `get` 等标准方法。

---

## Slide 9: Next Steps

**English:**
Finally, lets look at the next steps.
We have identified four pending tasks.
Task 1 is the **Controllers Layer**, involving REST API implementation, DTOs, and FastAPI configuration.
Task 2 is the **Frontend**, focusing on UI Development.
Task 3 is **E2E Testing**, which covers full business flow verification.
Task 4 is **Documentation**, including API docs, architecture, and guides.
Looking further ahead, we plan to add future capabilities such as sub-scene calls (nested scenes), scene version control, and containerization support.
This report was presented by Team 2 members: Yixue Wang, Linghao Dong, Yang Xiao, Chenxu Liu, and Tong Lu. Thank you for listening.

**Chinese:**
最后，我们来看看接下来的步骤。
我们确定了四个待办任务。
任务 1 是**控制层**，涉及 REST API 实现、DTO 和 FastAPI 配置。
任务 2 是**前端**，专注于 UI 开发。
任务 3 是**端到端测试**，涵盖完整的业务流程验证。
任务 4 是**文档**，包括 API 文档、架构和指南。
展望未来，我们计划增加未来的功能，如子场景调用（嵌套场景）、场景版本控制和容器化支持。
本报告由第二小组成员：王一学、董凌豪、肖扬、刘晨旭和鲁通汇报。谢谢大家的聆听。
