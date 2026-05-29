# context_ledger.md（模板）— 可复现上下文账本

> 目标：记录本轮任务“读过什么、得出什么、做了什么、还缺什么”，让下一轮先复用已有上下文，再只补读过期或缺失部分。
> 约束：只写可验证事实和压缩结论，不粘贴大段源码/日志。

## 1) 基本信息
- task_id：
- context_id：
- phase：init / plan / execute / subagent / accept / deliver / recover
- created_at：
- updated_at：

## 2) 已读取来源
| 来源 | 用途 | 新鲜度依据 |
|------|------|------------|
| path-or-url | 为什么读 | 文件 sha256 / mtime / 外部链接日期 |

## 3) 关键发现
- 

## 4) 已完成动作
- 

## 5) 关键决策
- 

## 6) 缺口与下一轮补读
- 缺口：
- 下一轮优先读取：

## 7) 机器化记录

推荐使用 CLI 生成结构化账本和 Markdown：

```bash
python scripts/yunshu.py context record \
  --task-id <task_id> \
  --phase <init|plan|execute|subagent|accept|deliver|recover> \
  --source <path-or-url> \
  --finding "<压缩结论>" \
  --action "<已完成动作>" \
  --gap "<仍缺什么>" \
  --next-read "<下次只需补读什么>"
```

恢复时先运行：

```bash
python scripts/yunshu.py context list --task-id <task_id>
python scripts/yunshu.py context show <context_id>
python scripts/yunshu.py context status <context_id>
```

若 `context status` 显示 `fresh`，优先使用账本结论；若显示 `stale` 或 `missing`，只重读对应来源。
