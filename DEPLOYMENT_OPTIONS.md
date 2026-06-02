# Cloud Deployment Guide - Nintendo Museum Monitor

## 🎯 概述

本项目支持将 Telegram Bot 监控功能部署到云服务，实现 **24/7 自动监控**，无需本地设备保持运行。

## 📋 两种部署方案对比

### 方案 A：GitHub Actions（推荐 - 最简单）

| 特性 | 详情 |
|------|------|
| **成本** | 完全免费 |
| **配置复杂度** | ⭐ 简单 |
| **维护成本** | ⭐ 低 |
| **免费额度** | 月 2000 分钟 |
| **推荐频率** | 每小时一次 |
| **支持平台** | Telegram + Bark |

**优点：**
- ✅ 无需服务器管理
- ✅ 代码版本控制
- ✅ 自动备份
- ✅ 透明的执行日志

**缺点：**
- ❌ 免费配额有限
- ❌ 不支持实时监控
- ❌ 运行时间有限制

### 方案 B：Railway/Render（付费 - 持续运行）

| 特性 | 详情 |
|------|------|
| **成本** | $5-10/月 |
| **配置复杂度** | ⭐⭐ 中等 |
| **维护成本** | ⭐⭐ 中等 |
| **免费额度** | 750 小时/月（Render） |
| **推荐频率** | 每 10-30 分钟 |
| **支持平台** | Telegram + Bark |

**优点：**
- ✅ 持续运行 24/7
- ✅ 更灵活的配置
- ✅ 无时间限制
- ✅ 更快的检查频率

**缺点：**
- ❌ 需要付费
- ❌ 需要维护服务器配置
- ❌ 更复杂的部署流程

---

## 🚀 快速开始：GitHub Actions 方案

### 第 1 步：创建 Telegram Bot（5 分钟）

详见 `CLOUD_DEPLOYMENT_GUIDE.md` 的第一部分

**关键步骤：**
1. 搜索 `@BotFather` → `/newbot` 创建 bot
2. 记录 **Bot Token**
3. 发送消息给 bot，访问 API 获取 **Chat ID**

### 第 2 步：添加 GitHub Secrets（3 分钟）

```
Settings → Secrets and variables → Actions → New repository secret
```

添加这些 Secrets：
- `TELEGRAM_BOT_TOKEN` = 你的 bot token
- `TELEGRAM_CHAT_ID` = 你的 chat id
- `TARGET_DATE` = 2025-06-15

### 第 3 步：添加工作流文件（2 分钟）

1. 在你的项目中创建文件：
   ```
   .github/workflows/cloud-monitor-telegram.yml
   ```

2. 复制本项目提供的工作流内容

3. 提交

### 第 4 步：测试（1 分钟）

1. 点击 `Actions` 标签
2. 选择工作流
3. 点击 `Run workflow`
4. 检查 Telegram 是否收到通知

✅ 完成！自动监控已启用

---

## 🌐 云服务部署：Railway.app 方案

### 环境搭建

1. **在 Railway 上部署：**
   ```bash
   git push railway main
   ```

2. **设置环境变量：**
   ```
   TELEGRAM_BOT_TOKEN=xxx
   TELEGRAM_CHAT_ID=xxx
   TARGET_DATE=2025-06-15
   SERVICE_TYPE=telegram
   ```

3. **启用持续运行**

### Docker 部署

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    chromium-browser \
    chromium-chromedriver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "cloud-monitor.py"]
```

---

## 📊 成本对比

| 方案 | 成本/月 | 检查频率 | 配置难度 |
|------|--------|--------|--------|
| **GitHub Actions** | 🆓 免费 | 每小时 | ⭐ 简单 |
| **Railway** | 💰 $5 | 每 10 分钟 | ⭐⭐ 中等 |
| **Render** | 🆓-💰 | 每 30 分钟 | ⭐⭐ 中等 |
| **本地电脑** | 💰 电费 | 连续 | ⭐ 简单 |

---

## 🔄 工作流说明

### GitHub Actions 工作流是什么？

工作流是一个自动化任务，包括：
1. **触发条件**（定时或手动）
2. **执行环境**（操作系统和软件）
3. **执行步骤**（运行脚本或命令）

### 我们的工作流做了什么？

```
每 10 分钟（可自定义）
    ↓
启动 Ubuntu 虚拟机
    ↓
安装 Python + Chromium + ChromeDriver
    ↓
运行 Python 脚本检查 Nintendo Museum 票务
    ↓
如果有票 → 发送 Telegram 通知
    ↓
关闭虚拟机
```

每次运行大约消耗 1-2 分钟的配额。

---

## ⚡ 性能优化建议

### 1. 调整检查频率

太频繁 = 配额快速耗尽
太稀疏 = 可能错过有票

**推荐配置：**
- 工作日: `0 8-20 * * 1-5` (工作时间每小时)
- 周末: `0 10-22 * * 0,6` (周末较晚时间)

### 2. 增加超时时间

网络慢时可能超时，增加容差：

```yaml
timeout-minutes: 10  # 最多运行 10 分钟
```

### 3. 多日期监控策略

**方案 1：并行监控（多个工作流）**
- 创建多个 `.github/workflows/` 文件
- 每个监控不同日期

**方案 2：顺序监控（一个脚本）**
- 在 Python 脚本中循环多个日期
- 一个工作流文件完成所有监控

---

## 📝 常见问题 FAQ

### Q: GitHub Actions 配额用完了怎么办？

**答：** GitHub 免费账户每月 2000 分钟
- 改成每小时检查一次 = 720 分钟/月 ✅
- 改成每 30 分钟一次 = 1440 分钟/月 ✅（勉强）
- 改成每 10 分钟一次 = 4320 分钟/月 ❌（超限）

### Q: 为什么我没收到通知？

**排查步骤：**
1. 检查 Telegram Bot 是否在线
   ```
   给 bot 发送消息 → 访问 getUpdates API
   ```

2. 检查 Secrets 是否正确
   ```
   Settings → Secrets → 逐个验证
   ```

3. 查看工作流日志
   ```
   Actions → 选择工作流 → 查看完整日志
   ```

4. 测试 Telegram API
   ```bash
   curl "https://api.telegram.org/botTOKEN/getMe"
   ```

### Q: 可以改变通知文字吗？

**是的！** 编辑 `cloud-monitor.py` 中的这一行：

```python
self.notification_service.send(
    "任天堂博物馆有票了！",  # ← 改这里（标题）
    f"🎮 {self.target_date} 有可用座位，立即前往预订！"  # ← 改这里（内容）
)
```

### Q: 支持其他通知方式吗？

**是的！** 项目支持 Telegram 和 Bark

需要其他服务？可以：
1. 创建新的 `NotificationService` 子类
2. 实现 `send()` 方法
3. 在 `main()` 中添加条件分支

**例如支持钉钉：**
```python
class DingTalkNotificationService(NotificationService):
    def send(self, title: str, body: str) -> bool:
        # 调用钉钉 API
        pass
```

---

## 🛠️ 自定义部署

### 修改检查日期

编辑 GitHub Secrets 中的 `TARGET_DATE`:
```
2025-06-15
```

### 修改检查频率

编辑 `.github/workflows/cloud-monitor-telegram.yml`:
```yaml
schedule:
  - cron: '0 * * * *'  # 改这里
```

### 修改通知消息

编辑 `cloud-monitor.py`:
```python
self.notification_service.send(
    "你的标题",
    "你的内容"
)
```

---

## 📚 相关文档

- Telegram Bot API: https://core.telegram.org/bots/api
- GitHub Actions: https://docs.github.com/en/actions
- Cron 表达式: https://crontab.guru/
- Railway 部署: https://docs.railway.app/

---

## ✅ 部署检查清单

- [ ] 创建 Telegram Bot，获得 Token
- [ ] 获取你的 Chat ID
- [ ] 在 GitHub 添加 3 个 Secrets
- [ ] 创建 `.github/workflows/cloud-monitor-telegram.yml`
- [ ] 手动运行工作流测试
- [ ] 验证 Telegram 通知
- [ ] 调整检查频率（可选）
- [ ] 启用自动定时任务
- [ ] 监控一周以验证稳定性

---

**准备好了？现在就 Fork 项目并开始部署吧！** 🚀
