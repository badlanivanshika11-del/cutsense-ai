import os
import time
import ssl
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

class EditingSegment(BaseModel):
    timestamp_start: str = Field(description="Start time, e.g., 00:05")
    timestamp_end: str = Field(description="End time, e.g., 00:08")
    editing_type: str = Field(description="Cut, Transition, Zoom, B-roll, Text Overlay, SFX Drop, etc.")
    description: str = Field(description="Detailed explanation of what editing technique was used.")
    engagement_impact: str = Field(description="Why this keeps the viewer engaged.")
    tutorial_query: str = Field(description="Search query to learn this edit in Premiere Pro, CapCut, or After Effects, e.g., 'How to do overhead hand swipe transition tutorial'")

class VideoAnalysisReport(BaseModel):
    pacing_rating: str = Field(description="Fast-paced, Moderate, or Slow")
    estimated_cuts_per_minute: int
    thumbnail_analysis: str = Field(description="Analysis of thumbnail appeal, contrast, and clickability.")
    script_hook_evaluation: str = Field(description="How strong the first 10-15 seconds hook is.")
    top_engagement_drivers: list[str] = Field(description="Key elements driving high viewer retention.")
    timeline: list[EditingSegment]

def analyze_video_with_gemini(video_file_path: str, api_key: str = None) -> VideoAnalysisReport:
    """Uploads video to Gemini API with automatic retry, tutorial links, and model fallback for high demand spikes."""
    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        client = genai.Client()
    
    print("Uploading video file to Gemini API...")
    uploaded_file = client.files.upload(file=video_file_path)
    
    while uploaded_file.state.name == "PROCESSING":
        time.sleep(3)
        uploaded_file = client.files.get(name=uploaded_file.name)
        
    if uploaded_file.state.name == "FAILED":
        raise ValueError("Video processing failed on Gemini API.")
        
    prompt = """
    You are an expert YouTube Video Editor and Audience Retention Analyst.
    Analyze this video in detail and provide:
    1. A breakdown of editing techniques used (cuts, transitions, text overlays, zooms, sound drops).
    2. An assessment of pacing, script hook (first 10-15s), thumbnail appeal, and engagement drivers.
    3. Timestamped breakdown of major visual transitions and key edit moments.
    4. For each edit segment, provide a specific tutorial_query (e.g., 'How to do overhead hand swipe transition Premiere Pro CapCut') so editors can learn to recreate it.
    """
    
    # Fallback models in case of 503 high demand spikes
    models_to_try = ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite"]
    last_error = None
    
    for model_name in models_to_try:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[uploaded_file, prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=VideoAnalysisReport,
                    )
                )
                return VideoAnalysisReport.model_validate_json(response.text)
            except Exception as e:
                last_error = e
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    time.sleep(2)
                    continue
                else:
                    break

    raise Exception(f"Gemini API Error after retries: {str(last_error)}")
