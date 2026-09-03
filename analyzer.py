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
    tutorial_title: str = Field(description="Title of the best tutorial to learn this technique.")
    tutorial_query: str = Field(description="Search phrase to find the specific #1 tutorial video for this edit.")
    quick_step_guide: str = Field(description="Brief 3-step guide on how to recreate this edit in Premiere Pro/CapCut.")

class VideoAnalysisReport(BaseModel):
    virality_score_out_of_100: int = Field(description="Overall virality and viewer retention score out of 100.")
    why_it_got_views_and_likes: str = Field(description="Detailed explanation of why this video generated high views, likes, and watch time.")
    comment_section_triggers: str = Field(description="Specific moments, debates, or skits in the video that drove high comment engagement.")
    thumbnail_title_synergy: str = Field(description="How the thumbnail and title work together to generate massive click-through rate (CTR).")
    pacing_rating: str = Field(description="Fast-paced, Moderate, or Slow")
    estimated_cuts_per_minute: int
    thumbnail_analysis: str = Field(description="Analysis of thumbnail appeal, contrast, and clickability.")
    script_hook_evaluation: str = Field(description="How strong the first 10-15 seconds hook is.")
    top_engagement_drivers: list[str] = Field(description="Key elements driving high viewer retention.")
    timeline: list[EditingSegment]

def analyze_video_with_gemini(video_file_path: str, api_key: str = None) -> VideoAnalysisReport:
    """Uploads video to Gemini API and analyzes editing, virality, comments, and specific tutorial links."""
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
    You are an expert YouTube & Instagram Algorithm Specialist, Video Editor, and Audience Retention Analyst.
    Perform an in-depth analysis of this video:
    1. Virality & Engagement Mechanics: Explain in detail WHY this video got high attention, views, likes, and comments. Analyze curiosity gaps, pattern interrupts, and storytelling.
    2. Comment Section Drivers: Identify specific moments or questions that drove viewers to write comments.
    3. Thumbnail & Title Synergy: Evaluate how the thumbnail and title work together for maximum CTR.
    4. Editing & Transition Timeline: For every major edit timestamp, provide the technique, engagement impact, a recommended tutorial title, a specific YouTube search query to open the #1 tutorial video, and a 3-step quick guide to recreate it.
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
