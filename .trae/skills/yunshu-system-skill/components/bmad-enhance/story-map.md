# Story Map：BMad Story 到云舒执行分派包映射

## 目标

把 BMad Story 转换为云舒 03-execute 或 07-subagent 可使用的自包含任务分派包，减少实现阶段上下文缺失和范围漂移。

## 输入

- 云舒 `plan.md` / `spec.md` / `tasks.md`
- BMad `story-[slug].md` 或等价 Story 文档
- 可选 `project-context.md`
- 相关代码调查结论或 context ledger

## 输出

建议使用 `templates/bmad_story_map.md` 生成：

- 执行任务目标
- 用户价值
- 写入范围
- 必需上下文
- 接口契约
- 验收标准
- 验证命令
- 非目标
- 风险、回滚和 concerns

## 映射表

| BMad Story 字段 | 云舒分派包字段 | 转换规则 |
|-----------------|----------------|----------|
| Story / User Value | `task_goal` / `user_value` | 保留用户价值，但执行目标必须具体到文件或模块 |
| Acceptance Criteria | `acceptance` | 每条映射到 DoD 或测试策略 |
| Dev Notes | `required_context` | 只保留执行所需上下文，避免大段粘贴 |
| Tasks / Subtasks | `execution_steps` | 转成 ≤30 分钟的云舒任务 |
| Dependencies | `dependencies` / `risks` | 缺失依赖必须阻塞或登记风险 |
| Testing | `validation_commands` | 转成可运行命令或人工检查步骤 |

## 03-execute 使用规则

适合串行执行时，Story Map 产物作为执行前上下文：

1. 读取 Story Map。
2. 做变更前影响分析。
3. 按任务步骤执行。
4. 每个验证声明写入证据。
5. 完成后进入 04-accept。

## 07-subagent 使用规则

适合子智能体时，Story Map 产物作为分派包：

- 必须明确 write_scope，避免多个子智能体改同一文件。
- 必须包含验收标准和验证命令。
- 必须包含非目标，防止范围蔓延。
- Codex 中只有用户明确授权子智能体时才可分派。

## 门禁

执行前必须满足：

- Story 不依赖未确认的 PRD 或架构假设。
- 写入范围明确。
- 验收标准可检查。
- 验证命令可运行，或人工验证步骤足够具体。
- 相关 project-context 已检查新鲜度。

## 上下文账本记录

```bash
python scripts/yunshu.py context record \
  --task-id <task_id> \
  --phase execute \
  --source <story.md> \
  --finding "已完成 Story 到云舒执行分派包的映射" \
  --action "准备用于 03-execute 或 07-subagent" \
  --gap "<仍缺的实现上下文>"
```

## 反模式

- 让子智能体自己读一堆 PRD/架构材料
- Story 没有 write_scope 就进入并行
- 验收标准只写“功能正常”
- Story Map 产物没有回写 context ledger
