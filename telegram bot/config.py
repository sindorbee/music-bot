import os
from pathlib import Path
from dotenv import load_dotenv

# .env yuklash
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Bot sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Admin ID lar (vergul bilan ajratilgan: masalan 1234567,9876543)
ADMINS = [int(admin_id.strip()) for admin_id in os.getenv("ADMINS", "").split(",") if admin_id.strip().isdigit()]

# Yuklab olish papkasi
DOWNLOADS_DIR = BASE_DIR / "downloads"
DOWNLOADS_DIR.mkdir(exist_ok=True)

# Ma'lumotlar bazasi fayli
DATABASE_PATH = BASE_DIR / "music_bot.db"

# FFmpeg yo'li
def get_ffmpeg_path():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

FFMPEG_PATH = get_ffmpeg_path()

# Maksimal fayl hajmi (Telegram botlar uchun 49MB limit)
MAX_FILE_SIZE_MB = 49
MAX_DURATION_SECONDS = 1200  # 20 daqiqagacha bo'lgan qo'shiqlar
