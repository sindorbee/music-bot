from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database import db
from keyboards.inline import get_favorites_keyboard, get_audio_player_keyboard

router = Router()

FAVS_PER_PAGE = 5

@router.message(F.text == "⭐️ Sevimlilarim")
async def show_user_favorites(message: Message):
    user_id = message.from_user.id
    total_count = await db.count_user_favorites(user_id)

    if total_count == 0:
        await message.answer(
            "⭐️ <b>Sizda hali saqlangan qo'shiqlar yo'q.</b>\n\n"
            "Musiqa tinglayotganingizda, uning ostidagi <b>«❤️ Sevimlilarga»</b> tugmasini bossangiz, "
            "qo'shiq bu yerda saqlanadi va xohlagan payt qayta eshita olasiz!",
            parse_mode="HTML"
        )
        return

    favs = await db.get_user_favorites(user_id, limit=FAVS_PER_PAGE, offset=0)
    total_pages = (total_count + FAVS_PER_PAGE - 1) // FAVS_PER_PAGE

    text = (
        f"⭐️ <b>Sizning sevimli qo'shiqlaringiz:</b>\n"
        f"<i>Jami: {total_count} ta qo'shiq</i>\n\n"
        f"Qo'shiqni eshitish uchun uning ustiga bosing:"
    )

    keyboard = get_favorites_keyboard(favs, current_page=1, total_pages=total_pages)
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data.startswith("favpg:"))
async def handle_favorites_pagination(call: CallbackQuery):
    user_id = call.from_user.id
    page_num = int(call.data.split(":")[1])

    total_count = await db.count_user_favorites(user_id)
    total_pages = (total_count + FAVS_PER_PAGE - 1) // FAVS_PER_PAGE

    if page_num < 1:
        page_num = 1
    elif page_num > total_pages:
        page_num = total_pages

    offset = (page_num - 1) * FAVS_PER_PAGE
    favs = await db.get_user_favorites(user_id, limit=FAVS_PER_PAGE, offset=offset)

    text = (
        f"⭐️ <b>Sizning sevimli qo'shiqlaringiz:</b>\n"
        f"<i>Jami: {total_count} ta qo'shiq (Sahifa {page_num})</i>\n\n"
        f"Qo'shiqni eshitish uchun uning ustiga bosing:"
    )

    keyboard = get_favorites_keyboard(favs, current_page=page_num, total_pages=total_pages)
    try:
        await call.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        pass
    await call.answer()

@router.callback_query(F.data.startswith("fav:"))
async def add_to_favorites(call: CallbackQuery):
    video_id = call.data.split(":", 1)[1]
    user_id = call.from_user.id

    cached = await db.get_cached_music(video_id)
    if not cached:
        await call.answer("Qo'shiq ma'lumoti topilmadi.", show_alert=True)
        return

    success = await db.add_favorite(
        user_id=user_id,
        video_id=video_id,
        title=cached.get("title", ""),
        artist=cached.get("artist", ""),
        duration=cached.get("duration", 0),
        file_id=cached.get("file_id", "")
    )

    if success:
        await call.answer("❤️ Sevimlilarga saqlandi!")
        # Tugmani yangilaymiz (endi "O'chirish" bo'ladi)
        try:
            await call.message.edit_reply_markup(
                reply_markup=get_audio_player_keyboard(
                    video_id,
                    is_fav=True,
                    share_query=f"{cached.get('artist', '')} - {cached.get('title', '')}"
                )
            )
        except Exception:
            pass
    else:
        await call.answer("Qo'shiq allaqachon sevimlilarda bor!")

@router.callback_query(F.data.startswith("unfav:"))
async def remove_from_favorites(call: CallbackQuery):
    video_id = call.data.split(":", 1)[1]
    user_id = call.from_user.id

    await db.remove_favorite(user_id, video_id)
    await call.answer("💔 Sevimlilardan olib tashlandi!")

    cached = await db.get_cached_music(video_id)
    artist = cached.get("artist", "") if cached else ""
    title = cached.get("title", "") if cached else ""

    try:
        await call.message.edit_reply_markup(
            reply_markup=get_audio_player_keyboard(
                video_id,
                is_fav=False,
                share_query=f"{artist} - {title}"
            )
        )
    except Exception:
        pass

@router.callback_query(F.data.startswith("delfav:"))
async def delete_favorite_item(call: CallbackQuery):
    video_id = call.data.split(":", 1)[1]
    user_id = call.from_user.id

    await db.remove_favorite(user_id, video_id)
    await call.answer("🗑 Qo'shiq o'chirildi!")

    # Ro'yxatni yangilaymiz
    total_count = await db.count_user_favorites(user_id)
    if total_count == 0:
        await call.message.edit_text(
            "⭐️ <b>Sevimlilar ro'yxati bo'shatildi.</b>",
            parse_mode="HTML"
        )
        return

    favs = await db.get_user_favorites(user_id, limit=FAVS_PER_PAGE, offset=0)
    total_pages = (total_count + FAVS_PER_PAGE - 1) // FAVS_PER_PAGE
    keyboard = get_favorites_keyboard(favs, current_page=1, total_pages=total_pages)

    text = (
        f"⭐️ <b>Sizning sevimli qo'shiqlaringiz:</b>\n"
        f"<i>Jami: {total_count} ta qo'shiq</i>\n\n"
        f"Qo'shiqni eshitish uchun uning ustiga bosing:"
    )

    try:
        await call.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        pass
