# mouse_mover.py

import pyautogui
import time

def move_mouse_every_6_minutes():
    print("開始滑鼠自動移動程式（每6分鐘）...")
    try:
        while True:
            current_pos = pyautogui.position()  # 取得目前滑鼠位置
            # 輕微移動一下（向右1像素，再回來）
            pyautogui.move(1, 0, duration=0.1)
            pyautogui.move(-1, 0, duration=0.1)
            print(f"滑鼠動了一下喔！目前時間：{time.strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(360)  # 等待6分鐘（360秒）
    except KeyboardInterrupt:
        print("\n已手動停止滑鼠移動程式。")

if __name__ == "__main__":
    move_mouse_every_6_minutes()
