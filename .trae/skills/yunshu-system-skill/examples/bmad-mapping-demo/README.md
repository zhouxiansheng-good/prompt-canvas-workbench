# BMad Mapping Demo

This demo shows the minimum end-to-end flow for the Yunshu BMad enhancement layer.

## Sources

- `PRD.md`
- `architecture.md`
- `story-cli-evidence-dashboard.md`
- `project-context.md`

## Commands

```bash
python scripts/yunshu.py bmad map --task-id bmad-mapping-demo --kind prd --source examples/bmad-mapping-demo/PRD.md --map-id demo-prd-map --gap "Default limit needs product decision"
python scripts/yunshu.py bmad map --task-id bmad-mapping-demo --kind architecture --source examples/bmad-mapping-demo/architecture.md --map-id demo-architecture-map
python scripts/yunshu.py bmad map --task-id bmad-mapping-demo --kind story --source examples/bmad-mapping-demo/story-cli-evidence-dashboard.md --source examples/bmad-mapping-demo/project-context.md --map-id demo-story-map
python scripts/yunshu.py bmad map --task-id bmad-mapping-demo --kind project-context --source examples/bmad-mapping-demo/project-context.md --map-id demo-project-context-map
```

## Expected Outputs

- `.yunshu/bmad/demo-prd-map.json`
- `.yunshu/bmad/demo-architecture-map.json`
- `.yunshu/bmad/demo-story-map.json`
- `.yunshu/bmad/demo-project-context-map.json`
- matching context records in `.yunshu/context/`

## Validation

```bash
python scripts/yunshu.py bmad validate .yunshu/bmad/demo-prd-map.json
python scripts/yunshu.py bmad status demo-prd-map
```
