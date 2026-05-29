---
name: prompt-canvas-workbench
description: >
  AI提示词画板工作台 - 一键构建复古拟物化AI提示词展示网站。
  用户说"帮我做一个提示词网站"/"建一个AI提示词画板"/"prompt canvas"/"提示词工作台"时激活。
  三组件联动：项目初始化 → 页面构建 → 部署上线。
---

# AI提示词画板工作台

**架构**: 三组件联动（初始化 → 页面构建 → 部署上线）

**美术风格**: 复古拟物化工作台，四色主题切换（经典复古/包豪斯墨绿/极夜低噪/柔和多巴胺）

---

## 组件总览

| 组件 | 名称 | 功能 | 前置条件 | 调用地址 |
|------|------|------|---------|---------|
| **组件一** | 项目初始化 | 创建Next.js项目骨架、安装依赖、配置Tailwind | 无（独立运行） | `components/01-project-init/SKILL.md` |
| **组件二** | 页面构建 | 生成所有核心文件（页面/组件/样式/数据） | 需先运行组件一 | `components/02-page-build/SKILL.md` |
| **组件三** | 部署上线 | 构建静态导出并部署到Cloudflare Pages | 需先运行组件一、二 | `components/03-deploy/SKILL.md` |

---

## 核心工作流

```
用户触发
  ↓
组件一：项目初始化
  - 检查/创建Next.js项目
  - 安装依赖（react-draggable等）
  - 配置Tailwind、PostCSS、Next.js
  - 创建目录结构
  ↓
组件二：页面构建
  - 生成数据模型（src/lib/prompts.ts）
  - 生成全局样式（src/app/globals.css）
  - 生成核心页面（src/app/page.tsx）
  - 生成组件（Header/Footer/PromptCard/SupportButton）
  - 生成Tailwind配置
  ↓
组件三：部署上线
  - 配置wrangler.toml
  - 构建静态导出
  - 部署到Cloudflare Pages
  - 返回访问地址
```

---

## 全局约束

1. **技术栈锁定**: Next.js 15 + React 19 + TypeScript + Tailwind CSS v3 + react-draggable
2. **美术模板锁定**: 四色CSS变量主题系统，复古拟物阴影，网格背景
3. **输出模式锁定**: `output: 'export'` 静态导出，`distDir: 'dist'`
4. **部署目标锁定**: Cloudflare Pages（wrangler CLI）
5. **响应式断点**: `lg:` (1024px) 区分桌面端与移动端
6. **技能目录只存模板**，项目数据放在用户指定的项目根目录

---

## 触发词

- "帮我做一个提示词网站"
- "建一个AI提示词画板"
- "prompt canvas"
- "提示词工作台"
- "做一个AI prompt展示站"

---

## 调用地址

- 本技能根入口：`SKILL.md`
- 组件一：`components/01-project-init/SKILL.md`
- 组件二：`components/02-page-build/SKILL.md`
- 组件三：`components/03-deploy/SKILL.md`
- 美术指南：`guides/aesthetic-system.md`
- 部署指南：`guides/deploy-guide.md`

---

## 目录结构原则

```
技能目录（只读模板）
  .trae/skills/prompt-canvas-workbench/
  ├── SKILL.md
  ├── components/
  │   ├── 01-project-init/
  │   ├── 02-page-build/
  │   └── 03-deploy/
  └── guides/

项目目录（读写数据）
  {project_root}/
  ├── src/
  │   ├── app/
  │   │   ├── page.tsx
  │   │   ├── layout.tsx
  │   │   ├── globals.css
  │   │   └── ...
  │   ├── components/
  │   │   ├── Header.tsx
  │   │   ├── Footer.tsx
  │   │   ├── PromptCard.tsx
  │   │   └── SupportButton.tsx
  │   └── lib/
  │       └── prompts.ts
  ├── public/
  │   └── 赞赏码.jpg
  ├── next.config.ts
  ├── tailwind.config.ts
  ├── postcss.config.mjs
  ├── wrangler.toml
  └── package.json
```
