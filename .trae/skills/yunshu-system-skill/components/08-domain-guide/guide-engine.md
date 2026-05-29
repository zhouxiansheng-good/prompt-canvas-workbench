# 引导引擎规范

> 定义 08-domain-guide 的核心算法：如何遍历决策树、如何逐层引导用户、如何生成上下文包。

## 算法流程

```
输入: 用户输入文本 + 领域决策树定义
输出: 领域上下文包 或 回退到苏格拉底提问

Step 1: 领域识别
  从用户输入中提取关键词
  匹配决策树的 keywords 字段
  如果匹配成功 → 继续 Step 2
  如果匹配失败 → 回退到 01-init 苏格拉底提问

Step 2: 决策树加载
  读取 components/08-domain-guide/examples/<domain>/decision-tree.json
  使用 decision-tree-schema.json 验证结构
  如果验证失败 → 记录错误，回退到苏格拉底提问

Step 3: 层级引导（循环）
  current_level = 1
  selections = {}
  decomposition_depth = 0
  max_depth = 决策树.decomposition_config.max_decomposition_depth || 10

  while true:
    # === 预定义层级引导 ===
    if current_level <= 决策树.levels.length:
      level_def = 决策树.levels[current_level - 1]

      Step 3.1: 级联过滤
        如果 level_def.parent_level 存在:
          parent_selection = selections[level_def.parent_level]
          choices = 过滤出 parent_filter 包含 parent_selection.id 的选项
        否则:
          choices = level_def.choices

      Step 3.2: 选项展示
        使用当前平台 adapter 指定的原生交互工具展示选项（2-4个）
        每个选项包含: name + description

      Step 3.3: 用户选择
        等待用户选择
        如果用户输入"跳过" → 使用第一个选项作为默认值
        记录选择: selections[current_level] = 用户选择的选项

      Step 3.4: 终止检查
      如果选择的选项 next_level 为 null:
        进入 Step 3.5 动态分解评估
      否则:
        current_level = 选择的选项 next_level
        continue

    # === 动态分解模式 ===
    Step 3.5: 动态分解（当预定义层级结束后或 next_level 为 null 时）
      if not 决策树.decomposition_config.enable_dynamic_decomposition:
        跳出循环

      decomposition_depth++

      if decomposition_depth > max_depth:
        记录警告: "达到最大分解深度，停止分解"
        跳出循环

      Step 3.5.1: 评估当前任务复杂度
        current_task = 构建当前任务描述（基于所有选择）
        使用LLM评估: "这个任务是否足够简单？"
        评估标准: 决策树.decomposition_config.atomic_task_criteria
        评估提示词模板: 见 atomic-task-criteria.md "动态分解时的评估方法"

      Step 3.5.2: 判断是否需要继续分解
        if 任务足够简单:
          跳出循环
        else:
          Step 3.5.3: 动态分解任务
            使用LLM生成2-4个子任务选项
            提示词模板: 决策树.decomposition_config.decomposition_prompt_template
            每个子任务包含: name + description + 预期输出

          Step 3.5.4: 展示子任务选项
            使用当前平台 adapter 指定的原生交互工具展示子任务选项
            标记为 "[动态分解 L{decomposition_depth}]"

          Step 3.5.5: 用户选择子任务
            等待用户选择
            记录选择: selections[current_level] = 用户选择的子任务
            current_level++
            continue

Step 4: 上下文包生成
  context_package = {
    domain_id: 决策树.domain_id,
    version: 决策树.version,
    selections: 将 selections 转换为 {L1: {...}, L2: {...}} 格式,
    context: 合并所有选中选项的 context_inject,
    software_skills: 合并所有选中选项的 software_skills（去重）,
    constraints: 合并所有选中选项的 constraints,
    next_action: "进入 07-subagent 分派实现任务"
  }

  验证 context_package 包含 context_package_template.required_fields 中的所有字段
  如果验证失败 → 补充默认值或报错

Step 5: 输出
  返回 context_package
```

## 关键规则

### 规则 1：选项数量限制
- 每层最多展示 4 个选项（遵循当前平台 adapter 的交互限制）
- 如果某层选项 > 4 个，使用"分组展示"策略：
  - 展示前 3 个选项 + 第 4 个选项为"更多..."（包含剩余选项）
  - 用户选择"更多..."后，展示剩余选项（同样最多 4 个）
  - 如果剩余选项仍 > 4 个，递归使用相同策略

### 规则 2：级联过滤
- 子层级的选项必须定义 parent_filter
- 如果过滤后选项 < 2 个，需要检查决策树定义是否有误

### 规则 3：默认值处理
- 用户输入"跳过"时，使用第一个选项作为默认值
- 默认值必须在选项列表中明确标注（如"[默认]"）

### 规则 4：歧义检测
- 如果用户输入无法匹配任何选项，暂停并请求澄清
- 如果多个选项都匹配，展示所有匹配项让用户选择

### 规则 5：上下文注入合并
- 同名的 context_inject 键，后层级的值覆盖前层级
- 数组类型的值（如 applicable_codes）合并去重

## 错误处理

| 错误场景 | 处理方式 | 回退行为 |
|----------|----------|----------|
| 决策树文件不存在 | 记录错误日志 | 回退到苏格拉底提问 |
| Schema 验证失败 | 记录具体错误 | 回退到苏格拉底提问 |
| 级联过滤后选项 < 2 | 记录错误日志 | 展示所有选项（忽略过滤） |
| 用户选择无效 | 提示重新选择 | 重复当前层级 |
| 上下文包缺少必填字段 | 补充默认值 | 继续执行 |

## 与 01-init 的集成点

在 01-init 的 Step 4（逐个提问澄清）中，增加分支：

```
Step 4: 逐个提问澄清
  │
  ├─ 检测到领域关键词？
  │   ├─ 是 → 进入 08-domain-guide
  │   │       └─ 执行引导引擎算法
  │   │       └─ 生成领域上下文包
  │   │       └─ 将上下文包附加到任务卡
  │   │
  │   └─ 否 → 继续原有苏格拉底提问
  │
  └─ 用户显式要求"进入领域引导模式"？
      └─ 是 → 进入 08-domain-guide（跳过关键词检测）
```

## 与 07-subagent 的集成点

在 07-subagent 的 Step 2（分派实现者）中，增加上下文包注入：

```
分派 yunshu-implementer 智能体
  query: |
    任务描述：[任务文本]
    领域上下文：[来自 08-domain-guide 的 context_package]
    软件技能：[context_package.software_skills 列表]
    ...
```

**与 07-subagent DECOMPOSITION_REQUEST 的协同**：

```
08-domain-guide 动态分解 与 07-subagent 子智能体分解 的协同规则：

1. 优先级：
   - 如果任务经过 08-domain-guide 领域引导 → 优先使用 08-domain-guide 的动态分解
   - 如果任务未经领域引导 → 由 07-subagent 的子智能体自行判断是否需要分解

2. 避免重复分解：
   - 08-domain-guide 分解后的子任务，子智能体不应再请求分解（除非遇到未预见的复杂度）
   - 子智能体请求分解前，先检查是否已经过 08-domain-guide 分解

3. 分解深度控制：
   - 08-domain-guide 动态分解深度 + 子智能体分解深度 ≤ max_decomposition_depth
   - 防止两层分解叠加导致过度分解

4. 上下文传递：
   - 08-domain-guide 分解产生的上下文包，传递给子智能体作为基础上下文
   - 子智能体分解产生的新子任务，继承原任务的领域上下文
```
