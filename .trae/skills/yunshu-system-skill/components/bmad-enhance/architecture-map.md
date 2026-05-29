# Architecture Map：架构文档到云舒计划规范映射

## 目标

把 BMad 的 `architecture.md` 或架构说明映射为云舒 02-plan 所需的 spec、ADR、WBS、风险和测试策略。

## 输入

- 云舒任务卡
- 可选 `PRD.md`
- BMad `architecture.md` 或等价架构文档
- 可选 `project-context.md`

## 输出

建议使用 `templates/bmad_architecture_map.md` 生成：

- 模块边界
- 接口契约
- 数据流和数据归属
- 技术约束
- ADR 决策记录
- 风险登记
- 测试策略
- 回滚点

## 映射表

| BMad 字段 | 云舒产物 | 转换规则 |
|-----------|----------|----------|
| Components / Modules | `plan.md` WBS、`spec.md` 边界 | 每个模块必须有职责、输入、输出和依赖 |
| API / Interfaces | `spec.md` 输入输出契约 | 写清字段、类型、错误、边界条件 |
| Data Model / Data Flow | `spec.md` 数据边界 | 明确数据归属和跨模块读写方式 |
| Tech Stack | 约束 / 风险 | 与现有代码库不一致时标为风险 |
| Decisions | ADR | 记录背景、选项、决策、影响、可逆性 |
| Deployment / Operations | 交付和回滚策略 | 涉及部署、配置、迁移时必须有回滚 |

## 架构门禁

进入执行前必须通过：

- 已明确模块边界，不存在“所有东西都放一个模块”的大泥球倾向。
- 已明确接口契约，执行时不需要临时发明字段。
- 已明确数据归属，跨模块访问有边界。
- 关键架构决策已有 ADR。
- 每个高风险架构动作有回滚策略。
- 测试策略覆盖关键路径和风险点。

## 冲突处理

| 冲突 | 处理 |
|------|------|
| BMad 架构与现有代码模式冲突 | 优先现有代码库证据；需要改写时进入风险登记 |
| 架构文档缺接口细节 | 回到 02-plan 补 spec，不允许进入执行 |
| 技术栈建议引入新依赖 | 触发 `safeguards/dependency.md` |
| 涉及大规模重构 | 触发 `safeguards/refactor.md` 并要求回滚点 |

## 上下文账本记录

```bash
python scripts/yunshu.py context record \
  --task-id <task_id> \
  --phase plan \
  --source <architecture.md> \
  --finding "已完成架构到云舒 spec/ADR/WBS 的映射" \
  --decision "<采用的关键架构决策>" \
  --gap "<仍缺的接口/数据/风险信息>"
```

## 反模式

- 把架构图当成可执行计划
- 只有模块名，没有输入输出契约
- 技术栈选择没有证据
- ADR 只写“选择了什么”，不写“为什么”
