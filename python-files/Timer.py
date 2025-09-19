import time
import ttkbootstrap as tb
from tkinter import messagebox


class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⏳ تایمر")
        self.root.geometry("400x300")

        # انتخاب تم (پیش‌فرض: لایت)
        self.style = tb.Style("flatly")

        # عنوان
        self.label = tb.Label(root, text="مدت زمان (دقیقه):", font=("Arial", 14))
        self.label.pack(pady=10)

        # ورودی
        self.entry = tb.Entry(root, font=("Arial", 14), justify="center", width=10, bootstyle="info")
        self.entry.pack(pady=5)

        # نمایش تایمر
        self.time_label = tb.Label(root, text="00:00", font=("Arial", 36, "bold"), bootstyle="danger")
        self.time_label.pack(pady=15)

        # دکمه‌ها
        btn_frame = tb.Frame(root)
        btn_frame.pack(pady=10)

        self.start_btn = tb.Button(btn_frame, text="شروع", bootstyle="success-outline", command=self.start_timer)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = tb.Button(btn_frame, text="⏸ توقف", bootstyle="warning-outline", command=self.pause_timer, state="disabled")
        self.pause_btn.grid(row=0, column=1, padx=5)

        self.resume_btn = tb.Button(btn_frame, text="▶ ادامه", bootstyle="info-outline", command=self.resume_timer, state="disabled")
        self.resume_btn.grid(row=0, column=2, padx=5)

        self.reset_btn = tb.Button(btn_frame, text="🔄 ریست", bootstyle="secondary-outline", command=self.reset_timer, state="disabled")
        self.reset_btn.grid(row=0, column=3, padx=5)

        # دکمه تغییر حالت (دارک/لایت)
        self.mode_btn = tb.Button(root, text="🌙 دارک/لایت مود", bootstyle="dark-outline", command=self.toggle_mode)
        self.mode_btn.pack(pady=10)

        # متغیرها
        self.remaining_time = 0
        self.end_time = None
        self.running = False
        self.paused = False
        self.dark_mode = False

    def start_timer(self):
        try:
            minutes = int(self.entry.get())
            self.remaining_time = minutes * 60
            self.end_time = time.time() + self.remaining_time
            self.running = True
            self.paused = False
            self.update_timer()

            self.start_btn.config(state="disabled")
            self.pause_btn.config(state="normal")
            self.reset_btn.config(state="normal")

        except ValueError:
            messagebox.showerror("خطا", "لطفاً عدد صحیح وارد کنید!")

    def update_timer(self):
        if self.running and not self.paused:
            self.remaining_time = int(self.end_time - time.time())
            if self.remaining_time > 0:
                mins, secs = divmod(self.remaining_time, 60)
                self.time_label.config(text=f"{mins:02}:{secs:02}")
                self.root.after(1000, self.update_timer)
            else:
                self.time_label.config(text="00:00")
                self.running = False
                messagebox.showinfo("پایان", "⏰ زمان تمام شد!")
                self.start_btn.config(state="normal")
                self.pause_btn.config(state="disabled")
                self.resume_btn.config(state="disabled")
                self.reset_btn.config(state="disabled")

    def pause_timer(self):
        if self.running:
            self.paused = True
            self.remaining_time = int(self.end_time - time.time())
            self.pause_btn.config(state="disabled")
            self.resume_btn.config(state="normal")

    def resume_timer(self):
        if self.paused:
            self.end_time = time.time() + self.remaining_time
            self.paused = False
            self.resume_btn.config(state="disabled")
            self.pause_btn.config(state="normal")
            self.update_timer()

    def reset_timer(self):
        self.running = False
        self.paused = False
        self.time_label.config(text="00:00")
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="disabled")
        self.reset_btn.config(state="disabled")

    def toggle_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.style.theme_use("darkly")  # تم تاریک
        else:
            self.style.theme_use("flatly")  # تم روشن


# اجرای برنامه
if __name__ == "__main__":
    root = tb.Window(themename="flatly")
    app = TimerApp(root)
    root.mainloop()
