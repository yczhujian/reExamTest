# 测试指南 - 智能专利分析系统

## 系统启动

### 1. 启动后端API服务器
```bash
cd api
python main.py
```
API文档访问地址: http://localhost:8000/docs

### 2. 启动前端开发服务器
```bash
cd frontend
npm run dev
```
前端访问地址: http://localhost:3002

## 重要配置说明

### Supabase邮箱验证设置

**问题**: 目前Supabase启用了邮箱验证，导致使用测试邮箱（如test@example.com）注册会失败。

**解决方案**:

1. **临时禁用邮箱验证**（推荐用于测试）:
   - 登录Supabase项目仪表板
   - 转到 Authentication → Settings
   - 在 Email Auth 部分，关闭 "Confirm email" 选项
   - 保存更改

2. **使用真实邮箱格式**:
   - 使用符合真实邮箱格式的地址，如: user1@gmail.com, test@qq.com
   - 即使邮箱不存在，只要格式正确就能通过验证

## 测试流程

### 1. 用户注册
- 访问 http://localhost:3002
- 点击"注册"按钮
- 填写注册表单：
  - 姓名：测试用户
  - 邮箱：使用真实格式的邮箱（如user1@gmail.com）
  - 密码：至少8位（如testuser123）

### 2. 用户登录
- 使用刚注册的账号登录
- 系统会保存JWT token到localStorage

### 3. 创建专利分析
- 登录后进入仪表板
- 点击"新建分析"
- 填写专利信息：
  - 发明名称：例如"新型锂电池技术"
  - 简要描述：例如"提高能量密度的锂电池"
  - 技术领域：选择"电池技术"
  - 技术方案：详细描述技术内容

### 4. 查看分析结果
- 提交后系统会：
  1. 通过SERP API搜索相关专利和现有技术
  2. 使用Gemini API进行AI分析
  3. 生成新颖性、创造性、实用性评分
- 分析完成后可在仪表板查看结果

## API测试命令

### 测试注册（使用真实邮箱格式）
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser1@gmail.com",
    "password": "testuser123",
    "name": "测试用户1"
  }'
```

### 测试登录
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser1@gmail.com",
    "password": "testuser123"
  }'
```

### 测试专利分析（需要先获取token）
```bash
# 先登录获取token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "testuser1@gmail.com", "password": "testuser123"}' \
  | jq -r '.access_token')

# 创建分析
curl -X POST http://localhost:8000/api/analyze-patent \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "新型锂电池技术",
    "description": "提高能量密度的锂电池",
    "technical_field": "电池技术",
    "technical_content": "本发明涉及一种新型锂电池技术...",
    "user_id": "YOUR_USER_ID"
  }'
```

## 常见问题

### 1. 注册失败：Email address is invalid
- 原因：Supabase邮箱验证
- 解决：使用真实邮箱格式或禁用邮箱验证

### 2. 端口占用
- 前端默认端口：3000（如占用会自动使用3001, 3002等）
- 后端端口：8000
- 解决：结束占用端口的进程或修改端口配置

### 3. API连接失败
- 检查后端服务是否运行
- 确认前端API地址配置正确（http://localhost:8000）

### 4. Supabase连接失败
- 检查.env.local文件中的Supabase配置
- 确认Supabase项目正在运行

## 数据库初始化

如果还未执行数据库脚本，请在Supabase SQL编辑器中执行：
```sql
-- 执行 database/schema.sql 中的所有SQL语句
```

## 监控和日志

- API日志：`api/api.log`
- 前端控制台：浏览器开发者工具
- Supabase日志：Supabase仪表板的Logs部分