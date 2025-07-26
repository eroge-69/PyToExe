
import os
import tkinter as tk
from tkinter import messagebox

def run_command(command):
    result = os.system(command)
    if result == 0:
        messagebox.showinfo("İşlem Başarılı", "İşlem tamamlandı.")
    else:
        messagebox.showerror("Hata", "Bir sorun oluştu.")

def ultimate_performance():
    run_command("powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61")

def ram_disk_clean():
    os.system("%windir%\\System32\\rundll32.exe advapi32.dll,ProcessIdleTasks")
    os.system("ipconfig /flushdns")
    os.system("del /s /f /q %temp%\\*.* >nul 2>&1")
    os.system("del /s /f /q C:\\Windows\\Temp\\*.* >nul 2>&1")
    messagebox.showinfo("Temizlik", "RAM ve geçici dosyalar temizlendi.")

def dns_boost():
    os.system("netsh interface ip set dns name=\"Wi-Fi\" static 1.1.1.1")
    os.system("netsh interface ip add dns name=\"Wi-Fi\" 1.0.0.1 index=2")
    os.system("ipconfig /flushdns")
    messagebox.showinfo("DNS", "Cloudflare DNS ayarlandı.")

def gpu_cpu_optimize():
    os.system("reg import gpu_cpu_optimize.reg")
    messagebox.showinfo("GPU/CPU", "GPU ve CPU optimize edildi. Yeniden başlatmanız önerilir.")

def game_mode(game):
    if game == "Zula":
        os.system("ipconfig /flushdns")
        os.system("taskkill /f /im discord.exe >nul 2>&1")
        os.system("taskkill /f /im chrome.exe >nul 2>&1")
    elif game == "Minecraft":
        os.system("wmic process where name='javaw.exe' CALL setpriority 128 >nul")
    elif game == "CS2":
        os.system("ipconfig /flushdns")
        os.system("taskkill /f /im steamwebhelper.exe >nul 2>&1")
    elif game == "LoL":
        os.system("ipconfig /flushdns")
        os.system("taskkill /f /im RiotClientServices.exe >nul 2>&1")
        os.system("taskkill /f /im LeagueClient.exe >nul 2>&1")
    messagebox.showinfo("Oyun Modu", f"{game} için optimize edildi.")

def all_in_one():
    ultimate_performance()
    ram_disk_clean()
    dns_boost()
    gpu_cpu_optimize()
    messagebox.showinfo("Tam Uygulama", "Tüm işlemler başarıyla tamamlandı.")

root = tk.Tk()
root.title("Bilgisayar Turbo Aracı")
root.geometry("400x600")
root.configure(bg="#1e1e1e")

btn_style = {"bg": "#2d2d2d", "fg": "#00ffcc", "font": ("Arial", 10, "bold"), "padx": 10, "pady": 8, "relief": "raised"}

tk.Label(root, text="Bilgisayar Turbo Aracı", font=("Arial", 14, "bold"), fg="#00ffcc", bg="#1e1e1e").pack(pady=10)

tk.Button(root, text="Ultimate Performance Aç", command=ultimate_performance, **btn_style).pack(pady=5)
tk.Button(root, text="RAM & Disk Temizle", command=ram_disk_clean, **btn_style).pack(pady=5)
tk.Button(root, text="DNS Hızlandır (1.1.1.1)", command=dns_boost, **btn_style).pack(pady=5)
tk.Button(root, text="GPU/CPU Optimize Et", command=gpu_cpu_optimize, **btn_style).pack(pady=5)

tk.Label(root, text="Oyun Modları", font=("Arial", 12, "bold"), fg="#00ffcc", bg="#1e1e1e").pack(pady=10)
tk.Button(root, text="Zula Optimize", command=lambda: game_mode("Zula"), **btn_style).pack(pady=3)
tk.Button(root, text="Minecraft Optimize", command=lambda: game_mode("Minecraft"), **btn_style).pack(pady=3)
tk.Button(root, text="CS2 Optimize", command=lambda: game_mode("CS2"), **btn_style).pack(pady=3)
tk.Button(root, text="LoL Optimize", command=lambda: game_mode("LoL"), **btn_style).pack(pady=3)

tk.Button(root, text="Tümünü Uygula", command=all_in_one, **btn_style).pack(pady=10)

root.mainloop()
