from langgraph.graph import Graph, StateGraph
from typing import TypedDict, List, Dict, Any
import google.generativeai as genai
from serpapi import GoogleSearch
import os

# Define the state structure
class PatentAnalysisState(TypedDict):
    # Input
    title: str
    description: str
    technical_field: str
    technical_content: str
    
    # Processing states
    prior_art_searches: List[Dict[str, Any]]
    patent_searches: List[Dict[str, Any]]
    novelty_analysis: Dict[str, Any]
    inventiveness_analysis: Dict[str, Any]
    utility_analysis: Dict[str, Any]
    
    # Output
    final_report: Dict[str, Any]
    error: str

# Initialize Gemini model
model = genai.GenerativeModel('gemini-pro')

def search_prior_art(state: PatentAnalysisState) -> PatentAnalysisState:
    """Search for prior art using SERP API"""
    try:
        search_query = f"{state['technical_field']} {state['title']}"
        
        params = {
            "q": search_query,
            "api_key": os.getenv("SERPAPI_KEY"),
            "num": 10,
            "hl": "zh-cn",
            "gl": "cn"
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        state['prior_art_searches'] = results.get("organic_results", [])
    except Exception as e:
        state['error'] = f"Prior art search failed: {str(e)}"
    
    return state

def search_patents(state: PatentAnalysisState) -> PatentAnalysisState:
    """Search for related patents using Google Patents"""
    try:
        # For now, using SERP API with Google Patents
        search_query = f"site:patents.google.com {state['technical_field']} {state['title']}"
        
        params = {
            "q": search_query,
            "api_key": os.getenv("SERPAPI_KEY"),
            "num": 10
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        state['patent_searches'] = results.get("organic_results", [])
    except Exception as e:
        state['error'] = f"Patent search failed: {str(e)}"
    
    return state

def analyze_novelty(state: PatentAnalysisState) -> PatentAnalysisState:
    """Analyze novelty using Gemini"""
    try:
        prompt = f"""
        作为专利分析专家，请分析以下发明的新颖性：
        
        发明名称：{state['title']}
        技术领域：{state['technical_field']}
        技术内容：{state['technical_content']}
        
        已找到的现有技术：
        {[item['title'] for item in state['prior_art_searches'][:5]]}
        
        请从以下方面分析：
        1. 与现有技术的区别
        2. 新颖性破坏风险
        3. 建议的改进方向
        
        请用JSON格式返回分析结果。
        """
        
        response = model.generate_content(prompt)
        # Parse response and store analysis
        state['novelty_analysis'] = {
            "analysis": response.text,
            "score": 0.8  # TODO: Extract from response
        }
    except Exception as e:
        state['error'] = f"Novelty analysis failed: {str(e)}"
    
    return state

def analyze_inventiveness(state: PatentAnalysisState) -> PatentAnalysisState:
    """Analyze inventiveness using Gemini"""
    try:
        prompt = f"""
        作为专利分析专家，请分析以下发明的创造性：
        
        发明名称：{state['title']}
        技术内容：{state['technical_content']}
        新颖性分析：{state.get('novelty_analysis', {}).get('analysis', '')}
        
        请分析：
        1. 技术问题的识别
        2. 解决方案的非显而易见性
        3. 技术效果的突出性
        
        请用JSON格式返回分析结果。
        """
        
        response = model.generate_content(prompt)
        state['inventiveness_analysis'] = {
            "analysis": response.text,
            "score": 0.75
        }
    except Exception as e:
        state['error'] = f"Inventiveness analysis failed: {str(e)}"
    
    return state

def analyze_utility(state: PatentAnalysisState) -> PatentAnalysisState:
    """Analyze utility using Gemini"""
    try:
        prompt = f"""
        作为专利分析专家，请分析以下发明的实用性：
        
        发明名称：{state['title']}
        技术内容：{state['technical_content']}
        
        请分析：
        1. 工业应用可行性
        2. 技术方案完整性
        3. 实施难度评估
        
        请用JSON格式返回分析结果。
        """
        
        response = model.generate_content(prompt)
        state['utility_analysis'] = {
            "analysis": response.text,
            "score": 0.85
        }
    except Exception as e:
        state['error'] = f"Utility analysis failed: {str(e)}"
    
    return state

def generate_report(state: PatentAnalysisState) -> PatentAnalysisState:
    """Generate final comprehensive report"""
    try:
        prompt = f"""
        基于以下分析结果，生成专业的专利分析报告：
        
        发明信息：
        - 名称：{state['title']}
        - 领域：{state['technical_field']}
        
        分析结果：
        - 新颖性：{state.get('novelty_analysis', {}).get('score', 0)}
        - 创造性：{state.get('inventiveness_analysis', {}).get('score', 0)}
        - 实用性：{state.get('utility_analysis', {}).get('score', 0)}
        
        请生成包含执行摘要、详细分析、风险评估和建议的完整报告。
        """
        
        response = model.generate_content(prompt)
        state['final_report'] = {
            "summary": response.text,
            "overall_score": 0.8,
            "recommendation": "建议进行专利申请"
        }
    except Exception as e:
        state['error'] = f"Report generation failed: {str(e)}"
    
    return state

# Create the workflow graph
def create_patent_analysis_workflow():
    workflow = StateGraph(PatentAnalysisState)
    
    # Add nodes
    workflow.add_node("search_prior_art", search_prior_art)
    workflow.add_node("search_patents", search_patents)
    workflow.add_node("analyze_novelty", analyze_novelty)
    workflow.add_node("analyze_inventiveness", analyze_inventiveness)
    workflow.add_node("analyze_utility", analyze_utility)
    workflow.add_node("generate_report", generate_report)
    
    # Define edges
    workflow.set_entry_point("search_prior_art")
    workflow.add_edge("search_prior_art", "search_patents")
    workflow.add_edge("search_patents", "analyze_novelty")
    workflow.add_edge("analyze_novelty", "analyze_inventiveness")
    workflow.add_edge("analyze_inventiveness", "analyze_utility")
    workflow.add_edge("analyze_utility", "generate_report")
    
    return workflow.compile()

# Export the compiled workflow
patent_analysis_chain = create_patent_analysis_workflow()