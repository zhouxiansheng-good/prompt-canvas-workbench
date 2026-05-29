# BMad Method × 云舒系统增强方案 V1

> 日期：2026-05-12
> 阶段：方案设计，不进入代码实现
> 方法：云舒系统（调查研究 → 主要矛盾 → 阶段判断 → 计划规范 → 验收定义）
> 关联上下文账本：`bmad-yunshu-fusion-analysis-plan-20260512-211613`

---

## 1. 任务卡

### 1.1 目标

在不破坏云舒系统现有“证据化、门控、恢复、安全防护”主流程的前提下，引入 BMad Method 的上下文工程、PRD/架构/Story 文档流和多角色协作能力，形成一个可渐进落地的 `bmad-enhance` 增强模块。

### 1.2 完成定义

- 方案明确回答：BMad 能增强云舒哪些能力、哪些能力暂不进入默认流程。
- 方案给出 V1 的模块边界、文件结构、流程映射、输入输出契约和实施顺序。
- 方案保留云舒主流程和硬规则，不要求一开始安装或强依赖 BMad CLI。
- 方案定义后续实现时的验收标准、风险、回滚策略和证据要求。

### 1.3 约束

- 云舒是主流程和门禁系统，BMad 只能作为增强层或可选工作流。
- 第一版先做文件协议和文档映射，不做深度 CLI 耦合。
- 不把 BMad 命名代理直接替换云舒现有三类子智能体。
- Party Mode 不进入 P0，只作为复杂决策的可选机制。
- 所有 BMad 产物进入云舒后，必须经过云舒的上下文账本、证据链和验收门禁。

### 1.4 非目标

- 不在 V1 实现完整 BMad 安装器封装。
- 不在 V1 实现双向自动同步所有 BMad 文档。
- 不在 V1 新增超过 3 个默认子智能体角色。
- 不在 V1 修改云舒 01-init 到 05-deliver 的主路由。
- 不在 V1 把 Party Mode 作为默认规划方式。

---

## 2. 调研结论

### 2.1 已读材料

- `BMad-云舒融合分析报告.md`
- `BMAD-METHOD-README.md`
- `BMAD-METHOD-详细文档.md`
- `yunshu-system-skill/SKILL.md`
- `yunshu-system-skill/components/02-plan/SKILL.md`
- `yunshu-system-skill/components/07-subagent/SKILL.md`
- `yunshu-system-skill/safeguards/meta-cognition.md`
- `yunshu-system-skill/safeguards/architecture.md`
- `yunshu-system-skill/safeguards/agent-safety.md`
- `yunshu-system-skill/safeguards/maintenance.md`

### 2.2 关键判断

BMad 的最大价值不是“命名代理很热闹”，而是它把需求、架构、故事、实现上下文串成了连续文档流。云舒当前已经有强门禁和证据机制，但产品规划、PRD 化、Story 化和项目上下文“宪法”能力还可以增强。

因此，融合重点应从“代理人格合并”转向“上下文工程合并”。

### 2.3 主要矛盾

表层问题：云舒想增强 BMad 能力，但直接融合会增加复杂度。

5-Why：

```text
为什么直接融合会复杂？
  因为 BMad 有独立代理、命令、文档流和工作流地图。
为什么这些会冲击云舒？
  因为云舒已有阶段门控、子智能体、上下文账本和验收机制。
为什么会冲突？
  因为两套系统都试图定义“谁来规划、谁来执行、谁来审查”。
为什么不能简单叠加？
  因为叠加会导致用户不知道当前该服从云舒阶段，还是 BMad 角色/工作流。
根因：
  缺少一个明确的融合边界：BMad 应作为上下文工程增强层，而不是第二套主流程。
```

主要矛盾：如何吸收 BMad 的上下文工程能力，同时不稀释云舒的证据化主流程。

次要矛盾：

- 命名代理是否替换云舒子智能体。
- BMad CLI 是否成为云舒运行依赖。
- Party Mode 是否进入默认决策流。
- BMad 文档产物如何接入云舒验收证据。

---

## 3. 架构决策

### ADR-001：采用“云舒主流程 + BMad 增强层”

**背景**：云舒已有稳定阶段路由和门禁，BMad 的价值集中在规划文档流和上下文工程。

**选项**：

- A：把 BMad 整体并入云舒主流程。优点是能力完整；缺点是复杂度高，主流程会失焦。
- B：只抽取 BMad 上下文工程能力，做成云舒增强模块。优点是风险低、可渐进；缺点是第一版不会覆盖全部 BMad 能力。
- C：保持两套系统完全独立。优点是无集成风险；缺点是用户需要手工搬运上下文。

**决策**：选择 B。

**影响**：新增 `bmad-enhance` 模块，但不改变现有 01-init、02-plan、03-execute、04-accept、05-deliver 主流程。

**可逆性**：高。若效果不好，可删除增强模块和映射文档，不影响云舒核心。

### ADR-002：V1 使用文件协议，不强依赖 BMad CLI

**背景**：BMad CLI 与云舒 Python CLI 技术栈不同，直接耦合会增加安装、版本和平台适配成本。

**选项**：

- A：云舒直接调用 `npx bmad-method`。
- B：云舒只读取/生成约定 Markdown 文档，BMad CLI 作为可选外部工具。
- C：重新实现 BMad 工作流。

**决策**：选择 B。

**影响**：V1 可在没有 BMad CLI 的环境中先落地文档映射；后续再验证 CLI schema。

**可逆性**：高。文件协议稳定后，可以逐步增加 CLI 适配器。

### ADR-003：命名代理暂不替换云舒子智能体

**背景**：云舒当前三类子智能体围绕实现、规范审查、质量审查设计，和证据化验收强绑定。

**选项**：

- A：直接升级为 BMad 6 个命名代理。
- B：保留云舒三类子智能体，把 BMad 角色作为分派模板或决策视角。
- C：完全不引入 BMad 角色。

**决策**：选择 B。

**影响**：实现阶段仍由 `yunshu-implementer`、`yunshu-spec-reviewer`、`yunshu-quality-reviewer` 执行；BMad 的 Analyst/PM/Architect/UX/Writer 主要用于计划和文档增强。

**可逆性**：中。若后续证明确有价值，可逐步新增角色模板。

---

## 4. V1 模块设计

### 4.1 推荐目录结构

```text
yunshu-system-skill/
  components/
    bmad-enhance/
      SKILL.md
      prd-map.md
      architecture-map.md
      story-map.md
      project-context-sync.md
      party-mode-gate.md
  templates/
    bmad_prd_map.md
    bmad_architecture_map.md
    bmad_story_map.md
    bmad_project_context.md
  schemas/
    bmad_mapping.schema.json
```

### 4.2 模块职责

| 文件 | 职责 | 默认阶段 |
|------|------|----------|
| `components/bmad-enhance/SKILL.md` | 增强模块入口和触发规则 | 全局按需 |
| `prd-map.md` | 任务卡、PRD、Tech Spec 的映射规则 | 01-init / 02-plan |
| `architecture-map.md` | architecture.md 到云舒 spec/ADR/WBS 的映射 | 02-plan |
| `story-map.md` | BMad story 到云舒执行任务/分派包的映射 | 03-execute / 07-subagent |
| `project-context-sync.md` | `.yunshu/context/` 与 `project-context.md` 的同步规则 | 01-init / 02-plan / recover |
| `party-mode-gate.md` | 何时允许多角色讨论，何时禁止 | 02-plan / accept / retrospective |

### 4.3 触发规则

默认不触发。只在以下场景按需加载：

- 用户明确说“使用 BMad / BMad 融合 / PRD / Story / project-context”。
- 任务是产品规划、复杂功能、跨模块架构、需要史诗/故事拆分。
- 计划阶段发现任务数较多、上下文传递风险高。
- 子智能体分派前需要把复杂需求压缩成自包含 Story。

禁止触发：

- 单文件微调。
- 简单 Bug 修复。
- 用户只要快速答案。
- 当前任务还没有通过云舒 01-init 的任务卡门禁。

---

## 5. 流程映射

### 5.1 01-init：任务卡到 PRD 摘要

输入：

- 用户目标
- 云舒任务卡：goal、done_definition、constraints、risks、non_goals
- 可选 BMad PRD / product brief / PRFAQ

输出：

- 云舒任务卡增强版
- `bmad_prd_map.md`
- 上下文账本记录

映射规则：

| 云舒字段 | BMad 字段 | 说明 |
|----------|-----------|------|
| `goal` | Product Goal / Problem Statement | 保持一句话目标 |
| `done_definition` | Acceptance Criteria | 必须可验证 |
| `constraints` | Constraints / Assumptions | 区分硬约束和假设 |
| `risks` | Risks / Open Questions | 风险进入 02-plan |
| `non_goals` | Out of Scope | 防止 PRD 膨胀 |

### 5.2 02-plan：PRD/Architecture 到计划规范

输入：

- 云舒任务卡
- 可选 `PRD.md`
- 可选 `architecture.md`
- 可选 `_bmad-output/project-context.md`

输出：

- `plan.md`
- `spec.md`
- `tasks.md`
- ADR 决策记录
- context ledger

关键动作：

1. 从 PRD 提取目标、用户、场景、验收标准。
2. 从 architecture 提取模块边界、接口、数据流、技术约束。
3. 从 project-context 提取实现规则、技术栈、代码组织约定。
4. 转成云舒 WBS、风险登记表、回滚策略和测试策略。
5. 标记未被 BMad 文档覆盖的缺口，不允许用猜测补齐。

### 5.3 03-execute / 07-subagent：Story 到执行分派包

输入：

- 云舒计划任务
- BMad story 文件
- spec 中的接口契约和测试策略
- project-context 中的实现规则

输出：

- 自包含任务分派包
- 代码变更
- 验证证据
- 子智能体审查报告

Story 分派包必须包含：

- 任务目标
- 用户价值
- 文件写入范围
- 相关上下文
- 接口契约
- 验收标准
- 测试命令
- 非目标
- 风险和回滚点

### 5.4 04-accept：BMad Review 到云舒证据链

输入：

- 代码审查意见
- Story 验收结果
- 测试输出
- 云舒 DoD

输出：

- acceptance evidence
- acceptance runbook
- 未通过项分类

规则：

- BMad code-review 只能作为审查输入，不能替代云舒验收。
- 每条 DoD 必须有新鲜证据。
- 文档产物必须通过链接检查和结构检查。

### 5.5 05-deliver：归档和回滚

输入：

- 云舒变更报告
- BMad PRD/architecture/story/project-context
- 验收证据

输出：

- change_report
- 回滚方案
- 文档同步清单
- 后续 BMad 产物归档路径

---

## 6. 优先级

### P0：上下文工程最小闭环

1. 新增 `components/bmad-enhance/SKILL.md`
2. 新增 `prd-map.md`
3. 新增 `architecture-map.md`
4. 新增 `story-map.md`
5. 新增 `project-context-sync.md`
6. 新增 4 个模板文件
7. 在云舒主 `SKILL.md` 的目录导航中登记该增强模块

P0 验收：能把一个任务卡、一个 PRD、一个 architecture、一个 story 映射成云舒 plan/spec/tasks 和执行分派包。

### P1：工具化与校验

1. 增加 `schemas/bmad_mapping.schema.json`
2. 扩展 `scripts/yunshu.py`，支持 `bmad map/status/validate`
3. 把映射结果写入 `.yunshu/context/`
4. 支持对 `project-context.md` 做新鲜度检查

P1 验收：CLI 能校验映射文件结构，并能发现缺字段和 stale 来源。

### P2：多角色讨论和 BMad CLI 适配

1. 新增 `party-mode-gate.md`
2. 增加 BMad CLI 可选适配说明
3. 评估是否引入 Analyst/PM/Architect/UX/Writer 角色模板
4. 建立角色输出进入云舒门禁的规则

P2 验收：复杂架构决策可以触发多角色讨论，但最终产物仍必须落入云舒 ADR、计划、验收证据。

---

## 7. V1 实施计划

### Phase 1：文档增强模块

Task 1.1：创建 `components/bmad-enhance/SKILL.md`

- 产物：增强模块入口
- 验证：链接可从主 `SKILL.md` 导航进入
- 风险：触发规则写太宽导致过度使用

Task 1.2：创建 `prd-map.md`、`architecture-map.md`、`story-map.md`、`project-context-sync.md`

- 产物：四个映射规则文档
- 验证：每个文件包含输入、输出、映射表、门禁、反模式
- 风险：字段映射过度依赖当前 BMad 文档摘要

Task 1.3：创建模板文件

- 产物：`templates/bmad_*.md`
- 验证：模板无占位符残留，能被人工填写
- 风险：模板太重，影响使用体验

### Phase 2：主入口登记

Task 2.1：更新 `yunshu-system-skill/SKILL.md`

- 产物：目录导航和触发表增加 BMad 增强层
- 验证：不改变原有 01-init 到 05-deliver 主流程
- 风险：主文档膨胀

Task 2.2：更新 README

- 产物：增加一节“BMad 增强层”
- 验证：用户能知道什么时候用、什么时候不用
- 风险：说明太像推荐默认使用

### Phase 3：验证和归档

Task 3.1：链接检查

- 命令：`python scripts/yunshu.py audit links`
- 通过条件：新增链接不破

Task 3.2：版本检查

- 命令：`python scripts/yunshu.py version-check`
- 通过条件：若未改版本号，必须说明这是方案/文档增强；若改主功能，必须同步 VERSION/README/SKILL

Task 3.3：上下文账本和检查点

- 命令：`python scripts/yunshu.py context record ...`
- 命令：`python scripts/yunshu.py checkpoint create ...`
- 通过条件：能恢复本次设计决策和后续实施步骤

---

## 8. 输入输出契约

### 8.1 BMad PRD Map

输入：

```yaml
yunshu_task_card:
  goal: string
  done_definition: string[]
  constraints: string[]
  risks: string[]
  non_goals: string[]
bmad_prd:
  path: string
  sections: string[]
```

输出：

```yaml
prd_map:
  goal_alignment: string
  acceptance_criteria: string[]
  constraints: string[]
  open_questions: string[]
  out_of_scope: string[]
  gaps: string[]
```

### 8.2 BMad Architecture Map

输入：

```yaml
bmad_architecture:
  path: string
  modules: string[]
  interfaces: string[]
  data_flow: string[]
  decisions: string[]
```

输出：

```yaml
yunshu_spec_patch:
  contracts: string[]
  boundaries: string[]
  test_strategy: string[]
  adr: string[]
  risks: string[]
```

### 8.3 BMad Story Map

输入：

```yaml
bmad_story:
  path: string
  story_id: string
  acceptance_criteria: string[]
  implementation_notes: string[]
project_context:
  path: string
```

输出：

```yaml
yunshu_dispatch_package:
  task_goal: string
  write_scope: string[]
  required_context: string[]
  acceptance: string[]
  validation_commands: string[]
  non_goals: string[]
  concerns: string[]
```

---

## 9. 风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| 流程复杂度增加 | 高 | 高 | 默认不触发，只有复杂任务和显式 BMad 需求触发 |
| BMad 文档格式变化 | 中 | 中 | V1 使用宽松 Markdown 映射，P1 再做 schema |
| 命名代理稀释云舒门禁 | 中 | 高 | 命名代理只作为视角，不替代云舒子智能体 |
| 文档漂移 | 中 | 高 | 映射结果必须写入 context ledger，交付时做文档同步检查 |
| 用户学习成本增加 | 中 | 中 | README 只说明“何时使用”，细节放增强模块 |
| 技术栈耦合 | 中 | 中 | V1 不强依赖 BMad CLI |

---

## 10. 回滚策略

回滚点 1：只新增增强模块文档时

- 回滚方式：删除 `components/bmad-enhance/` 和 `templates/bmad_*.md`
- 回滚验证：主 `SKILL.md` 无坏链，`audit links` 通过

回滚点 2：主 `SKILL.md` 已登记增强模块时

- 回滚方式：移除目录导航、触发表和 README 中的 BMad 增强段落
- 回滚验证：云舒原流程路由仍为 01-init → 02-plan → 03-execute/07-subagent → 04-accept → 05-deliver

回滚点 3：后续增加 CLI 命令时

- 回滚方式：保留文档映射，撤销 `scripts/yunshu.py` 中的 `bmad` 子命令
- 回滚验证：现有 `init/context/checkpoint/verify/validate/audit/version-check` 命令不受影响

---

## 11. 验收标准

### 11.1 方案验收

- 本方案明确了“增强层”而非“主流程替换”的架构边界。
- 本方案给出 P0/P1/P2 优先级，且 P0 可在不安装 BMad CLI 的情况下实施。
- 本方案包含任务卡、主要矛盾、ADR、流程映射、实施计划、契约、风险和回滚。
- 本方案明确把 Party Mode 和命名代理降为后续可选能力。

### 11.2 后续实现验收

- 新增文档全部能被主 `SKILL.md` 或 README 导航到。
- `python scripts/yunshu.py audit links` 通过。
- `python scripts/yunshu.py context record` 留下本轮新增来源、决策和缺口。
- 至少用一个样例完成：任务卡 → PRD Map → Architecture Map → Story Map → 云舒分派包。
- 任意 BMad 产物进入执行阶段前，必须能被云舒 DoD、测试策略和上下文账本追踪。

---

## 12. 推荐结论

可以把 BMad 加到云舒系统里，但第一版只加“上下文工程增强层”。

推荐实施顺序：

1. 先做 `bmad-enhance` 文档模块和模板。
2. 再做映射样例和 schema。
3. 最后评估 BMad CLI 与 Party Mode。

一句话原则：

> 云舒负责判断和验收，BMad负责把复杂需求变成更好的上下文燃料。
