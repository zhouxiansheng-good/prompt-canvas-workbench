---
name: bmad-enhance
description: "BMad Method 增强层：把 PRD、架构、Story 和 project-context 映射进云舒任务卡、计划规范、执行分派包和上下文账本。"
metadata:
  phase: "optional"
---

# bmad-enhance：BMad 上下文工程增强层

> 云舒负责判断和验收，BMad 负责把复杂需求变成更好的上下文燃料。

## 定位

`bmad-enhance` 是云舒系统的**可选增强层**，不是第二套主流程。它只在复杂规划、产品化需求、跨模块架构、Story 拆分或用户明确要求 BMad 融合时加载。

云舒主流程保持不变：

```text
01-init -> 02-plan -> 03-execute / 07-subagent -> 04-accept -> 05-deliver
```

BMad 产物进入云舒后，必须服从云舒的任务卡、上下文账本、证据链、门控检查和验收标准。

## 适用 / 不适用

**适用**：

- 产品规划、复杂功能、跨模块架构设计
- 需要 PRD、Architecture、Story 逐层传递上下文
- 子智能体分派前，需要把复杂任务压缩成自包含分派包
- 现有项目需要沉淀 `project-context.md` 作为实现规则摘要

**不适用**：

- 单文件微调
- 简单 Bug 修复
- 用户只要快速问答
- 任务还没有通过 01-init 的任务卡门禁
- 没有证据或验收标准的“角色讨论”

## 触发规则

满足以下任一条件时，可加载本组件：

1. 用户明确提到 BMad、PRD、Story、Architecture、project-context 或 “BMad 融合”。
2. 02-plan 发现任务数较多，且上下文传递风险高。
3. 07-subagent 分派前，需要把任务包装成更完整的 Story 分派包。
4. 复杂架构决策需要先把 BMad 文档流映射为云舒 ADR、WBS 和测试策略。

## 子组件路由表

| 用户意图 | 子组件路径 | 子组件职责 |
|----------|------------|------------|
| "PRD映射" / "需求文档" / "Tech Spec" / "产品文档" | `prd-map.md` | 任务卡、PRD、Tech Spec 的字段映射规则 |
| "架构映射" / "Architecture" / "ADR" / "WBS" | `architecture-map.md` | Architecture 到 spec、ADR、WBS、风险的映射 |
| "Story映射" / "用户故事" / "分派包" | `story-map.md` | Story 到执行任务、分派包、验收证据的映射 |
| "项目上下文" / "project-context" / "规则同步" | `project-context-sync.md` | `.yunshu/context/` 与 `project-context.md` 的同步规则 |
| "Party Mode" / "多角色讨论" / "角色扮演" | `party-mode-gate.md` | 多角色讨论何时允许、如何落回云舒产物 |
| "BMad CLI" / "CLI适配" / "命令行" | `bmad-cli-adapter.md` | BMad CLI 的可选适配边界 |

## 执行流程

### Step 1：确认云舒任务卡

进入本组件前，必须已经有云舒任务卡：

```yaml
goal: string
done_definition: string[]
constraints: string[]
risks: string[]
non_goals: string[]
```

没有任务卡时，回到 `components/01-init/SKILL.md`。

### Step 2：选择映射路径

| 输入材料 | 加载文件 | 输出 |
|----------|----------|------|
| PRD / Product Brief / Tech Spec | `prd-map.md` | 任务卡增强、验收标准、开放问题 |
| Architecture | `architecture-map.md` | spec 增强、ADR、风险、测试策略 |
| Story | `story-map.md` | 执行任务、子智能体分派包 |
| project-context.md / 项目规则 | `project-context-sync.md` | 实现规则摘要、上下文账本 |

### Step 3：记录 BMad 映射（强制）

> **硬规则**：每次吸收 BMad 产物后，必须执行 `bmad map`，不许跳过。

```bash
python scripts/yunshu.py bmad map \
  --task-id <task_id> \
  --kind <prd|architecture|story|project-context> \
  --source <bmad-artifact-path> \
  --gap "<仍缺什么>" \
  --next-read "<下一轮只需补读什么>"
python scripts/yunshu.py bmad validate .yunshu/bmad/<map_id>.json
```

`bmad map` 会同时生成 `.yunshu/bmad/<map_id>.json`、`.md`，并自动写入 `.yunshu/context/`。

**验证映射结果**：

```bash
python scripts/yunshu.py bmad status <map_id>
python scripts/yunshu.py bmad validate .yunshu/bmad/<map_id>.json
```

**创建 BMad 阶段检查点**（强制）：

```bash
python scripts/yunshu.py checkpoint create \
  --task-id <task_id> \
  --phase bmad-enhance \
  --summary "<BMad映射完成摘要>" \
  --completed "<已映射的BMad产物>" \
  --pending "<待执行的任务>" \
  --artifact ".yunshu/bmad/<map_id>.json" \
  --next-action "<进入02-plan或03-execute>"
python scripts/yunshu.py validate checkpoint .yunshu/checkpoints/<checkpoint_id>/checkpoint.json
```

**硬规则**：没有执行 `bmad map` 和 `checkpoint create` → 不许进入下一步

### Step 4：进入云舒原阶段

映射完成后，不在本组件内直接实现代码：

- PRD / Architecture 映射完成 -> 回到 `components/02-plan/SKILL.md`
- Story 映射完成 -> 进入 `components/03-execute/SKILL.md` 或 `components/07-subagent/SKILL.md`
- project-context 同步完成 -> 回到当前阶段继续

## 硬规则

1. **云舒主流程优先**：BMad 不能绕过任务卡、计划、验收和交付。
2. **证据化优先**：BMad 文档是上下文来源，不是验收证据本身。
3. **不替换子智能体**：BMad 角色只作为规划视角或文档来源，不替换 `yunshu-implementer`、`yunshu-spec-reviewer`、`yunshu-quality-reviewer`。
4. **不默认启用 Party Mode**：多角色讨论属于可选讨论机制，未触发门禁或未经用户要求时不进入默认流程。
5. **缺口必须显式记录**：BMad 文档未覆盖的字段，不允许脑补，必须写入 gaps 或返回澄清。

## 模板

| 模板 | 用途 |
|------|------|
| `templates/bmad_prd_map.md` | PRD / Tech Spec 到云舒任务卡的映射表 |
| `templates/bmad_architecture_map.md` | Architecture 到云舒 spec / ADR 的映射表 |
| `templates/bmad_story_map.md` | Story 到云舒执行分派包的映射表 |
| `templates/bmad_project_context.md` | project-context 摘要模板 |

## 可执行工具

| 命令 | 用途 | 产物 |
|------|------|------|
| `python scripts/yunshu.py bmad map --task-id <id> --kind <kind> --source <path>` | 记录 BMad 产物映射 | `.yunshu/bmad/<map_id>.json` + `.md` + context ledger |
| `python scripts/yunshu.py bmad status <map_id>` | 检查映射来源 fresh/stale/missing | 终端状态码 |
| `python scripts/yunshu.py bmad validate <file>` | 校验 BMad 映射结构 | 结构化校验结果 |

## 路由

- 缺少任务卡 -> `components/01-init/SKILL.md`
- PRD/Architecture 映射完成 -> `components/02-plan/SKILL.md`
- Story 映射完成且任务紧耦合 -> `components/03-execute/SKILL.md`
- Story 映射完成且用户明确授权子智能体 -> `components/07-subagent/SKILL.md`
- 验收 BMad 产物影响 -> `components/04-accept/SKILL.md`

## 反模式

- 跳过云舒任务卡，直接按 PRD 写代码
- 把 BMad code-review 当成云舒验收通过
- 让命名代理替代规范审查和质量审查
- 把 project-context 当成永久正确，不检查新鲜度
- 为简单任务强行生成 PRD、Architecture、Story
