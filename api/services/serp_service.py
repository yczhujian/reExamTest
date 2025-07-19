"""SERP API服务模块"""
import os
from typing import Dict, Any, List, Optional
import logging
import hashlib
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

class SerpService:
    """SERP API服务封装"""
    
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_KEY必须配置")
        self.base_url = "https://serpapi.com/search"
    
    def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送请求到SERP API"""
        params["api_key"] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"SERP API请求失败: {e}")
            raise
    
    def search_patents(self, query: str, num_results: int = 10, 
                      location: str = "China", language: str = "zh-cn") -> List[Dict[str, Any]]:
        """搜索专利相关信息"""
        try:
            # 构建专利搜索查询
            patent_query = f"site:patents.google.com {query}"
            
            params = {
                "q": patent_query,
                "num": num_results,
                "hl": language,
                "gl": location.lower()[:2],  # 国家代码
                "engine": "google"
            }
            
            results = self._make_request(params)
            
            # 解析结果
            parsed_results = []
            for result in results.get("organic_results", []):
                parsed = {
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "position": result.get("position", 0)
                }
                
                # 尝试从URL提取专利号
                if "patents.google.com/patent/" in parsed["link"]:
                    patent_id = parsed["link"].split("/patent/")[1].split("/")[0]
                    parsed["patent_id"] = patent_id
                
                parsed_results.append(parsed)
            
            return parsed_results
            
        except Exception as e:
            logger.error(f"专利搜索失败: {e}")
            raise
    
    def search_prior_art(self, query: str, num_results: int = 20,
                        exclude_patents: bool = False) -> List[Dict[str, Any]]:
        """搜索现有技术（非专利文献）"""
        try:
            # 构建查询，可选择排除专利
            if exclude_patents:
                query = f"{query} -site:patents.google.com"
            
            params = {
                "q": query,
                "num": num_results,
                "hl": "zh-cn",
                "gl": "cn",
                "engine": "google"
            }
            
            results = self._make_request(params)
            
            # 解析结果
            parsed_results = []
            for result in results.get("organic_results", []):
                parsed = {
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "source": self._identify_source(result.get("link", "")),
                    "date": result.get("date", ""),
                    "position": result.get("position", 0)
                }
                parsed_results.append(parsed)
            
            return parsed_results
            
        except Exception as e:
            logger.error(f"现有技术搜索失败: {e}")
            raise
    
    def search_scholar(self, query: str, num_results: int = 10,
                      year_start: Optional[int] = None) -> List[Dict[str, Any]]:
        """搜索学术文献"""
        try:
            params = {
                "q": query,
                "num": num_results,
                "hl": "zh-cn",
                "engine": "google_scholar"
            }
            
            # 添加年份过滤
            if year_start:
                params["as_ylo"] = year_start
            
            results = self._make_request(params)
            
            # 解析学术结果
            parsed_results = []
            for result in results.get("organic_results", []):
                parsed = {
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "publication_info": result.get("publication_info", {}),
                    "authors": self._parse_authors(result.get("publication_info", {})),
                    "year": self._extract_year(result.get("publication_info", {})),
                    "cited_by": result.get("inline_links", {}).get("cited_by", {}).get("total", 0),
                    "position": result.get("position", 0)
                }
                parsed_results.append(parsed)
            
            return parsed_results
            
        except Exception as e:
            logger.error(f"学术搜索失败: {e}")
            raise
    
    def search_company_patents(self, company_name: str, num_results: int = 20) -> List[Dict[str, Any]]:
        """搜索特定公司的专利"""
        try:
            # 构建公司专利搜索查询
            query = f'site:patents.google.com "assignee:{company_name}"'
            
            params = {
                "q": query,
                "num": num_results,
                "hl": "zh-cn",
                "gl": "cn",
                "engine": "google"
            }
            
            results = self._make_request(params)
            
            # 解析结果
            parsed_results = []
            for result in results.get("organic_results", []):
                parsed = {
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "assignee": company_name,
                    "position": result.get("position", 0)
                }
                
                # 提取专利号
                if "patents.google.com/patent/" in parsed["link"]:
                    patent_id = parsed["link"].split("/patent/")[1].split("/")[0]
                    parsed["patent_id"] = patent_id
                
                parsed_results.append(parsed)
            
            return parsed_results
            
        except Exception as e:
            logger.error(f"公司专利搜索失败: {e}")
            raise
    
    def get_search_suggestions(self, query: str) -> List[str]:
        """获取搜索建议"""
        try:
            params = {
                "q": query,
                "engine": "google_autocomplete"
            }
            
            results = self._make_request(params)
            
            suggestions = []
            for suggestion in results.get("suggestions", []):
                suggestions.append(suggestion.get("value", ""))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"获取搜索建议失败: {e}")
            return []
    
    def _identify_source(self, url: str) -> str:
        """识别URL来源类型"""
        if "patents.google.com" in url:
            return "google_patents"
        elif "scholar.google.com" in url:
            return "google_scholar"
        elif "github.com" in url:
            return "github"
        elif "arxiv.org" in url:
            return "arxiv"
        elif any(domain in url for domain in [".edu", "university", "academic"]):
            return "academic"
        elif any(domain in url for domain in ["wikipedia", "baike.baidu"]):
            return "encyclopedia"
        else:
            return "web"
    
    def _parse_authors(self, publication_info: Dict) -> List[str]:
        """解析作者信息"""
        summary = publication_info.get("summary", "")
        if " - " in summary:
            authors_part = summary.split(" - ")[0]
            return [author.strip() for author in authors_part.split(",")]
        return []
    
    def _extract_year(self, publication_info: Dict) -> Optional[int]:
        """提取发表年份"""
        summary = publication_info.get("summary", "")
        import re
        year_match = re.search(r"\b(19|20)\d{2}\b", summary)
        if year_match:
            return int(year_match.group())
        return None

# 创建全局实例
serp = SerpService()