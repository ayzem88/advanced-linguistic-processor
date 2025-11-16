@echo off
chcp 65001 >nul
echo ========================================
echo المختار اللغوي المتقدم - Advanced Arabic Text Analyzer
echo ========================================
echo.
echo جاري تحميل المكتبات المطلوبة...
pip install -r requirements.txt
echo.
echo جاري التشغيل...
echo.

python main.py

pause

