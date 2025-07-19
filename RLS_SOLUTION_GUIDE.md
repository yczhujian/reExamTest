# RLS问题解决指南

## 当前问题
系统在执行专利分析时遇到RLS（行级安全）策略错误：
```
new row violates row-level security policy for table "analysis_reports"
```

## 解决步骤

### 步骤1：登录Supabase控制台
1. 访问：https://supabase.com/dashboard/project/grjslrfvlarfslgtoeqi/editor
2. 进入SQL编辑器

### 步骤2：执行禁用RLS脚本
在SQL编辑器中执行以下命令：

```sql
-- 禁用所有相关表的RLS
ALTER TABLE patent_analyses DISABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_reports DISABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs DISABLE ROW LEVEL SECURITY;
ALTER TABLE search_cache DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_subscriptions DISABLE ROW LEVEL SECURITY;
```

### 步骤3：验证RLS已禁用
执行以下查询确认RLS已禁用：

```sql
SELECT 
    tablename,
    rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('patent_analyses', 'analysis_reports', 'usage_logs', 'search_cache', 'user_subscriptions')
ORDER BY tablename;
```

所有表的`rowsecurity`列应该显示为`false`。

### 步骤4：重新测试系统

#### 方法A：使用自动化测试脚本
```bash
./test_system.sh
```

#### 方法B：手动测试
```bash
# 1. 注册新用户
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123456","full_name":"Test User"}'

# 2. 登录获取token（替换YOUR_EMAIL和YOUR_PASSWORD）
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"YOUR_EMAIL","password":"YOUR_PASSWORD"}' | jq -r '.access_token')

# 3. 执行专利分析（替换YOUR_USER_ID）
curl -X POST http://localhost:8000/api/analyze-patent \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "测试专利",
    "description": "测试描述",
    "technical_field": "测试领域",
    "technical_content": "测试内容",
    "user_id": "YOUR_USER_ID"
  }'
```

## 预期结果

禁用RLS后，专利分析应该能够成功完成，返回类似以下的响应：

```json
{
  "analysis_id": "xxx-xxx-xxx",
  "status": "completed",
  "overall_score": 85,
  "recommendation": "该发明具有较高的新颖性和创造性...",
  "message": "Patent analysis completed successfully"
}
```

## 重要提醒

⚠️ **安全警告**：禁用RLS仅适用于开发和测试环境。在生产环境中，必须正确配置RLS策略以确保数据安全。

## 后续步骤

1. **测试完成后**：确认所有功能正常工作
2. **生产环境部署前**：必须重新设计和实施适当的RLS策略
3. **建议**：考虑使用Supabase的服务账号或API密钥来绕过RLS，而不是完全禁用它

## 常见问题

### Q: 为什么使用service role key还是有RLS错误？
A: 可能是因为：
1. Service role key配置不正确
2. RLS策略中没有正确配置service_role的权限
3. Supabase客户端初始化时的问题

### Q: 如何在保持安全的同时解决这个问题？
A: 生产环境的正确做法是：
1. 为service_role创建专门的RLS策略
2. 使用触发器或存储过程来处理敏感操作
3. 在应用层实现额外的权限检查

## 联系支持

如果问题持续存在，请检查：
1. Supabase项目设置
2. 环境变量配置（特别是SUPABASE_SERVICE_ROLE_KEY）
3. API日志中的详细错误信息