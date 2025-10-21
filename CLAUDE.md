# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Dreamina自动化注册程序 - 使用DrissionPage自动化框架和临时邮箱服务自动注册Dreamina账号。

## 运行环境

- Python 3.12+
- uv包管理器
- Windows平台

## 核心命令

### 运行程序
```bash
uv run python src/main.py
```

### 安装依赖
```bash
uv sync
```

## 环境配置

必须创建`.env`文件（参考`.env.example`）：

```bash
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
```

## 代码架构

### 核心模块

1. **src/config.py** - 配置管理
   - 从.env加载配置
   - 验证必需的API密钥

2. **src/tempmail/** - 临时邮箱服务抽象层
   - `base.py`: TempMailBase抽象基类，定义统一接口
   - `moemail.py`: MoeMail服务实现
   - `tempmailhub.py`: TempMailHub服务实现
   - 所有实现必须提供：`create_email()`, `get_domains()`, `get_messages()`, `get_message_content()`, `extract_verification_code()`

3. **src/automation/dreamina.py** - Dreamina注册自动化
   - DreaminaRegister类：完整的16步注册流程
   - 使用DrissionPage进行浏览器自动化
   - 支持代理配置（HTTP/SOCKS5）
   - 支持无头模式（headless）配置

4. **src/utils/password.py** - 密码生成工具
   - 生成10-15位随机密码
   - 包含大小写字母、数字和特殊字符

5. **src/services/gptload.py** - Gptload API服务封装
   - GptloadService类：处理keys推送到gptload系统
   - `get_groups()`: 获取所有groups
   - `find_group_by_name()`: 根据name查找group_id
   - `push_keys()`: 批量推送keys到指定group

### 注册流程（16步）

详细流程见`mission.md`，关键步骤：
1. 打开Dreamina网站（隐身模式）
2-4. 导航到注册页面
5. 生成临时邮箱
6-8. 填写邮箱和密码，提交
9-10. 获取并填入验证码
11-14. 填写生日信息
15-16. 提取sessionid并保存到key.txt（格式：us-{sessionid}）

### 临时邮箱API

- **MoeMail**: 需要先获取域名列表，随机选择域名创建邮箱
- **TempMailHub**: 支持多个渠道（minmail/tempmailplus/mailtm等），部分渠道需要accessToken

详细API文档见`tempmail-use-API.md`

## 开发注意事项

1. **DrissionPage元素定位**：
   - 优先使用`@@role=xxx@@id=xxx`组合定位
   - 备用方案使用`text=xxx`文本定位
   - 输入框使用`@placeholder=xxx`或`@@type=xxx@@placeholder=xxx`

2. **等待时间**：
   - 页面加载后等待10秒
   - 点击操作后等待3-4秒
   - 输入操作后等待1秒

3. **验证码提取**：
   - 正则匹配：`Your verification code:\s*([A-Z]{6})`
   - 验证码为6位大写字母

4. **代理格式**：
   - HTTP: `http://user:pass@ip:port`
   - SOCKS5: `socks5://user:pass@ip:port`

5. **输出文件**：
   - key.txt：每行一个sessionid（格式：us-{sessionid}）
   - account.txt：每行一组账号信息（格式：{邮箱}|{密码}）
   - 使用追加模式写入

6. **Gptload自动推送**：
   - 批量注册完成后自动执行
   - 需要配置`GPTLOAD_AUTH_KEY`才会启用
   - 先调用`/api/groups`获取所有groups
   - 匹配`GPTLOAD_CHANNEL_NAME`对应的group_id
   - 调用`/api/keys/add-async`批量推送keys
   - 认证方式：`Authorization: Bearer {GPTLOAD_AUTH_KEY}`

## 扩展临时邮箱服务

新增临时邮箱服务需要：
1. 在`src/tempmail/`创建新文件
2. 继承`TempMailBase`抽象类
3. 实现所有抽象方法
4. 在`src/config.py`添加配置项
5. 在`src/main.py`添加服务选择逻辑
