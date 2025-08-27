import os
import tkinter as tk
from tkinter import messagebox

# ---- CONFIG PATHS ----
CONFIG_FILE = r"C:\Program Files\TxGameAssistant\AppMarket\Config.ini"
CACHE_FOLDER = r"C:\Program Files\TxGameAssistant\AndroidEmulator\Engine\Cache"

# ---- FUNCTIONS ----
def set_fps():
    fps_value = fps_slider.get()
    try:
        with open(CONFIG_FILE, "r") as file:
            lines = file.readlines()
        with open(CONFIG_FILE, "w") as file:
            for line in lines:
                if "FrameRate=" in line:
                    file.write(f"FrameRate={fps_value}\n")
                else:
                    file.write(line)
        messagebox.showinfo("Success", f"FPS set to {fps_value}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def set_resolution(width, height):
    try:
        with open(CONFIG_FILE, "r") as file:
            lines = file.readlines()
        with open(CONFIG_FILE, "w") as file:
            for line in lines:
                if "ScreenWidth=" in line:
                    file.write(f"ScreenWidth={width}\n")
                elif "ScreenHeight=" in line:
                    file.write(f"ScreenHeight={height}\n")
                else:
                    file.write(line)
        messagebox.showinfo("Success", f"Resolution set to {width}x{height}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def set_ram():
    ram_value = ram_slider.get()
    try:
        with open(CONFIG_FILE, "r") as file:
            lines = file.readlines()
        with open(CONFIG_FILE, "w") as file:
            for line in lines:
                if "Memory=" in line:
                    file.write(f"Memory={ram_value}G\n")
                else:
                    file.write(line)
        messagebox.showinfo("Success", f"RAM allocation set to {ram_value} GB")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def set_cpu():
    cores = cpu_slider.get()
    try:
        with open(CONFIG_FILE, "r") as file:
            lines = file.readlines()
        with open(CONFIG_FILE, "w") as file:
            for line in lines:
                if "CPU=" in line:
                    file.write(f"CPU={cores}\n")
                else:
                    file.write(line)
        messagebox.showinfo("Success", f"CPU cores set to {cores}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def clear_cache():
    try:
        for root, dirs, files in os.walk(CACHE_FOLDER):
            for f in files:
                os.remove(os.path.join(root, f))
        messagebox.showinfo("Success", "Shader/cache cleared successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---- GUI ----
root = tk.Tk()
root.title("Ultimate Gameloop Tweaker")
root.geometry("400x550")

# FPS Slider
tk.Label(root, text="FPS:").pack(pady=5)
fps_slider = tk.Scale(root, from_=30, to=144, orient=tk.HORIZONTAL)
fps_slider.set(120)
fps_slider.pack()
tk.Button(root, text="Apply FPS", command=set_fps).pack(pady=5)

# Resolution Buttons
tk.Label(root, text="Resolution Presets:").pack(pady=5)
tk.Button(root, text="1080p (1920x1080)", command=lambda: set_resolution(1920,1080)).pack(pady=2)
tk.Button(root, text="1440p (2560x1440)", command=lambda: set_resolution(2560,1440)).pack(pady=2)
tk.Button(root, text="iPad (2048x1536)", command=lambda: set_resolution(2048,1536)).pack(pady=2)
tk.Button(root, text="1920x1440", command=lambda: set_resolution(1920,1440)).pack(pady=2)
tk.Button(root, text="1728x1296", command=lambda: set_resolution(1728,1296)).pack(pady=2)
tk.Button(root, text="1728x1440", command=lambda: set_resolution(1728,1440)).pack(pady=2)

# RAM Slider
tk.Label(root, text="RAM Allocation (GB):").pack(pady=5)
ram_slider = tk.Scale(root, from_=2, to=12, orient=tk.HORIZONTAL)
ram_slider.set(8)
ram_slider.pack()
tk.Button(root, text="Apply RAM", command=set_ram).pack(pady=5)

# CPU Slider
tk.Label(root, text="CPU Cores:").pack(pady=5)
cpu_slider = tk.Scale(root, from_=1, to=10, orient=tk.HORIZONTAL)
cpu_slider.set(8)
cpu_slider.pack()
tk.Button(root, text="Apply CPU Cores", command=set_cpu).pack(pady=5)

# Clear Cache
tk.Button(root, text="Clear Shader/Cache", command=clear_cache, bg="orange").pack(pady=20)

root.mainloop()
