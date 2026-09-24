from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import json
from pipeline import get_troubleshooting_plan
import time
import os

app = FastAPI(
    title="Smart Guided Troubleshooting Engine",
    description="Theme 2 - PRISM Hackathon",
    version="1.0.0"
)

class TroubleshootRequest(BaseModel):
    query: str
    siis_response: Optional[str] = None

@app.post("/v1/troubleshoot")
async def troubleshoot(req: TroubleshootRequest):
    """
    POST /v1/troubleshoot
    
    Takes a vague customer complaint and returns structured troubleshooting steps.
    
    Example:
    {
      "query": "screen flickers and battery dies fast",
      "siis_response": "optional context from SIIS"
    }
    """
    try:
        result = get_troubleshooting_plan(req.query, req.siis_response)
        return result
    except Exception as e:
        return {
            "error": str(e),
            "contexts": []
        }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "troubleshoot-engine"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Smart Guided Troubleshooting Engine",
        "theme": "Theme 2 - PRISM GenAI Hackathon 3rd Edition",
        "endpoints": {
            "POST /v1/troubleshoot": "Get troubleshooting steps",
            "GET /health": "Health check",
            "GET /docs": "Interactive API docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)