import os
import time
import ssl
import urllib.parse
import yt_dlp
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
    tutorial_youtube_url: str = Field(description="Direct YouTube video URL to the top-viewed tutorial for this edit.")
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

def fetch_top_viewed_tutorial_video(editing_type: str) -> dict:
    """Locates the #1 top-viewed tutorial video on YouTube for a specific edit technique."""
    query = f"ytsearch1:How to do {editing_type} tutorial Premiere Pro CapCut"
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'nocheckcertificate': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            res = ydl.extract_info(query, download=False)
            if res and 'entries' in res and len(res['entries']) > 0:
                top = res['entries'][0]
                video_id = top.get('id')
                title = top.get('title') or f"How to do {editing_type} Tutorial"
                if video_id:
                    return {
                        "title": title,
                        "url": f"https://www.youtube.com/watch?v={video_id}"
                    }
    except Exception:
        pass
        
    encoded = urllib.parse.quote(f"How to do {editing_type} tutorial")
    return {
        "title": f"How to do {editing_type} Tutorial (Most Viewed)",
        "url": f"https://www.youtube.com/results?search_query={encoded}&sp=CAM%253D" # Sorted by View Count
    }

def analyze_video_with_gemini(video_file_path: str, api_key: str = None) -> VideoAnalysisReport:
    """Uploads video to Gemini API, generates report, and resolves direct top-viewed tutorial videos for every edit."""
    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        client = genai.Client()
    
    print("Uploading video file to Gemini API...")
    uploaded_file = client.files.upload(file=video_file_path)
    
    while uploaded_file.state.name == "PROCESSING":
        time.sleep(1.5)
        uploaded_file = client.files.get(name=uploaded_file.name)
        
    if uploaded_file.state.name == "FAILED":
        raise ValueError("Video processing failed on Gemini API.")
        
    prompt = """
    You are an expert YouTube & Instagram Algorithm Specialist and Video Editor.
    Analyze this video rapidly:
    1. Virality Mechanics: Why this video got high views, likes, and watch time.
    2. Comment Section Drivers: Specific moments driving comments.
    3. Thumbnail & Title Synergy: CTR evaluation.
    4. Editing Timeline: For each edit segment, provide technique & engagement impact and a 3-step quick guide.
    """
    
    models_to_try = ["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.7-flash"]
    last_error = None
    report = None
    
    for model_name in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[uploaded_file, prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=VideoAnalysisReport,
                    )
                )
                report = VideoAnalysisReport.model_validate_json(response.text)
                break
            except Exception as e:
                last_error = e
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    time.sleep(1.5)
                    continue
                else:
                    break
        if report:
            break

    if not report:
        raise Exception(f"Gemini API Error: {str(last_error)}")

    # Resolve direct top-viewed YouTube video URLs for every edit segment
    for item in report.timeline:
        top_vid = fetch_top_viewed_tutorial_video(item.editing_type)
        item.tutorial_title = top_vid["title"]
        item.tutorial_youtube_url = top_vid["url"]

    return report
