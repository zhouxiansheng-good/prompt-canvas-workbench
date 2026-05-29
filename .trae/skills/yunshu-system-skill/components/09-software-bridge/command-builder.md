# 命令构建规范

> 定义如何将领域上下文包转换为可执行的软件命令。

## 构建流程

```
输入: 领域上下文包 + 软件注册表
输出: 可执行命令序列

Step 1: 软件匹配
  从 context_package.software_skills 获取软件ID列表
  按优先级排序（第一个为首选）
  加载对应软件的注册表定义

Step 2: 参数映射
  遍历 software_registry.context_mapping
  将领域上下文字段映射到软件参数
  应用转换规则（direct/enum_map/format/concatenate）

Step 3: 命令选择
  根据任务类型选择合适的命令模板
  例如：创建项目 → create_project，绘制线形 → draw_alignment

Step 4: 参数填充
  使用映射后的参数填充命令模板
  验证必填参数是否都有值
  应用默认值（可选参数）

Step 5: 命令验证
  检查命令语法是否正确
  检查参数值是否在有效范围内
  检查依赖的前置命令是否已执行

Step 6: 输出命令序列
  生成有序的命令列表
  每个命令包含：命令文本、预期输出、验证方法
```

## 参数映射规则

| 转换规则 | 说明 | 示例 |
|----------|------|------|
| **direct** | 直接传递 | context.road_type → command.road_type |
| **enum_map** | 枚举映射 | context.grade="arterial" → command.grade="sub-arterial" |
| **format** | 格式化 | context.design_speed=[40,50,60] → command.speed="40-60" |
| **concatenate** | 拼接 | context.lane_count=4 → command.lanes="4-lane" |
| **select** | 从数组选取 | context.design_speed=[40,50,60] → command.speed=50（取默认值或用户确认） |

## 命令序列示例

```
领域上下文:
  road_type: municipal
  grade: arterial
  design_speed: 60
  lane_count: 6

软件注册表: hongye-municipal-road

生成的命令序列:
  1. CreateProject --name AutoProject --type municipal --grade arterial
     验证: 项目文件存在
     
  2. SetDesignSpeed --speed 60
     验证: 设计速度参数已设置
     
  3. SetLaneCount --count 6
     验证: 车道数参数已设置
```

## 错误处理

| 错误场景 | 处理方式 |
|----------|----------|
| 必填参数缺失 | 报告错误，请求补充上下文 |
| 上下文包无对应字段 | 提示用户输入该参数值，或使用默认值 |
| 参数值无效 | 报告错误，提供有效值范围 |
| 命令模板不存在 | 回退到手动操作指导 |
| 前置命令未执行 | 自动插入前置命令 |
| select转换源非数组 | 报告错误，回退到direct转换 |
