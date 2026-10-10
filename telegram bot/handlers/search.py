from aiogram import Router, types, F
from aiogram.types import Message, CallbackQuery
from database import db
from services.music_service import music_service
from keyboards.inline import get_search_results_keyboard, get_genres_keyboard
from utils.cache import search_cache

router = Router()

GENRE_MAP = {
    "uzbek_hits": ("🇺🇿 O'zbek Xitlar", "uzbek yangi xit qoshiqlar 2025"),
    "uzbek_rap": ("🎤 O'zbek Rep & Hip-Hop", "uzbek rep yangilari Konsta Timur Alixonov Masa"),
    "russian_rap": ("🇷🇺 Ruscha Rep & Xitlar", "russian rap top hits Macan Miyagi"),
    "world_pop": ("🌍 Jahon Pop (World)", "top billboard pop hits"),
    "bass_remix": ("⚡️ Bass & Remix", "bass boosted car remix track"),
    "retro_uzbek": ("📻 Retro & Milliy", "ozbek retro mumtoz qoshiqlari"),
    "tiktok_trends": ("🔥 TikTok Trend Musiqalar", "tiktok trend music xit"),
}

def format_search_message(query: str, items: list, page: int = 1, per_page: int = 5) -> str:
    """Qidiruv natijalari xabar matnini chiroyli formatlash"""
    total_items = len(items)
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    page_items = items[start_idx:end_idx]

    lines = [
        f"🎵 <b>Qidiruv natijalari:</b> «{query}»",
        f"<i>Topildi: {total_items} ta natija (Sahifa {page})</i>\n"
    ]

    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    for i, item in enumerate(page_items):
        num_str = emojis[start_idx + i] if (start_idx + i) < len(emojis) else f"[{start_idx + i + 1}]"
        artist = item.get("artist", "")
        title = item.get("title", "")
        duration = item.get("duration_str", "00:00")
        lines.append(f"{num_str} <b>{artist}</b> - {title} <code>[{duration}]</code>")

    lines.append("\n👇 <i>Eshitish va yuklab olish uchun pastdagi raqamni bosing:</i>")
    return "\n".join(lines)

@router.message(F.text == "🔍 Musiqa qidirish")
async def ask_for_search(message: Message):
    await message.answer(
        "🔎 <b>Qidirmoqchi bo'lgan musiqa yoki ijrochi nomini yozing:</b>\n\n"
        "Masalan: <code>Konsta</code>, <code>Xamdam Sobirov</code>, <code>Macan</code>, <code>Eminem</code>",
        parse_mode="HTML"
    )

@router.message(F.text == "🔥 Trend Xitlar")
async def show_trending_hits(message: Message):
    status_msg = await message.answer("🔥 <i>Trenddagi xitlar yuklanmoqda...</i>", parse_mode="HTML")
    results = await music_service.search("uzbek xit qoshiqlar 2025 2026", limit=10)
    
    if not results:
        await status_msg.edit_text("❌ Trend qo'shiqlar topilmadi. Qayta urinib ko'ring.")
        return

    search_id = search_cache.save_search(results, "Trend Xitlar 2025/2026")
    msg_text = format_search_message("🔥 Trend Xitlar", results, page=1)
    keyboard = get_search_results_keyboard(search_id, results, current_page=1)
    
    await status_msg.edit_text(msg_text, reply_markup=keyboard, parse_mode="HTML")

@router.message(F.text == "📁 Janrlar (Rep, Pop...)")
async def show_genres(message: Message):
    await message.answer(
        "📁 <b>Musiqa janrini tanlang:</b>\n\n"
        "O'zingizga yoqqan yo'nalishdagi eng sara qo'shiqlarni bir zumda toping!",
        reply_markup=get_genres_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("gn:"))
async def handle_genre_select(call: CallbackQuery):
    genre_key = call.data.split(":", 1)[1]
    if genre_key not in GENRE_MAP:
        await call.answer("Bunday janr mavjud emas!", show_alert=True)
        return

    genre_name, search_query = GENRE_MAP[genre_key]
    await call.answer(f"«{genre_name}» saralanmoqda...")
    await call.message.edit_text(f"⏳ <b>{genre_name}</b> bo'yicha sara qo'shiqlar qidirilmoqda...", parse_mode="HTML")

    results = await music_service.search(search_query, limit=10)
    if not results:
        await call.message.edit_text(f"❌ {genre_name} bo'yicha hech narsa topilmadi.")
        return

    search_id = search_cache.save_search(results, genre_name)
    msg_text = format_search_message(genre_name, results, page=1)
    keyboard = get_search_results_keyboard(search_id, results, current_page=1)

    await call.message.edit_text(msg_text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data.startswith("pg:"))
async def handle_pagination(call: CallbackQuery):
    parts = call.data.split(":")
    if len(parts) != 3:
        await call.answer()
        return

    search_id = parts[1]
    try:
        page = int(parts[2])
    except ValueError:
        page = 1

    cached = search_cache.get_search(search_id)
    if not cached:
        await call.answer("⚠️ Qidiruv muddati tugagan. Iltimos, qaytadan qidiring.", show_alert=True)
        return

    items = cached["items"]
    query = cached["query"]

    msg_text = format_search_message(query, items, page=page)
    keyboard = get_search_results_keyboard(search_id, items, current_page=page)

    try:
        await call.message.edit_text(msg_text, reply_markup=keyboard, parse_mode="HTML")
        await call.answer()
    except Exception:
        await call.answer()

@router.message(F.text)
async def handle_search_text(message: Message):
    query = message.text.strip()
    # Menyu tugmalari bo'lsa o'tkazib yuboramiz
    if query in ["⭐️ Sevimlilarim", "ℹ️ Bot haqida", "🎲 Tasodifiy musiqa", "❌ Bekor qilish"]:
        return

    if len(query) < 2:
        await message.answer("⚠️ Qidirish uchun kamida 2 ta harf kiriting.")
        return

    await db.increment_searches()

    status_msg = await message.answer(
        f"🔎 <b>Qidirilmoqda:</b> «<i>{query}</i>»...\n<i>Biroz kuting...</i>",
        parse_mode="HTML"
    )

    results = await music_service.search(query, limit=10)
    if not results:
        await status_msg.edit_text(
            f"❌ «<b>{query}</b>» bo'yicha hech qanday musiqa topilmadi.\n\n"
            f"Iltimos, nomini to'g'ri yozganingizga ishonch hosil qiling yoki boshqa nom bilan qidiring.",
            parse_mode="HTML"
        )
        return

    search_id = search_cache.save_search(results, query)
    msg_text = format_search_message(query, results, page=1)
    keyboard = get_search_results_keyboard(search_id, results, current_page=1)

    await status_msg.edit_text(msg_text, reply_markup=keyboard, parse_mode="HTML")
