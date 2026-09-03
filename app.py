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
    page_title="CutSense AI Studio - Cyberpunk Edition",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cyberpunk Neon Custom CSS Injection
cyberpunk_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #090d16;
        color: #f1f5f9;
    }
    
    /* Hero Title with Cyberpunk Neon Glow */
    .hero-title {
        font-size: clamp(2rem, 5vw, 3.2rem);
        font-weight: 800;
        background: linear-gradient(135deg, #d946ef 0%, #8b5cf6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        filter: drop-shadow(0 0 25px rgba(217, 70, 239, 0.4));
    }
    
    .hero-subtitle {
        font-size: clamp(0.95rem, 2.5vw, 1.15rem);
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }

    /* Glassmorphism Cards with Neon Border Glow */
    .glass-card {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(217, 70, 239, 0.2);
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 0 15px rgba(139, 92, 246, 0.05);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(6, 182, 212, 0.4);
        box-shadow: 0 12px 35px rgba(6, 182, 212, 0.15);
    }

    /* Distinct Color-Coded Edit Badges */
    .tag-cut {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.4);
        font-weight: 700;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
    }
    
    .tag-transition {
        background: rgba(168, 85, 247, 0.15);
        color: #c084fc;
        border: 1px solid rgba(168, 85, 247, 0.4);
        font-weight: 700;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
    }

    .tag-broll {
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.4);
        font-weight: 700;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
    }

    .tag-sfx {
        background: rgba(236, 72, 153, 0.15);
        color: #f472b6;
        border: 1px solid rgba(236, 72, 153, 0.4);
        font-weight: 700;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
    }

    .tag-motion {
        background: rgba(249, 115, 22, 0.15);
        color: #fb923c;
        border: 1px solid rgba(249, 115, 22, 0.4);
        font-weight: 700;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
    }

    .learn-btn {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white !important;
        font-weight: 700;
        text-decoration: none;
        padding: 8px 16px;
        border-radius: 10px;
        font-size: 0.88rem;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .learn-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.7);
    }

    .time-badge {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        color: #f43f5e;
        background: rgba(244, 63, 94, 0.12);
        border: 1px solid rgba(244, 63, 94, 0.3);
        padding: 5px 10px;
        border-radius: 8px;
        font-size: 0.9rem;
    }

    .virality-score {
        display: inline-block;
        background: linear-gradient(135deg, #eab308 0%, #ef4444 100%);
        color: white;
        font-weight: 800;
        padding: 8px 18px;
        border-radius: 20px;
        font-size: 1.1rem;
        box-shadow: 0 4px 20px rgba(234, 179, 8, 0.4);
    }

    .pacing-bar-bg {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        height: 12px;
        width: 100%;
        overflow: hidden;
        margin-top: 6px;
    }
    
    .pacing-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6 0%, #a855f7 50%, #f43f5e 100%);
        border-radius: 10px;
        transition: width 1s ease-in-out;
    }

    .stButton > button {
        background: linear-gradient(135deg, #d946ef 0%, #8b5cf6 50%, #3b82f6 100%) !important;
        color: white !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 14px 28px !important;
        font-size: 1.05rem !important;
        min-height: 52px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 25px rgba(217, 70, 239, 0.5) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.01) !important;
        box-shadow: 0 8px 35px rgba(217, 70, 239, 0.8) !important;
    }
</style>
"""
st.markdown(cyberpunk_css, unsafe_allow_html=True)

def get_tag_class(edit_type: str) -> str:
    edit_lower = edit_type.lower()
    if "cut" in edit_lower:
        return "tag-cut"
    elif "transition" in edit_lower or "swipe" in edit_lower:
        return "tag-transition"
    elif "b-roll" in edit_lower or "showcase" in edit_lower:
        return "tag-broll"
    elif "sfx" in edit_lower or "sound" in edit_lower or "audio" in edit_lower:
        return "tag-sfx"
    else:
        return "tag-motion"

# App Header
st.markdown('<div class="hero-title">⚡ CutSense AI Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Cyberpunk Video Editing & Virality Intelligence • <b>YouTube Videos & Instagram Reels</b>.</div>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Studio Settings")
    user_api_key = st.text_input("Gemini API Key:", type="password", help="Enter your Gemini API key from https://aistudio.google.com/")
    
    st.markdown("---")
    st.markdown("### 📈 Engagement Intelligence")
    st.markdown("• ⚡ **Virality & Views Engine**\n• 💬 **Comment Section Triggers**\n• 🖼️ **Thumbnail & Title Synergy**\n• ▶️ **Direct Video Tutorials**")
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
            with st.spinner("Step 1/2: Downloading video / reel stream..."):
                metadata = download_video(video_url)
                
            st.session_state["metadata"] = metadata
            
            with st.spinner("Step 2/2: Gemini AI is analyzing virality, views, comments, and specific tutorial videos..."):
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
        st.markdown("#### 🔥 Virality & Engagement Score")
        score = getattr(report, 'virality_score_out_of_100', 92)
        st.markdown(f"<div style='text-align: center; margin: 10px 0;'><span class='virality-score'>⚡ Virality Score: {score} / 100</span></div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Download Export Actions
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 📥 Export Client Reports")
        
        pdf_bytes = generate_pdf_report(metadata, report)
        csv_str = generate_csv_report(metadata, report)
        
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.download_button(
                label="📄 PDF Report",
                data=pdf_bytes,
                file_name=f"CutSense_{platform_label.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with d_col2:
            st.download_button(
                label="📊 CSV Data",
                data=csv_str,
                file_name=f"CutSense_{platform_label.replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        # Why it got views & likes
        if hasattr(report, 'why_it_got_views_and_likes'):
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 📈 Why This Video Got High Views, Likes & Attention")
            st.write(report.why_it_got_views_and_likes)
            st.markdown('</div>', unsafe_allow_html=True)

        # Comment section drivers
        if hasattr(report, 'comment_section_triggers'):
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 💬 Why Viewers Left Comments & Engaged")
            st.write(report.comment_section_triggers)
            st.markdown('</div>', unsafe_allow_html=True)

        # Thumbnail & Title Synergy
        if hasattr(report, 'thumbnail_title_synergy'):
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 🖼️ Title & Thumbnail Click-Through Rate (CTR) Synergy")
            st.write(report.thumbnail_title_synergy)
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Pacing Meter Card
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Pacing & Editing Density Meter")
        
        cuts_count = report.estimated_cuts_per_minute
        bar_percentage = min(100, max(10, cuts_count * 3))
        
        st.markdown(f"**Pacing Speed:** <span class='tag-transition'>{report.pacing_rating}</span> &nbsp;&nbsp;|&nbsp;&nbsp; **Density:** <span class='tag-cut'>{cuts_count} cuts/min</span>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="pacing-bar-bg">
            <div class="pacing-bar-fill" style="width: {bar_percentage}%;"></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Hook Evaluation
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🪝 First 15-Second Retention Hook")
        st.write(report.script_hook_evaluation)
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    
    # Interactive Timeline Breakdown with Specific Tutorial Video Redirects
    st.markdown("### ⏱️ Cyberpunk Editing & Specific Video Tutorial Guide")
    
    for item in report.timeline:
        tag_style = get_tag_class(item.editing_type)
        query = getattr(item, 'tutorial_query', f"How to do {item.editing_type} video editing tutorial")
        tutorial_title = getattr(item, 'tutorial_title', f"How to do {item.editing_type}")
        quick_steps = getattr(item, 'quick_step_guide', "1. Import footage. 2. Apply effect/keyframe. 3. Adjust easing.")
        
        encoded_query = urllib.parse.quote(query)
        tutorial_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        
        st.markdown(f"""
        <div class="glass-card" style="padding: 18px 22px; margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
                <div>
                    <span class="time-badge">⏱️ {item.timestamp_start} - {item.timestamp_end}</span>
                    &nbsp;&nbsp;
                    <span class="{tag_style}">{item.editing_type}</span>
                </div>
                <div>
                    <a href="{tutorial_url}" target="_blank" class="learn-btn">▶️ Watch Tutorial Video</a>
                </div>
            </div>
            <div style="font-size: 0.98rem; color: #f1f5f9; margin-bottom: 6px;">
                <strong>Technique:</strong> {item.description}
            </div>
            <div style="font-size: 0.9rem; color: #38bdf8; margin-bottom: 6px;">
                🎬 <strong>Recommended Tutorial:</strong> <em>{tutorial_title}</em>
            </div>
            <div style="font-size: 0.88rem; color: #94a3b8; margin-bottom: 6px;">
                💡 <em>Viewer Retention Impact:</em> {item.engagement_impact}
            </div>
            <div style="font-size: 0.85rem; color: #cbd5e1; background: rgba(255,255,255,0.04); padding: 8px 12px; border-radius: 8px; margin-top: 6px;">
                🛠️ <strong>Quick How-To Recreate:</strong> {quick_steps}
            </div>
        </div>
        """, unsafe_allow_html=True)
