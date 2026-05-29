---
name: supabase-browser-skill
description: "Supabase 浏览器自动化子技能。操作 Supabase Dashboard，执行 SQL、管理表并验证数据状态。"
metadata:
  parent: "browser-automation"
  type: "browser-automation-child"
---

# supabase-browser-skill

通过浏览器自动化操作 Supabase Dashboard，执行 SQL、管理表、查看数据。

---

## 触发条件

用户输入匹配以下任一模式时激活：
- "操作 Supabase"
- "登录 Supabase"
- "在 Supabase 中..."
- "Supabase SQL"
- "Supabase 表"
- "帮我操作 Supabase"
- "Supabase 数据库"
- "Supabase 部署"
- "配置 Supabase"

---

## 能力边界

| 能力 | 说明 |
|------|------|
| 浏览器登录 | 自动导航到 Supabase Dashboard 并完成身份验证 |
| SQL 执行 | 在 SQL Editor 中创建、编辑、运行查询 |
| 表管理 | 查看表结构、验证表是否存在 |
| 数据查看 | 读取表数据（只读或根据权限） |

---

## 安全规则（不可覆盖）

1. 密码必须从环境变量读取，禁止硬编码到任何文件
2. 禁止在日志、聊天记录中输出明文密码
3. 2FA 验证码由用户手动输入，禁止自动化绕过
4. 会话 token 仅保存在内存，禁止持久化到磁盘

---

## 使用流程

```
检查凭证  →  登录  →  定位项目  →  执行任务  →  验证结果
```

1. **检查凭证**：读取 `SUPABASE_EMAIL`、`SUPABASE_PASSWORD` 环境变量；缺失时提示用户配置
2. **登录**：调用 `components/01-auth` 完成浏览器登录
3. **定位项目**：根据 `SUPABASE_PROJECT_ID` 或用户指定进入对应项目
4. **执行任务**：根据用户意图调用 SQL Editor 或 Table Manager
5. **验证结果**：截图或读取页面元素确认操作成功

---

## 组件索引

| 组件 | 路径 | 职责 |
|------|------|------|
| 认证 | `components/01-auth/SKILL.md` | 登录、2FA、会话保持 |
| SQL 编辑器 | `components/02-sql-editor/SKILL.md` | 打开、执行、验证 SQL |
| 表管理 | `components/03-table-manager/SKILL.md` | 查看表结构、验证存在性 |

---

## 环境变量

参见 `.env.example`

---

## 错误码

| 错误码 | 含义 | 处理建议 |
|--------|------|----------|
| AUTH_001 | 环境变量缺失 | 检查 `.env` 文件 |
| AUTH_002 | 登录失败 | 确认邮箱密码正确 |
| AUTH_003 | 2FA 要求 | 等待用户输入验证码 |
| AUTH_004 | 会话过期 | 重新执行登录流程 |
| SQL_001 | 查询执行失败 | 检查 SQL 语法 |
| SQL_002 | 超时未返回 | 检查网络或查询复杂度 |
| TBL_001 | 表不存在 | 确认表名或项目 |
