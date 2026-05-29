# BMad CLI Adapter：可选外部工具适配

## 定位

BMad CLI 是可选外部工具，不是云舒运行依赖。云舒 BMad 增强层以本地文件和映射门禁为主；只有用户明确要求安装或运行 BMad CLI 时，才进入本适配说明。

## 可用场景

- 用户已经安装 BMad Method，并提供 PRD / Architecture / Story / project-context 路径。
- 用户要求运行 `npx bmad-method` 生成或检查 BMad 产物。
- 用户要求使用 BMad flatten 准备代码库上下文。

## 前置门禁

运行外部 CLI 前必须：

1. 读取 `safeguards/dependency.md`，确认依赖来源和命令必要性。
2. 明确命令是否会修改项目文件。
3. 明确输出路径。
4. 记录命令和产物到 context ledger。

## 推荐边界

| 操作 | 云舒默认态度 |
|------|--------------|
| 读取已有 BMad 文档 | 允许，进入 `bmad map` |
| 校验已有 BMad 文档 | 允许，使用云舒映射校验 |
| 运行 BMad flatten | 按需，输出必须加入 context ledger |
| 安装 / 更新 BMad CLI | 高风险依赖操作，需用户确认 |
| 让 BMad CLI 直接改云舒文件 | 默认禁止 |

## 接入流程

```text
已有 BMad 产物
  -> python scripts/yunshu.py bmad map --kind <kind> --source <path>
  -> python scripts/yunshu.py bmad status <map_id>
  -> 回到云舒 02-plan / 03-execute / 07-subagent
```

## 反模式

- 把 `npx bmad-method install` 当作默认步骤。
- 没确认版本和来源就运行远程 CLI。
- 让 BMad CLI 输出直接覆盖云舒任务卡、计划或验收文件。
- 运行 flatten 后把超大 XML 直接塞进主上下文，不做账本压缩。
