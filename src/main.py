from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import json
from pipeline import get_troubleshooting_plan, decode_image_and_troubleshoot
import time
import os

app = FastAPI(
    title="Smart Guided Troubleshooting Engine",
    description="Theme 2 - PRISM Hackathon",
    version="2.0.0"
)

# Ensure static directory exists
os.makedirs("public", exist_ok=True)
app.mount("/static", StaticFiles(directory="public"), name="static")

class TroubleshootRequest(BaseModel):
    query: str
    siis_response: Optional[str] = None

@app.post("/v1/troubleshoot")
async def troubleshoot(req: TroubleshootRequest):
    """
    POST /v1/troubleshoot
    Takes customer complaint and returns rich structured troubleshooting steps.
    """
    try:
        result = get_troubleshooting_plan(req.query, req.siis_response)
        return result
    except Exception as e:
        return {
            "error": str(e),
            "contexts": []
        }

@app.post("/v1/troubleshoot-image")
async def troubleshoot_image(
    image: UploadFile = File(...),
    notes: Optional[str] = Form(None)
):
    """
    POST /v1/troubleshoot-image
    Decodes error code or visual symptoms from an uploaded image & generates scratch solution.
    """
    try:
        contents = await image.read()
        mime_type = image.content_type or "image/jpeg"
        result = decode_image_and_troubleshoot(contents, mime_type, notes)
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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
os.makedirs(PUBLIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=PUBLIC_DIR), name="static")

@app.get("/")
async def root():
    """Serve minimalist Web UI"""
    index_path = os.path.join(PUBLIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "service": "Smart Guided Troubleshooting Engine",
        "theme": "Theme 2 - PRISM GenAI Hackathon 3rd Edition",
        "endpoints": {
            "POST /v1/troubleshoot": "Get text troubleshooting steps",
            "POST /v1/troubleshoot-image": "Decode error image & get scratch steps",
            "GET /health": "Health check"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)