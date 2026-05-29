---
name: cloudflare-deploy
description: "Cloudflare Pages 部署组件。触发文件夹上传部署，等待完成并提取访问链接。"
metadata:
  parent: "cloudflare-pages-deploy"
  type: "browser-automation-step"
---

# Cloudflare Pages — 部署组件

> 在 Cloudflare Pages 项目页面中触发部署、上传文件夹、等待完成并获取访问链接。

---

## 职责

- 点击 Create deployment 按钮
- 选择 folder upload 方式
- 在文件选择对话框中定位并选择源文件夹
- 等待部署完成
- 从部署结果中提取访问链接

---

## 操作流程

### 1. 前置检查

1. 确认当前页面为项目页面且包含 "Create deployment" 按钮
2. 确认 `DEPLOY_SOURCE_PATH` 指向的文件夹存在
3. 确认文件夹内包含有效静态文件（如 `index.html`）

### 2. 触发 Create deployment

1. 在页面中定位 "Create deployment" 按钮
   - 通常位于部署历史列表上方或页面右上角
   - 也可能显示为 "+" 图标按钮
2. 点击按钮，等待弹出部署方式选择面板

### 3. 选择 folder upload

1. 在弹出的面板中选择 "Upload assets" 或 "Upload a folder" 选项
2. 等待文件选择对话框打开（系统原生文件选择器）

### 4. 文件选择对话框操作

1. 在文件选择对话框中导航到 `DEPLOY_SOURCE_PATH`
2. 选中该文件夹（或文件夹内的内容，视对话框行为而定）
3. 点击 "选择文件夹" / "Upload" / "打开" 确认

> **注意**：文件选择对话框为系统原生组件，浏览器自动化工具需支持文件上传句柄注入。

### 5. 等待部署完成

1. 文件上传开始后，Cloudflare 页面显示部署进度
2. 轮询检查部署状态：
   - 页面显示 "Building..." / "Deploying..."
   - 部署历史列表中出现新的部署记录
3. 等待状态变为 "Success" 或 "Active"
   - 超时时间：建议 5 分钟（根据文件大小调整）

### 6. 获取部署链接

部署成功后，从页面提取以下链接：

| 链接类型 | 来源 | 示例 |
|----------|------|------|
| 预览链接 | 部署详情中的预览 URL | `https://{hash}--{project}.pages.dev` |
| 生产链接 | 项目设置中的自定义域或默认域 | `https://{project}.pages.dev` |

---

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `source_path` | string | 是 | 要上传的文件夹绝对路径 |
| `timeout_ms` | number | 否 | 部署等待超时，默认 300000（5分钟） |

---

## 输出

| 状态 | 含义 | 返回数据 |
|------|------|----------|
| `DEP_OK` | 部署成功 | `{ preview_url, production_url, deploy_id }` |
| `DEP_001` | 源文件夹不存在 | — |
| `DEP_002` | 文件选择对话框超时 | — |
| `DEP_003` | 部署失败 | `{ error_message }` |
| `DEP_004` | 部署超时 | — |

---

## 部署状态判断

| 页面显示 | 状态 | 动作 |
|----------|------|------|
| "Building..." / "Uploading..." | 进行中 | 继续等待 |
| "Success" / "Active" / 绿色对勾 | 成功 | 提取链接并返回 |
| "Failed" / "Error" / 红色警告 | 失败 | 提取错误信息，返回 DEP_003 |
| 无变化超过超时时间 | 超时 | 返回 DEP_004 |

---

## 注意事项

- **文件夹内容**：确保 `dist` 文件夹包含 `index.html`，否则部署后访问会 404
- **文件大小**：大文件上传耗时较长，适当调整超时时间
- **重复部署**：同一项目短时间内多次部署可能排队，需等待前一次完成
- **浏览器文件选择器**：不同操作系统（Windows/macOS/Linux）的文件选择对话框行为不同，需针对性处理
