#!/bin/bash

# 快速测试脚本 - 用于验证RLS禁用后的系统功能
# 使用方法: ./quick_test.sh

echo "======================================"
echo "专利分析系统快速测试"
echo "======================================"
echo ""
echo "请确保已在Supabase中禁用RLS！"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 生成唯一的测试邮箱
TEST_EMAIL="quick_test_$(date +%s)@example.com"
TEST_PASSWORD="QuickTest123"

echo -e "${YELLOW}1. 创建测试用户${NC}"
echo "   邮箱: $TEST_EMAIL"

# 注册
REGISTER_RESP=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"full_name\":\"Quick Test\"}")

if echo "$REGISTER_RESP" | grep -q "user_id"; then
    USER_ID=$(echo $REGISTER_RESP | jq -r '.user_id')
    echo -e "   ${GREEN}✓ 注册成功${NC}"
    echo "   用户ID: $USER_ID"
else
    echo -e "   ${RED}✗ 注册失败${NC}"
    echo "   错误: $REGISTER_RESP"
    exit 1
fi

# 登录
echo -e "\n${YELLOW}2. 用户登录${NC}"
LOGIN_RESP=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

if echo "$LOGIN_RESP" | grep -q "access_token"; then
    TOKEN=$(echo $LOGIN_RESP | jq -r '.access_token')
    echo -e "   ${GREEN}✓ 登录成功${NC}"
else
    echo -e "   ${RED}✗ 登录失败${NC}"
    echo "   错误: $LOGIN_RESP"
    exit 1
fi

# 执行专利分析
echo -e "\n${YELLOW}3. 执行专利分析${NC}"
echo "   正在分析专利，请稍候（可能需要10-30秒）..."

START_TIME=$(date +%s)

ANALYSIS_RESP=$(curl -s -X POST http://localhost:8000/api/analyze-patent \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"title\": \"智能交通管理系统\",
    \"description\": \"基于AI的城市交通流量优化系统\",
    \"technical_field\": \"人工智能、交通管理、物联网\",
    \"technical_content\": \"本发明涉及一种智能交通管理系统，通过部署在路口的传感器收集实时交通数据，使用深度学习算法预测交通流量，动态调整信号灯时序，优化城市交通流量，减少拥堵。\",
    \"user_id\": \"$USER_ID\"
  }")

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
if echo "$ANALYSIS_RESP" | grep -q "analysis_id"; then
    echo -e "   ${GREEN}✓ 分析完成！${NC}"
    echo "   耗时: ${DURATION}秒"
    echo ""
    echo "   分析结果:"
    echo "$ANALYSIS_RESP" | jq '{
        analysis_id: .analysis_id,
        status: .status,
        overall_score: .overall_score,
        recommendation: .recommendation | .[0:100] + "..."
    }'
    
    # 获取分析ID
    ANALYSIS_ID=$(echo $ANALYSIS_RESP | jq -r '.analysis_id')
    
    # 查看分析详情
    echo -e "\n${YELLOW}4. 查看分析详情${NC}"
    DETAIL_RESP=$(curl -s -X GET "http://localhost:8000/api/analyses/$ANALYSIS_ID" \
      -H "Authorization: Bearer $TOKEN")
    
    echo "$DETAIL_RESP" | jq '{
        id: .id,
        title: .title,
        status: .status,
        created_at: .created_at,
        reports_count: .reports | length
    }'
    
    echo -e "\n${GREEN}======================================"
    echo -e "测试成功！系统运行正常。"
    echo -e "======================================${NC}"
    
else
    echo -e "   ${RED}✗ 分析失败${NC}"
    echo "   错误信息:"
    echo "$ANALYSIS_RESP" | jq
    
    echo -e "\n${RED}======================================"
    echo -e "测试失败！"
    echo -e "请确保已在Supabase中禁用RLS。"
    echo -e "======================================${NC}"
    exit 1
fi