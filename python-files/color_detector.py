@echo off
chcp 65001 > nul
echo ===============================
echo    تبدیل خودکار پایتون به EXE
echo ===============================
echo.

REM بررسی وجود پایتون
python --version > nul 2>&1
if errorlevel 1 (
    echo ! خطا: پایتون نصب نیست
    echo لطفا پایتون را از python.org نصب کنید
    pause
    exit
)

echo ✓ پایتون شناسایی شد

REM نصب کتابخانه‌های مورد نیاز
echo در حال نصب کتابخانه‌های مورد نیاز...
pip install opencv-python pyautogui keyboard pynput numpy pyinstaller

echo.
echo ✓ کتابخانه‌ها نصب شدند

REM ایجاد فایل پایتون
echo import cv2 > color_detector.py
echo import numpy as np >> color_detector.py
echo import pyautogui >> color_detector.py
echo import keyboard >> color_detector.py
echo from pynput import mouse >> color_detector.py
echo import threading >> color_detector.py
echo import time >> color_detector.py
echo. >> color_detector.py
echo class ColorDetectionApp: >> color_detector.py
echo. >> color_detector.py
REM ... بقیه کد رو اینجا اضافه کنید ...

echo ✓ فایل پایتون ایجاد شد

REM تبدیل به EXE
echo در حال تبدیل به فایل EXE...
pyinstaller --onefile --windowed --hidden-import=keyboard --hidden-import=pynput.mouse --hidden-import=cv2 color_detector.py

echo.
echo ===============================
echo ✓ فایل EXE با موفقیت ساخته شد!
echo.
echo مکان فایل: dist\color_detector.exe
echo.
echo ! نکته مهم: ممکن است آنتی‌ویروس هشدار دهد
echo ===============================
pause