import tkinter as tk
from tkinter import messagebox
import os

# مسار مجلد FIFA 18 في المستندات
fifa_docs_path = os.path.expanduser("~/Documents/FIFA 18")
config_file_path = os.path.join(fifa_docs_path, "fifasetup.ini")

# إعدادات منخفضة مع دقة مخصصة
def generate_settings(width, height):
    return f"""[SETTINGS]
RESOLUTIONWIDTH = {width}
RESOLUTIONHEIGHT = {height}
FULLSCREEN = 1
MSAA_LEVEL = 0
RENDERINGQUALITY = 0
POSTPROCESSING = 0
DYNAMICSHADOWS = 0
CROWD = 0
GRASS = 0
LOCKTO60 = 0
ANTIALIASING = 0
SHADOWQUALITY = 0
TEXTUREQUALITY = 0
FRAMERATECAP = 0
"""

# تطبيق الإعدادات
def apply_low_settings():
    try:
        width = resolution_var.get().split("x")[0]
        height = resolution_var.get().split("x")[1]
        content = generate_settings(width, height)
        os.makedirs(fifa_docs_path, exist_ok=True)
        with open(config_file_path, "w") as file:
            file.write(content)
        messagebox.showinfo("نجاح", f"تم تطبيق إعدادات فيفا 18 بدقة {width}x{height} بنجاح!")
    except Exception as e:
        messagebox.showerror("خطأ", f"حدث خطأ أثناء حفظ الإعدادات:\n{e}")

# واجهة البرنامج
root = tk.Tk()
root.title("FIFA 18 Low Settings")
root.geometry("350x200")

label = tk.Label(root, text="اختر دقة الشاشة:", font=("Arial", 12))
label.pack(pady=10)

# قائمة اختيار الدقة
resolutions = ["800x600", "1024x768", "1280x720", "1366x768"]
resolution_var = tk.StringVar(value=resolutions[0])
resolution_menu = tk.OptionMenu(root, resolution_var, *resolutions)
resolution_menu.pack(pady=5)

apply_button = tk.Button(root, text="تطبيق الإعدادات", command=apply_low_settings, bg="green", fg="white", font=("Arial", 10))
apply_button.pack(pady=20)

root.mainloop()
