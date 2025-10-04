#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
telegram_clean_auto.py

1. Завершает все процессы Telegram/AyuGram (включая портейбл).
2. Ищет папки Telegram по log.txt и удаляет их автоматически:
   - если найден "FROZEN_METHOD_INVALID" → удалить;
   - если найден "OpenGL: [TRUE]" и после него больше нет строк → удалить;
   - если найден "OpenGL: [TRUE]" и после него есть строки,
       то удалить только если среди них есть "FROZEN_METHOD_INVALID".
"""

import os
import shutil
import psutil
import win32gui
import win32process
import win32con
from pathlib import Path

# === Настройки ===
ROOT = Path("C:\\")
TARGET_FILENAME = "log.txt"

KEYWORDS = ["telegram", "ayugram"]

EXCLUDE_FOLDERS = {
    "windows",
    "users",
    "program files",
    "program files (x86)",
    "perflogs",
    "$recycle.bin",
    "recovery",
    "system volume information"
}
# =================


# --- Часть 1: Завершение процессов ---
def enum_windows():
    """Возвращает список (hwnd, title, pid)"""
    results = []

    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                results.append((hwnd, title, pid))
        return True

    win32gui.EnumWindows(callback, None)
    return results


def close_by_windows():
    windows = enum_windows()
    found = False

    for hwnd, title, pid in windows:
        if any(k in title.lower() for k in KEYWORDS):
            try:
                proc = psutil.Process(pid)
                print(f"Закрываю PID={pid} | Title='{title}' | EXE={proc.name()}")
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                proc.wait(timeout=3)
            except Exception:
                try:
                    proc.kill()
                    print(f"💀 Kill PID={pid}")
                except Exception:
                    pass
            found = True

    if not found:
        print("⚠️ Окна Telegram/AyuGram не найдены.")


# --- Часть 2: Анализ и удаление папок ---
def analyze_log(text: str):
    if "FROZEN_METHOD_INVALID" in text:
        return "❌ Заморожен", True

    idx = text.find("OpenGL: [TRUE]")
    if idx != -1:
        rest = text[idx:].strip()
        lines_after = rest.splitlines()[1:]
        if not lines_after:
            return "🧹 Пустой (OpenGL, конец лога)", True
        else:
            if "FROZEN_METHOD_INVALID" in "\n".join(lines_after):
                return "❌ Заморожен после OpenGL", True
            else:
                return "✅ Нормальный запуск (есть активность)", False

    return "ℹ️ Неопределён", False


def is_excluded(path: Path) -> bool:
    parts = [p.lower() for p in path.parts]
    return any(ex in parts for ex in EXCLUDE_FOLDERS)


def clean_telegram_folders():
    print("\n🚀 Сканирование C:\\ ...\n")

    for dirpath, dirnames, filenames in os.walk(ROOT):
        try:
            current = Path(dirpath)

            if is_excluded(current):
                dirnames[:] = []
                continue

            if TARGET_FILENAME not in filenames:
                continue

            log_path = current / TARGET_FILENAME

            try:
                text = log_path.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:
                print(f"⚠️ Не удалось прочитать {log_path}: {e}")
                continue

            status, should_delete = analyze_log(text)

            print(f"📄 Лог: {log_path}")
            print(f"   Статус: {status}")

            try:
                files_here = [f.lower() for f in os.listdir(dirpath)]
            except PermissionError:
                print("   ⚠️ Нет доступа к этой папке.")
                continue

            if "telegram.exe" in files_here:
                telegram_folder = current
            else:
                telegram_folder = current.parent

            print(f"📂 Папка Telegram: {telegram_folder}")

            if should_delete:
                try:
                    shutil.rmtree(telegram_folder)
                    print(f"✅ Удалено: {telegram_folder}\n")
                except Exception as e:
                    print(f"⚠️ Ошибка удаления {telegram_folder}: {e}\n")
            else:
                print("⏩ Не требует удаления.\n")

        except Exception as e:
            print(f"Ошибка при обработке {dirpath}: {e}")

    print("\n✅ Сканирование завершено.")


if __name__ == "__main__":
    print("=== Этап 1: Завершение процессов Telegram/AyuGram ===")
    close_by_windows()

    print("\n=== Этап 2: Очистка папок Telegram ===")
    clean_telegram_folders()
