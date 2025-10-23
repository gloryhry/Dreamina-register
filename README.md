# Dreamina 自动化注册程序

> 基于 DrissionPage 的 Dreamina 账号自动化注册工具，支持临时邮箱、代理、批量注册和自动推送功能。

## ✨ 功能特性

- 🤖 **全自动注册**：完整的 16 步自动化注册流程
- 📧 **临时邮箱支持**：集成 MoeMail 和 TempMailHub 两种临时邮箱服务
- 🔐 **随机密码生成**：自动生成 10-15 位强密码
- 🌐 **代理支持**：支持 HTTP 和 SOCKS5 代理（含认证）
- 📦 **批量注册**：支持一次性注册多个账号
- 👻 **无头模式**：可选的浏览器无头模式，适合服务器环境
- 🚀 **自动推送**：注册完成后自动推送 keys 到 Gptload 系统
- 💾 **数据保存**：自动保存 SessionID 和账号信息

## 📋 环境要求

- **Python**: 3.12 或更高版本
- **包管理器**: [uv](https://github.com/astral-sh/uv)
- **操作系统**: Windows / Linux / macOS
- **浏览器**: Chromium 内核浏览器（DrissionPage 自动管理）

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/gloryhry/Dreamina-register
cd Dreamina-register
```

### 2. 安装依赖

使用 uv 安装项目依赖：

```bash
uv sync
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的参数（详见下方配置说明）。

### 4. 运行程序

```bash
uv run python src/main.py
```

## ⚙️ 配置说明

### 临时邮箱配置

#### 选项 1：使用 MoeMail

```bash
TEMPMAIL_TYPE=moemail
MOEMAIL_API_KEY=your_api_key_here
MOEMAIL_BASE_URL=https://moemail
```

#### 选项 2：使用 TempMailHub

```bash
TEMPMAIL_TYPE=tempmailhub
TEMPMAILHUB_API_KEY=your_api_key_here
TEMPMAILHUB_BASE_URL=https://tempmailhub
TEMPMAILHUB_CHANNEL=minmail
```

**支持的 TempMailHub 渠道**：
- `minmail`
- `tempmailplus`
- `mailtm`
- 其他渠道（详见 API 文档）

### 代理配置（可选）

支持 HTTP 和 SOCKS5 代理，包括用户名密码认证：

```bash
# HTTP 代理
PROXY_URL=http://user:pass@ip:port

# SOCKS5 代理
PROXY_URL=socks5://user:pass@ip:port

# 不使用代理
PROXY_URL=
```

### 批量注册配置（可选）

```bash
# 一次性注册的账号数量，默认为 1
REGISTER_COUNT=5
```

### 浏览器配置（可选）

```bash
# 无头模式：true 为后台运行，false 为显示浏览器（默认）
HEADLESS=false
```

**使用场景**：
- `HEADLESS=false`：开发调试时，可以看到浏览器操作过程
- `HEADLESS=true`：生产环境或服务器上运行，节省资源

### Gptload 自动推送配置（可选）

注册完成后自动推送 keys 到 Gptload 系统：

```bash
GPTLOAD_API_URL=https://gptload.985100.xyz
GPTLOAD_AUTH_KEY=your_auth_key
GPTLOAD_CHANNEL_NAME=Dreamina
```

**说明**：
- 如果不配置 `GPTLOAD_AUTH_KEY`，将跳过自动推送
- `GPTLOAD_CHANNEL_NAME` 为 Gptload 中的 group name

## 📖 使用指南

### 基本使用

1. 配置 `.env` 文件
2. 运行程序：

```bash
uv run python src/main.py
```

### 批量注册示例

注册 10 个账号：

```bash
# 在 .env 中设置
REGISTER_COUNT=10

# 运行程序
uv run python src/main.py
```

### 使用代理示例

```bash
# 在 .env 中设置代理
PROXY_URL=http://user:pass@proxy.example.com:8080

# 运行程序
uv run python src/main.py
```

### 无头模式运行

适合在服务器上运行：

```bash
# 在 .env 中启用无头模式
HEADLESS=true

# 运行程序
uv run python src/main.py
```

## 📁 项目结构

```
Dreamina-register/
├── src/
│   ├── automation/
│   │   └── dreamina.py          # Dreamina 注册自动化逻辑
│   ├── tempmail/
│   │   ├── base.py              # 临时邮箱抽象基类
│   │   ├── moemail.py           # MoeMail 服务实现
│   │   └── tempmailhub.py       # TempMailHub 服务实现
│   ├── services/
│   │   └── gptload.py           # Gptload API 服务封装
│   ├── utils/
│   │   └── password.py          # 密码生成工具
│   ├── config.py                # 配置管理
│   └── main.py                  # 程序入口
├── .env.example                 # 环境变量示例
├── pyproject.toml               # 项目依赖配置
├── CLAUDE.md                    # Claude Code 指导文档
└── README.md                    # 项目说明文档
```

## 📤 输出文件

程序运行后会生成以下文件：

### key.txt

保存注册成功的 SessionID，每行一个：

```
us-abc123def456...
us-xyz789ghi012...
```

**格式**：`us-{sessionid}`

### account.txt

保存账号信息，每行一组：

```
email1@example.com:Password123!
email2@example.com:SecurePass456@
```

**格式**：`{邮箱}:{密码}`

## ❓ 常见问题

### 1. 如何获取临时邮箱 API Key？

- **MoeMail**：访问 MoeMail 服务提供商获取 API Key
- **TempMailHub**：访问 TempMailHub 服务提供商获取 API Key

### 2. 程序运行失败怎么办？

检查以下几点：
- 确认 `.env` 配置正确
- 确认临时邮箱 API Key 有效
- 检查网络连接和代理设置
- 查看控制台错误信息

### 3. 如何在服务器上运行？

1. 启用无头模式：`HEADLESS=true`
2. 确保服务器安装了 Chromium 浏览器
3. 使用 `nohup` 或 `screen` 后台运行：

```bash
nohup uv run python src/main.py > output.log 2>&1 &
```

### 4. 验证码获取失败怎么办？

- 检查临时邮箱服务是否正常
- 增加等待时间（程序默认等待 60 秒）
- 尝试更换临时邮箱服务

### 5. 如何扩展支持其他临时邮箱服务？

1. 在 `src/tempmail/` 创建新的服务实现文件
2. 继承 `TempMailBase` 抽象类
3. 实现所有抽象方法
4. 在 `src/config.py` 添加配置项
5. 在 `src/main.py` 添加服务选择逻辑

详见 `CLAUDE.md` 中的扩展说明。

## 🔐 安全说明

- ⚠️ 请勿将 `.env` 文件提交到版本控制系统
- ⚠️ 妥善保管 API Key 和认证信息
- ⚠️ 生成的账号信息文件包含敏感数据，请注意保护

## 📝 开发说明

### 添加新功能

项目使用模块化设计，便于扩展：

- **临时邮箱服务**：在 `src/tempmail/` 添加新实现
- **自动化流程**：修改 `src/automation/dreamina.py`
- **配置项**：在 `src/config.py` 和 `.env.example` 添加

### 代码规范

- 遵循 PEP 8 代码规范
- 使用类型注解
- 添加必要的注释和文档字符串

### 测试

运行单个账号注册测试：

```bash
# 设置 REGISTER_COUNT=1
uv run python src/main.py
```

## 📄 许可证

本项目仅供学习和研究使用，请勿用于非法用途。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

如有问题或建议，请通过 Issue 联系。

---

**⚠️ 免责声明**：本工具仅供学习和研究使用，使用者需自行承担使用本工具的风险和责任。请遵守相关法律法规和服务条款。
