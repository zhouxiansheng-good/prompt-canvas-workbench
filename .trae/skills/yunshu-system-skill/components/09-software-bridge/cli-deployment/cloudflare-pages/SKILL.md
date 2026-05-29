---
name: cloudflare-pages-cli-deploy
description: "Cloudflare Pages CLI 部署组件。使用 wrangler CLI 将静态构建产物部署到 Cloudflare Pages，替代不稳定的浏览器自动化方案。"
metadata:
  parent: "09-software-bridge"
  type: "cli-deployment"
  replaces: "browser-automation/cloudflare/components/03-deploy"
---

# Cloudflare Pages — CLI 部署组件

> 使用 wrangler CLI 将 `dist`（或指定目录）部署到 Cloudflare Pages。优先于浏览器自动化方案。

---

## 职责

- 验证构建产物目录存在且包含 `index.html`
- 检查/补全部署所需配置（wrangler.toml、环境变量）
- 执行 wrangler pages deploy
- 返回部署 URL

---

## 核心原则

1. **CLI 优先**：永远优先使用 wrangler CLI，仅在 CLI 不可用时降级到浏览器自动化
2. **非交互**：所有操作通过环境变量传入，不依赖交互式登录
3. **幂等**：重复执行同一部署命令不会破坏已有项目

---

## 前置条件

| 条件 | 检查方式 | 缺失处理 |
|------|---------|---------|
| `CLOUDFLARE_API_TOKEN` | `$env:CLOUDFLARE_API_TOKEN` | 向用户索要，指导创建方式 |
| `CLOUDFLARE_ACCOUNT_ID` | `$env:CLOUDFLARE_ACCOUNT_ID` 或 wrangler.toml | 从 Dashboard URL 提取或向用户索要 |
| `dist` 目录存在 | `Test-Path dist/index.html` | 先执行 `npm run build` |
| wrangler CLI | `npx wrangler --version` | 自动通过 npx 调用 |

---

## 操作流程

### Step 1: 构建产物检查

```powershell
# 检查 dist 目录和 index.html
if (-not (Test-Path "dist/index.html")) {
    # 尝试构建
    npm run build
    if (-not (Test-Path "dist/index.html")) {
        return "BUILD_FAILED: 构建后仍未找到 dist/index.html"
    }
}
```

### Step 2: 获取 Account ID

```powershell
# 优先级：环境变量 > wrangler.toml > API查询 > 用户输入
$accountId = $env:CLOUDFLARE_ACCOUNT_ID

if (-not $accountId) {
    # 尝试从 wrangler.toml 读取（注意：Pages 项目不支持 account_id 字段）
    # 如果用户已提供，直接使用
    # 否则尝试通过 zones API 获取（需 Token 有 Zone:Read 权限）
}

if (-not $accountId) {
    # 从用户提供的 Dashboard URL 提取
    # dash.cloudflare.com/{account_id}/...
    # 或直接向用户索要
}
```

**Account ID 获取方式（教用户）：**
1. 打开 https://dash.cloudflare.com
2. 登录后看浏览器地址栏：`dash.cloudflare.com/{32位字符串}/...`
3. 复制这 32 位字符串

### Step 3: 验证 API Token 权限

```powershell
# 测试 Token 是否可用
$headers = @{ Authorization = "Bearer $env:CLOUDFLARE_API_TOKEN" }
try {
    $r = Invoke-RestMethod -Uri "https://api.cloudflare.com/client/v4/zones" -Headers $headers
    # 如果能调用 zones API，说明 Token 有效
} catch {
    # 403 表示权限不足，但可能仍有 Pages 部署权限
    # 继续尝试部署，让 wrangler 报错
}
```

### Step 4: 确定项目名

```powershell
# 从 wrangler.toml 读取 name 字段
# 或从用户输入获取
# 项目名必须与 Cloudflare Pages 上已创建的项目名一致
```

**常见错误**：`Project not found` — 项目名不匹配。需确认 Dashboard 中显示的项目名。

### Step 5: 执行部署

```powershell
$env:CLOUDFLARE_API_TOKEN = "<token>"
$env:CLOUDFLARE_ACCOUNT_ID = "<account_id>"
npx wrangler pages deploy <dist-dir> --project-name=<project-name> --branch=main
```

**Windows PowerShell 注意**：
- 环境变量设置语法：`$env:VAR = "value"`
- 不要使用 `export`（Linux/macOS 语法）

### Step 6: 提取部署 URL

wrangler 成功输出示例：
```
✨ Deployment complete! Take a peek over at https://{hash}.{project}.pages.dev
```

提取该 URL 返回给用户。

---

## 完整命令模板

```powershell
# PowerShell (Windows)
$env:CLOUDFLARE_API_TOKEN = "cfut_xxxxxxxx"
$env:CLOUDFLARE_ACCOUNT_ID = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
cd "<项目根目录>"
npx wrangler pages deploy dist --project-name=<项目名> --branch=main
```

```bash
# Bash (Linux/macOS)
export CLOUDFLARE_API_TOKEN="cfut_xxxxxxxx"
export CLOUDFLARE_ACCOUNT_ID="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
cd "<项目根目录>"
npx wrangler pages deploy dist --project-name=<项目名> --branch=main
```

---

## 错误处理

| 错误 | 原因 | 解决 |
|------|------|------|
| `Failed to retrieve account IDs` | Token 缺少 Account:Read 权限 | 设置 `CLOUDFLARE_ACCOUNT_ID` 环境变量 |
| `Project not found` | 项目名不匹配 | 确认 Dashboard 中的实际项目名 |
| `Configuration file does not support "account_id"` | wrangler.toml 写了 account_id | Pages 项目不支持，改用环境变量 |
| `Failed to write to log file` | wrangler 日志目录不存在 | 不影响部署，可忽略 |
| `ENOENT: no such file or directory` | dist 目录不存在 | 先执行 `npm run build` |

---

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `project_root` | string | 是 | 项目根目录绝对路径 |
| `project_name` | string | 是 | Cloudflare Pages 项目名 |
| `dist_dir` | string | 否 | 构建输出目录，默认 `dist` |
| `branch` | string | 否 | 部署分支，默认 `main` |
| `api_token` | string | 条件 | CLOUDFLARE_API_TOKEN，未设置环境变量时必填 |
| `account_id` | string | 条件 | CLOUDFLARE_ACCOUNT_ID，未设置环境变量时必填 |

---

## 输出

| 状态 | 含义 | 返回数据 |
|------|------|----------|
| `DEP_OK` | 部署成功 | `{ deploy_url, project_url }` |
| `DEP_001` | 构建产物不存在 | — |
| `DEP_002` | API Token 无效或权限不足 | — |
| `DEP_003` | 项目名不存在 | — |
| `DEP_004` | 部署失败 | `{ error_message }` |

---

## 与浏览器自动化方案的对比

| | CLI 方案（本 Skill） | 浏览器自动化（旧方案） |
|--|---------------------|----------------------|
| 稳定性 | ✅ 高，命令行直接调用 API | ❌ 低，受页面变动影响 |
| 速度 | ✅ 快，秒级部署 | ❌ 慢，需等待页面加载 |
| 环境要求 | 需 API Token | 需浏览器登录状态 |
| 可复现性 | ✅ 100% 可复现 | ❌ 受网络/页面状态影响 |
| 文件上传 | ✅ 支持大文件 | ⚠️ 受浏览器上传限制 |
| 适用场景 | 所有静态站点部署 | CLI 不可用时的降级方案 |

---

## 注意事项

- **wrangler.toml 限制**：Cloudflare Pages 项目不支持在 `wrangler.toml` 中写 `account_id`，必须通过环境变量传入
- **项目名大小写**：Cloudflare Pages 项目名区分大小写
- **重复部署**：同一分支短时间内多次部署会覆盖，旧部署链接仍可用（基于 hash）
- **静态导出**：Next.js 项目需配置 `output: 'export'` 才能生成静态文件
