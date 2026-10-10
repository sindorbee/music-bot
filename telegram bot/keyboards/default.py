from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu() -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi"""
    keyboard = [
        [
            KeyboardButton(text="🔍 Musiqa qidirish"),
            KeyboardButton(text="🔥 Trend Xitlar"),
        ],
        [
            KeyboardButton(text="📁 Janrlar (Rep, Pop...)"),
            KeyboardButton(text="⭐️ Sevimlilarim"),
        ],
        [
            KeyboardButton(text="🎲 Tasodifiy musiqa"),
            KeyboardButton(text="ℹ️ Bot haqida"),
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Qo'shiq yoki ijrochi nomini yozing..."
    )

def get_cancel_button() -> ReplyKeyboardMarkup:
    """Bekor qilish tugmasi"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True
    )
