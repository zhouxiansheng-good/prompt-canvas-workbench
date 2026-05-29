---
name: compliance-audit-legacy-route
description: "合规审查旧入口。仅保留软件桥接兼容路由，实际审查组件统一使用 04-accept/compliance-audit。"
metadata:
  parent: "browser-automation"
  type: "legacy-route"
  canonical: "components/04-accept/compliance-audit/SKILL.md"
---

# compliance-audit — 旧入口兼容路由

> 主入口已迁移到 `components/04-accept/compliance-audit/SKILL.md`。本文件只负责把旧的 `09-software-bridge/browser-automation/compliance/` 路径导向验收阶段的合规审查组件，避免维护两份重复规则。

## 使用规则

- 用户要求“合规审查”“法律风险”“隐私政策检查”“AI 标识”“支付/退款/许可证检查”时，加载 `components/04-accept/compliance-audit/SKILL.md`。
- 不在本目录维护法规指南、五维合规子组件或环境变量示例。
- 若需要浏览器操作辅助，只在 04-accept 合规审查确认需要打开站点或后台后，再经 `components/09-software-bridge/browser-automation/SKILL.md` 路由到对应浏览器自动化能力。

## 权威路径

| 内容 | 权威路径 |
|------|----------|
| 合规审查入口 | `components/04-accept/compliance-audit/SKILL.md` |
| 隐私合规 | `components/04-accept/compliance-audit/components/01-privacy/SKILL.md` |
| 内容合规 | `components/04-accept/compliance-audit/components/02-content/SKILL.md` |
| 交易合规 | `components/04-accept/compliance-audit/components/03-transaction/SKILL.md` |
| 安全合规 | `components/04-accept/compliance-audit/components/04-security/SKILL.md` |
| 知识产权 | `components/04-accept/compliance-audit/components/05-intellectual-property/SKILL.md` |
| 法规指南 | `components/04-accept/compliance-audit/guides/01-china-ai-regulations.md` |
