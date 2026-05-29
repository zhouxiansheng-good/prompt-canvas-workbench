# 云舒系统修复与优化验证报告

## 元信息

- 修复日期：2026-05-09
- 修复对象：`E:\traework\000 自动化工作流研究\yunshu-system-skill`
- 基准报告：`reports/yunshu-system-full-logic-validation-20260509.md`
- 修复版本：`3.3.0`
- 执行环境：Codex + PowerShell + Windows 中文路径
- 平台适配：已按 `adapters/codex/SKILL.md` 执行，未获得显式授权时不启用子智能体
- 结构化证据：`reports/yunshu-system-remediation-evidence-20260509.json`

## 总结论

本次修复已经覆盖基准报告中影响云舒闭环落地的主要问题：

- `verify run` 的中文/异常字节输出捕获已修复，不再因 Windows 编码导致证据文件为空但状态为 passed。
- `validate evidence` 与 `validate checkpoint` 已补强关键 schema 约束：必填字符串非空、`created_at` 为 ISO 8601 时间、字符串数组不能有空项。
- `validate evidence` 会检查本地证据路径是否真实存在，避免“结构合法但证据丢失”。
- Codex adapter 的限制已在核心路由、02-plan、03-execute、07-subagent 中明确优先于通用子智能体路由。
- 恢复事实源已统一为 `.yunshu/checkpoints/<id>/phase_memory.json`；旧的 `docs/handoffs/` 与 `phase_memory_card.md` 仅作人工兜底。
- README 中 safeguard 数量和 `meta-cognition.md` 目录项已同步。
- TDD/验收措辞已调整为“按任务类型选择合适的新鲜验证证据”，避免文档、配置、流程审计任务被误判为必须先写测试。

当前判定：

| 维度 | 修复后结论 |
|---|---|
| 阶段设计完整性 | 通过 |
| Codex 平台可执行性 | 通过，adapter 优先级已明示 |
| 最小机器门禁 | 通过，版本、链接、checkpoint、证据校验、验证日志可跑 |
| 证据可靠性 | 通过，中文输出回归已验证 |
| schema 关键约束 | 通过，关键约束已有 CLI 与单测覆盖 |
| 是否完全机器强制 safeguards | 部分通过，仍有部分 safeguard 属于控制器纪律而非 hook/CI 强制 |

## 修复清单

| 原问题 | 修复动作 | 证据 |
|---|---|---|
| `verify run` 中文输出捕获不可靠 | 改为二进制捕获，再用 UTF-8、系统 locale、默认编码逐级安全解码，最终 `errors=replace` 保底 | `scripts/yunshu.py`、`.yunshu/verification/verify-20260509-193657-696642-1cd781b7.log` |
| 证据校验没有检查本地路径 | `validate evidence` 对看起来像本地路径的 evidence 项执行存在性检查 | `scripts/yunshu.py`、`tests/test_yunshu_cli.py` |
| schema 关键约束未落地 | 补强非空字符串、ISO 时间、字符串数组空项校验 | `scripts/yunshu.py`、`tests/test_yunshu_cli.py` |
| Codex 子智能体授权冲突 | 在核心路由和 02/03/07 组件中明确 adapter 优先，Codex 必须用户显式授权 | `SKILL.md`、`components/02-plan/SKILL.md`、`components/03-execute/SKILL.md`、`components/07-subagent/SKILL.md` |
| 恢复来源双轨 | 明确 `.yunshu/checkpoints/<id>/phase_memory.json` 是机器恢复唯一事实来源 | `components/01-init/SKILL.md`、`components/03-execute/SKILL.md`、`components/06-recover/SKILL.md` |
| README safeguard 数量漂移 | 数量改为 24，并补充 `meta-cognition.md` | `README.md` |
| TDD/测试措辞对非代码任务过硬 | 将“测试通过”泛化为“合适的新鲜验证证据”，代码行为变更仍优先测试 | `SKILL.md`、`README.md`、`components/03-execute/SKILL.md`、`components/04-accept/SKILL.md` |

## 本次实例回归

本次仍以“修复云舒系统自身”为实例，按云舒闭环执行：

| 云舒阶段 | 本次动作 | 产物 |
|---|---|---|
| 01-init | 读取基准验证报告、Codex adapter、工作区状态和现有交接摘要 | 明确修复目标和 DoD |
| 02-plan | 按问题优先级确定先修证据地基，再修文档冲突和恢复权威 | 修复矩阵 |
| 03-execute | 修改 CLI、测试和流程文档，保持范围集中 | `scripts/yunshu.py`、`tests/test_yunshu_cli.py`、组件文档 |
| 04-accept | 使用单测、编译、版本、链接、中文输出回归、结构化证据校验验收 | `.yunshu/verification/*.log` |
| 05-deliver | 输出本报告、结构化证据和交付检查点 | `reports/yunshu-system-remediation-*.json/md`、`.yunshu/checkpoints/` |

## 新鲜验证证据

| 验证声明 | 命令 | 结果 | 证据 |
|---|---|---|---|
| 单元测试通过 | `python -m unittest discover -s tests -v` | passed，7 tests OK | `.yunshu/verification/verify-20260509-193647-225409-fc64b70b.log` |
| CLI 可编译 | `python -m py_compile scripts\yunshu.py` | passed | `.yunshu/verification/verify-20260509-193647-749245-05f3206b.log` |
| 版本元数据一致 | `python scripts\yunshu.py version-check` | passed | `.yunshu/verification/verify-20260509-193648-178155-de29b6df.log` |
| Markdown 内链通过 | `python scripts\yunshu.py audit links` | passed | `.yunshu/verification/verify-20260509-193648-557188-f3c64af6.log` |
| 中文输出可被证据化捕获 | `python scripts\yunshu.py verify run --claim ... --command "powershell -NoProfile -Command Write-Output 中文输出"` | passed，证据文件包含 `中文输出` | `.yunshu/verification/verify-20260509-193657-696642-1cd781b7.log` |
| 修复证据文件可校验 | `python scripts\yunshu.py validate evidence reports\yunshu-system-remediation-evidence-20260509.json` | passed | `.yunshu/verification/verify-20260509-193907-466570-c6fb50ba.log` |

## 剩余限制

- safeguards 的大量判断仍属于“控制器必做门禁”，不是 hook、CI 或状态机强制。当前修复没有把所有 safeguard 自动化。
- `sync-trae.ps1` 仍以 dry-run/Apply 同步为主，目标安装副本的自动复验可以作为下一步增强。
- 本仓库上层工作区存在旧副本和旧报告，本次只修复 `yunshu-system-skill/` 主包，没有清理上层散落副本。

## 最终判定

基准报告中的阻塞性问题已经修复。云舒系统现在可以更可靠地完成“调查 -> 计划 -> 执行 -> 验收 -> 交付 -> 恢复”的闭环，并且关键证据链可由 CLI 复跑验证。

更准确的边界是：云舒系统的核心执行逻辑和最小机器门禁已落实；全部 safeguard 的强制自动化仍是后续增强方向。
