---
name: supabase-auth
description: "Supabase Dashboard 认证组件。处理浏览器登录、2FA 提示和会话保持。"
metadata:
  parent: "supabase-browser-skill"
  type: "browser-automation-step"
---

# 01-auth — Supabase Dashboard 认证

负责浏览器环境下的登录、2FA 处理、会话保持。

---

## 环境变量要求

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `SUPABASE_EMAIL` | 是 | Supabase 账号邮箱 |
| `SUPABASE_PASSWORD` | 是 | Supabase 账号密码 |
| `SUPABASE_PROJECT_ID` | 否 | 多项目时指定默认项目 |

缺失任一必填变量时，立即返回 `AUTH_001` 并提示用户配置 `.env`。

---

## 登录流程

### Step 1: 导航到登录页

打开 `https://supabase.com/dashboard/sign-in`

等待页面加载完成（判断依据：`input[type="email"]` 可见）。

### Step 2: 输入凭证

1. 在邮箱输入框填入 `SUPABASE_EMAIL`
2. 在密码输入框填入 `SUPABASE_PASSWORD`
3. 点击登录按钮（或触发表单提交）

### Step 3: 处理 2FA

检测页面是否出现 2FA 输入框：
- **出现**：暂停自动化，提示用户手动输入验证码；用户提交后继续
- **未出现**：直接进入 Step 4

### Step 4: 确认登录成功

验证以下任一条件：
- URL 变为 `https://supabase.com/dashboard/projects` 或包含 `/project/`
- 页面出现项目列表或项目侧边栏
- 出现用户头像/账号菜单

满足则返回 `success`；否则进入错误处理。

---

## 错误处理

| 场景 | 检测方式 | 处理动作 |
|------|----------|----------|
| 邮箱或密码错误 | 页面出现 "Invalid credentials" 或类似文案 | 返回 `AUTH_002`，提示检查凭证 |
| 2FA 要求 | 出现验证码输入框 | 返回 `AUTH_003`，等待用户输入 |
| 会话过期 | 后续操作被重定向到登录页 | 返回 `AUTH_004`，重新执行登录流程 |
| 网络超时 | 页面 10s 内未加载完成 | 重试 1 次，仍失败则报错 |

---

## 会话保持

- 登录成功后，浏览器上下文保持打开
- 会话 token 仅驻留内存，不写入文件
- 若检测到会话失效（被重定向到登录页），自动触发重新登录

---

## 接口定义

```
login(): Result<Session, AuthError>
  - 前置条件：环境变量已加载
  - 后置条件：浏览器处于已登录状态
  - 副作用：打开浏览器标签页，可能弹出 2FA 提示

ensure_session(): Result<Session, AuthError>
  - 检查当前是否已登录，若否则调用 login()
```
