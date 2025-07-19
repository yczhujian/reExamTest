-- 临时禁用RLS以进行测试
-- 警告：仅用于开发/测试环境，生产环境必须启用RLS

ALTER TABLE patent_analyses DISABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_reports DISABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs DISABLE ROW LEVEL SECURITY;
ALTER TABLE search_cache DISABLE ROW LEVEL SECURITY;

-- 验证RLS状态
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('patent_analyses', 'analysis_reports', 'usage_logs', 'search_cache');