-- 专利分析系统数据库架构
-- 使用Supabase PostgreSQL

-- 启用必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 专利分析任务表
CREATE TABLE patent_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT CHECK (status IN ('pending', 'processing', 'completed', 'failed')) DEFAULT 'pending',
    input_file_url TEXT,
    report_url TEXT,
    metadata JSONB DEFAULT '{}',
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 搜索缓存表
CREATE TABLE search_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_hash TEXT UNIQUE NOT NULL,
    query_text TEXT NOT NULL,
    results JSONB NOT NULL,
    source TEXT CHECK (source IN ('google_patent', 'serp', 'scholar')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

-- 使用量记录表
CREATE TABLE usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    analysis_id UUID REFERENCES patent_analyses(id) ON DELETE CASCADE,
    service TEXT NOT NULL CHECK (service IN ('gemini', 'serp', 'storage')),
    tokens_used INTEGER,
    api_calls INTEGER DEFAULT 1,
    cost DECIMAL(10,4),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 专利向量表（用于相似度搜索）
CREATE TABLE patent_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patent_id TEXT NOT NULL,
    title TEXT NOT NULL,
    abstract TEXT,
    embedding vector(768),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(patent_id)
);

-- 分析报告表
CREATE TABLE analysis_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES patent_analyses(id) ON DELETE CASCADE,
    report_type TEXT CHECK (report_type IN ('novelty', 'inventiveness', 'utility', 'fto', 'comprehensive')),
    content JSONB NOT NULL,
    summary TEXT,
    score DECIMAL(3,2) CHECK (score >= 0 AND score <= 1),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(analysis_id, report_type)
);

-- 用户订阅表
CREATE TABLE user_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    plan_type TEXT CHECK (plan_type IN ('starter', 'professional', 'enterprise')) DEFAULT 'starter',
    status TEXT CHECK (status IN ('active', 'canceled', 'expired')) DEFAULT 'active',
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    monthly_analyses_limit INTEGER,
    monthly_analyses_used INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_patent_analyses_user_id ON patent_analyses(user_id);
CREATE INDEX idx_patent_analyses_status ON patent_analyses(status);
CREATE INDEX idx_search_cache_expires ON search_cache(expires_at);
CREATE INDEX idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX idx_usage_logs_created_at ON usage_logs(created_at);
CREATE INDEX idx_patent_embeddings_embedding ON patent_embeddings USING ivfflat (embedding vector_cosine_ops);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_patent_analyses_updated_at BEFORE UPDATE ON patent_analyses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_subscriptions_updated_at BEFORE UPDATE ON user_subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS (Row Level Security) 策略
ALTER TABLE patent_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;

-- 用户只能查看自己的数据
CREATE POLICY "Users can view own analyses" ON patent_analyses
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own analyses" ON patent_analyses
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own analyses" ON patent_analyses
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own usage" ON usage_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own reports" ON analysis_reports
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM patent_analyses 
            WHERE patent_analyses.id = analysis_reports.analysis_id 
            AND patent_analyses.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can view own subscription" ON user_subscriptions
    FOR SELECT USING (auth.uid() = user_id);