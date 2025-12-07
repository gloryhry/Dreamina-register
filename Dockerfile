# Dreamina-register Dockerfile
# 基于 Python 3.12-slim，集成 uv 包管理器和 Chromium 浏览器

FROM python:3.12-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # DrissionPage 无头模式
    HEADLESS=true

# 安装系统依赖 + Chromium 浏览器
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Chromium 及驱动
    chromium \
    chromium-driver \
    # 中文字体支持
    fonts-wqy-zenhei \
    fonts-noto-cjk \
    # 其他必要依赖
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 安装 uv 包管理器
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 设置工作目录
WORKDIR /app

# 复制依赖配置文件（利用 Docker 缓存）
COPY pyproject.toml uv.lock ./

# 安装 Python 依赖
RUN uv sync --frozen --no-cache

# 复制项目源代码
COPY src/ ./src/

# 暴露端口
EXPOSE 8000

# 设置工作目录到 src（解决模块导入问题）
WORKDIR /app/src

# 启动 FastAPI 服务
CMD ["uv", "run", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
