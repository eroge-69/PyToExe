import webbrowser
import os
import shutil
import subprocess
import ctypes
import psutil
import winreg
import threading
import tkinter as tk
from tkinter import scrolledtext

# === Your contact info ===
MAKER_NAME = "YUNG"
YOUTUBE_URL = "https://youtube.com/yourchannel"   # https://www.youtube.com/@yungjoking
DISCORD_URL = "https://discord.gg/yourdiscord"    # https://discord.gg/P6agfTbjqW
TELEGRAM_URL = "https://t.me/yourtelegram"        # https://t.me/CheekyAndShameless

def open_url(url):
    webbrowser.open_new(url)

# === Optimization functions ===

def log_print(text):
    gui_log.config(state='normal')
    gui_log.insert(tk.END, text + '\n')
    gui_log.see(tk.END)
    gui_log.config(state='disabled')

def clear_temp():
    temp_path = os.getenv('TEMP')
    try:
        for filename in os.listdir(temp_path):
            file_path = os.path.join(temp_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception:
                pass
        log_print("[✔] Temporary files cleared.")
    except Exception as e:
        log_print(f"[!] Failed to clear temp files: {e}")

def clear_recycle_bin():
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x0007)
        log_print("[✔] Recycle Bin emptied.")
    except Exception as e:
        log_print(f"[!] Failed to empty Recycle Bin: {e}")

def optimize_timer_resolution():
    class TimerResolution:
        def __init__(self):
            self.winmm = ctypes.WinDLL('winmm')
            self.current_resolution = 0
        def set_resolution(self, ms):
            res = self.winmm.timeBeginPeriod(ms)
            if res == 0:
                self.current_resolution = ms
                log_print(f"[✔] Timer resolution set to {ms} ms.")
            else:
                log_print("[✘] Failed to set timer resolution.")
    timer = TimerResolution()
    timer.set_resolution(1)

def apply_network_tweaks():
    log_print("[~] Applying network tweaks for low ping...")
    try:
        subprocess.run('netsh interface tcp set global congestionprovider=ctcp', shell=True, stdout=subprocess.DEVNULL)
        subprocess.run('netsh interface tcp set global autotuninglevel=highlyrestricted', shell=True, stdout=subprocess.DEVNULL)
        subprocess.run('netsh interface tcp set global rss=enabled', shell=True, stdout=subprocess.DEVNULL)
        log_print("[✔] Network tweaks applied.")
    except Exception as e:
        log_print(f"[!] Failed to apply network tweaks: {e}")

def disable_defender_real_time_protection():
    log_print("[~] Disabling Windows Defender Real-Time Protection...")
    try:
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection")
        winreg.SetValueEx(key, "DisableRealtimeMonitoring", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        log_print("[✔] Defender Real-Time Protection disabled (restart required).")
    except Exception as e:
        log_print(f"[!] Failed to disable Defender real-time protection: {e}")

def disable_visual_effects():
    log_print("[~] Disabling unnecessary visual effects for performance...")
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)  # Adjust for best performance
        winreg.CloseKey(key)
        log_print("[✔] Visual effects adjusted.")
    except Exception as e:
        log_print(f"[!] Failed to disable visual effects: {e}")

def disable_prefetch_superfetch():
    log_print("[~] Disabling Prefetch and Superfetch...")
    try:
        key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "EnablePrefetcher", 0, winreg.REG_DWORD, 0)
        winreg.SetValueEx(key, "EnableSuperfetch", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        log_print("[✔] Prefetch and Superfetch disabled.")
    except Exception as e:
        log_print(f"[!] Failed to disable Prefetch/Superfetch: {e}")

def set_gpu_priority_high():
    log_print("[~] Setting GPU hardware scheduling to high priority...")
    try:
        key_path = r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        winreg.SetValueEx(key, "HwSchMode", 0, winreg.REG_DWORD, 2)  # High priority mode
        winreg.CloseKey(key)
        log_print("[✔] GPU priority set high (restart required).")
    except Exception as e:
        log_print(f"[!] Failed to set GPU priority: {e}")

def set_power_plan_ultimate_performance():
    log_print("[~] Setting Ultimate Performance power plan...")
    try:
        subprocess.run("powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61", shell=True, stdout=subprocess.DEVNULL)
        subprocess.run("powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61", shell=True)
        log_print("[✔] Ultimate Performance power plan set.")
    except Exception as e:
        log_print(f"[!] Failed to set power plan: {e}")

def disable_service(service_name):
    try:
        subprocess.run(f"sc stop {service_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(f"sc config {service_name} start= disabled", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log_print(f"[✔] Service {service_name} stopped and disabled.")
    except Exception as e:
        log_print(f"[!] Could not disable service {service_name}: {e}")

services_to_disable = [
    "SysMain",
    "WSearch",
    "DiagTrack",
    "WMPNetworkSvc",
    "XblGameSave",
    "XboxNetApiSvc",
    "MapsBroker",
    "CDPUserSvc",
]

scheduled_tasks_to_disable = [
    r"\Microsoft\Windows\Application Experience\ProgramDataUpdater",
    r"\Microsoft\Windows\Autochk\Proxy",
    r"\Microsoft\Windows\Customer Experience Improvement Program\Consolidator",
    r"\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip",
    r"\Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticDataCollector",
    r"\Microsoft\Windows\Maintenance\WinSAT",
]

def disable_scheduled_tasks(tasks):
    for task in tasks:
        try:
            subprocess.run(f'schtasks /Change /TN "{task}" /Disable', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            log_print(f"[✔] Disabled scheduled task: {task}")
        except Exception as e:
            log_print(f"[!] Could not disable scheduled task {task}: {e}")

processes_to_kill = [
    "OneDrive.exe",
    "Spotify.exe",
    "Cortana.exe",
    "MicrosoftEdge.exe",
    "SearchUI.exe",
    "RuntimeBroker.exe",
    "LockApp.exe",
    "ShellExperienceHost.exe",
]

def kill_unnecessary_processes():
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] in processes_to_kill:
                proc.kill()
                log_print(f"[✔] Killed process: {proc.info['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def reduce_cpu_overhead():
    log_print("[~] Reducing unnecessary CPU processes and services...")
    for svc in services_to_disable:
        disable_service(svc)
    disable_scheduled_tasks(scheduled_tasks_to_disable)
    kill_unnecessary_processes()
    log_print("[✔] CPU overhead reduction complete.")

def disable_xbox_features():
    log_print("[~] Disabling Xbox Game Bar and Game DVR...")
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR")
        winreg.SetValueEx(key, "AppCaptureEnabled", 0, winreg.REG_DWORD, 0)
        winreg.SetValueEx(key, "GameDVR_Enabled", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)

        disable_service("XblGameSave")
        disable_service("XboxNetApiSvc")

        log_print("[✔] Xbox Game Bar and Game DVR disabled.")
    except Exception as e:
        log_print(f"[!] Failed to disable Xbox features: {e}")

def disable_fullscreen_optimizations():
    log_print("[~] Disabling fullscreen optimizations system-wide...")
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore")
        winreg.SetValueEx(key, "GameDVR_FSEBehaviorMode", 0, winreg.REG_DWORD, 2)
        winreg.CloseKey(key)

        key2 = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR")
        winreg.SetValueEx(key2, "AppCaptureEnabled", 0, winreg.REG_DWORD, 0)
        winreg.SetValueEx(key2, "GameDVR_Enabled", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key2)
        log_print("[✔] Fullscreen optimizations disabled.")
    except Exception as e:
        log_print(f"[!] Failed to disable fullscreen optimizations: {e}")

def disable_mouse_acceleration():
    log_print("[~] Disabling mouse acceleration...")
    try:
        SPI_SETMOUSE = 0x0071
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETMOUSE, 0, (0, 0, 0, 0), 0)
        log_print("[✔] Mouse acceleration disabled.")
    except Exception as e:
        log_print(f"[!] Failed to disable mouse acceleration: {e}")

# === Main function to apply all tweaks ===

def apply_all_tweaks():
    log_print("=== Starting Fortnite & Valorant Optimizations ===")
    clear_temp()
    clear_recycle_bin()
    optimize_timer_resolution()
    apply_network_tweaks()
    disable_defender_real_time_protection()
    disable_visual_effects()
    disable_prefetch_superfetch()
    set_gpu_priority_high()
    set_power_plan_ultimate_performance()
    disable_xbox_features()
    disable_fullscreen_optimizations()
    disable_mouse_acceleration()
    reduce_cpu_overhead()
    log_print("\n[!] Done applying all tweaks. Please restart your PC for changes to take effect.")

# === GUI setup ===

def run_optimization_thread():
    thread = threading.Thread(target=apply_all_tweaks)
    thread.start()

root = tk.Tk()
root.title("Fortnite & Valorant Windows Optimizer")
root.geometry("700x530")
root.resizable(False, False)
root.configure(bg="#121212")  # Black background

frame = tk.Frame(root, bg="#121212")
frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=False)

# Info section at top
info_frame = tk.Frame(frame, bg="#121212")
info_frame.pack(fill=tk.X, pady=(0,10))

maker_label = tk.Label(info_frame, text=f"Maker: {MAKER_NAME}", font=("Arial", 12, "bold"), fg="#BB86FC", bg="#121212")
maker_label.pack(side=tk.LEFT)

def make_link(label_text, url):
    link = tk.Label(info_frame, text=label_text, fg="#BB86FC", cursor="hand2", font=("Arial", 12, "underline"), bg="#121212")
    link.pack(side=tk.LEFT, padx=10)
    link.bind("<Button-1>", lambda e: open_url(url))
    return link

yt_link = make_link("YouTube", YOUTUBE_URL)
discord_link = make_link("Discord", DISCORD_URL)
telegram_link = make_link("Telegram", TELEGRAM_URL)

# Main frame for button and log
main_frame = tk.Frame(root, bg="#121212")
main_frame.pack(padx=10, pady=(0,10), fill=tk.BOTH, expand=True)

btn_run = tk.Button(main_frame, text="Apply All Optimizations", command=run_optimization_thread,
                    bg="#BB86FC", fg="#121212", font=("Arial", 14, "bold"), activebackground="#9a63d9", activeforeground="#121212",
                    relief=tk.FLAT)
btn_run.pack(fill=tk.X, pady=(0,10))

gui_log = scrolledtext.ScrolledText(main_frame, state='disabled', font=("Consolas", 10), bg="#1E1E1E", fg="#E0E0E0", insertbackground="white")
gui_log.pack(fill=tk.BOTH, expand=True)

root.mainloop()
