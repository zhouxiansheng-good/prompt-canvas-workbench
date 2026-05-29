# Frontend-Design 融合模块

> 云舒系统 × Anthropic Frontend-Design Skill 融合
> 位置：`components/03-execute/frontend-design/`

---

## 模块职责

为云舒系统 03-execute 模块提供前端设计能力增强：
- **设计思考流程** — 编码前确定美学方向
- **美学合规检查** — 代码自检增加设计质量维度
- **设计验证证据** — 设计决策可追溯、可验证

## 触发条件

当任务涉及以下内容时自动加载：
- Web 组件开发
- 页面开发（落地页、仪表盘等）
- UI/UX 设计
- 样式化/美化 Web UI

## 核心文件

| 文件 | 用途 |
|------|------|
| `design-thinking.md` | 设计思考流程（目的/调性/约束/差异化） |
| `aesthetic-checklist.md` | 美学合规检查清单（7项检查） |
| `banned-patterns.md` | 禁止模式清单（字体/色彩/布局） |
| `design-templates/*.md` | 风格模板（极简/极繁/复古未来/野兽派） |

## 使用方式

1. 03-execute 识别前端任务 → 自动加载本模块
2. 按 `design-thinking.md` 流程完成设计思考
3. 产出 `design-decision.md` 设计决策文档
4. 编码时遵循 `banned-patterns.md` 禁止清单
5. 代码自检时执行 `aesthetic-checklist.md` 检查

## 与云舒主流程的关系

```
03-execute SKILL.md
  ├── Step 2.0: 元认知门禁 → 增加设计方向审视
  ├── Step 2.1: 声明意图 → 增加设计方向声明
  ├── Step 2.2: TDD 循环 → 增加设计测试
  ├── Step 2.4: 代码自检 → 增加美学合规检查
  └── gates.md → 增加前端设计门禁
```

## 设计哲学

> "先聊清楚，再干活" — 编码前确定美学方向，避免生成"AI风格"的通用界面。

---

*融合模块 v1.0*
