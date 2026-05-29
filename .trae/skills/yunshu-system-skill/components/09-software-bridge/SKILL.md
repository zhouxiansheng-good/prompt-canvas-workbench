---
name: 09-software-bridge
description: "软件桥接元技能。把领域上下文包映射为可执行的软件技能、命令构建和沙箱执行流程。"
metadata:
  phase: "2"
  type: "optional-component"
---

# 09-software-bridge — 软件桥接元技能

> 把领域上下文包翻译成可执行的软件操作命令，让大模型直接操作专业软件。

<!-- L1:START -->
触发条件：08-domain-guide 生成上下文包且包含 software_skills 时自动触发。或用户显式要求"操作[软件名]"时激活。
<!-- L1:END -->

## 适用 / 不适用

- **适用**：需要操作专业软件的任务（CAD、Revit、鸿业、纬地等）、有明确软件技能注册的场景、领域上下文包已包含 software_skills
- **不适用**：纯代码开发任务、无对应软件技能注册的场景、软件不可CLI/API调用

## 全局交互规则

遵循云舒系统全局交互规则（见 SKILL.md 主入口）。

**额外规则**：
- 执行命令前必须向用户确认（高风险操作）
- 命令执行后必须验证结果
- 失败时提供明确的错误信息和回滚方案

**命令确认交互**（Trae IDE）：
执行任何软件操作命令前，调用 `AskUserQuestion`：
- 问题："即将执行：[命令描述]。是否确认？"
- 选项："确认执行" / "取消" / "查看回滚方案"
- 用户选择"查看回滚方案" → 展示回滚方式后继续询问

---

<!-- L2:START -->
## 流程路由

### 顶层路由：软件技能匹配

```
用户意图 → 匹配子技能 → 加载子技能SKILL.md → 子技能自路由 → 执行
```

**元技能职责边界**：本文件（09-software-bridge）只负责**识别用户意图**并**路由到正确的子技能入口**。具体的操作步骤、认证流程、执行细节全部由子技能自身管理。

**嵌套加载规则**：
1. 匹配到子技能后，立即读取该子技能的 `SKILL.md`
2. 将用户原始意图完整传递给子技能
3. 子技能内部可继续嵌套（子技能 → 组件 → 子组件），深度无限制
4. 每一层只加载当前层需要的上下文，不向上层泄露下层细节

| 阶段 | 产物 | 说明 |
|------|------|------|
| 匹配 | 子技能路径 | 根据用户意图匹配子技能（见下方路由表） |
| 加载 | 子技能对象 | 读取对应子技能的 `SKILL.md` |
| 委托 | 执行权转移 | 将用户意图传递给子技能，由子技能自路由 |
| 验证 | 子技能执行结果 | 验证子技能是否成功完成 |

> **回退机制**：子技能未匹配或加载失败时，回退到手动操作指导（生成操作步骤说明）。

### 子技能路由表

| 用户意图关键词 | 子技能路径 | 子技能职责 | 优先级 |
|----------------|------------|------------|--------|
| "部署网站" / "部署到 Cloudflare" / "帮我部署" / "发布网站" | `cli-deployment/cloudflare-pages/` | **CLI 方式部署**（推荐，稳定可靠） | 🔴 首选 |
| "部署网站" / "部署到 Cloudflare" / "帮我部署" / "发布网站" | `browser-automation/cloudflare/` | 浏览器自动化部署（CLI 不可用时的降级方案） | 🟡 降级 |
| "操作 Supabase" / "Supabase 数据库" / "配置 Supabase" | `browser-automation/supabase/` | Supabase Dashboard 操作 |
| "审查合规" / "法律风险" / "合规检查" / "帮我审查" | `../04-accept/compliance-audit/` | 项目法律合规审查；`browser-automation/compliance/` 仅保留旧入口跳转 |
| "浏览器自动化" / "打开浏览器" / "操作网站" | `browser-automation/` | 通用浏览器自动化（需进一步路由） |

**路由优先级**：精确匹配 > 模糊匹配。如用户说"部署到 Cloudflare"，直接路由到 `cloudflare/`，不经过 `browser-automation/` 中间层。

## 输入输出

**输入**：领域上下文包（来自 08-domain-guide）+ 软件技能注册表

**输出**：执行结果报告

```json
{
  "status": "success | partial | failed",
  "software_id": "hongye-municipal-road",
  "commands_executed": [
    {
      "command": "CreateProject --name Project1 --type municipal --grade arterial",
      "exit_code": 0,
      "output": "Project created successfully",
      "execution_time": "2.3s"
    }
  ],
  "results": {
    "files_created": ["Project1.hyprj"],
    "errors": [],
    "warnings": []
  },
  "verification": {
    "method": "文件存在性检查",
    "result": "passed"
  }
}
```

---

## 软件桥接留底（强制）

> 软件操作命令和结果是关键证据，必须留底。

**执行完成后必须记录**：

```bash
python scripts/yunshu.py context record \
  --task-id <task_id> \
  --phase software-bridge \
  --source "<执行的命令和参数>" \
  --finding "<执行结果摘要：成功/失败/部分成功>" \
  --action "<已执行的软件操作>" \
  --gap "<未完成的操作或错误待修复>" \
  --next-read "<验证阶段需检查的文件>"
python scripts/yunshu.py validate context .yunshu/context/<context_id>.json
```

**高价值场景**：
- 部署操作（如 Cloudflare Pages 部署）→ 记录部署 URL、构建日志路径
- 数据库操作（如 Supabase SQL 执行）→ 记录执行的 SQL 和返回结果
- 合规审查 → 记录审查结论和修复建议

**硬规则**：软件操作没有留底 → 不许宣称操作完成

## 核心能力

| 能力 | 关键方法 | 毛选思想 |
|------|----------|----------|
| 软件匹配 | software_skills 匹配 + 注册表索引 | 调查研究：先找到合适的工具 |
| 参数映射 | 领域上下文 → 软件参数转换 | 具体问题具体分析：每个软件参数映射都不同 |
| 命令构建 | 模板填充 + 参数验证 | 集中优势兵力：一次构建一条命令 |
| 执行验证 | 沙箱执行 + 结果验证 | 实践是检验真理的唯一标准 |

## 反模式

- 🚫 执行命令前不向用户确认（高风险必停）
- 🚫 不验证执行结果就宣称成功（实践是检验真理的唯一标准）
- 🚫 忽略软件版本兼容性（具体问题具体分析）
- 🚫 一次执行多个不相关的命令（集中优势兵力）

---

## 子技能（嵌套模块）

| 子技能 | 路径 | 触发条件 | 说明 |
|--------|------|----------|------|
| **cli-deployment** | `cli-deployment/` | "部署网站"、"部署到 Cloudflare"、"发布网站"、"上传 dist"、"帮我部署" | **CLI 命令行部署**（推荐），含 Cloudflare Pages 等 |
| **browser-automation** | `browser-automation/` | "浏览器自动化"、"打开浏览器操作" | 浏览器自动化操作（降级方案） |

### cli-deployment 子模块

| 子模块 | 路径 | 触发条件 | 说明 |
|--------|------|----------|------|
| **cloudflare-pages** | `cli-deployment/cloudflare-pages/` | "部署网站"、"部署到 Cloudflare"、"Cloudflare Pages 部署"、"上传 dist"、"发布到 Cloudflare"、"帮我部署" | **wrangler CLI 部署**，稳定可靠，替代浏览器自动化方案 |

### browser-automation 子模块

| 子模块 | 路径 | 触发条件 | 说明 |
|--------|------|----------|------|
| **cloudflare** | `browser-automation/cloudflare/` | CLI 不可用时的降级方案 | Cloudflare Pages 浏览器自动化部署（已废弃，保留兼容） |
| **supabase** | `browser-automation/supabase/` | "操作 Supabase" | Supabase Dashboard 登录、SQL 执行、表管理 |
| **compliance** | `../04-accept/compliance-audit/` | "审查合规"、"法律风险"、"合规检查" | 全面审查网站项目的法律合规性；`browser-automation/compliance/` 仅作旧入口兼容 |

---

## 目录导航

| 层级 | 内容 | 路径 |
|------|------|------|
| L3 | 软件注册表 Schema | `software-registry-schema.json` |
| L3 | 命令构建规范 | `command-builder.md` |
| L3 | 执行沙箱规范 | `execution-sandbox.md` |
| L3 | 注册表子目录 | `registry/` |
| L3 | 示例软件注册表 | `registry/example-software.json` |
| L3 | 浏览器自动化子技能 | `browser-automation/SKILL.md` |
| L3 | Supabase Dashboard 操作 | `browser-automation/supabase/SKILL.md` |

<!-- L2:END -->
