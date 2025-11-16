#!/bin/bash
# ملف تشغيل المختار اللغوي على macOS

cd "$(dirname "$0")"

# التحقق من تثبيت المكتبات
pip3 install -r requirements.txt

# تشغيل البرنامج
python3 main.py

