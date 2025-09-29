import tkinter as tk
from tkinter import messagebox
import winsound
import time

class EnhancedSelfDestructApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Windows 系统安全警告")
        self.root.configure(bg='black')
        
        # 设置全屏
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        
        # 绑定退出快捷键
        self.root.bind('<Alt-F4>', self.emergency_exit)
        self.root.bind('<Escape>', self.emergency_exit)
        
        self.countdown_time = 10
        self.countdown_active = True
        
        # 播放警告声音
        self.play_warning_sound()
        
        self.setup_ui()
        self.start_countdown()
        
    def play_warning_sound(self):
        try:
            # 播放系统警告声音
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        except:
            pass
        
    def setup_ui(self):
        # 主框架
        main_frame = tk.Frame(self.root, bg='black')
        main_frame.pack(expand=True, fill='both')
        
        # 微软风格的警告头
        header_frame = tk.Frame(main_frame, bg='0078D4', height=40)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, text="Windows 安全中心", 
                               font=("Arial", 16, "bold"), fg='white', bg='0078D4')
        header_label.pack(side='left', padx=20)
        
        # 警告内容
        content_frame = tk.Frame(main_frame, bg='black')
        content_frame.pack(expand=True)
        
        # 警告图标
        warning_icon = "⚠️"
        icon_label = tk.Label(content_frame, text=warning_icon, font=("Arial", 72), 
                             fg='red', bg='black')
        icon_label.pack(pady=20)
        
        # 个性化警告信息
        warning_text = "董雨，系统检测到严重安全威胁！\n你的电脑将在十秒钟后启动自毁程序！\n\n威胁类型: 核心系统文件损坏\n影响级别: 严重\n建议操作: 立即备份重要数据"
        warning_label = tk.Label(content_frame, text=warning_text, font=("Arial", 18), 
                                fg='white', bg='black', justify='center')
        warning_label.pack(pady=20)
        
        # 倒计时显示
        self.countdown_label = tk.Label(content_frame, text=f"00:{self.countdown_time:02d}", 
                                       font=("Arial", 48, "bold"), fg='red', bg='black')
        self.countdown_label.pack(pady=30)
        
        # 隐藏提示
        hint_label = tk.Label(main_frame, text="提示: 按 Alt+F4 或 ESC 键可取消自毁程序", 
                             font=("Arial", 12), fg='gray', bg='black')
        hint_label.pack(side='bottom', pady=20)
        
    def start_countdown(self):
        self.update_countdown()
        
    def update_countdown(self):
        if self.countdown_time > 0 and self.countdown_active:
            self.countdown_label.config(text=f"00:{self.countdown_time:02d}")
            
            # 最后5秒播放滴答声
            if self.countdown_time <= 5:
                try:
                    winsound.Beep(1000, 200)
                except:
                    pass
            
            self.countdown_time -= 1
            self.root.after(1000, self.update_countdown)
        elif self.countdown_time == 0 and self.countdown_active:
            self.show_destruction_message()
            
    def show_destruction_message(self):
        self.countdown_label.config(text="自毁程序已启动！")
        
        # 播放爆炸声音
        try:
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
        except:
            pass
            
        # 显示爆炸效果
        self.create_explosion_effect()
        
    def create_explosion_effect(self):
        colors = ['red', 'orange', 'yellow', 'white']
        for color in colors:
            self.root.configure(bg=color)
            self.root.update()
            self.root.after(100)
        
        # 显示结束信息
        self.root.after(1000, self.show_exit_prompt)
        
    def show_exit_prompt(self):
        messagebox.showinfo("玩笑结束", 
                           "董雨，这只是个玩笑！\n\n"
                           "你的电脑完全安全，没有任何问题。\n"
                           "希望这个恶作剧让你笑了！😄\n\n"
                           "—— 来自你的朋友")
        self.emergency_exit()
        
    def emergency_exit(self, event=None):
        self.countdown_active = False
        self.root.destroy()

if __name__ == "__main__":
    app = EnhancedSelfDestructApp()
    app.root.mainloop()