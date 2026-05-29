# 云舒系统交互定义修复报告

**修复时间**: 2026-05-29
**修复范围**: 02-plan / 04-accept / 05-deliver / 06-recover / 09-software-bridge
**修复目标**: 补充 AskUserQuestion 交互定义，确保各阶段关键确认点弹出选项框

---

## 修复文件清单

| 文件 | 修改位置 | 修改内容 |
|------|----------|----------|
| [components/02-plan/SKILL.md](file:///e:/traework/000%20自动化工作流研究/.trae/skills/yunshu-system-skill/components/02-plan/SKILL.md#L294-L304) | 2.4 风险评估后 | 补充高风险操作确认交互定义 |
| [components/04-accept/SKILL.md](file:///e:/traework/000%20自动化工作流研究/.trae/skills/yunshu-system-skill/components/04-accept/SKILL.md#L366-L395) | Step 7 验收通过确认前 | 补充验收确认交互定义 |
| [components/05-deliver/SKILL.md](file:///e:/traework/000%20自动化工作流研究/.trae/skills/yunshu-system-skill/components/05-deliver/SKILL.md#L228-L240) | Step 3 交付方式选择 | 规范化交互定义，补充选项描述和二次确认逻辑 |
| [components/06-recover/SKILL.md](file:///e:/traework/000%20自动化工作流研究/.trae/skills/yunshu-system-skill/components/06-recover/SKILL.md#L278-L290) | Step 4 确认恢复点 | 将文字模板替换为 AskUserQuestion 调用定义 |
| [components/09-software-bridge/SKILL.md](file:///e:/traework/000%20自动化工作流研究/.trae/skills/yunshu-system-skill/components/09-software-bridge/SKILL.md#L26-L36) | 全局交互规则后 | 补充命令执行前确认交互定义 |

---

## 修复详情

### 02-plan：高风险操作确认
```markdown
**用户确认交互**（Trae IDE）：
遇到上述高风险操作时，调用 `AskUserQuestion`：
- 问题："以下操作存在 [风险描述]，是否继续？"
- 选项："确认执行" / "取消操作" / "查看回滚方案"
- 用户选择"查看回滚方案" → 展示回滚策略后继续询问
```

### 04-accept：验收通过确认
```markdown
**验收通过确认交互**（Trae IDE）：
调用 `AskUserQuestion`：
- 问题："验收通过。DoD N/N 条通过，代码质量无问题，法律合规 [结论]。是否进入交付阶段？"
- 选项："确认，进入交付" / "需要修改"
- 用户选择"需要修改" → 回到执行阶段修复，修复后重新从 Step 1 开始验收
```

### 05-deliver：交付方式选择
```markdown
**交付方式选择交互**（Trae IDE）：
调用 `AskUserQuestion`：
- 问题："实现已完成。你想怎么处理？"
- 选项：
  - "本地合并到主分支" — 直接合并并删除特性分支
  - "推送并创建 Pull Request" — 推送到远程并创建 PR 请求审查
  - "保留当前分支（稍后自己处理）" — 不清理工作区，保留当前状态
  - "放弃这次工作" — 永久删除分支和提交（需二次确认）
- 用户选择"放弃这次工作" → 二次确认："输入 'discard' 确认删除"
```

### 06-recover：恢复确认
```markdown
**恢复确认交互**（Trae IDE）：
调用 `AskUserQuestion`：
- 问题："从交接文档恢复：\n目标: [一句话目标]\n当前状态: [一句话状态]\n已完成: N 项\n未完成: M 项\n下一步: [未完成的第一项]\n\n确认从这里继续？"
- 选项："确认继续" / "需要调整"
- 用户选择"确认继续" → 继续
- 用户选择"需要调整" → 更新交接文档后继续
```

### 09-software-bridge：命令执行确认
```markdown
**命令确认交互**（Trae IDE）：
执行任何软件操作命令前，调用 `AskUserQuestion`：
- 问题："即将执行：[命令描述]。是否确认？"
- 选项："确认执行" / "取消" / "查看回滚方案"
- 用户选择"查看回滚方案" → 展示回滚方式后继续询问
```

---

## 任务卡留底机制验证

**验证结果**: 留底机制完整 ✅

| 留底层级 | 产物 | 路径 | 状态 |
|----------|------|------|------|
| 上下文账本 | JSON + Markdown | `.yunshu/context/yunshu-interaction-test-2026-init-20260529-092955.json` | 存在 |
| 检查点 | checkpoint.json + phase_memory.json | `.yunshu/checkpoints/yunshu-interaction-test-2026-init-20260529-093655/` | 存在 |
| 关联关系 | checkpoint → context_ledger | checkpoint.json 中 `context_ledger` 字段指向上下文账本 | 正确 |
| 预加载测试 | context preload | 成功加载并判定为 fresh | 通过 |

**结论**: 任务卡通过 `context record` 写入上下文账本，通过 `checkpoint create` 创建检查点，两者通过 `context_ledger` 字段关联。上下文压缩后可通过 `checkpoint resume` 或 `context preload` 恢复。

---

## 修复后交互覆盖

| 阶段 | 交互点 | 状态 |
|------|--------|------|
| 01-init | 10 个交互点（复述/追问/场景/思路/领域/提问/追问/方案/分段/审批） | ✅ 已定义 + 已测试 |
| 02-plan | 高风险操作确认 | ✅ 已修复 |
| 03-execute | 无交互需求 | ⚠️ 纯执行阶段 |
| 04-accept | 验收通过确认 | ✅ 已修复 |
| 05-deliver | 交付方式选择 | ✅ 已修复 |
| 06-recover | 恢复确认 | ✅ 已修复 |
| 07-subagent | 无交互需求（控制器驱动） | ⚠️ 控制器自主决策 |
| 08-domain-guide | 决策树引导（规则存在） | ⚠️ 需实际领域任务触发 |
| 09-software-bridge | 命令执行确认 | ✅ 已修复 |

---

## 结论

**5 个文件的交互定义已全部修复**，所有关键确认点现在都有明确的 `AskUserQuestion` 调用定义。

**任务卡留底机制验证通过**：澄清需求后生成的任务卡，通过 `context record` 写入上下文账本，通过 `checkpoint create` 创建检查点，上下文压缩后可通过 `checkpoint resume` 或 `context preload` 恢复。
