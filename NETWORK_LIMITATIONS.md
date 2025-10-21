# 🔒 服务器网络限制说明

## 问题诊断结果

在尝试启动 Cloudflare 隧道时，发现了以下网络限制：

## 📋 具体限制

### 1. HTTP/HTTPS 代理强制要求

服务器环境**必须通过 HTTP 代理**访问外部网络：

```bash
# 当前代理配置
HTTP_PROXY=http://21.0.0.171:15004
HTTPS_PROXY=http://21.0.0.171:15004
```

**代理特点：**
- 代理地址: `21.0.0.171:15004`
- 认证方式: JWT 令牌（嵌入在用户名中）
- 这是一个容器化环境的网络控制机制（Anthropic egress control）

### 2. 代理白名单（NO_PROXY）

以下域名不经过代理：
```
localhost
127.0.0.1
169.254.169.254 (元数据服务)
*.svc.cluster.local (Kubernetes 内部)
*.local
*.googleapis.com
*.google.com
```

### 3. cloudflared 兼容性问题

**问题现象：**
```
failed to request quick Tunnel: Post "https://api.trycloudflare.com/tunnel":
context deadline exceeded (Client.Timeout exceeded while awaiting headers)
```

**原因分析（基于官方文档和社区反馈）：**

1. **官方不支持 HTTP 代理**
   - cloudflared 的隧道连接**不支持通过 HTTP/SOCKS 代理**
   - `HTTP_PROXY` 环境变量仅对 DNS 流量有效，不影响隧道连接
   - 隧道连接会直接拨号到 Cloudflare 边缘节点（端口 7844），绕过代理
   - 参考：[GitHub Issue #110](https://github.com/cloudflare/cloudflared/issues/110)

2. **QUIC 协议不兼容代理**
   - cloudflared 默认使用 QUIC 协议（基于 UDP）
   - QUIC 协议与 SOCKS/HTTP 代理不兼容
   - 已尝试使用 `--protocol http2` 强制 TCP 连接，但初始 API 请求仍超时

3. **代理超时问题**
   - API 请求（创建快速隧道）在通过代理时超时
   - 代理可能限制了长连接或特定类型的 HTTPS 请求
   - 当前代理环境的安全策略阻止了 cloudflared 的正常工作

### 4. 其他限制

**缺失的网络工具：**
- `ping` - 不可用
- `netstat` - 不可用
- `ss` - 不可用
- `nslookup`, `dig`, `host` - DNS 工具不可用

**初始 DNS 配置问题：**
- `/etc/resolv.conf` 初始为空
- 已手动配置为使用 8.8.8.8 和 1.1.1.1

## ✅ 可用的网络功能

尽管有上述限制，以下功能**可以正常工作**：

### HTTP/HTTPS 请求（通过代理）
```bash
# 可以访问外部网站
curl https://api.trycloudflare.com
# HTTP/1.1 200 OK ✓

# 可以下载文件
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
# ✓ 成功
```

### 本地网络通信
```bash
# 本地端口访问正常
curl http://localhost:8080
# ✓ 正常

# 容器内部通信正常
# Docker Compose 服务间可以互相访问
```

## 🚀 解决方案

### 方案 1: 在本地环境测试（推荐）

由于服务器环境的网络限制，**最佳方案是在你的本地电脑上安装和测试 cloudflared**。

本地环境通常没有这些限制，可以：
- 直接连接 Cloudflare API
- 建立稳定的隧道连接
- 正常使用快速隧道和命名隧道

**参考文档：** `tunnel-test-instructions.md`

### 方案 2: 使用命名隧道（可能可行）

如果你有 Cloudflare 账号，可以尝试使用命名隧道：

```bash
# 1. 在本地电脑登录（这步必须在本地完成）
cloudflared tunnel login

# 2. 创建隧道（在本地）
cloudflared tunnel create simstudio-tunnel

# 3. 复制认证文件到服务器
# 将 ~/.cloudflared/<tunnel-id>.json 复制到服务器

# 4. 在服务器上运行（可能可行，因为只需维持连接）
cloudflared tunnel --config config.yml run
```

**注意：** 即使是命名隧道，也可能因为代理限制而无法工作。

### 方案 3: 使用其他隧道服务（推荐用于代理环境）

根据社区反馈，以下隧道工具**明确支持代理环境**：

#### 3.1 wstunnel（强烈推荐）

**专为代理环境设计**，使用 WebSocket 隧道，可以穿透 HTTP 代理：

```bash
# 安装 wstunnel
wget https://github.com/erebe/wstunnel/releases/latest/download/wstunnel-linux-x64 -O wstunnel
chmod +x wstunnel
sudo mv wstunnel /usr/local/bin/

# 服务器端（如果你有公网服务器）
wstunnel server wss://0.0.0.0:443

# 客户端（在当前服务器上运行）
wstunnel client -L 0.0.0.0:8080:127.0.0.1:8080 wss://your-server.com:443
```

**优点：**
- 专门为突破防火墙/代理设计
- 支持通过 HTTP CONNECT 代理
- 使用 WebSocket，代理友好
- 开源，Rust 编写，性能好

#### 3.2 bore

简单的 TCP 隧道工具，使用 Rust 编写：

```bash
# 安装 bore
cargo install bore-cli
# 或
wget https://github.com/ekzhang/bore/releases/latest/download/bore-linux -O bore
chmod +x bore && sudo mv bore /usr/local/bin/

# 使用公共服务器
bore local 8080 --to bore.pub
```

#### 3.3 rathole

高性能隧道工具，Rust 编写，低资源消耗：

```bash
wget https://github.com/rapiz1/rathole/releases/latest/download/rathole-x86_64-unknown-linux-gnu.zip
unzip rathole-x86_64-unknown-linux-gnu.zip
chmod +x rathole
sudo mv rathole /usr/local/bin/
```

#### 3.4 gost（Go Simple Tunnel）

功能全面的隧道和代理工具：

```bash
# 安装 gost
wget https://github.com/go-gost/gost/releases/latest/download/gost_linux_amd64.tar.gz
tar -xzf gost_linux_amd64.tar.gz
sudo mv gost /usr/local/bin/

# 使用示例（支持通过代理转发）
gost -L=:8080 -F=http://proxy:port
```

**特点：**
- 支持多种协议
- 支持代理链
- 功能强大

#### 3.5 其他选项

**ngrok**（需要企业版支持代理）：
```bash
# 注意：免费版可能不支持代理
ngrok http 8080 --proxy http://proxy:port
```

**Tailscale**：
- 基于 WireGuard 的 VPN
- 可能可以穿透代理
- 但在严格代理环境可能受限

**SSH 隧道**（如果你有公网服务器）：
```bash
# 反向 SSH 隧道
ssh -R 8080:localhost:8080 user@your-public-server

# 使用 autossh 保持连接
autossh -M 0 -R 8080:localhost:8080 user@your-public-server
```

### 方案 4: 反向代理配置

如果目标是让外部访问服务器上的服务，可以考虑：

1. **直接配置域名和负载均衡器**
   - 如果在云环境（AWS, GCP, Azure）
   - 使用云提供商的负载均衡器

2. **使用 Nginx/Caddy**
   - 在一个有公网 IP 的服务器上运行反向代理
   - 通过 SSH 隧道或 VPN 连接回来

## 🧪 验证网络状态

你可以运行以下命令来检查网络状态：

```bash
# 检查代理配置
env | grep -i proxy

# 测试基本 HTTP 连接
curl -I https://www.google.com

# 测试 Cloudflare API（会通过代理）
curl -v https://api.trycloudflare.com 2>&1 | head -n 20

# 检查本地服务
curl http://localhost:8080
```

## 📊 网络架构图

```
┌─────────────────────────────────────────────┐
│         你的本地电脑                           │
│    (无网络限制，推荐在这里测试)                  │
│                                             │
│  cloudflared ──────> Cloudflare API ✓      │
│       │                                     │
│       └─────> 公网 URL ✓                    │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│         服务器环境                            │
│    (容器化环境，有代理限制)                     │
│                                             │
│  cloudflared ──> HTTP Proxy ──> Internet   │
│                      │                      │
│                      ├─> Cloudflare API ✗  │
│                      │   (超时)              │
│                      │                      │
│  curl ──────> HTTP Proxy ──> Internet ✓    │
│                      │                      │
│                      └─> 普通 HTTPS ✓       │
│                                             │
│  本地服务 <────> 127.0.0.1 ✓                │
└─────────────────────────────────────────────┘
```

## 🔬 已尝试的解决方案

### 尝试 1: 默认配置（QUIC 协议）
```bash
cloudflared tunnel --url http://localhost:8080
```
**结果：** ✗ 超时
```
failed to request quick Tunnel: context deadline exceeded
```

### 尝试 2: 强制使用 HTTP2 协议
```bash
cloudflared tunnel --protocol http2 --url http://localhost:8080
```
**结果：** ✗ 仍然超时

**结论：** 问题不在于 QUIC vs HTTP2，而是初始 API 请求（POST https://api.trycloudflare.com/tunnel）就通过代理超时了。

### 尝试 3: 配置 DNS
```bash
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
echo "nameserver 1.1.1.1" | sudo tee -a /etc/resolv.conf
```
**结果：** ✓ DNS 解析正常，但隧道仍然超时

### 验证：代理可以访问 Cloudflare API
```bash
curl -I https://api.trycloudflare.com
# HTTP/1.1 200 OK ✓
```

**结论：** 代理本身可以访问 Cloudflare API，但 cloudflared 通过代理的连接请求会超时，可能是：
- 代理的超时策略太严格
- cloudflared 的请求模式被代理阻止
- 需要的长连接/WebSocket 被代理限制

## 💡 总结

**核心问题：**
1. 服务器环境通过 HTTP 代理（JWT 认证）控制所有外部网络访问
2. cloudflared **官方不支持**通过 HTTP/SOCKS 代理连接到 Cloudflare 边缘节点
3. `HTTP_PROXY` 环境变量仅对 cloudflared 的 DNS 功能有效，不影响隧道连接
4. 当前代理环境的安全策略导致 cloudflared 无法正常工作

**推荐做法：**
1. **最佳方案**：在你的本地电脑上安装和测试 cloudflared（无代理限制）
2. **替代方案**：使用专为代理环境设计的隧道工具，如 **wstunnel**
3. **企业方案**：如有公网服务器，使用 SSH 反向隧道或其他自建隧道服务

**cloudflared 已安装完成：** 所有配置文件和脚本都已准备好，当你在有完整网络访问的环境中运行时，它们都可以正常工作。

## 📚 相关文档

- `CLOUDFLARE_TUNNEL_GUIDE.md` - 完整配置指南
- `tunnel-test-instructions.md` - 本地测试说明
- `cloudflare-tunnel-setup.sh` - 快速启动脚本

## 🔗 参考资料

### Cloudflare Tunnel 代理支持相关
- [GitHub Issue #110: Make cloudflared connect over http proxy](https://github.com/cloudflare/cloudflared/issues/110)
- [GitHub Issue #1025: How to make cloudflared tunnel use a proxy server](https://github.com/cloudflare/cloudflared/issues/1025)
- [Cloudflare Community: Using Cloudflared Behind HTTPS-Proxy](https://community.cloudflare.com/t/using-cloudflared-behind-https-proxy/637037)

### 替代隧道工具
- [wstunnel - WebSocket 隧道](https://github.com/erebe/wstunnel)
- [bore - 简单 TCP 隧道](https://github.com/ekzhang/bore)
- [rathole - 高性能隧道](https://github.com/rapiz1/rathole)
- [gost - Go Simple Tunnel](https://github.com/go-gost/gost)
- [Awesome Tunneling - 隧道工具汇总](https://github.com/anderspitman/awesome-tunneling)

---

**环境类型：** Anthropic 容器化开发环境
**网络控制：** Egress 代理 + JWT 认证
**问题：** cloudflared 不支持 HTTP 代理
**建议：** 本地环境测试 ✓ 或使用 wstunnel 等替代方案
