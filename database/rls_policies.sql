-- RLS策略配置
-- 在执行schema.sql之后执行此脚本

-- 为user_subscriptions表启用RLS
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;

-- 允许用户读取自己的订阅信息
CREATE POLICY "Users can view own subscription" ON user_subscriptions
FOR SELECT USING (auth.uid() = user_id);

-- 允许service role创建订阅记录
CREATE POLICY "Service role can insert subscriptions" ON user_subscriptions
FOR INSERT WITH CHECK (true);

-- 允许用户更新自己的订阅信息
CREATE POLICY "Users can update own subscription" ON user_subscriptions
FOR UPDATE USING (auth.uid() = user_id);

-- 为patent_analyses表启用RLS
ALTER TABLE patent_analyses ENABLE ROW LEVEL SECURITY;

-- 允许用户查看自己的分析
CREATE POLICY "Users can view own analyses" ON patent_analyses
FOR SELECT USING (auth.uid() = user_id);

-- 允许用户创建分析
CREATE POLICY "Users can create analyses" ON patent_analyses
FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 允许用户更新自己的分析
CREATE POLICY "Users can update own analyses" ON patent_analyses
FOR UPDATE USING (auth.uid() = user_id);

-- 为analysis_reports表启用RLS
ALTER TABLE analysis_reports ENABLE ROW LEVEL SECURITY;

-- 允许用户查看自己分析的报告
CREATE POLICY "Users can view own analysis reports" ON analysis_reports
FOR SELECT USING (
    EXISTS (
        SELECT 1 FROM patent_analyses
        WHERE patent_analyses.id = analysis_reports.analysis_id
        AND patent_analyses.user_id = auth.uid()
    )
);

-- 允许service role创建报告
CREATE POLICY "Service role can manage reports" ON analysis_reports
FOR ALL USING (true);

-- 为usage_logs表启用RLS
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;

-- 只允许用户查看自己的使用记录
CREATE POLICY "Users can view own usage logs" ON usage_logs
FOR SELECT USING (auth.uid() = user_id);

-- 允许service role记录使用情况
CREATE POLICY "Service role can insert usage logs" ON usage_logs
FOR INSERT WITH CHECK (true);