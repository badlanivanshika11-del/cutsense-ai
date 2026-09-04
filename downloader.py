import yt_dlp
import os
import ssl

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

def download_video(url: str, output_dir: str = "downloads") -> dict:
    """Downloads lightweight 360p video stream for ultra-fast download and AI analysis speed."""
    os.makedirs(output_dir, exist_ok=True)
    is_instagram = "instagram.com" in url.lower() or "instagr.am" in url.lower()
    platform_name = "Instagram Reel" if is_instagram else "YouTube Video"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    # Fast 360p stream selector for ultra-fast download & AI upload
    options_list = [
        {
            'format': 'b[height<=360]/best[height<=480]/best',
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'overwrites': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'http_headers': headers,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web', 'mweb'],
                }
            },
            'quiet': True,
        },
        {
            'format': 'b/best',
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'overwrites': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'quiet': True,
        }
    ]

    last_error = None
    for opts in options_list:
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
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
        except Exception as e:
            last_error = e
            continue

    raise Exception(f"Unable to download video stream after fallback attempts: {str(last_error)}")

# Alias for backwards compatibility
download_youtube_video = download_video
