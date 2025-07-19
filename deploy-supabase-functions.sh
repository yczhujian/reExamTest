#!/bin/bash

# Supabase Functions 部署脚本
# 使用前请确保已安装 Supabase CLI 并完成登录

echo "🚀 开始部署 Supabase Edge Functions..."

# 检查是否已安装 Supabase CLI
if ! command -v supabase &> /dev/null
then
    echo "❌ 未找到 Supabase CLI，请先安装："
    echo "npm install -g supabase"
    exit 1
fi

# 项目 ID
PROJECT_ID="grjslrfvlarfslgtoeqi"

# 检查是否已登录
echo "📋 检查 Supabase 登录状态..."
if ! supabase projects list &> /dev/null
then
    echo "❌ 请先登录 Supabase："
    echo "supabase login"
    exit 1
fi

# 链接项目
echo "🔗 链接 Supabase 项目..."
supabase link --project-ref $PROJECT_ID

# 部署所有 Edge Functions
echo "📦 部署 Edge Functions..."

# 部署 analyze-patent 函数
echo "  - 部署 analyze-patent..."
supabase functions deploy analyze-patent

# 部署 create-analysis 函数
echo "  - 部署 create-analysis..."
supabase functions deploy create-analysis

# 部署 get-analyses 函数
echo "  - 部署 get-analyses..."
supabase functions deploy get-analyses

echo "✅ 所有 Edge Functions 部署完成！"
echo ""
echo "⚠️  重要提醒："
echo "1. 请在 Supabase 控制台设置以下环境变量："
echo "   - GEMINI_API_KEY"
echo "   - SERPAPI_KEY"
echo ""
echo "2. 设置路径："
echo "   项目控制台 → Edge Functions → 管理密钥"
echo ""
echo "3. 验证部署："
echo "   访问 https://supabase.com/dashboard/project/$PROJECT_ID/functions"