import tkinter as tk
from tkinter import ttk
import datetime
import winsound

class TimerRow(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # 等級輸入
        self.level_var = tk.StringVar(value="")
        self.level_entry = tk.Entry(self, textvariable=self.level_var, width=6)
        self.level_entry.grid(row=0, column=0, padx=2)
        # 頻道下拉選單
        self.channel_var = tk.StringVar(value="ch1")
        self.channel_menu = ttk.Combobox(self, textvariable=self.channel_var, values=["ch1", "ch2", "ch3"], width=4, state="readonly")
        self.channel_menu.grid(row=0, column=1, padx=2)
        # 計時輸入（小時、分鐘）
        self.hour_var = tk.StringVar(value="0")
        self.min_var = tk.StringVar(value="0")
        self.hour_entry = tk.Entry(self, textvariable=self.hour_var, width=3)
        self.hour_entry.grid(row=0, column=2, padx=1)
        tk.Label(self, text="時").grid(row=0, column=3)
        self.min_entry = tk.Entry(self, textvariable=self.min_var, width=3)
        self.min_entry.grid(row=0, column=4, padx=1)
        tk.Label(self, text="分").grid(row=0, column=5)
        # 完成時間顯示
        self.finish_time_var = tk.StringVar(value="--:--")
        self.finish_time_label = tk.Label(self, textvariable=self.finish_time_var, width=8)
        self.finish_time_label.grid(row=0, column=6, padx=2)
        # 開始按鈕
        self.start_btn = tk.Button(self, text="開始", command=self.start_timer)
        self.start_btn.grid(row=0, column=7, padx=2)
        # 暫停/繼續按鈕
        self.pause_btn = tk.Button(self, text="暫停", command=self.pause_timer, state="disabled")
        self.pause_btn.grid(row=0, column=8, padx=2)
        # 倒數顯示
        self.countdown_var = tk.StringVar(value="00:00:00")
        self.countdown_label = tk.Label(self, textvariable=self.countdown_var, width=8, font=("Arial", 12))
        self.countdown_label.grid(row=0, column=9, padx=2)
        # 狀態
        self.remaining = 0
        self.running = False
        self.paused = False

    def start_timer(self):
        try:
            hours = int(self.hour_var.get())
            mins = int(self.min_var.get())
            self.remaining = hours * 3600 + mins * 60
            if self.remaining <= 0:
                self.countdown_var.set("00:00:00")
                return
            self.running = True
            self.paused = False
            self.pause_btn.config(state="normal", text="暫停")
            # 計算完成時間
            finish_time = (datetime.datetime.now() + datetime.timedelta(seconds=self.remaining)).strftime("%H:%M:%S")
            self.finish_time_var.set(finish_time)
            self.countdown()
        except ValueError:
            self.countdown_var.set("錯誤")

    def countdown(self):
        if self.running and not self.paused and self.remaining >= 0:
            h, rem = divmod(self.remaining, 3600)
            m, s = divmod(rem, 60)
            self.countdown_var.set(f"{h:02d}:{m:02d}:{s:02d}")
            if self.remaining == 0:
                self.running = False
                self.countdown_var.set("完成！")
                self.finish_time_var.set("--:--")
                self.pause_btn.config(state="disabled")
                for _ in range(3):
                    winsound.Beep(1000, 300)
            else:
                self.remaining -= 1
                self.after(1000, self.countdown)
        elif self.running and self.paused:
            # 暫停狀態，不繼續倒數
            pass

    def pause_timer(self):
        if self.running:
            if not self.paused:
                self.paused = True
                self.pause_btn.config(text="繼續")
            else:
                self.paused = False
                self.pause_btn.config(text="暫停")
                self.countdown()

def add_timer_row():
    row = TimerRow(root)
    row.grid(row=len(timer_rows)+1, column=0, columnspan=10, pady=2)
    timer_rows.append(row)

root = tk.Tk()
root.title("caca製計時器(初學版)")

# 標題列
header = ["等級", "頻道", "計時", "", "", "完成時間", "開始", "暫停", "倒數"]
for i, h in enumerate(header):
    tk.Label(root, text=h, font=("Arial", 10, "bold")).grid(row=0, column=i, padx=2, pady=2)

timer_rows = []

# 新增計時器按鈕
add_btn = tk.Button(root, text="新增計時器", command=add_timer_row)
add_btn.grid(row=100, column=0, columnspan=10, pady=10)

# 預設新增1個計時器
add_timer_row()

root.mainloop()