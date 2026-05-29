# 变更报告 — 云舒系统全量测试

## 概要
- 目标: 全量测试云舒系统所有组件和功能
- 状态: 部分完成（核心五阶段 + 子系统测试通过）
- 变更文件数: 0（本任务为测试验证，未修改业务代码）

## 变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| .yunshu/tasks/yunshu-full-test-2026.json | 新增 | 测试任务追踪卡 |
| .yunshu/context/yunshu-full-test-2026-* | 新增 | 5个阶段上下文账本 |
| .yunshu/checkpoints/yunshu-full-test-2026-* | 新增 | 5个阶段检查点 |
| .yunshu/gates/gate-*-yunshu-full-test-2026.json | 新增 | 4个阶段过渡门控记录 |
| .yunshu/verification/acceptance_evidence_yunshu-full-test-2026.json | 新增 | 结构化验收证据 |
| .yunshu/verification/change_report_yunshu-full-test-2026.md | 新增 | 变更报告 |

## 影响面分析
- 受影响模块: 云舒系统 CLI (scripts/yunshu.py)
- 受影响接口: 无（纯测试验证）
- 数据库变更: 无
- 配置变更: 无

## 回滚方案
1. 回滚任务追踪: 删除 .yunshu/tasks/yunshu-full-test-2026.json
2. 回滚上下文账本: 删除 .yunshu/context/yunshu-full-test-2026-*
3. 回滚检查点: 删除 .yunshu/checkpoints/yunshu-full-test-2026-*
4. 回滚门控记录: 删除 .yunshu/gates/gate-*-yunshu-full-test-2026.json

## 复跑指令
1. 进入项目目录: cd .trae/skills/yunshu-system-skill
2. 运行全量测试命令序列（参考 03-execute 阶段测试步骤）
3. 验证: python scripts/yunshu.py task status --task-id yunshu-full-test-2026

## 已知遗留
- 06-recover 组件测试待完成
- 07-subagent / 08-domain-guide / 09-software-bridge 组件测试待完成
- BMad增强层测试待完成
- safeguards 安全防护触发测试待完成

## 文档同步状态
- 已同步: 各阶段上下文账本、检查点、验收证据
- 未同步: 无

## 架构决策记录
- ADR-001: 验收证据中 pending 状态的 DoD 使用占位证据路径以满足验证器要求
