from tkinter import *
from time import *
from random import randint

# ========== 狀態變數 ==========
use_24_hour = False
is_daytime = None
current_font_index = 0
current_theme_index = 0  # 用來手動切換主題

font_list = ["Press Start 2P", "Minecraftia", "Arial"]

# ========== 主題配色定義 ==========
THEMES = [
    {
        "name": "day",
        "bg": "#FFFFFF",
        "fg": "#000000"
    },
    {
        "name": "night",
        "bg": "#000000",
        "fg": "#00FF00"
    },
    {
        "name": "coffee",
        "bg": "#f4e3cf",
        "fg": "#5e3d2c"
    }
]

# ========== 主視窗 ==========
window = Tk()
window.title("不透明黑客時鐘")
window.minsize(1, 1)

# ========== 更新時間 ==========
def update():
    global use_24_hour, is_daytime

    time_format = "%H:%M:%S" if use_24_hour else "%I:%M:%S %p"
    time_label.config(text=strftime(time_format))
    day_label.config(text=strftime("%A"))
    date_label.config(text=strftime("%B %d, %Y"))

    hour = int(strftime("%H"))
    now_daytime = 6 <= hour < 18
    if now_daytime != is_daytime:
        is_daytime = now_daytime
        auto_switch_theme(now_daytime)

    time_label.after(1000, update)

# ========== 根據白天/夜晚自動切換主題 ==========
def auto_switch_theme(day=True):
    theme_name = "day" if day else "night"
    apply_theme_by_name(theme_name)

# ========== 根據主題名稱切換主題 ==========
def apply_theme_by_name(name):
    global current_theme_index
    for i, theme in enumerate(THEMES):
        if theme["name"] == name:
            current_theme_index = i
            apply_theme(theme)
            return

# ========== 套用主題 ==========
def apply_theme(theme):
    bg, fg = theme["bg"], theme["fg"]
    window.configure(bg=bg)
    for label in (time_label, day_label, date_label):
        label.config(bg=bg, fg=fg)

# ========== 手動切換主題 ==========
def toggle_theme(event=None):
    global current_theme_index
    current_theme_index = (current_theme_index + 1) % len(THEMES)
    apply_theme(THEMES[current_theme_index])

# ========== 切換 12/24 時制 ==========
def toggle_time_format(event=None):
    global use_24_hour
    use_24_hour = not use_24_hour

# ========== 切換字體 ==========
def toggle_font(event=None):
    global current_font_index
    current_font_index = (current_font_index + 1) % len(font_list)
    apply_font_sizes()

# ========== 根據視窗大小調整字體大小 ==========
def apply_font_sizes(event=None):
    width = window.winfo_width()
    height = window.winfo_height()

    font_name = font_list[current_font_index]
    time_size = max(8, width // 15)
    day_size = max(6, width // 25)
    date_size = max(5, width // 30)

    time_label.config(font=(font_name, time_size))
    day_label.config(font=(font_name, day_size))
    date_label.config(font=(font_name, date_size))

# ========== 三大 Label ==========
time_label = Label(window)
time_label.pack()

day_label = Label(window)
day_label.pack()

date_label = Label(window)
date_label.pack()

# ========== 鍵盤與事件綁定 ==========
window.bind("<Configure>", apply_font_sizes)
window.bind("<t>", toggle_time_format)
window.bind("<T>", toggle_time_format)
window.bind("<f>", toggle_font)
window.bind("<F>", toggle_font)
window.bind("<m>", toggle_theme)
window.bind("<M>", toggle_theme)

# ========== 啟動 ==========
apply_theme_by_name("day")  # 預設從白天開始
apply_font_sizes()
update()
window.mainloop()
