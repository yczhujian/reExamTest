# Supabase架构方案分析

## 一、Supabase优势与挑战

### 优势
1. **开发效率高**
   - 内置认证系统
   - 实时数据库
   - 自动生成API
   - 文件存储
   - Edge Functions支持

2. **成本优势**
   - 免费版可支持MVP
   - 按需付费，成本可控
   - 无需维护基础设施

3. **开箱即用**
   - PostgreSQL数据库
   - Row Level Security (RLS)
   - 实时订阅
   - 向量扩展(pgvector)

### 挑战
1. **LangGraph集成**：需要在Edge Functions中运行
2. **任务队列**：需要额外解决方案
3. **向量数据库**：pgvector性能不如专用方案

## 二、推荐架构方案

### 方案A：Supabase + Vercel（推荐）

```
┌─────────────────┐     ┌─────────────────┐
│   Next.js App   │     │  Vercel Edge    │
│   (Vercel)      │────▶│   Functions     │
└─────────────────┘     └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │    Supabase     │
                        ├─────────────────┤
                        │ • PostgreSQL    │
                        │ • Auth          │
                        │ • Storage       │
                        │ • Realtime      │
                        └────────┬────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 │                               │
        ┌────────▼────────┐            ┌────────▼────────┐
        │  LangGraph      │            │   External APIs  │
        │  (Vercel API)   │            │ • Gemini        │
        └─────────────────┘            │ • SERP          │
                                       └─────────────────┘
```

**优点**：
- Vercel与Next.js完美集成
- Edge Functions支持Python（通过WASM）
- 全球CDN部署
- 简化的DevOps

### 方案B：Supabase + 自建API服务

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js App   │────▶│    Supabase     │◀────│  Python API     │
│   (Vercel)      │     │  (Auth+DB)      │     │  (Cloud Run)    │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                          │
                                                 ┌────────▼────────┐
                                                 │   LangGraph     │
                                                 │   Workflow      │
                                                 └─────────────────┘
```

**优点**：
- Python环境完全可控
- LangGraph原生支持
- 可使用Celery等任务队列

## 三、具体实施建议

### 1. 数据库设计（使用Supabase）

```sql
-- 用户表（由Supabase Auth管理）

-- 专利分析任务表
CREATE TABLE patent_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    title TEXT NOT NULL,
    status TEXT CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    input_file_url TEXT,
    report_url TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 搜索缓存表
CREATE TABLE search_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_hash TEXT UNIQUE NOT NULL,
    results JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

-- 使用量记录表
CREATE TABLE usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    service TEXT NOT NULL,
    tokens_used INTEGER,
    cost DECIMAL(10,4),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 启用向量扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 专利向量表
CREATE TABLE patent_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patent_id TEXT NOT NULL,
    embedding vector(768),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. Edge Functions实现

```typescript
// supabase/functions/analyze-patent/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  const { analysisId, step } = await req.json()
  
  // 调用Python API进行分析
  const response = await fetch(`${PYTHON_API_URL}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ analysisId, step })
  })
  
  // 更新数据库状态
  const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
  await supabase
    .from('patent_analyses')
    .update({ status: 'processing', updated_at: new Date() })
    .eq('id', analysisId)
  
  return new Response(JSON.stringify({ success: true }))
})
```

### 3. 任务队列替代方案

**使用Supabase Realtime + pg_cron**：
```sql
-- 创建任务表
CREATE TABLE task_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type TEXT NOT NULL,
    payload JSONB,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- 使用pg_cron定期处理任务
SELECT cron.schedule(
    'process-tasks',
    '*/1 * * * *', -- 每分钟
    $$
    UPDATE task_queue 
    SET status = 'processing' 
    WHERE status = 'pending' 
    AND created_at < NOW() - INTERVAL '5 seconds'
    LIMIT 10;
    $$
);
```

## 四、成本对比

### Supabase方案成本
| 项目 | 免费版 | Pro版($25/月) |
|------|--------|--------------|
| 数据库 | 500MB | 8GB |
| 存储 | 1GB | 100GB |
| 带宽 | 2GB | 50GB |
| Edge Functions | 500K调用 | 2M调用 |
| 向量维度 | 支持 | 支持 |

### 原方案成本对比
- 原方案：$2,250/月
- Supabase方案：~$300/月（包含所有服务）
- **节省：87%**

## 五、迁移建议

1. **保留的技术**：
   - Next.js前端
   - LangGraph（通过API）
   - Gemini & SERP集成

2. **替换的技术**：
   - PostgreSQL → Supabase Database
   - Redis → Supabase Realtime
   - 自建Auth → Supabase Auth
   - MinIO → Supabase Storage

3. **新增考虑**：
   - 使用Inngest替代Celery（专为Serverless设计）
   - 使用Upstash Redis补充缓存需求
   - 考虑Pinecone Cloud作为向量数据库

## 六、最终推荐

**推荐采用方案A（Supabase + Vercel）**，原因：
1. 开发速度快3倍
2. 运维成本降低90%
3. 自动扩展，无需担心性能
4. 专注于核心业务逻辑

**但建议保留一个轻量Python服务**用于：
- LangGraph工作流执行
- 复杂的专利分析逻辑
- 批量数据处理

这样既能享受Supabase的便利，又不失去Python生态的强大功能。