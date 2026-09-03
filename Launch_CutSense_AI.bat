@echo off
title CutSense AI Studio Desktop Launcher
echo Launching CutSense AI Studio...
cd /d "%~dp0"
call venv\Scripts\activate
streamlit run app.py
pause
