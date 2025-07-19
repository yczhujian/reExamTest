"""Supabase客户端模块"""
from supabase import create_client, Client
from typing import Optional, Dict, Any, List
import os
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(dotenv_path="../.env.local")

logger = logging.getLogger(__name__)

class SupabaseDB:
    """Supabase数据库操作封装类"""
    
    def __init__(self):
        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            raise ValueError("Supabase URL和Service Role Key必须配置")
        
        self.client: Client = create_client(url, key)
    
    # ========== 专利分析相关 ==========
    
    async def create_analysis(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新的专利分析"""
        try:
            result = self.client.table("patent_analyses").insert({
                "user_id": user_id,
                "title": data.get("title"),
                "description": data.get("description"),
                "status": "pending",
                "metadata": data.get("metadata", {})
            }).execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"创建分析失败: {e}")
            raise
    
    async def get_analysis(self, analysis_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """获取分析详情"""
        try:
            query = self.client.table("patent_analyses").select("*").eq("id", analysis_id)
            
            if user_id:
                query = query.eq("user_id", user_id)
            
            result = query.execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"获取分析失败: {e}")
            raise
    
    async def update_analysis_status(self, analysis_id: str, status: str, error_message: Optional[str] = None):
        """更新分析状态"""
        try:
            update_data = {"status": status}
            if error_message:
                update_data["error_message"] = error_message
            
            result = self.client.table("patent_analyses").update(update_data).eq("id", analysis_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"更新分析状态失败: {e}")
            raise
    
    async def list_user_analyses(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """获取用户的分析列表"""
        try:
            result = self.client.table("patent_analyses")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .offset(offset)\
                .execute()
            
            return result.data
        except Exception as e:
            logger.error(f"获取分析列表失败: {e}")
            raise
    
    # ========== 搜索缓存相关 ==========
    
    async def get_cached_search(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """获取缓存的搜索结果"""
        try:
            result = self.client.table("search_cache")\
                .select("*")\
                .eq("query_hash", query_hash)\
                .gt("expires_at", datetime.utcnow().isoformat())\
                .execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"获取搜索缓存失败: {e}")
            return None
    
    async def cache_search_result(self, query_hash: str, query_text: str, results: Dict[str, Any], 
                                source: str, cache_hours: int = 24):
        """缓存搜索结果"""
        try:
            expires_at = datetime.utcnow() + timedelta(hours=cache_hours)
            
            result = self.client.table("search_cache").upsert({
                "query_hash": query_hash,
                "query_text": query_text,
                "results": results,
                "source": source,
                "expires_at": expires_at.isoformat()
            }).execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"缓存搜索结果失败: {e}")
            raise
    
    # ========== 使用量记录相关 ==========
    
    async def log_usage(self, user_id: str, analysis_id: Optional[str], service: str, 
                       tokens_used: Optional[int] = None, cost: Optional[float] = None):
        """记录API使用量"""
        try:
            usage_data = {
                "user_id": user_id,
                "service": service,
                "metadata": {}
            }
            
            if analysis_id:
                usage_data["analysis_id"] = analysis_id
            if tokens_used:
                usage_data["tokens_used"] = tokens_used
            if cost:
                usage_data["cost"] = cost
            
            result = self.client.table("usage_logs").insert(usage_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"记录使用量失败: {e}")
            raise
    
    async def get_user_usage_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """获取用户使用量汇总"""
        try:
            start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            result = self.client.table("usage_logs")\
                .select("service, tokens_used, cost")\
                .eq("user_id", user_id)\
                .gte("created_at", start_date)\
                .execute()
            
            # 汇总数据
            summary = {
                "total_cost": 0,
                "total_tokens": 0,
                "by_service": {}
            }
            
            for record in result.data:
                service = record["service"]
                if service not in summary["by_service"]:
                    summary["by_service"][service] = {"cost": 0, "tokens": 0, "calls": 0}
                
                summary["by_service"][service]["calls"] += 1
                if record["cost"]:
                    summary["total_cost"] += record["cost"]
                    summary["by_service"][service]["cost"] += record["cost"]
                if record["tokens_used"]:
                    summary["total_tokens"] += record["tokens_used"]
                    summary["by_service"][service]["tokens"] += record["tokens_used"]
            
            return summary
        except Exception as e:
            logger.error(f"获取使用量汇总失败: {e}")
            raise
    
    # ========== 文件存储相关 ==========
    
    async def upload_file(self, bucket: str, file_path: str, file_data: bytes, 
                         content_type: str = "application/octet-stream") -> str:
        """上传文件到Storage"""
        try:
            result = self.client.storage.from_(bucket).upload(
                file_path,
                file_data,
                {"content-type": content_type}
            )
            
            # 获取公开URL
            public_url = self.client.storage.from_(bucket).get_public_url(file_path)
            return public_url
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            raise
    
    async def download_file(self, bucket: str, file_path: str) -> bytes:
        """从Storage下载文件"""
        try:
            result = self.client.storage.from_(bucket).download(file_path)
            return result
        except Exception as e:
            logger.error(f"文件下载失败: {e}")
            raise
    
    async def delete_file(self, bucket: str, file_path: str):
        """删除Storage中的文件"""
        try:
            result = self.client.storage.from_(bucket).remove([file_path])
            return result
        except Exception as e:
            logger.error(f"文件删除失败: {e}")
            raise
    
    # ========== 分析报告相关 ==========
    
    async def save_analysis_report(self, analysis_id: str, report_type: str, 
                                 content: Dict[str, Any], score: Optional[float] = None):
        """保存分析报告"""
        try:
            report_data = {
                "analysis_id": analysis_id,
                "report_type": report_type,
                "content": content
            }
            
            if score is not None:
                report_data["score"] = score
            
            # 计算摘要
            if "summary" in content:
                report_data["summary"] = content["summary"]
            
            result = self.client.table("analysis_reports").upsert(report_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"保存分析报告失败: {e}")
            raise
    
    async def get_analysis_reports(self, analysis_id: str) -> List[Dict[str, Any]]:
        """获取分析的所有报告"""
        try:
            result = self.client.table("analysis_reports")\
                .select("*")\
                .eq("analysis_id", analysis_id)\
                .execute()
            
            return result.data
        except Exception as e:
            logger.error(f"获取分析报告失败: {e}")
            raise

# 创建全局实例
db = SupabaseDB()