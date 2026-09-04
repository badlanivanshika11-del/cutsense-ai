import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sys

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from downloader import download_video
from analyzer import analyze_video_with_gemini
from style_director import transfer_style_to_raw_video
from report_generator import generate_pdf_report, generate_csv_report

app = FastAPI(title="CutSense AI Custom API - Phase 2")

# Allow CORS for custom frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    url: str
    api_key: str = None

class StyleTransferRequest(BaseModel):
    reference_urls: list[str]
    raw_url: str
    api_key: str = None

@app.post("/api/analyze")
async def analyze_endpoint(request: AnalyzeRequest):
    """API endpoint to download and analyze video with Gemini AI."""
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
        
    api_key_to_use = request.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key_to_use:
        raise HTTPException(status_code=400, detail="Gemini API key is required")
        
    try:
        metadata = download_video(request.url)
        report = analyze_video_with_gemini(metadata["file_path"], api_key=api_key_to_use)
        
        return {
            "metadata": metadata,
            "report": report.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/style-transfer")
async def style_transfer_endpoint(request: StyleTransferRequest):
    """Phase 2 Endpoint: Transfers reference video style onto raw video clip."""
    if not request.reference_urls or not request.raw_url:
        raise HTTPException(status_code=400, detail="Reference URLs and Raw URL are required")
        
    api_key_to_use = request.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key_to_use:
        raise HTTPException(status_code=400, detail="Gemini API key is required")
        
    try:
        ref_paths = []
        for idx, rurl in enumerate(request.reference_urls):
            rmeta = download_video(rurl, output_dir=f"downloads/ref{idx}")
            ref_paths.append(rmeta["file_path"])
            
        raw_meta = download_video(request.raw_url, output_dir="downloads/raw")
        
        plan = transfer_style_to_raw_video(ref_paths, raw_meta["file_path"], api_key=api_key_to_use)
        
        return {
            "raw_metadata": raw_meta,
            "style_plan": plan.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static custom UI files
custom_ui_path = os.path.join(os.path.dirname(__file__), "custom_ui")
app.mount("/", StaticFiles(directory=custom_ui_path, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
