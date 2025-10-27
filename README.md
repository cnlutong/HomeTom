# HomeTom

<img width="249" height="264" alt="75c685e169fae2d11706d3d06af5ab36" src="https://github.com/user-attachments/assets/fc280e62-298f-4553-821a-2701eda85fec" />

### 看板
https://fb.tonglu.de/

受 Home Assistant 启发的智能家居控制器层架构。

## 📋 功能特性

- ✅ RESTful API（设备管理、场景管理）
- ✅ WebSocket 实时推送
- ✅ 场景自动化引擎（支持复杂条件和定时触发）
- ✅ HAL 适配层（支持多种通信方式）
- ✅ 轻量级数据持久化（SQLite）
- ✅ 事件驱动架构

## 🏗️ 架构设计

采用洋葱架构（Onion Architecture）：

```
┌─────────────────────────────────────────────────────────┐
│                      接口层 (API Layer)                  │
│  FastAPI REST Endpoints + WebSocket Handler            │
├─────────────────────────────────────────────────────────┤
│                   应用服务层 (Application)               │
│  Device Service | Scene Service | Event Bus             │
├─────────────────────────────────────────────────────────┤
│                   领域层 (Domain Layer)                  │
│  Scene Engine (策略模式) | Entities                     │
├─────────────────────────────────────────────────────────┤
│                 基础设施层 (Infrastructure)              │
│  HAL Adapter | SQLite Repo | State Manager              │
└─────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd controller
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 并根据实际情况修改：

```bash
HAL_ENDPOINT=http://localhost:8080
DATABASE_PATH=./data/controller.db
LOG_LEVEL=INFO
```

### 3. 启动服务

```bash
python main.py
```

服务将在 `http://0.0.0.0:8000` 启动。

### 4. 访问文档

浏览器访问：
- API 文档：http://localhost:8000/docs
- ReDoc 文档：http://localhost:8000/redoc

## 📡 API 示例

### 设备管理

```bash
# 获取所有设备
curl http://localhost:8000/api/devices

# 获取设备状态
curl http://localhost:8000/api/devices/light_01/state

# 控制设备
curl -X POST http://localhost:8000/api/devices/light_01/control \
  -H "Content-Type: application/json" \
  -d '{"command": {"state": "on", "brightness": 80}}'
```

### 场景管理

```bash
# 创建场景
curl -X POST http://localhost:8000/api/scenes \
  -H "Content-Type: application/json" \
  -d '{
    "id": "scene_001",
    "name": "回家模式",
    "definition": {
      "triggers": [{
        "type": "time",
        "cron": "0 18 * * *"
      }],
      "actions": [{
        "type": "device_control",
        "device_id": "light_01",
        "command": {"state": "on", "brightness": 80}
      }]
    }
  }'

# 手动触发场景
curl -X POST http://localhost:8000/api/scenes/scene_001/trigger
```

### WebSocket 连接

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('事件类型:', data.type);
  console.log('事件数据:', data.data);
};

// 发送心跳
setInterval(() => ws.send('ping'), 30000);
```

## 🎬 场景定义格式

```json
{
  "triggers": [
    {
      "type": "device_state",
      "device_id": "door_sensor_01",
      "condition": {
        "operator": "eq",
        "attribute": "state",
        "value": "open"
      }
    },
    {
      "type": "time",
      "cron": "0 18 * * *"
    }
  ],
  "conditions": {
    "operator": "and",
    "items": [
      {
        "type": "device_state",
        "device_id": "light_sensor_01",
        "condition": {
          "operator": "lt",
          "attribute": "brightness",
          "value": 50
        }
      },
      {
        "type": "time_range",
        "start": "18:00",
        "end": "23:00"
      }
    ]
  },
  "actions": [
    {
      "type": "device_control",
      "device_id": "light_01",
      "command": {"state": "on", "brightness": 80}
    },
    {
      "type": "delay",
      "seconds": 5
    }
  ]
}
```

### 支持的触发器类型

- `device_state`: 设备状态变化触发
- `time`: 定时触发（cron 表达式）
- `manual`: 手动触发

### 支持的条件类型

- `device_state`: 设备状态条件
- `time_range`: 时间范围条件
- 条件组合：`and` / `or`

### 支持的动作类型

- `device_control`: 控制设备
- `delay`: 延迟执行

### 支持的运算符

- `eq`: 等于
- `ne`: 不等于
- `gt`: 大于
- `ge`: 大于等于
- `lt`: 小于
- `le`: 小于等于

## 📂 项目结构

```
controller/
├── main.py                      # FastAPI 应用入口
├── config.py                    # 配置管理
├── dependencies.py              # 依赖注入
├── exceptions.py                # 统一异常定义
├── api/                         # 接口层
│   ├── routes/                  # REST 路由
│   └── websocket.py            # WebSocket 处理器
├── application/                 # 应用服务层
│   ├── event_bus.py            # 事件总线（简化版）
│   ├── device_service.py       # 设备服务
│   └── scene_service.py        # 场景服务
├── domain/                      # 领域层
│   ├── entities/               # 实体模型
│   └── scene_engine/           # 场景引擎
│       ├── parser.py           # 解析器
│       ├── conditions.py       # 条件评估器（策略模式）
│       ├── executor.py         # 执行器
│       └── scheduler.py        # 调度器
└── infrastructure/              # 基础设施层
    ├── hal/                    # HAL 适配层
    │   ├── client.py           # httpx 客户端（连接池配置）
    │   └── models.py           # HAL 数据模型
    ├── database/               # 数据持久化
    │   ├── schema.sql          # 数据库模式
    │   ├── connection.py       # SQLite 连接
    │   └── repositories.py     # 仓储实现
    └── state_manager.py        # 内存状态管理（优化版）
```

## 🔧 核心设计优化

1. **简化事件总线**：使用观察者模式，代码量减少 80%
2. **状态管理优化**：纯内存，应用重启时从 HAL 重新加载
3. **精简数据库**：仅保留核心表（devices, scenes）
4. **策略模式条件评估器**：易扩展，符合开闭原则
5. **HAL 客户端连接池**：优化性能，防止连接泄漏
6. **统一错误处理**：中间件级别的异常处理
7. **依赖注入改进**：支持测试模式，易于单元测试

## 🧪 测试

```bash
# 启用测试模式（使用 Mock HAL）
export TESTING=true
python main.py
```

## 📊 性能指标

- 设备数量：<50 个（小规模家庭）
- 场景数量：无限制
- WebSocket 连接：支持多客户端
- 响应时间：<100ms（本地 HAL）

## 🔮 扩展点

- 插件系统：自定义 Action 和 Condition 类型
- 多 HAL 支持：适配多个 HAL 实例
- MQTT 集成：支持 MQTT 协议设备
- 场景优先级和冲突检测
- 历史记录表（scene_executions, device_state_history）

## 📝 许可证

MIT License

