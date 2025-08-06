#!/usr/bin/env python3
"""
滑鼠和鍵盤活動追蹤器

由於沙盒環境的限制，這個版本提供了一個模擬的實現，
展示了如何記錄滑鼠移動距離、點擊次數和鍵盤打擊次數。

在實際環境中，您需要安裝 pynput 函式庫：
pip install pynput

然後取消註解下面的實際實現代碼。
"""

import math
import time
import threading
import random

class ActivityTracker:
    def __init__(self):
        self.mouse_distance = 0.0
        self.click_count = 0
        self.key_press_count = 0
        self.last_mouse_pos = (0, 0)
        self.running = True

    def simulate_activity(self):
        """模擬滑鼠和鍵盤活動以展示功能"""
        print("模擬模式：展示滑鼠和鍵盤活動追蹤功能")
        print("在實際環境中，這將監控真實的滑鼠和鍵盤事件")
        print("按 Ctrl+C 停止模擬\n")

        while self.running:
            try:
                # 模擬滑鼠移動
                new_x = self.last_mouse_pos[0] + random.randint(-50, 50)
                new_y = self.last_mouse_pos[1] + random.randint(-50, 50)
                
                dx = new_x - self.last_mouse_pos[0]
                dy = new_y - self.last_mouse_pos[1]
                distance = math.sqrt(dx**2 + dy**2)
                self.mouse_distance += distance
                self.last_mouse_pos = (new_x, new_y)

                # 模擬隨機點擊
                if random.random() < 0.3:  # 30% 機率點擊
                    self.click_count += 1

                # 模擬隨機按鍵
                if random.random() < 0.4:  # 40% 機率按鍵
                    self.key_press_count += 1

                self.print_stats()
                time.sleep(1)  # 每秒更新一次

            except KeyboardInterrupt:
                self.running = False
                print("\n\n停止模擬。")
                break

    def print_stats(self):
        """顯示當前統計數據"""
        print(f"\r滑鼠移動距離: {self.mouse_distance:.2f} 像素 | "
              f"點擊次數: {self.click_count} | "
              f"鍵盤打擊次數: {self.key_press_count}", end="", flush=True)

    def start(self):
        """開始追蹤活動"""
        self.simulate_activity()

# 實際實現（需要 pynput 函式庫）
"""
import math
from pynput import mouse, keyboard

class RealActivityTracker:
    def __init__(self):
        self.mouse_distance = 0.0
        self.click_count = 0
        self.key_press_count = 0
        self.last_mouse_pos = None

    def on_move(self, x, y):
        if self.last_mouse_pos is not None:
            dx = x - self.last_mouse_pos[0]
            dy = y - self.last_mouse_pos[1]
            self.mouse_distance += math.sqrt(dx**2 + dy**2)
        self.last_mouse_pos = (x, y)
        self.print_stats()

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.click_count += 1
            self.print_stats()

    def on_press(self, key):
        self.key_press_count += 1
        self.print_stats()

    def print_stats(self):
        print(f"\\r滑鼠移動距離: {self.mouse_distance:.2f} 像素 | "
              f"點擊次數: {self.click_count} | "
              f"鍵盤打擊次數: {self.key_press_count}", end="", flush=True)

    def start(self):
        print("開始監聽滑鼠和鍵盤活動... (按 Ctrl+C 停止)")
        
        mouse_listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click
        )
        keyboard_listener = keyboard.Listener(on_press=self.on_press)

        mouse_listener.start()
        keyboard_listener.start()

        try:
            mouse_listener.join()
            keyboard_listener.join()
        except KeyboardInterrupt:
            print("\\n停止監聽。")
            mouse_listener.stop()
            keyboard_listener.stop()
"""

if __name__ == "__main__":
    tracker = ActivityTracker()
    tracker.start()

