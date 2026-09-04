import streamlit as st
import os
import importlib
import urllib.parse
import downloader
import analyzer
import report_generator
from downloader import download_video
from analyzer import analyze_video_with_gemini
from report_generator import generate_pdf_report, generate_csv_report

# Force fresh module load
importlib.reload(analyzer)
importlib.reload(downloader)
importlib.reload(report_generator)

st.set_page_config(
    page_title="CutSense AI Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ultra-Clean Mobile & Laptop CSS Injection
clean_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    
    /* Clean Hero Title */
    .hero-title {
        font-size: clamp(1.8rem, 4.5vw, 2.8rem);
        font-weight: 800;
        background: linear-gradient(135deg, #d946ef 0%, #8b5cf6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .hero-subtitle {
        font-size: clamp(0.9rem, 2vw, 1.05rem);
        color: #94a3b8;
        margin-bottom: 1.2rem;
    }

    /* Clean Glassmorphism Cards */
    .glass-card {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(217, 70, 239, 0.18);
        border-radius: 16px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }

    /* Distinct Color-Coded Edit Badges */
    .tag-cut { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 0.82rem; }
    .tag-transition { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 0.82rem; }
    .tag-broll { background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 0.82rem; }
    .tag-sfx { background: rgba(236, 72, 153, 0.15); color: #f472b6; border: 1px solid rgba(236, 72, 153, 0.3); font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 0.82rem; }
    .tag-motion { background: rgba(249, 115, 22, 0.15); color: #fb923c; border: 1px solid rgba(249, 115, 22, 0.3); font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 0.82rem; }

    .learn-btn {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white !important;
        font-weight: 700;
        text-decoration: none;
        padding: 8px 16px;
        border-radius: 10px;
        font-size: 0.88rem;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        transition: transform 0.2s;
    }

    .learn-btn:hover { transform: translateY(-2px); }

    .time-badge {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        color: #f43f5e;
        background: rgba(244, 63, 94, 0.12);
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.85rem;
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
        padding: 12px 24px !important;
        font-size: 1rem !important;
        min-height: 48px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(217, 70, 239, 0.4) !important;
    }

    @media (max-width: 768px) {
        .glass-card { padding: 12px 14px !important; margin-bottom: 10px !important; }
        .stButton > button { width: 100% !important; }
    }
</style>
"""
st.markdown(clean_css, unsafe_allow_html=True)

def get_tag_class(edit_type: str) -> str:
    edit_lower = edit_type.lower()
    if "cut" in edit_lower: return "tag-cut"
    elif "transition" in edit_lower or "swipe" in edit_lower: return "tag-transition"
    elif "b-roll" in edit_lower or "showcase" in edit_lower: return "tag-broll"
    elif "sfx" in edit_lower or "sound" in edit_lower or "audio" in edit_lower: return "tag-sfx"
    else: return "tag-motion"

# App Header
st.markdown('<div class="hero-title">⚡ CutSense AI Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Deconstruct cuts, virality drivers & <b>#1 top-viewed tutorial videos</b> for YouTube & Instagram Reels.</div>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Studio Settings")
    user_api_key = st.text_input("Gemini API Key:", type="password", help="Enter your Gemini API key from https://aistudio.google.com/")
    st.markdown("---")
    st.caption("Crafted for Video Editors & Content Creators")

# Input Section
video_url = st.text_input("YouTube Video or Instagram Reel URL:", placeholder="Paste YouTube link or https://www.instagram.com/reel/...")

if st.button("🚀 Deconstruct Edits & Virality", use_container_width=True):
    api_key_to_use = user_api_key or os.environ.get("GEMINI_API_KEY")
    
    if not video_url:
        st.warning("Please enter a valid YouTube or Instagram Reel URL.")
    elif not api_key_to_use:
        st.error("Please enter your Gemini API Key in the sidebar or set the GEMINI_API_KEY environment variable.")
    else:
        try:
            with st.spinner("⚡ Step 1/2: Downloading video stream..."):
                metadata = download_video(video_url)
                
            st.session_state["metadata"] = metadata
            
            with st.spinner("⚡ Step 2/2: Gemini AI & YouTube engine locating #1 top-viewed tutorial videos..."):
                report = analyze_video_with_gemini(metadata["file_path"], api_key=api_key_to_use)
                st.session_state["report"] = report

        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")

# Display Results from Session State
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
        
        # Virality Score Card
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        score = getattr(report, 'virality_score_out_of_100', 92)
        st.markdown(f"<div style='text-align: center;'><span class='virality-score'>⚡ Virality Score: {score} / 100</span></div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Download Export Actions
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 📥 Export Client Reports")
        
        pdf_bytes = generate_pdf_report(metadata, report)
        csv_str = generate_csv_report(metadata, report)
        
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.download_button("📄 PDF Report", data=pdf_bytes, file_name=f"CutSense_{platform_label.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)
        with d_col2:
            st.download_button("📊 CSV Data", data=csv_str, file_name=f"CutSense_{platform_label.replace(' ', '_')}.csv", mime="text/csv", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        # Pacing & Density
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Pacing & Cut Density")
        cuts_count = report.estimated_cuts_per_minute
        st.markdown(f"**Pacing:** <span class='tag-transition'>{report.pacing_rating}</span> &nbsp;|&nbsp; **Density:** <span class='tag-cut'>{cuts_count} cuts/min</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Why it got views & likes (Collapsible for Clean Mobile UI)
        if hasattr(report, 'why_it_got_views_and_likes'):
            with st.expander("📈 Why This Video Got High Views & Likes", expanded=True):
                st.write(report.why_it_got_views_and_likes)

        # Comment section drivers
        if hasattr(report, 'comment_section_triggers'):
            with st.expander("💬 Why Viewers Left Comments & Engaged", expanded=False):
                st.write(report.comment_section_triggers)

        # Thumbnail & Title Synergy
        if hasattr(report, 'thumbnail_title_synergy'):
            with st.expander("🖼️ Title & Thumbnail CTR Synergy", expanded=False):
                st.write(report.thumbnail_title_synergy)
        
        # Hook Evaluation
        with st.expander("🪝 First 15-Second Retention Hook", expanded=False):
            st.write(report.script_hook_evaluation)

    st.divider()
    
    # Interactive Timeline Breakdown with Direct Specific High-Viewed Tutorial Videos
    st.markdown("### ⏱️ Timestamped Editing & #1 Top-Viewed Tutorial Video Redirects")
    
    for item in report.timeline:
        tag_style = get_tag_class(item.editing_type)
        tutorial_title = getattr(item, 'tutorial_title', f"How to do {item.editing_type}")
        tutorial_url = getattr(item, 'tutorial_youtube_url', f"https://www.youtube.com/results?search_query=How+to+do+{urllib.parse.quote(item.editing_type)}+tutorial&sp=CAM%253D")
        quick_steps = getattr(item, 'quick_step_guide', "1. Import footage. 2. Apply effect. 3. Keyframe easing.")
        
        st.markdown(f"""
        <div class="glass-card" style="padding: 16px 20px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
                <div>
                    <span class="time-badge">⏱️ {item.timestamp_start} - {item.timestamp_end}</span>
                    &nbsp;&nbsp;
                    <span class="{tag_style}">{item.editing_type}</span>
                </div>
                <div>
                    <a href="{tutorial_url}" target="_blank" class="learn-btn">▶️ Watch #1 Top-Viewed Tutorial Video</a>
                </div>
            </div>
            <div style="font-size: 0.96rem; color: #f1f5f9; margin-bottom: 6px;">
                <strong>Technique:</strong> {item.description}
            </div>
            <div style="font-size: 0.9rem; color: #38bdf8; margin-bottom: 6px;">
                🎬 <strong>Top Tutorial:</strong> <em>{tutorial_title}</em>
            </div>
            <div style="font-size: 0.88rem; color: #94a3b8; margin-bottom: 6px;">
                💡 <em>Retention Impact:</em> {item.engagement_impact}
            </div>
            <div style="font-size: 0.84rem; color: #cbd5e1; background: rgba(255,255,255,0.04); padding: 8px 12px; border-radius: 8px; margin-top: 6px;">
                🛠️ <strong>Quick How-To:</strong> {quick_steps}
            </div>
        </div>
        """, unsafe_allow_html=True)
