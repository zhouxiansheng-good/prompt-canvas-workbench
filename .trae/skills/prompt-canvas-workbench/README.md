# Prompt Canvas Workbench

一个可复用的 AI 技能（Skill），一键构建复古拟物化风格的 AI 提示词展示网站。

---

## 这是什么

Prompt Canvas Workbench 是一套面向 Trae / AI IDE 的自动化工作流技能。用户只需说出"帮我做一个提示词网站"，即可自动完成从项目初始化、页面构建到部署上线的全过程。

它不只是代码模板，而是一套**完整的工程化工作流**：
- **项目初始化**：自动创建 Next.js 项目骨架，安装依赖，配置 Tailwind CSS
- **页面构建**：生成所有核心文件——数据模型、页面、组件、样式、主题系统
- **部署上线**：构建静态导出并一键部署到 Cloudflare Pages

---

## 核心特性

| 特性 | 说明 |
|------|------|
| **复古拟物化美学** | 四色主题切换（经典复古 / 包豪斯墨绿 / 北欧极夜 / 多巴胺柔和），硬阴影 + 网格背景 |
| **桌面端交互** | 可拖拽卡片窗口、双层手风琴收纳架、Z-Index 焦点管理 |
| **移动端适配** | 抽屉式侧边栏、流式卡片布局、触控友好 |
| **响应式断点** | `lg:` (1024px) 精确区分桌面与移动端体验 |
| **静态导出** | `output: 'export'` 零服务端依赖，适合任意静态托管 |
| **一键部署** | 内置 wrangler CLI 配置，自动推送到 Cloudflare Pages |

---

## 技术栈

- **Next.js 15** + **React 19** + **TypeScript**
- **Tailwind CSS v3**
- **react-draggable**（桌面端卡片拖拽）
- **Cloudflare Pages**（部署目标）

---

## 三组件架构

```
用户触发
  ↓
组件一：项目初始化
  - 检查/创建 Next.js 项目
  - 安装依赖（react-draggable 等）
  - 配置 Tailwind、PostCSS、Next.js
  ↓
组件二：页面构建
  - 生成数据模型、全局样式、核心页面
  - 生成组件（Header / Footer / PromptCard / SupportButton）
  - 四色主题 CSS 变量系统
  ↓
组件三：部署上线
  - 配置 wrangler.toml
  - 构建静态导出
  - 部署到 Cloudflare Pages，返回访问地址
```

---

## 触发词

对 AI 说出以下任意一句话即可激活：

- "帮我做一个提示词网站"
- "建一个 AI 提示词画板"
- "prompt canvas"
- "提示词工作台"
- "做一个 AI prompt 展示站"

---

## 目录结构

```
.trae/skills/prompt-canvas-workbench/
├── SKILL.md                          # 技能根入口
├── README.md                         # 本文件
├── components/
│   ├── 01-project-init/SKILL.md      # 组件一：项目初始化
│   ├── 02-page-build/SKILL.md        # 组件二：页面构建
│   │   └── templates/                # 代码模板目录
│   └── 03-deploy/SKILL.md            # 组件三：部署上线
└── guides/
    ├── aesthetic-system.md           # 美术设计系统指南
    └── deploy-guide.md               # Cloudflare 部署指南
```

---

## 使用前提

- Trae 或支持 Skill 机制的 AI IDE
- Node.js 18+
- Cloudflare 账号（用于部署）

---

## License

MIT
