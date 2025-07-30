import time
import win32gui
import win32con
import keyboard

# ====== ตั้งค่าหลัก ======
WINDOW_TITLE = "Minecraft NeoForge"
click_points = [(200, 300), (400, 350)]  # พิกัดคลิก GUI เควส

# ====== สถานะควบคุม ======
is_paused = False
is_running = True

# ====== ปุ่มควบคุม ======
def toggle_pause():
    global is_paused
    is_paused = not is_paused
    print("⏸️ Paused" if is_paused else "▶️ Resumed")

def stop_bot():
    global is_running
    is_running = False
    print("🛑 Exiting bot...")

keyboard.add_hotkey("F9", toggle_pause)
keyboard.add_hotkey("F10", stop_bot)

# ====== จัดการหน้าต่าง Minecraft ======
def find_minecraft_window():
    def enum_handler(hwnd, result):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if WINDOW_TITLE in title:
                result.append(hwnd)
    result = []
    win32gui.EnumWindows(enum_handler, result)
    return result[0] if result else None

# ====== ฟังก์ชันส่งคีย์และคลิก ======
def send_enter(hwnd):
    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
    time.sleep(0.1)

def send_string(hwnd, text):
    for ch in text:
        win32gui.PostMessage(hwnd, win32con.WM_CHAR, ord(ch), 0)
        time.sleep(0.05)
    time.sleep(0.1)

def click_at(hwnd, x, y):
    lparam = (y << 16) | x
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    time.sleep(0.05)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)
    time.sleep(0.1)

def left_click_loop(hwnd, duration_sec=120, interval_ms=500):
    end_time = time.time() + duration_sec
    while time.time() < end_time and is_running:
        if is_paused:
            time.sleep(0.2)
            continue
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, 0)
        time.sleep(0.05)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, 0)
        time.sleep(interval_ms / 1000)

# ====== ลูปหลักของบอท ======
def main_loop():
    hwnd = find_minecraft_window()
    if hwnd is None:
        print("❌ ไม่พบหน้าต่าง Minecraft")
        return

    print(f"✅ พบหน้าต่าง Minecraft: {hwnd}")
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

    while is_running:
        if is_paused:
            time.sleep(0.2)
            continue

        print("🎯 รับเควส...")
        send_enter(hwnd)
        send_string(hwnd, "/nonononono")
        send_enter(hwnd)

        time.sleep(2)  # รอ GUI ปรากฏ

        for x, y in click_points:
            click_at(hwnd, x, y)

        print("⚔️ เริ่มโจมตี...")
        left_click_loop(hwnd, duration_sec=120, interval_ms=500)

        print("🔁 วนลูปรอบใหม่...")
        time.sleep(1)

    print("👋 บอทหยุดทำงานแล้ว")

# ====== รันโปรแกรม ======
if __name__ == "__main__":
    print("🚀 เริ่มบอท Minecraft NeoForge")
    print("👉 F9 = Pause / Resume | F10 = Exit")
    main_loop()
