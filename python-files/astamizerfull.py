import sys
import subprocess
import importlib
import os

# ------------------ Auto-Install Missing Modules ------------------
def install_module(module_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])

for module in ["winshell", "pywin32"]:
    try:
        importlib.import_module(module)
    except ImportError:
        install_module(module)

# Now import after ensuring installed
import ctypes
import winshell
import shutil
import tempfile
import tkinter as tk
from tkinter import messagebox

# ------------------ Admin Auto-Request ------------------
if not ctypes.windll.shell32.IsUserAnAdmin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit()

# ------------------ Helper Functions ------------------
def delete_folder_contents(folder_path):
    total_deleted = 0
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    size = os.path.getsize(file_path)
                    os.unlink(file_path)
                    total_deleted += size
                elif os.path.isdir(file_path):
                    size = get_folder_size(file_path)
                    shutil.rmtree(file_path)
                    total_deleted += size
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")
    return total_deleted

def get_folder_size(folder):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size

# ------------------ Optimizations ------------------
def ultra_smooth_mode():
    try:
        os.system('reg add "HKCU\\Control Panel\\Mouse" /v MouseSensitivity /t REG_SZ /d 20 /f')
        os.system('reg add "HKCU\\Control Panel\\Mouse" /v MouseSpeed /t REG_SZ /d 0 /f')
        os.system('reg add "HKCU\\Control Panel\\Mouse" /v MouseThreshold1 /t REG_SZ /d 0 /f')
        os.system('reg add "HKCU\\Control Panel\\Mouse" /v MouseThreshold2 /t REG_SZ /d 0 /f')
        os.system('reg add "HKCU\\Control Panel\\Keyboard" /v KeyboardDelay /t REG_SZ /d 0 /f')
        os.system('reg add "HKCU\\Control Panel\\Keyboard" /v KeyboardSpeed /t REG_SZ /d 31 /f')
        messagebox.showinfo("Astamizer", "Ultra Smooth Mode Applied!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed: {e}")

def high_performance_plan():
    try:
        subprocess.call('powercfg -setactive SCHEME_MIN', shell=True)
        messagebox.showinfo("Astamizer", "High Performance Power Plan Activated!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed: {e}")

def high_cpu_priority():
    try:
        pid = int(subprocess.check_output(
            "powershell (Get-Process -Id (Get-Process | Where-Object {$_.MainWindowHandle -ne 0}).Id).Id",
            shell=True))
        os.system(f"wmic process where processid={pid} CALL setpriority 128")
        messagebox.showinfo("Astamizer", "Active Game Set to High CPU Priority")
    except:
        messagebox.showwarning("Astamizer", "No active window detected for priority.")

def disable_visual_effects():
    try:
        subprocess.call('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f', shell=True)
        messagebox.showinfo("Astamizer", "Visual Effects Disabled for Performance")
    except:
        messagebox.showerror("Astamizer", "Failed to disable visual effects")

def monitor_tweaks():
    try:
        subprocess.call('reg add "HKCU\\Software\\Microsoft\\GameBar" /v AllowAutoGameMode /t REG_DWORD /d 1 /f', shell=True)
        messagebox.showinfo("Astamizer",
                            "Game Mode Enabled!\nSet your monitor to max refresh rate & native resolution.\nDisable HDR if not needed.")
    except:
        messagebox.showerror("Astamizer", "Failed to apply monitor tweaks")

def clean_temp_cache():
    total = 0
    total += delete_folder_contents(r"C:\Windows\Temp")
    total += delete_folder_contents(tempfile.gettempdir())
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
    except:
        pass
    freed_mb = total / (1024*1024)
    messagebox.showinfo("Astamizer", f"Deleted approx. {freed_mb:.2f} MB of temporary files")

def full_optimization():
    ultra_smooth_mode()
    high_performance_plan()
    high_cpu_priority()
    disable_visual_effects()
    monitor_tweaks()
    clean_temp_cache()
    messagebox.showinfo("Astamizer", "All optimizations applied!")

# ------------------ GUI ------------------
root = tk.Tk()
root.title("Astamizer - Ultimate System Optimizer")
root.geometry("600x500")
root.configure(bg="#1E1E2F")
root.resizable(False, False)

tk.Label(root, text="Astamizer", font=("Arial", 20, "bold"), bg="#1E1E2F", fg="#00FFFF").pack(pady=15)
tk.Label(root, text="Ultimate One-Click System Optimizer", font=("Arial", 12), bg="#1E1E2F", fg="white").pack(pady=5)

# Buttons
btn_style = {"width":30, "height":2, "bg":"#282C34", "fg":"#00FFFF", "font":("Arial", 10, "bold")}
tk.Button(root, text="Ultra Smooth Mode (Mouse & Keyboard)", command=ultra_smooth_mode, **btn_style).pack(pady=8)
tk.Button(root, text="High Performance Power Plan", command=high_performance_plan, **btn_style).pack(pady=8)
tk.Button(root, text="Set Active Game to High CPU Priority", command=high_cpu_priority, **btn_style).pack(pady=8)
tk.Button(root, text="Disable Windows Visual Effects", command=disable_visual_effects, **btn_style).pack(pady=8)
tk.Button(root, text="Apply Monitor Tweaks & Game Mode", command=monitor_tweaks, **btn_style).pack(pady=8)
tk.Button(root, text="Clean Temp & Cache Files", command=clean_temp_cache, **btn_style).pack(pady=8)

# Full Optimization Button
full_btn_style = {"width":30, "height":2, "bg":"#00FFFF", "fg":"#1E1E2F", "font":("Arial", 10, "bold")}
tk.Button(root, text="Run Full Optimization (One-Click)", command=full_optimization, **full_btn_style).pack(pady=15)

root.mainloop()
