---
name: prompt-canvas-init
description: >
  项目初始化组件。创建Next.js项目骨架、安装依赖、配置构建工具。
  Trigger: 用户说"初始化项目"/"创建项目"/"开始构建"时激活。
---

# 项目初始化组件

**Trigger**: "初始化项目" / "创建项目" / "开始构建" / "setup"

---

## 前置条件

- 无。本组件可独立运行，是整套技能的第一入口。
- 需要用户提供：项目根目录路径（如 `e:\project\my-prompt-site`）

---

## 输出产物

```
{project_root}/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx          (占位，由组件二填充)
│   │   ├── globals.css       (占位，由组件二填充)
│   │   └── ...
│   ├── components/           (目录，由组件二填充)
│   └── lib/                  (目录，由组件二填充)
├── public/
├── next.config.ts            (静态导出配置)
├── tailwind.config.ts        (主题变量映射)
├── postcss.config.mjs        (PostCSS配置)
├── wrangler.toml             (Cloudflare部署配置)
└── package.json              (依赖清单)
```

---

## 执行流程

### Step 1：收集项目信息

- 项目根目录路径
- 网站名称（默认：AI提示词画板）
- 是否已有Next.js项目（是 → 复用，否 → 创建）

### Step 2：创建/检查项目骨架

**如果项目不存在**:
```bash
cd {parent_dir}
npx create-next-app@latest {project_name} --typescript --tailwind --eslint --app --src-dir --no-turbopack
```

**如果项目已存在**:
- 检查 `package.json` 是否存在
- 检查 Next.js 版本是否兼容（>=15）
- 如版本不兼容，提示用户

### Step 3：安装额外依赖

```bash
cd {project_root}
npm install react-draggable
npm install -D @types/react-draggable
```

### Step 4：配置文件生成

**next.config.ts**（静态导出）:
```typescript
import type { NextConfig } from "next";
const nextConfig: NextConfig = {
  output: 'export',
  distDir: 'dist',
  images: { unoptimized: true },
};
export default nextConfig;
```

**tailwind.config.ts**（主题变量映射）:
```typescript
import type { Config } from "tailwindcss";
const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "theme-canvas": "var(--theme-canvas)",
        "theme-paper": "var(--theme-paper)",
        "theme-card": "var(--theme-card)",
        "theme-text": "var(--theme-text)",
        "theme-muted": "var(--theme-muted)",
        "theme-border": "var(--theme-border)",
        "theme-grid": "var(--theme-grid)",
      },
      boxShadow: {
        'retro-sm': '2px 2px 0px 0px var(--theme-border)',
        'retro-md': '5px 5px 0px 0px var(--theme-border)',
        'retro-lg': '10px 10px 0px 0px var(--theme-border)',
      },
      fontFamily: {
        serif: ['"Noto Serif SC"', '"Songti SC"', "serif"],
        sans: ['"Inter"', '"PingFang SC"', "sans-serif"],
        mono: ['"Fira Code"', "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
```

**postcss.config.mjs**:
```javascript
/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
export default config;
```

**wrangler.toml**:
```toml
name = "prompt-canvas"
compatibility_date = "2026-05-01"

[site]
bucket = "./dist"
```

### Step 5：创建目录结构

```bash
mkdir -p src/components src/lib public
```

### Step 6：输出初始化报告

报告创建的文件清单和下一步建议（进入组件二）。

---

## 调用地址

- 本组件：`components/01-project-init/SKILL.md`
- 模板目录：`components/01-project-init/templates/`

---

## 关联组件

- 组件二（页面构建）：读取本组件创建的项目骨架，填充所有代码文件
