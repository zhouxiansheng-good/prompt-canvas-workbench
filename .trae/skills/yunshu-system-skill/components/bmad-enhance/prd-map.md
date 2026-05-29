# PRD Map：任务卡、PRD 与 Tech Spec 映射

## 目标

把 BMad 的 PRD、Product Brief、PRFAQ 或 Tech Spec 转换为云舒可执行的任务卡增强信息，确保需求进入 02-plan 前具备清晰目标、可验证 DoD、约束、风险和非目标。

## 输入

至少需要：

- 云舒任务卡：`goal`、`done_definition`、`constraints`、`risks`、`non_goals`
- 可选 BMad 产物：`PRD.md`、`product-brief.md`、`prfaq.md`、`tech-spec.md`

## 输出

建议使用 `templates/bmad_prd_map.md` 生成：

- 目标对齐结论
- 用户 / 场景 / 问题陈述
- 验收标准映射
- 约束与假设
- 风险与开放问题
- 非目标
- 需要回到 01-init 澄清的阻塞缺口

## 映射表

| 云舒字段 | BMad 常见字段 | 转换规则 |
|----------|---------------|----------|
| `goal` | Product Goal / Problem Statement / Objective | 压缩成一句话目标；如果 PRD 有多个目标，拆成主目标和次目标 |
| `done_definition` | Acceptance Criteria / Success Metrics | 每条必须能回答“通过/未通过”；模糊指标进入 gaps |
| `constraints` | Constraints / Assumptions / Requirements | 硬约束保留为 constraints；未经验证的假设写入 assumptions |
| `risks` | Risks / Open Questions / Dependencies | 进入 02-plan 风险登记表 |
| `non_goals` | Out of Scope / Not Now | 作为范围防线，防止计划膨胀 |

## 门禁

进入 02-plan 前，必须满足：

- 目标不超过一个主目标。
- 至少 3 条可检查 DoD。
- 非目标明确。
- PRD 中的开放问题已分类为阻塞 / 非阻塞。
- BMad 文档和云舒任务卡冲突时，以用户最新确认和云舒任务卡为准。

## 缺口处理

| 缺口 | 处理 |
|------|------|
| PRD 目标和任务卡目标冲突 | 返回 01-init，只问一个必要问题 |
| 验收标准不可检查 | 改写为可验证标准；无法改写则记为阻塞 |
| BMad 文档有假设但无证据 | 写入 risks / assumptions |
| PRD 范围过大 | 拆成多个云舒任务卡 |

## 上下文账本记录

```bash
python scripts/yunshu.py context record \
  --task-id <task_id> \
  --phase plan \
  --source <PRD.md> \
  --finding "已完成 PRD 到云舒任务卡字段映射" \
  --gap "<开放问题或缺口>" \
  --next-read "<下一轮只需补读的章节>"
```

## 反模式

- 直接复制 PRD 原文作为任务卡
- 把 Success Metrics 当作测试命令
- 忽略 Out of Scope
- 用“优化、提升、完善”这类词充当 DoD
