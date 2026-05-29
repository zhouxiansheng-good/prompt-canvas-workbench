---
name: supabase-table-manager
description: "Supabase 表管理组件。打开 Table Editor，查看表结构并验证表是否存在。"
metadata:
  parent: "supabase-browser-skill"
  type: "browser-automation-step"
---

# 03-table-manager — 表管理

查看表结构、验证表是否存在。

---

## 前置条件

- 已通过 `components/01-auth` 完成登录
- 已定位到目标项目

---

## 打开 Table Editor

1. 确认当前处于项目内（URL 包含 `/project/{project_ref}`）
2. 点击左侧导航 "Table Editor"
3. 等待页面加载（判断依据：表列表或 "New table" 按钮可见）

---

## 查看表结构

### 定位表

1. 在表列表中查找目标表名
2. 点击表名进入详情页

### 读取结构信息

提取以下信息：
- 列名、数据类型、默认值
- 是否可空（Nullable）
- 是否主键（Primary Key）
- 外键关系（Foreign Keys）
- 索引（Indexes）
- RLS 策略状态（是否启用）

向用户返回结构摘要。

---

## 验证表是否存在

1. 在 Table Editor 的表列表中搜索目标表名
2. 若列表中存在该表名，返回 `exists: true`
3. 若不存在，返回 `exists: false`（错误码 `TBL_001`）

---

## 错误处理

| 场景 | 检测方式 | 处理动作 |
|------|----------|----------|
| 表不存在 | 表列表中无目标表名 | 返回 `TBL_001`，提示确认表名 |
| 页面加载失败 | 10s 内未出现表列表 | 刷新重试 1 次 |
| 权限不足 | 提示 "You don't have permission" | 提示检查项目权限 |

---

## 接口定义

```
open_table_editor(project_ref: string): Result<void, Error>
  - 打开指定项目的 Table Editor

list_tables(): Result<string[], Error>
  - 返回当前项目下所有表名列表

describe_table(table_name: string): Result<TableSchema, Error>
  - 返回指定表的完整结构信息

table_exists(table_name: string): Result<bool, Error>
  - 快速验证表是否存在
```

---

## TableSchema 结构

```
TableSchema {
  name: string,
  columns: Column[],
  primary_key: string[],
  foreign_keys: ForeignKey[],
  indexes: Index[],
  rls_enabled: bool
}

Column {
  name: string,
  type: string,
  nullable: bool,
  default: string | null
}
```
