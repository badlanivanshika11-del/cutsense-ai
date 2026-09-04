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
    page_title="CutSense AI Studio - Phase 2 Edition",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cyberpunk Neon & Clean Styling
clean_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    
    .hero-title {
        font-size: clamp(1.8rem, 4.5vw, 2.8rem);
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
        padding: 8px 18px;
        border-radius: 20px;
        font-size: 1rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #d946ef 0%, #8b5cf6 50%, #3b82f6 100%) !important;
        color: white !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-size: 1rem !important;
        min-height: 48px !important;
        box-shadow: 0 4px 20px rgba(217, 70, 239, 0.4) !important;
    }
</style>
"""
st.markdown(clean_css, unsafe_allow_html=True)

# App Header
st.markdown('<div class="hero-title">⚡ CutSense AI Studio - Phase 2</div>', unsafe_allow_html=True)
st.caption("AI Style Transfer • Reusable Video Templates • 1-Click Copy-Paste Editing Director & Software Advisor")

# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Studio Navigation")
    app_mode = st.radio(
        "Select Mode:",
        ["🎯 Mode 1: Deconstruct & Virality Engine", "⚡ Mode 2: AI Style Transfer & Copy-Paste Director"],
        index=1
    )
    st.markdown("---")
    user_api_key = st.text_input("Gemini API Key:", type="password", help="Enter your Gemini API key from https://aistudio.google.com/")
    st.markdown("---")
    st.caption("Crafted for Video Editors & Content Creators")

# MODE 2: AI STYLE TRANSFER & COPY-PASTE EDIT DIRECTOR (PHASE 2)
if app_mode == "⚡ Mode 2: AI Style Transfer & Copy-Paste Director":
    st.subheader("⚡ Phase 2: Copy-Paste Video Style Transfer & AI Editing Director")
    st.write("Upload reference video(s) showing an editing style you love, plus your own video clip. AI will generate a 100% copy-paste ready editing blueprint for your video!")

    col_ref, col_raw = st.columns(2)
    
    with col_ref:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 🎬 Reference Video(s) (Editing Style DNA)")
        ref_url1 = st.text_input("Reference Video 1 URL (YouTube / Reel):", placeholder="https://www.youtube.com/watch?v=...")
        ref_url2 = st.text_input("Reference Video 2 URL (Optional):", placeholder="https://www.instagram.com/reel/...")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_raw:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 📽️ Your Video Clip")
        raw_url = st.text_input("Your Raw Video URL (YouTube / Reel):", placeholder="https://www.youtube.com/watch?v=...")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    target_preset_option = st.selectbox(
        "Choose Target Editing Preset & Software Style:",
        [
            "Option A: CapCut Fast Viral Reel (Easiest & Fastest)",
            "Option B: Premiere Pro Studio Professional (High Quality)",
            "Option C: After Effects Motion Graphic Mastery (Complex Effects)"
        ]
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("⚡ Generate Copy-Paste Editing Blueprint", use_container_width=True):
        api_key_to_use = user_api_key or os.environ.get("GEMINI_API_KEY")
        
        if not ref_url1 or not raw_url:
            st.warning("Please enter at least Reference Video 1 URL and Your Raw Video URL.")
        elif not api_key_to_use:
            st.error("Please enter your Gemini API Key in the sidebar or set GEMINI_API_KEY.")
        else:
            try:
                with st.spinner("Step 1/3: Downloading reference video style stream..."):
                    ref_meta1 = download_video(ref_url1, output_dir="downloads/ref1")
                    ref_paths = [ref_meta1["file_path"]]
                    if ref_url2:
                        ref_meta2 = download_video(ref_url2, output_dir="downloads/ref2")
                        ref_paths.append(ref_meta2["file_path"])
                        
                with st.spinner("Step 2/3: Downloading your raw video clip..."):
                    raw_meta = download_video(raw_url, output_dir="downloads/raw")
                    
                with st.spinner("Step 3/3: Gemini AI is mapping reference editing DNA onto your video timeline..."):
                    plan = transfer_style_to_raw_video(ref_paths, raw_meta["file_path"], api_key=api_key_to_use)
                    st.session_state["style_plan"] = plan
                    st.session_state["raw_meta"] = raw_meta

            except Exception as e:
                st.error(f"An error occurred during style transfer: {str(e)}")

    if "style_plan" in st.session_state and "raw_meta" in st.session_state:
        plan = st.session_state["style_plan"]
        raw_meta = st.session_state["raw_meta"]
        
        st.success(f"Generated Copy-Paste Template for: **{raw_meta['title']}**")
        
        # Software & Vibe Recommendation Cards
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(f"**Recommended Editing App:**<br><span class='app-recommendation'>💡 {plan.recommended_editing_app}</span>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with sc2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(f"**Editing Difficulty:** **{plan.difficulty_level}**", unsafe_allow_html=True)
            st.markdown(f"**Style Name:** *{plan.template_name}*", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with sc3:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(f"🎵 **Suggested BGM:**<br>*{plan.suggested_background_music}*", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🎨 Visual Aesthetic & Style Transfer Vibe")
        st.write(plan.overall_editing_vibe)
        st.markdown('</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📋 1:1 Copy-Paste Ready Timeline Script for Your Video")
        
        for idx, item in enumerate(plan.step_by_timeline if hasattr(plan, 'step_by_timeline') else plan.step_by_step_timeline, 1):
            st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <span style="font-family: monospace; font-weight: 700; color: #f43f5e; background: rgba(244,63,94,0.15); padding: 4px 8px; border-radius: 6px;">⏱️ Timestamp: {item.timestamp}</span>
                        &nbsp;&nbsp;
                        <span style="font-weight: 700; color: #38bdf8;">[{item.action_type}]</span>
                    </div>
                    <div style="font-size: 0.82rem; color: #94a3b8;">
                        Ref Style: <em>{item.style_from_reference}</em>
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
                    📱 <strong>CapCut Step:</strong> {item.how_to_do_in_capcut}<br>
                    💻 <strong>Premiere Pro Step:</strong> {item.how_to_do_in_premiere}
                </div>
            </div>
            """, unsafe_allow_html=True)

# MODE 1: DECONSTRUCT & VIRALITY ENGINE (PHASE 1)
else:
    st.subheader("🎯 Mode 1: Video Deconstruction & Virality Analytics")
    video_url = st.text_input("YouTube Video or Instagram Reel URL:", placeholder="Paste YouTube link or https://www.instagram.com/reel/...")

    if st.button("🚀 Deconstruct Edits & Virality", use_container_width=True):
        api_key_to_use = user_api_key or os.environ.get("GEMINI_API_KEY")
        
        if not video_url:
            st.warning("Please enter a valid YouTube or Instagram Reel URL.")
        elif not api_key_to_use:
            st.error("Please enter your Gemini API Key in the sidebar or set GEMINI_API_KEY.")
        else:
            try:
                with st.spinner("Step 1/2: Downloading video stream..."):
                    metadata = download_video(video_url)
                    
                st.session_state["metadata"] = metadata
                
                with st.spinner("Step 2/2: Gemini AI is analyzing frame edits & virality..."):
                    report = analyze_video_with_gemini(metadata["file_path"], api_key=api_key_to_use)
                    st.session_state["report"] = report

            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")

    if "metadata" in st.session_state and "report" in st.session_state:
        metadata = st.session_state["metadata"]
        report = st.session_state["report"]
        
        platform_label = metadata.get("platform", "Video")
        st.success(f"Loaded {platform_label}: **{metadata['title']}** (By: {metadata['uploader']})")
        
        col1, col2 = st.columns([1.1, 1.9])
        
        with col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(f"#### 📽️ {platform_label} Preview")
            if metadata.get("thumbnail"):
                st.image(metadata["thumbnail"], use_container_width=True)
            st.video(metadata["file_path"])
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            pdf_bytes = generate_pdf_report(metadata, report)
            csv_str = generate_csv_report(metadata, report)
            
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.download_button("📄 PDF Report", data=pdf_bytes, file_name=f"CutSense_{platform_label.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)
            with d_col2:
                st.download_button("📊 CSV Data", data=csv_str, file_name=f"CutSense_{platform_label.replace(' ', '_')}.csv", mime="text/csv", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 📊 Pacing & Cut Density")
            cuts_count = report.estimated_cuts_per_minute
            st.markdown(f"**Pacing:** **{report.pacing_rating}** &nbsp;|&nbsp; **Density:** **{cuts_count} cuts/min**", unsafe_allow_html=True)
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

        st.divider()
        st.markdown("### ⏱️ Timestamped Editing & Direct Tutorial Videos")
        
        for item in report.timeline:
            query = getattr(item, 'tutorial_query', f"How to do {item.editing_type} video editing tutorial")
            tutorial_title = getattr(item, 'tutorial_title', f"How to do {item.editing_type}")
            quick_steps = getattr(item, 'quick_step_guide', "1. Import footage. 2. Apply effect. 3. Keyframe easing.")
            
            tutorial_url = getattr(item, 'tutorial_youtube_url', '')
            if not tutorial_url or not tutorial_url.startswith("http"):
                encoded_query = urllib.parse.quote(query)
                tutorial_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            
            st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 6px;">
                    <div>
                        <span style="font-family: monospace; font-weight: 700; color: #f43f5e; background: rgba(244,63,94,0.12); padding: 4px 8px; border-radius: 6px;">⏱️ {item.timestamp_start} - {item.timestamp_end}</span>
                        &nbsp;&nbsp;
                        <span style="font-weight: 700; color: #38bdf8;">[{item.editing_type}]</span>
                    </div>
                    <div>
                        <a href="{tutorial_url}" target="_blank" style="background: #059669; color: white; padding: 6px 12px; border-radius: 8px; text-decoration: none; font-size: 0.85rem; font-weight: 700;">▶️ Watch Tutorial Video</a>
                    </div>
                </div>
                <div style="font-size: 0.94rem; color: #f1f5f9; margin-bottom: 4px;">
                    <strong>Technique:</strong> {item.description}
                </div>
                <div style="font-size: 0.88rem; color: #38bdf8; margin-bottom: 4px;">
                    🎬 <strong>Tutorial:</strong> <em>{tutorial_title}</em>
                </div>
                <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 4px;">
                    💡 <em>Retention Impact:</em> {item.engagement_impact}
                </div>
                <div style="font-size: 0.82rem; color: #cbd5e1; background: rgba(255,255,255,0.04); padding: 6px 10px; border-radius: 6px; margin-top: 4px;">
                    🛠️ <strong>Quick How-To:</strong> {quick_steps}
                </div>
            </div>
            """, unsafe_allow_html=True)
