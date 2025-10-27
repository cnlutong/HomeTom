# HomeTom 控制器架构文档

## 一、整体架构

### 1.1 架构图

```
                            ┌─────────────────────┐
                            │     WebUI Client    │
                            │   (Browser/App)     │
                            └──────────┬──────────┘
                                       │
                           HTTP/REST   │   WebSocket
                                       │
                    ┌──────────────────┴──────────────────┐
                    │         API Layer (FastAPI)         │
                    │  ┌──────────┬──────────┬─────────┐ │
                    │  │ Devices  │ Scenes   │ System  │ │
                    │  │ Routes   │ Routes   │ Routes  │ │
                    │  └──────────┴──────────┴─────────┘ │
                    │  ┌─────────────────────────────┐   │
                    │  │   WebSocket Handler         │   │
                    │  │   (Real-time Push)          │   │
                    │  └─────────────────────────────┘   │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────┴──────────────────────┐
                    │      Application Services           │
                    │  ┌──────────┬──────────┬─────────┐ │
                    │  │ Device   │ Scene    │ Event   │ │
                    │  │ Service  │ Service  │ Bus     │ │
                    │  └──────────┴──────────┴─────────┘ │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────┴──────────────────────┐
                    │         Domain Layer                │
                    │  ┌─────────────┬────────────────┐   │
                    │  │  Entities   │ Scene Engine   │   │
                    │  │  - Device   │  - Parser      │   │
                    │  │  - Scene    │  - Conditions  │   │
                    │  │             │  - Executor    │   │
                    │  │             │  - Scheduler   │   │
                    │  └─────────────┴────────────────┘   │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────┴──────────────────────┐
                    │      Infrastructure Layer           │
                    │  ┌──────────┬──────────┬─────────┐ │
                    │  │ HAL      │ Database │ State   │ │
                    │  │ Adapter  │ (SQLite) │ Manager │ │
                    │  │ (httpx)  │          │(Memory) │ │
                    │  └──────────┴──────────┴─────────┘ │
                    └──────────────┬──────────────────────┘
                                   │
                            ┌──────┴──────┐
                            │   HAL API   │
                            │  (Hardware) │
                            └─────────────┘
```

### 1.2 架构原则

1. **洋葱架构（Onion Architecture）**
   - 依赖方向：外层依赖内层
   - 核心领域层不依赖外部框架
   - 易于测试和维护

2. **关注点分离**
   - API 层：处理 HTTP/WebSocket 通信
   - 应用层：业务逻辑编排
   - 领域层：核心业务规则
   - 基础设施层：技术实现细节

3. **依赖倒置**
   - 通过接口/抽象类定义契约
   - 使用依赖注入提供实现

## 二、核心模块设计

### 2.1 API 层

**职责**：处理 HTTP 请求和 WebSocket 连接

**组件**：
- `devices.py`: 设备管理 API
- `scenes.py`: 场景管理 API
- `system.py`: 系统状态 API
- `websocket.py`: WebSocket 实时推送

**特点**：
- 使用 Pydantic 模型验证请求
- 统一错误处理中间件
- 支持 CORS

### 2.2 应用服务层

**职责**：业务逻辑编排和事件协调

#### 2.2.1 事件总线（简化版）

使用观察者模式实现：

```python
class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable):
        """订阅事件"""
        
    async def publish(self, event_type: str, data: Dict):
        """发布事件（非阻塞）"""
```

**优势**：
- 代码简洁（<50 行）
- 非阻塞发布
- 支持同步/异步处理器

#### 2.2.2 设备服务

**核心方法**：
- `get_device_state()`: 获取设备状态（优先内存）
- `control_device()`: 控制设备并更新状态
- `sync_device_state()`: 强制从 HAL 同步

**事件发布**：
- `device_state_changed`
- `device_added`
- `device_removed`

#### 2.2.3 场景服务

**核心方法**：
- `create_scene()`: 创建场景并注册调度器
- `trigger_scene()`: 手动/自动触发场景
- `activate_scene()`: 激活/停用场景

**事件发布**：
- `scene_triggered`
- `scene_completed`
- `scene_failed`

### 2.3 领域层

#### 2.3.1 实体（Entities）

使用 Pydantic 模型：

```python
class Device(BaseModel):
    id: str
    name: str
    type: str
    config: Optional[Dict[str, Any]]

class Scene(BaseModel):
    id: str
    name: str
    definition: SceneDefinition
    is_active: bool
```

#### 2.3.2 场景引擎

**1. 解析器（Parser）**

验证场景 JSON 定义：

```python
class SceneParser:
    @staticmethod
    def parse(definition_data: Dict) -> SceneDefinition:
        """使用 Pydantic 验证"""
```

**2. 条件评估器（策略模式）**

```python
# 策略接口
class Condition(ABC):
    @abstractmethod
    async def evaluate(self, context: Dict) -> bool:
        pass

# 具体策略
class DeviceStateCondition(Condition):
    async def evaluate(self, context: Dict) -> bool:
        # 评估设备状态
        
class TimeRangeCondition(Condition):
    async def evaluate(self, context: Dict) -> bool:
        # 评估时间范围

# 工厂模式
class ConditionFactory:
    _registry: Dict[str, type] = {
        "device_state": DeviceStateCondition,
        "time_range": TimeRangeCondition,
    }
    
    @classmethod
    def create(cls, condition_data: Dict) -> Condition:
        """根据类型创建条件实例"""
```

**优势**：
- 易于扩展（注册新条件类型）
- 符合开闭原则
- 单元测试友好

**3. 执行器（Executor）**

```python
class SceneExecutor:
    async def execute_scene(self, scene: Scene) -> ExecutionResult:
        # 1. 准备上下文
        # 2. 评估条件
        # 3. 执行动作序列
        # 4. 返回结果
```

**4. 调度器（Scheduler）**

使用 APScheduler：

```python
class SceneScheduler:
    def register_scene(self, scene: Scene, callback: Callable):
        """注册定时任务"""
        
    def unregister_scene(self, scene_id: str):
        """取消定时任务"""
```

### 2.4 基础设施层

#### 2.4.1 HAL 适配层

**连接池配置**（优化）：

```python
class HALClient:
    def __init__(self):
        self._client = httpx.AsyncClient(
            base_url=config.HAL_ENDPOINT,
            timeout=config.HAL_TIMEOUT,
            limits=httpx.Limits(
                max_connections=config.HAL_MAX_CONNECTIONS,
                max_keepalive_connections=config.HAL_MAX_KEEPALIVE
            ),
            transport=httpx.AsyncHTTPTransport(
                retries=config.HAL_RETRY_TIMES
            )
        )
```

**核心方法**：
- `get_device_state()`: 获取设备状态
- `control_device()`: 控制设备
- `health_check()`: 健康检查

#### 2.4.2 数据库层

**精简表结构**（优化）：

```sql
-- 仅保留核心表
CREATE TABLE devices (...);
CREATE TABLE scenes (...);

-- 历史记录表后续扩展
```

**仓储模式**：

```python
class DeviceRepository:
    async def get_all() -> List[Device]
    async def save(device: Device)
    
class SceneRepository:
    async def get_all(active_only: bool) -> List[Scene]
    async def save(scene: Scene)
```

#### 2.4.3 状态管理器

**纯内存设计**（优化）：

```python
class StateManager:
    def __init__(self):
        self._states: Dict[str, DeviceState] = {}
        self._lock = asyncio.Lock()
    
    async def get_state(self, device_id: str) -> DeviceState:
        """线程安全的状态获取"""
        
    async def set_state(self, device_id: str, state: DeviceState):
        """线程安全的状态设置"""
```

**优势**：
- 无需状态同步
- 启动时从 HAL 加载
- 高性能（内存访问）

## 三、数据流

### 3.1 设备控制流程

```
WebUI → API → DeviceService → HALClient → HAL
                    ↓
              StateManager ← (更新状态)
                    ↓
               EventBus → (发布事件)
                    ↓
            WebSocket → (推送给前端)
```

### 3.2 场景触发流程

```
定时器/手动触发 → SceneService
                       ↓
                  SceneExecutor
                       ↓
              ConditionEvaluator (评估条件)
                       ↓
              HALClient (执行动作)
                       ↓
              EventBus (发布完成事件)
                       ↓
              WebSocket (推送给前端)
```

### 3.3 设备状态变化流程

```
HAL 推送/轮询 → StateManager
                     ↓
                 EventBus
                     ↓
            SceneEngine (检查触发器)
                     ↓
            WebSocket (推送给前端)
```

## 四、依赖注入

### 4.1 设计原则

- 单例模式：HALClient, StateManager, EventBus
- 每请求：DeviceService, SceneService
- 每连接：数据库连接

### 4.2 实现方式

```python
# 全局单例
_hal_client: HALClient = None

def get_hal_client() -> HALClient:
    global _hal_client
    if _hal_client is None:
        if config.TESTING:
            _hal_client = MockHALClient()  # 测试模式
        else:
            _hal_client = HALClient()
    return _hal_client

# FastAPI 依赖
def get_device_service(
    db: Connection = Depends(get_db)
) -> DeviceService:
    return DeviceService(
        device_repo=DeviceRepository(db),
        hal_client=get_hal_client(),
        state_manager=get_state_manager(),
        event_bus=get_event_bus()
    )
```

## 五、错误处理

### 5.1 异常层次

```
ControllerException (基类)
    ├── HALCommunicationError
    ├── DeviceNotFoundError
    ├── SceneNotFoundError
    ├── SceneExecutionError
    ├── SceneDefinitionError
    ├── DatabaseError
    └── StateManagerError
```

### 5.2 统一处理

```python
@app.exception_handler(ControllerException)
async def controller_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": exc.message}
    )
```

## 六、配置管理

使用 Pydantic Settings：

```python
class Settings(BaseSettings):
    HAL_ENDPOINT: str
    DATABASE_PATH: str
    LOG_LEVEL: str
    TESTING: bool = False
    
    model_config = SettingsConfigDict(env_file=".env")

config = Settings()
```

## 七、测试策略

### 7.1 单元测试

- 使用 MockHALClient
- 测试领域逻辑
- 测试条件评估器

### 7.2 集成测试

- 测试完整的 API 流程
- 测试场景执行
- 测试事件传播

## 八、性能优化

1. **连接池**：HAL 客户端使用连接池
2. **内存缓存**：设备状态缓存到内存
3. **异步 I/O**：全异步架构
4. **事件非阻塞**：事件发布使用 create_task

## 九、扩展性

### 9.1 新增条件类型

```python
class CustomCondition(Condition):
    async def evaluate(self, context: Dict) -> bool:
        # 自定义逻辑
        
# 注册
ConditionFactory.register("custom", CustomCondition)
```

### 9.2 新增动作类型

在 SceneExecutor 中添加新的动作处理逻辑。

### 9.3 多 HAL 支持

创建 HALClientManager 管理多个 HAL 实例。

## 十、安全考虑

1. **API 认证**：后续可添加 JWT 认证
2. **输入验证**：使用 Pydantic 验证所有输入
3. **SQL 注入**：使用参数化查询
4. **CORS 配置**：生产环境限制域名

## 十一、部署建议

### 11.1 开发环境

```bash
python main.py
```

### 11.2 生产环境

```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### 11.3 Docker 部署

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 十二、监控和日志

- 使用 Python logging 模块
- 日志级别：DEBUG/INFO/WARNING/ERROR
- 关键操作记录：场景执行、设备控制、异常

## 十三、总结

本架构设计遵循以下原则：

1. ✅ **轻量化**：无重型框架，SQLite 单文件
2. ✅ **可靠性**：事件驱动 + 错误处理
3. ✅ **简单**：代码清晰，易于理解
4. ✅ **易实现**：模块化设计，逐步开发
5. ✅ **可扩展**：策略模式、工厂模式支持扩展

核心优化点：
- 简化事件总线（观察者模式）
- 状态管理优化（纯内存）
- 精简数据库表
- 策略模式条件评估器
- HAL 客户端连接池配置
- 统一错误处理
- 依赖注入改进

