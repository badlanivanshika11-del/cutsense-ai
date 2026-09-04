import streamlit as st
import os
import importlib
import urllib.parse
import downloader
import analyzer
import report_generator
import style_director
from downloader import download_video
from analyzer import analyze_video_with_gemini
from report_generator import generate_pdf_report, generate_csv_report
from style_director import transfer_style_to_raw_video

# Force fresh module load
importlib.reload(analyzer)
importlib.reload(downloader)
importlib.reload(report_generator)
importlib.reload(style_director)

st.set_page_config(
    page_title="CutSense AI Master Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Styling Injection
clean_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    
    .hero-title {
        font-size: clamp(2rem, 5vw, 3rem);
        font-weight: 800;
        background: linear-gradient(135deg, #d946ef 0%, #8b5cf6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .glass-card {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(217, 70, 239, 0.18);
        border-radius: 16px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }

    .copy-box {
        background: rgba(15, 23, 42, 0.9);
        border: 1px dashed rgba(6, 182, 212, 0.5);
        border-radius: 10px;
        padding: 10px 14px;
        font-family: 'JetBrains Mono', monospace;
        color: #38bdf8;
        font-size: 0.9rem;
        margin: 6px 0;
    }

    .app-recommendation {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        font-weight: 800;
        padding: 6px 16px;
        border-radius: 16px;
        font-size: 0.95rem;
    }

    .virality-score {
        display: inline-block;
        background: linear-gradient(135deg, #eab308 0%, #ef4444 100%);
        color: white;
        font-weight: 800;
        padding: 6px 16px;
        border-radius: 16px;
        font-size: 1rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #d946ef 0%, #8b5cf6 50%, #3b82f6 100%) !important;
        color: white !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        font-size: 1.05rem !important;
        min-height: 52px !important;
        box-shadow: 0 4px 20px rgba(217, 70, 239, 0.4) !important;
    }
</style>
"""
st.markdown(clean_css, unsafe_allow_html=True)

# App Header
st.markdown('<div class="hero-title">⚡ CutSense AI Master Studio</div>', unsafe_allow_html=True)
st.caption("Video Deconstruct • Virality Analytics • Style Transfer • Modular Short-Clip Video Templates • Multi-Software Advisor")

# Sidebar Settings
with st.sidebar:
    st.markdown("### ⚙️ Studio Settings")
    user_api_key = st.text_input("Gemini API Key:", type="password", help="Enter your Gemini API key from https://aistudio.google.com/")
    st.markdown("---")
    st.markdown("### 📱 Supported Editing Apps")
    st.markdown("• CapCut\n• VN Video Editor\n• InShot\n• DaVinci Resolve\n• Premiere Pro\n• Final Cut Pro\n• After Effects")
    st.markdown("---")
    st.caption("Crafted for Video Editors & Content Creators")

# UNIFIED UNIFIED INPUT SECTION FOR PHASE 1 & 2
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("### 🎬 Input Video & Raw Clips Settings")

col_ref, col_raw = st.columns(2)

with col_ref:
    st.markdown("#### 1. Reference Video to Copy Style / Deconstruct")
    video_url = st.text_input("YouTube / Instagram Reel Link:", placeholder="https://www.youtube.com/watch?v=...", key="master_url")

with col_raw:
    st.markdown("#### 2. Your Raw Video / Short Clips (File Upload or Link)")
    uploaded_file = st.file_uploader("Upload Raw Video File (Up to 200 MB on Cloud / 1.0 GB on Local http://localhost:8501):", type=["mp4", "mov", "mkv", "avi"], help="Streamlit Cloud caps web uploads at 200MB. For 0.8 GB files, use your local app http://localhost:8501 or paste a video link!", key="master_file")
    raw_url_input = st.text_input("OR Paste Raw Video Link URL:", placeholder="https://www.youtube.com/watch?v=...", key="master_raw_url")

    # SAVE UPLOADED FILE PERSISTENTLY INTO SESSION STATE IMMEDIATELY
    if uploaded_file:
        os.makedirs("downloads/uploaded_raw", exist_ok=True)
        saved_raw_path = os.path.join("downloads/uploaded_raw", uploaded_file.name)
        with open(saved_raw_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state["raw_file_path"] = saved_raw_path
        st.session_state["raw_title"] = uploaded_file.name
        st.success(f"📁 Raw video loaded: **{uploaded_file.name}**")

st.markdown('</div>', unsafe_allow_html=True)

if st.button("🚀 Analyze, Deconstruct & Generate Editing Template", use_container_width=True, key="master_submit"):
    api_key_to_use = user_api_key or os.environ.get("GEMINI_API_KEY")
    
    if not video_url:
        st.warning("Please enter a Reference Video URL to analyze.")
    elif not api_key_to_use:
        st.error("Please enter your Gemini API Key in the sidebar or set GEMINI_API_KEY.")
    else:
        try:
            # 1. Check raw video path from session state or URL input
            raw_path = st.session_state.get("raw_file_path")
            if not raw_path and raw_url_input and raw_url_input.strip():
                with st.spinner("⚡ Downloading raw video link..."):
                    raw_meta = download_video(raw_url_input.strip(), output_dir="downloads/raw")
                    raw_path = raw_meta.get("file_path")
                    st.session_state["raw_file_path"] = raw_path
                    st.session_state["raw_title"] = raw_meta.get("title", "Your Raw Video")

            # 2. Download & Analyze Reference Video (Phase 1)
            with st.spinner("⚡ Step 1/3: Downloading reference video stream..."):
                metadata = download_video(video_url)
                st.session_state["metadata"] = metadata

            with st.spinner("⚡ Step 2/3: Gemini AI analyzing frame edits & virality..."):
                report = analyze_video_with_gemini(metadata.get("file_path"), api_key=api_key_to_use, meta_dict=metadata)
                st.session_state["report"] = report

            # 3. Generate Modular Short-Clip Style Transfer Template (Phase 2)
            ref_paths = [metadata["file_path"]] if metadata.get("file_path") else []
            with st.spinner("⚡ Step 3/3: Building modular short-clip editing template for your video..."):
                plan = transfer_style_to_raw_video(ref_paths, raw_path, api_key=api_key_to_use)
                st.session_state["style_plan"] = plan

        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")

# UNIFIED DASHBOARD DISPLAY
if "metadata" in st.session_state and "report" in st.session_state:
    metadata = st.session_state["metadata"]
    report = st.session_state["report"]
    platform_label = metadata.get("platform", "Video")
    
    st.success(f"Analysis Complete for {platform_label}: **{metadata['title']}** (By: {metadata['uploader']})")

    # PROMINENT PHASE 2 MODULAR SHORT-CLIP TEMPLATE AT TOP
    if "style_plan" in st.session_state:
        plan = st.session_state["style_plan"]
        raw_title = st.session_state.get("raw_title", "Your Video Clips")
        
        st.markdown(f"### 🎬 MODULAR SHORT-CLIP EDITING TEMPLATE FOR: **{raw_title}**")
        st.write("Follow this clip-by-clip assembly template to arrange your short raw video clips into a high-retention final video!")

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(f"**Recommended Editing App:**<br><span class='app-recommendation'>💡 {plan.recommended_editing_app}</span>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with sc2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(f"**Difficulty:** **{plan.difficulty_level}**", unsafe_allow_html=True)
            st.markdown(f"**Template Style:** *{plan.template_name}*", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with sc3:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(f"🎵 **Suggested BGM:**<br>*{plan.suggested_background_music}*", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 🎨 Visual Aesthetic & Style Transfer Vibe")
        st.write(plan.overall_editing_vibe)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("#### ✂️ Clip-by-Clip Assembly Template (Add your short clips here):")
        
        clip_list = getattr(plan, 'modular_clip_template', getattr(plan, 'step_by_step_timeline', []))
        for idx, item in enumerate(clip_list, 1):
            clip_num = getattr(item, 'clip_number', idx)
            duration = getattr(item, 'recommended_duration_seconds', '3-5 seconds')
            purpose = getattr(item, 'clip_purpose', 'Short Clip Slot')
            raw_inst = getattr(item, 'what_raw_clip_to_insert', 'Insert your short raw video clip snippet here.')
            transition = getattr(item, 'transition_to_next_clip', getattr(item, 'transition_name', 'Cut'))
            copy_text = getattr(item, 'copy_paste_text_popup', getattr(item, 'copy_paste_text', ''))
            sfx = getattr(item, 'recommended_sfx_drop', getattr(item, 'recommended_sfx', 'Whoosh.wav'))
            mobile_steps = getattr(item, 'how_to_assemble_in_mobile_apps', getattr(item, 'how_to_do_in_mobile_apps', 'Import clip & trim.'))
            desktop_steps = getattr(item, 'how_to_assemble_in_desktop_apps', getattr(item, 'how_to_do_in_desktop_apps', 'Import clip & trim.'))

            st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap;">
                    <div>
                        <span style="font-family: monospace; font-weight: 700; color: #f43f5e; background: rgba(244,63,94,0.15); padding: 4px 10px; border-radius: 6px;">🎬 CLIP #{clip_num} ({duration})</span>
                        &nbsp;&nbsp;
                        <span style="font-weight: 700; color: #38bdf8;">[{purpose}]</span>
                    </div>
                </div>
                <div style="font-size: 0.94rem; color: #f1f5f9; margin-bottom: 6px;">
                    📹 <strong>What Raw Clip to Insert Here:</strong> {raw_inst}
                </div>
                {f'<div style="margin: 6px 0;">💬 <strong>Copy-Paste Text Overlay:</strong><div class="copy-box">{copy_text}</div></div>' if copy_text else ''}
                <div style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 6px;">
                    ✨ <strong>Transition to Next Clip:</strong> <code>{transition}</code> &nbsp;|&nbsp; 
                    🔊 <strong>SFX Sound Drop:</strong> <code>{sfx}</code>
                </div>
                <div style="font-size: 0.85rem; color: #94a3b8; background: rgba(255,255,255,0.03); padding: 8px; border-radius: 8px;">
                    📱 <strong>CapCut / VN / InShot Step:</strong> {mobile_steps}<br>
                    💻 <strong>Premiere Pro / DaVinci / Final Cut Step:</strong> {desktop_steps}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.divider()

    # METRICS ROW (PHASE 1)
    col1, col2 = st.columns([1.1, 1.9])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"#### 📽️ {platform_label} Preview")
        if metadata.get("thumbnail"):
            st.image(metadata["thumbnail"], use_container_width=True)
        if metadata.get("file_path") and os.path.exists(metadata["file_path"]):
            st.video(metadata["file_path"])
        elif metadata.get("webpage_url"):
            st.video(metadata["webpage_url"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Virality Card
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        score = getattr(report, 'virality_score_out_of_100', 94)
        st.markdown(f"<div style='text-align: center;'><span class='virality-score'>⚡ Virality Score: {score} / 100</span></div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Export Actions
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 📥 Export Client Reports")
        pdf_bytes = generate_pdf_report(metadata, report)
        csv_str = generate_csv_report(metadata, report)
        
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.download_button("📄 PDF Report", data=pdf_bytes, file_name=f"CutSense_{platform_label.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True, key="m_pdf")
        with d_col2:
            st.download_button("📊 CSV Data", data=csv_str, file_name=f"CutSense_{platform_label.replace(' ', '_')}.csv", mime="text/csv", use_container_width=True, key="m_csv")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        # Pacing & Cut Density
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Pacing & Editing Density")
        cuts_count = report.estimated_cuts_per_minute
        st.markdown(f"**Pacing Speed:** **{report.pacing_rating}** &nbsp;|&nbsp; **Density:** **{cuts_count} cuts/min**", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if hasattr(report, 'why_it_got_views_and_likes'):
            with st.expander("📈 Why This Video Got High Views & Likes", expanded=True):
                st.write(report.why_it_got_views_and_likes)

        if hasattr(report, 'comment_section_triggers'):
            with st.expander("💬 Why Viewers Left Comments & Engaged", expanded=False):
                st.write(report.comment_section_triggers)

        if hasattr(report, 'thumbnail_title_synergy'):
            with st.expander("🖼️ Title & Thumbnail CTR Synergy", expanded=False):
                st.write(report.thumbnail_title_synergy)

        with st.expander("🪝 First 15-Second Retention Hook", expanded=False):
            st.write(report.script_hook_evaluation)

    # TIMELINE SECTION
    st.divider()
    st.markdown("### ⏱️ Reference Video Edit Breakdown & #1 Top-Viewed Tutorial Videos")
    
    for item in report.timeline:
        query = getattr(item, 'tutorial_query', f"How to do {item.editing_type} video editing tutorial")
        tutorial_title = getattr(item, 'tutorial_title', f"How to do {item.editing_type}")
        quick_steps = getattr(item, 'quick_step_guide', "1. Import footage. 2. Apply effect. 3. Keyframe easing.")
        
        tutorial_url = getattr(item, 'tutorial_youtube_url', '')
        if not tutorial_url or not tutorial_url.startswith("http"):
            encoded_query = urllib.parse.quote(query)
            tutorial_url = f"https://www.youtube.com/results?search_query={encoded_query}&sp=CAM%253D"
        
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 6px;">
                <div>
                    <span style="font-family: monospace; font-weight: 700; color: #f43f5e; background: rgba(244,63,94,0.12); padding: 4px 8px; border-radius: 6px;">⏱️ {item.timestamp_start} - {item.timestamp_end}</span>
                    &nbsp;&nbsp;
                    <span style="font-weight: 700; color: #38bdf8;">[{item.editing_type}]</span>
                </div>
                <div>
                    <a href="{tutorial_url}" target="_blank" style="background: #059669; color: white; padding: 6px 12px; border-radius: 8px; text-decoration: none; font-size: 0.85rem; font-weight: 700;">▶️ Watch #1 Top-Viewed Tutorial Video</a>
                </div>
            </div>
            <div style="font-size: 0.94rem; color: #f1f5f9; margin-bottom: 4px;">
                <strong>Technique:</strong> {item.description}
            </div>
            <div style="font-size: 0.88rem; color: #38bdf8; margin-bottom: 4px;">
                🎬 <strong>Top Tutorial:</strong> <em>{tutorial_title}</em>
            </div>
            <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 4px;">
                💡 <em>Retention Impact:</em> {item.engagement_impact}
            </div>
            <div style="font-size: 0.82rem; color: #cbd5e1; background: rgba(255,255,255,0.04); padding: 6px 10px; border-radius: 6px; margin-top: 4px;">
                🛠️ <strong>Quick How-To:</strong> {quick_steps}
            </div>
        </div>
        """, unsafe_allow_html=True)
