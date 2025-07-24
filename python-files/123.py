import tkinter as tk
from tkinter import font
import random
import threading
import time
import sys
import winsound  # 用于声音（Windows 专用）

class FakeVirusApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')
        self.root.overrideredirect(True)  # 无边框

        # 病毒消息
        self.messages = [
            '你的电脑已经中病毒',
            '数据正在被加密...',
            '立即输入密码以避免数据丢失！'
        ]
        self.virus_label = tk.Label(self.root, text=random.choice(self.messages), fg='red', bg='black',
                                    font=font.Font(family='Arial', size=72, weight='bold'))
        self.virus_label.place(relx=0.5, rely=0.4, anchor='center')

        # 倒计时
        self.time_left = 600  # 10 分钟
        self.countdown_label = tk.Label(self.root, text='', fg='yellow', bg='black', font=('Arial', 24))
        self.countdown_label.place(relx=0.5, rely=0.6, anchor='center')

        # 密码输入
        tk.Label(self.root, text='输入解锁密码以修复：', fg='white', bg='black', font=('Arial', 24)).place(relx=0.5, rely=0.75, anchor='center')
        self.password_entry = tk.Entry(self.root, show='*', font=('Arial', 24), bg='black', fg='white', insertbackground='white')
        self.password_entry.place(relx=0.5, rely=0.8, anchor='center', width=300)
        self.password_entry.bind('<Return>', self.check_password)

        tk.Button(self.root, text='提交', command=self.check_password, bg='red', fg='black', font=('Arial', 24)).place(relx=0.5, rely=0.85, anchor='center')

        # 错误消息
        self.error_label = tk.Label(self.root, text='', fg='yellow', bg='black', font=('Arial', 18))
        self.error_label.place(relx=0.5, rely=0.9, anchor='center')

        # 扫描动画
        self.scan_label = tk.Label(self.root, text='系统扫描中...', fg='white', bg='black', font=('Arial', 18))
        self.scan_label.place(relx=0.5, rely=0.95, anchor='center')

        # 绑定键
        self.root.bind('<Control-q>', lambda e: self.root.destroy())
        self.root.bind('<Alt-F4>', lambda e: None)  # 禁用 Alt+F4

        # 启动线程
        threading.Thread(target=self.update_threat, daemon=True).start()
        threading.Thread(target=self.flash_background, daemon=True).start()
        threading.Thread(target=self.start_countdown, daemon=True).start()
        threading.Thread(target=self.fake_scan, daemon=True).start()
        threading.Thread(target=self.play_sound, daemon=True).start()

        self.root.mainloop()

    def update_threat(self):
        while True:
            self.virus_label.config(text=random.choice(self.messages))
            time.sleep(3)

    def flash_background(self):
        while True:
            self.root.config(bg='darkred' if self.root['bg'] == 'black' else 'black')
            time.sleep(1)

    def start_countdown(self):
        while self.time_left > 0:
            min_ = self.time_left // 60
            sec = self.time_left % 60
            self.countdown_label.config(text=f'剩余时间: {min_}:{sec:02d}')
            self.time_left -= 1
            time.sleep(1)

    def fake_scan(self):
        dots = 0
        while True:
            dots = (dots + 1) % 4
            self.scan_label.config(text='系统扫描中' + '.' * dots)
            time.sleep(0.5)

    def play_sound(self):
        while True:
            winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)  # 系统警报声
            time.sleep(2)  # 循环播放

    def check_password(self, event=None):
        if self.password_entry.get() == 'qzfh':
            self.root.destroy()
        else:
            self.error_label.config(text='密码错误！')
            self.root.after(3000, lambda: self.error_label.config(text=''))
            self.password_entry.delete(0, tk.END)

if __name__ == '__main__':
    FakeVirusApp()