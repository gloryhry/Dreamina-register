# Dreamina-register Dockerfile
# 基于 Python 3.12-slim，集成 uv 包管理器、Chromium 浏览器和 gost 代理

FROM python:3.12-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # DrissionPage 无头模式
    HEADLESS=true

# gost 版本
ARG GOST_VERSION=2.12.0

# 安装系统依赖 + Chromium 浏览器 + 下载 gost
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Chromium 及驱动
    chromium \
    chromium-driver \
    # 中文字体支持
    fonts-wqy-zenhei \
    fonts-noto-cjk \
    # 其他必要依赖
    curl \
    # gzip 用于解压 gost
    gzip \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    # 下载并安装 gost (用于 SOCKS5 代理认证中转)
    && curl -fsSL "https://github.com/ginuerzh/gost/releases/download/v${GOST_VERSION}/gost_${GOST_VERSION}_linux_amd64.tar.gz" -o /tmp/gost.tar.gz \
    && tar -xzf /tmp/gost.tar.gz -C /tmp \
    && mv /tmp/gost /usr/local/bin/gost \
    && chmod +x /usr/local/bin/gost \
    && rm /tmp/gost.tar.gz \
    && echo "gost installed: $(/usr/local/bin/gost -V)"

# 安装 uv 包管理器
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 设置工作目录
WORKDIR /app

# 复制依赖配置文件（利用 Docker 缓存）
COPY pyproject.toml uv.lock ./

# 安装 Python 依赖
RUN uv sync --frozen --no-cache

# 复制入口脚本
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# 复制项目源代码
COPY src/ ./src/

# 暴露端口
EXPOSE 8000

# 设置工作目录到 src（解决模块导入问题）
WORKDIR /app/src

# 使用入口脚本启动（自动处理代理中转）
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uv", "run", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
