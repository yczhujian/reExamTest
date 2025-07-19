"""
LangGraph 专利分析工作流
实现多代理协作的高级专利分析系统
"""
from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
import asyncio
import json
from datetime import datetime
from services.serp import SERPService
from services.gemini import GeminiService
from db.db import DB

# 定义工作流状态
class PatentAnalysisState(TypedDict):
    # 输入信息
    title: str
    description: str
    technical_field: str
    technical_content: str
    user_id: str
    analysis_id: str
    
    # 搜索结果
    patent_searches: List[Dict[str, Any]]
    academic_searches: List[Dict[str, Any]]
    market_searches: List[Dict[str, Any]]
    
    # 分析结果
    novelty_analysis: Dict[str, Any]
    inventiveness_analysis: Dict[str, Any]
    utility_analysis: Dict[str, Any]
    market_analysis: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    
    # 最终报告
    comprehensive_report: str
    overall_score: float
    recommendations: List[str]
    
    # 工作流控制
    current_step: str
    error: str
    progress: int

class PatentAnalysisWorkflow:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)
        self.serp_service = SERPService()
        self.gemini_service = GeminiService()
        self.db = DB()
        
        # 构建工作流图
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        # 创建工作流图
        workflow = StateGraph(PatentAnalysisState)
        
        # 添加节点
        workflow.add_node("patent_search", self.patent_search_node)
        workflow.add_node("academic_search", self.academic_search_node)
        workflow.add_node("market_search", self.market_search_node)
        workflow.add_node("novelty_analysis", self.novelty_analysis_node)
        workflow.add_node("inventiveness_analysis", self.inventiveness_analysis_node)
        workflow.add_node("utility_analysis", self.utility_analysis_node)
        workflow.add_node("market_analysis", self.market_analysis_node)
        workflow.add_node("risk_analysis", self.risk_analysis_node)
        workflow.add_node("generate_report", self.generate_report_node)
        workflow.add_node("save_results", self.save_results_node)
        
        # 设置入口点
        workflow.set_entry_point("patent_search")
        
        # 添加边（定义执行流程）
        # 并行搜索
        workflow.add_edge("patent_search", "academic_search")
        workflow.add_edge("academic_search", "market_search")
        
        # 分析阶段（依赖搜索结果）
        workflow.add_edge("market_search", "novelty_analysis")
        workflow.add_edge("novelty_analysis", "inventiveness_analysis")
        workflow.add_edge("inventiveness_analysis", "utility_analysis")
        workflow.add_edge("utility_analysis", "market_analysis")
        workflow.add_edge("market_analysis", "risk_analysis")
        
        # 生成报告
        workflow.add_edge("risk_analysis", "generate_report")
        workflow.add_edge("generate_report", "save_results")
        workflow.add_edge("save_results", END)
        
        return workflow.compile()
    
    async def patent_search_node(self, state: PatentAnalysisState) -> PatentAnalysisState:
        """专利搜索节点"""
        try:
            state["current_step"] = "patent_search"
            state["progress"] = 10
            
            # 使用多个关键词组合搜索
            search_queries = [
                state["title"],
                f"{state["technical_field"]} {state["title"]}",
                state["description"][:100]  # 使用描述的前100字符
            ]
            
            all_results = []
            for query in search_queries:
                results = await self.serp_service.search_patents(query)
                all_results.extend(results.get("organic_results", [])[:5])
            
            # 去重和排序
            seen = set()
            unique_results = []
            for result in all_results:
                if result.get("title") not in seen:
                    seen.add(result.get("title"))
                    unique_results.append(result)
            
            state["patent_searches"] = unique_results[:10]
            print(f"找到 {len(state['patent_searches'])} 个相关专利")
            
        except Exception as e:
            state["error"] = f"专利搜索失败: {str(e)}"
            print(f"Error in patent_search_node: {e}")
            
        return state
    
    async def academic_search_node(self, state: PatentAnalysisState) -> PatentAnalysisState:
        """学术文献搜索节点"""
        try:
            state["current_step"] = "academic_search"
            state["progress"] = 20
            
            # 搜索学术文献
            query = f"scholar:{state['technical_field']} {state['title']}"
            results = await self.serp_service.search(query, "scholar")
            
            state["academic_searches"] = results.get("organic_results", [])[:10]
            print(f"找到 {len(state['academic_searches'])} 篇相关学术文献")
            
        except Exception as e:
            state["error"] = f"学术搜索失败: {str(e)}"
            print(f"Error in academic_search_node: {e}")
            
        return state
    
    async def market_search_node(self, state: PatentAnalysisState) -> PatentAnalysisState:
        """市场信息搜索节点"""
        try:
            state["current_step"] = "market_search"
            state["progress"] = 30
            
            # 搜索市场信息
            query = f"{state['technical_field']} market analysis {state['title']} commercial"
            results = await self.serp_service.search(query)
            
            state["market_searches"] = results.get("organic_results", [])[:5]
            print(f"找到 {len(state['market_searches'])} 条市场信息")
            
        except Exception as e:
            state["error"] = f"市场搜索失败: {str(e)}"
            print(f"Error in market_search_node: {e}")
            
        return state
    
    async def novelty_analysis_node(self, state: PatentAnalysisState) -> PatentAnalysisState:
        """新颖性分析节点"""
        try:
            state["current_step"] = "novelty_analysis"
            state["progress"] = 40
            
            # 构建详细的分析提示
            prior_art = "\n".join([
                f"- {p.get('title', 'N/A')}: {p.get('snippet', 'N/A')}"
                for p in state["patent_searches"][:5]
            ])
            
            prompt = f"""作为专利审查专家，请对以下发明进行深入的新颖性分析：

发明标题：{state["title"]}
技术领域：{state["technical_field"]}
技术内容：{state["technical_content"]}

现有技术：
{prior_art}

请提供：
1. 详细的新颖性分析（300-500字）
2. 与每个现有技术的具体对比
3. 新颖性评分（0-100分）
4. 主要创新点列表
5. 潜在的新颖性风险

返回JSON格式：
{{
    "analysis": "详细分析内容",
    "comparisons": [
        {{"prior_art": "现有技术名称", "differences": "具体差异"}},
        ...
    ],
    "score": 85,
    "innovations": ["创新点1", "创新点2", ...],
    "risks": ["风险1", "风险2", ...]
}}"""
            
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            novelty_result = json.loads(response.content)
            
            state["novelty_analysis"] = novelty_result
            print(f"新颖性评分: {novelty_result['score']}")
            
        except Exception as e:
            state["error"] = f"新颖性分析失败: {str(e)}"
            print(f"Error in novelty_analysis_node: {e}")
            
        return state
    
    async def inventiveness_analysis_node(self, state: PatentAnalysisState) -> PatentAnalysisState:
        """创造性分析节点"""
        try:
            state["current_step"] = "inventiveness_analysis"
            state["progress"] = 50
            
            prompt = f"""基于新颖性分析结果，评估发明的创造性：

发明：{state["title"]}
新颖性得分：{state.get('novelty_analysis', {}).get('score', 0)}
主要创新点：{json.dumps(state.get('novelty_analysis', {}).get('innovations', []), ensure_ascii=False)}

请评估：
1. 技术方案的非显而易见性（300字）
2. 是否具有预料不到的技术效果
3. 解决的技术问题难度
4. 创造性评分（0-100分）
5. 创造性高度评价

返回JSON格式：
{{
    "analysis": "详细分析",
    "non_obvious_aspects": ["方面1", "方面2", ...],
    "unexpected_effects": ["效果1", "效果2", ...],
    "problem_difficulty": "高/中/低",
    "score": 80,
    "creativity_level": "突破性/显著/一般/较低"
}}"""
            
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            inventiveness_result = json.loads(response.content)
            
            state["inventiveness_analysis"] = inventiveness_result
            print(f"创造性评分: {inventiveness_result['score']}")
            
        except Exception as e:
            state["error"] = f"创造性分析失败: {str(e)}"
            print(f"Error in inventiveness_analysis_node: {e}")
            
        return state
    
    async def utility_analysis_node(self, state: PatentAnalysisState) -> PatentAnalysisState:
        """实用性分析节点"""
        try:
            state["current_step"] = "utility_analysis"
            state["progress"] = 60
            
            prompt = f"""评估发明的实用性和产业应用价值：

发明：{state["title"]}
技术内容：{state["technical_content"]}
技术领域：{state["technical_field"]}

请评估：
1. 产业化可行性分析（200字）
2. 解决的实际问题
3. 应用场景列表
4. 技术成熟度评估
5. 实用性评分（0-100分）

返回JSON格式：
{{
    "analysis": "详细分析",
    "industrial_feasibility": "高/中/低",
    "problems_solved": ["问题1", "问题2", ...],
    "application_scenarios": ["场景1", "场景2", ...],
    "technology_readiness_level": "1-9级",
    "score": 90
}}"""
            
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            utility_result = json.loads(response.content)
            
            state["utility_analysis"] = utility_result
            print(f"实用性评分: {utility_result['score']}")
            
        except Exception as e:
            state["error"] = f"实用性分析失败: {str(e)}"
            print(f"Error in utility_analysis_node: {e}")
            
        return state
    
    async def market_analysis_node(self, state: PatentAnalysisState) -> PatentAnalysisState:
        """市场分析节点"""
        try:
            state["current_step"] = "market_analysis"
            state["progress"] = 70
            
            market_info = "\n".join([
                f"- {m.get('title', 'N/A')}: {m.get('snippet', 'N/A')}"
                for m in state.get("market_searches", [])
            ])
            
            prompt = f"""进行专利的市场价值分析：

发明：{state["title"]}
技术领域：{state["technical_field"]}
应用场景：{json.dumps(state.get('utility_analysis', {}).get('application_scenarios', []), ensure_ascii=False)}

市场信息：
{market_info}

请分析：
1. 市场规模评估
2. 竞争态势分析
3. 商业化潜力
4. 目标客户群体
5. 市场价值评分（0-100分）

返回JSON格式：
{{
    "market_size": "市场规模描述",
    "competition_analysis": "竞争分析",
    "commercialization_potential": "高/中/低",
    "target_customers": ["客户群体1", "客户群体2", ...],
    "market_trends": ["趋势1", "趋势2", ...],
    "score": 75
}}"""
            
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            market_result = json.loads(response.content)
            
            state["market_analysis"] = market_result
            print(f"市场价值评分: {market_result['score']}")
            
        except Exception as e:
            state["error"] = f"市场分析失败: {str(e)}"
            print(f"Error in market_analysis_node: {e}")
            
        return state
    
    async def risk_analysis_node(self, state: PatentAnalysisState) -> PatentAnalysisState:
        """风险分析节点"""
        try:
            state["current_step"] = "risk_analysis"
            state["progress"] = 80
            
            prompt = f"""进行专利申请的风险评估：

发明：{state["title"]}
新颖性风险：{json.dumps(state.get('novelty_analysis', {}).get('risks', []), ensure_ascii=False)}
技术领域：{state["technical_field"]}

请评估：
1. 专利侵权风险
2. 技术实施风险
3. 市场风险
4. 法律风险
5. 综合风险等级

返回JSON格式：
{{
    "infringement_risks": [{{"risk": "风险描述", "severity": "高/中/低", "mitigation": "缓解措施"}}],
    "technical_risks": [{{"risk": "风险描述", "severity": "高/中/低", "mitigation": "缓解措施"}}],
    "market_risks": [{{"risk": "风险描述", "severity": "高/中/低", "mitigation": "缓解措施"}}],
    "legal_risks": [{{"risk": "风险描述", "severity": "高/中/低", "mitigation": "缓解措施"}}],
    "overall_risk_level": "高/中/低",
    "risk_score": 30
}}"""
            
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            risk_result = json.loads(response.content)
            
            state["risk_analysis"] = risk_result
            print(f"风险评分: {risk_result['risk_score']} (越低越好)")
            
        except Exception as e:
            state["error"] = f"风险分析失败: {str(e)}"
            print(f"Error in risk_analysis_node: {e}")
            
        return state
    
    async def generate_report_node(self, state: PatentAnalysisState) -> PatentAnalysisState:
        """生成综合报告节点"""
        try:
            state["current_step"] = "generate_report"
            state["progress"] = 90
            
            # 计算综合评分
            scores = [
                state.get("novelty_analysis", {}).get("score", 0),
                state.get("inventiveness_analysis", {}).get("score", 0),
                state.get("utility_analysis", {}).get("score", 0),
                state.get("market_analysis", {}).get("score", 0),
                100 - state.get("risk_analysis", {}).get("risk_score", 0)  # 风险分数反向计算
            ]
            
            overall_score = sum(scores) / len(scores)
            state["overall_score"] = overall_score
            
            # 生成建议
            recommendations = []
            
            if overall_score >= 80:
                recommendations.append("强烈建议提交专利申请")
                recommendations.append("该发明具有显著的创新性和市场价值")
            elif overall_score >= 60:
                recommendations.append("建议提交专利申请，但需关注以下方面")
                if state.get("novelty_analysis", {}).get("score", 0) < 70:
                    recommendations.append("建议进一步强化技术创新点")
                if state.get("market_analysis", {}).get("score", 0) < 70:
                    recommendations.append("建议深入研究市场定位")
            else:
                recommendations.append("建议暂缓专利申请")
                recommendations.append("需要进一步完善技术方案")
            
            # 添加具体建议
            if state.get("risk_analysis", {}).get("overall_risk_level") == "高":
                recommendations.append("建议进行专利侵权风险排查")
            
            state["recommendations"] = recommendations
            
            # 生成详细报告
            report = f"""# 专利分析综合报告

## 执行摘要
**发明名称**：{state["title"]}
**技术领域**：{state["technical_field"]}
**综合评分**：{overall_score:.1f}/100
**建议**：{recommendations[0]}

## 1. 新颖性分析（评分：{state.get("novelty_analysis", {}).get("score", 0)}/100）
{state.get("novelty_analysis", {}).get("analysis", "N/A")}

**主要创新点**：
{chr(10).join(f"- {inn}" for inn in state.get("novelty_analysis", {}).get("innovations", []))}

## 2. 创造性分析（评分：{state.get("inventiveness_analysis", {}).get("score", 0)}/100）
{state.get("inventiveness_analysis", {}).get("analysis", "N/A")}

**创造性水平**：{state.get("inventiveness_analysis", {}).get("creativity_level", "N/A")}

## 3. 实用性分析（评分：{state.get("utility_analysis", {}).get("score", 0)}/100）
{state.get("utility_analysis", {}).get("analysis", "N/A")}

**应用场景**：
{chr(10).join(f"- {app}" for app in state.get("utility_analysis", {}).get("application_scenarios", []))}

## 4. 市场分析（评分：{state.get("market_analysis", {}).get("score", 0)}/100）
**市场规模**：{state.get("market_analysis", {}).get("market_size", "N/A")}
**商业化潜力**：{state.get("market_analysis", {}).get("commercialization_potential", "N/A")}

## 5. 风险评估（风险分：{state.get("risk_analysis", {}).get("risk_score", 0)}/100）
**整体风险等级**：{state.get("risk_analysis", {}).get("overall_risk_level", "N/A")}

## 6. 综合建议
{chr(10).join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))}

---
*报告生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*分析引擎：LangGraph Advanced Patent Analysis System v1.0*
"""
            
            state["comprehensive_report"] = report
            print("综合报告生成完成")
            
        except Exception as e:
            state["error"] = f"报告生成失败: {str(e)}"
            print(f"Error in generate_report_node: {e}")
            
        return state
    
    async def save_results_node(self, state: PatentAnalysisState) -> PatentAnalysisState:
        """保存结果节点"""
        try:
            state["current_step"] = "save_results"
            state["progress"] = 100
            
            # 保存各项分析报告到数据库
            analysis_id = state["analysis_id"]
            
            # 保存新颖性报告
            await self.db.save_analysis_report(
                analysis_id=analysis_id,
                report_type="novelty",
                content=state.get("novelty_analysis", {}).get("analysis", ""),
                score=state.get("novelty_analysis", {}).get("score", 0),
                metadata=state.get("novelty_analysis", {})
            )
            
            # 保存创造性报告
            await self.db.save_analysis_report(
                analysis_id=analysis_id,
                report_type="inventiveness",
                content=state.get("inventiveness_analysis", {}).get("analysis", ""),
                score=state.get("inventiveness_analysis", {}).get("score", 0),
                metadata=state.get("inventiveness_analysis", {})
            )
            
            # 保存实用性报告
            await self.db.save_analysis_report(
                analysis_id=analysis_id,
                report_type="utility",
                content=state.get("utility_analysis", {}).get("analysis", ""),
                score=state.get("utility_analysis", {}).get("score", 0),
                metadata=state.get("utility_analysis", {})
            )
            
            # 保存市场分析报告
            await self.db.save_analysis_report(
                analysis_id=analysis_id,
                report_type="market",
                content=json.dumps(state.get("market_analysis", {}), ensure_ascii=False),
                score=state.get("market_analysis", {}).get("score", 0),
                metadata=state.get("market_analysis", {})
            )
            
            # 保存风险分析报告
            await self.db.save_analysis_report(
                analysis_id=analysis_id,
                report_type="risk",
                content=json.dumps(state.get("risk_analysis", {}), ensure_ascii=False),
                score=state.get("risk_analysis", {}).get("risk_score", 0),
                metadata=state.get("risk_analysis", {})
            )
            
            # 保存综合报告
            await self.db.save_analysis_report(
                analysis_id=analysis_id,
                report_type="comprehensive",
                content=state["comprehensive_report"],
                score=state["overall_score"],
                metadata={
                    "recommendations": state["recommendations"],
                    "overall_score": state["overall_score"]
                }
            )
            
            # 更新分析状态
            await self.db.update_analysis_status(
                analysis_id=analysis_id,
                status="completed",
                metadata={
                    "overall_score": state["overall_score"],
                    "completion_time": datetime.now().isoformat()
                }
            )
            
            print("所有结果已保存到数据库")
            
        except Exception as e:
            state["error"] = f"结果保存失败: {str(e)}"
            print(f"Error in save_results_node: {e}")
            
        return state
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """运行工作流"""
        try:
            # 初始化状态
            initial_state = PatentAnalysisState(
                title=input_data["title"],
                description=input_data["description"],
                technical_field=input_data["technical_field"],
                technical_content=input_data["technical_content"],
                user_id=input_data["user_id"],
                analysis_id=input_data["analysis_id"],
                patent_searches=[],
                academic_searches=[],
                market_searches=[],
                novelty_analysis={},
                inventiveness_analysis={},
                utility_analysis={},
                market_analysis={},
                risk_analysis={},
                comprehensive_report="",
                overall_score=0.0,
                recommendations=[],
                current_step="",
                error="",
                progress=0
            )
            
            # 运行工作流
            final_state = await self.workflow.ainvoke(initial_state)
            
            return {
                "success": not bool(final_state.get("error")),
                "analysis_id": final_state["analysis_id"],
                "overall_score": final_state["overall_score"],
                "recommendations": final_state["recommendations"],
                "error": final_state.get("error", ""),
                "progress": final_state["progress"]
            }
            
        except Exception as e:
            print(f"Workflow execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis_id": input_data.get("analysis_id", ""),
                "progress": 0
            }

# 创建工作流实例
patent_workflow = PatentAnalysisWorkflow()