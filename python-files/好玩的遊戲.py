import tkinter as tk
import tkinter.messagebox
import random
import threading
import time
from tkinter import ttk
from playsound import playsound


class 恐怖中毒程式:

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("⚠️ 系統警告 ⚠️")
        self.window.geometry('400x300')
        self.window.configure(bg='black')

        self.window.attributes('-topmost', True)

        title_label = tk.Label(
            self.window, 
            text="🚨 系統已中毒 🚨", 
            font=('Arial', 16, 'bold'),
            fg='red',
            bg='black'
        )
        title_label.pack(pady=20)
        
        warning_text = tk.Label(
            self.window,
            text="⚠️ 警告：檢測到惡意程式入侵 ⚠️\n\n你的電腦已被病毒感染\n所有檔案正在被加密\n\n點擊下方按鈕開始緊急病毒清除",
            font=('Arial', 12),
            fg='red',
            bg='black',
            justify='center'
        )
        warning_text.pack(pady=20)
        
        self.clear_button = tk.Button(
            self.window,
            text="🚨 緊急!!開始清理病毒 🚨",
            font=('Arial', 12, 'bold'),
            bg='red',
            fg='white',
            command=self.開始瘋狂彈窗
        )
        self.clear_button.pack(pady=20)

        self.progress_label = tk.Label(
            self.window,
            text="進度：0/∞",
            font=('Arial', 10),
            fg='yellow',
            bg='black'
        )
        self.progress_label.pack(pady=10)

        self.彈窗次數 = 0
        self.目標次數 = 100
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

        threading.Thread(target=self.執行瘋狂彈窗, daemon=True).start()
        
    def 執行瘋狂彈窗(self):
        """執行瘋狂彈窗"""
        for i in range(self.目標次數):
            if not self.正在執行:
                break
                
            self.彈窗次數 += 1

            self.window.after(0, self.更新進度)

            彈窗數量 = min(15, 1 + (self.彈窗次數 // 10))
            
            for j in range(彈窗數量):
                threading.Timer(j * 0.05, self.創建彈窗).start()

            screen_width = 1920
            screen_height = 1080
            x = random.randint(0, screen_width - 400)
            y = random.randint(0, screen_height - 300)
            self.window.after(0, lambda x=x, y=y: self.window.geometry(f'400x300+{x}+{y}'))

            time.sleep(random.uniform(0.05, 0.2))

        self.window.after(0, self.顯示完成訊息)
        
    def 更新進度(self):
        """更新進度顯示"""
        self.progress_label.config(text=f"進度：{self.彈窗次數}/∞")
        self.clear_button.config(text=f"🚨 已執行 {self.彈窗次數} 次 🚨")
        
    def 顯示完成訊息(self):
        """顯示完成訊息"""
        self.progress_label.config(text="💀 清除完成！你的電腦已死亡 💀", fg='red')
        self.clear_button.config(text="💀 任務完成 💀", state='normal')

        for i in range(5):
            threading.Timer(i * 1, self.創建最終彈窗).start()
            
    def 創建最終彈窗(self):
        """創建最終的恐怖彈窗"""
        popup = tk.Toplevel()
        popup.title("💀 最終警告 💀")
        popup.geometry('400x250')
        popup.configure(bg='black')
        popup.attributes('-topmost', True)
        
        screen_width = 1920
        screen_height = 1080
        popup_width = 400
        popup_height = 250

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
        

        final_messages = [
            "💀 清除完成！你的電腦已徹底死亡 💀",
            "⚰️ 系統已停止運作，所有資料已銷毀 ⚰️",
            "🔥 電腦正在燃燒，請立即逃離 🔥",
            "👻 幽靈程式已佔領你的電腦 👻",
            "🎭 小丑說：遊戲結束了 🎭"
        ]
        
        message = random.choice(final_messages)

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

        grid_x = random.randint(0, 8)  
        grid_y = random.randint(0, 5)  

        screen_width = 1920
        screen_height = 1080
        popup_width = 350
        popup_height = 200
        
        x = (grid_x * (screen_width - popup_width) // 8) + random.randint(-50, 50)
        y = (grid_y * (screen_height - popup_height) // 5) + random.randint(-50, 50)

        x = max(0, min(x, screen_width - popup_width))
        y = max(0, min(y, screen_height - popup_height))
        
        popup.geometry(f'{popup_width}x{popup_height}+{x}+{y}')

        message = random.choice(self.恐怖訊息)
        if "{}" in message:
            message = message.format(self.彈窗次數)

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

        ok_button = tk.Button(
            popup,
            text="💀 我明白了 💀",
            font=('Arial', 12, 'bold'),
            bg='red',
            fg='white',
            command=popup.destroy
        )
        ok_button.pack(pady=10)

        popup.after(3000, popup.destroy)
        
    def 運行(self):
        """運行程式"""
        self.window.mainloop()

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


class 當機模擬程式:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("系統錯誤")
        self.window.attributes('-fullscreen', True)
        self.window.configure(bg='#0078D7')  # Windows藍
        
        self.建立畫面()

    def 建立畫面(self):
        # 表情符號
        emoji_label = tk.Label(self.window, text=":(", font=('Arial', 150, 'bold'), bg='#0078D7', fg='white')
        emoji_label.pack(pady=30)

        # 錯誤文字
        error_text = (
            "Your PC has encountered a problem\n"
            "and needs to restart. You can restart\n"
            "without losing your current activity.\n\n"
            "0% complete\n\n"
            "For more information, visit https://www.widows.com/stopcode\n\n"
            "If you call a support person, give them this info:\n"
            "STOP CODE: UNDEAD COMPUTER\n"
            "Password: Kobe01020412"
        )

        text_label = tk.Label(self.window, text=error_text, font=('Arial', 16), bg='#0078D7', fg='white', justify='center')
        text_label.pack()

        # 關閉按鈕（避免真的卡死）
        close_button = tk.Button(self.window, text="🔒 輸入密碼解除", font=('Arial', 14, 'bold'), bg='white', fg='black', command=self.解鎖畫面)
        close_button.pack(pady=20)

    def 解鎖畫面(self):
        # 密碼輸入視窗
        密碼視窗 = tk.Toplevel()
        密碼視窗.title("密碼驗證")
        密碼視窗.geometry("300x150")
        密碼視窗.configure(bg='black')
        密碼視窗.attributes('-topmost', True)

        label = tk.Label(密碼視窗, text="請輸入密碼解除：", font=('Arial', 12), bg='black', fg='white')
        label.pack(pady=10)

        密碼框 = tk.Entry(密碼視窗, show='*', font=('Arial', 14))
        密碼框.pack(pady=5)

        def 驗證密碼():
            if 密碼框.get() == "Kobe01020412":
                self.window.destroy()
            else:
                label.config(text="❌ 密碼錯誤", fg='red')

        確認鍵 = tk.Button(密碼視窗, text="確認", font=('Arial', 12), bg='red', fg='white', command=驗證密碼)
        確認鍵.pack(pady=10)

    def 運行(self):
        self.window.mainloop()

if __name__ == "__main__":
    當機 = 當機模擬程式()
    當機.運行()
