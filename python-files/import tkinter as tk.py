import tkinter as tk
import time

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🐧美极计时器🐧")
        self.root.attributes('-topmost', True)
        self.root.geometry("340x260")
        self.root.resizable(False, False)

        # 渐变背景
        self.bg_canvas = tk.Canvas(root, width=340, height=260, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.draw_gradient(self.bg_canvas, "#4e54c8", "#8f94fb")

        # 内容框架，白色
        self.content_frame = tk.Frame(root, bg="#ffffff")
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center", width=300, height=220)

        self.running = False
        self.start_time = None
        self.time_limit = 0
        self.elapsed = 0
        self.overtime = 0

        self.label = tk.Label(self.content_frame, text="00:00:00", font=("Arial", 36, "bold"), fg="#222", bg="#ffffff")
        self.label.pack(pady=8)

        # 快速设置按钮
        quick_frame = tk.Frame(self.content_frame, bg="#ffffff")
        quick_frame.pack(pady=(0, 3))
        for min_ in [10, 15, 20, 40]:
            btn = tk.Button(
                quick_frame, text=f"{min_}分钟", font=("Arial", 11),
                command=lambda m=min_: self.quick_set(m), 
                bg="#e3e6fd", fg="#4e54c8", activebackground="#c0c7fa", relief="flat", bd=0, width=6, height=1
            )
            btn.pack(side="left", padx=4)

        self.entry = tk.Entry(self.content_frame, font=("Arial", 16), width=10, justify="center", bg="#f7f7fa", relief="flat")
        self.entry.insert(0, "05:00")
        self.entry.pack(pady=5)

        btn_frame = tk.Frame(self.content_frame, bg="#ffffff")
        btn_frame.pack(fill="x", pady=10, padx=6)

        self.start_btn = tk.Button(btn_frame, text="开始", font=("Arial", 14), command=self.start, bg="#6a82fb", fg="white", activebackground="#4e54c8", relief="flat", bd=0)
        self.pause_btn = tk.Button(btn_frame, text="暂停", font=("Arial", 14), command=self.pause, state='disabled', bg="#bdbdbd", fg="white", activebackground="#888", relief="flat", bd=0)
        self.reset_btn = tk.Button(btn_frame, text="重置", font=("Arial", 14), command=self.reset, bg="#ffb347", fg="white", activebackground="#ffcc80", relief="flat", bd=0)

        self.start_btn.grid(row=0, column=0, sticky="ew", padx=4)
        self.pause_btn.grid(row=0, column=1, sticky="ew", padx=4)
        self.reset_btn.grid(row=0, column=2, sticky="ew", padx=4)

        btn_frame.grid_columnconfigure(0, weight=1, minsize=80)
        btn_frame.grid_columnconfigure(1, weight=1, minsize=80)
        btn_frame.grid_columnconfigure(2, weight=1, minsize=80)

    def draw_gradient(self, canvas, color1, color2):
        r1, g1, b1 = self.root.winfo_rgb(color1)
        r2, g2, b2 = self.root.winfo_rgb(color2)
        r_ratio = (r2 - r1) / 260
        g_ratio = (g2 - g1) / 260
        b_ratio = (b2 - b1) / 260
        for i in range(260):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = f"#{nr//256:02x}{ng//256:02x}{nb//256:02x}"
            canvas.create_line(0, i, 340, i, fill=color)

    def quick_set(self, mins):
        self.entry.config(state='normal', bg="#f7f7fa")
        self.entry.delete(0, tk.END)
        self.entry.insert(0, f"{mins:02d}:00")

    def start(self):
        if not self.running:
            if self.start_time is None:
                try:
                    mins, secs = map(int, self.entry.get().split(":"))
                    self.time_limit = mins * 60 + secs
                    self.entry.config(bg="#f7f7fa")
                except:
                    self.entry.delete(0, tk.END)
                    self.entry.insert(0, "格式:mm:ss")
                    self.entry.config(bg="#ffd1d1")
                    return
                self.start_time = time.time()
            else:
                self.start_time = time.time() - self.elapsed
            self.running = True
            self.start_btn.config(state='disabled')
            self.pause_btn.config(state='normal')
            self.entry.config(state='disabled', bg="#f7f7fa")
            self.update_timer()
    
    def update_timer(self):
        if self.running:
            self.elapsed = int(time.time() - self.start_time)
            if self.elapsed <= self.time_limit:
                remain = self.time_limit - self.elapsed
                self.label.config(text=self.format_time(remain), fg="#222")
            else:
                self.overtime = self.elapsed - self.time_limit
                self.label.config(text=f"超时 {self.format_time(self.overtime)}", fg="#e53935")
            self.root.after(1000, self.update_timer)
    
    def pause(self):
        if self.running:
            self.running = False
            self.start_btn.config(state='normal')
            self.pause_btn.config(state='disabled')
    
    def reset(self):
        self.running = False
        self.start_time = None
        self.elapsed = 0
        self.overtime = 0
        self.label.config(text="00:00:00", fg="#222")
        self.start_btn.config(state='normal')
        self.pause_btn.config(state='disabled')
        self.entry.config(state='normal', bg="#f7f7fa")
        self.entry.delete(0, tk.END)
        self.entry.insert(0, "05:00")
    
    def format_time(self, seconds):
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        else:
            return f"{m:02d}:{s:02d}"

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
