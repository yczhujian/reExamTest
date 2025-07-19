# **产品需求文档（PRD）：智能专利分析系统**

## **第一部分：项目概述**

### **1.1 产品背景**

专利申请和评估是一个复杂且专业的过程，需要深入的技术分析、现有技术调研和法律评估。传统的专利分析依赖人工，耗时长、成本高，且容易遗漏重要信息。本产品通过集成Google Patent搜索和Gemini AI分析能力，实现专利性评估的自动化和智能化。

### **1.2 产品定位**

本产品定位为专业的专利分析SaaS平台，主要特点：
- **深度分析**：提供媲美专业专利代理人的分析深度和准确性
- **自动化调研**：通过SERP API自动搜索和分析现有技术
- **智能评估**：利用Gemini AI进行新颖性、创造性和实用性评估
- **专业报告**：生成符合专利法要求的专业评估报告

### **1.3 目标用户**

- **主要用户**：发明人、研发团队、初创企业
- **次要用户**：专利代理机构、知识产权部门
- **专业用户**：专利律师、技术转移办公室

## **第二部分：核心功能需求**

### **2.1 专利信息输入与管理**

#### **2.1.1 技术交底书管理**
- 技术交底书上传（支持多种格式：PDF、Word、Markdown）
- 结构化信息提取（技术领域、技术问题、技术方案）
- 版本管理与修订历史
- 多语言支持（中英文）

#### **2.1.2 发明信息录入**
- 发明名称与摘要
- 技术领域分类（IPC/CPC分类）
- 发明人信息管理
- 优先权信息

### **2.2 现有技术自动调研**

#### **2.2.1 专利搜索引擎**
- Google Patent API集成
- 多维度搜索（关键词、分类号、申请人、日期范围）
- 搜索策略优化（同义词扩展、引用分析）
- 搜索结果去重与排序

#### **2.2.2 非专利文献搜索**
- 学术论文搜索（Google Scholar）
- 技术标准检索
- 产品手册和技术文档
- 行业报告和白皮书

#### **2.2.3 现有技术分析**
- 技术特征提取与对比
- 相似度评分
- 技术演进路线分析
- 竞争对手技术布局

### **2.3 专利性智能评估**

#### **2.3.1 新颖性分析**
- 技术特征逐项对比
- 区别技术特征识别
- 新颖性破坏风险评估
- 引证文献标注

#### **2.3.2 创造性分析**
- 最接近现有技术确定
- 技术问题识别
- 显而易见性评估
- 技术效果分析

#### **2.3.3 实用性评估**
- 工业应用可行性
- 技术方案完整性
- 实施例充分性
- 技术效果可信度

### **2.4 专业报告生成**

#### **2.4.1 报告模板系统**
- 多种报告类型（专利性评估、FTO分析、技术趋势分析）
- 自定义报告结构
- 多语言报告生成
- 专业术语库

#### **2.4.2 报告内容生成**
- 基于模板的深度分析报告
- 图表自动生成（技术对比表、引证关系图）
- 法律条款引用
- 风险评估与建议

#### **2.4.3 报告质量控制**
- AI审核与优化
- 逻辑一致性检查
- 专业术语校验
- 引证准确性验证

### **2.5 工作流与协作**

#### **2.5.1 分析工作流**
- 专利分析流程管理
- 任务分配与进度跟踪
- 审核与批准流程
- 时限提醒

#### **2.5.2 团队协作**
- 多人协同编辑
- 评论与批注
- 变更追踪
- 知识共享

### **2.6 双模式分析系统**

#### **2.6.1 标准分析模式**
- **技术实现**：Supabase Edge Functions
- **响应时间**：1-2分钟
- **分析内容**：
  - 基础新颖性分析
  - 基础创造性分析
  - 基础实用性分析
  - 简要综合报告
- **适用场景**：初步评估、快速筛选

#### **2.6.2 高级分析模式（LangGraph）**
- **技术实现**：Python API + LangGraph 多代理系统
- **响应时间**：5-10分钟
- **分析内容**：
  - 深度新颖性分析（多维度对比）
  - 深度创造性分析（技术演进路径）
  - 深度实用性分析（产业应用评估）
  - 市场价值分析
  - 风险评估（侵权、技术、市场、法律）
  - 竞争态势分析
  - 专业综合报告
- **多代理系统**：
  - PatentSearchAgent（专利检索专家）
  - TechnicalAnalystAgent（技术分析专家）
  - MarketAnalystAgent（市场分析专家）
  - RiskAssessmentAgent（风险评估专家）
  - ReportGeneratorAgent（报告生成专家）
- **适用场景**：正式申请前评估、投资决策、技术转让

#### **2.6.3 模式选择策略**
- 自动检测可用服务
- 用户手动选择偏好
- 根据任务复杂度推荐
- 无缝切换和降级机制

## **第三部分：技术架构设计**

### **3.1 核心技术决策**

#### **3.1.1 框架选择：LangGraph**

**决策理由**：
- 专利分析需要复杂的多步骤工作流（搜索→分析→评估→报告）
- 需要条件分支（根据搜索结果决定下一步分析策略）
- 需要状态管理（保存中间分析结果）
- 需要循环处理（迭代搜索直到找到足够的现有技术）

**LangGraph优势**：
- 支持复杂的图结构工作流
- 内置状态管理机制
- 支持条件分支和循环
- 可视化工作流调试

#### **3.1.2 LLM选择：Google Gemini Pro**

**主模型**：Gemini Pro 1.5
- 超长上下文窗口（1M tokens）
- 优秀的多语言能力
- 成本效益高（$0.00125/$0.00375 per 1K tokens）
- 原生支持结构化输出

**辅助模型**：Gemini Flash
- 用于快速预处理和分类
- 响应速度快，成本更低
- 适合简单任务

### **3.2 专利分析工作流设计**

#### **3.2.1 LangGraph工作流架构**
```python
# 工作流节点定义
class PatentAnalysisGraph:
    nodes = {
        "input_parser": 解析技术交底书,
        "feature_extractor": 提取技术特征,
        "search_strategy": 生成搜索策略,
        "patent_searcher": 执行专利搜索,
        "prior_art_analyzer": 分析现有技术,
        "novelty_checker": 新颖性评估,
        "obviousness_checker": 创造性评估,
        "report_generator": 生成分析报告,
        "quality_controller": 质量审核
    }
    
    edges = [
        ("input_parser", "feature_extractor"),
        ("feature_extractor", "search_strategy"),
        ("search_strategy", "patent_searcher"),
        ("patent_searcher", "prior_art_analyzer"),
        ("prior_art_analyzer", "novelty_checker"),
        ("novelty_checker", "obviousness_checker"),
        ("obviousness_checker", "report_generator"),
        ("report_generator", "quality_controller")
    ]
    
    conditional_edges = {
        "patent_searcher": 如果结果不足则返回search_strategy,
        "quality_controller": 如果质量不达标则返回相应节点
    }
```

### **3.3 API集成架构**

#### **3.3.1 Google Patent搜索集成**
```python
# SERP API配置
SERP_CONFIG = {
    "api_key": "YOUR_SERP_API_KEY",
    "search_type": "google_patents",
    "params": {
        "num": 100,  # 每次搜索结果数
        "lang": "en",
        "sort": "relevance",
        "date_range": "custom"
    }
}

# 搜索策略
SEARCH_STRATEGIES = [
    "keyword_search",      # 关键词搜索
    "classification_search",  # IPC/CPC分类搜索
    "citation_search",     # 引用关系搜索
    "semantic_search"      # 语义相似搜索
]
```

#### **3.3.2 Gemini API集成**
```python
# Gemini配置
GEMINI_CONFIG = {
    "api_key": "YOUR_GEMINI_API_KEY",
    "model": "gemini-pro-1.5",
    "temperature": 0.1,  # 低温度保证分析一致性
    "max_tokens": 32000,
    "response_format": "structured"  # 结构化输出
}
```

### **3.4 前端技术栈**

#### **3.4.1 技术选择**

**框架**：Next.js 14 (App Router)
- 服务端渲染支持，提升首屏加载速度
- 内置API路由，便于前后端集成
- 优秀的开发体验和性能优化
- TypeScript原生支持

**UI组件库**：shadcn/ui + Tailwind CSS
- 现代化设计，可定制性强
- 轻量级，无运行时开销
- 完美支持暗色模式
- 组件可完全控制

**状态管理**：Zustand + TanStack Query
- 轻量级状态管理
- 强大的服务端状态同步
- 自动缓存和后台更新
- TypeScript友好

**专业组件**：
- **PDF查看器**：react-pdf
- **Markdown编辑器**：@uiw/react-md-editor
- **流程图**：reactflow
- **数据表格**：TanStack Table

### **3.5 后端技术栈**

#### **3.5.1 技术选择**

**主框架**：FastAPI (Python 3.11+)
- 原生异步支持，性能优秀
- 自动生成OpenAPI文档
- Pydantic数据验证
- LangGraph生态完美集成

**数据存储**：
- **主数据库**：PostgreSQL 15（结构化数据）
- **向量数据库**：Qdrant（专利文档向量存储）
- **缓存**：Redis（API响应缓存、任务队列）
- **对象存储**：MinIO（文档和报告存储）

**任务处理**：
- **任务队列**：Celery + Redis
- **定时任务**：Celery Beat
- **长时任务**：专利分析工作流

**API网关**：Kong
- 统一入口管理
- 限流和认证
- API版本管理

### **3.6 系统架构图**

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Client    │     │  Mobile Client  │     │    API Client   │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                        │
         └───────────────────────┴────────────────────────┘
                                 │
                        ┌────────▼────────┐
                        │   API Gateway   │
                        │     (Kong)      │
                        └────────┬────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌────────▼────────┐     ┌────────▼────────┐    ┌────────▼────────┐
│  Auth Service   │     │ Patent Analysis │    │ Report Service  │
│   (FastAPI)     │     │Service(LangGraph)│   │   (FastAPI)     │
└────────┬────────┘     └────────┬────────┘    └────────┬────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 │                               │
        ┌────────▼────────┐             ┌────────▼────────┐
        │   PostgreSQL    │             │     Qdrant      │
        │   (Main DB)     │             │  (Vector DB)    │
        └─────────────────┘             └─────────────────┘
                 │                               │
                 │      ┌─────────────────┐      │
                 └──────┤  Redis Cache    ├──────┘
                        └─────────────────┘
```

### **3.7 核心实现细节**

#### **3.7.1 LangGraph专利分析实现**
```python
from langgraph.graph import StateGraph, State
from typing import List, Dict, Any

class PatentAnalysisState(State):
    """专利分析状态管理"""
    invention_info: Dict[str, Any]
    technical_features: List[str]
    search_results: List[Dict]
    prior_art_analysis: Dict[str, Any]
    novelty_assessment: Dict[str, Any]
    obviousness_assessment: Dict[str, Any]
    final_report: str

# 构建分析图
graph = StateGraph(PatentAnalysisState)

# 添加节点
graph.add_node("parse_input", parse_invention_disclosure)
graph.add_node("extract_features", extract_technical_features)
graph.add_node("search_patents", search_google_patents)
graph.add_node("analyze_prior_art", analyze_with_gemini)
graph.add_node("assess_novelty", check_novelty)
graph.add_node("assess_obviousness", check_obviousness)
graph.add_node("generate_report", create_final_report)

# 定义边和条件
graph.add_edge("parse_input", "extract_features")
graph.add_edge("extract_features", "search_patents")
graph.add_conditional_edges(
    "search_patents",
    should_continue_search,
    {
        True: "search_patents",  # 继续搜索
        False: "analyze_prior_art"  # 进入分析
    }
)
```

#### **3.7.2 SERP API集成实现**
```python
import serpapi

class PatentSearcher:
    def __init__(self, api_key: str):
        self.client = serpapi.Client(api_key)
    
    async def search_patents(self, query: str, filters: Dict) -> List[Dict]:
        """执行专利搜索"""
        params = {
            "engine": "google_patents",
            "q": query,
            "num": 100,
            "before": filters.get("before_date"),
            "after": filters.get("after_date"),
            "assignee": filters.get("assignee"),
            "inventor": filters.get("inventor"),
            "cpc": filters.get("cpc_class")
        }
        
        results = await self.client.search(params)
        return self._parse_results(results)
    
    def _parse_results(self, raw_results: Dict) -> List[Dict]:
        """解析搜索结果"""
        patents = []
        for result in raw_results.get("organic_results", []):
            patents.append({
                "patent_id": result["patent_id"],
                "title": result["title"],
                "abstract": result["snippet"],
                "filing_date": result["filing_date"],
                "assignee": result.get("assignee"),
                "pdf_link": result.get("pdf")
            })
        return patents
```

#### **3.7.3 Gemini分析集成**
```python
import google.generativeai as genai

class PatentAnalyzer:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro-1.5')
    
    async def analyze_novelty(self, invention: Dict, prior_art: List[Dict]) -> Dict:
        """新颖性分析"""
        prompt = self._build_novelty_prompt(invention, prior_art)
        response = await self.model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        )
        return response.json()
    
    async def analyze_obviousness(self, invention: Dict, prior_art: List[Dict]) -> Dict:
        """创造性分析"""
        prompt = self._build_obviousness_prompt(invention, prior_art)
        response = await self.model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        )
        return response.json()
```

### **3.8 部署架构**

#### **3.8.1 推荐架构：Vercel + Railway**
- **前端托管**：Vercel
  - Next.js 优化
  - 全球 CDN
  - 自动 CI/CD
  - Edge Functions
- **Python API**：Railway
  - LangGraph 支持
  - 自动扩展
  - 持续部署
  - 无时间限制
- **数据库与服务**：Supabase
  - PostgreSQL + pgvector
  - 实时订阅
  - 认证系统
  - 文件存储

#### **3.8.2 备选架构：Vercel + Supabase**
- 全部使用 Supabase Edge Functions
- 适合快速原型和基础功能
- 成本更低但功能受限

## **第四部分：开发计划**

### **4.1 开发阶段**

#### **Phase 1: MVP版本（6-8周）**
- 基础技术交底书解析
- Google Patent搜索集成
- 简单的新颖性分析
- 基础报告生成
- 简单Web界面

**核心交付物**：
- 能够输入技术交底书并获得基础专利性评估
- 支持中英文专利搜索
- 生成简化版分析报告

#### **Phase 2: 专业版本（8-10周）**
- 完整的LangGraph工作流
- 深度专利分析能力
- 创造性和实用性评估
- 专业报告模板系统
- 用户管理和权限系统

**核心交付物**：
- 达到专业专利代理人水平的分析深度
- 支持复杂的多轮搜索策略
- 可定制的报告模板

#### **Phase 3: 企业版本（10-12周）**
- 团队协作功能
- API开放平台
- 批量分析能力
- 高级数据分析和可视化
- 性能优化和扩展

**核心交付物**：
- 支持企业级并发和性能要求
- 完整的API和集成能力
- 数据分析仪表板

### **4.2 团队配置**

| 角色 | 人数 | 核心职责 |
|-----|------|----------|
| **产品经理** | 1 | 专利分析流程设计、用户需求管理 |
| **技术架构师** | 1 | LangGraph架构设计、系统集成 |
| **AI工程师** | 2 | LangGraph实现、Gemini集成、提示工程 |
| **后端开发** | 2 | FastAPI开发、数据库设计、API集成 |
| **前端开发** | 2 | Next.js开发、UI/UX实现 |
| **专利顾问** | 1 | 专业指导、报告模板设计、质量把控 |
| **DevOps** | 1 | 部署自动化、监控告警 |

## **第五部分：风险评估与应对**

### **5.1 技术风险**

| 风险类型 | 描述 | 应对措施 |
|---------|------|---------|
| **分析准确性** | AI分析结果可能存在偏差 | 专利专家审核机制、持续优化提示词、建立反馈循环 |
| **API成本控制** | Gemini和SERP API成本高 | 智能缓存策略、相似查询复用、批量处理优化 |
| **搜索覆盖度** | 可能遗漏关键现有技术 | 多维度搜索策略、引文分析、语义扩展搜索 |
| **性能问题** | 深度分析耗时长 | 异步处理、进度可视化、分阶段交付结果 |
| **数据安全** | 专利信息高度敏感 | 端到端加密、访问控制、审计日志、数据脱敏 |

### **5.2 业务风险**

| 风险类型 | 描述 | 应对措施 |
|---------|------|---------|
| **法律责任** | 分析结果影响专利申请决策 | 明确免责声明、提供参考而非法律建议、建议专业复核 |
| **市场接受度** | 用户对AI分析信任度低 | 透明展示分析过程、提供引证来源、案例验证 |
| **竞争压力** | 传统专利代理机构抵制 | 定位为辅助工具、与代理机构合作、提供API集成 |
| **技术依赖** | 过度依赖Google服务 | 多搜索引擎支持、本地专利数据库、离线分析能力 |

## **第六部分：成功指标**

### **6.1 分析质量指标**
- 新颖性分析准确率 > 90%（与专业评估对比）
- 创造性评估准确率 > 85%
- 报告完整度评分 > 4.5/5
- 专利检索召回率 > 95%
- 误判率 < 5%

### **6.2 性能指标**
- 完整分析时间 < 10分钟（包含搜索和分析）
- API响应时间 < 500ms (P95)
- 系统可用性 > 99.9%
- 并发分析任务 > 100
- 报告生成时间 < 30秒

### **6.3 业务指标**
- 月分析报告数 > 10,000
- 用户满意度（NPS）> 70
- 专业用户占比 > 40%
- 付费转化率 > 15%
- 客户续费率 > 85%

### **6.4 成本效率指标**
- 单次分析成本 < $5
- API调用成本占比 < 40%
- 缓存命中率 > 60%
- 重复搜索节省率 > 70%

## **附录：专利分析系统详细规格**

### **A.1 支持的专利数据源**

| 数据源 | 覆盖范围 | 更新频率 | 特点 |
|--------|---------|----------|------|
| Google Patents | 全球120+国家 | 每周 | 覆盖最全、免费 |
| USPTO | 美国专利 | 每日 | 官方数据、最权威 |
| EPO | 欧洲专利 | 每周 | 多语言支持 |
| WIPO | PCT申请 | 每周 | 国际申请 |
| CNIPA | 中国专利 | 每日 | 中文专利 |

### **A.2 分析报告类型**

| 报告类型 | 分析深度 | 预计时长 | 适用场景 |
|---------|---------|----------|----------|
| **快速评估** | 基础 | 2-3分钟 | 初步筛选 |
| **标准分析** | 中等 | 5-8分钟 | 常规申请 |
| **深度分析** | 专业 | 10-15分钟 | 重要专利 |
| **FTO分析** | 全面 | 20-30分钟 | 产品上市 |
| **技术趋势** | 宏观 | 15-20分钟 | 战略规划 |

### **A.3 成本估算（优化后）**

| 项目 | 配置 | 月成本（USD） | 备注 |
|------|------|--------------|------|
| 云服务器 | 8核16G × 3台 | $600 | Kubernetes集群 |
| PostgreSQL | RDS 8核32G | $400 | 主从热备 |
| Qdrant | 向量数据库4核16G | $300 | 专利向量存储 |
| Redis | 8G集群 | $150 | 缓存和队列 |
| 对象存储 | 2TB | $100 | 报告和文档 |
| Gemini API | 2000万tokens | $50 | 批量优惠价 |
| SERP API | 10万次查询 | $500 | 企业套餐 |
| CDN | 2TB流量 | $150 | 全球分发 |
| **总计** | - | **$2,250** | 月1万次分析 |

### **A.4 竞争优势总结**

1. **技术优势**
   - LangGraph实现复杂工作流，分析深度超越简单AI工具
   - Gemini长上下文能力，可处理完整专利文档
   - 智能缓存系统，大幅降低API成本

2. **产品优势**
   - 分析深度达到专业专利代理人水平
   - 中英文双语支持，覆盖主要专利市场
   - 可定制报告模板，满足不同需求

3. **商业优势**
   - 分析成本仅为人工的1/20
   - 处理速度提升10倍以上
   - SaaS模式，易于规模化

---

**文档版本**：v3.0  
**更新日期**：2025-07-19  
**文档类型**：智能专利分析系统PRD
**下次评审**：2025-08-19

## **更新记录**

### v3.0 (2025-07-19)
- 新增双模式分析系统（标准模式/高级LangGraph模式）
- 添加多代理协作系统详细说明
- 更新部署架构（Vercel + Railway）
- 增加市场分析和风险评估功能

### v2.0 (2025-07-01)
- 初始版本发布