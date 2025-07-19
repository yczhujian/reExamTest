# 部署指南 - 智能专利分析系统

本指南将帮助您将系统部署到生产环境（前端部署到 Vercel，后端部署到 Supabase Edge Functions）。

## 📋 前置要求

1. GitHub 账号
2. Vercel 账号（免费）
3. Supabase 项目（已创建）
4. Node.js 18+ 已安装
5. Git 已安装

## 🚀 第一步：准备代码

### 1.1 克隆或下载项目代码
```bash
git clone [您的仓库地址]
cd reExamTest
```

### 1.2 安装依赖
```bash
# 安装前端依赖
cd frontend
npm install
cd ..

# 安装 Supabase CLI（如果还没安装）
npm install -g supabase
```

## 🔧 第二步：部署后端（Supabase Edge Functions）

### 2.1 登录 Supabase CLI
```bash
supabase login
```
浏览器会自动打开，完成登录授权。

### 2.2 运行部署脚本
```bash
# 在项目根目录运行
./deploy-supabase-functions.sh
```

### 2.3 设置环境变量
1. 打开 Supabase 控制台：https://supabase.com/dashboard
2. 选择您的项目
3. 左侧菜单选择 "Edge Functions"
4. 点击 "Manage secrets"
5. 添加以下环境变量：
   - `GEMINI_API_KEY`：您的 Gemini API 密钥
   - `SERPAPI_KEY`：您的 SERP API 密钥

## 🌐 第三步：部署前端（Vercel）

### 3.1 准备 GitHub 仓库
1. 创建新的 GitHub 仓库
2. 上传代码（确保 `.env.local` 文件不要上传）：
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 3.2 在 Vercel 部署

1. **登录 Vercel**
   - 访问 https://vercel.com
   - 使用 GitHub 账号登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Import Git Repository"
   - 选择您的 GitHub 仓库

3. **配置项目**
   - Framework Preset: Next.js（会自动检测）
   - Root Directory: `frontend`
   - Build Command: `npm run build`（默认）
   - Output Directory: `.next`（默认）

4. **设置环境变量**（重要！）
   
   点击 "Environment Variables"，添加以下变量：

   | 变量名 | 值 | 说明 |
   |--------|-----|------|
   | `NEXT_PUBLIC_SUPABASE_URL` | `https://grjslrfvlarfslgtoeqi.supabase.co` | Supabase 项目 URL |
   | `NEXT_PUBLIC_SUPABASE_ANON_KEY` | 从 .env.local 复制 | Supabase 匿名密钥 |
   | `SUPABASE_SERVICE_ROLE_KEY` | 从 .env.local 复制 | Supabase 服务密钥 |

5. **部署**
   - 点击 "Deploy"
   - 等待部署完成（约 2-3 分钟）

### 3.3 配置 Supabase 允许的域名

1. 打开 Supabase 控制台
2. 进入 Authentication → URL Configuration
3. 在 "Site URL" 添加您的 Vercel 域名（如 `https://your-app.vercel.app`）
4. 在 "Redirect URLs" 添加：
   - `https://your-app.vercel.app`
   - `https://your-app.vercel.app/*`

## ✅ 第四步：验证部署

1. **访问您的应用**
   - 打开 Vercel 提供的 URL（如 `https://your-app.vercel.app`）

2. **测试功能**
   - 注册新用户（使用真实邮箱格式）
   - 登录系统
   - 创建专利分析
   - 查看分析结果

## 🔐 安全建议

### 生产环境密钥管理

1. **生成新的 API 密钥**（推荐）
   - Gemini API: https://makersuite.google.com/app/apikey
   - SERP API: https://serpapi.com/manage-api-key

2. **定期轮换密钥**
   - 每 3-6 个月更新一次
   - 在 Vercel 和 Supabase 中同步更新

3. **监控使用情况**
   - 设置 API 使用限额
   - 监控异常请求

## 🚨 常见问题

### 1. Edge Functions 部署失败
- 确保已正确登录 Supabase CLI
- 检查项目 ID 是否正确
- 尝试手动部署：`supabase functions deploy function-name`

### 2. 前端无法连接后端
- 检查 Supabase URL 和密钥是否正确
- 确保 Edge Functions 已成功部署
- 检查浏览器控制台错误信息

### 3. 用户无法登录
- 确保已在 Supabase 中禁用邮箱验证（用于测试）
- 检查 Redirect URLs 配置
- 清除浏览器缓存和 Cookie

### 4. CORS 错误
- 检查 Edge Functions 的 CORS 配置
- 确保前端域名已添加到允许列表

## 📊 监控和维护

### 监控
- Vercel Dashboard: 查看前端性能和错误
- Supabase Dashboard: 监控数据库和函数调用
- 设置错误通知（可选）

### 维护建议
- 定期检查日志
- 监控 API 配额使用
- 定期备份数据库
- 更新依赖包

## 🔄 更新部署

### 更新前端
```bash
git push origin main
```
Vercel 会自动检测并重新部署。

### 更新 Edge Functions
```bash
./deploy-supabase-functions.sh
```

## 📞 获取帮助

如遇到问题：
1. 查看项目的 README.md 和 TESTING_GUIDE.md
2. 检查 Vercel 和 Supabase 的日志
3. 查阅官方文档：
   - Vercel: https://vercel.com/docs
   - Supabase: https://supabase.com/docs

---

祝您部署顺利！🎉