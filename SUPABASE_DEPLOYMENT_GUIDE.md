# Supabase 部署指南

本指南将帮助你将后端部署到 Supabase，这样你就可以使用真实账号而不是测试账号。

## 前置要求

1. **安装 Supabase CLI**
   ```bash
   brew install supabase/tap/supabase
   ```

2. **确保已经在 Supabase 中禁用了 RLS**（之前已完成）

## 部署步骤

### 1. 安装依赖

```bash
cd frontend
npm install @supabase/auth-helpers-nextjs
```

### 2. 部署 Edge Functions

运行部署脚本：
```bash
./deploy-supabase.sh
```

这个脚本会：
- 登录到 Supabase
- 链接到你的项目
- 设置环境变量（GEMINI_API_KEY 和 SERPAPI_KEY）
- 部署三个 Edge Functions：
  - `analyze-patent` - 执行专利分析
  - `create-analysis` - 创建分析记录
  - `get-analyses` - 获取分析列表

### 3. 更新前端配置

前端已经更新为使用 Supabase Auth，主要变化：
- 登录页面使用 `supabase.auth.signInWithPassword`
- 注册页面使用 `supabase.auth.signUp`
- API 调用使用 Supabase Edge Functions

### 4. 启用邮箱验证（可选）

如果你想要真实的邮箱验证：
1. 登录 Supabase 控制台
2. 进入 Authentication → Providers → Email
3. 启用 "Confirm email"
4. 配置 SMTP 设置（可以使用 SendGrid、Mailgun 等）

## 使用真实账号

部署完成后，你可以：

1. **访问前端**
   ```
   http://localhost:3000
   ```

2. **注册真实账号**
   - 使用真实邮箱地址
   - 设置安全的密码
   - 如果启用了邮箱验证，需要查收邮件

3. **登录并使用**
   - 使用注册的账号登录
   - 创建专利分析
   - 查看分析结果

## Edge Functions URL

部署后的 Edge Functions URL：
- 分析专利: `https://grjslrfvlarfslgtoeqi.supabase.co/functions/v1/analyze-patent`
- 创建分析: `https://grjslrfvlarfslgtoeqi.supabase.co/functions/v1/create-analysis`
- 获取分析: `https://grjslrfvlarfslgtoeqi.supabase.co/functions/v1/get-analyses`

## 故障排除

### 1. 部署失败
- 确保已安装 Supabase CLI
- 确保已登录 Supabase: `supabase login`
- 检查项目 ID 是否正确

### 2. 认证问题
- 确保前端使用的是 Supabase Auth
- 检查环境变量是否正确设置
- 查看浏览器控制台的错误信息

### 3. Edge Functions 错误
- 查看 Supabase 控制台中的函数日志
- 确保 API 密钥（GEMINI_API_KEY, SERPAPI_KEY）已正确设置

## 生产环境部署

对于生产环境：

1. **部署前端到 Vercel**
   ```bash
   vercel --prod
   ```

2. **配置环境变量**
   在 Vercel 中设置：
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`

3. **启用 RLS**
   生产环境必须启用并正确配置 RLS 策略

4. **配置自定义域名**
   在 Vercel 和 Supabase 中配置自定义域名

## 总结

现在你的系统已经：
- ✅ 使用 Supabase Auth 进行真实用户认证
- ✅ 后端部署为 Supabase Edge Functions
- ✅ 可以注册和使用真实账号
- ✅ 数据安全存储在 Supabase 中

你不再需要使用测试账号，可以注册真实账号来使用系统了！