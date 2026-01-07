# Smart Home Demo Lab - Speech Script
# 智能家居演示实验室 - 演讲稿

---

## Slide 2: Recap - Recent Progress

### English Version

> Before we dive into the technical details, let me give you a **quick recap** of what we've accomplished since the last update.
>
> On the **Frontend** side:
> - We designed and implemented the **Homepage** of our application.
> - We also refactored the **Scene Editor** page with a new n8n-style DAG design.
>
> On the **Backend** side:
> - We developed the **Backend API** following the specification document we defined earlier.
> - We also built a **Mock Hardware API Server** to support testing without real hardware.
>
> For **Infrastructure** improvements:
> - We optimized the **Database** module for better performance.
> - We improved the **Logging** system for easier debugging.
>
> Finally, we fixed various **bugs** to improve overall system quality.

---

### 中文版本

> 在深入技术细节之前，让我先**快速回顾**一下我们自上次更新以来完成的工作。
>
> 在**前端**方面：
> - 我们设计并实现了应用程序的**主页**。
> - 我们还使用新的 n8n 风格 DAG 设计重构了**场景编辑器**页面。
>
> 在**后端**方面：
> - 我们按照之前定义的规范文档开发了**后端 API**。
> - 我们还构建了一个**模拟硬件 API 服务器**来支持无需真实硬件的测试。
>
> 在**基础设施**改进方面：
> - 我们优化了**数据库**模块以提高性能。
> - 我们改进了**日志**系统以便于调试。
>
> 最后，我们修复了多个 **Bug** 以提高整体系统质量。

---

## Slide 3: Backend System - Architecture & Functionality

### English Version

> Now let's talk about the **Backend System Architecture and Functionality**.
>
> On the left side, we focus on the **Core Functionality** our API provides:
> - First, **Device Lifecycle Management**. This is about a unified CRUD interface for all device types — Equipment, Sensors, and Scene Parameters. Whether you're adding a new smart light or updating a sensor, the operations are consistent and well-defined.
> - Second, the **Automation Engine**. It follows a classic Trigger-Condition-Action model described in our API specification. Users can create rules that respond to device state changes, and dynamically enable or disable these automations as needed.
>
> On the right, we highlight the **Architecture Design**:
> - We adhere to **Strict RESTful Standards**. All URLs are resource-oriented, like `/api/devices/equipment`, and we use standard HTTP verbs — GET, POST, PUT, DELETE.
> - Every API response follows a **Standardized Envelope** format: a `code` for status, a `message` for human-readable feedback, and `data` for the actual payload.
> - For **Security**, we implement stateless Bearer Token Authentication, exactly as specified in the documentation.

---

### 中文版本

> 现在让我们来讲一下**后端系统的架构和功能**。
>
> 在左边，我们关注的是 API 提供的**核心功能**：
> - 首先是**设备生命周期管理**。这是一个统一的 CRUD 接口，用于处理所有设备类型——设备、传感器和场景参数。无论是添加新的智能灯还是更新传感器，操作都是一致且明确定义的。
> - 其次是**自动化引擎**。它遵循 API 规范中描述的经典触发器-条件-动作模型。用户可以创建对设备状态变化做出响应的规则，并根据需要动态启用或禁用这些自动化。
>
> 在右边，我们展示的是**架构设计**：
> - 我们遵守**严格的 RESTful 标准**。所有 URL 都是面向资源的，比如 `/api/devices/equipment`，我们使用标准的 HTTP 动词——GET、POST、PUT、DELETE。
> - 每个 API 响应都遵循**标准化信封**格式：`code` 表示状态，`message` 提供人类可读的反馈，`data` 包含实际数据载荷。
> - 在**安全性**方面，我们实现了无状态的 Bearer Token 认证，完全按照文档规范。

---

## Slide 3: Backend System - FastAPI Implementation

### English Version

> Moving to the next slide, let's look at **how we implement** this backend using FastAPI.
>
> On the left, we cover the **Technology Stack and Patterns**:
> - We chose **FastAPI** as our framework because of its native async I/O support — critical for handling multiple concurrent device requests efficiently. It also provides auto-generated OpenAPI documentation, which is very helpful for our frontend integration.
> - We use **Modular Routing** with FastAPI's `APIRouter`. This lets us separate endpoints by domain — `/devices` in one router, `/automations` in another. This makes the codebase clean and maintainable.
> - For data validation, we rely on **Pydantic Models** to ensure all incoming request payloads strictly match the expected schema.
>
> On the right, we describe our **Implementation Logic**:
> - We leverage **Dependency Injection** heavily. Auth checks and service layer access are all injected, making the code easier to test and mock.
> - **Type Safety** is enforced throughout. Pydantic ensures that if a payload doesn't match the expected format, an automatic validation error is returned to the client.
>
> This implementation strategy allows us to build a robust, maintainable API that aligns precisely with our specification document.

---

### 中文版本

> 接下来，让我们看看**如何使用 FastAPI 实现**这个后端。
>
> 在左边，我们介绍**技术栈和设计模式**：
> - 我们选择 **FastAPI** 作为框架，因为它原生支持异步 I/O——这对于高效处理多个并发设备请求至关重要。它还提供自动生成的 OpenAPI 文档，这对前端集成非常有帮助。
> - 我们使用 FastAPI 的 `APIRouter` 实现**模块化路由**。这让我们可以按领域分离端点——`/devices` 放在一个路由器中，`/automations` 放在另一个中。这使代码库保持清晰和可维护。
> - 对于数据验证，我们依赖 **Pydantic Models** 确保所有传入的请求载荷严格匹配预期的模式。
>
> 在右边，我们描述**实现逻辑**：
> - 我们大量使用**依赖注入**。认证检查和服务层访问都是注入的，使代码更易于测试和模拟。
> - 全程强制执行**类型安全**。Pydantic 确保如果载荷不匹配预期格式，会自动向客户端返回验证错误。
>
> 这种实现策略使我们能够构建一个健壮、可维护的 API，并且与我们的规范文档精确对齐。

---

## Mock Hardware API Server - Introduction / Background



## Slide 1: Overview & Architecture

### English Version

> Now I'd like to introduce the **Mock Hardware API Server** module that we developed.
>
> This module simulates the Home Assistant REST API to provide hardware interfaces for our development and testing workflow. Instead of relying on actual hardware devices during development, we can use this mock server to test our smart home control logic.
>
> Let me highlight the **key features**:
> - First, it provides a **fully HA-compatible API**, meaning our backend can connect to it exactly as it would connect to a real Home Assistant instance.
> - It supports **14 different device types**, including lights, switches, covers, climate controls, locks, and more.
> - All device states are stored using **JSON persistence**, so the data survives server restarts.
> - We built it with **FastAPI**, which gives us automatic Swagger documentation.
> - And of course, it includes **token authentication** to simulate the real security model.
>
> Looking at the **architecture** on the right: we have three layers.
> - The **API layer** handles incoming requests through FastAPI endpoints with token authentication.
> - The **Storage layer** uses a JsonDeviceStore class with memory cache for fast access.
> - Finally, device data is persisted to **JSON files** organized by device domain.

---

### 中文版本

> 现在我来介绍一下我们开发的**模拟硬件 API 服务器**模块。
>
> 这个模块模拟了 Home Assistant 的 REST API，为我们的开发和测试流程提供硬件接口。在开发过程中，我们不需要依赖真实的硬件设备，可以使用这个模拟服务器来测试智能家居控制逻辑。
>
> 让我介绍一下**主要特性**：
> - 首先，它提供**完全兼容 HA 的 API**，这意味着我们的后端可以像连接真实 Home Assistant 实例一样连接它。
> - 它支持 **14 种不同的设备类型**，包括灯、开关、窗帘、空调、门锁等。
> - 所有设备状态都使用 **JSON 持久化**存储，因此数据在服务器重启后仍然保留。
> - 我们使用 **FastAPI** 构建，它自动提供 Swagger 文档。
> - 当然，它也包含**令牌认证**来模拟真实的安全模型。
>
> 看右边的**架构图**：我们有三层。
> - **API 层**通过 FastAPI 端点和令牌认证处理传入请求。
> - **存储层**使用 JsonDeviceStore 类，配合内存缓存实现快速访问。
> - 最后，设备数据按设备域组织，持久化到 **JSON 文件**中。

---

## Slide 2: API Endpoints

### English Version

> Moving to the second slide, let's look at the **API endpoints** we implemented.
>
> On the left, you can see the **core endpoints**. These follow the Home Assistant REST API specification:
> - GET `/api/states` returns all device states
> - We can get, set, or delete individual devices by their entity ID
> - The `/api/services` endpoint allows us to call device services like `turn_on` or `set_temperature`
> - And we can fire events through the events endpoint
>
> We also added some **helper endpoints** for testing purposes:
> - `/test/reload` to reload all device JSON files
> - `/test/service-calls` to view the history of service calls
> - And filtering devices by domain
>
> On the right side, you can see the **10 device domains** we support, along with their available services. For example, lights support turn on, turn off, and toggle; climate devices support setting temperature and HVAC mode; and so on.
>
> This mock server has been essential for our development workflow, allowing us to test the complete device control pipeline without physical hardware.

---

### 中文版本

> 接下来看第二页，让我们了解一下我们实现的 **API 端点**。
>
> 在左边，你可以看到**核心端点**。这些遵循 Home Assistant REST API 规范：
> - GET `/api/states` 返回所有设备状态
> - 我们可以通过实体 ID 获取、设置或删除单个设备
> - `/api/services` 端点允许我们调用设备服务，比如 `turn_on` 或 `set_temperature`
> - 我们还可以通过 events 端点触发事件
>
> 我们还添加了一些用于测试的**辅助端点**：
> - `/test/reload` 用于重新加载所有设备 JSON 文件
> - `/test/service-calls` 用于查看服务调用历史
> - 以及按域筛选设备
>
> 在右侧，你可以看到我们支持的 **10 种设备域**及其可用服务。例如，灯支持开、关和切换；空调设备支持设置温度和 HVAC 模式；等等。
>
> 这个模拟服务器对我们的开发流程至关重要，让我们能够在没有物理硬件的情况下测试完整的设备控制流程。

---

**Estimated speaking time for Mock Hardware slides: 2-3 minutes**
**模拟硬件幻灯片预计演讲时间：2-3 分钟**

---

## Slide 6: Development Roadmap

### English Version

> Finally, let me share our **Development Roadmap** for the coming weeks.
>
> **This week**, we are focusing on adapting our backend to the new frontend design. Our Scene Editor now uses an **n8n-style DAG (Directed Acyclic Graph)** approach. This means we need to:
> - Optimize our automation JSON format to support this new graph-based structure.
> - Update the backend execution logic so the automation engine can correctly interpret and run DAG-based workflows.
>
> **Next week**, our priority shifts to **End-to-End Testing**. We will run full integration tests across all layers — from the frontend scene editor, through the backend APIs, down to the mock hardware server — to validate complete user workflows.
>
> Our **Goal** is clear: by the next Update presentation, we aim to deliver a **working, demonstrable version** of the complete system.

---

### 中文版本

> 最后，让我分享一下我们接下来几周的**开发计划**。
>
> **本周**，我们专注于让后端适配前端的新设计。我们的场景编辑器现在采用了类似 **n8n 的 DAG（有向无环图）** 设计。这意味着我们需要：
> - 优化自动化 JSON 格式以支持这种新的图结构。
> - 更新后端执行逻辑，使自动化引擎能够正确解析和运行基于 DAG 的工作流。
>
> **下周**，我们的重点转向**端到端测试**。我们将在所有层级运行完整的集成测试——从前端场景编辑器，到后端 API，再到模拟硬件服务器——以验证完整的用户工作流程。
>
> 我们的**目标**很明确：在下次 Update 演示时，我们的目标是交付一个**可运行、可演示的完整系统版本**。

---

**Total estimated speaking time: 4-5 minutes**
**总预计演讲时间：4-5 分钟**
