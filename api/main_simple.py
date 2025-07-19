from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../.env.local")

# Initialize FastAPI app
app = FastAPI(title="Patent Analysis API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
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

# Health check endpoint
@app.get("/")
async def health_check():
    return {
        "status": "healthy", 
        "service": "Patent Analysis API",
        "message": "API is running. Some features are being installed."
    }

# Create new analysis (mock for now)
@app.post("/api/analyses", response_model=AnalysisResponse)
async def create_analysis(request: AnalysisRequest):
    # Mock response while dependencies are being installed
    import uuid
    analysis_id = str(uuid.uuid4())
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="pending",
        message="Analysis created successfully (mock mode)"
    )

# Test endpoint
@app.get("/api/test")
async def test_endpoint():
    return {
        "supabase_url": os.getenv("NEXT_PUBLIC_SUPABASE_URL", "Not set"),
        "gemini_key": "Set" if os.getenv("GEMINI_API_KEY") else "Not set",
        "serp_key": "Set" if os.getenv("SERPAPI_KEY") else "Not set",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)