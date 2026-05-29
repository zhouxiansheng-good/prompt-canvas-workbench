---
name: prompt-canvas-build
description: >
  页面构建组件。生成所有核心代码文件（页面/组件/样式/数据）。
  Trigger: 组件一完成后自动进入，或用户说"生成页面"/"构建代码"/"写组件"时激活。
---

# 页面构建组件

**Trigger**: "生成页面" / "构建代码" / "写组件" / "填充模板"

**前置条件**: 组件一已完成（项目骨架已创建）

---

## 执行流程

### Step 1：生成数据模型

文件：`src/lib/prompts.ts`

模板来源：`templates/prompts.ts.template`

**关键规则**:
- Prompt接口定义必须包含：id, title, description, content, type, category, tags, usageCount, createdAt
- type字段枚举：'prompt' | 'persona' | 'project' | 'skill'
- categories数组定义所有二级标签
- 提供至少5条示例数据（覆盖不同类型）

### Step 2：生成全局样式

文件：`src/app/globals.css`

模板来源：`templates/globals.css.template`

**关键规则**:
- 四色主题变量（paper/blackboard/nordic/dopamine）
- body网格背景（24px网格线）
- 滚动条隐藏类 `.scrollbar-none`
- 响应式overflow（手机overflow-x:hidden，桌面overflow:hidden）

### Step 3：生成核心页面

文件：`src/app/page.tsx`

模板来源：`templates/page.tsx.template`

**关键规则**:
- 双层手风琴联动（BIG_TYPES → subTags → prompts）
- 卡片状态管理（openCardIds, cardPositions, focusOrder）
- 移动端抽屉式侧边栏（isMobileSidebarOpen）
- 响应式断点检测（window.innerWidth < 1024）
- 卡片初始位置：桌面x:360，手机x:16
- autoArrange动态计算列数

### Step 4：生成组件

**Header.tsx** (`templates/Header.tsx.template`):
- 接收 onMenuClick / showMenu props
- 手机端显示汉堡菜单 ☰
- 小屏隐藏副标题

**Footer.tsx** (`templates/Footer.tsx.template`):
- 包含 SupportButton
- 简洁版权信息

**PromptCard.tsx** (`templates/PromptCard.tsx.template`):
- react-draggable包裹
- drag-handle限制拖拽区域
- 收起/展开/关闭/复制功能
- 移动端自适应宽度
- typeConfig四色标签映射

**SupportButton.tsx** (`templates/SupportButton.tsx.template`):
- 赞赏码弹窗Modal
- 点击遮罩关闭
- 图片加载失败兜底

### Step 5：生成布局文件

文件：`src/app/layout.tsx`

基础HTML结构，引入全局样式。

### Step 6：验证文件完整性

检查清单：
- [ ] src/lib/prompts.ts
- [ ] src/app/globals.css
- [ ] src/app/page.tsx
- [ ] src/app/layout.tsx
- [ ] src/components/Header.tsx
- [ ] src/components/Footer.tsx
- [ ] src/components/PromptCard.tsx
- [ ] src/components/SupportButton.tsx

---

## 调用地址

- 本组件：`components/02-page-build/SKILL.md`
- 模板目录：`components/02-page-build/templates/`

---

## 关联组件

- 组件一（初始化）：提供项目骨架
- 组件三（部署）：读取本组件生成的代码进行构建
