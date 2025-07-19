#!/bin/bash

# Supabase Edge Functions 部署脚本

echo "======================================"
echo "部署 Supabase Edge Functions"
echo "======================================"

# 检查是否安装了 Supabase CLI
if ! command -v supabase &> /dev/null; then
    echo "错误：未安装 Supabase CLI"
    echo "请运行: brew install supabase/tap/supabase"
    exit 1
fi

# 设置项目ID
PROJECT_ID="grjslrfvlarfslgtoeqi"

echo "1. 登录 Supabase..."
supabase login

echo "2. 链接到项目..."
supabase link --project-ref $PROJECT_ID

echo "3. 设置环境变量..."
supabase secrets set GEMINI_API_KEY="AIzaSyCCjQkj3PVIM1F6KtFJu5gkIMqcADj1xfY"
supabase secrets set SERPAPI_KEY="672387e8385873e2a499ade2cc2ac0064fbfca0664ee89f206c54d1d04c3c63f"

echo "4. 部署 Edge Functions..."
# 部署分析专利函数
supabase functions deploy analyze-patent

# 部署创建分析函数
supabase functions deploy create-analysis

# 部署获取分析列表函数
supabase functions deploy get-analyses

echo "5. 获取函数URL..."
echo ""
echo "Edge Functions 已部署到："
echo "- 分析专利: https://$PROJECT_ID.supabase.co/functions/v1/analyze-patent"
echo "- 创建分析: https://$PROJECT_ID.supabase.co/functions/v1/create-analysis"
echo "- 获取分析: https://$PROJECT_ID.supabase.co/functions/v1/get-analyses"
echo ""
echo "部署完成！"