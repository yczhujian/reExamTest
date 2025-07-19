# CSP 错误解决方案

## 问题分析

### 错误原因
1. **Content Security Policy (CSP) 冲突**
   - Supabase Auth Helpers 库在某些操作中使用了 `eval()` 或类似的动态代码执行
   - 浏览器的安全策略阻止了这种行为
   - 这是一个已知的兼容性问题

2. **为什么会发生**
   - `@supabase/auth-helpers-nextjs` 在处理认证时可能使用了不安全的代码执行方式
   - Next.js 的开发模式默认启用了严格的 CSP 策略
   - 两者产生了冲突

## 解决方案

### 方案A：回退到本地 API（已实施）✅

我们已经将认证系统回退到使用本地 FastAPI 后端：

1. **登录页面** (`/app/auth/login/page.tsx`)
   - 使用 `fetch` 调用本地 API：`http://localhost:8000/api/auth/login`
   - 将 JWT token 保存在 localStorage

2. **注册页面** (`/app/auth/register/page.tsx`)
   - 使用 `fetch` 调用本地 API：`http://localhost:8000/api/auth/register`
   - 注册成功后跳转到登录页

### 方案B：修改 CSP 策略（备选）

如果你仍想使用 Supabase Auth，可以：

1. 在 `middleware.ts` 中添加 `'unsafe-eval'`（不推荐用于生产）
2. 使用 `supabase.auth.signInWithOtp` 替代密码登录
3. 升级到最新版本的 Supabase 库

### 方案C：使用 Supabase 但不使用 Auth Helpers

创建自定义的 Supabase 客户端（`/lib/supabase-client.ts`），直接使用 `@supabase/supabase-js`

## 当前状态

✅ **已修复** - 系统现在使用本地 API 进行认证，避免了 CSP 错误

## 使用说明

1. **确保后端运行**
   ```bash
   cd api
   python main.py
   ```

2. **访问前端**
   ```bash
   cd frontend
   npm run dev
   ```

3. **注册新账号**
   - 访问 http://localhost:3000/auth/register
   - 使用真实邮箱格式（如 user@example.com）
   - 密码至少 8 位

4. **登录系统**
   - 使用注册的账号登录
   - 系统会保存 JWT token 用于后续请求

## 优势

1. **没有 CSP 错误** - 完全避免了 eval 相关的安全策略问题
2. **更快的响应** - 本地 API 响应更快
3. **完全控制** - 可以自定义认证逻辑
4. **兼容性好** - 不依赖可能有兼容性问题的第三方库

## 后续建议

如果要部署到生产环境：

1. **使用 HTTPS** - 部署 API 到安全的服务器
2. **实现刷新令牌** - 增强安全性
3. **添加速率限制** - 防止暴力破解
4. **使用环境变量** - 管理 API 端点

## 测试账号

你可以创建新账号或使用之前的测试账号：
- demo_user_1752949248@example.com / Demo123456
- quick_test_1752948916@example.com / QuickTest123

现在系统应该可以正常登录了！