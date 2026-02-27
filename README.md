# Softwareprojekt Smart Home Demo Lab Team 2

*Language: [English](#english-version) | [中文版](#chinese-version)*

---

<a id="english-version"></a>
# English Version

## 1. Project Background and Introduction

**Softwareprojekt Smart Home Demo Lab Team 2** is a smart home automation and orchestration system built using **Domain-Driven Design (DDD)** and **Onion Architecture**. It acts as a high-performance, asynchronous integration layer. The system manages scenes, triggers, and device workflows across different smart home hardware ecosystems. It primarily uses Home Assistant as the hardware abstraction layer.

By isolating the core domain logic from infrastructure, this platform provides a reliable and extensible environment for complex scene management. It ensures that actions, conditional evaluations, and external triggers are handled reliably and concurrently.

## 2. Technical Architecture

The architecture maps strictly to an **Onion/Clean Architecture** paradigm, ensuring that inner domain layers never depend on outer infrastructural layers.

*   **System Context:**
    The entry point is a FastAPI-driven RESTful API (`src/api/routers`), which accepts client requests and delegates them to the **Application Layer**. The Application Layer coordinates interactions between the Domain Layer and Infrastructure components (such as Database ORMs and HTTP Clients).
*   **Component Design:**
    *   **Device Context:** Manages physical and virtual devices (`DeviceAggregate`). It defines capabilities (`Actuators`, `Sensors`) and rules for state synchronization.
    *   **Scene Context:** Contains the configuration for automations. It defines the `Trigger`, `Condition`, and `Action` objects, and uses state machines (`SceneStateMachine`) to manage scene lifecycles.
    *   **Execution Context:** Represents the runtime environment. It includes the `WorkflowEngine` and `ConditionEvaluator`, which create an `ExecutionAggregate` to track success or failure states, retry policies, and logs.
*   **Data Flow:**
    A typical data flow for a scene execution works like this:
    1. A schedule (Cron) or network request (HTTP) triggers the FastAPI endpoint.
    2. `OrchestrationService` generates an `ExecutionAggregate` with a unique ID and calls the `WorkflowEngine`.
    3. `WorkflowEngine` uses `ConditionEvaluator` to sequentially check conditions using the `DeviceManager`.
    4. Upon validation, it issues commands (`ActionType.DEVICE_CONTROL`).
    5. `DeviceManager` delegates the command to the Infrastructure Layer's `HomeAssistantClient` (via `IHardwareClient` interface).
    6. Domain Events (`ActionExecuted`, `ExecutionSucceeded`) are published concurrently to the `InMemoryEventBus`.

## 3. Design Philosophy and Decisions

The architecture of this system addresses common challenges in smart home automation, such as unpredictable network latency, state inconsistencies, and distributed hardware.

*   **Technical Stack:**
    *   **FastAPI and Uvicorn (Asynchronous I/O):** Smart home automation relies heavily on network communication. Communicating with IoT devices causes unpredictable network delays. Traditional synchronous frameworks can run out of threads when handling many long-running requests at the same time. An asynchronous framework, relying on `asyncio`, prevents thread blocking. This keeps the API responsive even during heavy load.
    *   **SQLAlchemy 2.0 (aiosqlite and asyncpg):** To prevent database queries from blocking the application, the entire data persistence layer uses asynchronous operations. SQLAlchemy 2.0 provides native `asyncio` support. The project uses SQLite (`aiosqlite`) for local development, which allows developers to easily switch to PostgreSQL (`asyncpg`) for production environments that need high data throughput.
    *   **Pydantic 2.0:** All incoming configurations and hardware data are validated using Pydantic. This ensures that only correctly formatted data enters the core Domain models.
    *   **APScheduler:** Integrated into the Application Layer, this tool provides asynchronous scheduled triggers (such as `CronTrigger` or `IntervalTrigger`). This removes the need to deploy external message brokers just for task scheduling.
*   **Design Principles and Patterns:**
    *   **Domain-Driven Design (DDD):** Business logic is kept within Aggregates. For example, `SceneAggregate` verifies state transitions, and `ExecutionAggregate` manages its own retry logic. This prevents business rules from mixing with the API controllers.
    *   **Inversion of Control (IoC) and Dependency Injection:** The Domain Layer (`src/domain`) only references abstract base classes and interfaces (such as `IHardwareClient` and `ISceneRepository`). It does not reference databases or network protocols. The Infrastructure Layer (`src/infrastructure`) implements these interfaces. A central Container (`src/application/container.py`) injects these dependencies when the application starts. This approach makes testing easier and maintains strict component boundaries.
    *   **Event-Driven Architecture (EDA):** The system separates core execution tasks from secondary tasks using an In-Memory Event Bus (`src/infrastructure/messaging/in_memory_event_bus.py`). When a scene runs, the system does not wait to write logs or send notifications. Instead, it publishes lightweight Domain Events (such as `ActionExecuted`). Background handlers process these events asynchronously, keeping the main tasks fast.
    *   **Fail-Fast and Graceful Degradation:** The hardware communication layer uses timeouts to limit delays. The `WorkflowEngine` uses the `stop_on_error` setting to control error handling. If a critical task fails, the system stops safely and records the failure state to prevent further errors.

## 4. Implementation Details

The system relies on several core modules that handle dependency injection, data persistence, and task execution.

1.  **Automated System Bootstrap (`SystemBootstrap`):**
    Located in `src/application/bootstrap.py`, this module manages the startup process. It initializes the database and event bus, configures dependency injection, retrieves data from Home Assistant, schedules tasks, and starts ongoing scenes. If any step fails, the startup stops and logs the error.
2.  **Centralized Dependency Injection (`Container`):**
    Located in `src/application/container.py`, the Container manages the lifecycles of system objects (like the Event Bus and Repositories). The FastAPI routers access this container to create the Application Services they need. This provides each HTTP request with a safe, isolated database session.
3.  **Unit of Work and Repository Pattern:**
    In `src/infrastructure/persistence`, the `UnitOfWork` class manages SQLAlchemy database sessions. It maps Aggregates (like `SceneAggregate`) to SQL tables. Database commits and rollbacks happen at the boundary of Application Service methods. This ensures that related database changes succeed or fail together as a single transaction.
4.  **Scene Orchestration Engine (`OrchestrationService`):**
    Located in `src/application/orchestration/OrchestrationService.py`, this service coordinates the Device, Scene, and Execution modules. It adds scheduled tasks to `APScheduler`. When a scene starts, it creates an `ExecutionAggregate`. If a task fails, it uses the `RetryPolicy` to decide whether to try again.
5.  **Deterministic Workflow Execution (`WorkflowEngine`):**
    Located in `src/domain/Execution/services/workflow_engine_impl.py`, this engine executes scenes step-by-step. First, it uses `ConditionEvaluator` to check the rules. Then, it runs the defined actions. It records metrics (like response times and commands sent). If an error occurs, it creates an `<ActionExecuted>` Domain Event and decides whether to stop based on the `stop_on_error` setting.
6.  **Hardware Anti-Corruption Layer (`HomeAssistantClient`):**
    Located in `src/infrastructure/adapters/hardware_adapter.py`, this module communicates with Home Assistant APIs. It acts as a protective layer, converting Home Assistant's specific JSON responses into standard Domain formats (`HAStateObject`, `HardwareResponse`). This protects the core system from changes in external APIs.
7.  **Priority-Based Event Messaging (`InMemoryEventBus`):**
    Located in `src/infrastructure/messaging/in_memory_event_bus.py`, this module uses an `asyncio.PriorityQueue` to manage events. High-priority tasks are processed before low-priority analytical tasks. It also catches errors in individual handlers so that a single failure doesn't stop the entire event system.
8.  **Dynamic Scene Validation (`SceneValidator`):**
    Located in `src/domain/Scene/services/scene_validator_impl.py`, this module checks the rules of a scene before saving them to the database. It checks syntax (like `$system.time` rules) and uses the `DeviceRepository` to ensure the devices actually support the requested actions before allowing the scene to be saved.

## 5. Scalability and Extensibility

*   **Open/Closed Principle:** You can add support for new device manufacturers without changing the core Domain or Application code. Developers only need to create a new `IHardwareClient` (for example, `TuyaHardwareAdapter`) in the `adapters` folder and register it in the Container.
*   **Modular Decoupling:** By using Aggregate roots, the system keeps transactions isolated in small boundaries. Developers can add new notification services or data dashboards by subscribing new background handlers to the Event Bus.

## 6. Environment and Prerequisites

*   **Language:** Python 3.10 or later.
*   **Libraries:** `fastapi` (0.104.0 or later), `uvicorn`, `sqlalchemy` (2.0.0 or later), `pydantic` (2.0.0 or later), `httpx`, `APScheduler`, `pytest`.
*   **Database:** SQLite (default for development) or PostgreSQL (for production using `asyncpg`).
*   **External Integration:** A running instance of Home Assistant (accessible on the network) with a Long-Lived Access Token.

## 7. Build and Setup

1.  **Clone the Repository and Prepare the Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use: venv\Scripts\activate
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment Variables:**
    Set the database connection and your Home Assistant credentials.
    ```bash
    export HA_BASE_URL="http://localhost:8123"
    export HA_TOKEN="your_long_lived_access_token"
    ```
4.  **Run the Development Server:**
    You can use the standard uvicorn command or the provided shell script.
    ```bash
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    # Or use the startup script:
    bash start_dev.sh
    ```

## 8. Development and Debugging

*   **API Exploration:** Go to `http://localhost:8000/docs` to read the OpenAPI (Swagger) documentation. You can use this page to test device configurations and run scenes manually.
*   **Built-in Startup Script:** The project includes a `start_dev.sh` shell script to simplify local development. It finds and stops stale processes using the required ports, then starts:
    1. The Mock Hardware API Server (Port `8123`)
    2. The Backend FastAPI Server (Port `8000`)
    3. The Frontend Vite Development Environment (Port `8080`)
*   **Quick Deployment:** Run `bash start_dev.sh` in your terminal. Make sure your Python virtual environment (`venv`) is active and that you have installed the Node.js packages in the `Front` directory. Press `Ctrl+C` to stop all three services at the same time securely.
*   **Runtime Log Files:** To keep your terminal output clean, the startup script routes the logs from each service into dedicated files in the root folder:
    *   `backend_dev.log`: Records core domain executions, orchestration traffic, and system errors.
    *   `mock_api.log`: Records simulated hardware data and intercepted REST commands.
    *   `frontend.log`: Records frontend compilation events, Hot Module Replacement (HMR) status, and browser warnings.

---

<br><br>

<a id="chinese-version"></a>
# 中文版本

## 1. 项目背景与简介

**Softwareprojekt Smart Home Demo Lab Team 2** 是一个智能家居自动化编排系统。该系统基于**领域驱动设计 (DDD)** 和**洋葱架构 (Onion Architecture)**。它作为一个高性能的异步集成层，管理跨硬件平台的场景、触发条件和设备工作流。系统主要使用 Home Assistant 作为硬件抽象层。

该平台将核心业务逻辑与底层代码隔离，为开发者提供了一个可靠且可扩展的环境。它能够并发、稳定地处理复杂的场景动作、条件评估和外部触发。

## 2. 技术架构

项目的架构严格映射了**洋葱模型 (Onion Architecture) / 整洁架构** 的范式，确保内部的领域层绝对不依赖于外部的基础设施层。

*   **系统上下文 (System Context):**
    系统的入口点是基于 FastAPI 构建的 RESTful API (`src/api/routers`)，它接管客户端请求并委托给**应用层 (Application Layer)**。应用层负责协调领域层与基础设施组件（如数据库 ORM 和 HTTP 客户端）之间的交互。
*   **组件设计:**
    *   **设备上下文:** 管理物理和虚拟设备 (`DeviceAggregate`)。它抽象出各种设备的能力 (`Actuators`, `Sensors`) 并定义状态同步规则。
    *   **场景上下文:** 管理自动化配置。它定义了触发器 (`Trigger`)、条件 (`Condition`) 和动作 (`Action`)，并利用状态机 (`SceneStateMachine`) 管理场景的生命周期。
    *   **执行上下文:** 表示系统运行环境。包含工作流引擎 (`WorkflowEngine`) 和条件评估器 (`ConditionEvaluator`)。它使用执行聚合 (`ExecutionAggregate`) 来记录成功或失败状态、重试策略以及运行日志。
*   **数据流向:**
    一次典型的场景运行流程：
    1. 定时任务 (Cron) 或网络请求 (HTTP) 触发 FastAPI 接口。
    2. 编排服务 (`OrchestrationService`) 生成带有唯一 ID 的执行聚合，并调用工作流引擎。
    3. 工作流引擎 (`WorkflowEngine`) 通过条件评估器和设备管理器检查前置条件。
    4. 校验通过后，系统下发控制指令（如 `ActionType.DEVICE_CONTROL`）。
    5. 设备管理器将指令委托给基础设施层的 `HomeAssistantClient`（通过 `IHardwareClient` 接口防腐层）。
    6. 并发地向内存事件总线 (`InMemoryEventBus`) 发布领域事件（如动作已执行 `ActionExecuted`、执行成功 `ExecutionSucceeded`）。

## 3. 设计思路与决策

该系统的架构设计旨在解决智能家居自动化中的常见问题：网络延迟、状态不同步和硬件多样化。

*   **技术栈选择:**
    *   **FastAPI 和 Uvicorn (异步 I/O):** 智能家居控制依赖于网络通信。与物联网设备通信会产生不可预测的网络延迟。处理多个并发请求时，传统的同步框架会耗尽线程。使用基于 `asyncio` 的异步框架可以避免线程阻塞，确保 API 在高负载下仍能快速响应。
    *   **SQLAlchemy 2.0 (aiosqlite 和 asyncpg):** 为了防止数据库查询阻塞应用程序，整个数据持久层使用异步操作。SQLAlchemy 2.0 提供原生的 `asyncio` 支持。系统在开发环境中使用 SQLite (`aiosqlite`)，在生产环境中可以轻松切换到 PostgreSQL (`asyncpg`)，以支持高吞吐量数据处理。
    *   **Pydantic 2.0:** 系统使用 Pydantic 验证所有传入的配置和硬件设备数据。这确保只有格式正确的数据能够进入核心领域模型。
    *   **APScheduler:** 该工具集成在应用层，提供异步定时任务调度（例如 `CronTrigger` 或 `IntervalTrigger`）。这避免了仅仅为了处理定时任务而部署外部消息队列。
*   **设计原则与模式:**
    *   **领域驱动设计 (DDD):** 业务逻辑保存在聚合中。例如，`SceneAggregate` 负责验证状态，`ExecutionAggregate` 负责管理重试逻辑。这样可以防止业务规则和 API 控制器混合。
    *   **控制反转 (IoC) 与依赖注入:** 领域层 (`src/domain`) 仅引用抽象类和接口（如 `IHardwareClient`）。它不依赖于数据库或网络协议。基础设施层 (`src/infrastructure`) 实现这些接口。系统启动时，由容器 (`src/application/container.py`) 注入这些依赖项。这有助于模块解耦并简化测试。
    *   **事件驱动架构 (EDA):** 系统使用内存事件总线 (`src/infrastructure/messaging/in_memory_event_bus.py`) 将核心任务与次要任务分离。系统执行场景时，不需要等待日志记录或发送通知。引擎只发送轻量级的领域事件（如 `ActionExecuted`）。后台的处理器会异步处理这些事件，保持系统响应迅速。
    *   **快速失败与优雅降级:** 硬件通信层使用超时设置来控制延迟。工作流引擎根据 `stop_on_error` 设置处理错误。如果发生严重故障，系统会安全停止并记录错误，避免产生连锁反应。

## 4. 实现细节

系统使用以下核心模块来处理依赖注入、数据存储和任务执行：

1.  **自动系统启动 (`SystemBootstrap`):**
    位于 `src/application/bootstrap.py`，负责系统的启动流程。它按顺序初始化数据库和事件总线，配置依赖注入，加载 Home Assistant 的设备数据，启动定时任务及常驻场景。如果初始化出错，系统会提示错误并安全停止。
2.  **集中式依赖注入 (`Container`):**
    位于 `src/application/container.py`，容器管理事件总线、硬件客户端和数据仓库等对象的生命周期。FastAPI 路由通过它创建应用服务。这确保每个请求都有独立的、安全的数据库会话。
3.  **工作单元和仓储模式:**
    在 `src/infrastructure/persistence` 中，系统使用 `UnitOfWork` 管理数据库操作。它将聚合对象（如 `SceneAggregate`）保存到数据表。数据库的提交或回滚都在应用方法结束时统一进行。这保证了相关的数据修改能作为一个完整的事务，要么全部成功，要么全部失败。
4.  **场景编排引擎 (`OrchestrationService`):**
    位于 `src/application/orchestration/OrchestrationService.py`，它协调设备和场景。它将定时任务添加到 `APScheduler`。场景运行时，它会创建一个 `ExecutionAggregate` 记录状态。如果任务失败，它会根据 `RetryPolicy` 决定是否重试。
5.  **确定性工作流执行 (`WorkflowEngine`):**
    位于 `src/domain/Execution/services/workflow_engine_impl.py`，引擎负责逐步执行场景。它先用 `ConditionEvaluator` 检查条件，通过后再执行动作。它记录运行日志（如发送的命令和响应时间）。如果遇到错误，它会发出 `<ActionExecuted>` 事件，并根据 `stop_on_error` 设置决定是否继续运行。
6.  **硬件防腐层 (`HomeAssistantClient`):**
    位于 `src/infrastructure/adapters/hardware_adapter.py`，该模块与 Home Assistant API 进行通信。它充当保护层，将外部 API 的任意 JSON 数据转换为标准的内部格式（如 `HAStateObject`）。这可以防止外部 API 的变更影响核心系统。
7.  **基于优先级的事件总线 (`InMemoryEventBus`):**
    位于 `src/infrastructure/messaging/in_memory_event_bus.py`，系统使用 `asyncio.PriorityQueue` 管理事件。高优先级的任务会被优先处理。它还会隔离各个处理器的错误，防止单个错误导致整个事件系统崩溃。
8.  **动态场景校验 (`SceneValidator`):**
    位于 `src/domain/Scene/services/scene_validator_impl.py`。该模块在保存场景前检查规则的正确性。除了检查语法（例如时间条件），它还通过 `DeviceRepository` 检查设备是否真的支持相应的动作指令，从而避免保存无效的场景配置。

## 5. 可扩展性

*   **开闭原则:** 添加新品牌的智能设备不需要修改核心和应用代码。开发者只需在 `adapters` 文件夹中编写新的硬件客户端（例如 `TuyaHardwareAdapter`），并将其注册到容器中即可。
*   **模块解耦:** 使用聚合根的方法将数据处理限制在较小的范围内。开发者可以通过向事件总线订阅新的后台处理器，轻松添加新的功能（如通知服务或数据看板）。

## 6. 环境依赖与提前准备

*   **运行语言:** Python 3.10 或更高版本。
*   **核心第三方库:** `fastapi` (0.104.0 或更高版本), `uvicorn`, `sqlalchemy` (2.0.0 或更高版本), `pydantic` (2.0.0 或更高版本), `httpx`, `APScheduler`, `pytest`。
*   **数据库:** SQLite（默认开发环境）或 PostgreSQL（生产环境，配合 `asyncpg` 使用）。
*   **外部设备:** 局域网或公网中必须有一台运行中的 Home Assistant 服务器，并已生成有效的“长期访问令牌”（Long-Lived Access Token）。

## 7. 构建与设置

1.  **克隆代码库并准备虚拟环境:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows 用户请执行: venv\Scripts\activate
    ```
2.  **安装依赖:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **配置环境变量:**
    设置数据库连接和 Home Assistant 凭证。
    ```bash
    export HA_BASE_URL="http://localhost:8123"
    export HA_TOKEN="your_long_lived_access_token"
    ```
4.  **运行开发服务器:**
    可以使用传统的 uvicorn 命令或提供的启动脚本。
    ```bash
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    # 或直接使用脚本:
    bash start_dev.sh
    ```

## 8. 开发与调试

*   **API 文档:** 访问 `http://localhost:8000/docs` 查看 OpenAPI (Swagger) 接口文档。您可以使用它进行设备调试和运行场景。
*   **内置启动脚本:** 项目根目录下的 `start_dev.sh` 脚本可简化本地开发过程。它在启动前会清理占用端口的旧进程，然后同时启动以下三个服务：
    1. 本地模拟的硬件 API 服务器 (监听端口 `8123`)
    2. 后端核心控制引擎 (监听端口 `8000`)
    3. 基于 Vite 的前端界面 (监听端口 `8080`)
*   **快速部署:** 在终端执行 `bash start_dev.sh` 即可启动服务。在执行前，请确保 Python 虚拟环境已激活，且 `Front` 文件夹下的 Node.js 依赖已完成安装。按下 `Ctrl+C` 即可安全释放所有占用的端口。
*   **运行日志:** 为了防止不同服务的输出在终端内混杂，启动脚本会将各个服务的日志记录到项目根目录的独立文件中：
    *   `backend_dev.log`: 记录核心场景执行、服务调度和系统错误。
    *   `mock_api.log`: 记录硬件接口模拟的网络请求和被拦截的指令。
    *   `frontend.log`: 记录前端界面的编译消息、热更新 (HMR) 状态和警告。
