# 修复RLS策略问题

当前系统在执行专利分析时遇到了RLS（行级安全）策略错误。这是因为`analysis_reports`表的策略配置不正确。

## 问题描述
错误信息：`new row violates row-level security policy for table "analysis_reports"`

## 解决方案

### 方法1：执行修复脚本（推荐）
1. 登录到Supabase控制台：https://supabase.com/dashboard/project/grjslrfvlarfslgtoeqi/editor
2. 在SQL编辑器中执行 `database/fix_rls_policies.sql` 文件的内容
3. 执行成功后，RLS策略将被正确配置

### 方法2：临时禁用RLS（仅用于测试）
如果您只是想快速测试系统，可以临时禁用RLS：

```sql
-- 在Supabase SQL编辑器中执行
ALTER TABLE analysis_reports DISABLE ROW LEVEL SECURITY;
ALTER TABLE patent_analyses DISABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs DISABLE ROW LEVEL SECURITY;
```

**注意**：这种方法仅适用于测试环境，生产环境必须启用RLS。

### 方法3：验证Service Role Key
确保 `.env.local` 文件中的 `SUPABASE_SERVICE_ROLE_KEY` 是正确的。Service Role Key应该绕过所有RLS策略。

## 验证修复
修复后，可以通过以下命令测试专利分析功能：

```bash
# 1. 注册新用户
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
  }'

# 2. 登录获取token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'

# 3. 使用token创建分析（替换YOUR_TOKEN和YOUR_USER_ID）
curl -X POST http://localhost:8000/api/analyze-patent \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "测试专利",
    "description": "测试描述",
    "technical_field": "人工智能",
    "technical_content": "测试技术内容",
    "user_id": "YOUR_USER_ID"
  }'
```

## 根本原因
问题的根本原因是RLS策略没有正确配置service_role的权限。API使用service role key访问数据库，但RLS策略限制了插入操作。修复脚本通过为service_role角色添加完全访问权限来解决这个问题。