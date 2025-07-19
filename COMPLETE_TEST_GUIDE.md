# 完整测试指南

## 当前问题及解决方案

### RLS策略问题
系统当前遇到的主要问题是数据库的行级安全（RLS）策略配置。这阻止了专利分析功能的正常运行。

**解决方案选项：**

1. **选项A：完整修复RLS策略**（推荐用于生产环境）
   - 在Supabase SQL编辑器中执行 `database/fix_rls_complete.sql`
   
2. **选项B：临时禁用RLS**（仅用于测试）
   - 在Supabase SQL编辑器中执行 `database/disable_rls_temp.sql`

## 自动化测试

运行自动化测试脚本：
```bash
./test_system.sh
```

该脚本会自动测试：
- API服务器状态
- 前端服务状态
- 数据库连接
- 外部API集成（SERP、Gemini）
- 用户注册和登录
- 专利分析创建

## 手动测试流程

### 1. 前端界面测试

1. **访问系统**
   ```
   http://localhost:3000
   ```

2. **用户注册**
   - 点击"注册"按钮
   - 填写邮箱（使用真实邮箱格式，如 user@gmail.com）
   - 设置密码（至少8位）
   - 填写姓名
   - 提交注册

3. **用户登录**
   - 使用刚注册的账号登录
   - 应该自动跳转到仪表板

4. **创建专利分析**
   - 点击"新建分析"
   - 填写专利信息：
     - 标题：智能家居控制系统
     - 描述：基于AI的智能家居解决方案
     - 技术领域：人工智能、物联网
     - 技术内容：详细描述技术方案
   - 提交分析

5. **查看分析结果**
   - 在仪表板查看分析列表
   - 点击查看详细分析报告

### 2. API测试（使用curl）

```bash
# 1. 注册用户
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testapi@example.com",
    "password": "password123",
    "full_name": "API Test User"
  }'

# 2. 登录获取token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testapi@example.com",
    "password": "password123"
  }' | jq -r '.access_token')

# 3. 创建分析（简单）
curl -X POST http://localhost:8000/api/analyses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "测试专利",
    "description": "测试描述",
    "technical_field": "测试领域",
    "technical_content": "测试内容",
    "user_id": "YOUR_USER_ID"
  }'

# 4. 运行完整分析（如果RLS已修复）
curl -X POST http://localhost:8000/api/analyze-patent \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "智能温控系统",
    "description": "基于AI的温度控制",
    "technical_field": "人工智能、物联网",
    "technical_content": "使用机器学习优化温度控制",
    "user_id": "YOUR_USER_ID"
  }'
```

### 3. 数据库验证

在Supabase SQL编辑器中运行：

```sql
-- 查看最近的分析记录
SELECT * FROM patent_analyses 
ORDER BY created_at DESC 
LIMIT 5;

-- 查看分析报告
SELECT * FROM analysis_reports 
ORDER BY created_at DESC 
LIMIT 5;

-- 查看使用记录
SELECT * FROM usage_logs 
ORDER BY created_at DESC 
LIMIT 5;

-- 检查RLS状态
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';
```

## 测试检查清单

- [ ] API服务器在端口8000运行
- [ ] 前端服务器在端口3000运行
- [ ] 可以访问前端首页
- [ ] 用户注册功能正常
- [ ] 用户登录功能正常
- [ ] 数据库连接正常
- [ ] SERP API集成正常
- [ ] Gemini API集成正常
- [ ] 可以创建专利分析记录
- [ ] 完整专利分析流程可运行（需要修复RLS）

## 常见问题

### 1. RLS策略错误
**错误**：`new row violates row-level security policy`
**解决**：执行RLS修复脚本或临时禁用RLS

### 2. 端口被占用
**错误**：`address already in use`
**解决**：
```bash
# 查找占用端口的进程
lsof -i :3000  # 或 :8000
# 终止进程
kill -9 <PID>
```

### 3. 环境变量未设置
**错误**：`Supabase URL和Service Role Key必须配置`
**解决**：确保`.env.local`文件存在且包含所有必需的环境变量

## 性能测试

完整的专利分析可能需要10-30秒，因为需要：
1. 搜索现有专利（SERP API）
2. 新颖性分析（Gemini API）
3. 创造性分析（Gemini API）
4. 实用性分析（Gemini API）
5. 生成综合报告（Gemini API）

## 下一步行动

1. **修复RLS策略**：这是当前最重要的任务
2. **完善错误处理**：改进错误信息的用户友好性
3. **添加进度显示**：专利分析时显示实时进度
4. **实现文件上传**：支持PDF等文档上传
5. **优化性能**：考虑使用任务队列处理长时间运行的分析