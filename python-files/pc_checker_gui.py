import tkinter as tk
from tkinter import messagebox, ttk
import psutil
import platform
import GPUtil
import speedtest
import threading

def get_specs():
    cpu = platform.processor()
    ram = psutil.virtual_memory().total / (1024 ** 3)
    disk = psutil.disk_usage('/')
    gpus = GPUtil.getGPUs()
    gpu_name = gpus[0].name if gpus else "Not Detected"
    vram = gpus[0].memoryTotal if gpus else 0
    return cpu, ram, disk.total / (1024 ** 3), gpu_name, vram

def get_speed():
    try:
        st = speedtest.Speedtest()
        download = st.download() / 1_000_000
        upload = st.upload() / 1_000_000
        return download, upload
    except:
        return None, None

def estimate_games(ram, vram, cpu):
    score = 0
    if ram >= 4: score += 1
    if ram >= 8: score += 1
    if vram >= 1: score += 1
    if vram >= 2: score += 1
    if "i5" in cpu.lower() or "ryzen 5" in cpu.lower(): score += 1

    games = {
        "Minecraft": 1,
        "GTA V": 2,
        "Fortnite": 3,
        "Valorant": 2,
        "Call of Duty Warzone": 4,
        "PUBG": 3,
        "Red Dead Redemption 2": 5
    }

    results = []
    for game, req in games.items():
        if score >= req:
            fps = 30 + (score - req) * 10
            results.append(f"✅ {game} — {fps}+ FPS")
        else:
            results.append(f"❌ {game} — Not Recommended")
    return results

def run_checker():
    status_label.config(text="🔍 Checking your PC...")
    cpu, ram, disk, gpu, vram = get_specs()
    download, upload = get_speed()
    games = estimate_games(ram, vram, cpu)

    info = f"🇵🇰 PAKISTAN GAMER REPORT\n========================\n"
    info += f"🧠 CPU: {cpu}\n"
    info += f"💾 RAM: {ram:.2f} GB\n"
    info += f"📀 Disk: {disk:.2f} GB\n"
    info += f"🎮 GPU: {gpu} ({vram} MB VRAM)\n"
    info += f"⬇ Download: {download:.2f} Mbps\n⬆ Upload: {upload:.2f} Mbps\n\n"
    info += "🎮 Game Compatibility:\n" + "\n".join(games)
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, info)
    status_label.config(text="✅ Done. Report Ready!")

def threaded_check():
    threading.Thread(target=run_checker).start()

def compare_popup():
    messagebox.showinfo("Compare", "PC comparison feature coming soon!")

def game_check_popup():
    game = game_entry.get()
    if game.lower() in ["valorant", "gta", "fortnite"]:
        messagebox.showinfo("Game Check", f"✅ Your PC can likely run {game.title()}!")
    else:
        messagebox.showinfo("Game Check", f"❌ Unknown game or not recommended.")

# GUI Setup
app = tk.Tk()
app.title("🇵🇰 Pakistan PC Checker - Hammad Edition")
app.geometry("600x600")
app.config(bg="black")

status_label = tk.Label(app, text="Ready to check your PC.", bg="black", fg="white", font=("Arial", 12))
status_label.pack(pady=10)

check_button = tk.Button(app, text="🧠 Check PC Strength", font=("Arial", 14), command=threaded_check)
check_button.pack(pady=10)

compare_button = tk.Button(app, text="⚔️ Compare With Friend", font=("Arial", 12), command=compare_popup)
compare_button.pack(pady=5)

game_entry = tk.Entry(app, font=("Arial", 12))
game_entry.pack(pady=5)

game_button = tk.Button(app, text="🎮 Can I Run This Game?", font=("Arial", 12), command=game_check_popup)
game_button.pack(pady=5)

result_text = tk.Text(app, height=20, width=70, font=("Courier", 10))
result_text.pack(pady=10)

app.mainloop()
