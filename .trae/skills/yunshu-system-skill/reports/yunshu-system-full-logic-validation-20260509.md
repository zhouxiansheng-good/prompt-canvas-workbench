# 云舒系统完整执行逻辑验证报告

## 元信息

- 验证日期：2026-05-09
- 验证对象：`E:\traework\000 自动化工作流研究\yunshu-system-skill`
- 当前版本：`3.3.0`
- 执行环境：Codex + PowerShell + Windows 中文路径
- 平台适配：已读取 `adapters/codex/SKILL.md`
- 本次检查点：`.yunshu/checkpoints/yunshu-system-audit-execute-20260509-175447/`
- 结构化证据：`reports/yunshu-system-audit-acceptance-evidence-20260509.json`

## 总结论

云舒系统 v3.3.0 的“文档流程链路”已经基本完整，阶段可以从 `01-init` 路由到 `02-plan`、`03-execute` 或 `07-subagent`、`04-accept`、`05-deliver`，并通过 `06-recover` 恢复。它也已经有最小机器门禁层：版本检查、链接审计、检查点创建/恢复、验证日志、结构化证据校验。

但它还不能被判定为“完整执行逻辑已经完全落实”。原因是：关键门禁仍大量依赖模型/人类自觉执行，CLI 只覆盖了最小骨架；本次实测还发现 `verify run` 在 Windows 中文输出场景下可能出现“命令被记录为 passed，但证据文件为空且捕获线程抛出 UnicodeDecodeError”的问题。这直接影响云舒“缺证据 = 未完成”的核心原则。

当前判断：

| 维度 | 结论 |
|---|---|
| 阶段设计完整性 | 通过，阶段和产物完整 |
| Codex 平台可执行性 | 基本可执行，但必须让 adapter 优先于核心 subagent 路由 |
| 最小机器门禁 | 部分通过，版本/链接/checkpoint 可跑 |
| 证据可靠性 | 未完全通过，中文输出捕获存在 P0/P1 缺陷 |
| 是否完全机器强制落实 | 未通过，多数 safeguard 仍是文档纪律 |
| 是否已完成本次验证任务 | 通过，已实际跑通实例并记录问题 |

## 本次任务卡

```yaml
goal: "验证云舒系统整体执行逻辑是否可落地，并形成验证文档"
done_definition:
  - "检查核心阶段、组件、adapter、模板、safeguard、CLI 与 schema 是否完整"
  - "运行一次云舒实例流程，覆盖调查、计划、执行、验收、恢复证据"
  - "运行最小机器门禁：version-check、audit links、checkpoint validate/resume、verify run、py_compile"
  - "分类记录冗余、错误、冲突、缺漏，并给出修正优先级"
  - "生成可复查的验证报告和 acceptance_evidence.json"
constraints:
  - "不修改既有云舒流程文档和代码，只新增验证产物"
  - "Codex 环境未获得显式子智能体授权，因此不启用 subagent"
  - "保留已有工作区改动，不回滚用户或历史修改"
non_goals:
  - "本次不修复云舒代码"
  - "本次不执行 sync-trae.ps1 -Apply，不覆盖 Trae 安装副本"
```

## 按云舒逻辑运行的实例

本次把“审计云舒系统自身”作为实例任务，按云舒流程走了一遍。

| 云舒阶段 | 本次动作 | 实际产物/证据 |
|---|---|---|
| 0. 01-init 调查 | 读取 `SKILL.md`、Codex adapter、README、既有 checkpoint、git 状态和目录结构 | 发现已有 checkpoint `yunshu-v3-upgrade-plan-20260509-172336`，工作区已有多处未提交改动 |
| 1. 02-plan 计划 | 确定 DoD、执行模式和验证矩阵 | 因 Codex adapter 要求显式授权才可用子智能体，本次选择串行验证 |
| 2. 03-execute 执行 | 读取组件、gates、schema、CLI、adapter、safeguards；运行机器门禁 | `.yunshu/verify-log.tsv`、`.yunshu/verification/*.log` |
| 2.5 recover 检查点 | 创建本次审计 checkpoint 并校验 | `.yunshu/checkpoints/yunshu-system-audit-execute-20260509-175447/` |
| 3. 04-accept 验收 | 生成 DoD 到证据映射，标记系统级通过/失败项 | `reports/yunshu-system-audit-acceptance-evidence-20260509.json` |
| 4. 05-deliver 交付 | 生成本报告，最终复跑 version/link/evidence 门禁 | 本报告 |

## 静态完整性检查

| 模块 | 检查结果 | 备注 |
|---|---|---|
| 核心入口 | 存在 `SKILL.md`，版本为 3.3.0 | 通过 |
| README | 存在并覆盖架构、流程、工具、adapter、安装 | 基本通过，存在 safeguard 数量漂移 |
| 组件 | 7 个目录：01-init、02-plan、03-execute、04-accept、05-deliver、06-recover、07-subagent | 通过 |
| gates | 02-plan、03-execute、04-accept 均有 gates.md | 通过 |
| adapters | trae、codex、claude-code 均存在 | 通过 |
| agents | implementer、spec-reviewer、quality-reviewer 三个 AGENT.md | 通过 |
| safeguards | 实际 24 个文件 | README 写“23 个安全防护文件”，需同步 |
| templates | 实际 16 个模板 | 通过 |
| schemas | checkpoint、acceptance_evidence 两个 JSON Schema | 存在，但 CLI 未完整按 schema 校验 |
| CLI | `scripts/yunshu.py` 包含 init/checkpoint/verify/validate/audit/version-check | 通过，但 verify 捕获有中文编码缺陷 |
| Trae 同步脚本 | `scripts/sync-trae.ps1` dry-run 可列出 72 个待同步文件 | 脚本可直接跑，verify 包裹时暴露编码问题 |

## 动态验证结果

| 命令/动作 | 结果 | 证据 |
|---|---|---|
| `python scripts\yunshu.py version-check` | 通过，输出 `Version check passed: 3.3.0` | `.yunshu/verification/verify-20260509-175152-669951-5d0ead24.log` |
| `python scripts\yunshu.py audit links` | 通过，Markdown 内链审计通过 | `.yunshu/verification/verify-20260509-175246-928191-9ae04bb3.log` |
| `python scripts\yunshu.py validate checkpoint .yunshu\checkpoints\yunshu-v3-upgrade-plan-20260509-172336\checkpoint.json` | 通过 | `.yunshu/verification/verify-20260509-175256-441259-de3d55d9.log` |
| `python scripts\yunshu.py checkpoint resume yunshu-v3-upgrade-plan-20260509-172336` | 通过，输出 checkpoint 与 phase_memory 路径 | `.yunshu/verification/verify-20260509-175404-694453-dcd935cc.log` |
| `python -m py_compile scripts\yunshu.py` | 通过 | `.yunshu/verification/verify-20260509-180521-571218-f9185aba.log` |
| `python scripts\yunshu.py checkpoint create --task-id yunshu-system-audit ...` | 通过，创建本次 checkpoint | `.yunshu/checkpoints/yunshu-system-audit-execute-20260509-175447/` |
| `python scripts\yunshu.py validate checkpoint .yunshu\checkpoints\yunshu-system-audit-execute-20260509-175447\checkpoint.json` | 通过 | 终端输出 `VALID checkpoint` |
| `powershell -ExecutionPolicy Bypass -File scripts\sync-trae.ps1` | 通过，dry-run 列出 72 个文件 | 终端输出可见 |
| `verify run` 包裹 `sync-trae.ps1` | 不可靠：日志记为 passed，但捕获线程报 UnicodeDecodeError，证据文件 0 字节 | `.yunshu/verification/verify-20260509-180541-432516-33a08eaa.log` |
| `verify run` 包裹 `Write-Output 中文输出` | 不可靠：日志记为 passed，但捕获线程报 UnicodeDecodeError，证据文件 0 字节 | `.yunshu/verification/verify-20260509-181348-374239-cdee5d2f.log` |
| `verify run` 包裹 `Write-Output ascii-output` | 通过，证据文件包含 `ascii-output` | `.yunshu/verification/verify-20260509-181404-495473-f5506cea.log` |

## 问题清单

### P0/P1：`verify run` 对中文输出的证据采集不可靠

证据：

- `scripts/yunshu.py:247` 使用 `subprocess.run(command, shell=True, cwd=root, text=True, capture_output=True)`，未显式指定 `encoding` 与 `errors`。
- 最小复现命令：`python scripts\yunshu.py verify run --claim "BUG-1 verify run captures non-ASCII PowerShell output" --command "powershell -NoProfile -Command Write-Output 中文输出"`。
- 结果：外层出现 `UnicodeDecodeError: 'gbk' codec can't decode byte...`，`.yunshu/verification/verify-20260509-181348-374239-cdee5d2f.log` 为 0 字节，但 `.yunshu/verify-log.tsv` 写入了 `passed`。

影响：

- 云舒的核心原则是“缺证据 = 未完成”，但当前可能出现“命令退出码成功、证据捕获失败、状态仍 passed”的反向情况。
- 中文路径和中文输出是本项目主场景，这不是边缘问题。

建议：

- 在 `cmd_verify_run` 中改为二进制捕获，然后用 `utf-8` / locale / `errors="replace"` 安全解码。
- 或显式使用 `subprocess.run(..., text=True, encoding="utf-8", errors="replace")`，并确认 PowerShell 输出编码。
- 如果 `stdout/stderr` 捕获线程异常或应有输出却为空，应标记为 `inconclusive` 而不是 `passed`。

### P1：核心 subagent 路由与 Codex adapter 存在执行优先级冲突

证据：

- `SKILL.md:54` 和 `components/02-plan/SKILL.md:363` 表述为“任务 >=3 且基本独立，优先使用 07-subagent”。
- `adapters/codex/SKILL.md:26` 表述为 Codex subagents 需要用户显式授权。

影响：

- 如果只读核心流程，模型可能在 Codex 中错误启用子智能体。
- 本次按 adapter 约束选择串行执行，说明实际可行路径依赖“adapter 优先”的隐含规则。

建议：

- 在核心路由处补一句硬规则：平台 adapter 约束优先于通用执行模式。
- 02-plan / 03-execute / 07-subagent 的路由表统一注明 Codex 下“任务 >=3”只是建议，不构成 spawn 授权。

### P1：恢复来源存在双轨叙述

证据：

- `components/01-init/SKILL.md:53` 和 `components/06-recover/SKILL.md:58` 要扫描 `docs/handoffs/`。
- `components/06-recover/SKILL.md:194` 仍提到 `phase_memory_card.md`。
- CLI 实际创建 `.yunshu/checkpoints/<id>/checkpoint.json`、`phase_memory.json`、`handoff.md`。
- `scripts/yunshu.py:131` 和 `scripts/yunshu.py:233` 明确恢复时“以 phase_memory 为唯一历史事实来源”。

影响：

- 文档读者会不确定到底以 `docs/handoffs/`、`phase_memory_card.md`，还是 `.yunshu/checkpoints/<id>/phase_memory.json` 为准。

建议：

- 明确 `.yunshu/checkpoints/<id>/phase_memory.json` 为机器恢复权威。
- `docs/handoffs/` 可保留为人工归档，但不要作为优先恢复入口。

### P1/P2：schema 存在，但 CLI 没有完整按 JSON Schema 校验

证据：

- `schemas/checkpoint.schema.json` 和 `schemas/acceptance_evidence.schema.json` 定义了 `minLength`、`format: date-time` 等约束。
- `scripts/yunshu.py:279` 与 `scripts/yunshu.py:293` 是手写最小校验，只检查必填字段、phase/status 枚举和数组类型。

影响：

- README 中“schema 让恢复和验收有稳定数据契约”的说法目前只部分成立。
- 空字符串、非法时间格式、证据路径不存在等问题无法被当前 CLI 完整发现。

建议：

- 若保持零依赖，可补齐关键约束的手写校验。
- 若允许依赖，可使用 `jsonschema` 并在依赖策略中记录来源、版本和回滚方式。
- 至少增加 evidence 路径存在性检查，避免“结构合法但证据丢失”。

### P2：README safeguard 数量与实际文件数不一致

证据：

- `README.md:253` 写“23个安全防护文件”。
- 实际 `safeguards/` 目录有 24 个文件，包含 `meta-cognition.md`。
- `SKILL.md:175` 已把 `safeguards/meta-cognition.md` 列入全局触发。

影响：

- 属于云舒自己定义的文档同步问题。

建议：

- README 的安全防护数量改为 24，并在目录树中补上 `meta-cognition.md`。

### P2：TDD 和“测试通过”措辞对非代码任务过硬

证据：

- `components/03-execute/SKILL.md:107` 写“没有失败测试 -> 不写生产代码”。
- `SKILL.md:84` 与 `components/04-accept/SKILL.md:9` 写“没有测试通过就不算完成”。
- 同时 `components/03-execute/SKILL.md:156` 和 `templates/acceptance_runbook.md:8` 又承认编译验证、代码检查、运行验证、CLI 验证等多种验收类型。

影响：

- 对文档、配置、流程审计、CLI 验证类任务，严格 TDD 表述容易造成不必要阻塞。

建议：

- 顶层硬规则改为“没有合适的新鲜验证证据就不算完成”。
- TDD 铁律限定在生产代码行为变更；文档/配置/脚本审计走 claim-based verification。

### P2：自动触发门禁仍主要是文档纪律

证据：

- 02/03/04 组件和 safeguards 大量描述“自动触发”“自动同步”“自动评估”。
- 当前 CLI 只覆盖版本、链接、checkpoint、verify log、JSON 结构最小校验。
- 没有 hook、MCP server、agent manifest 状态机或 CI workflow 强制执行 safeguards。

影响：

- 流程能被遵守，但不能稳定强制。

建议：

- 把门禁分为“机器门禁”和“控制器必做门禁”两类。
- 下一步优先机器化：schema 严格校验、证据路径存在性、TODO/HACK 扫描、safeguard 触发记录、checkpoint 生命周期检查。

### P3：外层工作区有旧副本和旧报告，可能干扰判断

证据：

- 工作区根目录存在 `SKILL.md`、`README.md`、`components/`、`templates/`、`云舒系统技能核查报告.md`。
- 旧报告描述的是 v3.3.0 工具化之前的状态，里面“没有脚本/schema”等结论已不再完全准确。

影响：

- 如果用户或 agent 从工作区根目录读取旧副本，可能得到过期结论。

建议：

- 在根目录旧报告头部标注“历史报告，已被 2026-05-09 新报告取代”。
- 或将旧散落副本归档，明确 `yunshu-system-skill/` 是当前主包。

## 冗余与可优化点

| 类型 | 位置 | 说明 | 建议 |
|---|---|---|---|
| 恢复流程双轨 | `docs/handoffs`、`.yunshu/checkpoints`、`phase_memory_card.md` | 人工交接与机器检查点并存，但优先级不够清楚 | 统一机器权威，人工文档作为派生物 |
| subagent 路由重复 | `SKILL.md`、02-plan、03-execute、07-subagent、adapter | 多处重复容易漂移 | 保留核心原则，平台限制统一放 adapter 并被核心引用 |
| 元认知门禁重复 | 全局 safeguard + 多组件嵌入 | 有助于强调，但长任务中会变重 | 保留全局五维，组件只写本阶段重点 |
| 技术债检查分散 | `vibe-coding.md`、`team.md`、`maintenance.md`、`code-quality.md` | 覆盖全面但交叉较多 | 形成一张 debt gate 总表，子文件只放细则 |

## 缺漏汇总

| 缺漏 | 影响 | 建议优先级 |
|---|---|---|
| `verify run` 缺少健壮编码捕获 | 中文环境证据可能丢失且误判 passed | P0/P1 |
| CLI 未严格按 schema 校验 | 结构契约不够硬 | P1 |
| evidence 不检查路径存在 | 可能“证据字段非空但文件不存在” | P1 |
| 没有 `yunshu.py` 单元测试 | CLI 只能 py_compile，缺行为回归测试 | P1 |
| safeguards 无机器触发记录 | 无法审计哪些门禁真的执行过 | P2 |
| sync-trae 无 `-VerifyTarget` | dry-run/Apply 后仍需人工在目标包复验 | P2 |
| Codex subagent 授权规则未在核心路由中高亮 | 平台冲突风险 | P1 |

## 可落实程度评估

| 阶段 | 是否可落实 | 机器支撑 | 剩余缺口 |
|---|---|---|---|
| 01-init | 可落实 | 无直接 CLI | 用户确认/业务理解仍靠模型纪律 |
| 02-plan | 可落实 | 无直接 CLI | 依赖图、ADR、风险登记无法自动校验 |
| 03-execute | 部分可落实 | `verify run` | TDD/影响分析/safeguard 触发未机器化，verify 有中文捕获缺陷 |
| 07-subagent | 平台相关 | 无直接 CLI | Codex 必须显式授权，Trae 需人工创建 agent |
| 04-accept | 部分可落实 | `validate evidence` | schema 校验不完整，证据路径不检查 |
| 05-deliver | 部分可落实 | `version-check`、`audit links`、`sync-trae.ps1` dry-run | PR/合并/target 复验仍靠人工 |
| 06-recover | 基本可落实 | checkpoint create/list/resume/validate | 文档恢复路径与 `.yunshu` 权威需统一 |

## 后续建议

1. 先修 `verify run` 的中文输出捕获，这是证据系统的地基。
2. 把 `validate evidence/checkpoint` 做到与 schema 一致，至少补 `date-time`、空字符串、证据路径存在性。
3. 在核心路由中声明“adapter 约束优先”，避免 Codex 环境误启 subagent。
4. 统一恢复权威：`.yunshu/checkpoints/<id>/phase_memory.json` 为机器事实，`docs/handoffs` 只是人工归档。
5. 修正 README safeguard 数量和 `meta-cognition.md` 目录项。
6. 为 `scripts/yunshu.py` 增加最小单元测试，覆盖 version、audit、checkpoint、verify、validate。

## 最终判定

云舒系统已经从“纯提示词流程包”进化到了“流程文档 + 最小 CLI 门禁 + adapter 分层”的状态。它可以被一个遵守云舒纪律的 agent 真实跑起来，本次实例也证明了版本、链接、检查点、恢复和部分验证日志链路可以工作。

但“完整执行逻辑完全落实”这一项未通过。当前更准确的结论是：

> 云舒系统的完整流程可以按文档执行，核心机器门禁已部分落地；但证据采集、schema 校验、平台授权优先级、恢复事实源和 safeguard 自动化仍有缺口，尚不能宣称完全落实。
