# 🎬 CutSense AI - Video Editing & Audience Retention Studio

> Deconstruct complex YouTube video editing styles, frame transitions, cut rates, script hooks, and audience engagement drivers using **Google Gemini 3.6 Flash**.

![CutSense AI Studio](https://img.shields.io/badge/AI-Gemini%203.6%20Flash-purple)
![Framework](https://img.shields.io/badge/UI-Streamlit-red)
![Language](https://img.shields.io/badge/Python-3.12-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🌟 Key Features

- **⚡ Frame-Level Cut & Transition Detection**: Detects fast cuts, whip-pans, zooms, B-roll overlays, and motion graphics.
- **🪝 First 15-Second Retention Hook Evaluation**: Evaluates the psychological hook of the video's intro.
- **🖼️ Thumbnail & Visual Clickability Scoring**: Analyzes visual contrast, text hierarchy, and clickability.
- **📊 Pacing & Editing Density**: Calculates cuts per minute and pacing speed.
- **📄 Client Export Reports**: Download styled **PDF** and **CSV** reports for clients and editing teams.
- **💎 Dark Glassmorphic UI**: Sleek, modern responsive interface built with Streamlit and custom CSS.

---

## 🏗️ Architecture

```
[ YouTube URL ] ──> [ yt-dlp Video Extractor ]
                           │
                           ▼
               [ Gemini 3.6 Flash API ]
             (Pydantic Structured Output)
                           │
                           ▼
          [ CutSense AI Streamlit Studio ]
     ├── Glassmorphic Dashboard UI
     ├── Interactive Editing Timeline
     └── PDF / CSV Report Generator
```

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/cutsense-ai.git
cd cutsense-ai
```

### 2. Set Up Virtual Environment & Install Dependencies
```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Run the App
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 🛠️ Built With

* **Python 3.12**
* **Google Gemini 3.6 Flash API** (`google-genai` SDK)
* **Streamlit** (Web Dashboard Framework)
* **yt-dlp** (YouTube Video & Metadata Extraction)
* **Pydantic** (Structured AI Output Validation)
* **ReportLab** (PDF Report Generation)

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
