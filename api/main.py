from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv
from db import db
from services import serp, gemini, auth
import hashlib
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
# Try to load from .env.local if it exists (for local development)
if os.path.exists("../.env.local"):
    load_dotenv(dotenv_path="../.env.local")
else:
    # In production, environment variables should be set directly
    logger.info("No .env.local file found, using environment variables")

# Initialize FastAPI app
app = FastAPI(title="Patent Analysis API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3002", "https://*.vercel.app", "https://*.railway.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class AnalysisRequest(BaseModel):
    title: str
    description: str
    technical_field: str
    technical_content: str
    user_id: str

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str

class SearchRequest(BaseModel):
    query: str
    source: str = "serp"  # serp, google_patent, scholar
    user_id: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# OAuth2 配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# 获取当前用户的依赖
async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = await auth.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Patent Analysis API", 
        "version": "2.0.0",
        "features": ["standard_analysis", "advanced_analysis_langgraph"]
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Patent Analysis API",
        "version": "1.0.1",
        "supabase": "connected"
    }

# Create new analysis
@app.post("/api/analyses", response_model=AnalysisResponse)
async def create_analysis(request: AnalysisRequest):
    try:
        # 创建分析记录
        analysis = await db.create_analysis(
            user_id=request.user_id,
            data={
                "title": request.title,
                "description": request.description,
                "metadata": {
                    "technical_field": request.technical_field,
                    "technical_content": request.technical_content
                }
            }
        )
        
        if not analysis:
            raise HTTPException(status_code=500, detail="Failed to create analysis")
        
        # TODO: 触发后台分析任务
        
        return AnalysisResponse(
            analysis_id=analysis["id"],
            status=analysis["status"],
            message="Analysis created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get analysis status
@app.get("/api/analyses/{analysis_id}")
async def get_analysis(analysis_id: str, user_id: Optional[str] = None):
    try:
        analysis = await db.get_analysis(analysis_id, user_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # 获取相关报告
        reports = await db.get_analysis_reports(analysis_id)
        analysis["reports"] = reports
        
        return analysis
    except Exception as e:
        logger.error(f"Error getting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# List user analyses
@app.get("/api/analyses")
async def list_analyses(user_id: str, limit: int = 20, offset: int = 0):
    try:
        analyses = await db.list_user_analyses(user_id, limit, offset)
        return {
            "data": analyses,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error listing analyses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Search with caching
@app.post("/api/search")
async def search_with_cache(request: SearchRequest):
    try:
        # 生成查询哈希
        query_hash = hashlib.md5(f"{request.query}:{request.source}".encode()).hexdigest()
        
        # 检查缓存
        cached = await db.get_cached_search(query_hash)
        if cached:
            logger.info(f"返回缓存的搜索结果: {query_hash}")
            return {
                "results": cached["results"],
                "cached": True
            }
        
        # 执行实际搜索
        results = None
        if request.source == "google_patent":
            results = serp.search_patents(request.query)
        elif request.source == "scholar":
            results = serp.search_scholar(request.query)
        else:  # 默认使用常规搜索
            results = serp.search_prior_art(request.query)
        
        search_results = {
            "query": request.query,
            "source": request.source,
            "results": results,
            "count": len(results)
        }
        
        # 缓存结果
        await db.cache_search_result(
            query_hash=query_hash,
            query_text=request.query,
            results=search_results,
            source=request.source
        )
        
        # 记录使用量
        await db.log_usage(
            user_id=request.user_id,
            analysis_id=None,
            service=request.source,
            cost=0.01  # SERP API成本
        )
        
        return {
            "results": search_results,
            "cached": False
        }
    except Exception as e:
        logger.error(f"Error in search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# File upload endpoint
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), user_id: str = None):
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID required")
        
        # 读取文件内容
        contents = await file.read()
        
        # 生成文件路径
        file_path = f"uploads/{user_id}/{file.filename}"
        
        # 上传到Supabase Storage
        public_url = await db.upload_file(
            bucket="documents",
            file_path=file_path,
            file_data=contents,
            content_type=file.content_type or "application/octet-stream"
        )
        
        return {
            "filename": file.filename,
            "url": public_url,
            "size": len(contents)
        }
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Usage statistics endpoint
@app.get("/api/usage/{user_id}")
async def get_usage_stats(user_id: str, days: int = 30):
    try:
        summary = await db.get_user_usage_summary(user_id, days)
        return summary
    except Exception as e:
        logger.error(f"Error getting usage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Test Supabase connection
@app.get("/api/test-supabase")
async def test_supabase():
    try:
        # 尝试查询一条记录来测试连接
        result = db.client.table("patent_analyses").select("id").limit(1).execute()
        return {
            "status": "success",
            "message": "Supabase connection successful",
            "test_query": "Executed successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Test SERP API
@app.get("/api/test-serp")
async def test_serp_api():
    try:
        # 测试专利搜索
        results = serp.search_patents("battery technology", num_results=3)
        return {
            "status": "success",
            "message": "SERP API connection successful",
            "sample_results": results[:2] if results else [],
            "total_found": len(results)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Test Gemini API
@app.get("/api/test-gemini")
async def test_gemini_api():
    try:
        # 测试文本生成
        response = gemini.generate_content("Hello, please respond with: 'Gemini API is working!'")
        return {
            "status": "success",
            "message": "Gemini API connection successful",
            "response": response
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Full patent analysis endpoint
@app.post("/api/analyze-patent")
async def analyze_patent(request: AnalysisRequest):
    try:
        # 1. 创建分析记录
        analysis = await db.create_analysis(
            user_id=request.user_id,
            data={
                "title": request.title,
                "description": request.description,
                "metadata": {
                    "technical_field": request.technical_field,
                    "technical_content": request.technical_content
                }
            }
        )
        
        analysis_id = analysis["id"]
        
        # 2. 搜索现有技术
        logger.info(f"开始搜索现有技术: {request.title}")
        prior_art = serp.search_prior_art(f"{request.technical_field} {request.title}", num_results=10)
        patents = serp.search_patents(request.title, num_results=5)
        
        # 3. 进行新颖性分析
        logger.info("开始新颖性分析")
        novelty_result = await gemini.analyze_patent_novelty(
            {
                "title": request.title,
                "technical_field": request.technical_field,
                "technical_content": request.technical_content
            },
            prior_art + patents
        )
        
        # 保存新颖性分析结果
        await db.save_analysis_report(
            analysis_id=analysis_id,
            report_type="novelty",
            content=novelty_result["analysis"],
            score=novelty_result["score"]
        )
        
        # 4. 进行创造性分析
        logger.info("开始创造性分析")
        inventiveness_result = await gemini.analyze_patent_inventiveness(
            {
                "title": request.title,
                "technical_field": request.technical_field,
                "technical_content": request.technical_content
            },
            novelty_result
        )
        
        # 保存创造性分析结果
        await db.save_analysis_report(
            analysis_id=analysis_id,
            report_type="inventiveness",
            content=inventiveness_result["analysis"],
            score=inventiveness_result["score"]
        )
        
        # 5. 进行实用性分析
        logger.info("开始实用性分析")
        utility_result = await gemini.analyze_patent_utility({
            "title": request.title,
            "technical_field": request.technical_field,
            "technical_content": request.technical_content
        })
        
        # 保存实用性分析结果
        await db.save_analysis_report(
            analysis_id=analysis_id,
            report_type="utility",
            content=utility_result["analysis"],
            score=utility_result["score"]
        )
        
        # 6. 生成综合报告
        logger.info("生成综合报告")
        final_report = await gemini.generate_patent_report({
            "novelty": novelty_result,
            "inventiveness": inventiveness_result,
            "utility": utility_result
        })
        
        # 保存综合报告
        await db.save_analysis_report(
            analysis_id=analysis_id,
            report_type="comprehensive",
            content=final_report["report"],
            score=final_report["overall_score"]
        )
        
        # 更新分析状态
        await db.update_analysis_status(analysis_id, "completed")
        
        # 记录使用量
        await db.log_usage(
            user_id=request.user_id,
            analysis_id=analysis_id,
            service="gemini",
            tokens_used=1000,  # 估算
            cost=0.05  # 估算成本
        )
        
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "overall_score": final_report["overall_score"],
            "recommendation": final_report["recommendation"],
            "message": "Patent analysis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"专利分析失败: {e}")
        if 'analysis_id' in locals():
            await db.update_analysis_status(analysis_id, "failed", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Advanced patent analysis with LangGraph
@app.post("/api/analyze-patent-advanced")
async def analyze_patent_advanced(request: AnalysisRequest):
    """使用 LangGraph 进行高级专利分析"""
    try:
        # 1. 创建分析记录
        analysis = await db.create_analysis(
            user_id=request.user_id,
            data={
                "title": request.title,
                "description": request.description,
                "metadata": {
                    "technical_field": request.technical_field,
                    "technical_content": request.technical_content,
                    "analysis_mode": "advanced"
                }
            }
        )
        
        analysis_id = analysis["id"]
        
        # 2. 使用 LangGraph 工作流
        logger.info(f"启动 LangGraph 高级分析: {request.title}")
        
        # 导入 LangGraph 工作流
        from workflows.langgraph_analysis import patent_workflow
        
        # 异步运行工作流
        import asyncio
        asyncio.create_task(patent_workflow.run({
            "title": request.title,
            "description": request.description,
            "technical_field": request.technical_field,
            "technical_content": request.technical_content,
            "user_id": request.user_id,
            "analysis_id": analysis_id
        }))
        
        return {
            "analysis_id": analysis_id,
            "status": "processing",
            "message": "高级专利分析已启动，请通过进度接口查询状态"
        }
        
    except Exception as e:
        logger.error(f"高级分析启动失败: {e}")
        if 'analysis_id' in locals():
            await db.update_analysis_status(analysis_id, "failed", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Get analysis progress
@app.get("/api/analysis/{analysis_id}/progress")
async def get_analysis_progress(analysis_id: str):
    """获取分析进度"""
    try:
        # 从数据库获取分析状态
        analysis = await db.get_analysis(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="分析不存在")
        
        # 获取已完成的报告
        reports = await db.get_analysis_reports(analysis_id)
        
        # 计算进度
        total_steps = 5  # 新颖性、创造性、实用性、市场、风险
        completed_steps = len([r for r in reports if r["report_type"] != "comprehensive"])
        progress = int((completed_steps / total_steps) * 100)
        
        return {
            "analysis_id": analysis_id,
            "status": analysis["status"],
            "progress": progress,
            "current_step": analysis.get("metadata", {}).get("current_step", ""),
            "completed_reports": [r["report_type"] for r in reports]
        }
        
    except Exception as e:
        logger.error(f"获取进度失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========== 认证相关端点 ==========

# 用户注册
@app.post("/api/auth/register")
async def register(user_data: UserRegister):
    try:
        result = await auth.register_user(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        
        if result["success"]:
            return {
                "user_id": result["user_id"],
                "email": result["email"],
                "message": result["message"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        logger.error(f"注册失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请重试"
        )

# 用户登录
class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: LoginRequest):
    try:
        result = await auth.login_user(
            email=form_data.email,
            password=form_data.password
        )
        
        if result["success"]:
            return {
                "access_token": result["access_token"],
                "token_type": result["token_type"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"],
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        logger.error(f"登录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请重试"
        )

# 获取当前用户信息
@app.get("/api/auth/me")
async def get_me(current_user: Dict = Depends(get_current_user)):
    return current_user

# 用户登出
@app.post("/api/auth/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    try:
        await auth.logout_user(token)
        return {"message": "登出成功"}
    except Exception as e:
        logger.error(f"登出失败: {e}")
        return {"message": "登出失败"}

# 请求重置密码
@app.post("/api/auth/reset-password-request")
async def reset_password_request(email: EmailStr):
    try:
        result = await auth.reset_password_request(email)
        return result
    except Exception as e:
        logger.error(f"重置密码请求失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送重置邮件失败"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)