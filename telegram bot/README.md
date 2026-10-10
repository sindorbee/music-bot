# 🎵 Telegram Zamonaviy Musiqa Boti

Ushbu bot har qanday musiqani (O'zbekcha qo'shiqlar, Rep, Pop, Estrada, Ruscha va Jahon xitlari) bir zumda topib, yuqori sifatli audio (MP3) formatda Telegram orqali yuboruvchi zamonaviy bot hisoblanadi.

---

## ✨ Asosiy Imkoniyatlari

- 🔍 **Tezkor qidiruv:** Qo'shiq nomi, ijrochi yoki matni bo'yicha eng sara 10 ta variantni topish.
- 🇺🇿 **O'zbekcha va Jahon musiqalari:** Konsta, Xamdam Sobirov, Jaloliddin Ahmadaliyev, Jahongir Otajonov, Macan, Eminem, Billie Eilish va boshqa barcha ijrochilar.
- 📁 **Janrlar menyusi:**
  - 🇺🇿 O'zbek Xitlar
  - 🎤 O'zbek Rep & Hip-Hop
  - 🇷🇺 Ruscha Rep & Xitlar
  - 🌍 Jahon Pop (World Top)
  - ⚡️ Bass & Remix
  - 📻 Retro & Milliy
  - 🔥 TikTok Trendlar
- ⚡️ **Aqlli Kesh (Smart Cache):** Agar biror qo'shiq oldin yuklangan bo'lsa, ikkinchi foydalanuvchiga 0.1 soniyada bir zumda yuboriladi (trafik va vaqt tejaladi).
- ⭐️ **Sevimlilarim (Favorites):** O'zingiz yoqtirgan qo'shiqlarni alohida ro'yxatga saqlab qo'yish imkoniyati.
- 🎲 **Tasodifiy musiqa:** Kayfiyatga qarab yangi xit qo'shiq tavsiya qilish.
- 🔄 **Inline rejim:** Do'stlar bilan chatda yoki guruhlarda `@botingiz_nomi qo'shiq nomi` deb yozib to'g'ridan-to'g'ri musiqa jo'natish.
- 🔗 **YouTube havolalari:** YouTube video havolasini yuborsangiz ham, bot uni MP3 audio qilib beradi.
- 🎧 **To'liq MP3 Metama'lumotlar:** Artist nomi, qo'shiq sarlavhasi, davomiyligi va albom muqovasi (thumbnail) bilan yuboriladi.

---

## 🚀 Ishga Tushirish Qo'llanmasi

### 1-qadam: Bot Token olish
1. Telegramda [@BotFather](https://t.me/BotFather) botiga kiring.
2. `/newbot` buyrug'ini yuboring.
3. Botingizga nom va username bering (masalan: `MegaMusicUzBot`).
4. `@BotFather` sizga bergan **API Token**ni nusxalab oling.

### 2-qadam: Tokenni kiritish
Loyiha papkasidagi `.env` faylini oching va tokenni yozing:
```env
BOT_TOKEN=1234567890:AAHxxxxxxxxx_sizning_tokeningiz
```

### 3-qadam: Botni ishga tushirish
Windows tizimida botni ishga tushirish uchun oddiygina:
👉 **`run.bat`** faylini ikki marta bosing!

Yoki terminal/PowerShell orqali:
```bash
python bot.py
```

---

## 🛠 Texnologiyalar
- **Python 3.13+**
- **Aiogram 3** - Asinxron Telegram bot freymvorki
- **yt-dlp** - Tezkor musiqa va audio chiqaruvchi
- **imageio-ffmpeg** - Avtomatik MP3 konvertori
- **aiosqlite** - Asinxron SQLite ma'lumotlar bazasi va kesh tizimi
