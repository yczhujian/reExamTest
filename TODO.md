# 智能专利分析系统开发任务清单

## 项目概述
基于Supabase + LangGraph + Gemini + SERP API构建的专业专利分析SaaS系统

## 技术栈更新
- **后端服务**: Supabase (PostgreSQL + Auth + Storage + Realtime)
- **API服务**: Vercel Functions + Python API (Cloud Run)
- **前端框架**: Next.js 14 + Vercel
- **工作流引擎**: LangGraph (Python API)
- **AI服务**: Google Gemini + SERP API

## 开发任务列表

### Phase 1: 基础架构搭建（第1-2周）

#### Supabase配置
- [ ] 1. **初始化Supabase项目**
  - [ ] 创建Supabase项目
  - [ ] 配置环境变量（.env.local）
  - [ ] 设置项目安全规则
  - [ ] 启用必要的扩展（pgvector）

- [ ] 2. **设计数据库架构**
  - [ ] 创建专利分析表（patent_analyses）
  - [ ] 创建搜索缓存表（search_cache）
  - [ ] 创建使用量记录表（usage_logs）
  - [ ] 创建专利向量表（patent_embeddings）
  - [ ] 设置RLS（行级安全）策略

- [ ] 3. **配置Supabase服务**
  - [ ] 设置Authentication
  - [ ] 配置Storage buckets（文档、报告）
  - [ ] 创建Database Functions
  - [ ] 设置Realtime订阅

#### Python API服务
- [ ] 4. **搭建Python API服务（Cloud Run）**
  - [ ] 创建FastAPI项目结构
  - [ ] 配置Docker容器
  - [ ] 实现Supabase连接
  - [ ] 设置CORS和认证中间件

### Phase 2: 核心功能实现（第3-4周）

#### API集成
- [ ] 5. **实现SERP API集成和专利搜索模块**
  - [ ] 创建SERP API客户端封装
  - [ ] 实现专利搜索策略（关键词、分类、引用）
  - [ ] 开发搜索结果解析和标准化
  - [ ] 利用Supabase缓存搜索结果

- [ ] 6. **实现Gemini API集成和分析模块**
  - [ ] 创建Gemini API客户端封装
  - [ ] 设计提示词模板系统
  - [ ] 实现结构化输出解析
  - [ ] 开发API调用重试和错误处理

#### LangGraph工作流
- [ ] 7. **构建LangGraph工作流引擎**
  - [ ] 设计专利分析状态机
  - [ ] 实现工作流节点（解析、搜索、分析、报告）
  - [ ] 配置条件边和循环逻辑
  - [ ] 集成Supabase状态持久化

### Phase 3: 分析模块开发（第5-6周）

- [ ] 8. **开发技术交底书解析模块**
  - [ ] 利用Supabase Storage处理文档上传
  - [ ] 实现多格式文档读取（PDF、Word、Markdown）
  - [ ] 开发技术特征提取算法
  - [ ] 创建IPC/CPC分类识别
  - [ ] 存储解析结果到Supabase

- [ ] 9. **开发新颖性分析模块**
  - [ ] 设计技术特征对比算法
  - [ ] 实现现有技术映射
  - [ ] 开发新颖性评分系统
  - [ ] 创建区别特征识别

- [ ] 10. **开发创造性分析模块**
  - [ ] 实现最接近现有技术识别
  - [ ] 开发技术问题分析
  - [ ] 创建显而易见性评估
  - [ ] 实现技术效果分析

- [ ] 11. **开发报告生成模块**
  - [ ] 设计报告模板引擎
  - [ ] 实现Markdown到PDF转换
  - [ ] 创建图表生成器
  - [ ] 将报告存储到Supabase Storage

### Phase 4: 前端开发（第7-8周）

#### 前端基础
- [ ] 12. **搭建Next.js前端项目**
  - [ ] 初始化Next.js 14项目
  - [ ] 配置TypeScript和ESLint
  - [ ] 集成shadcn/ui和Tailwind CSS
  - [ ] 配置Supabase客户端

- [ ] 13. **实现Supabase认证集成**
  - [ ] 配置Supabase Auth
  - [ ] 实现登录/注册界面
  - [ ] 开发OAuth集成（Google/GitHub）
  - [ ] 创建用户profile管理

#### 核心界面
- [ ] 14. **开发文件上传和管理界面**
  - [ ] 集成Supabase Storage上传
  - [ ] 实现拖拽上传组件
  - [ ] 创建文件列表和预览
  - [ ] 利用Realtime显示解析状态

- [ ] 15. **开发分析任务管理界面**
  - [ ] 创建任务创建向导
  - [ ] 实现任务列表（使用Supabase查询）
  - [ ] 开发实时进度（Supabase Realtime）
  - [ ] 创建任务详情页面

- [ ] 16. **开发报告查看和下载功能**
  - [ ] 从Supabase Storage获取报告
  - [ ] 实现报告预览界面
  - [ ] 创建PDF查看器集成
  - [ ] 实现公开分享链接

### Phase 5: 系统优化（第9-10周）

#### 性能和可靠性
- [ ] 17. **实现缓存和后台任务**
  - [ ] 利用Supabase函数实现缓存逻辑
  - [ ] 配置Vercel Edge缓存
  - [ ] 使用Inngest实现后台任务
  - [ ] 开发任务重试机制

- [ ] 18. **实现API限流和使用量追踪**
  - [ ] 使用Supabase RLS实现限流
  - [ ] 创建使用量统计函数
  - [ ] 实现配额管理
  - [ ] 开发使用量仪表板

#### 商业功能
- [ ] 19. **开发订阅和支付系统**
  - [ ] 集成Stripe支付
  - [ ] 在Supabase中管理订阅状态
  - [ ] 实现Webhook处理（Vercel Functions）
  - [ ] 创建计费页面

### Phase 6: 测试和部署（第11-12周）

- [ ] 20. **编写测试用例**
  - [ ] Python API单元测试
  - [ ] LangGraph工作流测试
  - [ ] 前端组件测试（Jest + React Testing Library）
  - [ ] E2E测试（Playwright）

- [ ] 21. **部署配置**
  - [ ] 配置Vercel部署（前端）
  - [ ] 配置Cloud Run部署（Python API）
  - [ ] 设置GitHub Actions CI/CD
  - [ ] 配置环境变量和密钥

### Phase 7: 文档和优化（第13周+）

- [ ] 22. **编写文档**
  - [ ] API文档（自动生成）
  - [ ] 用户使用指南
  - [ ] 开发者集成文档
  - [ ] 视频教程制作

- [ ] 23. **性能优化**
  - [ ] 分析Supabase查询性能
  - [ ] 优化向量搜索
  - [ ] 实施边缘缓存
  - [ ] 进行负载测试

## 技术栈清单（更新后）

### 核心服务
- **Supabase**: 数据库、认证、存储、实时通信
- **Vercel**: 前端托管、Edge Functions
- **Google Cloud Run**: Python API服务

### 后端技术
- Python 3.11+
- FastAPI（轻量API服务）
- LangGraph（工作流引擎）
- Supabase Python客户端

### 前端技术
- Next.js 14 (App Router)
- TypeScript
- shadcn/ui
- Tailwind CSS
- @supabase/supabase-js
- @supabase/auth-helpers-nextjs

### AI/API服务
- Google Gemini API
- SERP API
- Inngest（后台任务）

### 支付和监控
- Stripe
- Vercel Analytics
- Sentry（错误追踪）

## 开发优先级说明

1. **高优先级**（1-16）：核心功能，MVP必需
2. **中优先级**（17-21）：优化和商业化功能
3. **低优先级**（22-23）：文档和性能优化

## 预计时间线

- **MVP版本**：6-8周（任务1-16）
- **Beta版本**：10-12周（任务1-21）
- **正式版本**：13周+（所有任务）

## 成本优化（使用Supabase后）

### 月度成本对比
| 项目 | 原方案 | Supabase方案 |
|------|--------|-------------|
| 基础设施 | $1,600 | $25 (Pro版) |
| 数据库 | $400 | 包含 |
| 向量数据库 | $300 | 包含(pgvector) |
| 存储 | $250 | 包含 |
| API服务 | - | $50 (Cloud Run) |
| **总计** | $2,550 | $75 |
| **节省** | - | 97% |

---

**注意事项**：
- Supabase大幅简化了基础设施管理
- 重点关注业务逻辑而非运维
- 利用Supabase的实时功能提升用户体验
- 保持Python API精简，仅处理LangGraph工作流