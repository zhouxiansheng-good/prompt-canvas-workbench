---
name: yunshu-system-skill
description: 云舒系统 — 毛选方法论驱动的证据化研发工作流。把《毛泽东选集》的核心方法论注入代码开发全流程：澄清→计划→执行→验收→交付。当用户说"使用云舒系统"/"用云舒系统"/"启动云舒"时触发。
metadata:
  version: "3.6.0"
---

# 云舒系统 — 毛选方法论驱动的证据化研发工作流

<!-- L1:START -->
触发条件：用户说"使用云舒系统"/"用云舒系统"/"启动云舒"时激活。或用户提出跨多文件复杂改动需求、带验收标准的交付型任务时自动匹配。
<!-- L1:END -->

## 适用 / 不适用

- **适用**：新项目启动、复杂功能开发、疑难 Bug 修复、结构性重构、交付型任务、多任务并行开发
- **不适用**：单步问答/概念解释、一次性微调、任务无法在当前环境执行

## CLI 路径选择（强制）

> **Trae IDE 优先规则**：用户在 Trae 里把云舒作为项目技能使用时，通常站在用户项目根目录，不在云舒 skill 包根目录；因此不能默认运行 `python scripts/yunshu.py ...`。

先按当前宿主选择 `<YUNSHU_CLI>`：

| 场景 | `<YUNSHU_CLI>` |
|------|----------------|
| Trae IDE 项目根目录，云舒安装在 `.trae/skills/yunshu-system-skill/` | `python .trae/skills/yunshu-system-skill/scripts/yunshu.py --root .` |
| 正在云舒源码包根目录内维护云舒自身 | `python scripts/yunshu.py --root .` |
| 从云舒源码包操作另一个项目 | `python scripts/yunshu.py --root <项目根目录>` |
| 其他平台适配器另有规定 | 服从 `adapters/<platform>/` |

**硬规则**：
- 下文所有 `python scripts/yunshu.py ...` 示例在 Trae 项目根目录中都必须替换为 `<YUNSHU_CLI> ...`。
- `.yunshu/` 必须写入用户项目根目录；如果出现在 `.trae/skills/yunshu-system-skill/.yunshu/`，说明命令路径或同步包已污染，必须先修正。
- Trae 进入云舒前必须读取 `adapters/trae/SKILL.md`；该 adapter 的命令路径和交互规则优先于通用说明。

## 项目留底初始化（强制）

> **解决项目失忆问题**：云舒系统的 `.yunshu/` 留底必须延伸到用户的具体项目目录，不能仅存于 skill 自身目录。

**触发条件**：首次对某个项目使用云舒系统时，或检测到当前工作目录没有 `.yunshu/` 目录时。

**执行动作**：

```bash
# 1. 初始化 .yunshu/ 目录结构
<YUNSHU_CLI> init

# 2. 创建项目级上下文账本（记录技术栈、项目结构、关键决策）
<YUNSHU_CLI> context record \
  --task-id "project-init" \
  --phase init \
  --source "<项目根目录>" \
  --finding "<技术栈、项目结构摘要>" \
  --action "初始化 .yunshu/ 目录结构" \
  --gap "<待调查项>" \
  --next-read "<下次需补读的文件>"

# 3. 验证初始化结果
<YUNSHU_CLI> validate context .yunshu/context/project-init.json
```

**初始化产物**：

| 路径 | 用途 |
|------|------|
| `.yunshu/context/` | 上下文账本目录 |
| `.yunshu/checkpoints/` | 检查点目录 |
| `.yunshu/verify-log.tsv` | 验证声明日志 |
| `.yunshu/bmad/` | BMad 映射目录 |

**硬规则**：
- 没有 `.yunshu/` 目录 → 不许进入任何组件执行流程
- 初始化失败 → 记录失败原因，降级到手动创建目录结构
- 已有 `.yunshu/` → 检查账本新鲜度，不重复初始化

## 启动预检与阶段防跳门禁（强制）

> **解决“模型跳步骤”问题**：云舒不是按用户话里的动词直接跳到某个阶段，而是按任务状态、检查点和阶段门禁路由。

每次触发云舒时先执行启动预检：

1. 检查 `.yunshu/` 是否存在；不存在先执行项目留底初始化。
2. 如果用户提供 `checkpoint_id`，先运行 `<YUNSHU_CLI> checkpoint resume <checkpoint_id>`，再进入 `06-recover`。
3. 如果是“继续 / 接着上次 / 新开同一个任务”，先运行 `<YUNSHU_CLI> context preload --task-id <task_id> --limit 3`；任务编号不明确时运行 `<YUNSHU_CLI> context preload --query "<用户请求关键词>" --limit 3`。
4. 只读取预加载命令选出的最近且相关账本；不要遍历或全文读取整个 `.yunshu/`。
5. 没有已确认任务卡、用户对齐记录和新鲜上下文账本时，一律路由到 `components/01-init/SKILL.md`，不能进入计划、执行、验收或交付。

阶段跳转必须执行机器门禁：

```bash
<YUNSHU_CLI> gate transition \
  --task-id <task_id> \
  --from-phase init \
  --to-phase plan \
  --user-aligned \
  --dod-confirmed \
  --task-card <任务卡或任务账本路径>
```

**判定规则**：
- `init → plan`：必须有用户对齐、确认后的任务卡、确认后的 DoD，以及新鲜 context ledger。
- `plan → execute/subagent`：必须有计划和规范产物，并通过 `gate transition`。
- `execute/subagent → accept`：必须有实现/验证证据，并通过 `gate transition`。
- `accept → deliver`：必须有验收证据，并通过 `gate transition`。
- 任何跨阶段直跳（例如 `init → execute`）都是失败门禁；门禁失败时停留在当前阶段，补澄清或补证据。

**最小澄清规则**：即使用户说“直接做”，也至少要完成一句话复述、确认目标/非目标/DoD，并留下任务卡或 context ledger；用户明确确认后才能进入下一阶段。

## 全局交互规则

**所有需要用户选择或确认的地方，必须优先使用当前平台的原生交互工具。**

| 平台 | 首选交互方式 | 降级方式 |
|------|--------------|----------|
| Trae IDE | `AskUserQuestion`，2-4 个明确选项 | 工具不可用时，问一个简短问题并记录限制 |
| Codex | Codex 可用的用户输入/确认机制 | 无工具时直接问一个必要问题，不列冗长选项 |
| Claude Code / 其他 | 平台原生选择或确认机制 | 简短自然语言确认 |

**平台适配文件**：进入特定宿主前先读取 `adapters/<platform>/`，不要在非 Trae 环境调用 `AskUserQuestion`，也不要声明不存在的 `workflow_*` 工具已可用。平台 adapter 的限制优先于通用流程路由；例如 Codex 未获显式授权时，不因“任务 ≥3 且独立”自动启用子智能体。

**禁止行为**：
- 假装调用了当前平台不存在的工具
- 把 Trae、Codex、Claude Code 的工具名混在同一执行指令里
- 在需要高风险确认时自行默认继续
- 写"请回复 A/B/C"代替平台原生选择工具

**正确行为**：
- 先判断当前平台，再使用对应 adapter
- 问题明确，选项 2-4 个（当平台支持选择框时）
- 用户选择后立即继续流程

<!-- L2:START -->
## 流程路由

### 子模块路由表

| 用户意图/当前阶段 | 子模块路径 | 子模块职责 |
|-------------------|------------|------------|
| "开始" / "澄清需求" / "任务卡" / "调查研究" | `components/01-init/SKILL.md` | 需求澄清、代码库调查、任务卡生成 |
| "计划" / "制定计划" / "方案设计" / "规划" | `components/02-plan/SKILL.md` | 计划规范、文件结构映射、风险评估 |
| "执行" / "开发" / "写代码" / "实现" / "调试" | `components/03-execute/SKILL.md` | 串行执行、TDD、证据化验证 |
| "子智能体" / "并行" / "分派任务" / "多人协作" | `components/07-subagent/SKILL.md` | 子智能体驱动开发、两阶段审查 |
| "验收" / "检查" / "验证" / "合规审查" | `components/04-accept/SKILL.md` | 两阶段审查、DoD证据链、合规审查 |
| "交付" / "完成" / "发布" / "归档" | `components/05-deliver/SKILL.md` | 变更报告、回滚方案、交付摘要 |
| "恢复" / "继续" / "从检查点恢复" / "checkpoint" | `components/06-recover/SKILL.md` | 交接文档、阶段记忆、检查点恢复 |
| "领域引导" / "行业分析" / "决策树" | `components/08-domain-guide/SKILL.md` | 领域选择集收窄、动态分解 |
| "软件桥接" / "操作软件" / "CLI" / "部署" | `components/09-software-bridge/SKILL.md` | 软件技能匹配、命令构建、沙箱执行 |
| "BMad映射" / "PRD映射" / "架构映射" | `components/bmad-enhance/SKILL.md` | 外部规划文档转云舒上下文 |

### 阶段与组件映射

| 阶段 | 组件 | 产物 | 毛选方法论注入 |
|------|------|------|----------------|
| 0. 澄清 | 01-init | 任务卡（目标 + 完成定义 + 约束） | **调查研究**：没有调查就没有发言权 |
| 1. 计划 | 02-plan | plan.md + spec.md + tasks.md | **主要矛盾 + 阶段判断**：先找核心问题，再定阶段策略 |
| 2a. 串行执行 | 03-execute | 代码 + 验证证据 | **集中优势兵力 + 具体问题具体分析**：一次一个核心问题 |
| 2b. 子智能体执行 | 07-subagent | 子智能体执行 + 两阶段审查 | **统筹全局，协调各方**：专业的人做专业的事 |
| 2c. 领域引导（可选） | 08-domain-guide | 决策树引导 + 选择集收窄 + 上下文打包 | **调查研究 + 具体问题具体分析**：先识别领域，再精确引导 |
| 2d. 软件桥接（可选） | 09-software-bridge | 软件技能匹配 + 命令构建 + 沙箱执行 | **实践是检验真理的唯一标准**：让大模型直接操作软件 |
| 2e. BMad增强（可选） | bmad-enhance | PRD/Architecture/Story/project-context 映射 | **调查研究 + 主要矛盾**：把外部规划文档转成云舒可验证上下文 |
| 3. 验收 | 04-accept | 验收剧本 + 验收证据 | **实践检验**：实践是检验真理的唯一标准 |
| 3a. 合规审查（可选） | compliance-audit | 风险清单 + 修复建议 + 优先级 | 高风险项目必做，嵌入04-accept Step 6 |
| 4. 交付 | 05-deliver | 变更报告 + 回滚方案 | — |
| 5. 恢复 | 06-recover | 交接文档 + 阶段记忆 | — |

> **执行模式选择**（02-plan结束时决策）：在当前平台 adapter 允许的前提下，任务 ≥3 且基本独立 → 07-subagent；任务紧耦合或需调试 → 03-execute

## 输入输出

**输入**：`goal`（目标）+ `done_definition`（验收标准，≥3条）+ `constraints`（约束，可选）

**输出**：当前阶段产物 + 证据 + 下一步

## 可执行工具层

云舒自 v3.4.0 引入并在当前版本持续扩展一个最小工具化骨架，用来兑现版本、恢复、上下文复现、证据、链接、BMad 映射等门禁。

| 能力 | 命令 | 产物 |
|------|------|------|
| 初始化状态目录 | `python scripts/yunshu.py init` | `.yunshu/` |
| 创建检查点 | `python scripts/yunshu.py checkpoint create --task-id <id> --phase <phase>` | `.yunshu/checkpoints/<checkpoint_id>/` |
| 列出检查点 | `python scripts/yunshu.py checkpoint list` | checkpoint 索引 |
| 恢复检查点 | `python scripts/yunshu.py checkpoint resume <checkpoint_id>` | 恢复指令 + 文件路径 |
| 记录上下文账本 | `python scripts/yunshu.py context record --task-id <id> --phase <phase> --source <path>` | `.yunshu/context/<context_id>.json` + `.md` |
| 查看上下文账本 | `python scripts/yunshu.py context list/show/status` | 已读来源、发现、动作、缺口、新鲜度 |
| 启动/续接预加载 | `python scripts/yunshu.py context preload --task-id <id> --limit 3` | 最近且相关的 context 读取计划，只列 stale/missing/next_read 补读项 |
| 阶段跳转门禁 | `python scripts/yunshu.py gate transition --task-id <id> --from-phase <phase> --to-phase <phase>` | `.yunshu/gates/<gate_id>.json`，阻止缺澄清/缺证据的跨阶段跳转 |
| 记录验证声明 | `python scripts/yunshu.py verify run --claim "<claim>" --command "<cmd>"` | `.yunshu/verify-log.tsv` |
| 校验上下文账本 | `python scripts/yunshu.py validate context <file>` | 结构化复现判定 |
| 校验证据 | `python scripts/yunshu.py validate evidence <file>` | 结构化验收判定 |
| 校验检查点 | `python scripts/yunshu.py validate checkpoint <file>` | 结构化恢复判定 |
| 记录 BMad 映射 | `python scripts/yunshu.py bmad map --task-id <id> --kind <kind> --source <path>` | `.yunshu/bmad/<map_id>.json` + context ledger |
| 检查 BMad 映射新鲜度 | `python scripts/yunshu.py bmad status <map_id>` | fresh/stale/missing 判定 |
| 校验 BMad 映射 | `python scripts/yunshu.py bmad validate <file>` | 结构化映射判定 |
| 检查链接 | `python scripts/yunshu.py audit links` | Markdown 内链审计 |
| 检查版本 | `python scripts/yunshu.py version-check` | `VERSION` / `SKILL.md` / `README.md` / adapter 示例版本一致性 |

**原则**：文档门禁负责判断，CLI 负责留下机器可复跑证据；没有运行 CLI 时，不许宣称这些机器门禁已经通过。

## 元认知输出门禁

用户实测有效的提示“发给我之前，先询问自己是否真的完全掌握并给出所有我要的信息”，在云舒中固化为**输出充分性门禁**。它不是要求暴露冗长思考，而是要求每次用户可见输出前先完成内部核查：

1. 用户显式问的问题是否逐一回答？
2. 用户要做判断/继续执行所需的信息是否给全？
3. 关键结论是否有本地文件、命令输出、外部资料或明确假设支撑？
4. 如有缺口，是应先查证、问用户，还是带限制说明继续？

**缺口分级**：
- 可查证缺口：先用工具查证，不把可调查的问题丢给用户。
- 阻塞缺口：停下，只问一个必要问题。
- 非阻塞缺口：明确写出假设、限制或后续风险，再继续输出。

## 硬规则（云舒 + 毛选融合版）

1. **没有调查就没有发言权**：不读代码库就不许写代码，缺证据 = 未完成
2. **先找主要矛盾**：不抓核心问题就动手，只会越改越乱
3. **实践是检验真理的唯一标准**：没有合适的新鲜验证证据就不算完成；代码行为变更优先使用自动化测试，文档/配置/流程任务可用编译、链接、CLI、结构化校验等证据
4. **具体问题具体分析**：不套模板，每段代码都要适配实际场景
5. **集中优势兵力**：一次只解决一个核心问题，不分兵
6. **高风险必停**：危险操作前必须确认
7. **3 次失败必暂停**：连续失败 ≥3 次，质疑架构
8. **改前必分析，修后必回归**：修改代码前做影响分析，修复后跑回归测试
9. **调试前查库，修后存库**：调试前查Bug知识库，修复后存入知识库
10. **子智能体审查不许跳步**：规范审查未通过不许做质量审查，审查发现问题必须复审
11. **阶段过渡必须执行门控检查**：每个阶段过渡处必须执行会话健康评估，退化时必须保存上下文并建议换会话
12. **输出前必自检**：任何输出/决策/行动前，必须执行元认知与输出充分性自检；可查证缺口先查证，阻塞缺口先提问，非阻塞缺口必须明示假设或限制
13. **调查后必留上下文账本**：凡是读取代码库/文档形成结论，阶段结束前必须写入 `.yunshu/context/`；下一轮先查账本新鲜度，只补读 stale/missing 或未覆盖来源

## 会话健康规则

> 解决P-003长会话退化：会话超过70%容量后响应变慢、质量下降、记忆混乱、创意枯竭。

### 退化信号清单

| 信号 | 具体表现 | 严重度 |
|------|----------|--------|
| 记忆混乱 | 重复问已确认的问题、自相矛盾、遗忘历史决策 | 🔴 |
| 质量下降 | 出现低级错误、代码风格不一致、忽略约束 | 🔴 |
| 响应变慢 | 思考时间明显变长、输出冗余增加 | 🟠 |
| 上下文遗忘 | 需要重新读取之前已读的文件、丢失任务上下文 | 🔴 |

### 门控触发条件

在以下**阶段过渡处**必须执行门控检查：

| 过渡点 | 触发动作 |
|--------|----------|
| 01-init → 02-plan | 评估澄清阶段长度，≥8轮对话则建议保存上下文 |
| 02-plan → 03-execute/07-subagent | 计划阶段通常较长，必须保存上下文包 |
| 03-execute 每完成一个任务 | 检查退化信号，有则建议换会话 |
| 03-execute → 04-accept | 执行阶段通常最长，必须保存上下文包 |
| 04-accept → 05-deliver | 验收阶段自然断点，保存上下文 |

### 门控检查流程

```
阶段过渡触发
  ↓
1. 自检退化信号（对照清单）
  ↓
2. 评估健康状态：
   - 健康（无信号）→ 继续下一阶段
   - 注意（1个🟠信号）→ 保存上下文包，继续
   - 警告（任何🔴信号或≥2个信号）→ 保存上下文包 + 建议换会话
  ↓
3. 如需换会话：
   - 创建交接文档（使用增强模板）
   - 创建阶段记忆卡（使用增强模板）
   - 告知用户恢复指令
```

### 会话切换协议

当门控检查结果为「警告」时：

1. **保存**：立即创建交接文档 + 阶段记忆卡（包含5类上下文：决策/进展/代码状态/待办/失败尝试）
2. **告知**：向用户说明退化原因和建议
3. **恢复指令**：`使用云舒系统，从 checkpoint_id=<id> 恢复继续执行`

## 安全防护触发表

> 渐进式披露：只在遇到对应场景时按需加载safeguard文件，不占主上下文。

| 触发场景 | 加载文件 | 覆盖问题 |
|----------|----------|----------|
| 引入新依赖/安装包 | `safeguards/dependency.md` | P-006 依赖幻觉 / P-007 技术栈幻觉 / P-008 文档幻觉 / P-009 Slopsquatting |
| 会话过长/读取大量文件/上下文接近容量上限 | `safeguards/context.md` | P-001 上下文窗口限制 / P-002 注意力稀释 / P-004 信息过载 / P-005 上下文污染 |
| 涉及安全相关代码 | `safeguards/security.md` | P-011 安全漏洞 / P-013 权限提升 / P-026 DevOps配置 |
| 代码审查/质量检查 | `safeguards/code-quality.md` | P-010 缺陷密度 / P-012 回归Bug / P-014 架构缺陷 |
| 跨文件重构 | `safeguards/refactor.md` | P-018 跨文件重构 / P-019 循环依赖 / P-020 接口破坏 |
| 数据库操作 | `safeguards/database.md` | P-021 N+1查询 / P-025 API版本控制 |
| 并发/多线程代码 | `safeguards/concurrency.md` | P-022 竞态条件 |
| 微服务架构 | `safeguards/microservice.md` | P-023 微服务理解不足 |
| 遗留代码维护 | `safeguards/legacy.md` | P-024 遗留代码理解 |
| MCP/Agent模式 | `safeguards/agent-safety.md` | P-043~P-049 Agent安全 |
| 新任务/新功能启动 | `safeguards/understanding.md` | P-015 业务理解缺失 |
| 架构决策/技术选型 | `safeguards/architecture.md` | P-016 架构判断力缺失 |
| 系统级依赖分析 | `safeguards/dependency-analysis.md` | P-017 系统级理解不足 |
| 代码验收/理解验证 | `safeguards/cognition.md` | P-053 理解债 |
| 代码执行/调试/技能保持 | `safeguards/skill-preserve.md` | P-055 调试退化 / P-056 技能萎缩 |
| 任务启动/偏差校准 | `safeguards/bias-calibration.md` | P-054 主观偏差 / P-061 监督者局限 |
| 代码交付/可持续性评估 | `safeguards/sustainability.md` | P-067 "有效直到无效" / P-069 长期存活率低 |
| Vibe Coding/90%陷阱 | `safeguards/vibe-coding.md` | P-050 90%陷阱 / P-051 技术债务隐蔽 / P-052 责任链断裂 |
| 代码维护/文档同步 | `safeguards/maintenance.md` | P-062 文档漂移 / P-063 决策无记录 / P-064 隐性知识 / P-065 只写代码 / P-066 重复代码 / P-068 变动激增 |
| 中文开发者/编码/国内生态/项目初始化 | `safeguards/chinese-dev.md` | P-037 中文文档理解差 / P-038 中文编码问题 / P-039 中文生态差异 |
| 团队协作/回归防护 | `safeguards/team.md` | P-070 回归错误 / P-071 补丁积累 |
| 代码验收/团队AI规范 | `safeguards/team-norms.md` | P-072 影子AI / P-073 审查瓶颈 / P-074 安全隐患 |
| 任务启动/人才梯队 | `safeguards/talent-pipeline.md` | P-075~077 人才梯队 |
| BMad/PRD/Architecture/Story/project-context 映射 | `components/bmad-enhance/SKILL.md` | 外部规划文档转云舒任务卡、计划规范、执行分派包 |
| 前端/UI任务/设计方向/美学合规 | `components/03-execute/frontend-design/design-thinking.md` `components/03-execute/frontend-design/aesthetic-checklist.md` `components/03-execute/frontend-design/banned-patterns.md` | 前端设计思考、美学合规检查、禁止模式扫描 |
| 前端E2E验证/Web应用测试/Playwright | `components/03-execute/webapp-testing/SKILL.md` `components/03-execute/webapp-testing/scripts/with_server.py` | 前端E2E验证、服务器生命周期管理、截图证据采集 |
| 需求澄清/领域差异化模板 | `components/01-init/requirement-clarification/domain-router.md` `components/01-init/requirement-clarification/templates/*.md` | 通用框架+领域模板路由、深度追问引擎、增强任务卡生成 |
| 领域引导/垂直行业任务 | `components/08-domain-guide/SKILL.md` `components/08-domain-guide/atomic-task-criteria.md` | 领域选择集收窄、动态分解、原子任务判定 |
| 软件操作/CLI-Anything | `components/09-software-bridge/SKILL.md` `components/09-software-bridge/execution-sandbox.md` | 软件技能匹配、命令构建、沙箱执行安全 |
| **任何输出/决策前** | **`safeguards/meta-cognition.md`** | **P-015 理解缺失 / P-053 理解债 / P-054 主观偏差 / P-003 长会话退化** |

**触发规则**：组件执行中检测到对应场景 → 读取safeguard文件 → 按文件中的流程执行

## 核心能力

| 能力 | 组件 | 关键方法 | 毛选思想 |
|------|------|----------|----------|
| 需求澄清 | 01-init | 领域识别、通用基础提问、领域专属模板、深度追问引擎、增强任务卡 | 调查研究 |
| 计划规范 | 02-plan | 代码库调研、逆向推导、文件结构映射、WBS分解+细粒度步骤、风险评估、占位符扫描、类型一致性检查 | 主要矛盾、阶段判断 |
| 执行验证 | 03-execute | TDD、证据化验证、科学实验式验证、系统化调试、CI调试、Bug知识库、变更安全机制、前端E2E验证（Playwright） | 集中优势兵力 |
| 子智能体驱动 | 07-subagent | 子智能体分派、两阶段审查、并行执行 | 统筹全局，协调各方 |
| 领域引导 | 08-domain-guide | 决策树遍历、层级引导、选择集收窄、上下文打包 | 调查研究、具体问题具体分析 |
| 软件桥接 | 09-software-bridge | 软件技能匹配、命令构建、沙箱执行、结果验证 | 实践是检验真理的唯一标准 |
| BMad增强层 | bmad-enhance | PRD/架构/Story/project-context 映射、上下文工程增强 | 调查研究、主要矛盾 |
| 验收交付 | 04-accept | 两阶段审查、AI冗余检查、DoD证据链、失败分类处理 | 实践检验 |
| 交付归档 | 05-deliver | 变更报告、回滚方案、快速交付模式、合并冲突处理、交付方式选择 | — |
| 恢复续跑 | 06-recover | 交接文档、检查点 | — |

## 反模式

- 🚫 跳过澄清直接执行（没有调查就没有发言权）
- 🚫 验收缺证据就宣称完成（实践是检验真理的唯一标准）
- 🚫 没有根因调查就提修复方案（先找主要矛盾）
- 🚫 修改代码前不做影响分析（具体问题具体分析）
- 🚫 修复后不跑回归测试（集中优势兵力，修完要验证）
- 🚫 同时解决多个核心问题（不分兵）
- 🚫 子智能体审查跳步或跳过复审（统筹全局，步步为营）
- 🚫 阶段过渡跳过门控检查（长会话退化必须主动预防）

## 斜杠命令

| 命令 | 用途 |
|------|------|
| `/plan` | 启动计划模式 |
| `/spec` | 启动规格模式 |
| `/compact` | 上下文压缩 |
| `/resume` | 恢复中断执行 |
| `/debug` | 启动调试会话 |
| `/subagent` | 启动子智能体驱动开发 |
| `/parallel` | 并行分派多个独立任务 |

<!-- L2:END -->

<!-- L3:START -->
## 目录导航

| 层级 | 内容 | 路径 |
|------|------|------|
| L2 | 组件（按阶段拆分） | `components/*/SKILL.md` |
| L2 | 领域引导（可选） | `components/08-domain-guide/SKILL.md` |
| L2 | 软件桥接（可选） | `components/09-software-bridge/SKILL.md` |
| L2 | 可选增强组件 | `components/bmad-enhance/SKILL.md` |
| L3 | 组件子文件（渐进式披露） | `components/*/verify.md` `components/*/debug.md` `components/*/dispatch.md` `components/*/frontend-design/*.md` `components/*/webapp-testing/*.md` `components/bmad-enhance/*.md` |
| L3 | 安全防护（按需加载） | `safeguards/*.md` |
| L3 | 模板 | `templates/` |
| L3 | 智能体提示词 | `agents/*/AGENT.md` |
| Tool | 可执行工具与 schema | `scripts/yunshu.py` `schemas/*.schema.json`（含 `bmad_mapping.schema.json`） |
| Adapter | 平台适配层 | `adapters/trae/` `adapters/codex/` `adapters/claude-code/` |

## 模板清单

| 模板 | 用途 |
|------|------|
| `plan.md` | 实施计划 |
| `spec.md` | 规格文档 |
| `tasks.md` | 任务清单 |
| `debug_session.md` | 调试会话记录 |
| `bug_knowledge.md` | Bug 知识卡 |
| `acceptance_runbook.md` | 验收剧本 |
| `change_report.md` | 变更报告 |
| `context_ledger.md` | 可复现上下文账本 |
| `handoff.md` | 交接文档 |
| `phase_memory_card.md` | 阶段记忆卡 |
| `subagent_implementer.md` | 子智能体实现者分派模板 |
| `subagent_spec_reviewer.md` | 子智能体规范审查者分派模板 |
| `subagent_quality_reviewer.md` | 子智能体质量审查者分派模板 |
| `bmad_prd_map.md` | BMad PRD / Tech Spec 到云舒任务卡映射模板 |
| `bmad_architecture_map.md` | BMad Architecture 到云舒 spec / ADR 映射模板 |
| `bmad_story_map.md` | BMad Story 到云舒执行分派包映射模板 |
| `bmad_project_context.md` | BMad project-context 到云舒上下文账本摘要模板 |
| `gsd_*.md` | GSD 项目文档 |

## 智能体清单

| 智能体 | 用途 | 版本 | 创建路径 |
|--------|------|------|---------|
| `yunshu-implementer` | 实现者：按云舒微流程（澄清→计划→执行→自验收）实现代码、写测试、自检、提交 | 2.0 | `agents/yunshu-implementer/AGENT.md` |
| `yunshu-spec-reviewer` | 规范审查者：按云舒微流程（澄清→计划→审查→自验收）验证代码是否严格匹配规范 | 2.0 | `agents/yunshu-spec-reviewer/AGENT.md` |
| `yunshu-quality-reviewer` | 质量审查者：按云舒微流程（澄清→计划→审查→自验收）验证代码质量 | 2.0 | `agents/yunshu-quality-reviewer/AGENT.md` |

<!-- L3:END -->
