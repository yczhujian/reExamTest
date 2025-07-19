# 智能专利分析系统

基于AI的专业专利分析SaaS平台，使用Google Gemini、SERP API和Supabase构建。

## 技术栈

- **前端**: Next.js 14 + TypeScript + Tailwind CSS
- **后端**: FastAPI (Python) + LangGraph
- **数据库**: Supabase (PostgreSQL)
- **AI服务**: Google Gemini + SERP API
- **部署**: Vercel (前端) + Cloud Run (API)

## 快速开始

### 1. 环境准备

确保已安装：
- Node.js 18+
- Python 3.11+
- npm 或 yarn

### 2. 配置环境变量

已配置的 `.env.local` 文件包含所有必要的API密钥。

### 3. 设置数据库

1. 访问 Supabase SQL编辑器：
   https://supabase.com/dashboard/project/grjslrfvlarfslgtoeqi/editor

2. 运行 `database/schema.sql` 中的SQL脚本

### 4. 安装依赖

```bash
# 前端依赖
cd frontend
npm install

# 后端依赖
cd ../api
pip install -r requirements.txt
```

### 5. 启动开发服务器

```bash
# 启动前端 (新终端)
cd frontend
npm run dev

# 启动后端API (新终端)
cd api
uvicorn main:app --reload --port 8000
```

### 6. 访问应用

- 前端: http://localhost:3000
- API文档: http://localhost:8000/docs

## 测试API连接

访问以下端点测试API连接：
- Gemini测试: http://localhost:8000/api/test-gemini
- SERP测试: http://localhost:8000/api/test-serp

## 项目结构

```
.
├── frontend/          # Next.js前端应用
├── api/              # FastAPI后端服务
│   └── workflows/    # LangGraph工作流
├── database/         # 数据库架构
├── scripts/          # 工具脚本
└── docs/            # 项目文档
```

## 开发进度

- [x] 项目初始化
- [x] Supabase数据库架构
- [x] Next.js前端框架
- [x] Python API基础
- [ ] LangGraph工作流集成
- [ ] 用户认证系统
- [ ] 专利分析功能
- [ ] 报告生成系统