---
name: security-compliance
description: "安全合规审查组件。检查 HTTPS/SSL、数据加密、访问控制、常见漏洞和日志审计。"
metadata:
  phase: "4"
  parent: "compliance-audit"
  type: "compliance-dimension"
---

# security-compliance — 安全合规审查组件

> 审查网站项目的安全合规性，覆盖HTTPS/SSL配置、数据加密、访问控制、漏洞扫描及日志审计。

---

## 职责

- 检查HTTPS/SSL配置是否正确
- 检查数据加密（传输加密+存储加密）
- 检查访问控制机制
- 检查常见漏洞（OWASP Top 10）
- 检查日志审计机制

---

## 操作流程

### 1. HTTPS/SSL配置审查

1. 检查网站是否全站启用HTTPS：
   - [ ] HTTP请求是否301重定向到HTTPS
   - [ ] 是否存在混合内容（HTTPS页面加载HTTP资源）
   - [ ] HSTS头是否配置（`Strict-Transport-Security`）
2. 检查SSL/TLS配置：
   - [ ] 证书是否有效（未过期、域名匹配）
   - [ ] 是否使用TLS 1.2或更高版本（禁用SSLv3、TLS 1.0/1.1）
   - [ ] 是否配置安全的密码套件（禁用RC4、DES等弱算法）
   - [ ] 是否启用OCSP Stapling
3. 检查安全响应头：
   - [ ] `Content-Security-Policy`
   - [ ] `X-Frame-Options`（防止点击劫持）
   - [ ] `X-Content-Type-Options: nosniff`
   - [ ] `Referrer-Policy`
   - [ ] `Permissions-Policy`

### 2. 数据加密审查

1. 传输加密：
   - [ ] 所有API接口是否HTTPS
   - [ ] WebSocket连接是否WSS
   - [ ] 第三方API调用是否HTTPS
2. 存储加密：
   - [ ] 数据库敏感字段是否加密（密码、身份证号、银行卡号）
   - [ ] 密码是否使用强哈希（bcrypt/Argon2/scrypt，禁止MD5/SHA1）
   - [ ] 密钥是否存储在环境变量或KMS，禁止硬编码
   - [ ] 备份数据是否加密
3. 密钥管理：
   - [ ] 加密密钥是否定期轮换
   - [ ] 密钥访问是否有权限控制
   - [ ] 开发/生产环境密钥是否分离

### 3. 访问控制审查

1. 身份认证：
   - [ ] 是否实现安全的登录机制（密码强度要求、登录失败锁定）
   - [ ] 是否支持多因素认证（MFA/2FA）
   - [ ] 会话管理是否安全（随机会话ID、过期时间、HttpOnly/Secure Cookie）
   - [ ] 是否防范暴力破解（验证码、速率限制）
2. 权限控制：
   - [ ] 是否实现最小权限原则
   - [ ] 是否有角色/权限分离（RBAC/ABAC）
   - [ ] 敏感操作是否二次确认
   - [ ] 是否有越权访问防护（水平越权、垂直越权）
3. API安全：
   - [ ] API是否要求认证
   - [ ] 是否有速率限制（Rate Limiting）
   - [ ] 是否防范IDOR（不安全的直接对象引用）
   - [ ] 是否防范Mass Assignment

### 4. 漏洞扫描（OWASP Top 10）

1. 检查以下漏洞：
   - [ ] **A01:2021-Broken Access Control** — 越权访问、目录遍历
   - [ ] **A02:2021-Cryptographic Failures** — 明文传输、弱加密
   - [ ] **A03:2021-Injection** — SQL注入、NoSQL注入、命令注入、XSS
   - [ ] **A04:2021-Insecure Design** — 业务逻辑缺陷
   - [ ] **A05:2021-Security Misconfiguration** — 默认配置、错误信息泄露
   - [ ] **A06:2021-Vulnerable and Outdated Components** — 依赖漏洞
   - [ ] **A07:2021-Identification and Authentication Failures** — 会话劫持、凭证填充
   - [ ] **A08:2021-Software and Data Integrity Failures** — 不安全的反序列化、供应链攻击
   - [ ] **A09:2021-Security Logging and Monitoring Failures** — 日志缺失、监控盲区
   - [ ] **A10:2021-Server-Side Request Forgery (SSRF)** — 服务端请求伪造
2. 代码扫描：
   - 检查是否存在`eval()`、`innerHTML`、拼接SQL等危险模式
   - 检查文件上传是否限制类型和大小
   - 检查是否暴露敏感信息（`.env`、密钥、调试信息）
3. 依赖安全：
   - 检查`package.json`中的依赖是否有已知CVE漏洞
   - 检查依赖版本是否过旧

### 5. 日志审计审查

1. 检查日志记录：
   - [ ] 是否记录关键操作（登录、修改、删除、支付）
   - [ ] 是否记录异常和错误
   - [ ] 是否记录安全事件（攻击尝试、权限变更）
2. 检查日志内容：
   - [ ] 日志是否包含时间戳、用户ID、操作类型、结果
   - [ ] 日志中是否脱敏（不记录密码、Token、身份证号）
   - [ ] 日志是否防篡改（只读存储、签名）
3. 检查日志保留：
   - [ ] 日志保留期限是否符合法规要求（网络安全法要求不少于6个月）
   - [ ] 是否有日志归档和备份机制
4. 检查监控告警：
   - [ ] 是否有异常行为监控（暴力破解、异常访问）
   - [ ] 是否有告警机制（邮件/短信/钉钉）

---

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `project_root` | string | 是 | 项目根目录绝对路径 |
| `target_url` | string | 否 | 部署后的目标URL（用于SSL检测） |
| `scan_dependencies` | boolean | 否 | 是否扫描依赖漏洞（默认true） |

---

## 输出

| 状态 | 含义 | 后续动作 |
|------|------|----------|
| `SEC_OK` | 安全合规审查通过 | 继续下一组件 |
| `SEC_WARN` | 存在中低危问题 | 记录风险清单，继续审查 |
| `SEC_FAIL` | 存在致命/高危问题 | 记录风险清单，建议阻断 |

---

## 风险项模板

| 编号 | 严重度 | 问题 | 法规依据 | 修复建议 |
|------|--------|------|----------|----------|
| S001 | 🔴 | 未启用HTTPS | 网络安全法第21条 | 全站启用HTTPS，配置HSTS |
| S002 | 🔴 | 密码使用弱哈希（MD5/SHA1） | 个保法第51条 | 改用bcrypt/Argon2 |
| S003 | 🟠 | 存在SQL注入风险 | 网络安全法第21条 | 使用参数化查询/ORM |
| S004 | 🟠 | 会话Cookie未设置HttpOnly/Secure | OWASP | 设置Cookie安全属性 |
| S005 | 🟡 | 缺少CSP安全头 | 最佳实践 | 配置Content-Security-Policy |
| S006 | 🟡 | 依赖存在已知CVE漏洞 | 最佳实践 | 升级依赖到安全版本 |
| S007 | 🟡 | 日志保留期不足6个月 | 网络安全法第21条 | 延长日志保留期 |
| S008 | 🟢 | 未启用2FA | 最佳实践 | 为管理员账户启用多因素认证 |
