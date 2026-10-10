import sys
import os
import asyncio
import logging

# Windows konsolida UTF-8 va emojilar to'g'ri ko'rinishi uchun
if sys.platform.startswith("win"):
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database import db
from handlers import start, search, download, favorites, inline_mode

# Loglarni sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("MusicBot")

async def main():
    if not BOT_TOKEN or BOT_TOKEN == "SIZNING_BOT_TOKENINGIZ":
        logger.error(
            "\n" + "="*60 + "\n"
            "❌ DIQQAT! BOT_TOKEN ko'rsatilmagan!\n"
            "Iltimos, '.env' faylini oching va Telegram @BotFather'dan olgan\n"
            "TOKENingizni quyidagicha yozing:\n\n"
            "BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ\n"
            + "="*60
        )
        return

    # Ma'lumotlar bazasini ishga tushiramiz
    logger.info("Ma'lumotlar bazasi ishga tushirilmoqda...")
    await db.init_db()

    # Bot va Dispatcherni yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Routerlarni ulash
    dp.include_router(start.router)
    dp.include_router(favorites.router)
    dp.include_router(download.router)
    dp.include_router(search.router)
    dp.include_router(inline_mode.router)

    # Eski kutilayotgan yangilanishlarni tozalash
    await bot.delete_webhook(drop_pending_updates=True)

    bot_info = await bot.get_me()
    logger.info(f"Bot muvaffaqiyatli ishga tushdi: @{bot_info.username} ({bot_info.first_name})")
    print(f"\n🚀 Bot ishlayapti: https://t.me/{bot_info.username}\n")

    # Render va boshqa bulutli hostinglar uchun web server (health check)
    port = int(os.environ.get("PORT", 0))
    runner = None
    if port:
        from aiohttp import web
        app = web.Application()
        app.router.add_get("/", lambda r: web.Response(text="Bot is running!"))
        app.router.add_get("/health", lambda r: web.Response(text="OK"))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        logger.info(f"Web server {port}-portda ishga tushdi (Render uchun).")

    try:
        await dp.start_polling(bot)
    finally:
        if runner:
            await runner.cleanup()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
