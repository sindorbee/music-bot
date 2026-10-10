from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_search_results_keyboard(
    search_id: str,
    items: List[Dict[str, Any]],
    current_page: int = 1,
    per_page: int = 5
) -> InlineKeyboardMarkup:
    """Qidiruv natijalari uchun sahifalangan klaviatura"""
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page
    if total_pages == 0:
        total_pages = 1

    start_idx = (current_page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    page_items = items[start_idx:end_idx]

    keyboard = []

    # 1. Qo'shiqlarni tanlash tugmalari qatori (1, 2, 3, 4, 5)
    num_buttons = []
    for i, item in enumerate(page_items):
        item_number = start_idx + i + 1
        video_id = item.get("id")
        num_buttons.append(
            InlineKeyboardButton(
                text=f"{item_number}",
                callback_data=f"dl:{video_id}"
            )
        )
    if num_buttons:
        keyboard.append(num_buttons)

    # 2. Sahifalash (Pagination) qatori
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Ortga",
                callback_data=f"pg:{search_id}:{current_page - 1}"
            )
        )
    else:
        nav_buttons.append(
            InlineKeyboardButton(text="⏹", callback_data="noop")
        )

    nav_buttons.append(
        InlineKeyboardButton(
            text=f"📄 {current_page}/{total_pages}",
            callback_data="noop"
        )
    )

    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"pg:{search_id}:{current_page + 1}"
            )
        )
    else:
        nav_buttons.append(
            InlineKeyboardButton(text="⏹", callback_data="noop")
        )

    keyboard.append(nav_buttons)

    # 3. Yopish tugmasi
    keyboard.append([
        InlineKeyboardButton(text="❌ Yopish", callback_data="close_msg")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_audio_player_keyboard(
    video_id: str,
    is_fav: bool = False,
    share_query: str = ""
) -> InlineKeyboardMarkup:
    """Musiqa ostidagi boshqaruv tugmalari"""
    fav_text = "💔 O'chirish" if is_fav else "❤️ Sevimlilarga"
    fav_action = f"unfav:{video_id}" if is_fav else f"fav:{video_id}"

    keyboard = [
        [
            InlineKeyboardButton(text=fav_text, callback_data=fav_action),
            InlineKeyboardButton(
                text="🔄 Do'stlarga ulashish",
                switch_inline_query=share_query[:40] if share_query else ""
            ),
        ],
        [
            InlineKeyboardButton(text="🔍 Boshqa musiqa qidirish", callback_data="new_search")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_genres_keyboard() -> InlineKeyboardMarkup:
    """Musiqa janrlari menyusi"""
    genres = [
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek Xitlar", callback_data="gn:uzbek_hits"),
            InlineKeyboardButton(text="🎤 O'zbek Rep", callback_data="gn:uzbek_rap"),
        ],
        [
            InlineKeyboardButton(text="🇷🇺 Ruscha Xitlar & Rep", callback_data="gn:russian_rap"),
            InlineKeyboardButton(text="🌍 Jahon Pop (World)", callback_data="gn:world_pop"),
        ],
        [
            InlineKeyboardButton(text="⚡️ Bass & Remix", callback_data="gn:bass_remix"),
            InlineKeyboardButton(text="📻 Retro & Milliy", callback_data="gn:retro_uzbek"),
        ],
        [
            InlineKeyboardButton(text="🔥 TikTok Trend 2025/2026", callback_data="gn:tiktok_trends"),
        ],
        [
            InlineKeyboardButton(text="❌ Yopish", callback_data="close_msg")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=genres)

def get_favorites_keyboard(
    favs: List[Dict[str, Any]],
    current_page: int = 1,
    total_pages: int = 1
) -> InlineKeyboardMarkup:
    """Sevimlilar ro'yxati klaviaturasi"""
    keyboard = []

    for item in favs:
        title = item.get("title", "Noma'lum")[:28]
        video_id = item.get("video_id")
        keyboard.append([
            InlineKeyboardButton(
                text=f"▶️ {title}",
                callback_data=f"dl:{video_id}"
            ),
            InlineKeyboardButton(
                text="🗑",
                callback_data=f"delfav:{video_id}"
            )
        ])

    nav_row = []
    if current_page > 1:
        nav_row.append(
            InlineKeyboardButton(text="⬅️ Ortga", callback_data=f"favpg:{current_page - 1}")
        )
    nav_row.append(
        InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="noop")
    )
    if current_page < total_pages:
        nav_row.append(
            InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"favpg:{current_page + 1}")
        )
    
    if len(nav_row) > 1:
        keyboard.append(nav_row)

    keyboard.append([
        InlineKeyboardButton(text="❌ Yopish", callback_data="close_msg")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
