---
name: cloudflare-pages-deploy
description: "Cloudflare Pages 部署子技能。通过浏览器自动化上传静态构建产物、触发部署并验证访问链接。"
metadata:
  parent: "browser-automation"
  type: "browser-automation-child"
---

# cloudflare-pages-deploy — Cloudflare Pages 部署子技能

> 通过浏览器自动化将静态网站部署到 Cloudflare Pages。嵌套于 browser-automation 之下，专司 Cloudflare Pages 项目的上传与部署。

---

## 触发条件

用户输入匹配以下任一模式时激活：
- "部署网站"
- "部署到 Cloudflare"
- "Cloudflare Pages 部署"
- "上传 dist"
- "发布到 Cloudflare"
- "帮我部署" / "部署好" / "部署一下"
- "发布网站" / "上线网站"
- "更新网站" / "重新部署"

---

## 能力边界

| 能力 | 说明 |
|------|------|
| 项目导航 | 自动进入指定 Cloudflare Pages 项目控制台 |
| 文件夹上传 | 通过文件选择对话框上传 dist 文件夹 |
| 部署触发 | 点击 Create deployment 并等待部署完成 |
| 链接获取 | 从部署状态中提取并返回访问链接 |
| 状态验证 | 通过页面元素或截图确认部署成功 |

---

## 安全规则（不可覆盖）

1. **账号隔离**：Cloudflare 账号 ID 和项目 URL 从环境变量读取，禁止硬编码
2. **路径校验**：部署源路径必须存在且为合法目录，禁止上传根目录或系统路径
3. **会话安全**：依赖浏览器已有会话，禁止在自动化中输入密码
4. **截图脱敏**：若截图包含账号敏感信息，需模糊处理
5. **操作确认**：上传前必须确认目标项目和源文件夹路径

---

## 使用流程

```
检查配置  →  验证登录  →  进入项目  →  创建部署  →  选择文件夹  →  等待完成  →  获取链接
```

1. **检查配置**：读取 `CLOUDFLARE_PROJECT_URL`、`DEPLOY_SOURCE_PATH` 环境变量；缺失时提示用户配置
2. **验证登录**：调用 `components/01-auth` 检查浏览器会话状态
3. **进入项目**：调用 `components/02-project` 导航到指定项目页面
4. **创建部署**：调用 `components/03-deploy` 点击 Create deployment 并选择 folder upload
5. **选择文件夹**：在文件选择对话框中导航到 `DEPLOY_SOURCE_PATH` 并确认
6. **等待完成**：轮询部署状态直到成功或失败
7. **获取链接**：从部署结果中提取预览链接或生产链接

---

## 组件索引

| 组件 | 路径 | 职责 |
|------|------|------|
| 认证 | `components/01-auth/SKILL.md` | 检查登录状态、处理未登录场景 |
| 项目选择 | `components/02-project/SKILL.md` | 进入指定项目、验证项目存在性 |
| 部署执行 | `components/03-deploy/SKILL.md` | 触发部署、文件上传、等待结果、获取链接 |

---

## 环境变量

参见 `.env.example`

---

## 错误码

| 错误码 | 含义 | 处理建议 |
|--------|------|----------|
| AUTH_001 | 未检测到登录会话 | 在浏览器中手动登录 Cloudflare |
| AUTH_002 | 会话过期 | 刷新页面或重新登录 |
| PRJ_001 | 项目不存在 | 检查 `CLOUDFLARE_PROJECT_NAME` 是否正确 |
| PRJ_002 | 项目 URL 不可访问 | 检查网络或账号权限 |
| DEP_001 | 源文件夹不存在 | 检查 `DEPLOY_SOURCE_PATH` 路径 |
| DEP_002 | 文件选择对话框超时 | 检查浏览器文件选择器是否正常 |
| DEP_003 | 部署失败 | 查看 Cloudflare 控制台错误信息 |
| DEP_004 | 部署超时 | 检查网络或文件大小是否过大 |

---

## 目录导航

| 层级 | 内容 | 路径 |
|------|------|------|
| L3 | Cloudflare Pages 部署入口 | `cloudflare/SKILL.md` |
| L3 | 认证组件 | `cloudflare/components/01-auth/SKILL.md` |
| L3 | 项目组件 | `cloudflare/components/02-project/SKILL.md` |
| L3 | 部署组件 | `cloudflare/components/03-deploy/SKILL.md` |
| L3 | 安全指南 | `cloudflare/guides/01-security.md` |
| L3 | 环境变量示例 | `cloudflare/.env.example` |
