-- 简单的RLS禁用方案（仅用于测试环境）
-- 在Supabase SQL编辑器中执行此脚本

-- 禁用所有相关表的RLS
ALTER TABLE patent_analyses DISABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_reports DISABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs DISABLE ROW LEVEL SECURITY;
ALTER TABLE search_cache DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_subscriptions DISABLE ROW LEVEL SECURITY;

-- 验证RLS已禁用
SELECT 
    tablename,
    rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('patent_analyses', 'analysis_reports', 'usage_logs', 'search_cache', 'user_subscriptions')
ORDER BY tablename;