import yt_dlp
import os
import ssl

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

def download_video(url: str, output_dir: str = "downloads") -> dict:
    """Downloads YouTube Videos, Shorts, and Instagram Reels with SABR-immune client rotation."""
    os.makedirs(output_dir, exist_ok=True)
    is_instagram = "instagram.com" in url.lower() or "instagr.am" in url.lower()
    platform_name = "Instagram Reel" if is_instagram else "YouTube Video"

    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    # SABR & Cloud-403 Immune Fallback Strategy
    options_list = [
        # Layer 1: iOS & Android Client (Bypasses SABR-only streaming experiment & 403 Forbidden)
        {
            'format': 'b/best',
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'overwrites': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'http_headers': headers,
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android'],
                }
            },
            'quiet': True,
        },
        # Layer 2: Mobile Web & Android VR Client
        {
            'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]/best',
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'overwrites': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['mweb', 'android_vr'],
                }
            },
            'quiet': True,
        },
        # Layer 3: TV Embedded Client
        {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'overwrites': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['tv_embedded', 'tv'],
                }
            },
            'quiet': True,
        },
        # Layer 4: Universal Emergency Fallback
        {
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'overwrites': True,
            'nocheckcertificate': True,
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

    raise Exception(f"Unable to download video stream after 4 fallback attempts: {str(last_error)}")

# Alias for backwards compatibility
download_youtube_video = download_video
