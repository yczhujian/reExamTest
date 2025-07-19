-- 完整的RLS策略修复方案
-- 请在Supabase SQL编辑器中执行此脚本

-- 1. 先禁用所有表的RLS（临时）
ALTER TABLE patent_analyses DISABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_reports DISABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs DISABLE ROW LEVEL SECURITY;
ALTER TABLE search_cache DISABLE ROW LEVEL SECURITY;

-- 2. 删除所有现有策略
DROP POLICY IF EXISTS "Users can view own analyses" ON patent_analyses;
DROP POLICY IF EXISTS "Users can create analyses" ON patent_analyses;
DROP POLICY IF EXISTS "Users can update own analyses" ON patent_analyses;
DROP POLICY IF EXISTS "Service role full access analyses" ON patent_analyses;

DROP POLICY IF EXISTS "Users can view own analysis reports" ON analysis_reports;
DROP POLICY IF EXISTS "Service role can manage reports" ON analysis_reports;
DROP POLICY IF EXISTS "Service role full access" ON analysis_reports;

DROP POLICY IF EXISTS "Users can view own usage logs" ON usage_logs;
DROP POLICY IF EXISTS "Service role can insert usage logs" ON usage_logs;
DROP POLICY IF EXISTS "Service role full access logs" ON usage_logs;

-- 3. 重新启用RLS
ALTER TABLE patent_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_cache ENABLE ROW LEVEL SECURITY;

-- 4. 创建新的策略 - patent_analyses表
-- 允许所有人通过service role访问（API使用service role key）
CREATE POLICY "Enable all access for service role" ON patent_analyses
FOR ALL TO service_role
USING (true)
WITH CHECK (true);

-- 允许用户查看自己的分析
CREATE POLICY "Enable read access for users" ON patent_analyses
FOR SELECT TO authenticated
USING (auth.uid() = user_id);

-- 5. 创建新的策略 - analysis_reports表
-- 允许所有人通过service role访问
CREATE POLICY "Enable all access for service role" ON analysis_reports
FOR ALL TO service_role
USING (true)
WITH CHECK (true);

-- 允许用户查看与自己分析相关的报告
CREATE POLICY "Enable read access for users" ON analysis_reports
FOR SELECT TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM patent_analyses
        WHERE patent_analyses.id = analysis_reports.analysis_id
        AND patent_analyses.user_id = auth.uid()
    )
);

-- 6. 创建新的策略 - usage_logs表
-- 允许所有人通过service role访问
CREATE POLICY "Enable all access for service role" ON usage_logs
FOR ALL TO service_role
USING (true)
WITH CHECK (true);

-- 允许用户查看自己的使用记录
CREATE POLICY "Enable read access for users" ON usage_logs
FOR SELECT TO authenticated
USING (auth.uid() = user_id);

-- 7. 创建新的策略 - search_cache表
-- 允许所有人通过service role访问
CREATE POLICY "Enable all access for service role" ON search_cache
FOR ALL TO service_role
USING (true)
WITH CHECK (true);

-- 允许所有认证用户读取缓存（缓存是共享的）
CREATE POLICY "Enable read access for all users" ON search_cache
FOR SELECT TO authenticated
USING (true);

-- 8. 验证策略设置
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename IN ('patent_analyses', 'analysis_reports', 'usage_logs', 'search_cache')
ORDER BY tablename, policyname;