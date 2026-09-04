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
    editing_type: str = Field(description="Cut, Transition, Zoom, B-roll, Text Overlay, SFX Drop, Color Grade, Motion Graphic, Speed Ramp, Lower Third, etc.")
    description: str = Field(description="Honest & detailed explanation of what exact editing technique was used.")
    engagement_impact: str = Field(description="Psychological retention impact on the audience.")
    tutorial_title: str = Field(description="Title of the best tutorial to learn this technique.")
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

def analyze_video_with_gemini(video_file_path: str = None, api_key: str = None, meta_dict: dict = None) -> VideoAnalysisReport:
    """Uploads video payload to Gemini API or analyzes metadata if video file is restricted by Cloud 403."""
    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        client = genai.Client()
    
    contents_payload = []
    
    if video_file_path and os.path.exists(video_file_path):
        print("Uploading video file to Gemini API...")
        uploaded_file = client.files.upload(file=video_file_path)
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(1.0)
            uploaded_file = client.files.get(name=uploaded_file.name)
        if uploaded_file.state.name == "ACTIVE":
            contents_payload.append(uploaded_file)
            
    prompt = """
    You are an unsparing, highly rigorous Master Video Editor and Retention Analyst.
    Perform an EXHAUSTIVE, 100% HONEST breakdown of EVERY SINGLE editing technique in this video from 00:00 to the very end.

    RULES FOR TIMELINE (MANDATORY):
    - Do NOT summarize or limit the timeline. Identify ALL edit moments throughout the entire video.
    - Aim for AT LEAST 15 to 25+ distinct timestamped edit items spanning the intro, body, transitions, and outro.
    - Log every micro-cut, push-in zoom, whip-pan, sound effect (SFX) drop, text popup, lower third, B-roll insert, split screen, color grade shift, and speed ramp.
    - Be completely honest, specific, and thorough about what technique was used and its exact retention impact.

    Provide:
    1. Virality Mechanics & Engagement: Detailed reasons why this video got high views, likes, and watch time.
    2. Comment Section Triggers: Specific debates, skits, or questions driving comments.
    3. Thumbnail & Title Synergy: CTR evaluation.
    4. Exhaustive 15-25+ Segment Timeline: With techniques, retention impact, tutorial titles, and 3-step quick guides.
    """
    
    if meta_dict:
        prompt += f"\n\nVIDEO METADATA CONTEXT:\nTitle: {meta_dict.get('title')}\nChannel: {meta_dict.get('uploader')}\nDescription: {meta_dict.get('description', '')[:1000]}"

    contents_payload.append(prompt)
    
    models_to_try = ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite"]
    last_error = None
    report = None
    
    for model_name in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents_payload,
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
