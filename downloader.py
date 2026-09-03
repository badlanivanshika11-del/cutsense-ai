import yt_dlp
import os
import ssl

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

def download_youtube_video(url: str, output_dir: str = "downloads") -> dict:
    """Downloads a YouTube video and returns metadata."""
    os.makedirs(output_dir, exist_ok=True)
    
    ydl_opts = {
        'format': 'mp4[height<=720]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'overwrites': True,
        'nocheckcertificate': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        
        return {
            "title": info.get("title", "Unknown Title"),
            "uploader": info.get("uploader", "Unknown Creator"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration", 0),
            "file_path": filename
        }
