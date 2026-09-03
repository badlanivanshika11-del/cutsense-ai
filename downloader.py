import yt_dlp
import os
import ssl

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

def download_video(url: str, output_dir: str = "downloads") -> dict:
    """Downloads a YouTube video or Instagram Reel and returns metadata."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Custom headers to bypass Instagram / YouTube bot detection
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    ydl_opts = {
        'format': 'mp4[height<=720]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'overwrites': True,
        'nocheckcertificate': True,
        'http_headers': headers,
        'quiet': False,
    }
    
    # Platform detection
    is_instagram = "instagram.com" in url.lower() or "instagr.am" in url.lower()
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        
        platform_name = "Instagram Reel" if is_instagram else "YouTube Video"
        title = info.get("title") or info.get("description") or f"{platform_name} Analysis"
        if len(title) > 60:
            title = title[:57] + "..."
            
        return {
            "title": title,
            "uploader": info.get("uploader") or info.get("channel") or info.get("uploader_id") or "Creator",
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration", 0),
            "platform": platform_name,
            "file_path": filename
        }

# Alias for backwards compatibility
download_youtube_video = download_video
