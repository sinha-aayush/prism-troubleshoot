from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# API Endpoints
@app.post("/v1/troubleshoot")
async def troubleshoot(req: TroubleshootRequest):
    """
    POST /v1/troubleshoot
    Takes a vague customer complaint and returns structured troubleshooting steps.
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
    """Serve the HTML frontend"""
    return FileResponse('static/index.html')

# Serve static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)