# Dreamina 自动化注册程序

> 基于 DrissionPage 的 Dreamina 账号自动化注册工具，支持临时邮箱、代理、批量注册和自动推送功能。

## 目录

- [功能特性](#功能特性)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [Docker 部署](#docker-部署)
- [配置说明](#配置说明)
- [使用指南](#使用指南)
- [API 文档](#api-文档)
- [架构与开发指南](#架构与开发指南)
- [常见问题](#常见问题)
- [安全说明](#安全说明)
- [免责声明](#免责声明)

## 功能特性

- 🤖 **全自动注册**：完整的 16 步自动化注册流程
- 📧 **临时邮箱支持**：集成 MoeMail 和 TempMailHub 两种临时邮箱服务
- 🔐 **随机密码生成**：自动生成 10-15 位强密码
- 🌐 **代理支持**：支持 HTTP 和 SOCKS5 代理（含认证）
- 📦 **批量注册**：支持一次性注册多个账号
- 👻 **无头模式**：可选的浏览器无头模式，适合服务器环境
- 🚀 **自动推送**：注册完成后自动推送 keys 到 Gptload 系统
- 💾 **数据保存**：自动保存 SessionID 和账号信息
- 🔌 **API 服务**：提供 HTTP 接口进行注册任务管理

## 环境要求

- **Python**: 3.12 或更高版本
- **包管理器**: [uv](https://github.com/astral-sh/uv)
- **操作系统**: Windows / Linux / macOS
- **浏览器**: Chromium 内核浏览器（DrissionPage 自动管理）

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/gloryhry/Dreamina-register
cd Dreamina-register
```

### 2. 安装依赖

使用 uv 安装项目依赖：

```powershell
uv sync
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

### 4. 运行程序

#### 方式一：启动 API 服务 (推荐)

```powershell
# 进入 src 目录运行
cd src
uv run uvicorn server:app --host 0.0.0.0 --port 8000
```

#### 方式二：运行命令行脚本

```powershell
uv run python src/main.py
```

## Docker 部署

项目支持通过 Docker 容器化部署，适合服务器环境和持续集成场景。

### 使用 Docker Compose（推荐）

这是最简单的部署方式，一键启动所有服务。

#### 1. 准备配置文件

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件，填写必要的 API Key
# 特别注意：HEADLESS 会在容器中自动设为 true
```

#### 2. 启动服务

```bash
# 构建并启动服务（后台运行）
docker-compose up -d

# 查看运行状态
docker-compose ps

# 查看实时日志
docker-compose logs -f
```

#### 3. 管理服务

```bash
# 停止服务
docker-compose down

# 重新构建（代码更新后）
docker-compose up -d --build

# 查看服务健康状态
docker-compose ps
```

#### 4. 数据持久化

- 账号数据保存在 `./data/` 目录（自动挂载）
- 配置通过 `.env` 文件加载（运行时挂载）

### 使用预构建镜像

从 GitHub Container Registry (GHCR) 拉取官方镜像：

```bash
# 拉取最新镜像
docker pull ghcr.io/gloryhry/dreamina-register:latest

# 运行容器
docker run -d \
  --name dreamina-register \
  -p 8000:8000 \
  --env-file .env \
  --shm-size=2g \
  ghcr.io/gloryhry/dreamina-register:latest
```

### 手动构建镜像

如需自定义构建：

```bash
# 构建镜像
docker build -t dreamina-register:custom .

# 运行容器
docker run -d \
  --name dreamina-register \
  -p 8000:8000 \
  --env-file .env \
  --shm-size=2g \
  dreamina-register:custom
```

### Docker 部署注意事项

> [!IMPORTANT]
> **共享内存大小**：Chromium 需要较大的共享内存，建议设置 `--shm-size=2g` 或在 docker-compose.yml 中配置 `shm_size: '2gb'`。

> [!NOTE]
> **镜像大小**：由于包含 Chromium 浏览器，完整镜像约 1GB+。首次拉取/构建需要较长时间。

## 配置说明

### 基础配置 (.env)

```ini
# 临时邮箱类型：moemail 或 tempmailhub
TEMPMAIL_TYPE=moemail

# MoeMail配置（当TEMPMAIL_TYPE=moemail时必填）
MOEMAIL_API_KEY=your_api_key
MOEMAIL_BASE_URL=https://moemail.985100.xyz

# TempMailHub配置（当TEMPMAIL_TYPE=tempmailhub时必填）
TEMPMAILHUB_API_KEY=your_api_key
TEMPMAILHUB_BASE_URL=https://tempmailhub.985100.xyz
TEMPMAILHUB_CHANNEL=minmail

# 代理配置（可选）
# 格式：http://user:pass@ip:port 或 socks5://user:pass@ip:port
PROXY_URL=

# 批量注册数量（可选，默认为1）
REGISTER_COUNT=1

# 浏览器无头模式（可选，默认为false显示浏览器）
HEADLESS=false

# Gptload配置（可选，用于自动推送keys）
GPTLOAD_API_URL=https://gptload.985100.xyz
GPTLOAD_AUTH_KEY=Glory0013
GPTLOAD_CHANNEL_NAME=jimeng

# API 服务认证 Key (默认为 dreamina-secret-key)
SERVER_API_KEY=dreamina-secret-key
```

## 使用指南

### 1. 命令行运行

直接运行 `src/main.py` 将根据 `.env` 配置执行注册任务。

- **批量注册**：在 `.env` 中设置 `REGISTER_COUNT=10`。
- **无头模式**：在 `.env` 中设置 `HEADLESS=true` (适合服务器)。

### 2. API 服务运行

启动服务后，可以通过 HTTP 请求管理注册任务。默认地址：`http://localhost:8000`。

### 3. 运行验证脚本

```powershell
uv run python test_api.py
```

### 4. 输出文件

- **key.txt**: 保存 SessionID (`us-{sessionid}`)
- **account.txt**: 保存账号密码 (`email:password`)

## API 文档

### 认证方式

所有受保护的接口需要在 Header 中包含认证Token。

- **Header**: `Authorization`
- **Value**: `Bearer <SERVER_API_KEY>`
- **说明**: `<SERVER_API_KEY>` 为部署时环境变量 `SERVER_API_KEY` 的值（默认为 `dreamina-secret-key`）。

### 接口列表

#### 1. 服务健康检查

- **URL**: `/health`
- **Method**: `GET`
- **Response**: `{"status": "ok"}`
- **认证**: 不需要

#### 2. 单账号注册 (异步)

- **URL**: `/register`
- **Method**: `POST`
- **认证**: 需要
- **Request Body**:
  ```json
  {
    "mail_type": "moemail" 
    // 可选值: "moemail", "tempmailhub"
    // 若使用 tempmailhub，可传递 "channel": "minmail"
  }
  ```
- **Response**: `{"task_id": "...", "status": "pending"}`

#### 3. 批量注册 (异步)

- **URL**: `/register/batch`
- **Method**: `POST`
- **认证**: 需要
- **Request Body**:
  ```json
  {
    "count": 5,
    "mail_type": "moemail"
  }
  ```
- **Response**: `{"task_id": "...", "status": "pending"}`

#### 4. 查询任务结果

- **URL**: `/tasks/{task_id}`
- **Method**: `GET`
- **认证**: 需要
- **Response 示例**:
  ```json
  {
    "task_id": "...",
    "status": "completed",
    "result": {
      "email": "example@moemail.com",
      "password": "...",
      "session_id": "us-..."
    },
    "error": null
  }
  ```

#### 5. 更新 SessionID (同步)

- **URL**: `/session/update`
- **Method**: `POST`
- **认证**: 需要
- **Request Body**: `{"email": "...", "password": "..."}`
- **Response**: `{"session_id": "...", "expires": ...}`

## 架构与开发指南

### 项目结构

```
Dreamina-register/
├── src/
│   ├── automation/      # 注册自动化逻辑 (DrissionPage)
│   ├── server.py        # FastAPI 服务入口
│   ├── tempmail/        # 临时邮箱抽象与实现
│   ├── services/        # 外部服务 (如 Gptload)
│   ├── utils/           # 工具函数 (密码生成等)
│   ├── config.py        # 配置管理
│   └── main.py          # 命令行入口
├── .env.example
├── README.md
```

### 注册流程详解 (Automation Flow)

1.  **启动与访问**：
    - 使用 DrissionPage (Incognito模式) 启动浏览器。
    - 打开 `https://dreamina.capcut.com/ai-tool/home`。
2.  **导航至注册**：
    - 点击 "Sign in" 按钮 (`#SiderMenuLogin`).
    - 点击 "Continue with email".
    - 点击 "Sign up".
3.  **创建账号**：
    - 调用配置的 `tempmail` 服务 API (moemail/tempmailhub) 获取新邮箱地址。
    - 输入邮箱 (`placeholder="Enter email"`).
    - 生成随机密码 (10-15位，含大小写字母+数字) 并输入 (`placeholder="Enter password"`).
    - 点击 "Continue".
4.  **验证邮箱**：
    - 轮询临时邮箱 API 获取最新邮件。
    - 使用正则 `Your verification code:\s*([A-Z]{6})` 提取 6 位大写字母验证码。
    - 逐个填入验证码输入框。
5.  **填写个人信息**：
    - 随机选择年份 (1991-2004)。
    - 随机选择月份和日期 (通过模拟点击下拉列表)。
    - 点击 "Next" 完成注册。
6.  **获取 Session**：
    - 等待跳转后，读取 cookie 中的 `sessionid`。
    - 格式化为 `us-{sessionid}`。
7.  **保存**：
    - 追加写入 `key.txt` 和 `account.txt`。
    - (可选) 调用 Gptload API 推送 key。

### 扩展临时邮箱

如需支持新的邮箱服务：
1.  在 `src/tempmail/` 创建新文件。
2.  定义类并继承 `TempMailBase`。
3.  实现必须的方法：`create_email`, `get_messages`, `extract_verification_code` 等。
4.  在 `src/config.py` 和工厂模式中注册新类。

## 常见问题

### Q: 报错 `ModuleNotFoundError: No module named 'config'`
**A:** 这是因为 Python 路径问题。请在 `src` 目录下运行命令，或者设置 `PYTHONPATH=src`。推荐使用 `cd src; uv run uvicorn server:app ...`。

### Q: 验证码获取失败
**A:** 可能是临时邮箱服务不稳定或被屏蔽。
- 增加等待时间（代码默认轮询 60s）。
- 尝试切换 `.env` 中的 `TEMPMAIL_TYPE`。

### Q: 接口鉴权失败 (403 Forbidden)
**A:** 检查请求 Header 中是否包含正确的 `Authorization: Bearer <Key>`。默认 Key 在 `.env` 中配置。

## 安全说明

- ⚠️ **敏感信息**：`.env` 文件包含 API Key，`account.txt` 包含生成的账号密码，请确保不要将这些文件提交到公开仓库 (`.gitignore` 已默认排除)。
- ⚠️ **合规性**：本工具仅用于自动化测试与学习，请勿用于大规模滥用或攻击目标服务。

## 免责声明

本工具仅供学习和研究使用，使用者需自行承担使用本工具的风险和责任。请遵守相关法律法规和服务条款。
