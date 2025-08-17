
import tkinter as tk
from tkinter import colorchooser, font
import pyperclip
import threading
import time
import winsound  # يعمل فقط على Windows

class AdvancedNewsTicker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("قناة نسارع الزمان – مباشر الآن")
        self.root.geometry("900x160")
        self.root.configure(bg='black')
        self.root.resizable(True, False)

        self.news_text = "🔴 عاجل | الجيش يعلن حالة الطوارئ | تابعونا عبر قناة نسارع الزمان | "
        self.alert_text = "▪︎ إسرائيل تمارس إبادة جماعية في غزة وجريمة حرب يجب المحاسبة عليها"
        self.manual_text = tk.StringVar()
        self.running = True
        self.use_clipboard = True
        self.font_style = ("Arial", 14, "bold")
        self.bg_color = "navy"
        self.text_color = "white"

        self.label = tk.Label(self.root, text=self.news_text, fg=self.text_color, bg=self.bg_color, font=self.font_style, anchor='w')
        self.label.pack(fill='x')

        self.alert_label = tk.Label(self.root, text=self.alert_text, fg='white', bg='darkred', font=self.font_style, anchor='w')
        self.alert_label.pack(fill='x')

        self.manual_entry = tk.Entry(self.root, textvariable=self.manual_text, font=self.font_style, bg='black', fg='white')
        self.manual_entry.pack(fill='x')

        self.clock_label = tk.Label(self.root, fg='white', bg='black', font=('Arial', 12))
        self.clock_label.place(x=820, y=5)

        button_frame = tk.Frame(self.root, bg='black')
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="🎨 ألوان/خط", command=self.change_style).pack(side='left', padx=5)
        tk.Button(button_frame, text="📋 تشغيل/إيقاف الحافظة", command=self.toggle_clipboard).pack(side='left', padx=5)
        tk.Button(button_frame, text="🔍 تكبير", command=lambda: self.resize_ui(1.2)).pack(side='left', padx=5)
        tk.Button(button_frame, text="🔎 تصغير", command=lambda: self.resize_ui(0.8)).pack(side='left', padx=5)

        threading.Thread(target=self.scroll_text, daemon=True).start()
        threading.Thread(target=self.watch_clipboard, daemon=True).start()
        self.update_time()

        self.root.mainloop()

    def scroll_text(self):
        while self.running:
            self.news_text = self.news_text[1:] + self.news_text[0]
            self.label.config(text=self.news_text)
            time.sleep(0.15)

    def update_time(self):
        now = time.strftime("%H:%M:%S")
        self.clock_label.config(text=now)
        self.root.after(1000, self.update_time)

    def toggle_clipboard(self):
        self.use_clipboard = not self.use_clipboard

    def watch_clipboard(self):
        last_text = ""
        while self.running:
            if self.use_clipboard:
                try:
                    current = pyperclip.paste()
                    if current != last_text and len(current.strip()) > 3:
                        self.news_text = "🔴 عاجل | " + current + " | "
                        winsound.Beep(1000, 300)
                        last_text = current
                except:
                    pass
            time.sleep(1)

    def change_style(self):
        color = colorchooser.askcolor(title="اختر لون الخلفية")[1]
        font_choice = font.askfont(self.root)
        if color:
            self.bg_color = color
            self.label.config(bg=color)
        if font_choice:
            self.font_style = (font_choice['family'], int(font_choice['size']), "bold")
            self.label.config(font=self.font_style)
            self.alert_label.config(font=self.font_style)
            self.manual_entry.config(font=self.font_style)

    def resize_ui(self, factor):
        width = int(self.root.winfo_width() * factor)
        height = int(self.root.winfo_height() * factor)
        self.root.geometry(f"{width}x{height}")

AdvancedNewsTicker()
