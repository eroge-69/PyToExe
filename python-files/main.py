import time
import pygetwindow as gw
import win32gui
import win32con

# 要找的視窗名稱關鍵字（可只放部分名稱）
TARGET_TITLE_KEYWORD = "MapleStory Worlds"  # 改成你的測試程式視窗關鍵字
# 要模擬按住的鍵（這裡用 F12）
VK_F12 = 0x7B  # virtual-key code for F12

# 每隔多久再送一次 WM_KEYDOWN（秒） —— 越小越像持續按住，但 CPU 消耗較高
SEND_INTERVAL = 0.05

def find_window_hwnd_by_keyword(keyword):
    wins = gw.getWindowsWithTitle(keyword)
    if not wins:
        return None
    # 取第一個符合的視窗
    return wins[0]._hWnd

def send_keydown(hwnd, vk):
    # wParam = vk, lParam minimal (0). 一些程式會需要正確 lParam 才處理 repeat/scan code。
    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk, 0)

def send_keyup(hwnd, vk):
    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk, 0)

def main():
    hwnd = find_window_hwnd_by_keyword(TARGET_TITLE_KEYWORD)
    if not hwnd:
        print(f"找不到包含關鍵字 '{TARGET_TITLE_KEYWORD}' 的視窗。請確認視窗是否已開啟，或改用不同關鍵字。")
        return

    # 印出視窗標題確認
    title = win32gui.GetWindowText(hwnd)
    print(f"目標視窗：{title} (hwnd=0x{hwnd:08X})")
    print("開始在背景送 WM_KEYDOWN（模擬持續按住）。按 Ctrl+C 停止並送 WM_KEYUP。")

    try:
        # 先送一次 keydown
        send_keydown(hwnd, VK_F12)
        # 持續定期再送 keydown（有些程式只要連續收到 keydown 就會當成按住）
        while True:
            time.sleep(SEND_INTERVAL)
            send_keydown(hwnd, VK_F12)
    except KeyboardInterrupt:
        # 停止時放開按鍵
        send_keyup(hwnd, VK_F12)
        print("\n已收到停止指令，已送出 WM_KEYUP 並結束。")

if __name__ == "__main__":
    main()
