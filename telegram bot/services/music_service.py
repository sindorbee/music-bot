import os
import re
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from pathlib import Path
import yt_dlp
from config import DOWNLOADS_DIR, FFMPEG_PATH, MAX_DURATION_SECONDS

def format_duration(seconds: Optional[int]) -> str:
    """Soniyalarni mm:ss yoki hh:mm:ss formatga o'tkazish"""
    if not seconds or seconds < 0:
        return "00:00"
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def clean_title(title: str) -> str:
    """Qo'shiq nomidagi keraksiz so'zlarni tozalash (masalan: [Official Video], klip va h.k.)"""
    if not title:
        return "Noma'lum qo'shiq"
    patterns = [
        r"\[.*?\]",
        r"\(Official.*?\)",
        r"\(Music Video.*?\)",
        r"\(Audio.*?\)",
        r"\(Lyrics.*?\)",
        r"\(Premyera.*?\)",
        r"\(Klip.*?\)",
        r"\(Official Klip.*?\)",
        r"\(Video.*?\)",
        r"#\S+",
    ]
    cleaned = title
    for pat in patterns:
        cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if cleaned else title

def parse_artist_and_title(raw_title: str, uploader: str = ""):
    """Artist va qo'shiq nomini ajratish"""
    cleaned = clean_title(raw_title)
    if " - " in cleaned:
        parts = cleaned.split(" - ", 1)
        artist = parts[0].strip()
        song_title = parts[1].strip()
    else:
        artist = uploader.replace(" - Topic", "").strip() if uploader else "Musiqa"
        song_title = cleaned
    return artist, song_title

class MusicService:
    def __init__(self):
        self.ffmpeg_path = FFMPEG_PATH

    def _sync_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Sinxron YouTube qidiruv (yt-dlp orqali)"""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "skip_download": True,
        }

        # Agar YouTube havolasi bo'lsa
        if "youtube.com" in query or "youtu.be" in query:
            search_query = query
        else:
            search_query = f"ytsearch{limit * 2}:{query}"

        results = []
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_query, download=False)
                if not info:
                    return []

                entries = info.get("entries", []) if "entries" in info else [info]
                for item in entries:
                    if not item:
                        continue
                    
                    video_id = item.get("id")
                    if not video_id:
                        continue

                    duration = item.get("duration") or 0
                    # Cheklov: 20 daqiqadan oshmagan qo'shiqlar
                    if duration > MAX_DURATION_SECONDS:
                        continue

                    raw_title = item.get("title", "Noma'lum")
                    uploader = item.get("uploader") or item.get("channel") or ""
                    artist, song_title = parse_artist_and_title(raw_title, uploader)

                    thumbnails = item.get("thumbnails", [])
                    thumbnail_url = thumbnails[-1].get("url") if thumbnails else None

                    results.append({
                        "id": video_id,
                        "title": song_title,
                        "raw_title": raw_title,
                        "artist": artist,
                        "duration": duration,
                        "duration_str": format_duration(duration),
                        "thumbnail": thumbnail_url,
                        "url": f"https://www.youtube.com/watch?v={video_id}"
                    })

                    if len(results) >= limit:
                        break

        except Exception as e:
            print(f"Qidiruvda xatolik: {e}")
        return results

    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Asinxron qidiruv chaqiruvi"""
        return await asyncio.to_thread(self._sync_search, query, limit)

    def _sync_download(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Sinxron qo'shiq yuklab olish va mp3 formatga o'tkazish"""
        output_template = str(DOWNLOADS_DIR / f"{video_id}.%(ext)s")
        target_mp3 = DOWNLOADS_DIR / f"{video_id}.mp3"

        # Agar oldin yuklangan bo'lsa
        if target_mp3.exists() and target_mp3.stat().st_size > 1000:
            return {
                "audio_path": target_mp3,
                "video_id": video_id,
            }

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "ffmpeg_location": self.ffmpeg_path,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "quiet": True,
            "no_warnings": True,
            "max_filesize": 49 * 1024 * 1024,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
                if not info:
                    return None

                raw_title = info.get("title", "")
                uploader = info.get("uploader") or info.get("channel") or ""
                artist, song_title = parse_artist_and_title(raw_title, uploader)
                duration = info.get("duration") or 0
                thumbnail_url = info.get("thumbnail")

                if target_mp3.exists():
                    return {
                        "audio_path": target_mp3,
                        "video_id": video_id,
                        "title": song_title,
                        "artist": artist,
                        "duration": int(duration),
                        "thumbnail_url": thumbnail_url,
                    }
        except Exception as e:
            print(f"Yuklab olishda xatolik ({video_id}): {e}")
            return None
        return None

    async def download(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Asinxron qo'shiq yuklab olish"""
        result = await asyncio.to_thread(self._sync_download, video_id)
        if not result:
            return None

        # Muqovani (thumbnail) yuklab olish
        thumb_path = None
        if result.get("thumbnail_url"):
            try:
                thumb_path = DOWNLOADS_DIR / f"{video_id}_thumb.jpg"
                async with aiohttp.ClientSession() as session:
                    async with session.get(result["thumbnail_url"], timeout=10) as resp:
                        if resp.status == 200:
                            content = await resp.read()
                            with open(thumb_path, "wb") as f:
                                f.write(content)
                            result["thumb_path"] = thumb_path
            except Exception as e:
                print(f"Thumbnail yuklashda xatolik: {e}")

        return result

    def cleanup_file(self, *paths):
        """Vaqtinchalik yuklangan fayllarni tozalash"""
        for p in paths:
            if p:
                try:
                    path_obj = Path(p)
                    if path_obj.exists():
                        path_obj.unlink()
                except Exception as e:
                    print(f"Fayl o'chirishda xatolik: {e}")

music_service = MusicService()
