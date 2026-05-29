# Yunshu Context: yunshu-context-ledger-deliver

- task_id: yunshu-context-ledger
- phase: deliver
- created_at: 2026-05-10T02:55:45Z
- updated_at: 2026-05-10T02:55:45Z

## Sources

- SKILL.md — sha256=511cc8518a94d473b89c2801100ec80bf15a3306df5bb2d984ba73c4b83c73c6 exists=True
- components/01-init/SKILL.md — sha256=1c76ddec5a9a30db69208df3b32b56c27c1ac2f929209cc97acaded260d23040 exists=True
- components/02-plan/SKILL.md — sha256=61b30170e0503ee14c2553053eed009f6d8cb895d2cf15af754c5e86143999ab exists=True
- components/05-deliver/SKILL.md — sha256=ec54a8a2f95312c81c7553351432cf871ef864614c73b1ecb6883975894cd5dc exists=True
- components/06-recover/SKILL.md — sha256=a79037ec53c0cbf9c57a5475c26fce7fba2de288c79ddb593e41c4be4448759f exists=True
- safeguards/context.md — sha256=d559fb458e792dce1d22c4b571f43761cc69648a71473a05e514b785f26e3564 exists=True
- scripts/yunshu.py — sha256=dc0a827aab9abd20fb769af8957050ea0f6f0149f857c99bc795abd53691a487 exists=True
- tests/test_yunshu_cli.py — sha256=072f40b897645804184baddf5e92ed7538649abfe10a3cf46ee61537ce5abddf exists=True
- schemas/context_ledger.schema.json — sha256=1b72d2aa128b64517ab25a763badb0e4ce1ab97540ff83e81140e3bec8889481 exists=True
- templates/context_ledger.md — sha256=0b01f666a984ae59a1450302a7182ddc9405e55c486da538f6490ce646f5b49a exists=True
- https://docs.cline.bot/features/memory-bank — sha256=n/a exists=external/unknown
- https://aider.chat/docs/repomap.html — sha256=n/a exists=external/unknown
- https://docs.openhands.dev/overview/skills/repo — sha256=n/a exists=external/unknown
- https://code.claude.com/docs/en/memory — sha256=n/a exists=external/unknown
- https://developers.openai.com/codex/guides/agents-md — sha256=n/a exists=external/unknown

## Findings

- 同类项目共同模式：持久项目指令、结构化记忆、仓库摘要索引、按需加载和检查点分工；云舒缺少记录已读来源与结论新鲜度的账本。
- 新增 .yunshu/context/ 账本，记录 sources/findings/actions/decisions/gaps/next_read，并用 sha256 判断本地来源 fresh/stale/missing。

## Actions

- 实现 context record/list/show/status 与 validate context，并让 checkpoint create 自动关联同 task_id 最新 context ledger。
- 更新 01-init、02-plan、05-deliver、06-recover、context safeguard、README 和模板，使恢复时先查账本再补读。

## Decisions

- 保留 checkpoint 作为阶段恢复事实源，新增 context ledger 作为调查复现事实源，避免把两类状态混在一个文件里。

## Gaps

- 后续可增加自动扫描 git diff 生成 source 列表，以及更细的目录指纹策略。

## Next Read

- 下次优化先运行 context show/status yunshu-context-ledger-deliver，再只补读 stale/missing 文件和新增需求涉及文件。

## Freshness

- SKILL.md: fresh
- components/01-init/SKILL.md: fresh
- components/02-plan/SKILL.md: fresh
- components/05-deliver/SKILL.md: fresh
- components/06-recover/SKILL.md: fresh
- safeguards/context.md: fresh
- scripts/yunshu.py: fresh
- tests/test_yunshu_cli.py: fresh
- schemas/context_ledger.schema.json: fresh
- templates/context_ledger.md: fresh
- https://docs.cline.bot/features/memory-bank: external or non-local source, freshness not checked
- https://aider.chat/docs/repomap.html: external or non-local source, freshness not checked
- https://docs.openhands.dev/overview/skills/repo: external or non-local source, freshness not checked
- https://code.claude.com/docs/en/memory: external or non-local source, freshness not checked
- https://developers.openai.com/codex/guides/agents-md: external or non-local source, freshness not checked
