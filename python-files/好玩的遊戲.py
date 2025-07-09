import tkinter as tk
import tkinter.messagebox
import random
import threading
import time
from tkinter import ttk

class 恐怖中毒程式:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("⚠️ 系統警告 ⚠️")
        self.window.geometry('400x300')
        self.window.configure(bg='black')
        
        # 設置視窗置頂
        self.window.attributes('-topmost', True)
        
        # 恐怖標題
        title_label = tk.Label(
            self.window, 
            text="🚨 系統已中毒 🚨", 
            font=('Arial', 16, 'bold'),
            fg='red',
            bg='black'
        )
        title_label.pack(pady=20)
        
        # 警告文字
        warning_text = tk.Label(
            self.window,
            text="⚠️ 警告：檢測到惡意程式入侵 ⚠️\n\n你的電腦已被病毒感染\n所有檔案正在被加密\n\n點擊下方按鈕開始緊急病毒清除",
            font=('Arial', 12),
            fg='red',
            bg='black',
            justify='center'
        )
        warning_text.pack(pady=20)
        
        # 假清除按鈕
        self.clear_button = tk.Button(
            self.window,
            text="🚨 緊急!!開始清理病毒 🚨",
            font=('Arial', 12, 'bold'),
            bg='red',
            fg='white',
            command=self.開始瘋狂彈窗
        )
        self.clear_button.pack(pady=20)
        
        # 進度標籤
        self.progress_label = tk.Label(
            self.window,
            text="進度：0/∞",
            font=('Arial', 10),
            fg='yellow',
            bg='black'
        )
        self.progress_label.pack(pady=10)
        
        # 計數器
        self.彈窗次數 = 0
        self.目標次數 = 1000
        self.正在執行 = False
        self.恐怖訊息 = [
            "🚨 病毒清除失敗！系統即將崩潰 🚨",
            "💀 你的電腦已被完全控制 💀",
            "⚠️ 所有檔案正在被刪除 ⚠️",
            "🔥 系統過熱！即將爆炸 🔥",
            "👻 幽靈程式正在竊取你的資料 👻",
            "🦠 病毒正在複製中... 🦠",
            "💣 倒數計時：系統將在10秒後自毀 💣",
            "🩸 你的電腦正在流血 🩸",
            "👹 惡魔程式已啟動 👹",
            "⚰️ 你的電腦已經死亡 ⚰️",
            "🕯️ 蠟燭熄滅了... 🕯️",
            "🎭 小丑正在看著你 🎭",
            "🕷️ 蜘蛛網覆蓋了你的螢幕 🕷️",
            "🌙 午夜時分，程式開始甦醒 🌙",
            "🔮 水晶球預示著你的末日 🔮",
            "💀 第{}次清除失敗 💀",
            "🚨 系統崩潰倒數：{}次 🚨",
            "🔥 溫度過高！第{}次警告 🔥",
            "👻 幽靈第{}次現身 👻",
            "🦠 病毒變種第{}代 🦠"
        ]
        
    def 開始瘋狂彈窗(self):
        """開始瘋狂彈窗"""
        if self.正在執行:
            return
            
        self.正在執行 = True
        self.clear_button.config(text="🚨 正在執行中... 🚨", state='disabled')
        
        # 啟動瘋狂彈窗線程
        threading.Thread(target=self.執行瘋狂彈窗, daemon=True).start()
        
    def 執行瘋狂彈窗(self):
        """執行瘋狂彈窗"""
        for i in range(self.目標次數):
            if not self.正在執行:
                break
                
            self.彈窗次數 += 1
            
            # 更新進度
            self.window.after(0, self.更新進度)
            
            # 創建多個彈窗（每10次增加一個彈窗）
            彈窗數量 = min(15, 1 + (self.彈窗次數 // 10))
            
            for j in range(彈窗數量):
                threading.Timer(j * 0.05, self.創建彈窗).start()
            
            # 隨機移動主視窗到螢幕不同位置
            screen_width = 1920
            screen_height = 1080
            x = random.randint(0, screen_width - 400)
            y = random.randint(0, screen_height - 300)
            self.window.after(0, lambda x=x, y=y: self.window.geometry(f'400x300+{x}+{y}'))
            
            # 隨機延遲（更快的節奏）
            time.sleep(random.uniform(0.05, 0.2))
            
        # 完成後顯示結果
        self.window.after(0, self.顯示完成訊息)
        
    def 更新進度(self):
        """更新進度顯示"""
        self.progress_label.config(text=f"進度：{self.彈窗次數}/∞")
        self.clear_button.config(text=f"🚨 已執行 {self.彈窗次數} 次 🚨")
        
    def 顯示完成訊息(self):
        """顯示完成訊息"""
        self.progress_label.config(text="💀 清除完成！你的電腦已死亡 💀", fg='red')
        self.clear_button.config(text="💀 任務完成 💀", state='normal')
        
        # 創建最終的恐怖彈窗
        for i in range(5):
            threading.Timer(i * 1, self.創建最終彈窗).start()
            
    def 創建最終彈窗(self):
        """創建最終的恐怖彈窗"""
        popup = tk.Toplevel()
        popup.title("💀 最終警告 💀")
        popup.geometry('400x250')
        popup.configure(bg='black')
        popup.attributes('-topmost', True)
        
        # 分布到整個螢幕
        screen_width = 1920
        screen_height = 1080
        popup_width = 400
        popup_height = 250
        
        # 隨機選擇螢幕區域
        area = random.choice(['top_left', 'top_right', 'bottom_left', 'bottom_right', 'center'])
        
        if area == 'top_left':
            x = random.randint(0, screen_width // 3)
            y = random.randint(0, screen_height // 3)
        elif area == 'top_right':
            x = random.randint(screen_width * 2 // 3, screen_width - popup_width)
            y = random.randint(0, screen_height // 3)
        elif area == 'bottom_left':
            x = random.randint(0, screen_width // 3)
            y = random.randint(screen_height * 2 // 3, screen_height - popup_height)
        elif area == 'bottom_right':
            x = random.randint(screen_width * 2 // 3, screen_width - popup_width)
            y = random.randint(screen_height * 2 // 3, screen_height - popup_height)
        else:  # center
            x = random.randint(screen_width // 4, screen_width * 3 // 4 - popup_width)
            y = random.randint(screen_height // 4, screen_height * 3 // 4 - popup_height)
        
        popup.geometry(f'{popup_width}x{popup_height}+{x}+{y}')
        
        # 最終訊息
        final_messages = [
            "💀 清除完成！你的電腦已徹底死亡 💀",
            "⚰️ 系統已停止運作，所有資料已銷毀 ⚰️",
            "🔥 電腦正在燃燒，請立即逃離 🔥",
            "👻 幽靈程式已佔領你的電腦 👻",
            "🎭 小丑說：遊戲結束了 🎭"
        ]
        
        message = random.choice(final_messages)
        
        # 警告標籤
        warning = tk.Label(
            popup,
            text=message,
            font=('Arial', 16, 'bold'),
            fg='red',
            bg='black',
            wraplength=350,
            justify='center'
        )
        warning.pack(expand=True, fill='both', padx=20, pady=20)
        
        # 確定按鈕
        ok_button = tk.Button(
            popup,
            text="💀 我明白了 💀",
            font=('Arial', 14, 'bold'),
            bg='red',
            fg='white',
            command=popup.destroy
        )
        ok_button.pack(pady=10)
        
    def 創建彈窗(self):
        """創建單個恐怖彈窗"""
        popup = tk.Toplevel()
        popup.title("🚨 緊急警告 🚨")
        popup.geometry('350x200')
        popup.configure(bg='black')
        popup.attributes('-topmost', True)
        
        # 分布到整個螢幕
        # 將螢幕分成網格，確保彈窗分布均勻
        grid_x = random.randint(0, 8)  # 9列
        grid_y = random.randint(0, 5)  # 6行
        
        # 計算實際位置（假設螢幕解析度1920x1080）
        screen_width = 1920
        screen_height = 1080
        popup_width = 350
        popup_height = 200
        
        x = (grid_x * (screen_width - popup_width) // 8) + random.randint(-50, 50)
        y = (grid_y * (screen_height - popup_height) // 5) + random.randint(-50, 50)
        
        # 確保視窗不會超出螢幕邊界
        x = max(0, min(x, screen_width - popup_width))
        y = max(0, min(y, screen_height - popup_height))
        
        popup.geometry(f'{popup_width}x{popup_height}+{x}+{y}')
        
        # 隨機恐怖訊息
        message = random.choice(self.恐怖訊息)
        if "{}" in message:
            message = message.format(self.彈窗次數)
        
        # 警告標籤
        warning = tk.Label(
            popup,
            text=message,
            font=('Arial', 14, 'bold'),
            fg='red',
            bg='black',
            wraplength=300,
            justify='center'
        )
        warning.pack(expand=True, fill='both', padx=20, pady=20)
        
        # 確定按鈕
        ok_button = tk.Button(
            popup,
            text="💀 我明白了 💀",
            font=('Arial', 12, 'bold'),
            bg='red',
            fg='white',
            command=popup.destroy
        )
        ok_button.pack(pady=10)
        
        # 3秒後自動關閉
        popup.after(3000, popup.destroy)
        
    def 運行(self):
        """運行程式"""
        self.window.mainloop()

# 創建並運行恐怖程式
if __name__ == "__main__":
    print("🚨 警告：此程式將瘋狂彈出視窗！ 🚨")
    print("💀 按 Ctrl+C 可以強制關閉程式 💀")
    print("🔥 準備好迎接瘋狂的彈窗風暴了嗎？ 🔥")
    
    try:
        恐怖程式 = 恐怖中毒程式()
        恐怖程式.運行()
    except KeyboardInterrupt:
        print("\n💀 程式已強制關閉 💀")
    except Exception as e:
        print(f"💀 程式發生錯誤：{e} 💀")