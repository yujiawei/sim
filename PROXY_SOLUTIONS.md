# 🚀 代理环境下的隧道解决方案 - 快速指南

## ⚠️ 问题概述

当前服务器环境存在 HTTP 代理限制，导致 **cloudflared 无法正常工作**。

```
错误: failed to request quick Tunnel: context deadline exceeded
原因: cloudflared 官方不支持通过 HTTP/SOCKS 代理连接
```

## ✅ 推荐解决方案

### 方案 1: 本地电脑测试（最简单）⭐

在你的本地电脑（Mac/Windows/Linux）上直接运行 cloudflared：

```bash
# macOS
brew install cloudflared
cloudflared tunnel --url http://localhost:8080

# Linux
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
./cloudflared-linux-amd64 tunnel --url http://localhost:8080

# Windows
# 下载 cloudflared-windows-amd64.exe
.\cloudflared.exe tunnel --url http://localhost:8080
```

**优点：**
- 无需处理代理问题
- 5 分钟内完成
- 官方支持，稳定可靠

**参考：** `tunnel-test-instructions.md`

---

### 方案 2: wstunnel（代理环境最佳）⭐⭐

**wstunnel** 专为突破防火墙和代理设计，使用 WebSocket：

#### 快速开始

**前提：** 你需要一台有公网 IP 的服务器

**步骤 1：在公网服务器上运行（服务端）**
```bash
# 安装
wget https://github.com/erebe/wstunnel/releases/latest/download/wstunnel-linux-x64
chmod +x wstunnel-linux-x64
sudo mv wstunnel-linux-x64 /usr/local/bin/wstunnel

# 运行服务器
wstunnel server wss://0.0.0.0:8443
```

**步骤 2：在当前服务器上运行（客户端）**
```bash
# 将本地 3000 端口暴露到公网服务器的 3000 端口
wstunnel client -L 0.0.0.0:3000:127.0.0.1:3000 wss://your-server.com:8443
```

**步骤 3：访问**
```
访问 http://your-server.com:3000 即可
```

**优点：**
- 专门为代理环境设计
- 支持 HTTP CONNECT 代理
- 性能好，资源占用低
- 开源，安全

**文档：** https://github.com/erebe/wstunnel

---

### 方案 3: bore（超简单）⭐

bore 是一个极简的隧道工具，有公共服务器可用：

```bash
# 安装
wget https://github.com/ekzhang/bore/releases/latest/download/bore-linux -O bore
chmod +x bore
sudo mv bore /usr/local/bin/

# 使用（一行命令）
bore local 8080 --to bore.pub
```

成功后会显示：
```
listening at bore.pub:xxxxx
```

直接访问 `http://bore.pub:xxxxx` 即可！

**优点：**
- 极简，一行命令
- 有公共服务器（bore.pub）
- 快速测试

**缺点：**
- 公共服务器不稳定
- 端口随机分配

---

### 方案 4: SSH 反向隧道（传统可靠）

如果你有一台公网服务器：

```bash
# 基本用法
ssh -R 8080:localhost:8080 user@your-public-server

# 持久连接（推荐）
autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" \
  -R 8080:localhost:8080 user@your-public-server
```

然后访问 `http://your-public-server:8080`

**优点：**
- 可靠，传统方案
- SSH 通常不被代理阻止
- 安全

**缺点：**
- 需要公网服务器
- 配置相对复杂

---

## 📊 方案对比

| 方案 | 难度 | 需要公网服务器 | 代理友好 | 稳定性 | 推荐度 |
|------|------|---------------|---------|--------|--------|
| 本地电脑测试 | ⭐ | ✗ | N/A | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| wstunnel | ⭐⭐ | ✓ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| bore | ⭐ | ✗ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| SSH 隧道 | ⭐⭐⭐ | ✓ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🎯 选择建议

**只想快速测试？**
→ 使用**本地电脑**或 **bore**

**需要在服务器上长期运行？**
→ 使用 **wstunnel** 或 **SSH 隧道**

**用于生产环境？**
→ 在本地电脑运行 cloudflared（命名隧道）或使用 wstunnel

## 🔧 故障排查

### 问题：wstunnel 连接失败

检查防火墙：
```bash
# 在公网服务器上
sudo ufw allow 8443/tcp
# 或
sudo firewall-cmd --add-port=8443/tcp --permanent
sudo firewall-cmd --reload
```

### 问题：bore 连接超时

bore.pub 可能繁忙，稍后再试或自建 bore 服务器

### 问题：SSH 隧道断开

使用 autossh 保持连接：
```bash
sudo apt install autossh  # Debian/Ubuntu
sudo yum install autossh   # CentOS/RHEL
```

## 📚 更多信息

- 完整网络限制说明：`NETWORK_LIMITATIONS.md`
- Cloudflare 隧道配置：`CLOUDFLARE_TUNNEL_GUIDE.md`
- 本地测试指南：`tunnel-test-instructions.md`

## 💡 快速决策流程图

```
需要公网访问本地服务？
│
├─ 能在本地电脑测试？
│  └─ YES → 使用 cloudflared（最简单）
│
├─ 必须在服务器上运行？
│  │
│  ├─ 有公网服务器？
│  │  └─ YES → 使用 wstunnel 或 SSH 隧道
│  │
│  └─ 没有公网服务器？
│     └─ 使用 bore（公共服务）
│
└─ 用于生产环境？
   └─ 建议在本地或有完整网络的环境运行 cloudflared
```

---

**最后更新：** 2025-10-21
**状态：** cloudflared 已安装但无法在当前代理环境使用
**建议：** 优先使用本地测试或 wstunnel
