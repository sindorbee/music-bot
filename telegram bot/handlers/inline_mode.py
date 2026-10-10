from aiogram import Router
from aiogram.types import (
    InlineQuery,
    InlineQueryResultAudio,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from services.music_service import music_service
from database import db

router = Router()

@router.inline_query()
async def inline_music_search(inline_query: InlineQuery):
    query = inline_query.query.strip()
    bot_info = await inline_query.bot.get_me()

    if not query:
        # Bo'sh qidiruvda tavsiya ko'rsatish
        items = [
            InlineQueryResultArticle(
                id="help",
                title="🔍 Musiqa qidirish",
                description=f"Qidirmoqchi bo'lgan qo'shiq yoki artist nomini yozing",
                input_message_content=InputTextMessageContent(
                    message_text=f"🎵 @{bot_info.username} orqali istalgan qo'shiqni qidirishingiz mumkin!"
                )
            )
        ]
        await inline_query.answer(items, cache_time=10, is_personal=True)
        return

    # Qidiruv o'tkazamiz
    search_results = await music_service.search(query, limit=5)
    results = []

    for item in search_results:
        video_id = item["id"]
        title = item["title"]
        artist = item["artist"]
        duration = item.get("duration", 0)

        # 1. Agar keshda bo'lsa - to'g'ridan-to'g'ri Audio sifatida yuboriladi!
        cached = await db.get_cached_music(video_id)
        if cached and cached.get("file_id"):
            results.append(
                InlineQueryResultAudio(
                    id=video_id,
                    audio_file_id=cached["file_id"],
                    caption=f"🎧 <b>{title}</b>\n👤 <b>Ijrochi:</b> {artist}\n\n🤖 @{bot_info.username}",
                    parse_mode="HTML"
                )
            )
        else:
            # 2. Agar keshda bo'lmasa - yuklab olish havolasi ko'rsatiladi
            kb = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="📥 Bot orqali yuklab olish",
                    url=f"https://t.me/{bot_info.username}?start=dl_{video_id}"
                )
            ]])
            results.append(
                InlineQueryResultArticle(
                    id=video_id,
                    title=f"🎵 {artist} - {title}",
                    description=f"⏱ {item.get('duration_str', '00:00')} | Yuklab olish uchun bosing",
                    thumbnail_url=item.get("thumbnail"),
                    input_message_content=InputTextMessageContent(
                        message_text=(
                            f"🎧 <b>{title}</b>\n"
                            f"👤 <b>Ijrochi:</b> {artist}\n"
                            f"⏱ <b>Davomiyligi:</b> {item.get('duration_str')}\n\n"
                            f"Pastdagi havola orqali yuklab oling 👇"
                        ),
                        parse_mode="HTML"
                    ),
                    reply_markup=kb
                )
            )

    await inline_query.answer(results, cache_time=300, is_personal=False)
