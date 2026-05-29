---
name: webapp-testing
description: 基于 Playwright 的本地 Web 应用测试工具集。融合自 Anthropic webapp-testing 技能。支持前端功能验证、UI调试、页面截图、浏览器控制台日志采集。遵循"先侦查后执行"流程。
---

# Web 应用测试

> 融合自 Anthropic webapp-testing 技能。与云舒"没有调查就没有发言权"方法论高度契合——先侦查再执行，不盲操作。

## 决策树：选择测试路径

```
前端验证任务 → 是静态 HTML？
    ├─ 是 → 读 HTML 文件直接识别选择器
    │       ├─ 成功 → 用选择器写 Playwright 脚本
    │       └─ 失败/不完整 → 按动态 WebApp 处理（下方）
    │
    └─ 否（动态 WebApp）→ 服务器是否已运行？
            ├─ 否 → 运行: python scripts/with_server.py --help
            │       然后用辅助脚本 + 写 Playwright 脚本
            │
            └─ 是 → 执行 Reconnaissance-Then-Action：
                    1. 导航并等待 networkidle
                    2. 截图或检查 DOM
                    3. 从渲染状态识别选择器
                    4. 用发现的选择器执行操作
```

## Reconnaissance-Then-Action 模式

> 云舒方法论映射："没有调查就没有发言权" — 先侦查（调查），再执行（发言）。

1. **侦查渲染 DOM**：
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **识别选择器**：从侦查结果中提取可用选择器

3. **执行操作**：用发现的选择器执行操作

## 服务器生命周期管理

使用 `scripts/with_server.py` 管理服务器（支持多服务器）：

**单服务器：**
```bash
python components/03-execute/webapp-testing/scripts/with_server.py \
  --server "npm run dev" --port 5173 -- python your_automation.py
```

**多服务器（后端 + 前端）：**
```bash
python components/03-execute/webapp-testing/scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

## Playwright 脚本模板

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:5173')
    page.wait_for_load_state('networkidle')  # 关键：等待 JS 执行完成
    # ... 你的自动化逻辑
    browser.close()
```

## 关键陷阱

⛔ **不要**在动态 App 上等 `networkidle` 之前检查 DOM
✅ **必须**先 `page.wait_for_load_state('networkidle')` 再检查

## 最佳实践

- 辅助脚本作为黑盒调用，不内联到上下文
- 使用 `sync_playwright()` 编写同步脚本
- 始终关闭浏览器
- 使用描述性选择器：`text=`、`role=`、CSS 选择器或 ID
- 添加适当等待：`page.wait_for_selector()` 或 `page.wait_for_timeout()`

## 控制台日志采集

```python
console_logs = []

def handle_console_message(msg):
    console_logs.append(f"[{msg.type}] {msg.text}")

page.on("console", handle_console_message)
# ... 交互后
# console_logs 即为采集的日志
```

## 依赖

Playwright 是**可选依赖**，仅前端任务需要：
```bash
pip install playwright && playwright install chromium
```

非前端任务无需安装。环境无 Playwright 时，降级为手动截图+日志作为证据。

## 参考文件

- `examples/element_discovery.py` — 发现页面上的按钮、链接和输入框
- `examples/static_html_automation.py` — 使用 file:// URL 测试本地 HTML
- `examples/console_logging.py` — 自动化期间捕获控制台日志
- `scripts/with_server.py` — 服务器生命周期管理
