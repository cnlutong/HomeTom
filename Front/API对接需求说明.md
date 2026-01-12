# 智能家居项目 - 后端API对接需求说明


---

## 1. 设备管理 API（优先级：高）

### 1.1 获取设备列表

#### GET /api/devices/equipment
获取所有设备列表

**请求参数：**
- 无

**请求头：**
```
Authorization: Bearer {token}x
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "device_001",
      "label": "Main light",
      "icon": "💡",
      "type": "equipment",
      "capability": "onOff",
      "status": "online",
      "currentState": {
        "onOff": false,
        "brightness": 0
      },
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**错误响应：**
```json
{
  "code": 401,
  "message": "Unauthorized",
  "data": null
}
```

---

#### GET /api/devices/sensors
获取所有传感器列表

**请求参数：**
- 无

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "sensor_001",
      "label": "Motion",
      "icon": "📡",
      "type": "sensor",
      "capability": "motion",
      "status": "online",
      "currentState": {
        "detected": false,
        "lastDetected": "2024-01-01T10:00:00Z"
      },
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

#### GET /api/devices/scene-parameters
获取所有场景参数列表

**请求参数：**
- 无

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "scene_param_001",
      "label": "Time",
      "icon": "⏰",
      "type": "scene",
      "capability": "time",
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z"
    },
    {
      "id": "scene_param_002",
      "label": "Temperature",
      "icon": "🌡️",
      "type": "scene",
      "capability": "temperature",
      "unit": "°C",
      "minValue": -15,
      "maxValue": 45,
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z"
    },
    {
      "id": "scene_param_003",
      "label": "Humidity",
      "icon": "💧",
      "type": "scene",
      "capability": "humidity",
      "unit": "%",
      "minValue": 0,
      "maxValue": 100,
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### 1.2 添加设备

#### POST /api/devices/equipment
添加新设备

**请求体：**
```json
{
  "label": "New Light",
  "icon": "💡",
  "type": "equipment",
  "capability": "onOff"
}
```

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 201,
  "message": "Device created successfully",
  "data": {
    "id": "device_002",
    "label": "New Light",
    "icon": "💡",
    "type": "equipment",
    "capability": "onOff",
    "status": "offline",
    "currentState": {
      "onOff": false
    },
    "createdAt": "2024-01-01T12:00:00Z",
    "updatedAt": "2024-01-01T12:00:00Z"
  }
}
```

**错误响应：**
```json
{
  "code": 400,
  "message": "Validation failed: label is required",
  "data": null
}
```

---

#### POST /api/devices/sensors
添加新传感器

**请求体：**
```json
{
  "label": "New Sensor",
  "icon": "📡",
  "type": "sensor",
  "capability": "motion"
}
```

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 201,
  "message": "Sensor created successfully",
  "data": {
    "id": "sensor_002",
    "label": "New Sensor",
    "icon": "📡",
    "type": "sensor",
    "capability": "motion",
    "status": "offline",
    "currentState": {
      "detected": false
    },
    "createdAt": "2024-01-01T12:00:00Z",
    "updatedAt": "2024-01-01T12:00:00Z"
  }
}
```

---

#### POST /api/devices/scene-parameters
添加新场景参数

**请求体：**
```json
{
  "label": "New Parameter",
  "icon": "⏰",
  "type": "scene",
  "capability": "time"
}
```

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 201,
  "message": "Scene parameter created successfully",
  "data": {
    "id": "scene_param_004",
    "label": "New Parameter",
    "icon": "⏰",
    "type": "scene",
    "capability": "time",
    "createdAt": "2024-01-01T12:00:00Z",
    "updatedAt": "2024-01-01T12:00:00Z"
  }
}
```

---

### 1.3 更新设备

#### PUT /api/devices/equipment/:id
更新设备信息

**路径参数：**
- `id` (string): 设备ID

**请求体：**
```json
{
  "label": "Updated Light",
  "icon": "💡"
}
```

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "Device updated successfully",
  "data": {
    "id": "device_001",
    "label": "Updated Light",
    "icon": "💡",
    "type": "equipment",
    "capability": "onOff",
    "status": "online",
    "currentState": {
      "onOff": false
    },
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T13:00:00Z"
  }
}
```

**错误响应：**
```json
{
  "code": 404,
  "message": "Device not found",
  "data": null
}
```

---

#### PUT /api/devices/sensors/:id
更新传感器信息

**路径参数：**
- `id` (string): 传感器ID

**请求体：**
```json
{
  "label": "Updated Sensor",
  "icon": "📡"
}
```

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "Sensor updated successfully",
  "data": {
    "id": "sensor_001",
    "label": "Updated Sensor",
    "icon": "📡",
    "type": "sensor",
    "capability": "motion",
    "status": "online",
    "currentState": {
      "detected": false
    },
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T13:00:00Z"
  }
}
```

---

#### PUT /api/devices/scene-parameters/:id
更新场景参数信息

**路径参数：**
- `id` (string): 场景参数ID

**请求体：**
```json
{
  "label": "Updated Parameter",
  "icon": "⏰"
}
```

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "Scene parameter updated successfully",
  "data": {
    "id": "scene_param_001",
    "label": "Updated Parameter",
    "icon": "⏰",
    "type": "scene",
    "capability": "time",
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T13:00:00Z"
  }
}
```

---

### 1.4 删除设备

#### DELETE /api/devices/equipment/:id
删除设备

**路径参数：**
- `id` (string): 设备ID

**请求头：**
```
Authorization: Bearer {token}
```

**响应格式：**
```json
{
  "code": 200,
  "message": "Device deleted successfully",
  "data": null
}
```

**错误响应：**
```json
{
  "code": 404,
  "message": "Device not found",
  "data": null
}
```

---

#### DELETE /api/devices/sensors/:id
删除传感器

**路径参数：**
- `id` (string): 传感器ID

**请求头：**
```
Authorization: Bearer {token}
```

**响应格式：**
```json
{
  "code": 200,
  "message": "Sensor deleted successfully",
  "data": null
}
```

---

#### DELETE /api/devices/scene-parameters/:id
删除场景参数

**路径参数：**
- `id` (string): 场景参数ID

**请求头：**
```
Authorization: Bearer {token}
```

**响应格式：**
```json
{
  "code": 200,
  "message": "Scene parameter deleted successfully",
  "data": null
}
```

---

## 2. 自动化配置管理 API（优先级：高）

### 2.1 创建自动化配置

#### POST /api/automations
创建新的自动化配置

**请求体：**
```json
{
  "automationId": "auto_morning_routine",
  "name": "Morning Routine",
  "description": "Automation with 2 trigger(s), 1 condition(s), and 3 action(s)",
  "isEnabled": true,
  "triggers": [
    {
      "type": "deviceState",
      "deviceId": "sensor_motion_01",
      "capability": "motion",
      "state": "detected"
    }
  ],
  "conditions": [
    {
      "type": "time",
      "time": "07:00"
    },
    {
      "type": "deviceState",
      "deviceId": "sensor_temp_01",
      "capability": "temperature",
      "state": ">= 20"
    }
  ],
  "actions": [
    {
      "type": "deviceCommand",
      "deviceId": "device_main_light_01",
      "capability": "onOff",
      "value": true
    },
    {
      "type": "deviceCommand",
      "deviceId": "device_conditioner_01",
      "capability": "temperature",
      "value": 26
    }
  ]
}
```

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 201,
  "message": "Automation created successfully",
  "data": {
    "automationId": "auto_morning_routine",
    "name": "Morning Routine",
    "description": "Automation with 2 trigger(s), 1 condition(s), and 3 action(s)",
    "isEnabled": true,
    "triggers": [
      {
        "type": "deviceState",
        "deviceId": "sensor_motion_01",
        "capability": "motion",
        "state": "detected"
      }
    ],
    "conditions": [
      {
        "type": "time",
        "time": "07:00"
      },
      {
        "type": "deviceState",
        "deviceId": "sensor_temp_01",
        "capability": "temperature",
        "state": ">= 20"
      }
    ],
    "actions": [
      {
        "type": "deviceCommand",
        "deviceId": "device_main_light_01",
        "capability": "onOff",
        "value": true
      },
      {
        "type": "deviceCommand",
        "deviceId": "device_conditioner_01",
        "capability": "temperature",
        "value": 26
      }
    ],
    "createdAt": "2024-01-01T12:00:00Z",
    "updatedAt": "2024-01-01T12:00:00Z",
    "createdBy": "user_001"
  }
}
```

**错误响应：**
```json
{
  "code": 400,
  "message": "Validation failed: automationId already exists",
  "data": null
}
```

---

### 2.2 获取自动化配置列表

#### GET /api/automations
获取用户的所有自动化配置列表

**查询参数：**
- `page` (number, 可选): 页码，默认1
- `pageSize` (number, 可选): 每页数量，默认10
- `isEnabled` (boolean, 可选): 筛选启用/禁用的自动化

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "automationId": "auto_morning_routine",
        "name": "Morning Routine",
        "description": "Automation with 2 trigger(s), 1 condition(s), and 3 action(s)",
        "isEnabled": true,
        "triggerCount": 2,
        "conditionCount": 1,
        "actionCount": 3,
        "createdAt": "2024-01-01T12:00:00Z",
        "updatedAt": "2024-01-01T12:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 10,
      "total": 1,
      "totalPages": 1
    }
  }
}
```

---

#### GET /api/automations/:id
获取单个自动化配置详情

**路径参数：**
- `id` (string): 自动化ID (automationId)

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "automationId": "auto_morning_routine",
    "name": "Morning Routine",
    "description": "Automation with 2 trigger(s), 1 condition(s), and 3 action(s)",
    "isEnabled": true,
    "triggers": [
      {
        "type": "deviceState",
        "deviceId": "sensor_motion_01",
        "capability": "motion",
        "state": "detected"
      }
    ],
    "conditions": [
      {
        "type": "time",
        "time": "07:00"
      },
      {
        "type": "deviceState",
        "deviceId": "sensor_temp_01",
        "capability": "temperature",
        "state": ">= 20"
      }
    ],
    "actions": [
      {
        "type": "deviceCommand",
        "deviceId": "device_main_light_01",
        "capability": "onOff",
        "value": true
      },
      {
        "type": "deviceCommand",
        "deviceId": "device_conditioner_01",
        "capability": "temperature",
        "value": 26
      }
    ],
    "createdAt": "2024-01-01T12:00:00Z",
    "updatedAt": "2024-01-01T12:00:00Z",
    "createdBy": "user_001"
  }
}
```

**错误响应：**
```json
{
  "code": 404,
  "message": "Automation not found",
  "data": null
}
```

---

### 2.3 更新自动化配置

#### PUT /api/automations/:id
更新现有自动化配置

**路径参数：**
- `id` (string): 自动化ID (automationId)

**请求体：**
```json
{
  "name": "Updated Morning Routine",
  "description": "Updated description",
  "isEnabled": false,
  "triggers": [
    {
      "type": "deviceState",
      "deviceId": "sensor_motion_01",
      "capability": "motion",
      "state": "detected"
    }
  ],
  "conditions": [
    {
      "type": "time",
      "time": "08:00"
    }
  ],
  "actions": [
    {
      "type": "deviceCommand",
      "deviceId": "device_main_light_01",
      "capability": "onOff",
      "value": true
    }
  ]
}
```

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "Automation updated successfully",
  "data": {
    "automationId": "auto_morning_routine",
    "name": "Updated Morning Routine",
    "description": "Updated description",
    "isEnabled": false,
    "triggers": [
      {
        "type": "deviceState",
        "deviceId": "sensor_motion_01",
        "capability": "motion",
        "state": "detected"
      }
    ],
    "conditions": [
      {
        "type": "time",
        "time": "08:00"
      }
    ],
    "actions": [
      {
        "type": "deviceCommand",
        "deviceId": "device_main_light_01",
        "capability": "onOff",
        "value": true
      }
    ],
    "createdAt": "2024-01-01T12:00:00Z",
    "updatedAt": "2024-01-01T14:00:00Z",
    "createdBy": "user_001"
  }
}
```

---

### 2.4 删除自动化配置

#### DELETE /api/automations/:id
删除自动化配置

**路径参数：**
- `id` (string): 自动化ID (automationId)

**请求头：**
```
Authorization: Bearer {token}
```

**响应格式：**
```json
{
  "code": 200,
  "message": "Automation deleted successfully",
  "data": null
}
```

**错误响应：**
```json
{
  "code": 404,
  "message": "Automation not found",
  "data": null
}
```

---

## 3. 自动化执行 API（优先级：中）

### 3.1 执行自动化

#### POST /api/automations/:id/execute
立即执行指定的自动化

**路径参数：**
- `id` (string): 自动化ID (automationId)

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "Automation executed successfully",
  "data": {
    "executionId": "exec_001",
    "automationId": "auto_morning_routine",
    "status": "running",
    "startedAt": "2024-01-01T15:00:00Z",
    "triggeredBy": "manual",
    "actions": [
      {
        "actionId": "action_001",
        "deviceId": "device_main_light_01",
        "status": "pending",
        "result": null
      }
    ]
  }
}
```

**错误响应：**
```json
{
  "code": 400,
  "message": "Automation is disabled",
  "data": null
}
```

---

### 3.2 启用/禁用自动化

#### POST /api/automations/:id/enable
启用自动化（自动执行）

**路径参数：**
- `id` (string): 自动化ID (automationId)

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "Automation enabled successfully",
  "data": {
    "automationId": "auto_morning_routine",
    "isEnabled": true,
    "updatedAt": "2024-01-01T15:00:00Z"
  }
}
```

---

#### POST /api/automations/:id/disable
禁用自动化

**路径参数：**
- `id` (string): 自动化ID (automationId)

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "Automation disabled successfully",
  "data": {
    "automationId": "auto_morning_routine",
    "isEnabled": false,
    "updatedAt": "2024-01-01T15:00:00Z"
  }
}
```

---

### 3.3 获取执行历史

#### GET /api/automations/:id/executions
获取自动化的执行历史

**路径参数：**
- `id` (string): 自动化ID (automationId)

**查询参数：**
- `page` (number, 可选): 页码，默认1
- `pageSize` (number, 可选): 每页数量，默认10
- `startDate` (string, 可选): 开始日期，格式 YYYY-MM-DD
- `endDate` (string, 可选): 结束日期，格式 YYYY-MM-DD

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "executionId": "exec_001",
        "automationId": "auto_morning_routine",
        "status": "completed",
        "triggeredBy": "trigger",
        "startedAt": "2024-01-01T15:00:00Z",
        "completedAt": "2024-01-01T15:00:05Z",
        "duration": 5000,
        "actionsExecuted": 3,
        "actionsSucceeded": 3,
        "actionsFailed": 0
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 10,
      "total": 1,
      "totalPages": 1
    }
  }
}
```

---

## 4. 设备状态实时更新 API（优先级：中）

### 4.1 获取设备状态

#### GET /api/devices/:id/status
获取单个设备状态

**路径参数：**
- `id` (string): 设备ID

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "device_001",
    "status": "online",
    "currentState": {
      "onOff": true,
      "brightness": 80
    },
    "lastUpdated": "2024-01-01T15:00:00Z"
  }
}
```

---

#### GET /api/devices/status
批量获取所有设备状态

**查询参数：**
- `type` (string, 可选): 设备类型筛选 (equipment/sensor)
- `status` (string, 可选): 状态筛选 (online/offline)

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "devices": [
      {
        "id": "device_001",
        "status": "online",
        "currentState": {
          "onOff": true,
          "brightness": 80
        },
        "lastUpdated": "2024-01-01T15:00:00Z"
      },
      {
        "id": "sensor_001",
        "status": "online",
        "currentState": {
          "detected": false,
          "lastDetected": "2024-01-01T10:00:00Z"
        },
        "lastUpdated": "2024-01-01T15:00:00Z"
      }
    ],
    "summary": {
      "total": 2,
      "online": 2,
      "offline": 0
    }
  }
}
```

---

### 4.2 WebSocket 实时推送

#### WebSocket /ws/devices/status
实时推送设备状态变化

**连接URL：**
```
ws://api.example.com/ws/devices/status?token={token}
```

**连接参数：**
- `token` (string): 认证token

**消息格式（服务器推送）：**
```json
{
  "type": "device_status_update",
  "timestamp": "2024-01-01T15:00:00Z",
  "data": {
    "deviceId": "device_001",
    "status": "online",
    "currentState": {
      "onOff": true,
      "brightness": 80
    }
  }
}
```

**消息格式（客户端订阅）：**
```json
{
  "action": "subscribe",
  "deviceIds": ["device_001", "device_002"]
}
```

**消息格式（客户端取消订阅）：**
```json
{
  "action": "unsubscribe",
  "deviceIds": ["device_001"]
}
```

---

## 5. 用户认证和权限 API（优先级：中）

### 5.1 用户注册

#### POST /api/auth/register
用户注册

**请求体：**
```json
{
  "username": "user123",
  "email": "user@example.com",
  "password": "password123",
  "confirmPassword": "password123"
}
```

**请求头：**
```
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 201,
  "message": "User registered successfully",
  "data": {
    "userId": "user_001",
    "username": "user123",
    "email": "user@example.com",
    "createdAt": "2024-01-01T12:00:00Z"
  }
}
```

**错误响应：**
```json
{
  "code": 400,
  "message": "Validation failed: email already exists",
  "data": null
}
```

---



### 5.5 刷新Token

#### POST /api/auth/refresh
刷新访问token

**请求体：**
```json
{
  "refreshToken": "refresh_token_here"
}
```

**请求头：**
```
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "Token refreshed successfully",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 3600
  }
}
```

---

## 6. 数据同步 API（优先级：低）

### 6.1 上传本地数据

#### POST /api/sync/upload
上传本地数据到服务器

**请求体：**
```json
{
  "sidebarSections": [
    {
      "title": "Equipment List",
      "items": [
        {
          "icon": "💡",
          "label": "Main light",
          "type": "equipment"
        }
      ]
    }
  ],
  "automations": [
    {
      "automationId": "auto_001",
      "name": "Test Automation",
      "triggers": [],
      "conditions": [],
      "actions": []
    }
  ]
}
```

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "Data uploaded successfully",
  "data": {
    "sidebarSections": {
      "synced": 3,
      "failed": 0
    },
    "automations": {
      "synced": 1,
      "failed": 0
    },
    "syncedAt": "2024-01-01T15:00:00Z"
  }
}
```

---

### 6.2 下载服务器数据

#### GET /api/sync/download
从服务器下载数据

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "sidebarSections": [
      {
        "title": "Equipment List",
        "items": [
          {
            "icon": "💡",
            "label": "Main light",
            "type": "equipment"
          }
        ]
      }
    ],
    "automations": [
      {
        "automationId": "auto_001",
        "name": "Test Automation",
        "triggers": [],
        "conditions": [],
        "actions": []
      }
    ],
    "downloadedAt": "2024-01-01T15:00:00Z"
  }
}
```

---

## API对接优先级建议

### 第一阶段（核心功能）
✅ **自动化执行API** - 运行、启用/禁用自动化
4. ✅ **设备状态API** - 获取设备实时状态


### 第二阶段（增强功能）
1. ✅ **设备管理API** - 获取设备列表、添加/编辑/删除设备
2. ✅ **自动化配置管理API** - 保存、获取、删除自动化配置

### 第三阶段（完善功能）

6. ✅ **数据同步API** - 本地与服务器数据同步

---

## 通用响应格式

所有API响应遵循统一格式：

**成功响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

**错误响应：**
```json
{
  "code": 400,
  "message": "Error message",
  "data": null
}
```

**HTTP状态码说明：**
- `200` - 成功
- `201` - 创建成功
- `400` - 请求参数错误
- `401` - 未授权
- `403` - 无权限
- `404` - 资源不存在
- `500` - 服务器错误

---

## 认证说明

除登录和注册接口外，所有API请求都需要在请求头中包含认证token：

```
Authorization: Bearer {token}
```

Token通过登录接口获取，有效期为1小时。Token过期后需要使用刷新token接口获取新的token。

---

## 注意事项

1. **时间格式**：所有时间字段使用ISO 8601格式 (YYYY-MM-DDTHH:mm:ssZ)
2. **分页**：列表接口支持分页，默认每页10条
3. **错误处理**：前端需要统一处理错误响应，显示友好的错误提示
4. **数据验证**：后端需要验证所有必填字段和数据类型
5. **安全性**：所有API请求使用HTTPS，敏感数据需要加密传输



Next, let me show our current  front-end page .
This visio n .wa are  mainly focuses on UI optimization of the page .
and, we've decided to add an initial loading page.
First, when a user  enters the web, they will see t he initial loading page.
This is just like  a homepage. That is will be the  users to better manage and view running automation scenarios.



to p here ,xyou can see the local time and the service time .
This is the server time, the time of the cloud server. This enhances the realism of the interaction.
In real-world scenarios, the logs generated by the system background are usually also based on server time.
And also you can see the current location.


the next you can see the basic information on the page .
Here is the number of all our automation scenarios.
Then is the number of all the devices we are currently using.
Here you can see the current temperature and humidity.
we use the free Open-Meteo plugin to obtain the current location and weather information for that location.


Here it is the scene list .we can see the detailed information for each scenario.
You can click this button to activate or deactivate a scenario.
If you don't need this scenario, you can click the button to delete it.
Clicking the edit button will take you to the scenario editing page.
This page you can edit the automation scenario again.
------------------
Compared to the previous version, we haven't added many new features.
The version we are mainly focus on the ui optimization of this page.
At the same time, we redesigned the scene editor page using a new n8n-style DAG design.
A  (DAG) is a logical structure consisting of nodes (tasks) and directed edges (connections).
It is used to ensure that data flows in a specified direction without creating infinite loops.
It clarifies the sequential dependencies between tasks.
It guarantees that automated processes can be executed in a deterministic order or processed in parallel.
----------------
The first change is .we are hided the components in the left sidebar and the action bo x. The canvas area will increase。
that  is mean .the user will have the good view to create the scenario.

you can click the plus button open the component list.
First, you need to select the component you want to add.
And the next ,you can click the component move to the canvas.
At this point, the canvas will connect the components according to the logic.
If you want to change the way with the  components connect.
You can double click the line . You can directly delect the connection.
The  Users can also place the component anywhere.

-----
Currently, some logic in this part still needs modification.
The next version will demonstrate the complete connection logic.
------


We can see that we've added an "Execute" button in the canvas.
Clicking it ,the system can saves the current automation scenario.
Returning to the homepage, we can see the current automation scenario.
The system will run automatically depending on the type of automation.



Therefore, we've added trigger types here. You can choose manual or automatic triggering.
Later, we will add conditions for automatic triggering, such as based on a specific time point or time period.
This will be updated in the next version.

So this is the current progress of the front-end.
The next version will connect to the back-end API, using real data for simulation. We will add the new fuction.Save the scene's logs and operation process.This feature will be at the bottom of the list.







--liu

we are presenting the Mock Hardware API Server. We built this tool to solve the "hardware dependency" issue. Its core function is to simulate the Home Assistant REST API, allowing us to develop and test interfaces without needing physical hardware

look at the left. The core strength of this server is its Full Compatibility. We essentially replicated the standard Home Assistant endpoints, so it behaves exactly like the real system.

Building on that, we achieved Broad Coverage, supporting 14 different device types, ranging from simple lights to complex HVAC systems.

More importantly, to ensure stability, we implemented JSON Persistence. This means every state change is saved in real-time, so never lose the data, even if the server restarts.

To ensure performance, we adopted a layered architecture.

First is the API Layer: All requests enter through FastAPI and pass through Token Auth for security verification, ensuring only legitimate requests get through.

Second is the Storage Layer: This is the core. The JsonDeviceStore handles business logic , supported by a Memory Cache  to ensure ultra-fast response times.

Finally, all data is stored locally as JSON files. This design is both lightweight and easy to debug.



----wang 
Moving to the second slide, let's look at the API endpoints we implemented.

On the left, you can see the core endpoints. These follow the Home Assistant REST API specification:
- GET /api/states returns all device states
- We can get, set, or delete individual devices by their entity ID
- The /api/services endpoint allows us to call device services like turn_on or set_temperature
- And we can fire events through the events endpoint

We also added some helper endpoints for testing purposes:
- /test/reload to reload all device JSON files
- /test/service-calls to view the history of service calls
- And filtering devices by domain

On the right side, you can see the 10 device domains we support, along with their available services. For example, lights support turn on, turn off, and toggle; climate devices support setting temperature and HVAC mode; and so on.

This mock server has been essential for our development workflow, allowing us to test the complete device control pipeline without physical hardware.