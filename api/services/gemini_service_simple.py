"""简化版Gemini API服务模块"""
import os
from typing import Dict, Any, List, Optional
import logging
import requests
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class GeminiService:
    """Gemini API服务封装（使用REST API）"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY必须配置")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    def _make_request(self, prompt: str) -> Dict[str, Any]:
        """发送请求到Gemini API"""
        headers = {
            "Content-Type": "application/json",
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        url = f"{self.base_url}?key={self.api_key}"
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API请求失败: {e}")
            raise
    
    def generate_content(self, prompt: str) -> str:
        """生成内容的简单方法"""
        try:
            response = self._make_request(prompt)
            # 提取生成的文本
            if "candidates" in response and response["candidates"]:
                content = response["candidates"][0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    return parts[0].get("text", "")
            return ""
        except Exception as e:
            logger.error(f"内容生成失败: {e}")
            raise
    
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
            {self._format_prior_art(prior_art[:5])}
            
            请从以下方面进行分析：
            1. 技术特征对比
            2. 区别技术特征识别
            3. 新颖性评估（高/中/低）
            4. 新颖性破坏风险
            5. 改进建议
            
            请以JSON格式返回分析结果。
            """
            
            response_text = self.generate_content(prompt)
            result = self._parse_response(response_text)
            
            return {
                "analysis": result,
                "score": 0.75,  # 简化评分
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
            
            请从以下方面进行创造性分析：
            1. 最接近的现有技术
            2. 发明实际解决的技术问题
            3. 技术方案的非显而易见性
            4. 技术效果的突出性
            5. 创造性评估（高/中/低）
            
            请以JSON格式返回分析结果。
            """
            
            response_text = self.generate_content(prompt)
            result = self._parse_response(response_text)
            
            return {
                "analysis": result,
                "score": 0.7,  # 简化评分
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
            
            response_text = self.generate_content(prompt)
            result = self._parse_response(response_text)
            
            return {
                "analysis": result,
                "score": 0.85,  # 简化评分
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"实用性分析失败: {e}")
            raise
    
    async def generate_patent_report(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成专利分析报告"""
        try:
            prompt = f"""
            基于以下专利分析结果，生成一份简洁的专利分析报告摘要。
            
            新颖性得分：{analysis_results.get('novelty', {}).get('score', 0)}
            创造性得分：{analysis_results.get('inventiveness', {}).get('score', 0)}
            实用性得分：{analysis_results.get('utility', {}).get('score', 0)}
            
            请生成包含执行摘要、主要发现和建议的报告。
            """
            
            response_text = self.generate_content(prompt)
            
            overall_score = (
                analysis_results.get('novelty', {}).get('score', 0) * 0.4 +
                analysis_results.get('inventiveness', {}).get('score', 0) * 0.4 +
                analysis_results.get('utility', {}).get('score', 0) * 0.2
            )
            
            return {
                "report": {"summary": response_text},
                "overall_score": overall_score,
                "recommendation": "建议申请专利" if overall_score > 0.6 else "建议改进后申请",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            raise
    
    def _format_prior_art(self, prior_art: List[Dict[str, Any]]) -> str:
        """格式化现有技术信息"""
        formatted = []
        for i, art in enumerate(prior_art, 1):
            formatted.append(f"{i}. {art.get('title', 'Unknown')}")
        return "\n".join(formatted)
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """解析响应"""
        try:
            return json.loads(response_text)
        except:
            return {"content": response_text}

# 创建全局实例
gemini = GeminiService()