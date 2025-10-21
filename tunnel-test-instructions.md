# 🚀 Cloudflare 隧道本地测试指南

## 当前服务器状态

✅ **已完成的配置**
- cloudflared 已安装（版本 2025.10.0）
- 测试 HTTP 服务器运行在端口 8080
- 测试页面已创建：`/home/user/sim/test-server.html`
- 启动脚本已准备：`/home/user/sim/cloudflare-tunnel-setup.sh`

⚠️ **网络限制说明**
当前服务器环境存在网络限制，无法直接连接到 Cloudflare API。你需要在具有完整互联网访问权限的环境中测试隧道功能。

---

## 📝 在你的本地电脑上安装和测试

### 方案 A：在本地 Linux/Mac 环境测试

#### 1. 安装 cloudflared

**Linux (x86_64):**
```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
```

**macOS (Intel):**
```bash
brew install cloudflared
```

**macOS (Apple Silicon):**
```bash
brew install cloudflared
```

#### 2. 启动一个测试服务

在本地电脑上创建测试服务：

```bash
# 方法 1: 使用 Python
python3 -m http.server 8080

# 方法 2: 使用 Node.js
npx http-server -p 8080

# 方法 3: 如果你有 SimStudio 项目
cd /path/to/simstudio
bun run dev  # 默认运行在 3000 端口
```

#### 3. 启动 Cloudflare 隧道

在另一个终端窗口运行：

```bash
# 连接到 8080 端口
cloudflared tunnel --url http://localhost:8080

# 或连接到 SimStudio (3000 端口)
cloudflared tunnel --url http://localhost:3000
```

#### 4. 获取公网 URL

成功启动后，你会看到类似输出：

```
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable): |
|  https://random-words-1234.trycloudflare.com                                               |
+--------------------------------------------------------------------------------------------+
```

#### 5. 在浏览器测试

1. 复制上面显示的 URL
2. 在任何设备的浏览器中打开这个 URL
3. 你应该能看到你的本地服务内容

---

### 方案 B：在 Windows 环境测试

#### 1. 下载 cloudflared

访问 [Cloudflare 下载页面](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/) 或直接下载：

```powershell
# 使用 PowerShell
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"
```

#### 2. 启动测试服务

```powershell
# 使用 Python
python -m http.server 8080
```

#### 3. 启动隧道

在另一个 PowerShell 窗口：

```powershell
.\cloudflared.exe tunnel --url http://localhost:8080
```

---

## 🎯 测试 SimStudio 应用互通

### 完整测试流程

#### 在服务器端：

1. 启动 SimStudio 应用：
```bash
cd /home/user/sim
bun run dev:full
```

2. 在另一个终端启动隧道：
```bash
cloudflared tunnel --url http://localhost:3000
```

#### 在本地电脑：

1. 获取隧道 URL（例如：`https://abc-def-123.trycloudflare.com`）
2. 在浏览器打开这个 URL
3. 你应该能访问运行在服务器上的 SimStudio 应用

---

## 🔍 验证测试成功

成功的测试应该满足以下条件：

- [ ] cloudflared 启动无错误
- [ ] 获得了 `https://*.trycloudflare.com` 格式的 URL
- [ ] 在浏览器中打开 URL 能看到服务内容
- [ ] 可以从不同网络（如手机 4G）访问相同 URL
- [ ] 页面交互正常，没有跨域或连接问题

---

## 💡 快速测试示例

如果你只想快速验证 cloudflared 是否工作，可以使用这个一行命令：

```bash
# 创建一个简单的 HTML 文件并启动隧道
echo '<h1>Cloudflare Tunnel Works!</h1>' > index.html && \
python3 -m http.server 8080 & \
cloudflared tunnel --url http://localhost:8080
```

---

## 🔧 常见问题解决

### Q1: "connection refused" 错误

**原因**: 本地服务未运行

**解决**: 确保本地服务已启动并监听正确端口
```bash
curl http://localhost:8080  # 应该有响应
```

### Q2: "context deadline exceeded" 错误

**原因**: 网络限制或防火墙

**解决**:
- 检查防火墙设置
- 尝试不同的网络环境
- 确保可以访问 `api.trycloudflare.com`

### Q3: 隧道 URL 无法访问

**原因**: 隧道还在建立中

**解决**: 等待 10-30 秒，隧道需要时间在 Cloudflare 网络中传播

---

## 📊 测试隧道性能

启动隧道后，你可以测试延迟和速度：

```bash
# 测试延迟
curl -o /dev/null -s -w "Time: %{time_total}s\n" https://your-tunnel-url.trycloudflare.com

# 使用 curl 测试下载速度
curl -o /dev/null https://your-tunnel-url.trycloudflare.com/large-file
```

---

## 🎓 下一步学习

成功测试后，你可以：

1. **配置命名隧道**（用于生产环境）
   ```bash
   cloudflared tunnel login
   cloudflared tunnel create my-tunnel
   ```

2. **设置自定义域名**
   - 在 Cloudflare 仪表板添加你的域名
   - 配置 DNS 记录指向隧道

3. **添加访问控制**
   - 使用 Cloudflare Access 限制访问
   - 配置身份验证策略

4. **配置多服务**
   - 使用配置文件路由不同服务
   - 设置负载均衡

---

## 📞 需要帮助？

参考完整文档：`/home/user/sim/CLOUDFLARE_TUNNEL_GUIDE.md`

Cloudflare 官方文档：
- [快速开始](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/tunnel-guide/)
- [故障排查](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/troubleshooting/)

---

**准备好了吗？** 选择上面的方案 A 或 B，在你的本地环境开始测试！
