---
name: 04-accept
description: "验收。实践是检验真理的唯一标准。两阶段审查（规范符合性→代码质量）+ DoD 证据链。缺证据 = 未完成。"
metadata:
  phase: "4"
---

# 04-accept：实践检验

> **"实践是检验真理的唯一标准"** — 没有合适的新鲜验证证据就不算完成；代码行为变更通常需要测试，文档/配置/流程任务可用编译、链接、CLI 或结构化校验证明。

## 职责

用可复跑、可审计的方式证明"确实做成了"。两阶段审查确保既做对了事（规范符合），又把事做好了（代码质量）。

## 子组件路由表

| 用户意图 | 子组件路径 | 子组件职责 |
|----------|------------|------------|
| "合规审查" / "法律风险" / "合规检查" / "审查合规" | `compliance-audit/SKILL.md` | 项目法律合规性审查、风险清单、修复建议 |
| "验收" / "检查验收" / "验证完成" / "验收测试" | 本组件继续执行 | 两阶段审查（规范符合性→代码质量）+ DoD证据链 |

<硬门禁>
任一完成定义缺证据 = 未完成，不许进入交付阶段。
</硬门禁>

---

## Step 1：运行基础验证

**目标**：先取得与任务类型匹配的新鲜验证证据，作为验收基础。

**方法**：

```bash
# 代码行为变更：运行项目测试套件
npm test / cargo test / pytest / go test ./...

# 文档 / 配置 / 流程 / 审计任务：运行对应机器门禁
python scripts/yunshu.py audit links
python scripts/yunshu.py validate evidence acceptance_evidence.json
python -m py_compile scripts/yunshu.py
```

**【前端任务】E2E 验证路径**（融合自 Anthropic webapp-testing）：

前端任务除运行单元测试外，还必须执行 E2E 验证：

1. 判断测试路径（决策树，详见 `03-execute/webapp-testing/SKILL.md`）：
   - 静态 HTML → 读源码识别选择器 → Playwright 验证
   - 动态 WebApp → 启动服务器 → Reconnaissance-Then-Action
2. 执行 Playwright E2E 验证脚本
3. 采集截图证据 + 控制台日志
4. 截图和日志作为 DoD 证据的一部分

```bash
# 前端 E2E 验证示例
python components/03-execute/webapp-testing/scripts/with_server.py \
  --server "npm run dev" --port 5173 \
  -- python your_e2e_test.py
```

**如果基础验证失败**：
```text
基础验证失败（N 个失败）。必须修复后才能继续验收：

[列出失败项]

无法继续验收，回到执行阶段修复。
```

→ 回到 `components/03-execute/SKILL.md` 修复

**如果基础验证通过** → 继续 Step 2

---

## Step 2：规范符合性审查

> 参考 Superpowers spec-reviewer：不要信任实现者的报告，独立验证。

**核心原则**：读代码验证，不信任报告。

### 2.1 逐条 DoD 核查

**方法**：对任务卡中的每条 DoD，独立验证：

```text
DoD: "用户可以通过 OAuth 登录"
  验证方式: 启动服务 → 访问登录页 → 点击 OAuth → 确认跳转和回调
  实际结果: [通过/未通过]
  证据: [截图/日志/测试输出]
```

**检查维度**：

| 维度 | 具体检查 |
|------|----------|
| **缺失需求** | 有没有 DoD 被跳过或遗漏？声称实现了但实际没做？ |
| **多余功能** | 有没有做了但不在 DoD 中的功能？过度工程？ |
| **理解偏差** | 有没有对 DoD 的理解与用户意图不同？解决了错误的问题？ |
| **实现深度** | 是真做了还是只做了表面？错误处理、边界情况是否覆盖？ |

### 2.2 代码 vs 规范对照

**方法**：读实际代码，逐行对比计划/规范中的要求：

1. 打开计划文件和规范文件
2. 对每个要求，在代码中找到对应实现
3. 找不到 → 标记为"缺失"
4. 找到了但与规范不符 → 标记为"偏差"
5. 找到了规范中没有的 → 标记为"多余"

### 2.3 规范符合性判定

```text
✅ 规范符合 — 所有 DoD 都有代码实现，无多余功能
❌ 发现问题 — [列出具体缺失/偏差/多余，附 file:line 引用]
```

**发现问题 → 回到执行阶段修复，修复后重新从 Step 1 开始验收**

---

## Step 3：代码质量审查

> 参考 Superpowers code-quality-reviewer：规范符合之后，再检查代码是否做得好。

**只在规范符合性审查通过后才执行此步骤。**

### 3.1 代码质量检查项

| 检查项 | 具体检查 | 严重度 |
|--------|----------|--------|
| **单一职责** | 每个文件是否只有一个明确的职责？ | 重要 |
| **接口清晰** | 模块间是否有清晰的接口？能否独立理解和测试？ | 重要 |
| **文件大小** | 新增文件是否过大？修改是否显著膨胀了已有文件？ | 次要 |
| **命名质量** | 函数/变量名是否清晰表达意图？ | 次要 |
| **重复代码** | 有没有可以提取的重复逻辑？ | 重要 |

**AI缺陷模式专项审查**：

在常规质量检查项之外，额外加载 `safeguards/code-quality.md` 中的AI特有缺陷模式清单，重点检查：
1. 假数据/硬编码（AI最常犯的错误）
2. 空catch/静默吞错
3. 边界条件缺失
4. 测试只覆盖快乐路径
5. 接口语义不匹配（类型对但语义错）

**安全漏洞专项审查**（代码涉及安全相关功能时触发）：

当代码中包含安全触发关键词时，额外加载 `safeguards/security.md` 中的安全漏洞模式清单，重点检查：
1. SQL注入/命令注入/XSS/路径遍历
2. 硬编码密钥/弱密码/权限缺失/越权访问
3. 敏感信息泄露（日志/注释/错误响应）
4. DevOps配置安全（Docker root/密钥明文/端口全开）

| **错误处理** | 错误路径是否处理？异常是否正确传播？ | 严重 |
| **测试覆盖** | 关键路径是否有测试？边界情况是否覆盖？ | 严重 |
| **安全问题** | 有没有硬编码密钥/SQL 注入/XSS 等风险？ | 严重 |
| **AI 冗余** | 有没有 AI 生成的冗余代码？（多余注释、异常防御性检查、`any` 类型转换、深度嵌套、风格不一致） | 重要 |

### 3.2 严重度分级与处理

| 严重度 | 定义 | 处理方式 |
|--------|------|----------|
| **严重** | 会导致崩溃/数据丢失/安全漏洞 | 必须立即修复，阻塞交付 |
| **重要** | 影响可维护性/可测试性/正确性 | 应该修复，修复后才能交付 |
| **次要** | 代码风格/命名/小改进 | 记录，可以后续处理 |

### 3.3 代码质量判定

```text
✅ 通过 — 无严重/重要问题
⚠️ 有问题 — [列出严重/重要问题，附 file:line 引用]
```

**有严重/重要问题 → 回到执行阶段修复，修复后重新从 Step 1 开始验收**

---

### 3.4 元认知与输出充分性门禁

> 解决P-053理解债/P-054主观偏差：验收前，确认验收标准完整性。

**触发条件**：代码质量判定通过后、进入Step 3.5之前自动触发

**执行动作**：

1. 读取 `safeguards/meta-cognition.md`
2. 执行五维信息审视（重点维度1意图 + 维度4假设）
3. 执行输出充分性四问：验收结论是否逐条覆盖 DoD、证据是否新鲜可复跑、失败项是否捕获
4. 标记所有可查证缺口、🟡非阻塞缺口、🔴阻塞缺口
5. 可查证缺口 → 先补验证；🔴阻塞缺口 → 返回01-init补充验收标准；🟡非阻塞缺口 → 写入已知限制后继续
6. 无阻塞缺口 → 进入Step 3.5验收门禁

**关键原则**：验收标准不完整时不许进入验收，验收不完整 = 交付风险

---

## Step 3.5：验收门禁

> 代码质量审查通过后，必须依次通过以下2个门禁。详见 [gates.md](gates.md)。

| 门禁 | 覆盖问题 | 关键原则 |
|------|----------|----------|
| 理解与可持续性 | P-053理解债/P-069存活率低 | 理解未通过=验收未通过；可持续性🔴=验收未通过 |
| 债务与团队 | P-051技术债务/P-052责任链/P-072~077团队 | 🔴债务未修复=验收未通过；无审查签名=验收未通过 |

**门禁1未通过 → 补充理解或修复可持续性问题后重新验证**
**门禁2未通过 → 修复关键债务或补充责任链后重新验证**

---

## Step 4：DoD→证据映射

**目标**：为每条 DoD 生成结构化证据，形成可审计的证据链。

### 4.1 证据类型

| 证据类型 | 适用场景 | 示例 |
|----------|----------|------|
| 测试输出 | 自动化验证 | `pytest` 输出：34/34 passed |
| 命令输出 | 运行验证 | `curl localhost:3000/health` → 200 OK |
| 截图 | UI 验证 | 登录页截图、功能操作截图 |
| 文件路径 | 代码存在 | `src/auth/oauth.py:42-67` |
| 日志片段 | 行为验证 | 服务启动日志、请求处理日志 |

### 4.2 证据质量标准

每条证据必须满足：

- **可复跑**：别人能按相同步骤得到相同结果
- **可引用**：有具体的文件路径/行号/命令输出
- **有时效**：是本次验收时新鲜获取的，不是历史缓存
- **无模糊**：不用"应该"/"大概"/"看起来"，只有"通过"/"未通过"

### 4.3 生成证据文档

使用 `templates/acceptance_runbook.md` 模板生成验收剧本。

**产物**：

1. `acceptance_runbook.md`：验收剧本（每条 DoD 的验证步骤和结果）
2. `acceptance_evidence.json`：结构化验收证据（包含 task_id / run_id / status / dod_items / failure_capture）
3. `.yunshu/verify-log.tsv`：使用 `python scripts/yunshu.py verify run ...` 记录的声明级验证日志

**证据文档结构**：

```json
{
  "task_id": "xxx",
  "run_id": "accept-20260509-103000",
  "status": "passed",
  "created_at": "2026-05-09T10:30:00Z",
  "dod_items": [
    {
      "id": "DOD-1",
      "description": "用户可以通过 OAuth 登录",
      "status": "passed",
      "evidence": [
        "screenshots/oauth-login.png",
        ".yunshu/verification/verify-20260509-103000.log"
      ]
    }
  ],
  "failure_capture": {}
}
```

生成后必须运行：

```bash
python scripts/yunshu.py validate evidence acceptance_evidence.json
```

**验收结果写入上下文账本**（强制）：

```bash
python scripts/yunshu.py context record \
  --task-id <task_id> \
  --phase accept \
  --source "acceptance_evidence.json, acceptance_runbook.md" \
  --finding "<验收结论：N/N条DoD通过，代码质量结论>" \
  --action "<验收阶段已完成动作>" \
  --gap "<遗留问题或限制>" \
  --next-read "<交付阶段需读取的文件>"
python scripts/yunshu.py validate context .yunshu/context/<context_id>.json
```

验收声明建议通过 CLI 记录：

```bash
python scripts/yunshu.py verify run --claim "DoD-1 用户可以通过 OAuth 登录" --command "<可复跑验证命令>"
```

---

## Step 5：验收失败处理

### 5.1 失败分类

| 失败类型 | 原因 | 处理方式 |
|----------|------|----------|
| DoD 缺失 | 功能未实现 | 回到执行阶段实现 |
| DoD 偏差 | 实现与规范不符 | 回到执行阶段修正 |
| 多余功能 | 实现了不需要的东西 | 回到执行阶段删除 |
| 代码质量 | 严重/重要问题 | 回到执行阶段修复 |
| 测试失败 | 自动化测试不通过 | 回到执行阶段修复 |

### 5.2 失败记录

验收失败时，必须填写 `failure_capture`：

```text
失败项: [哪条 DoD / 哪个质量检查]
预期: [应该是什么]
实际: [实际是什么]
根因: [为什么失败]
修复方案: [计划怎么修]
```

### 5.3 修复后重新验收

修复后必须**从 Step 1 重新开始**，不要跳步：
1. 运行全量测试
2. 规范符合性审查
3. 代码质量审查
4. DoD→证据映射

---

## Step 6：法律合规审查（可选，高风险项目必做）

> 合规审查组件已迁移至 `components/04-accept/compliance-audit/SKILL.md`

**触发条件**：
- 项目涉及AI生成内容、用户数据处理、支付交易、跨境服务
- 用户显式要求"审查合规"/"法律风险"/"合规检查"
- 验收门禁中发现法律合规缺口

**执行时机**：功能验收通过（Step 1~5）后、交付前执行。

**审查维度**：

| 维度 | 组件 | 适用场景 |
|------|------|----------|
| 隐私合规 | `compliance-audit/components/01-privacy/SKILL.md` | 所有收集用户数据的项目 |
| 内容合规 | `compliance-audit/components/02-content/SKILL.md` | AI生成内容、UGC平台 |
| 交易合规 | `compliance-audit/components/03-transaction/SKILL.md` | 含付费、订阅、电商功能 |
| 安全合规 | `compliance-audit/components/04-security/SKILL.md` | 所有上线项目 |
| 知识产权 | `compliance-audit/components/05-intellectual-property/SKILL.md` | 含开源依赖、用户内容 |

**合规审查结论处理**：

| 结论 | 处理方式 |
|------|----------|
| 通过 | 无致命/高危风险，进入 Step 7 |
| 有条件通过 | 存在中低危风险，记录待办后进入 Step 7 |
| 不通过 | 存在致命/高危风险，回到执行阶段修复，修复后重新从 Step 1 开始 |

**合规审查结果写入**：`acceptance_runbook.md` 的「法律合规审查」章节。

---

## Step 7：验收通过确认 + 检查点创建

**所有完成定义有证据 + 无严重/重要问题 + 合规审查通过（如执行）→ 验收通过**

输出验收通过前，必须再执行一次输出充分性四问：用户是否能从报告中看到 DoD 完成数、代码质量结论、合规审查结论、证据路径、剩余限制和下一步。

**创建验收阶段检查点**（强制）：

```bash
python scripts/yunshu.py checkpoint create \
  --task-id <task_id> \
  --phase accept \
  --summary "<验收阶段完成摘要>" \
  --completed "<已验收DoD列表>" \
  --pending "<遗留问题>" \
  --artifact "acceptance_evidence.json, acceptance_runbook.md" \
  --next-action "进入05-deliver交付"
python scripts/yunshu.py validate checkpoint .yunshu/checkpoints/<checkpoint_id>/checkpoint.json
```

**验收通过确认交互**（Trae IDE）：
调用 `AskUserQuestion`：
- 问题："验收通过。DoD N/N 条通过，代码质量无问题，法律合规 [结论]。是否进入交付阶段？"
- 选项："确认，进入交付" / "需要修改"
- 用户选择"需要修改" → 回到执行阶段修复，修复后重新从 Step 1 开始验收

向用户报告：

```text
验收通过 ✅

DoD 完成情况：N/N 条通过
代码质量：无严重/重要问题
法律合规：[通过/有条件通过/未执行]
证据文档：acceptance_runbook.md + acceptance_evidence.json

准备进入交付阶段。
```

---

## 动态验收（可选增强）

如果项目需要自动生成验收计划，可参照以下流程：

1. 读取项目需求文档，提取功能需求
2. 扫描代码仓库，识别已实现功能
3. 检索领域测试知识（按需联网搜索）
4. 生成验收计划（runbook + 测试用例）
5. 执行验收并收集证据

**注意**：动态验收是辅助手段，不能替代 Step 2-4 的手动审查流程。

---

## 路由

- 全部 DoD 有证据 + 代码质量通过 → 进入 `components/05-deliver/SKILL.md`
- 存在 DoD 缺证据或质量问题 → 回到 `components/03-execute/SKILL.md` 修复
