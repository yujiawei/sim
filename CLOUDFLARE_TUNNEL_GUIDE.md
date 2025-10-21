# Cloudflare 隧道配置指南

## 🎯 概述

Cloudflare 隧道已成功安装在服务器上。本指南将帮助你完成本地电脑与服务器的互通测试。

## ✅ 已完成的配置

### 1. 安装 cloudflared
```bash
cloudflared --version
# 输出: cloudflared version 2025.10.0
```

### 2. 创建测试服务
- 测试页面: `/home/user/sim/test-server.html`
- HTTP 服务器运行在端口: `8080`

### 3. 启动脚本
- 脚本位置: `/home/user/sim/cloudflare-tunnel-setup.sh`

## 🚀 快速启动隧道

### 方法一：使用快速隧道（推荐用于测试）

在服务器上运行以下命令：

```bash
# 启动隧道连接到本地 8080 端口
cloudflared tunnel --url http://localhost:8080
```

成功启动后，你会看到类似以下输出：

```
2025-10-21T03:47:22Z INF +--------------------------------------------------------------------------------------------+
2025-10-21T03:47:22Z INF |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
2025-10-21T03:47:22Z INF |  https://random-string.trycloudflare.com                                                   |
2025-10-21T03:47:22Z INF +--------------------------------------------------------------------------------------------+
```

### 方法二：使用提供的脚本

```bash
cd /home/user/sim
./cloudflare-tunnel-setup.sh 8080
```

## 🧪 本地电脑测试步骤

### 步骤 1: 获取隧道 URL

当 cloudflared 成功启动后，它会显示一个公网 URL，格式类似：
```
https://xxxxx-xxxx-xxxx.trycloudflare.com
```

### 步骤 2: 在本地浏览器测试

1. 复制上面显示的 URL
2. 在你的本地电脑浏览器中打开这个 URL
3. 如果看到 "Cloudflare 隧道连接成功！" 页面，说明隧道工作正常

### 步骤 3: 测试不同端口

如果你想将隧道连接到 SimStudio 应用（端口 3000）：

```bash
# 首先确保 SimStudio 应用正在运行
cd /home/user/sim
bun run dev

# 然后在另一个终端启动隧道
cloudflared tunnel --url http://localhost:3000
```

## 📋 常用端口说明

- `3000` - SimStudio 主应用
- `3002` - Realtime WebSocket 服务
- `5432` - PostgreSQL 数据库
- `8080` - 测试 HTTP 服务器（当前演示）

## 🔧 高级配置：命名隧道

对于生产环境，建议使用命名隧道：

### 1. 登录 Cloudflare
```bash
cloudflared tunnel login
```

### 2. 创建隧道
```bash
cloudflared tunnel create simstudio-tunnel
```

### 3. 配置隧道
创建配置文件 `~/.cloudflared/config.yml`：

```yaml
tunnel: <tunnel-id>
credentials-file: /root/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: your-domain.com
    service: http://localhost:3000
  - hostname: ws.your-domain.com
    service: http://localhost:3002
  - service: http_status:404
```

### 4. 启动隧道
```bash
cloudflared tunnel run simstudio-tunnel
```

## 🐛 故障排查

### 问题 1: 隧道无法启动

检查网络连接：
```bash
curl -I https://api.trycloudflare.com
```

### 问题 2: DNS 解析失败

配置 DNS 服务器：
```bash
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
echo "nameserver 1.1.1.1" | sudo tee -a /etc/resolv.conf
```

### 问题 3: 本地服务未运行

检查服务状态：
```bash
# 检查 8080 端口
curl http://localhost:8080

# 检查 3000 端口（SimStudio）
curl http://localhost:3000
```

启动测试服务器：
```bash
cd /home/user/sim
python3 -m http.server 8080
```

## 📱 测试检查清单

- [ ] cloudflared 已安装并可以运行
- [ ] 本地服务在指定端口运行
- [ ] cloudflared 隧道成功启动
- [ ] 获得了公网访问 URL
- [ ] 在本地浏览器可以访问该 URL
- [ ] 测试页面正常显示

## 🔐 安全注意事项

1. **临时隧道**：快速隧道（trycloudflare.com）是临时的，URL 会在每次启动时改变
2. **无认证**：默认情况下，任何人都可以访问你的隧道 URL
3. **生产环境**：请使用命名隧道并配置 Cloudflare Access 进行身份验证
4. **敏感数据**：不要通过临时隧道暴露包含敏感数据的服务

## 📚 参考资料

- [Cloudflare Tunnel 官方文档](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps)
- [快速隧道说明](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/do-more-with-tunnels/trycloudflare)
- [命名隧道创建指南](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/tunnel-guide)

## 🎉 下一步

成功测试隧道后，你可以：

1. 将隧道连接到 SimStudio 应用（端口 3000）
2. 配置自定义域名
3. 设置 Cloudflare Access 进行访问控制
4. 配置负载均衡和故障转移

---

**当前状态**: cloudflared 已安装，测试服务器已准备就绪，可以随时启动隧道进行测试。
