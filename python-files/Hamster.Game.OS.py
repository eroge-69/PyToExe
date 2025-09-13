
import curses
import os
import subprocess
import string
import platform
import time

# --- проверка наличия CD/DVD привода ---
def has_cd_drive():
    system = platform.system()
    if system == "Windows":
        # Проверяем стандартные буквы дисков (D: и дальше)
        for letter in range(68, 91):  # D:–Z:
            path = f"{chr(letter)}:\\"
            if os.path.exists(path):
                return True
        return False
    elif system == "Linux":
        return os.path.exists("/dev/cdrom") or os.path.exists("/dev/sr0")
    else:
        return False

# --- функции для открытия/закрытия привода ---
def toggle_cd_door():
    system = platform.system()
    try:
        if system == "Windows":
            import ctypes
            mci = ctypes.windll.winmm.mciSendStringW
            mci("set cdaudio door open", None, 0, None)
        elif system == "Linux":
            subprocess.call(["eject"])
        else:
            return False
        return True
    except Exception:
        return False

# --- поиск всех Hamster.exe ---
def scan_drives():
    found = []
    if platform.system() == "Windows":
        drives = [f"{chr(letter)}:\\" for letter in range(67, 91)]  # C:–Z:
    else:
        drives = ["/media", "/mnt"]  # Linux заглушка

    for d in drives:
        if os.path.exists(d):
            for root, dirs, files in os.walk(d):
                for f in files:
                    if f.lower() == "hamster.exe":
                        found.append(os.path.join(root, f))
                break
    return found[:26]  # максимум 26 файлов

# --- основной экран ---
def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)

    # Проверяем наличие CD-привода
    if not has_cd_drive():
        for _ in range(5):
            stdscr.clear()
            stdscr.addstr(0, 0, "Kernel Panic#1", curses.color_pair(1))
            stdscr.addstr(1, 0, "disk drive not detected", curses.color_pair(1))
            stdscr.refresh()
            time.sleep(2)

    def draw_start_screen(found_files):
        stdscr.clear()
        stdscr.addstr(0, 0, "вставьте диск", curses.color_pair(1))
        stdscr.addstr(1, 0, "(нажмите 0 чтобы открыть/закрыть дисковод)", curses.color_pair(1))
        stdscr.addstr(curses.LINES - 1, 0, "(Hamster.Game.OS.prototype)", curses.color_pair(1))

        for idx, file in enumerate(found_files):
            label = string.ascii_uppercase[idx]
            stdscr.addstr(3 + idx, 0, f"{label}. {os.path.basename(file)}", curses.color_pair(1))
        stdscr.refresh()

    while True:
        found = scan_drives()
        draw_start_screen(found)
        key = stdscr.getch()

        if key == ord("0"):  # открыть/закрыть лоток
            toggle_cd_door()

        if key in [ord(c) for c in string.ascii_uppercase[:len(found)]]:
            idx = string.ascii_uppercase.index(chr(key))
            exe_path = found[idx]
            try:
                subprocess.Popen([exe_path], shell=True)
                break
            except Exception as e:
                stdscr.clear()
                stdscr.addstr(0, 0, f"Ошибка запуска: {e}", curses.color_pair(1))
                stdscr.refresh()
                curses.napms(3000)

if __name__ == "__main__":
    curses.wrapper(main)