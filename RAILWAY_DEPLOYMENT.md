# Railway 部署指南 - Python API

本指南将帮助您将 Python API 部署到 Railway，实现高级专利分析功能。

## 前置要求

1. Railway 账号（https://railway.app）
2. GitHub 仓库已推送最新代码
3. 前端已部署到 Vercel

## 部署步骤

### 1. 创建 Railway 项目

1. 登录 Railway：https://railway.app
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 授权 Railway 访问您的 GitHub
5. 选择您的仓库：`reExamTest`

### 2. 配置项目

#### 2.1 设置根目录
- 在项目设置中，设置 Root Directory 为：`/api`

#### 2.2 环境变量
在 Railway 项目中添加以下环境变量：

```env
# Supabase 配置
SUPABASE_URL=https://grjslrfvlarfslgtoeqi.supabase.co
SUPABASE_SERVICE_ROLE_KEY=[从 .env.local 复制]

# AI 服务密钥
GEMINI_API_KEY=[您的 Gemini API 密钥]
SERPAPI_KEY=[您的 SERP API 密钥]

# Python 环境
PYTHON_VERSION=3.11
PORT=8000

# CORS 配置（添加您的 Vercel 域名）
ALLOWED_ORIGINS=https://your-app.vercel.app,https://*.vercel.app
```

### 3. 部署配置

Railway 会自动检测到以下配置文件：
- `railway.json` - Railway 配置
- `Procfile` - 启动命令
- `requirements.txt` - Python 依赖

### 4. 触发部署

1. 推送代码到 GitHub 会自动触发部署
2. 或在 Railway 控制台手动触发部署

### 5. 获取 API URL

部署成功后：
1. 在 Railway 项目设置中找到 "Domains"
2. 点击 "Generate Domain" 生成域名
3. 您会得到类似：`https://your-app.railway.app` 的 URL

### 6. 更新前端配置

在 Vercel 中添加环境变量：
```
NEXT_PUBLIC_API_URL=https://your-app.railway.app
```

然后重新部署前端。

## 监控和日志

### 查看日志
- 在 Railway 控制台点击 "Logs" 查看实时日志
- 使用 Railway CLI：`railway logs`

### 监控资源使用
- CPU 和内存使用情况在控制台实时显示
- 设置使用量警告

## 故障排除

### 1. 部署失败
- 检查 `requirements.txt` 中的依赖是否正确
- 查看部署日志中的错误信息
- 确保 Python 版本正确（3.11）

### 2. API 无法访问
- 检查是否生成了域名
- 验证环境变量是否正确设置
- 检查 CORS 配置是否包含前端域名

### 3. LangGraph 错误
- 确保所有 AI API 密钥正确
- 检查 Supabase 连接是否正常
- 查看错误日志获取详细信息

### 4. 内存不足
- LangGraph 可能需要较多内存
- 考虑升级 Railway 计划
- 优化工作流减少内存使用

## 成本估算

Railway 定价（2024年）：
- **Hobby Plan**: $5/月，包含 $5 使用额度
- **Pro Plan**: $20/月，包含 $20 使用额度
- 额外使用按需计费

对于专利分析系统：
- 预计每月 $10-30（取决于使用量）
- 高级分析功能会增加资源消耗

## 性能优化

1. **使用 Redis 缓存**（可选）
   ```python
   # 在 Railway 添加 Redis 插件
   # 更新代码使用缓存
   ```

2. **异步任务队列**（可选）
   ```python
   # 使用 Celery 处理长时间任务
   ```

3. **自动扩展**
   - Railway Pro 计划支持自动扩展
   - 根据负载自动调整资源

## 更新部署

### 自动更新
每次推送到 GitHub 主分支会自动部署

### 手动更新
```bash
# 使用 Railway CLI
railway up
```

### 回滚
在 Railway 控制台可以一键回滚到之前的部署

## 安全建议

1. **API 密钥管理**
   - 使用 Railway 的密钥管理功能
   - 定期轮换密钥
   - 不要在代码中硬编码密钥

2. **访问控制**
   - 实施 API 认证
   - 使用速率限制
   - 监控异常请求

3. **数据保护**
   - 确保 HTTPS 始终启用
   - 实施请求验证
   - 加密敏感数据

## 相关文档

- [Railway 官方文档](https://docs.railway.app)
- [Python on Railway](https://docs.railway.app/guides/python)
- [环境变量管理](https://docs.railway.app/guides/variables)

---

部署完成后，您的系统将拥有：
- ✅ 高性能 Python API
- ✅ LangGraph 高级分析能力
- ✅ 自动扩展和监控
- ✅ 持续部署流程