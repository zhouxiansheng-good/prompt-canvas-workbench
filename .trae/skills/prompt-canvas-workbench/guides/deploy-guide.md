# 部署指南

## Cloudflare Pages 部署

### 前置要求

1. Cloudflare 账号
2. Cloudflare API Token（需有 Pages 编辑权限）
3. 已安装 wrangler CLI（`npm install -g wrangler`）

### 获取 API Token

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 右上角头像 → My Profile → API Tokens
3. 点击 "Create Token"
4. 选择 "Custom token"
5. 权限设置：
   - Zone:Read（如使用自定义域名）
   - Account:Cloudflare Pages:Edit
6. 保存 Token

### 部署命令

```powershell
# 设置环境变量（PowerShell）
$env:CLOUDFLARE_API_TOKEN="your_token_here"

# 部署
cd {project_root}
npx wrangler pages deploy dist --project-name={your_project_name} --branch=main
```

### 首次部署

如果是首次部署到该项目：
1. 在 Cloudflare Dashboard 中先创建一个 Pages 项目（同名）
2. 或者使用 `wrangler pages project create {name}`

### 后续更新

每次代码更新后：
```bash
npm run build
npx wrangler pages deploy dist --project-name={name} --branch=main
```

### 自定义域名（可选）

1. 在 Cloudflare Dashboard → Pages → 你的项目
2. 点击 "Custom domains"
3. 添加你的域名并验证
