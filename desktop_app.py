import os
import sys
import subprocess
import webbrowser
import time

def main():
    print("====================================================")
    print("  🚀 Starting CutSense AI Studio Desktop App...     ")
    print("====================================================")
    
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    
    # Launch Streamlit server locally
    cmd = [sys.executable, "-m", "streamlit", "run", app_path, "--server.headless", "true"]
    process = subprocess.Popen(cmd)
    
    print("\nOpening CutSense AI in your browser at http://localhost:8501 ...")
    time.sleep(3)
    webbrowser.open("http://localhost:8501")
    
    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()

if __name__ == "__main__":
    main()
