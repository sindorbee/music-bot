@echo off
chcp 65001 > nul
title Telegram Zamonaviy Musiqa Boti
echo ============================================================
echo      Telegram Zamonaviy Musiqa Boti Ishga Tushmoqda...
echo ============================================================
echo.

python bot.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Xatolik yuz berdi! Iltimos .env faylida BOT_TOKEN to'g'ri kiritilganini tekshiring.
)

pause
