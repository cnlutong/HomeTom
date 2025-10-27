-- HomeTom 控制器数据库模式（精简版）
-- 仅包含核心表，历史记录后续扩展

-- 设备表
CREATE TABLE IF NOT EXISTS devices (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,          -- 设备类型：light, sensor, switch, etc.
    config JSON,                 -- 设备配置（Pydantic 模型序列化）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 场景表
CREATE TABLE IF NOT EXISTS scenes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    definition JSON NOT NULL,    -- 场景定义（Pydantic 模型序列化）
    is_active BOOLEAN DEFAULT 1, -- 是否激活
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_devices_type ON devices(type);
CREATE INDEX IF NOT EXISTS idx_scenes_active ON scenes(is_active);

