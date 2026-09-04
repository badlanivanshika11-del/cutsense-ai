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

class EditInstruction(BaseModel):
    timestamp: str = Field(description="Timestamp in user's raw video, e.g., 00:03")
    action_type: str = Field(description="Cut, Transition, SFX, Text Popup, B-roll, Speed Ramp, Color Grade")
    style_from_reference: str = Field(description="Which reference video style this comes from.")
    copy_paste_text: str = Field(description="Pre-designed text content for user to copy-paste into editor.")
    recommended_sfx: str = Field(description="Exact SFX sound to play, e.g., 'Whoosh_Fast.wav', 'Pop_Bubble.mp3'")
    transition_name: str = Field(description="Exact transition effect name to use.")
    how_to_do_in_capcut: str = Field(description="1-step instruction for CapCut.")
    how_to_do_in_premiere: str = Field(description="1-step instruction for Premiere Pro.")

class StyleTransferPlan(BaseModel):
    template_name: str = Field(description="Name given to this editing style template, e.g., 'Viral Fast-Paced Reel'")
    recommended_editing_app: str = Field(description="CapCut, Premiere Pro, After Effects, or DaVinci Resolve (with reason).")
    difficulty_level: str = Field(description="Beginner, Intermediate, or Advanced")
    overall_editing_vibe: str = Field(description="Summary of the visual aesthetic transferred from reference videos.")
    suggested_background_music: str = Field(description="Type of background music genre & bpm to use.")
    step_by_step_timeline: list[EditInstruction]

def transfer_style_to_raw_video(reference_video_paths: list[str], raw_video_path: str, api_key: str = None) -> StyleTransferPlan:
    """Analyzes 1-3 reference videos + user's raw video to generate a 1:1 copy-paste editing plan."""
    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        client = genai.Client()

    uploaded_files = []
    
    print("Uploading reference and raw video files to Gemini API...")
    for path in reference_video_paths:
        if os.path.exists(path):
            uf = client.files.upload(file=path)
            uploaded_files.append(uf)

    if os.path.exists(raw_video_path):
        raw_uf = client.files.upload(file=raw_video_path)
        uploaded_files.append(raw_uf)

    # Wait for processing
    for uf in uploaded_files:
        while uf.state.name == "PROCESSING":
            time.sleep(1.5)
            uf = client.files.get(name=uf.name)

    prompt = """
    You are a World-Class AI Video Editing Director & Style Transfer Specialist.
    The user provided Reference Video(s) showing a high-performing editing style, AND their own Raw Video clip.

    YOUR MISSION:
    1. Extract the visual & audio editing DNA from the Reference Video(s) (cuts per minute, text popup designs, SFX drops, B-roll timing, transitions).
    2. Map that EXACT editing style onto the User's Raw Video clip.
    3. Generate a 100% COPY-PASTE READY Timeline Script for the user's raw video:
       - Give exact timestamps on the user's raw video where to cut, add transitions, drop SFX, and overlay text.
       - Provide pre-designed text text content for them to copy-paste.
       - Recommend exact SFX file types (Whoosh, Pop, Camera Shutter).
       - Tell the user WHICH EDITING APP (CapCut vs Premiere Pro vs After Effects) is EASIEST for this specific style, with step-by-step instructions for both CapCut and Premiere Pro!
    """

    models_to_try = ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite"]
    last_error = None
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[*uploaded_files, prompt],
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
