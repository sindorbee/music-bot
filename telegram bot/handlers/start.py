import random
from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message
from database import db
from keyboards.default import get_main_menu
from keyboards.inline import get_audio_player_keyboard
from services.music_service import music_service
from handlers.download import send_music_to_chat

router = Router()

START_TEXT = """
👋 <b>Assalomu alaykum, {name}!</b>

🎵 <b>Zamonaviy Musiqa Botiga xush kelibsiz!</b>

Bu bot orqali siz:
🔹 <b>Har qanday qo'shiq</b>ni (nomi yoki ijrochisi bo'yicha) topishingiz;
🔹 <b>O'zbekcha xitlar, Rep, Pop, Ruscha va Jahon musiqalari</b>ni yuklab olishingiz;
🔹 Sevimli qo'shiqlaringizni saqlab qo'yishingiz;
🔹 Do'stlaringizga bitta tugma bilan ulashishingiz mumkin!

🔍 <i>Qo'shiq topish uchun uning nomini yoki ijrochini yozib yuboring (masalan: <code>Konsta</code>, <code>Xamdam Sobirov</code>, <code>Macan</code>, <code>Eminem</code>).</i>
"""

HELP_TEXT = """
📖 <b>Botdan foydalanish bo'yicha qo'llanma:</b>

1️⃣ <b>Qidiruv:</b>
Oddiygina qo'shiq nomi yoki ijrochisini xabar qilib yuboring. Masalan:
👉 <code>Konsta Odamlar nima deydi</code>
👉 <code>Jaloliddin Ahmadaliyev</code>
👉 <code>Miyagi</code>

2️⃣ <b>Janrlar va Trendlar:</b>
Menyudagi <b>«🔥 Trend Xitlar»</b> yoki <b>«📁 Janrlar»</b> tugmalarini bosing va ommabop musiqalarni bir zumda eshiting.

3️⃣ <b>Inline qidiruv:</b>
Istalgan do'stingiz bilan chatda yoki guruhda:
<code>@{bot_username} qo'shiq nomi</code>
deb yozsangiz, to'g'ridan-to'g'ri musiqa topib jo'natishingiz mumkin!

4️⃣ <b>YouTube havolasi:</b>
YouTube'dagi har qanday video havolasini yuborsangiz, bot uni MP3 qilib beradi!
"""

@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    user = message.from_user
    await db.add_user(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name
    )

    # Agar deep-link orqali kelgan bo'lsa (masalan: /start dl_VIDEOID)
    if command.args and command.args.startswith("dl_"):
        video_id = command.args[3:]
        await send_music_to_chat(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=user.id,
            video_id=video_id
        )
        return

    await message.answer(
        START_TEXT.format(name=user.first_name),
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    bot_info = await message.bot.get_me()
    await message.answer(
        HELP_TEXT.format(bot_username=bot_info.username),
        parse_mode="HTML"
    )

@router.message(F.text == "ℹ️ Bot haqida")
async def about_bot(message: Message):
    stats = await db.get_stats()
    text = f"""
🤖 <b>Zamonaviy Musiqa Boti</b>

📊 <b>Bot statistikasi:</b>
👥 Foydalanuvchilar: <b>{stats['users']}</b> ta
🎧 Keshdagi musiqalar: <b>{stats['cached_songs']}</b> ta
📥 Jami yuklab olishlar: <b>{stats['total_downloads']}</b> marta
🔎 Qidiruvlar soni: <b>{stats['total_searches']}</b> marta

⚡️ <i>Bot eng so'nggi texnologiyalar asosida tezkor va uzluksiz ishlaydi.</i>
"""
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "🎲 Tasodifiy musiqa")
async def random_music(message: Message):
    wait_msg = await message.answer("🎲 <i>Tasodifiy musiqa tanlanmoqda...</i>", parse_mode="HTML")
    
    popular = await db.get_popular_music(limit=20)
    if popular:
        chosen = random.choice(popular)
        try:
            is_fav = await db.is_favorite(message.from_user.id, chosen["video_id"])
            caption = (
                f"🎧 <b>{chosen['title']}</b>\n"
                f"👤 <b>Ijrochi:</b> {chosen.get('artist', 'Musiqa')}\n\n"
                f"🎲 <i>Tasodifiy tavsiya etilgan qo'shiq!</i>"
            )
            await message.answer_audio(
                audio=chosen["file_id"],
                title=chosen["title"],
                performer=chosen.get("artist"),
                duration=chosen.get("duration", 0),
                caption=caption,
                parse_mode="HTML",
                reply_markup=get_audio_player_keyboard(
                    chosen["video_id"],
                    is_fav=is_fav,
                    share_query=f"{chosen.get('artist', '')} {chosen['title']}"
                )
            )
            await wait_msg.delete()
            return
        except Exception:
            pass

    trend_queries = ["uzbek rep hit 2025", "trend uzbek music", "pop music hit"]
    res = await music_service.search(random.choice(trend_queries), limit=5)
    await wait_msg.delete()
    if res:
        item = random.choice(res)
        await send_music_to_chat(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            video_id=item["id"]
        )
    else:
        await message.answer("❌ Musiqa topilmadi, iltimos qayta urinib ko'ring.")
