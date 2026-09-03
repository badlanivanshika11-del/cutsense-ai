import streamlit as st
import os
import importlib
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
    page_title="CutSense AI - YouTube & Instagram Reel Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Mobile & Laptop Responsive CSS
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Responsive Header Title */
    .hero-title {
        font-size: clamp(1.8rem, 5vw, 2.8rem);
        font-weight: 800;
        background: linear-gradient(135deg, #a855f7 0%, #3b82f6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .hero-subtitle {
        font-size: clamp(0.95rem, 2.5vw, 1.15rem);
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    /* Platform Badges */
    .platform-badge {
        display: inline-block;
        background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
        color: white;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.82rem;
    }

    /* Metric Badges */
    .metric-badge {
        display: inline-block;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.9rem;
    }

    .edit-tag {
        display: inline-block;
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
    }

    .time-badge {
        font-family: monospace;
        font-weight: 700;
        color: #f43f5e;
        background: rgba(244, 63, 94, 0.1);
        padding: 4px 8px;
        border-radius: 6px;
    }

    /* Responsive Buttons & Touch Targets for Mobile */
    .stButton > button {
        background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-size: 1rem !important;
        min-height: 48px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(139, 92, 246, 0.6) !important;
    }

    /* Mobile Media Query Adjustments */
    @media (max-width: 768px) {
        .glass-card {
            padding: 12px;
            margin-bottom: 10px;
        }
        .stButton > button {
            width: 100% !important;
        }
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# App Header
st.markdown('<div class="hero-title">🎬 CutSense AI Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Deconstruct editing cuts, transitions & retention hooks for <b>YouTube Videos & Instagram Reels</b>.</div>', unsafe_allow_html=True)

# Sidebar Settings
with st.sidebar:
    st.markdown("### ⚙️ Studio Settings")
    user_api_key = st.text_input("Gemini API Key:", type="password", help="Enter your Gemini API key from https://aistudio.google.com/")
    
    st.markdown("---")
    st.markdown("### 📱 Mobile & Desktop Apps")
    st.markdown("Add this site to your Phone Home Screen for native app usage!")
    st.markdown("---")
    st.caption("Crafted for Video Editors & Content Creators")

# Input Section (YouTube + Instagram Reels)
video_url = st.text_input("Enter YouTube Video or Instagram Reel URL:", placeholder="Paste YouTube link or https://www.instagram.com/reel/...")

if st.button("🚀 Analyze Video / Reel", use_container_width=True):
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
            
            with st.spinner("Step 2/2: Gemini AI is analyzing frame edits & retention hooks..."):
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
    
    # Responsive Columns
    col1, col2 = st.columns([1.1, 1.9])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"#### 📽️ {platform_label} Preview")
        if metadata.get("thumbnail"):
            st.image(metadata["thumbnail"], use_container_width=True)
        st.video(metadata["file_path"])
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
        # Pacing Cards
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Pacing & Editing Density")
        
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"**Overall Pacing:** <span class='metric-badge'>{report.pacing_rating}</span>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"**Est. Cuts / Min:** <span class='metric-badge'>{report.estimated_cuts_per_minute} cuts/min</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Hook Evaluation
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🪝 First 15-Second Retention Hook")
        st.write(report.script_hook_evaluation)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Thumbnail Analysis
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🖼️ Visual Clickability / Cover Analysis")
        st.write(report.thumbnail_analysis)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Top Drivers
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🔥 Top Engagement Drivers")
        for driver in report.top_engagement_drivers:
            st.markdown(f"• **{driver}**")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    
    # Interactive Timeline Breakdown
    st.markdown("### ⏱️ Timestamped Editing & Transition Timeline")
    
    for item in report.timeline:
        st.markdown(f"""
        <div class="glass-card" style="padding: 14px 20px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div>
                    <span class="time-badge">⏱️ {item.timestamp_start} - {item.timestamp_end}</span>
                    &nbsp;
                    <span class="edit-tag">{item.editing_type}</span>
                </div>
            </div>
            <div style="font-size: 0.95rem; color: #e2e8f0; margin-bottom: 6px;">
                <strong>Edit Technique:</strong> {item.description}
            </div>
            <div style="font-size: 0.88rem; color: #94a3b8;">
                💡 <em>Viewer Retention Impact:</em> {item.engagement_impact}
            </div>
        </div>
        """, unsafe_allow_html=True)
