---
name: supabase-sql-editor
description: "Supabase SQL Editor 操作组件。创建、执行查询并验证执行结果。"
metadata:
  parent: "supabase-browser-skill"
  type: "browser-automation-step"
---

# 02-sql-editor — SQL Editor 操作

在 Supabase Dashboard 的 SQL Editor 中创建、执行查询并验证结果。

---

## 前置条件

- 已通过 `components/01-auth` 完成登录
- 已定位到目标项目

---

## 打开 SQL Editor

1. 确认当前处于项目内（URL 包含 `/project/{project_ref}`）
2. 点击左侧导航 "SQL Editor"
3. 等待页面加载（判断依据：编辑器区域或 "New query" 按钮可见）

---

## 创建/执行查询

### 新建查询

1. 点击 "New query" 或 "+" 按钮
2. 等待编辑器就绪（`textarea` 或 Monaco 编辑器挂载）

### 输入 SQL

1. 将用户提供的 SQL 语句输入编辑器
2. 若编辑器为 Monaco，使用 `page.type` 或 `page.evaluate` 注入内容

### 执行查询

1. 点击 "Run" 按钮（或使用快捷键 Ctrl+Enter / Cmd+Enter）
2. 等待执行完成（判断依据：结果区域出现数据表格或成功提示）

---

## 验证执行结果

| 结果类型 | 验证方式 |
|----------|----------|
| 查询成功返回数据 | 结果表格行数 > 0，或明确显示 "N rows" |
| 查询成功无数据 | 显示 "0 rows" 或成功提示 |
| DDL 成功 | 显示 "Success" 或 "Query completed" |
| 执行失败 | 错误面板出现红色错误信息 |

验证通过后，向用户返回结果摘要（行数、耗时、关键数据）。

---

## 错误处理

| 场景 | 检测方式 | 处理动作 |
|------|----------|----------|
| SQL 语法错误 | 错误面板显示语法错误 | 返回 `SQL_001`，提取错误信息给用户 |
| 执行超时 | 30s 内未返回结果 | 返回 `SQL_002`，建议优化查询 |
| 权限不足 | 错误信息包含 "permission denied" | 提示检查 RLS 或数据库权限 |
| 编辑器未加载 | 10s 内未检测到编辑器 | 刷新页面重试 1 次 |

---

## 接口定义

```
open_sql_editor(project_ref: string): Result<void, Error>
  - 打开指定项目的 SQL Editor

execute_sql(sql: string): Result<QueryResult, SqlError>
  - 前置条件：SQL Editor 已打开
  - 执行 SQL 并返回结果
  - 返回：行数、数据摘要、执行耗时
```
