# Project Context Sync：BMad project-context 与云舒上下文账本同步

## 目标

把 BMad `project-context.md` 中的项目规则、技术栈、代码组织和实现偏好纳入云舒上下文账本，作为 02-plan、03-execute 和 07-subagent 的新鲜上下文来源。

## 输入

- BMad `_bmad-output/project-context.md` 或任意 `project-context.md`
- 云舒 `.yunshu/context/` 账本
- 相关项目 README、配置文件、代码模式

## 输出

建议使用 `templates/bmad_project_context.md` 生成：

- 技术栈与版本摘要
- 代码组织规则
- 测试和验证规则
- API / 数据 / 配置约定
- 禁止事项
- 新鲜度依据
- 与云舒账本的差异

## 同步方向

### project-context -> 云舒

用于计划和执行阶段：

1. 读取 `project-context.md`。
2. 提取技术栈、实现规则、代码组织、测试要求。
3. 与本地 README、package/pyproject/config、现有代码模式交叉验证。
4. 写入 `.yunshu/context/`。
5. 在 plan/spec/story 分派包中引用 context_id。

### 云舒 -> project-context

用于后续沉淀：

1. 从 `.yunshu/context/` 中提取稳定、反复使用的项目规则。
2. 只同步“长期有效”的规则，不同步一次性调查结论。
3. 标记来源和更新时间。
4. 用户确认后更新 `project-context.md`。

默认只要求第一种方向；第二种方向作为人工协助，不自动覆盖文件。

## 新鲜度规则

必须用云舒 CLI 检查来源新鲜度：

```bash
python scripts/yunshu.py context list --task-id <task_id>
python scripts/yunshu.py context show <context_id>
python scripts/yunshu.py context status <context_id>
```

`project-context.md` 出现以下情况时视为 stale：

- 技术栈版本与本地配置不一致。
- 代码组织规则与实际目录不一致。
- 测试命令不存在或失败。
- 最近重大架构变更未同步。
- 文档没有来源或更新时间。

## 冲突处理

| 冲突 | 处理 |
|------|------|
| project-context 与代码不一致 | 以代码和配置证据为准，记录文档漂移 |
| project-context 与云舒任务约束冲突 | 以用户最新确认的任务约束为准 |
| project-context 缺测试规则 | 回到 02-plan 补测试策略 |
| project-context 过旧 | 只作为参考，不作为执行约束 |

## 上下文账本记录

```bash
python scripts/yunshu.py context record \
  --task-id <task_id> \
  --phase plan \
  --source <project-context.md> \
  --finding "已提取 project-context 中的长期实现规则" \
  --decision "<采用或拒绝的规则>" \
  --gap "<与代码库不一致或仍需确认的规则>" \
  --next-read "<下次只需补读的配置/目录>"
```

## 反模式

- 把 project-context 当成永远正确
- 用 project-context 覆盖用户最新约束
- 同步一次性调查结论到长期项目规则
- 自动覆盖 project-context 而不让用户确认
