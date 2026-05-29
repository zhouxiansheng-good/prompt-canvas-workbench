---
name: cloudflare-auth
description: "Cloudflare Pages 认证组件。检查浏览器登录状态并确保会话有效。"
metadata:
  parent: "cloudflare-pages-deploy"
  type: "browser-automation-step"
---

# Cloudflare Pages — 认证组件

> 检查并确保浏览器已登录 Cloudflare 账号。Cloudflare 通常保持长期会话，本组件以验证为主。

---

## 职责

- 检测当前浏览器是否已登录 Cloudflare
- 未登录时导航到登录页并提示用户手动完成
- 确认会话有效后方可继续后续操作

---

## 操作流程

### 1. 检查登录状态

1. 导航到 `https://dash.cloudflare.com`
2. 等待页面加载完成
3. 检查页面元素判断登录状态：
   - **已登录**：页面显示用户头像、账号信息或 Dashboard 内容
   - **未登录**：页面重定向到 `https://dash.cloudflare.com/login` 或显示登录表单

### 2. 已登录场景

- 确认页面 URL 包含 `dash.cloudflare.com` 且非登录页
- 可选：截图保存当前状态作为基线
- 返回 `AUTH_OK`，继续执行后续组件

### 3. 未登录场景

1. 导航到 `https://dash.cloudflare.com/login`
2. 截图提示用户：
   - "检测到未登录 Cloudflare，请在浏览器中完成登录"
   - "登录完成后请回复 '已登录' 继续"
3. 等待用户确认
4. 用户确认后重新检查登录状态
5. 若仍检测到未登录，返回 `AUTH_001`

---

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `target_url` | string | 否 | 目标项目 URL，用于快速验证权限 |

---

## 输出

| 状态 | 含义 | 后续动作 |
|------|------|----------|
| `AUTH_OK` | 已登录且会话有效 | 进入项目选择组件 |
| `AUTH_001` | 未检测到登录会话 | 提示用户手动登录 |
| `AUTH_002` | 会话过期 | 刷新页面或重新登录 |

---

## 注意事项

- **禁止自动化输入密码**：Cloudflare 登录凭证必须由用户在浏览器中手动输入
- **2FA 处理**：若账号开启两步验证，等待用户手动完成
- **会话保持**：Cloudflare 会话通常长期有效，无需每次重新登录
- **多账号场景**：若浏览器登录了多个账号，以当前活跃会话为准
