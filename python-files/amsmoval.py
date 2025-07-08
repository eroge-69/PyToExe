
import tkinter as tk
import ctypes
import os

# تحميل ملف DLL
dll_path = os.path.join(os.path.dirname(__file__), "iremovalpro.dll")
try:
    iremoval_dll = ctypes.CDLL(dll_path)
except Exception as e:
    iremoval_dll = None
    print(f"فشل في تحميل DLL: {e}")

# دوال مرتبطة بـ DLL أو وهمية للتجريب
def activate():
    if iremoval_dll and hasattr(iremoval_dll, "activate"):
        iremoval_dll.activate()
    else:
        print("Activate called (mock)")

def erase():
    if iremoval_dll and hasattr(iremoval_dll, "erase"):
        iremoval_dll.erase()
    else:
        print("Erase called (mock)")

def check_status():
    if iremoval_dll and hasattr(iremoval_dll, "check_status"):
        iremoval_dll.check_status()
    else:
        print("Check Status called (mock)")

def exit_app():
    root.destroy()

# إعداد الواجهة
root = tk.Tk()
root.title("amsmoval - Device Tool")
root.geometry("600x400")
root.configure(bg="#141414")  # لون داكن مثل Netflix

# عنوان
title = tk.Label(root, text="amsmoval", font=("Arial", 28, "bold"), fg="red", bg="#141414")
title.pack(pady=20)

# أزرار الوظائف
button_style = {"font": ("Arial", 14), "width": 20, "bg": "#e50914", "fg": "white", "bd": 0, "activebackground": "#b00610"}

tk.Button(root, text="Activate Device", command=activate, **button_style).pack(pady=10)
tk.Button(root, text="Erase iCloud", command=erase, **button_style).pack(pady=10)
tk.Button(root, text="Check Status", command=check_status, **button_style).pack(pady=10)
tk.Button(root, text="Exit", command=exit_app, bg="#444", activebackground="#222", **button_style).pack(pady=30)

root.mainloop()
