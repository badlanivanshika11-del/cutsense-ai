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
    page_title="CutSense AI Master Studio - Phase 1 & 2",
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

    .learn-btn {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white !important;
        font-weight: 700;
        text-decoration: none;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.82rem;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
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
st.caption("Phase 1 & 2 Combined • Video Deconstruct • Virality Analytics • Style Transfer • Copy-Paste Timeline • Multi-App Advisor")

# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Studio Settings")
    user_api_key = st.text_input("Gemini API Key:", type="password", help="Enter your Gemini API key from https://aistudio.google.com/")
    st.markdown("---")
    st.markdown("### 📱 Supported Apps")
    st.markdown("• CapCut\n• VN Video Editor\n• InShot\n• DaVinci Resolve\n• Premiere Pro\n• Final Cut Pro\n• After Effects")
    st.markdown("---")
    st.caption("Crafted for Video Editors & Content Creators")

# UNIFIED UNIFIED INPUT SECTION FOR PHASE 1 & 2
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("### 🎬 Input Video & Reference Settings")

col_ref, col_raw = st.columns(2)

with col_ref:
    st.markdown("#### 1. Analyzed / Reference Video (YouTube or Reel Link)")
    video_url = st.text_input("Video URL (YouTube / Reel):", placeholder="https://www.youtube.com/watch?v=...", key="master_url")

with col_raw:
    st.markdown("#### 2. Optional: Your Raw Video (To Transfer Style & Get Copy-Paste Script)")
    raw_upload_method = st.radio("Input Raw Video Clip:", ["📁 Upload Video File", "🔗 Paste Link URL", "🚫 None (Analysis Only)"], horizontal=True, key="master_raw_method")
    
    raw_file_path_to_use = None
    if "Upload Video File" in raw_upload_method:
        uploaded_file = st.file_uploader("Upload Raw Video File (Up to 0.15 GB / 150 MB):", type=["mp4", "mov", "mkv", "avi"], help="Supports raw video files up to 0.15 GB (150 MB)", key="master_file")
        if uploaded_file:
            os.makedirs("downloads/uploaded_raw", exist_ok=True)
            raw_file_path_to_use = os.path.join("downloads/uploaded_raw", uploaded_file.name)
            with open(raw_file_path_to_use, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"File uploaded: **{uploaded_file.name}**")
    elif "Paste Link URL" in raw_upload_method:
        raw_url_input = st.text_input("Raw Video Link URL:", placeholder="https://www.youtube.com/watch?v=...", key="master_raw_url")

st.markdown('</div>', unsafe_allow_html=True)

if st.button("🚀 Analyze, Deconstruct & Transfer Style", use_container_width=True, key="master_submit"):
    api_key_to_use = user_api_key or os.environ.get("GEMINI_API_KEY")
    
    if not video_url:
        st.warning("Please enter a Video URL to analyze.")
    elif not api_key_to_use:
        st.error("Please enter your Gemini API Key in the sidebar or set GEMINI_API_KEY.")
    else:
        try:
            with st.spinner("⚡ Step 1/3: Downloading video stream..."):
                metadata = download_video(video_url)
                st.session_state["metadata"] = metadata

            with st.spinner("⚡ Step 2/3: Gemini AI analyzing deconstruction, virality & tutorial videos..."):
                report = analyze_video_with_gemini(metadata["file_path"], api_key=api_key_to_use)
                st.session_state["report"] = report

            # If user provided raw video, also run Phase 2 Style Transfer Plan
            has_raw = raw_file_path_to_use or ("Paste Link URL" in raw_upload_method and raw_url_input)
            if has_raw:
                with st.spinner("⚡ Step 3/3: Mapping reference editing style onto your raw video clip..."):
                    if not raw_file_path_to_use:
                        raw_meta = download_video(raw_url_input, output_dir="downloads/raw")
                        raw_file_path_to_use = raw_meta["file_path"]
                        
                    plan = transfer_style_to_raw_video([metadata["file_path"]], raw_file_path_to_use, api_key=api_key_to_use)
                    st.session_state["style_plan"] = plan
            else:
                st.session_state.pop("style_plan", None)

        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")

# UNIFIED DASHBOARD DISPLAY (PHASE 1 & PHASE 2 COMBINED)
if "metadata" in st.session_state and "report" in st.session_state:
    metadata = st.session_state["metadata"]
    report = st.session_state["report"]
    platform_label = metadata.get("platform", "Video")
    
    st.success(f"Analysis Complete for {platform_label}: **{metadata['title']}** (By: {metadata['uploader']})")

    # TOP METRICS ROW
    col1, col2 = st.columns([1.1, 1.9])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"#### 📽️ {platform_label} Preview")
        if metadata.get("thumbnail"):
            st.image(metadata["thumbnail"], use_container_width=True)
        st.video(metadata["file_path"])
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

    # PHASE 2 STYLE TRANSFER SECTION (IF RAW VIDEO PROVIDED)
    if "style_plan" in st.session_state:
        plan = st.session_state["style_plan"]
        st.divider()
        st.markdown("### ⚡ Phase 2: Copy-Paste Editing Blueprint & Software Advisor for Your Video")
        
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(f"**Recommended Editing App:**<br><span class='app-recommendation'>💡 {plan.recommended_editing_app}</span>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with sc2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(f"**Difficulty:** **{plan.difficulty_level}**", unsafe_allow_html=True)
            st.markdown(f"**Style Name:** *{plan.template_name}*", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with sc3:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(f"🎵 **Suggested BGM:**<br>*{plan.suggested_background_music}*", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 🎨 Visual Aesthetic & Style Transfer Vibe")
        st.write(plan.overall_editing_vibe)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("#### 📋 1:1 Copy-Paste Ready Timeline Script for Your Raw Video")
        for idx, item in enumerate(getattr(plan, 'step_by_step_timeline', getattr(plan, 'step_by_timeline', [])), 1):
            mobile_steps = getattr(item, 'how_to_do_in_mobile_apps', getattr(item, 'how_to_do_in_capcut', 'Apply transition/text preset.'))
            desktop_steps = getattr(item, 'how_to_do_in_desktop_apps', getattr(item, 'how_to_do_in_premiere', 'Apply keyframe effect.'))
            
            st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap;">
                    <div>
                        <span style="font-family: monospace; font-weight: 700; color: #f43f5e; background: rgba(244,63,94,0.15); padding: 4px 8px; border-radius: 6px;">⏱️ Timestamp: {item.timestamp}</span>
                        &nbsp;&nbsp;
                        <span style="font-weight: 700; color: #38bdf8;">[{item.action_type}]</span>
                    </div>
                </div>
                <div style="margin: 8px 0;">
                    💬 <strong>Copy-Paste Text Content:</strong>
                    <div class="copy-box">{item.copy_paste_text}</div>
                </div>
                <div style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 6px;">
                    🔊 <strong>Recommended SFX Sound:</strong> <code>{item.recommended_sfx}</code> &nbsp;|&nbsp; 
                    ✨ <strong>Transition Effect:</strong> <code>{item.transition_name}</code>
                </div>
                <div style="font-size: 0.85rem; color: #94a3b8; background: rgba(255,255,255,0.03); padding: 8px; border-radius: 8px;">
                    📱 <strong>Mobile Apps (CapCut / VN / InShot):</strong> {mobile_steps}<br>
                    💻 <strong>Desktop Software (Premiere Pro / DaVinci Resolve / Final Cut):</strong> {desktop_steps}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # TIMELINE SECTION (PHASE 1)
    st.divider()
    st.markdown("### ⏱️ Timestamped Editing Timeline & #1 Top-Viewed Tutorial Videos")
    
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
