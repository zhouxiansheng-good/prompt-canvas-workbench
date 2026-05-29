# 任务卡：Frontend-Design Skill 融合到云舒系统

## 目标（Goal）
将 Anthropic 官方的 frontend-design skill 整合到云舒系统 03-execute 实现模块中，使前端开发任务具备设计思维流程、美学合规检查和设计验证证据。

## 完成定义（Done Definition）
1. [ ] 创建 `frontend-design/` 目录及所有必要文件
2. [ ] 修改 `03-execute/SKILL.md` 增加设计思考阶段
3. [ ] 修改 `gates.md` 增加前端设计门禁
4. [ ] 所有文件通过云舒代码自检（规范/类型/占位符/边界/AI冗余）
5. [ ] 融合方案文档与实际实现一致
6. [ ] 创建验证证据（文件清单 + 目录结构截图）

## 约束（Constraints）
- 不改变云舒现有 TDD、证据化验证、代码自检流程
- 设计阶段仅在前端任务时触发，非前端任务不受影响
- 所有新增文件遵循云舒现有文件命名和格式规范
- 不引入外部依赖（纯 Markdown 文件）
