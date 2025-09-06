import tkinter as tk

# تنظیمات خط خراب
LINE_WIDTH = 2
LINE_COLOR = "#00FF00"  # سبز روشن، شبیه پیکسل سوخته واقعی
LINE_ORIENTATION = "vertical"  # خط عمودی

# ایجاد پنجره بدون قاب
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-transparentcolor", "white")

# گرفتن اندازه صفحه
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# تنظیم اندازه پنجره بر اساس نوع خط
if LINE_ORIENTATION == "vertical":
    root.geometry(f"{LINE_WIDTH}x{screen_height}+{screen_width//2}+0")
else:
    root.geometry(f"{screen_width}x{LINE_WIDTH}+0+{screen_height//2}")

# ساخت canvas
canvas = tk.Canvas(root, width=screen_width, height=screen_height, highlightthickness=0, bg="white")
canvas.pack()

# کشیدن خط
if LINE_ORIENTATION == "vertical":
    canvas.create_line(LINE_WIDTH//2, 0, LINE_WIDTH//2, screen_height, fill=LINE_COLOR, width=LINE_WIDTH)
else:
    canvas.create_line(0, LINE_WIDTH//2, screen_width, LINE_WIDTH//2, fill=LINE_COLOR, width=LINE_WIDTH)

root.mainloop()