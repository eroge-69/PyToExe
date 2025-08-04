import pyautogui
import time
import webbrowser
import keyboard # Bạn sẽ cần cài đặt thư viện này: pip install keyboard

# --- Các biến và hằng số của AI ---
toggle = False
centerX = pyautogui.size().width // 2
centerY = pyautogui.size().height // 2 + 80
target_colors = [(74, 74, 74), (58, 58, 58)]
scan_time = 2  # Thời gian xoay để scan map (giây)

# --- Khởi động bot và mở game ---
def toggle_ai():
    global toggle
    toggle = not toggle
    if toggle:
        print("🤖 AI ĐANG CHẠY - Nhấn F9 để tắt")
    else:
        print("⏸ AI ĐÃ TẮT - Nhấn F9 để bật")

def scan_map():
    print("🔭 Đang xoay để dò map...")
    # Xoay sang phải
    pyautogui.keyDown('d')
    time.sleep(scan_time)
    pyautogui.keyUp('d')

    # Xoay ngược lại sang trái
    pyautogui.keyDown('a')
    time.sleep(scan_time * 2)
    pyautogui.keyUp('a')

    # Trở về vị trí ban đầu (hoặc gần ban đầu)
    pyautogui.keyDown('d')
    time.sleep(scan_time)
    pyautogui.keyUp('d')

# Mở bloxd.io
print("🌐 Đang mở Bloxd.io...")
webbrowser.open("https://bloxd.io")
time.sleep(5) # Chờ game load xong

print("🔄 Sẵn sàng! Nhấn F9 để bật bot.")

keyboard.add_hotkey('f9', toggle_ai)
keyboard.add_hotkey('f10', lambda: print('Đang thoát...')) and exit())

# --- Vòng lặp chính ---
while True:
    try:
        if toggle:
            # Logic di chuyển và nhảy
            color = pyautogui.pixel(centerX, centerY)

            if color in target_colors:
                pyautogui.press('space')
            else:
                pyautogui.keyDown('w')
                time.sleep(0.1)
                pyautogui.keyUp('w')

            # Sau mỗi 30 giây, thực hiện scan map
            if time.time() % 30 < 0.1: # Khoảng 30 giây một lần
                scan_map()
        
        time.sleep(0.05)
    except Exception as e:
        print(f"Lỗi: {e}")
        break