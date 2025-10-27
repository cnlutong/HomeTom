# HomeTom 控制器部署指南

## 一、开发环境部署

### 1.1 前置要求

- Python 3.10+
- pip

### 1.2 安装步骤

```bash
# 1. 进入项目目录
cd controller

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件

# 4. 启动服务
python main.py
```

或使用启动脚本：

```bash
# Linux/Mac
chmod +x start.sh
./start.sh

# Windows
start.bat
```

### 1.3 访问服务

- API 文档：http://localhost:8000/docs
- ReDoc 文档：http://localhost:8000/redoc
- WebSocket：ws://localhost:8000/ws

## 二、生产环境部署

### 2.1 使用 Gunicorn + Uvicorn

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --daemon
```

### 2.2 使用 Systemd（Linux）

创建服务文件 `/etc/systemd/system/hometom-controller.service`：

```ini
[Unit]
Description=HomeTom Controller
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/controller
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable hometom-controller
sudo systemctl start hometom-controller
sudo systemctl status hometom-controller
```

### 2.3 使用 Docker

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 创建数据和日志目录
RUN mkdir -p data logs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "main.py"]
```

构建和运行：

```bash
# 构建镜像
docker build -t hometom-controller .

# 运行容器
docker run -d \
  --name hometom-controller \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e HAL_ENDPOINT=http://hal-server:8080 \
  hometom-controller
```

### 2.4 使用 Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  controller:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - HAL_ENDPOINT=http://hal:8080
      - LOG_LEVEL=INFO
    restart: unless-stopped
    depends_on:
      - hal

  hal:
    image: your-hal-image
    ports:
      - "8080:8080"
    restart: unless-stopped
```

启动：

```bash
docker-compose up -d
```

## 三、反向代理配置

### 3.1 Nginx

创建配置文件 `/etc/nginx/sites-available/hometom`:

```nginx
upstream hometom_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # HTTP API
    location / {
        proxy_pass http://hometom_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://hometom_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/hometom /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3.2 HTTPS 配置（Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 四、环境配置

### 4.1 生产环境变量

```bash
# HAL 配置
HAL_ENDPOINT=http://your-hal-server:8080
HAL_TIMEOUT=10
HAL_MAX_CONNECTIONS=20
HAL_MAX_KEEPALIVE=10

# 数据库配置
DATABASE_PATH=/var/lib/hometom/controller.db

# 日志配置
LOG_LEVEL=WARNING
LOG_FILE=/var/log/hometom/controller.log

# 安全配置（建议添加）
# API_KEY=your-secret-key
# ALLOWED_ORIGINS=https://your-webui.com
```

### 4.2 文件权限

```bash
# 创建数据目录
sudo mkdir -p /var/lib/hometom
sudo mkdir -p /var/log/hometom

# 设置权限
sudo chown -R your_user:your_user /var/lib/hometom
sudo chown -R your_user:your_user /var/log/hometom
sudo chmod 755 /var/lib/hometom
sudo chmod 755 /var/log/hometom
```

## 五、监控和维护

### 5.1 健康检查

```bash
# 基础健康检查
curl http://localhost:8000/api/system/health

# 详细系统状态
curl http://localhost:8000/api/system/status
```

### 5.2 日志管理

```bash
# 查看实时日志
tail -f logs/controller.log

# 使用 logrotate 管理日志
sudo cat > /etc/logrotate.d/hometom << EOF
/var/log/hometom/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

### 5.3 数据库备份

```bash
# 备份数据库
sqlite3 data/controller.db ".backup data/controller.db.backup"

# 定时备份（添加到 crontab）
0 2 * * * sqlite3 /var/lib/hometom/controller.db ".backup /var/lib/hometom/backup/controller_$(date +\%Y\%m\%d).db"
```

## 六、性能优化

### 6.1 Worker 数量

推荐配置：

```bash
workers = (2 × CPU 核心数) + 1

# 例如 4 核 CPU
workers = 9
```

### 6.2 数据库优化

```sql
-- 定期优化数据库
VACUUM;
ANALYZE;
```

### 6.3 连接池调优

根据设备数量调整：

```python
# 小规模（<50 设备）
HAL_MAX_CONNECTIONS=10
HAL_MAX_KEEPALIVE=5

# 中等规模（50-200 设备）
HAL_MAX_CONNECTIONS=20
HAL_MAX_KEEPALIVE=10
```

## 七、安全加固

### 7.1 防火墙配置

```bash
# 只开放必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 7.2 限制访问

在 Nginx 中添加：

```nginx
# 限制请求速率
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api {
    limit_req zone=api burst=20;
}

# IP 白名单
allow 192.168.1.0/24;
deny all;
```

## 八、故障排查

### 8.1 常见问题

**问题 1：服务无法启动**

```bash
# 检查端口占用
sudo lsof -i :8000

# 检查日志
tail -n 100 logs/controller.log
```

**问题 2：HAL 连接失败**

```bash
# 测试 HAL 连接
curl http://hal-server:8080/health

# 检查网络
ping hal-server
```

**问题 3：数据库锁定**

```bash
# 关闭其他进程
fuser data/controller.db

# 重建数据库
rm data/controller.db
python -c "from infrastructure.database.connection import init_database; import asyncio; asyncio.run(init_database())"
```

### 8.2 调试模式

```bash
# 启用调试日志
export LOG_LEVEL=DEBUG
python main.py
```

## 九、升级指南

### 9.1 升级步骤

```bash
# 1. 备份数据
cp data/controller.db data/controller.db.backup

# 2. 停止服务
sudo systemctl stop hometom-controller

# 3. 更新代码
git pull origin main

# 4. 更新依赖
pip install -r requirements.txt --upgrade

# 5. 数据库迁移（如需要）
# python migrate.py

# 6. 启动服务
sudo systemctl start hometom-controller

# 7. 验证
curl http://localhost:8000/api/system/status
```

### 9.2 回滚

```bash
# 1. 停止服务
sudo systemctl stop hometom-controller

# 2. 回滚代码
git checkout <previous-version>

# 3. 恢复数据库
cp data/controller.db.backup data/controller.db

# 4. 启动服务
sudo systemctl start hometom-controller
```

## 十、总结

本部署指南涵盖了从开发到生产的完整部署流程。建议：

1. **开发环境**：使用 `python main.py` 直接启动
2. **生产环境**：使用 Gunicorn + Systemd + Nginx
3. **容器化**：使用 Docker Compose
4. **监控**：定期检查健康状态和日志
5. **备份**：每日自动备份数据库

