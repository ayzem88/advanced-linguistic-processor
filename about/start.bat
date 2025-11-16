@echo off
chcp 65001 >nul
echo ========================================
echo المختار اللغوي المتقدم
echo ========================================
echo.
echo جاري التشغيل...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo خطأ في التشغيل!
    echo تأكد من تثبيت Python
    echo.
    pause
)
