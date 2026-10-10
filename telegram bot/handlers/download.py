from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, FSInputFile
from database import db
from services.music_service import music_service, format_duration
from keyboards.inline import get_audio_player_keyboard

router = Router()

async def send_music_to_chat(
    bot: Bot,
    chat_id: int,
    user_id: int,
    video_id: str,
    status_msg: Message = None
) -> bool:
    """Foydalanuvchiga musiqani yuborish (keshdan yoki yuklab olib)"""
    bot_info = await bot.get_me()

    # 1. Keshni tekshirish
    cached = await db.get_cached_music(video_id)
    if cached:
        is_fav = await db.is_favorite(user_id, video_id)
        artist = cached.get("artist", "Musiqa")
        title = cached.get("title", "")
        duration_str = format_duration(cached.get("duration", 0))

        caption = (
            f"🎧 <b>{title}</b>\n"
            f"👤 <b>Ijrochi:</b> {artist}\n"
            f"⏱ <b>Davomiyligi:</b> {duration_str}\n\n"
            f"🤖 @{bot_info.username} orqali yuklandi"
        )

        try:
            await bot.send_audio(
                chat_id=chat_id,
                audio=cached["file_id"],
                title=title,
                performer=artist,
                duration=cached.get("duration", 0),
                caption=caption,
                parse_mode="HTML",
                reply_markup=get_audio_player_keyboard(
                    video_id,
                    is_fav=is_fav,
                    share_query=f"{artist} - {title}"
                )
            )
            if status_msg:
                try:
                    await status_msg.delete()
                except Exception:
                    pass
            return True
        except Exception as e:
            print(f"Keshdan yuborishda xatolik: {e}, qayta yuklanadi...")

    # 2. Yangidan yuklab olish
    if not status_msg:
        status_msg = await bot.send_message(
            chat_id=chat_id,
            text="⏳ <b>Musiqa yuklanmoqda va tayyorlanmoqda...</b>\n<i>Iltimos kuting...</i>",
            parse_mode="HTML"
        )

    data = await music_service.download(video_id)
    if not data or not data.get("audio_path"):
        await status_msg.edit_text(
            "❌ <b>Kechirasiz!</b> Ushbu musiqani yuklab olish imkoni bo'lmadi (hajm yoki mualliflik cheklovi tufayli).\n"
            "Boshqa musiqani tanlab ko'ring.",
            parse_mode="HTML"
        )
        return False

    artist = data.get("artist", "Musiqa")
    title = data.get("title", "Noma'lum")
    duration = data.get("duration", 0)
    duration_str = format_duration(duration)

    caption = (
        f"🎧 <b>{title}</b>\n"
        f"👤 <b>Ijrochi:</b> {artist}\n"
        f"⏱ <b>Davomiyligi:</b> {duration_str}\n\n"
        f"🤖 @{bot_info.username} orqali yuklandi"
    )

    is_fav = await db.is_favorite(user_id, video_id)
    audio_file = FSInputFile(str(data["audio_path"]))
    thumb_file = FSInputFile(str(data["thumb_path"])) if data.get("thumb_path") else None

    try:
        sent_audio = await bot.send_audio(
            chat_id=chat_id,
            audio=audio_file,
            title=title,
            performer=artist,
            duration=duration,
            thumbnail=thumb_file,
            caption=caption,
            parse_mode="HTML",
            reply_markup=get_audio_player_keyboard(
                video_id,
                is_fav=is_fav,
                share_query=f"{artist} - {title}"
            )
        )

        if sent_audio.audio:
            await db.save_music_cache(
                video_id=video_id,
                title=title,
                artist=artist,
                duration=duration,
                file_id=sent_audio.audio.file_id,
                file_unique_id=sent_audio.audio.file_unique_id
            )

        await status_msg.delete()
        return True
    except Exception as e:
        print(f"Audioni yuborishda xatolik: {e}")
        await status_msg.edit_text("❌ Musiqani yuborishda xatolik yuz berdi.")
        return False
    finally:
        music_service.cleanup_file(data.get("audio_path"), data.get("thumb_path"))

@router.callback_query(F.data.startswith("dl:"))
async def handle_download_callback(call: CallbackQuery):
    video_id = call.data.split(":", 1)[1]
    user_id = call.from_user.id
    
    # Callbackga tezkor javob
    await call.answer("⚡️ Musiqa tayyorlanmoqda...")
    await send_music_to_chat(
        bot=call.bot,
        chat_id=call.message.chat.id,
        user_id=user_id,
        video_id=video_id
    )

@router.callback_query(F.data == "new_search")
async def handle_new_search_click(call: CallbackQuery):
    await call.answer()
    await call.message.answer(
        "🔎 <b>Qidirmoqchi bo'lgan qo'shiq yoki ijrochi nomini yozing:</b>",
        parse_mode="HTML"
    )

@router.callback_query(F.data == "close_msg")
async def handle_close_msg(call: CallbackQuery):
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.answer()

@router.callback_query(F.data == "noop")
async def handle_noop(call: CallbackQuery):
    await call.answer()
