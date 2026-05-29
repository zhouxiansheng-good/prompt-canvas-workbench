# Yunshu Context: yunshu-context-ledger-flow-test

- task_id: yunshu-context-ledger
- phase: accept
- created_at: 2026-05-10T03:05:29Z
- updated_at: 2026-05-10T03:05:29Z

## Sources

- scripts/yunshu.py — sha256=c56eac08fa07fab4d52b67b8adb7088c61f62ebc1c44fc0f0d62b9120da0b2d8 exists=True
- tests/test_yunshu_cli.py — sha256=cd50f1884035f7b2022bcfd3738b935595f9d376b9a6c48724323874749cc3d2 exists=True
- tmp-yunshu-flow-e2e/.yunshu/context/demo-flow-deliver.json — sha256=b66862022ec4484e2c73687e5c8b61b289456f5743ab35aee6793eb2a187c4eb exists=True
- tmp-yunshu-flow-e2e/.yunshu/context/demo-flow-recover-second-run.json — sha256=8ce2d0f68311f96f399d834b3afd3ed6391378f61634ada80c73927b9862ff0a exists=True
- tmp-yunshu-flow-e2e/.yunshu/checkpoints/demo-flow-deliver-20260510-110349/phase_memory.json — sha256=aaaccc2ad25d56eb9b2e59c542d838f5c1be631c29f70e9ccba586a33b0dea43 exists=True
- tmp-yunshu-flow-e2e/.yunshu/checkpoints/demo-flow-recover-20260510-110414/phase_memory.json — sha256=945a433b5cbe11042f6945a955e305fd9dc2d95d029998761bd9bce01616cecc exists=True

## Findings

- 两遍实例流程验证通过：第一遍完成 init/plan/execute/accept/deliver 并生成账本、检查点、verify log、acceptance_evidence；第二遍从 deliver checkpoint 恢复，先 fresh，修改 src/calc.py 后准确检测 stale。
- 实例测试暴露 BOM JSON 问题，已将 read_json 改为 utf-8-sig 并新增回归测试。

## Actions

- 运行 unittest、version-check、audit links、validate context/checkpoint/evidence

## Decisions

- 上下文账本机制可行；恢复时可先信任 context status 决定补读范围

## Gaps

- 临时实例目录保留在 tmp-yunshu-flow-e2e 供人工查看；后续可把该流程固化为自动化 e2e 测试脚本。

## Next Read

- 后续优化先读取 yunshu-context-ledger-flow-test 与 tmp-yunshu-flow-e2e/.yunshu/checkpoints/demo-flow-recover-20260510-110414/phase_memory.json

## Freshness

- scripts/yunshu.py: fresh
- tests/test_yunshu_cli.py: fresh
- tmp-yunshu-flow-e2e/.yunshu/context/demo-flow-deliver.json: fresh
- tmp-yunshu-flow-e2e/.yunshu/context/demo-flow-recover-second-run.json: fresh
- tmp-yunshu-flow-e2e/.yunshu/checkpoints/demo-flow-deliver-20260510-110349/phase_memory.json: fresh
- tmp-yunshu-flow-e2e/.yunshu/checkpoints/demo-flow-recover-20260510-110414/phase_memory.json: fresh
