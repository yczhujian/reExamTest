# Supabase 配置指南

## 关闭邮箱验证（开发测试）

为了方便开发测试，您需要在Supabase仪表板中关闭邮箱验证：

1. **登录Supabase仪表板**
   - 访问 https://app.supabase.com
   - 登录您的账户

2. **进入项目设置**
   - 选择您的项目（grjslrfvlarfslgtoeqi）
   - 点击左侧菜单的 "Authentication"

3. **关闭邮箱验证**
   - 点击 "Providers" 标签
   - 找到 "Email" 部分
   - 关闭 "Confirm email" 开关
   - 保存更改

4. **可选：配置SMTP（生产环境）**
   如果您想在生产环境中启用邮箱验证，需要配置SMTP：
   - 在 Authentication → Settings → Email Auth
   - 配置您的SMTP服务器信息

## 数据库初始化

如果您还未执行数据库脚本：

1. **打开SQL编辑器**
   - 在Supabase仪表板左侧菜单
   - 点击 "SQL Editor"

2. **执行初始化脚本**
   - 复制 `database/schema.sql` 文件的全部内容
   - 粘贴到SQL编辑器中
   - 点击 "Run" 执行

## 测试账号

关闭邮箱验证后，您可以使用以下测试账号：

- 邮箱：testuser1@gmail.com
- 密码：testuser123

或者注册新的测试账号。

## 重要提醒

- **开发环境**：关闭邮箱验证方便测试
- **生产环境**：务必开启邮箱验证并配置SMTP
- **安全性**：生产环境还应考虑启用双因素认证等安全措施