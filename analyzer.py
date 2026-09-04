import os
import time
import ssl
import urllib.parse
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
    editing_type: str = Field(description="Cut, Transition, Zoom, B-roll, Text Overlay, SFX Drop, Color Grade, Motion Graphic, etc.")
    description: str = Field(description="Detailed explanation of what editing technique was used.")
    engagement_impact: str = Field(description="Why this keeps the viewer engaged.")
    tutorial_title: str = Field(description="Title of the top tutorial to learn this technique.")
    tutorial_youtube_url: str = Field(description="Direct YouTube link to the #1 top-viewed tutorial video for this edit.")
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

def get_direct_top_viewed_tutorial_link(editing_type: str) -> dict:
    """Generates instant view-count sorted #1 tutorial video link."""
    clean_type = editing_type.strip()
    encoded_query = urllib.parse.quote(f"How to do {clean_type} tutorial Premiere Pro CapCut")
    # sp=CAM%253D on YouTube forces search results to be sorted strictly by View Count (#1 Most Viewed)
    view_count_sorted_url = f"https://www.youtube.com/results?search_query={encoded_query}&sp=CAM%253D"
    
    return {
        "title": f"How to do {clean_type} Tutorial (Most Viewed)",
        "url": view_count_sorted_url
    }

def analyze_video_with_gemini(video_file_path: str, api_key: str = None) -> VideoAnalysisReport:
    """Uploads video to Gemini API for high-speed analysis and granular 10-15 point edit detection."""
    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        client = genai.Client()
    
    print("Uploading video file to Gemini API...")
    uploaded_file = client.files.upload(file=video_file_path)
    
    while uploaded_file.state.name == "PROCESSING":
        time.sleep(1.0)
        uploaded_file = client.files.get(name=uploaded_file.name)
        
    if uploaded_file.state.name == "FAILED":
        raise ValueError("Video processing failed on Gemini API.")
        
    prompt = """
    You are an expert YouTube & Instagram Algorithm Specialist and Senior Master Video Editor.
    Analyze this video thoroughly and rapidly:

    CRITICAL INSTRUCTIONS FOR TIMELINE:
    - Extract a COMPREHENSIVE, DETAILED timeline of AT LEAST 8 to 15 granular editing techniques across the video.
    - Identify every major cut, transition (whip pan, zoom-in, hand-swipe, match cut), B-roll overlay, text popup, motion graphic animation, sound effect (SFX) drop, color grade shift, and speed ramp.
    - Do NOT omit edit segments. Be thorough from the intro hook (00:00) all the way to the outro.

    Provide:
    1. Virality Mechanics & Engagement: Why this video got high views, likes, and watch time.
    2. Comment Section Triggers: Specific debates, skits, or questions driving comments.
    3. Thumbnail & Title Synergy: CTR evaluation.
    4. Detailed 8-15 Segment Timeline: With techniques, retention impact, tutorial titles, and 3-step quick guides.
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
                    time.sleep(1.0)
                    continue
                else:
                    break
        if report:
            break

    if not report:
        raise Exception(f"Gemini API Error: {str(last_error)}")

    # Instantly generate view-count sorted #1 tutorial video links for every edit
    for item in report.timeline:
        top_vid = get_direct_top_viewed_tutorial_link(item.editing_type)
        if not item.tutorial_title:
            item.tutorial_title = top_vid["title"]
        if not item.tutorial_youtube_url or "search_query" not in item.tutorial_youtube_url:
            item.tutorial_youtube_url = top_vid["url"]

    return report
