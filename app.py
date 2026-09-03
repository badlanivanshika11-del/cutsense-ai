import streamlit as st
import os
import importlib
import downloader
import analyzer
import report_generator
from downloader import download_youtube_video
from analyzer import analyze_video_with_gemini
from report_generator import generate_pdf_report, generate_csv_report

# Force fresh module load
importlib.reload(analyzer)
importlib.reload(downloader)
importlib.reload(report_generator)

st.set_page_config(
    page_title="CutSense AI - Video Editing & Retention Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling Injection
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Header Gradient Title */
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a855f7 0%, #3b82f6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .hero-subtitle {
        font-size: 1.15rem;
        color: #94a3b8;
        margin-bottom: 2rem;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    /* Metric Cards */
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

    /* Streamlit Button Customization */
    .stButton > button {
        background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(139, 92, 246, 0.6) !important;
    }

    /* Input Field Styling */
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        background: rgba(15, 23, 42, 0.6) !important;
        color: #f8fafc !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# App Header
st.markdown('<div class="hero-title">🎬 CutSense AI Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Deconstruct complex YouTube editing styles, cut-rates, transitions & retention drivers using Gemini 3.6 Flash.</div>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Studio Settings")
    user_api_key = st.text_input("Gemini API Key:", type="password", help="Enter your Gemini API key from https://aistudio.google.com/")
    
    st.markdown("---")
    st.markdown("### 📌 Features")
    st.markdown("""
    - ⚡ **Cut & Transition Detection**
    - 🪝 **First 15s Hook Evaluation**
    - 🖼️ **Thumbnail Clickability Score**
    - 🔥 **Viewer Retention Drivers**
    - ⏱️ **Timestamped Edit Breakdown**
    - 📄 **PDF & CSV Exporting**
    """)
    st.markdown("---")
    st.caption("Crafted for Video Editors & Content Creators")

# Main Input Section
url_col, btn_col = st.columns([4, 1])
with url_col:
    youtube_url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...", label_visibility="collapsed")
with btn_col:
    analyze_click = st.button("🚀 Analyze Edits", use_container_width=True)

if analyze_click:
    api_key_to_use = user_api_key or os.environ.get("GEMINI_API_KEY")
    
    if not youtube_url:
        st.warning("Please enter a valid YouTube URL.")
    elif not api_key_to_use:
        st.error("Please enter your Gemini API Key in the sidebar or set the GEMINI_API_KEY environment variable.")
    else:
        try:
            with st.spinner("Step 1/2: Downloading video stream & metadata..."):
                metadata = download_youtube_video(youtube_url)
                
            st.session_state["metadata"] = metadata
            
            with st.spinner("Step 2/2: Gemini AI is analyzing frame edits, cuts, and retention hooks..."):
                report = analyze_video_with_gemini(metadata["file_path"], api_key=api_key_to_use)
                st.session_state["report"] = report

        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")

# Display Results from Session State if available
if "metadata" in st.session_state and "report" in st.session_state:
    metadata = st.session_state["metadata"]
    report = st.session_state["report"]
    
    st.success(f"Loaded Analysis for: **{metadata['title']}** (Creator: {metadata['uploader']})")
    
    col1, col2 = st.columns([1.1, 1.9])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 📽️ Video Preview & Thumbnail")
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
                file_name=f"CutSense_Report_{metadata.get('title', 'video')[:15]}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with d_col2:
            st.download_button(
                label="📊 CSV Data",
                data=csv_str,
                file_name=f"CutSense_Timeline_{metadata.get('title', 'video')[:15]}.csv",
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
            st.markdown(f"**Overall Pacing Speed:** <span class='metric-badge'>{report.pacing_rating}</span>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"**Estimated Cuts / Min:** <span class='metric-badge'>{report.estimated_cuts_per_minute} cuts/min</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Hook Evaluation
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🪝 First 15-Second Retention Hook")
        st.write(report.script_hook_evaluation)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Thumbnail Analysis
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🖼️ Thumbnail & Visual Clickability")
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
