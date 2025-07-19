#!/bin/bash

# 智能专利分析系统自动化测试脚本
# 使用方法: ./test_system.sh

# set -e  # 遇到错误立即退出（暂时禁用以查看完整错误）

echo "========================================="
echo "智能专利分析系统自动化测试"
echo "========================================="

# 配置
API_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试结果计数
PASSED=0
FAILED=0

# 测试函数
test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    local headers=$5
    local expected_status=${6:-200}
    
    echo -n "测试 $name... "
    
    # 使用临时文件来分离响应体和状态码
    local tmp_body=$(mktemp)
    
    if [ -n "$headers" ]; then
        # 注意：这里需要正确处理带空格的headers参数
        status_code=$(curl -s -w "%{http_code}" -o "$tmp_body" -X $method "$url" -H "Content-Type: application/json" $headers -d "$data" 2>/dev/null)
    else
        status_code=$(curl -s -w "%{http_code}" -o "$tmp_body" -X $method "$url" -H "Content-Type: application/json" -d "$data" 2>/dev/null)
    fi
    
    body=$(cat "$tmp_body")
    rm -f "$tmp_body"
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ 通过${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ 失败${NC} (状态码: $status_code)"
        echo "  响应: $body"
        ((FAILED++))
        return 1
    fi
}

# 1. 检查服务状态
echo -e "\n${YELLOW}1. 检查服务状态${NC}"
test_endpoint "API健康检查" "GET" "$API_URL/" ""

# 检查前端
echo -n "测试 前端服务... "
frontend_status=$(curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL)
if [ "$frontend_status" = "200" ]; then
    echo -e "${GREEN}✓ 通过${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ 失败${NC} (状态码: $frontend_status)"
    ((FAILED++))
fi

# 2. 测试数据库连接
echo -e "\n${YELLOW}2. 测试数据库连接${NC}"
test_endpoint "Supabase连接" "GET" "$API_URL/api/test-supabase" ""

# 3. 测试API集成
echo -e "\n${YELLOW}3. 测试外部API集成${NC}"
test_endpoint "SERP API" "GET" "$API_URL/api/test-serp" ""
test_endpoint "Gemini API" "GET" "$API_URL/api/test-gemini" ""

# 4. 测试用户认证流程
echo -e "\n${YELLOW}4. 测试用户认证流程${NC}"

# 生成测试用户信息
TEST_EMAIL="test_$(date +%s)@example.com"
TEST_PASSWORD="TestPassword123!"
TEST_NAME="Test User $(date +%s)"

# 注册新用户
register_data="{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"full_name\":\"$TEST_NAME\"}"
echo -n "测试 用户注册... "
register_response=$(curl -s -X POST "$API_URL/api/auth/register" -H "Content-Type: application/json" -d "$register_data")
if echo "$register_response" | grep -q "user_id"; then
    echo -e "${GREEN}✓ 通过${NC}"
    ((PASSED++))
    USER_ID=$(echo "$register_response" | jq -r '.user_id')
    echo "  用户ID: $USER_ID"
else
    echo -e "${RED}✗ 失败${NC}"
    echo "  响应: $register_response"
    ((FAILED++))
fi

# 用户登录
login_data="{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}"
echo -n "测试 用户登录... "
login_response=$(curl -s -X POST "$API_URL/api/auth/login" -H "Content-Type: application/json" -d "$login_data")
if echo "$login_response" | grep -q "access_token"; then
    echo -e "${GREEN}✓ 通过${NC}"
    ((PASSED++))
    TOKEN=$(echo "$login_response" | jq -r '.access_token')
    echo "  Token: ${TOKEN:0:20}..."
else
    echo -e "${RED}✗ 失败${NC}"
    echo "  响应: $login_response"
    ((FAILED++))
fi

# 5. 测试专利分析功能
echo -e "\n${YELLOW}5. 测试专利分析功能${NC}"

if [ -n "$TOKEN" ] && [ -n "$USER_ID" ]; then
    # 创建分析
    analysis_data="{
        \"title\":\"智能健康监测手环\",
        \"description\":\"一种集成多种传感器的智能健康监测设备\",
        \"technical_field\":\"可穿戴设备、健康监测、物联网\",
        \"technical_content\":\"本发明涉及一种智能健康监测手环，包括心率传感器、血氧传感器、加速度计、陀螺仪等。通过AI算法分析用户健康数据，提供个性化健康建议。\",
        \"user_id\":\"$USER_ID\"
    }"
    
    test_endpoint "创建专利分析" "POST" "$API_URL/api/analyses" "$analysis_data" "-H \"Authorization: Bearer $TOKEN\""
    
    # 注意：完整的专利分析可能需要较长时间，这里只测试创建
    echo -e "${YELLOW}  注意：完整的专利分析需要调用analyze-patent端点，可能需要10-30秒${NC}"
fi

# 6. 测试结果汇总
echo -e "\n${YELLOW}=========================================${NC}"
echo -e "${YELLOW}测试结果汇总${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo -e "通过测试: ${GREEN}$PASSED${NC}"
echo -e "失败测试: ${RED}$FAILED${NC}"
echo -e "总计测试: $((PASSED + FAILED))"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}所有测试通过！系统运行正常。${NC}"
    exit 0
else
    echo -e "\n${RED}有 $FAILED 个测试失败，请检查系统配置。${NC}"
    exit 1
fi