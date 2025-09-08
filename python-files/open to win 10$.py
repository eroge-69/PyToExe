#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import platform
import random

# الألوان اختيارية عبر colorama؛ إن لم تتوفر سيكمل بدون ألوان
GREEN = ""
YELLOW = ""
RESET = ""

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    RESET = Style.RESET_ALL
except Exception:
    pass  # بدون ألوان

is_windows = platform.system().lower().startswith("win")

def set_title(title: str):
    if is_windows:
        os.system(f"title {title}")  # تغيير عنوان نافذة الأوامر على ويندوز
    # على الأنظمة الأخرى نتجاوز لضمان البساطة

def main():
    try:
        set_title("System Breach Detected")
        print(GREEN + "Initializing payload..." + RESET)
        time.sleep(0.8)

        stages = [
            "Scanning system files",
            "Escalating privileges",
            "Enumerating processes",
            "Establishing secure channel",
            "Extracting metadata",
            "Finalizing operations"
        ]

        # تقدّم مزيف
        for i in range(1, 101):
            status = random.choice(stages)
            msg = f"\r{YELLOW}{status}: {i}%{RESET}"
            print(msg, end="", flush=True)
            time.sleep(0.08)

        print()  # سطر جديد بعد شريط التقدم
        print()
        print("===========================================")
        print(GREEN + "هذا مجرد مقلب للتسلية. لا يوجد أي ضرر." + RESET)
        print("===========================================")

    finally:
        # إعادة العنوان الافتراضي بشكل تقريبي على ويندوز
        if is_windows:
            os.system("title Command Prompt")

        # إبقاء النافذة مفتوحة عند التشغيل بالنقر المزدوج على بعض البيئات
        try:
            input("\nاضغط Enter للإغلاق...")
        except EOFError:
            pass

if __name__ == "__main__":
    main()
