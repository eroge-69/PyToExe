import curses
import keyboard
import threading
import time
import sys
import os
import win32gui
import datetime

# ========================
# CONFIG
# ========================
SECRET_PHRASE = "ilovebsod"
LOG_FILE = "unlock_log.txt"
FAILSAFE_TRIGGER = 5

# Global state
is_unlocked = False
esc_count = 0
lock = threading.Lock()

def log_attempt(attempt):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{now}] Attempt: \"{attempt}\"\n")

def block_keys():
    """Block dangerous keys until unlocked"""
    global is_unlocked, esc_count
    blocked_keys = [
        'alt', 'left alt', 'right alt',
        'windows', 'left windows', 'right windows',
        'ctrl+shift+esc', 'ctrl+alt+delete',
        'alt+tab', 'alt+f4', 'ctrl+w',
        'f1', 'f12', 'menu', 'apps'
    ]

    while not is_unlocked:
        # Block combos and keys
        for key in blocked_keys:
            keyboard.block_key(key)

        # Handle failsafe: ESC x5
        if keyboard.is_pressed('esc'):
            with lock:
                esc_count += 1
            time.sleep(0.1)  # debounce
            if esc_count >= FAILSAFE_TRIGGER:
                is_unlocked = True
                return
        else:
            with lock:
                if esc_count > 0:
                    esc_count = 0

        time.sleep(0.01)

def kill_taskmgr():
    """Auto-close Task Manager if opened"""
    global is_unlocked
    while not is_unlocked:
        hwnd = win32gui.FindWindow(None, "Task Manager")
        if hwnd:
            win32gui.PostMessage(hwnd, 0x0010, 0, 0)  # WM_CLOSE
            time.sleep(0.5)
        time.sleep(0.3)

def main(stdscr):
    global is_unlocked

    # Setup terminal
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.clear()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    stdscr.bkgd(' ', curses.color_pair(1))

    # Draw BSOD
    lines = [
        "A fatal exception has occurred at 0x0000C0DE",
        "*** SYSTEM HALTED: PRANKLOCK ENGAGED ***",
        "",
        "🔓 Unlock phrase required. Type blindly to recover.",
        "🚨 Press ESC 5 times for emergency exit.",
        "",
        "          DO NOT TURN OFF YOUR COMPUTER",
    ]

    current_input = ""

    # Start background threads
    threading.Thread(target=block_keys, daemon=True).start()
    threading.Thread(target=kill_taskmgr, daemon=True).start()

    while not is_unlocked:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        for i, line in enumerate(lines):
            x = max(0, w // 2 - len(line) // 2)
            y = h // 2 - len(lines) // 2 + i
            if 0 <= y < h:
                stdscr.addstr(y, x, line, curses.color_pair(1))

        # Show input feedback (optional — comment out for true blind mode)
        # stdscr.addstr(h-2, 2, f"Input: {current_input[-20:]}", curses.color_pair(1))

        stdscr.refresh()

        try:
            key = stdscr.getkey()
            if key == '\n' or key == '\r':
                log_attempt(current_input)
                if current_input == SECRET_PHRASE:
                    is_unlocked = True
                else:
                    current_input = ""
            elif len(key) == 1 and ord(key) >= 32 and ord(key) <= 126:
                current_input += key
                if len(current_input) > 30:
                    current_input = ""
        except:
            pass

        time.sleep(0.05)

    # Unlock screen
    stdscr.clear()
    stdscr.bkgd(' ', curses.A_NORMAL)
    curses.curs_set(1)
    stdscr.addstr(5, 5, "🔓 SYSTEM RESTORED — Access granted.", curses.A_BOLD)
    stdscr.addstr(7, 5, "Press any key to exit...")
    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    # Create log file if not exists
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'w', encoding="utf-8").close()

    # Run curses wrapper
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass