"""Gemini API服务模块"""
import os
from typing import Dict, Any, List, Optional
import logging
import google.generativeai as genai
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class GeminiService:
    """Gemini API服务封装"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY必须配置")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def analyze_patent_novelty(self, invention_info: Dict[str, Any], 
                                   prior_art: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析专利新颖性"""
        try:
            prompt = f"""
            作为专利分析专家，请分析以下发明的新颖性。
            
            发明信息：
            - 名称：{invention_info.get('title', '')}
            - 技术领域：{invention_info.get('technical_field', '')}
            - 技术方案：{invention_info.get('technical_content', '')}
            
            现有技术：
            {self._format_prior_art(prior_art[:5])}  # 只使用前5个最相关的
            
            请从以下方面进行分析：
            1. 技术特征对比
            2. 区别技术特征识别
            3. 新颖性评估（高/中/低）
            4. 新颖性破坏风险
            5. 改进建议
            
            请以JSON格式返回分析结果。
            """
            
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            
            return {
                "analysis": result,
                "score": self._calculate_novelty_score(result),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"新颖性分析失败: {e}")
            raise
    
    async def analyze_patent_inventiveness(self, invention_info: Dict[str, Any],
                                         novelty_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分析专利创造性"""
        try:
            prompt = f"""
            作为专利分析专家，请分析以下发明的创造性。
            
            发明信息：
            - 名称：{invention_info.get('title', '')}
            - 技术领域：{invention_info.get('technical_field', '')}
            - 技术方案：{invention_info.get('technical_content', '')}
            
            新颖性分析结果：
            {json.dumps(novelty_analysis.get('analysis', {}), ensure_ascii=False, indent=2)}
            
            请从以下方面进行创造性分析：
            1. 最接近的现有技术
            2. 发明实际解决的技术问题
            3. 技术方案的非显而易见性
            4. 技术效果的突出性
            5. 创造性评估（高/中/低）
            
            请以JSON格式返回分析结果。
            """
            
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            
            return {
                "analysis": result,
                "score": self._calculate_inventiveness_score(result),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"创造性分析失败: {e}")
            raise
    
    async def analyze_patent_utility(self, invention_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析专利实用性"""
        try:
            prompt = f"""
            作为专利分析专家，请分析以下发明的实用性。
            
            发明信息：
            - 名称：{invention_info.get('title', '')}
            - 技术领域：{invention_info.get('technical_field', '')}
            - 技术方案：{invention_info.get('technical_content', '')}
            
            请从以下方面进行实用性分析：
            1. 工业应用可行性
            2. 技术方案的完整性
            3. 实施难度评估
            4. 预期技术效果
            5. 实用性评估（高/中/低）
            
            请以JSON格式返回分析结果。
            """
            
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            
            return {
                "analysis": result,
                "score": self._calculate_utility_score(result),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"实用性分析失败: {e}")
            raise
    
    async def generate_patent_report(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成专利分析报告"""
        try:
            prompt = f"""
            基于以下专利分析结果，生成一份专业的专利分析报告。
            
            分析结果：
            - 新颖性分析：{json.dumps(analysis_results.get('novelty', {}), ensure_ascii=False)}
            - 创造性分析：{json.dumps(analysis_results.get('inventiveness', {}), ensure_ascii=False)}
            - 实用性分析：{json.dumps(analysis_results.get('utility', {}), ensure_ascii=False)}
            
            请生成包含以下部分的报告：
            1. 执行摘要
            2. 技术背景
            3. 新颖性评估
            4. 创造性评估
            5. 实用性评估
            6. 风险分析
            7. 结论与建议
            
            报告应该专业、清晰、有说服力。请以JSON格式返回。
            """
            
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            
            return {
                "report": result,
                "overall_score": self._calculate_overall_score(analysis_results),
                "recommendation": self._generate_recommendation(analysis_results),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            raise
    
    async def extract_technical_features(self, document_text: str) -> List[Dict[str, Any]]:
        """从文档中提取技术特征"""
        try:
            prompt = f"""
            请从以下技术文档中提取关键技术特征。
            
            文档内容：
            {document_text[:3000]}  # 限制长度
            
            请提取：
            1. 技术问题
            2. 技术方案的关键特征
            3. 技术效果
            4. 创新点
            
            请以JSON格式返回，包含features数组。
            """
            
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            
            return result.get("features", [])
            
        except Exception as e:
            logger.error(f"技术特征提取失败: {e}")
            raise
    
    def _format_prior_art(self, prior_art: List[Dict[str, Any]]) -> str:
        """格式化现有技术信息"""
        formatted = []
        for i, art in enumerate(prior_art, 1):
            formatted.append(f"""
            {i}. {art.get('title', 'Unknown')}
            链接：{art.get('link', 'N/A')}
            摘要：{art.get('snippet', 'N/A')}
            """)
        return "\n".join(formatted)
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """解析Gemini响应，提取JSON"""
        try:
            # 尝试直接解析
            return json.loads(response_text)
        except json.JSONDecodeError:
            # 如果失败，尝试提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # 如果还是失败，返回原始文本
            return {"raw_response": response_text}
    
    def _calculate_novelty_score(self, analysis: Dict[str, Any]) -> float:
        """计算新颖性分数"""
        # 简化的评分逻辑，实际应该更复杂
        assessment = analysis.get("新颖性评估", "").lower()
        if "高" in assessment or "high" in assessment:
            return 0.9
        elif "中" in assessment or "medium" in assessment:
            return 0.6
        else:
            return 0.3
    
    def _calculate_inventiveness_score(self, analysis: Dict[str, Any]) -> float:
        """计算创造性分数"""
        assessment = analysis.get("创造性评估", "").lower()
        if "高" in assessment or "high" in assessment:
            return 0.85
        elif "中" in assessment or "medium" in assessment:
            return 0.5
        else:
            return 0.2
    
    def _calculate_utility_score(self, analysis: Dict[str, Any]) -> float:
        """计算实用性分数"""
        assessment = analysis.get("实用性评估", "").lower()
        if "高" in assessment or "high" in assessment:
            return 0.95
        elif "中" in assessment or "medium" in assessment:
            return 0.7
        else:
            return 0.4
    
    def _calculate_overall_score(self, analysis_results: Dict[str, Any]) -> float:
        """计算综合分数"""
        novelty_score = analysis_results.get("novelty", {}).get("score", 0)
        inventiveness_score = analysis_results.get("inventiveness", {}).get("score", 0)
        utility_score = analysis_results.get("utility", {}).get("score", 0)
        
        # 加权平均
        return (novelty_score * 0.4 + inventiveness_score * 0.4 + utility_score * 0.2)
    
    def _generate_recommendation(self, analysis_results: Dict[str, Any]) -> str:
        """生成建议"""
        overall_score = self._calculate_overall_score(analysis_results)
        
        if overall_score >= 0.7:
            return "强烈建议申请专利"
        elif overall_score >= 0.5:
            return "建议改进后申请专利"
        else:
            return "建议进一步研发后再考虑申请"

# 创建全局实例
gemini = GeminiService()