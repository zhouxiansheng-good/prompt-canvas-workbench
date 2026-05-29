---
name: browser-automation
description: "浏览器自动化子技能。识别目标网站类型并路由到 Cloudflare、Supabase 等 Web UI 自动化子技能。"
metadata:
  parent: "09-software-bridge"
  type: "software-bridge-child"
---

# browser-automation — 浏览器自动化子技能

> 通过浏览器自动化操作任何网站。嵌套于 09-software-bridge 之下，专司 Web UI 层面的自动化交互。

---

## 触发条件

用户输入匹配以下任一模式时激活：
- "浏览器自动化"
- "打开浏览器"
- "操作网站"
- "登录网站"

---

## 能力边界

| 能力 | 说明 |
|------|------|
| 浏览器操控 | 启动浏览器、导航页面、等待元素、点击、输入、截图 |
| 身份认证 | 自动填充凭证、处理 2FA（用户手动输入）、会话保持 |
| 数据操作 | 在 Web UI 中执行查询、查看/修改数据、提交表单 |
| 结果验证 | 通过页面元素或截图确认操作成功 |

---

## 安全规则（不可覆盖）

1. **密码来源**：密码必须从环境变量读取，禁止硬编码到任何文件
2. **日志脱敏**：禁止在日志、聊天记录中输出明文密码
3. **2FA 隔离**：验证码由用户手动输入，禁止自动化绕过
4. **会话安全**：会话 token 仅保存在内存，禁止持久化到磁盘
5. **截图脱敏**：若截图包含密码输入框，确保密码已用掩码显示

---

## 子技能列表

| 子技能 | 路径 | 触发条件 | 说明 |
|--------|------|----------|------|
| **Supabase Dashboard** | `supabase/` | "操作 Supabase" / "Supabase SQL" / "Supabase 表" | 登录 Supabase Dashboard、执行 SQL、管理表结构 |
| **Cloudflare Pages** | `cloudflare/` | "部署网站" / "部署到 Cloudflare" / "Cloudflare Pages 部署" / "上传 dist" | Cloudflare Pages 静态网站部署与管理 |
| **合规审查** | `../../04-accept/compliance-audit/` | "审查合规" / "法律风险" / "合规检查" / "项目风险评估" | 全面审查网站项目的法律合规性；`compliance/` 仅作旧入口兼容 |
| Stripe（未来） | `stripe/` | "操作 Stripe" / "Stripe 支付" | Stripe 支付管理、订单查看 |

---

## 使用流程

```
识别目标网站  →  加载对应子技能  →  委托执行  →  验证结果
```

**本层职责边界**：browser-automation 作为中间层元技能，只负责**识别目标网站类型**并**路由到对应子技能**。不处理具体登录、操作、执行细节。

1. **识别目标网站**：根据用户意图匹配子技能
   - Cloudflare Pages 部署 → `cloudflare/`
   - Supabase 操作 → `supabase/`
   - 合规审查 → `../../04-accept/compliance-audit/`（旧路径 `compliance/` 只跳转）
2. **加载子技能**：读取对应子目录下的 `SKILL.md`
3. **委托执行**：将用户原始意图完整传递给子技能，由子技能自路由、自执行
4. **验证结果**：接收子技能返回的执行结果，向用户汇报

### 子技能自路由规则

每个子技能（cloudflare/supabase）内部遵循相同的路由模式；合规审查统一交给 04-accept 的权威组件：

```
用户意图 → 匹配组件 → 加载组件SKILL.md → 组件执行 → 返回结果
```

**嵌套深度**：无限制。子技能可继续向下嵌套组件，组件可嵌套子组件。
**上下文隔离**：每一层只加载当前层需要的文件，不向上层泄露下层实现细节。

### 子技能路由表

| 用户意图关键词 | 子技能路径 | 下一层组件 |
|----------------|------------|------------|
| "部署网站" / "Cloudflare" | `cloudflare/` | 01-auth → 02-project → 03-deploy |
| "操作 Supabase" / "Supabase" | `supabase/` | 01-auth → 02-sql-editor / 03-table-manager |
| "审查合规" / "合规" / "法律" | `../../04-accept/compliance-audit/` | 隐私 / 内容 / 交易 / 安全 / 知识产权五维审查 |

---

## 目录导航

| 层级 | 内容 | 路径 |
|------|------|------|
| L3 | Supabase Dashboard 操作 | `supabase/SKILL.md` |
| L3 | Supabase 认证 | `supabase/components/01-auth/SKILL.md` |
| L3 | Supabase SQL Editor | `supabase/components/02-sql-editor/SKILL.md` |
| L3 | Supabase 表管理 | `supabase/components/03-table-manager/SKILL.md` |
| L3 | Supabase 安全指南 | `supabase/guides/01-security.md` |
| L3 | Supabase 环境变量示例 | `supabase/.env.example` |
| L3 | Cloudflare Pages 部署 | `cloudflare/SKILL.md` |
| L3 | Cloudflare 认证 | `cloudflare/components/01-auth/SKILL.md` |
| L3 | Cloudflare 项目选择 | `cloudflare/components/02-project/SKILL.md` |
| L3 | Cloudflare 部署执行 | `cloudflare/components/03-deploy/SKILL.md` |
| L3 | Cloudflare 安全指南 | `cloudflare/guides/01-security.md` |
| L3 | Cloudflare 环境变量示例 | `cloudflare/.env.example` |
| L3 | 合规审查旧入口 | `compliance/SKILL.md` |
| L3 | 合规审查权威入口 | `../../04-accept/compliance-audit/SKILL.md` |
| L4 | 隐私合规审查 | `../../04-accept/compliance-audit/components/01-privacy/SKILL.md` |
| L4 | 内容合规审查 | `../../04-accept/compliance-audit/components/02-content/SKILL.md` |
| L4 | 交易合规审查 | `../../04-accept/compliance-audit/components/03-transaction/SKILL.md` |
| L4 | 安全合规审查 | `../../04-accept/compliance-audit/components/04-security/SKILL.md` |
| L4 | 知识产权审查 | `../../04-accept/compliance-audit/components/05-intellectual-property/SKILL.md` |
| L4 | 中国AI法规指南 | `../../04-accept/compliance-audit/guides/01-china-ai-regulations.md` |
| L4 | 合规审查环境变量 | `../../04-accept/compliance-audit/.env.example` |
