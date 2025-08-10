import os
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk, font as tkfont
from PIL import Image, ImageTk
import threading

# -----------------------
# Restore Point
# -----------------------
def create_restore_point():
    try:
        messagebox.showinfo("Restore Point", "Creating restore point. Please wait...")
        subprocess.run([
            "powershell", 
            "-Command", 
            "Checkpoint-Computer -Description 'Fortnite Tweaks Backup' -RestorePointType 'MODIFY_SETTINGS'"
        ], shell=True)
        messagebox.showinfo("Restore Point", "Restore point created successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create restore point.\n{e}")

# -----------------------
# Tweaks
# -----------------------
def tweak_network_latency():
    os.system('powershell "Set-NetTCPSetting -SettingName InternetCustom -AutoTuningLevelLocal Normal"')
    messagebox.showinfo("Network Tweak", "Network latency optimization applied.")

def disable_fullscreen_opt():
    os.system('reg add "HKCU\\System\\GameConfigStore" /v "GameDVR_FSEBehaviorMode" /t REG_DWORD /d 2 /f')
    messagebox.showinfo("Fullscreen Optimization", "Fullscreen optimizations disabled.")

def enable_gpu_scheduling():
    os.system('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" /v "HwSchMode" /t REG_DWORD /d 2 /f')
    messagebox.showinfo("GPU Scheduling", "Hardware-accelerated GPU scheduling enabled.")

def lower_input_delay():
    os.system('reg add "HKCU\\Control Panel\\Mouse" /v MouseSensitivity /t REG_SZ /d 6 /f')
    messagebox.showinfo("Input Delay", "Mouse settings optimized for low delay.")

def high_performance_mode():
    os.system('powercfg -setactive SCHEME_MIN')
    messagebox.showinfo("Performance Mode", "High performance power plan activated.")

def disable_xbox_dvr():
    os.system('reg add "HKCU\\System\\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f')
    os.system('reg add "HKLM\\SOFTWARE\\Microsoft\\PolicyManager\\default\\ApplicationManagement\\AllowGameDVR" /v value /t REG_DWORD /d 0 /f')
    messagebox.showinfo("Xbox DVR", "Xbox DVR disabled.")

def clear_temp_files():
    os.system('del /q/f/s %TEMP%\\*')
    messagebox.showinfo("Temp Files", "Temporary files cleared.")

def tweak_tcp_ack():
    os.system('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v TcpAckFrequency /t REG_DWORD /d 1 /f')
    messagebox.showinfo("TCP ACK", "TCP Ack frequency tweak applied.")

def disable_background_apps():
    os.system('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications" /v GlobalUserDisabled /t REG_DWORD /d 1 /f')
    messagebox.showinfo("Background Apps", "Background apps disabled.")

def set_game_mode():
    os.system('reg add "HKCU\\Software\\Microsoft\\GameBar" /v AllowAutoGameMode /t REG_DWORD /d 1 /f')
    messagebox.showinfo("Game Mode", "Windows Game Mode enabled.")

# -----------------------
# Apply All Tweaks
# -----------------------
def apply_all_tweaks():
    threading.Thread(target=create_restore_point).start()
    tweak_network_latency()
    disable_fullscreen_opt()
    enable_gpu_scheduling()
    lower_input_delay()
    high_performance_mode()
    disable_xbox_dvr()
    clear_temp_files()
    tweak_tcp_ack()
    disable_background_apps()
    set_game_mode()
    messagebox.showinfo("All Tweaks", "All tweaks applied successfully!")

# -----------------------
# UI Setup
# -----------------------
root = tk.Tk()
root.title("🎯 Fortnite Tweaking Panel")
root.geometry("720x750")
root.config(bg="#121212")

# Load Cherry Blossom Image
try:
    bg_img = Image.open("sakura_bg.png")
    bg_img = bg_img.resize((720, 200), Image.ANTIALIAS)
    sakura_img = ImageTk.PhotoImage(bg_img)
    sakura_label = tk.Label(root, image=sakura_img, bg="#121212")
    sakura_label.place(x=0, y=0, relwidth=1)
except:
    pass  # if no image, skip

# Load Fortnite Font
try:
    fortnite_font = tkfont.Font(file="BurbankBigCondensedBlack.ttf", size=36)
except:
    fortnite_font = tkfont.Font(family="Impact", size=36, weight="bold")

# Title Text
title = tk.Label(root, text="Fortnite Tweaking Panel", font=fortnite_font, fg="#ffffff", bg="#121212")
title.place(x=20, y=70)

# Subtitle
subtitle = tk.Label(root, text="Boost FPS • Reduce Input Delay • Optimize Network", font=("Segoe UI", 12), fg="#aaaaaa", bg="#121212")
subtitle.place(x=20, y=120)

# Main Frame
frame = tk.Frame(root, bg="#1e1e1e", bd=2, relief="ridge")
frame.pack(pady=(220, 20), padx=20, fill="both", expand=True)

# Button Style
style = ttk.Style()
style.configure("TButton",
                font=("Segoe UI", 12, "bold"),
                padding=8)
style.map("TButton",
          background=[("active", "#ff66b2")],
          foreground=[("active", "#000000")])

# Buttons list
buttons = [
    ("Create Restore Point", create_restore_point),
    ("Optimize Network Latency", tweak_network_latency),
    ("Disable Fullscreen Optimizations", disable_fullscreen_opt),
    ("Enable GPU Scheduling", enable_gpu_scheduling),
    ("Lower Input Delay", lower_input_delay),
    ("High Performance Mode", high_performance_mode),
    ("Disable Xbox DVR", disable_xbox_dvr),
    ("Clear Temp Files", clear_temp_files),
    ("TCP Ack Optimization", tweak_tcp_ack),
    ("Disable Background Apps", disable_background_apps),
    ("Enable Game Mode", set_game_mode),
    ("🔥 Apply All Tweaks", apply_all_tweaks)
]

# Create buttons
for text, cmd in buttons:
    btn = ttk.Button(frame, text=text, command=cmd)
    btn.pack(pady=6, padx=20, fill="x")

# Footer
footer = tk.Label(root, text="⚡ Tweaks Applied at Your Own Risk • Made for Fortnite Lovers", font=("Segoe UI", 9), fg="#666666", bg="#121212")
footer.pack(side="bottom", pady=10)

root.mainloop()

