---
name: 06-recover
description: "恢复与检查点。捕获会话状态，从中断处续跑，以 .yunshu 检查点为机器事实来源。"
metadata:
  phase: "recover"
---

# 06-recover：恢复与检查点

## 职责

从任务中断处续跑，确保进度可恢复、下一步明确。核心原则：**捕获下一个会话需要知道的东西，而不是所有发生过的事情。**

`.yunshu/checkpoints/<id>/phase_memory.json` 是机器恢复的唯一事实来源。`checkpoint.json` 和 `handoff.md` 是同一检查点目录下的补充材料；`docs/handoffs/` 与 `phase_memory_card.md` 只作为人工归档或旧流程兜底。

`.yunshu/context/<context_id>.json` 是“调查可复现”的上下文账本，记录已读来源、关键发现、动作、缺口和下一轮补读；它不替代 checkpoint，而是让恢复后不必重新读取全部材料。

**上下文读取原则**：恢复不是把 `.yunshu/` 全量读进上下文。默认只读取指定 checkpoint 的 `phase_memory.json`、`checkpoint.json`，以及这些文件指向的最新 context ledger；如无 checkpoint，使用 `context preload` 选择最近且相关的 1-3 条账本。

---

## Part A：创建交接文档

### 何时创建交接

| 触发条件 | 说明 |
|----------|------|
| 每完成一个 Phase | 自然断点，记录进度 |
| 上下文压缩前 | 压缩会丢失细节，先交接 |
| 高风险动作执行前 | 万一失败，有回滚依据 |
| 会话即将结束 | 长会话、切换任务、准备离开 |
| 阶段门控触发 | 退化信号检测为「注意」或「警告」时 |
| 用户主动要求 | 随时可触发 |

### Step 1：收集机械状态

**方法**：运行命令收集文件级状态：

```bash
# 已修改文件
git diff --name-only
git status --porcelain

# 检查计划文件
ls .plans/active/*.md 2>/dev/null
ls docs/specs/*.md 2>/dev/null
ls docs/plans/*.md 2>/dev/null

# 当前分支
git branch --show-current

# 已有上下文账本
python scripts/yunshu.py context list --task-id <task_id>
```

### Step 2：生成主题标识

**方法**：从当前工作上下文派生一个简短的主题标识。

**规则**：
- 描述**正在做的事**，不是分支名或工单号
- 2-4 个词，小写 kebab-case，最多 40 字符
- 关注**对象和动作**：`auth-oauth-migration`、`stripe-webhook-retry`
- 避免通用标识：`bugfix`、`refactor`、`updates`

### Step 3：写入交接文档

**方法**：优先使用 CLI 在 `.yunshu/checkpoints/<checkpoint_id>/` 生成 `handoff.md`、`checkpoint.json` 和 `phase_memory.json`。如需人工归档，可再使用 `templates/handoff.md` 创建 `docs/handoffs/YYYY-MM-DD-<topic>.md`。

**交接文档结构**：

```markdown
---
created: <ISO 8601 UTC 时间戳>
branch: <当前 git 分支>
trigger: manual | compact | phase-complete | pre-risk | health-gate
restored: false
---

# 交接：<主题>

## 目标
[一句话：我们试图做什么]

## 当前状态
[一句话：现在到了哪一步]

## 已完成的
- [x] [已完成的步骤 1]
- [x] [已完成的步骤 2]

## 未完成的
- [ ] [下一步要做的 1]
- [ ] [下一步要做的 2]

## 关键决策
| 决策 | 选择 | 理由 |
|------|------|------|
| [决策 1] | [A/B] | [为什么] |

## 失败的尝试
| 尝试 | 为什么失败 | 教训 |
|------|-----------|------|
| [尝试 1] | [失败原因] | [学到了什么] |

## 修改的文件
| 文件 | 操作 | 说明 |
|------|------|------|
| [path] | 新增/修改/删除 | [做了什么] |

## 关键产物路径
- 任务卡: [path]
- 计划: [path]
- 验收证据: [path]
- 检查点: [path]

## 会话健康评估
- 健康状态: 健康 / 注意 / 警告
- 退化信号: [记录观察到的退化信号]

## 上下文包（5类关键信息）
1. 决策: [关键决策及理由]
2. 进展: [已完成的关键里程碑]
3. 代码状态: [当前代码/模块状态]
4. 待办: [下一步必须做的事]
5. 失败尝试: [已尝试但失败的方案及教训]

## 恢复指令
1. 读取本交接文档
2. 读取 checkpoint.json 和 phase_memory.json
3. 从"[未完成的第一项]"继续
4. 命令：`使用云舒系统，从 checkpoint_id=<id> 恢复继续执行`

## 阻塞项
- [如果有阻塞问题，列在这里]
```

### Step 4：写入结构化检查点

同时写入两个结构化文件：

**`checkpoint.json`**（包含 task_id / checkpoint_id / 当前阶段 / 已完成 / 未完成 / 关键产物路径）：
- 当前 Phase 和任务编号
- 后续动作
- 关键产物路径
- 交接文档路径

**`phase_memory.json`**（包含 task_id / 当前阶段 / 进展摘要 / 关键决策 / 下一步行动）：
- 历史决策摘要
- 有效变参（哪些参数已确认有效）
- 踩坑记录（哪些路走不通）

**推荐机器化方式**：优先使用 CLI 生成稳定目录和索引，避免手写 JSON 漂移。恢复时以生成的 `phase_memory.json` 为权威。

```bash
python scripts/yunshu.py checkpoint create \
  --task-id <task_id> \
  --phase <init|plan|execute|subagent|accept|deliver|recover> \
  --summary "<当前状态摘要>" \
  --completed "<已完成事项>" \
  --pending "<下一步事项>" \
  --artifact "<关键产物路径>" \
  --next-action "<恢复后第一步>"
```

产物位置：`.yunshu/checkpoints/<checkpoint_id>/checkpoint.json`、`phase_memory.json`、`handoff.md`。随后运行：

```bash
python scripts/yunshu.py validate checkpoint .yunshu/checkpoints/<checkpoint_id>/checkpoint.json
```

### Step 4.5：写入上下文账本

检查点记录“下一步从哪恢复”，上下文账本记录“为什么已经知道这些”。创建检查点前后必须记录或刷新同任务账本：

```bash
python scripts/yunshu.py context record \
  --task-id <task_id> \
  --phase <init|plan|execute|subagent|accept|deliver|recover> \
  --source <本阶段读过的关键文件/目录/链接> \
  --finding "<可复用结论>" \
  --action "<本阶段做了什么>" \
  --decision "<关键决策及理由>" \
  --gap "<仍缺什么>" \
  --next-read "<下次只需补读什么>"
python scripts/yunshu.py validate context .yunshu/context/<context_id>.json
```

`checkpoint create` 会自动把同 task_id 最新的 context ledger 路径写入 `checkpoint.json` 与 `phase_memory.json`，恢复时优先读取该路径。

### Step 4.6：输出充分性门禁

创建检查点或恢复提示前，读取 `safeguards/meta-cognition.md`，执行输出充分性四问：

- 是否明确当前 phase、已完成、未完成、下一步？
- 是否给出 checkpoint_id、关键产物路径和恢复命令？
- 是否记录 context ledger，说明下次只需补读什么？
- 是否记录失败尝试或风险，避免下次重复踩坑？

任何一项缺失且可查证 → 先补写；缺失且阻塞恢复 → 不许声明“可恢复”。

### Step 5：提交交接文档

```bash
git add docs/handoffs/YYYY-MM-DD-<topic>.md
git add checkpoint.json phase_memory.json
git commit -m "handoff: <topic>"
```

---

## Part B：从检查点恢复

> 参考 Superpowers handoff-resume：以 `.yunshu/checkpoints/<id>/phase_memory.json` 为机器事实来源，交接文档只作人工辅助。

### Step 1：定位检查点

**方法**：

1. 用户指定 checkpoint_id → 运行 `python scripts/yunshu.py checkpoint resume <checkpoint_id>`
2. 用户指定 checkpoint_id 后，继续运行 `python scripts/yunshu.py context preload --checkpoint-id <checkpoint_id> --limit 3`，只加载该检查点关联的 context ledger
3. 用户未指定 → 优先运行 `python scripts/yunshu.py checkpoint list` 查看最近检查点；如仍需用户选择，使用当前平台 adapter 的交互方式
4. 只有在用户明确说“同一个任务继续”但没有 checkpoint_id 时，运行 `python scripts/yunshu.py context preload --query "<用户请求关键词>" --limit 3`
5. 没有 `.yunshu/checkpoints/` → 再扫描 `docs/handoffs/` 作为旧流程兜底
6. 都没有 → 回到 `components/01-init/SKILL.md` 重新澄清

### Step 2：读取并理解交接内容

**方法**：按优先级读取：

| 优先级 | 文件 | 用途 |
|--------|------|------|
| 1 | `.yunshu/checkpoints/<id>/phase_memory.json` | 机器事实来源：阶段、进展、关键决策、待办、下一步 |
| 2 | `.yunshu/checkpoints/<id>/checkpoint.json` | 当前进度、产物、风险、后续动作 |
| 3 | `checkpoint.json` / `phase_memory.json` 中的 `context_ledger` | 已读来源、关键发现、缺口、新鲜度 |
| 4 | `.yunshu/checkpoints/<id>/handoff.md` | 人类可读上下文包与恢复提示 |
| 5 | `docs/handoffs/*` | 旧流程或人工归档兜底 |
| 6 | `phase_memory_card.md` | 旧流程兜底，按恢复优先级加载关键文件 |

**上下文包加载流程**：
1. 先读取 `phase_memory.json` 的阶段、进展、下一步
2. 再运行 `python scripts/yunshu.py context preload --checkpoint-id <checkpoint_id> --limit 3`
3. 对 preload 输出为 fresh 的来源复用账本结论；对 stale/missing 来源补读原文件
4. 然后读取待办和失败尝试，避免重复踩坑
5. 按「恢复优先级」加载关键文件；没有缺口时不重读全量历史

**核心原则**：以 `.yunshu/checkpoints/<id>/phase_memory.json` 为**唯一机器事实来源**。只在以下情况回读更多历史：
- 检查点缺字段
- 现场与记录冲突
- 高风险分叉需要更多上下文
- context ledger 标记 stale/missing 或未覆盖当前问题

**读取上限**：除非用户要求审计历史，恢复阶段最多预加载 3 条 context ledger，最多 1 个 checkpoint 目录；禁止为了“保险”批量读取 `.yunshu/context/*.json` 或 `.yunshu/checkpoints/*/*`。

### Step 3：验证现场一致性

**方法**：检查交接文档中记录的状态是否与当前代码库一致：

```bash
# 检查分支是否匹配
git branch --show-current

# 检查文件是否存在
ls [交接文档中记录的关键文件路径]

# 检查是否有未提交的变更
git status --porcelain
```

**不一致处理**：

| 不一致类型 | 处理方式 |
|------------|----------|
| 分支不匹配 | 切换到正确分支或询问用户 |
| 关键文件缺失 | 可能被回滚了，重新评估状态 |
| 有未提交变更 | 确认是否是交接后的新变更 |

### Step 4：确认恢复点

**恢复确认交互**（Trae IDE）：
调用 `AskUserQuestion`：
- 问题："从交接文档恢复：\n目标: [一句话目标]\n当前状态: [一句话状态]\n已完成: N 项\n未完成: M 项\n下一步: [未完成的第一项]\n\n确认从这里继续？"
- 选项："确认继续" / "需要调整"
- 用户选择"确认继续" → 继续
- 用户选择"需要调整" → 更新交接文档后继续

确认恢复点前必须执行输出充分性四问，确保这次说明足够用户判断是否从该点继续。

### Step 5：标记交接文档为已恢复

在交接文档元数据中标记 `restored: true`，避免重复恢复。

### Step 6：路由到对应组件

根据 checkpoint.json 中记录的当前 Phase，路由到对应组件：

| Phase | 组件 |
|-------|------|
| init | `components/01-init/SKILL.md` |
| plan | `components/02-plan/SKILL.md` |
| execute | `components/03-execute/SKILL.md` |
| subagent | `components/07-subagent/SKILL.md` |
| accept | `components/04-accept/SKILL.md` |
| deliver | `components/05-deliver/SKILL.md` |
| recover | `components/06-recover/SKILL.md` |

---

## 恢复命令

在 Trae 新开对话后：

```text
使用云舒系统，从 checkpoint_id=<id> 恢复继续执行；以 phase_memory 为唯一历史事实来源。
```

机器辅助恢复：

```bash
python scripts/yunshu.py checkpoint resume <checkpoint_id>
```

或：

```text
使用云舒系统，恢复最近的交接文档。
```

---

## 交接文档管理

### 归档

当任务完全交付后，将交接文档移到 `docs/handoffs/_archive/`：

```bash
mv docs/handoffs/YYYY-MM-DD-<topic>.md docs/handoffs/_archive/
```

### 清理

定期清理 `_archive/` 中超过 30 天的交接文档。

---

## 反模式

- 🚫 "我记得上次做了什么" — 记忆不可靠，以交接文档为准
- 🚫 "从头开始吧" — 有交接文档就应该从断点恢复
- 🚫 "交接文档太长" — 只写下一个会话需要知道的，不是所有发生过的事
- 🚫 "跳过验证直接恢复" — 现场可能已经变了，必须验证一致性
- 🚫 "不记录失败的尝试" — 失败尝试是最有价值的信息，避免重复踩坑
- 🚫 "跳过上下文包直接恢复" — 上下文包是换会话后无缝衔接的关键，必须加载

---

## 路由

- 恢复成功 → 进入检查点记录的下一 Phase 对应组件
- 检查点缺失/损坏 → 回到 `components/01-init/SKILL.md` 重新澄清
- 现场不一致 → 与用户确认后决定是恢复还是重新开始
