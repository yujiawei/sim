#!/bin/bash

# Cloudflare 隧道启动脚本
# 用于快速建立本地服务到公网的隧道

set -e

echo "======================================"
echo "Cloudflare 隧道配置工具"
echo "======================================"
echo ""

# 检查 cloudflared 是否安装
if ! command -v cloudflared &> /dev/null; then
    echo "错误: cloudflared 未安装"
    echo "请先运行以下命令安装："
    echo "wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared"
    echo "chmod +x cloudflared && sudo mv cloudflared /usr/local/bin/"
    exit 1
fi

# 默认端口
PORT=${1:-8080}

echo "正在启动 Cloudflare 隧道..."
echo "本地服务端口: $PORT"
echo ""

# 启动隧道
echo "执行命令: cloudflared tunnel --url http://localhost:$PORT"
echo ""
cloudflared tunnel --url http://localhost:$PORT
