---
name: 08-domain-guide
description: "领域细分引导元技能。通过结构化决策树逐层收窄领域选择集，生成领域上下文包并辅助原子任务判定。"
metadata:
  phase: "2"
  type: "optional-component"
---

# 08-domain-guide — 领域细分引导元技能

> 把云舒系统的**渐进式披露**理念，从"文档按需加载"扩展到"领域知识按需引导"。
> 通过结构化决策树，逐步引导用户提供选项答案，缩小选择集，提高领域任务成功率。

<!-- L1:START -->
触发条件：01-init 检测到用户输入包含**领域关键词**时自动触发。或用户显式要求"进入领域引导模式"时激活。
<!-- L1:END -->

## 适用 / 不适用

- **适用**：垂直领域任务（道路设计、建筑结构、桥梁设计等）、需要精确领域参数选择的场景、大模型容易选错参数的领域
- **不适用**：通用编程任务、无明确领域特征的需求、单步问答/概念解释

## 全局交互规则

遵循云舒系统全局交互规则（见 SKILL.md 主入口）。

**额外规则**：
- 每层引导必须提供 2-4 个明确选项（使用当前平台 adapter 指定的原生交互工具）
- 用户可随时输入"跳过"使用默认值
- 检测到歧义时暂停并请求澄清

---

<!-- L2:START -->
## 流程路由

| 阶段 | 产物 | 说明 |
|------|------|------|
| 识别 | 领域匹配结果 | 从用户输入提取领域关键词，匹配决策树 |
| 加载 | 决策树对象 | 加载对应领域的 decision-tree.json |
| 引导 | 用户选择序列 | 逐层提问，收集用户选择 |
| 打包 | 领域上下文包 | 生成结构化的上下文包，供子智能体使用 |

> **回退机制**：决策树文件缺失或匹配失败时，自动回退到 01-init 的原有苏格拉底提问流程。

## 输入输出

**输入**：用户模糊需求（如"帮我设计一条市政主干路"）+ 可选的领域决策树定义

**输出**：领域上下文包（JSON 格式）

```json
{
  "domain_id": "road-design",
  "version": "1.0.0",
  "selections": {
    "L1": { "id": "municipal", "name": "市政道路" },
    "L2": { "id": "arterial", "name": "主干路" },
    "L3": { "id": "pavement", "name": "路面工程" },
    "L4": { "id": "structure-layer", "name": "结构层设计" }
  },
  "context": {
    "applicable_codes": ["CJJ 37-2012", "CJJ 169-2012"],
    "design_speed": [40, 50, 60],
    "lane_count": [4, 6]
  },
  "software_skills": ["hongye-municipal-road", "weidi-road"],
  "constraints": ["适用《城市道路工程设计规范》CJJ 37-2012", "设计速度 40-60 km/h"],
  "next_action": "进入 07-subagent 分派实现任务"
}
```

---

## 核心能力

| 能力 | 关键方法 | 毛选思想 |
|------|----------|----------|
| 领域识别 | 关键词匹配 + 决策树索引 | 调查研究：先识别领域再深入 |
| 层级引导 | 决策树遍历 + 选项收窄 | 主要矛盾：逐层聚焦核心问题 |
| 上下文打包 | 选择序列 + 约束注入 + 规范映射 | 具体问题具体分析：每个选择影响后续上下文 |

## 反模式

- 🚫 跳过领域识别直接提问（没有调查就没有发言权）
- 🚫 提供过多选项导致选择困难（集中优势兵力，一次只聚焦一个层级）
- 🚫 忽略用户跳过某层级的意图（具体问题具体分析）
- 🚫 生成的上下文包缺少约束条件（实践是检验真理的唯一标准）

---

## 领域引导留底（强制）

> 领域选择序列是项目关键决策，必须留底。

**引导完成后必须执行**：

```bash
python scripts/yunshu.py context record \
  --task-id <task_id> \
  --phase domain-guide \
  --source "decision-tree.json, 用户选择序列" \
  --finding "<领域识别结果：domain_id, 选择序列, 适用规范>" \
  --action "<完成的引导步骤>" \
  --gap "<未覆盖的领域参数>" \
  --next-read "<实现阶段需参考的规范文档>"
python scripts/yunshu.py validate context .yunshu/context/<context_id>.json
```

**硬规则**：没有记录领域选择序列 → 不许进入 07-subagent 或 09-software-bridge

## 与 09-software-bridge 的集成点

当 08-domain-guide 生成上下文包且包含 software_skills 时：

```
08-domain-guide 输出上下文包
  │
  ├─ software_skills 存在？
  │   ├─ 是 → 触发 09-software-bridge
  │   │       └─ 软件技能匹配 → 命令构建 → 沙箱执行
  │   │
  │   └─ 否 → 继续原有流程（07-subagent 分派）
  │
  └─ 用户显式要求操作软件？
      └─ 是 → 触发 09-software-bridge
```

**集成规则**：
- 09-software-bridge 优先使用 08-domain-guide 提供的 software_skills 列表
- 如果 software_skills 中的软件未注册，回退到 07-subagent 分派
- 09-software-bridge 执行结果反馈给 08-domain-guide 更新上下文状态

## 子组件路由表

| 用户意图 | 子组件路径 | 子组件职责 |
|----------|------------|------------|
| "决策树" / "Schema定义" / "领域模型" | `decision-tree-schema.json` | 决策树JSON Schema定义、字段规范、验证规则 |
| "引导引擎" / "交互引导" / "选项收窄" | `guide-engine.md` | 逐层引导引擎规范、选项生成规则、回退机制 |
| "原子任务" / "任务拆分" / "分解标准" | `atomic-task-criteria.md` | 原子任务判定标准、复杂度评估、分解终止条件 |
| "示例" / "道路设计" / "参考案例" | `examples/road-design/decision-tree.json` | 道路设计领域决策树示例 |
| "软件桥接" / "操作软件" / "工具调用" | 见 SKILL.md "与 09-software-bridge 的集成点" | 与09-software-bridge的集成规范、软件技能匹配规则 |

<!-- L2:END -->
