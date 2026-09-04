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

class ClipSlot(BaseModel):
    clip_number: int = Field(description="Clip slot index, e.g., 1, 2, 3")
    recommended_duration_seconds: str = Field(description="Ideal duration for this short clip slot, e.g., '3-5 seconds'")
    clip_purpose: str = Field(description="Purpose of this clip, e.g., 'Intro Retention Hook', 'Talking Head Explanation', 'Action B-Roll'")
    what_raw_clip_to_insert: str = Field(description="Exact instruction on which short raw video clip/part to place here.")
    transition_to_next_clip: str = Field(description="Transition effect to connect to the next clip slot.")
    copy_paste_text_popup: str = Field(description="Pre-designed text content to overlay on this clip.")
    recommended_sfx_drop: str = Field(description="Exact SFX sound drop for this clip slot.")
    how_to_assemble_in_mobile_apps: str = Field(description="Step-by-step assembly for CapCut / VN / InShot.")
    how_to_assemble_in_desktop_apps: str = Field(description="Step-by-step assembly for Premiere Pro / DaVinci Resolve / Final Cut.")

class StyleTransferPlan(BaseModel):
    template_name: str = Field(description="Name given to this editing style template, e.g., 'Viral Fast-Paced Reel Template'")
    recommended_editing_app: str = Field(description="Best editing app suited for this style (CapCut, VN, Premiere Pro, DaVinci Resolve, InShot, Final Cut Pro, or After Effects) with clear reasoning.")
    alternative_apps: list[str] = Field(description="Alternative supported editing software options.")
    difficulty_level: str = Field(description="Beginner, Intermediate, or Advanced")
    overall_editing_vibe: str = Field(description="Summary of the visual aesthetic transferred from reference videos.")
    suggested_background_music: str = Field(description="Type of background music genre & bpm to use.")
    modular_clip_template: list[ClipSlot]

def transfer_style_to_raw_video(reference_video_paths: list[str], raw_video_path: str = None, api_key: str = None) -> StyleTransferPlan:
    """Analyzes reference video style + user's raw video file to build a modular clip-by-clip editing template."""
    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        client = genai.Client()

    uploaded_files = []
    
    print("Uploading video files for style transfer...")
    for path in reference_video_paths:
        if path and os.path.exists(path):
            uf = client.files.upload(file=path)
            uploaded_files.append(uf)

    if raw_video_path and os.path.exists(raw_video_path):
        raw_uf = client.files.upload(file=raw_video_path)
        uploaded_files.append(raw_uf)

    for uf in uploaded_files:
        while uf.state.name == "PROCESSING":
            time.sleep(1.5)
            uf = client.files.get(name=uf.name)

    prompt = """
    You are a Master AI Video Director & Short-Form Video Template Architect.
    The user provided a Reference Video showing a viral editing style, AND/OR their own Raw Video footage.

    YOUR MISSION:
    Build a MODULAR CLIP-BY-CLIP EDITING TEMPLATE for the user to assemble their short raw video clips into a high-retention final video:

    1. Extract the reference video's exact editing DNA (cuts, transitions, text popups, SFX drops, B-roll pacing).
    2. Create a MODULAR SHORT-CLIP ASSEMBLY PLAN (Clip #1, Clip #2, Clip #3...):
       - Give exact recommended clip duration (e.g. '3-4 seconds').
       - Tell the user EXACTLY which raw video clip or action snippet to insert in each slot.
       - Provide pre-designed text content to copy-paste.
       - Recommend exact SFX sound drops.
       - Provide step-by-step instructions for Mobile Apps (CapCut / VN / InShot) AND Desktop Software (Premiere Pro / DaVinci / Final Cut)!
    3. State WHICH EDITING APP is easiest to build this template in.
    """

    models_to_try = ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite"]
    last_error = None
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[*uploaded_files, prompt] if uploaded_files else [prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=StyleTransferPlan,
                )
            )
            return StyleTransferPlan.model_validate_json(response.text)
        except Exception as e:
            last_error = e
            continue

    raise Exception(f"Style Transfer API Error: {str(last_error)}")
