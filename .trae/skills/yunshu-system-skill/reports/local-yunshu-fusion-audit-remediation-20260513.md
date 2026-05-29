# 本地云舒融合审计与修复报告（2026-05-13）

## 结论

本轮审计对象是 `E:\traework\000 自动化工作流研究\yunshu-system-skill`。该包已经融合 BMad、frontend-design、webapp-testing、输出充分性、上下文账本等能力；主流程是完整的。修复重点是把新增能力接入规范、门禁、路由和分发边界，避免“材料在目录里，但触发和验收不稳定”。

## 已修复问题

| 类别 | 问题 | 修复 |
|------|------|------|
| 技能元数据 | 根技能与组件在 frontmatter 顶层使用 `version` / `phase`，与当前 skill-creator 规范冲突 | 迁移到 `metadata.version` / `metadata.phase` |
| 阶段语义 | `06-recover` / `07-subagent` 使用 `recovery` / `sub`，与 CLI 阶段枚举不一致 | 对齐为 `recover` / `subagent` |
| 版本漂移 | Codex adapter 与 Trae 示例仍是 `3.4.0`，且 `version-check` 未覆盖 adapter 示例 | 更新到 `3.6.0`，扩展 `version-check` 并补测试 |
| 平台冲突 | 共享组件/模板残留 `TodoWrite`、`SearchCodebase`、`Trae Task tool` | 改为平台中立表达，保留 adapter 决策边界 |
| BMad 措辞 | BMad 增强层残留 `V1` / `后续 P2` 语义 | 改为当前可选能力边界 |
| 前端融合路标 | `frontend-design` / `webapp-testing` 已接入 03-execute 门禁，但 README 导航不完整 | README 补充目录、能力说明和 v3.6.0 新特性 |
| 分发卫生 | `tmp-yunshu-*`、`.pytest_cache`、`__pycache__` 留在本地包和同步范围 | 删除运行残留，更新 `.gitignore` 与 `sync-trae.ps1` 排除规则 |
| UI 元数据 | 根技能缺少 `agents/openai.yaml` | 新增最小 UI 元数据 |

## 验证证据

| 门禁 | 结果 |
|------|------|
| `pytest -q` | 通过，14 passed |
| `python scripts\yunshu.py version-check` | 通过 |
| `python scripts\yunshu.py audit links` | 通过 |
| `skill-creator quick_validate` | 通过 |
| 组件级 quick_validate | 01-init、02-plan、03-execute、webapp-testing、04-accept、05-deliver、06-recover、07-subagent、bmad-enhance、Codex adapter 全部通过 |
| `powershell -ExecutionPolicy Bypass -File scripts\sync-trae.ps1` | dry-run 通过，118 files |

## 保留项

- `.yunshu/` 保留为本地机器事实来源，但同步脚本已排除。
- `reports/` 保留为审计与交付材料。
- 未执行 `sync-trae.ps1 -Apply`，避免覆盖 Trae 安装副本。

