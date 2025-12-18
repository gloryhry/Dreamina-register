#!/bin/bash
# Docker 入口脚本
# 功能：在检测到 SOCKS5 认证代理时，自动启动 gost 作为本地代理中转

set -e

# 本地代理端口
LOCAL_PROXY_PORT=1080

# 解析代理URL并启动 gost（如果需要）
start_proxy_relay() {
    if [ -z "$PROXY_URL" ]; then
        echo "[Proxy] PROXY_URL 未设置，跳过代理中转"
        return 0
    fi

    # 检查是否是需要认证的 SOCKS5 代理
    # 格式: socks5://user:pass@host:port 或 socks5h://user:pass@host:port
    if echo "$PROXY_URL" | grep -qE '^socks5h?://[^:]+:[^@]+@'; then
        echo "[Proxy] 检测到 SOCKS5 认证代理: $PROXY_URL"
        echo "[Proxy] 启动 gost 本地代理中转 (127.0.0.1:$LOCAL_PROXY_PORT -> $PROXY_URL)"
        
        # 后台启动 gost
        /usr/local/bin/gost -L ":$LOCAL_PROXY_PORT" -F "$PROXY_URL" &
        GOST_PID=$!
        
        # 等待 gost 启动
        sleep 1
        
        # 检查 gost 是否正常运行
        if kill -0 $GOST_PID 2>/dev/null; then
            echo "[Proxy] gost 启动成功 (PID: $GOST_PID)"
            # 导出本地代理地址供应用使用
            export PROXY_URL_ORIGINAL="$PROXY_URL"
            export PROXY_URL="socks5://127.0.0.1:$LOCAL_PROXY_PORT"
            echo "[Proxy] 应用将使用本地代理: $PROXY_URL"
        else
            echo "[Proxy] 警告: gost 启动失败，将尝试直接使用原始代理"
        fi
    else
        echo "[Proxy] 代理类型不需要中转: $PROXY_URL"
    fi
}

# 启动代理中转
start_proxy_relay

# 执行传入的命令
echo "[Entrypoint] 启动应用..."
exec "$@"
