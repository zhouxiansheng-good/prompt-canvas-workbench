---
name: prompt-canvas-deploy
description: >
  部署上线组件。构建静态导出并部署到Cloudflare Pages。
  Trigger: 组件二完成后自动进入，或用户说"部署"/"上线"/"发布"时激活。
---

# 部署上线组件

**Trigger**: "部署" / "上线" / "发布" / "deploy"

**前置条件**: 组件一、二已完成（代码已生成）

---

## 执行流程

### Step 1：检查构建环境

- 确认 `next.config.ts` 已配置 `output: 'export'` 和 `distDir: 'dist'`
- 确认 `wrangler.toml` 存在
- 确认 `package.json` 有 `build` 脚本

### Step 2：构建项目

```bash
cd {project_root}
npm run build
```

**预期输出**:
- `dist/` 目录生成
- 包含 `index.html` 和所有静态资源
- 无构建错误

### Step 3：部署到Cloudflare Pages

**方式A：wrangler CLI（推荐）**

```bash
$env:CLOUDFLARE_API_TOKEN="your_token_here"
npx wrangler pages deploy dist --project-name={project_name} --branch=main
```

**方式B：手动上传**
- 登录 Cloudflare Dashboard
- 进入 Pages → 创建项目
- 上传 `dist/` 文件夹

### Step 4：验证部署

- 访问返回的URL
- 检查页面是否正常加载
- 检查主题切换是否正常
- 检查卡片拖拽是否正常

### Step 5：输出部署报告

报告内容：
- 部署URL
- 项目配置摘要
- 已知限制（如需配置自定义域名等）

---

## 调用地址

- 本组件：`components/03-deploy/SKILL.md`

---

## 关联组件

- 组件一（初始化）：提供项目骨架和wrangler配置
- 组件二（页面构建）：提供可构建的代码
