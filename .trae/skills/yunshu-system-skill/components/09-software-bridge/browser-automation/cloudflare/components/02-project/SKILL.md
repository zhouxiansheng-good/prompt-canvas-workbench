---
name: cloudflare-project
description: "Cloudflare Pages 项目组件。导航并验证目标项目页面，提取项目 URL 和部署入口。"
metadata:
  parent: "cloudflare-pages-deploy"
  type: "browser-automation-step"
---

# Cloudflare Pages — 项目组件

> 导航到指定的 Cloudflare Pages 项目页面，验证项目存在并获取项目信息。

---

## 职责

- 根据环境变量或用户输入进入指定项目
- 验证项目页面可访问且存在
- 提取项目 URL 模式和部署历史入口

---

## 操作流程

### 1. 构建项目 URL

根据环境变量构建目标 URL：

```
基础格式：https://dash.cloudflare.com/{account_id}/pages/view/{project_name}
```

优先级：
1. 若提供了 `CLOUDFLARE_PROJECT_URL`，直接使用
2. 否则使用 `CLOUDFLARE_ACCOUNT_ID` + `CLOUDFLARE_PROJECT_NAME` 拼接

### 2. 导航到项目页面

1. 在浏览器中导航到构建好的项目 URL
2. 等待页面加载完成（等待 `#root` 或主要内容区域渲染）
3. 截图确认当前页面状态

### 3. 验证项目存在

检查页面元素判断项目状态：

- **项目存在**：页面显示项目名称、部署历史列表、"Create deployment" 按钮
- **项目不存在**：页面显示 404 或 "Project not found"
- **无权限**：页面显示访问被拒绝或重定向到账号选择

### 4. 获取项目信息

若项目存在，提取以下信息：

| 信息 | 用途 |
|------|------|
| 项目名称 | 确认目标正确 |
| 生产链接 | `https://{project_name}.pages.dev` |
| 部署历史区域 | 后续验证新部署是否出现在列表中 |
| Create deployment 按钮位置 | 供部署组件使用 |

---

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `project_url` | string | 条件 | 完整项目 URL，优先于分项配置 |
| `account_id` | string | 条件 | Cloudflare 账号 ID |
| `project_name` | string | 条件 | Pages 项目名称 |

---

## 输出

| 状态 | 含义 | 后续动作 |
|------|------|----------|
| `PRJ_OK` | 项目存在且可访问 | 进入部署组件 |
| `PRJ_001` | 项目不存在 | 检查项目名称或账号 ID |
| `PRJ_002` | 项目 URL 不可访问 | 检查网络或账号权限 |

---

## 项目 URL 模式

```
https://dash.cloudflare.com/{account_id}/pages/view/{project_name}
```

示例：
```
https://dash.cloudflare.com/729cddcd8f0e2f087bf00950b10ebc80/pages/view/promptbase
```

---

## 注意事项

- **账号 ID 校验**：URL 中的账号 ID 必须与登录账号匹配，否则会被重定向
- **项目名称大小写**：Cloudflare Pages 项目名称通常为小写，注意一致性
- **页面加载等待**：Cloudflare Dashboard 为单页应用，需等待 JS 渲染完成
