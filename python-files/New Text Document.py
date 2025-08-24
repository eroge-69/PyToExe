import tkinter as tk
from pynput.keyboard import Controller, Key

# --- تنظیمات ظاهری (می‌توانید این مقادیر را تغییر دهید) ---
BG_COLOR = "#282828"  # رنگ پس‌زمینه نوار کنترل
BTN_COLOR = "#404040" # رنگ دکمه‌ها
FG_COLOR = "#FFFFFF"  # رنگ آیکون‌ها (متن)
FONT_STYLE = ("Segoe UI Symbol", 12) # فونت و اندازه آیکون‌ها
INITIAL_GEOMETRY = "150x40+100+100" # عرضxارتفاع+موقعیت افقی+موقعیت عمودی اولیه

class MediaController:
    def __init__(self, root):
        self.root = root
        self.keyboard = Controller()

        # --- تنظیمات اصلی پنجره ---
        self.root.title("Media Controller")
        self.root.geometry(INITIAL_GEOMETRY)
        
        # حذف قاب و نوار عنوان پنجره
        self.root.overrideredirect(True)
        
        # همیشه بالا نگه داشتن پنجره
        self.root.attributes('-topmost', True)
        
        # تنظیم رنگ پس‌زمینه
        self.root.config(bg=BG_COLOR)

        # متغیرهایی برای جابجایی پنجره با ماوس
        self._offset_x = 0
        self._offset_y = 0

        # --- اتصال رویدادهای ماوس برای جابجایی پنجره ---
        self.root.bind('<Button-1>', self.click_window)
        self.root.bind('<B1-Motion>', self.drag_window)

        # --- ساخت دکمه‌های کنترل ---
        self.create_widgets()

        # --- ساخت منوی راست‌کلیک برای بستن برنامه ---
        self.create_right_click_menu()

    def create_widgets(self):
        # فریم اصلی برای قرار دادن دکمه‌ها
        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # تنظیم وزن ستون‌ها برای توزیع یکسان فضا
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # دکمه قبلی
        prev_button = tk.Button(main_frame, text="⏮", command=self.press_prev, **self.button_style())
        prev_button.grid(row=0, column=0, sticky="nsew")

        # دکمه پخش/توقف
        play_pause_button = tk.Button(main_frame, text="⏯", command=self.press_play_pause, **self.button_style())
        play_pause_button.grid(row=0, column=1, sticky="nsew")

        # دکمه بعدی
        next_button = tk.Button(main_frame, text="⏭", command=self.press_next, **self.button_style())
        next_button.grid(row=0, column=2, sticky="nsew")

    def button_style(self):
        """استایل مشترک برای همه دکمه‌ها"""
        return {
            "font": FONT_STYLE,
            "bg": BTN_COLOR,
            "fg": FG_COLOR,
            "relief": "flat",
            "borderwidth": 0,
            "activebackground": "#555555",
            "activeforeground": "#FFFFFF"
        }

    # --- توابع شبیه‌سازی کلیدهای مدیا ---
    def press_play_pause(self):
        self.keyboard.press(Key.media_play_pause)
        self.keyboard.release(Key.media_play_pause)

    def press_next(self):
        self.keyboard.press(Key.media_next)
        self.keyboard.release(Key.media_next)

    def press_prev(self):
        self.keyboard.press(Key.media_previous)
        self.keyboard.release(Key.media_previous)
        
    # --- توابع مربوط به جابجایی پنجره ---
    def drag_window(self, event):
        x = self.root.winfo_pointerx() - self._offset_x
        y = self.root.winfo_pointery() - self._offset_y
        self.root.geometry(f'+{x}+{y}')

    def click_window(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    # --- منوی راست‌کلیک ---
    def create_right_click_menu(self):
        self.right_click_menu = tk.Menu(self.root, tearoff=0, bg="#4f4f4f", fg="white")
        self.right_click_menu.add_command(label="بستن", command=self.root.destroy)
        
        # اتصال رویداد راست‌کلیک به پنجره
        self.root.bind("<Button-3>", self.show_right_click_menu)

    def show_right_click_menu(self, event):
        try:
            self.right_click_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.right_click_menu.grab_release()


if __name__ == "__main__":
    app_root = tk.Tk()
    controller_app = MediaController(app_root)
    app_root.mainloop()