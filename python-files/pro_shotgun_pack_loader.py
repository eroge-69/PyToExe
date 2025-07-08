
import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.title("PRO SHOTGUN PACK Loader")
root.geometry("500x400")
root.configure(bg="#1a1a1a")

font_title = ("Arial", 18, "bold")
font_normal = ("Arial", 12)
text_color = "#ffffff"
accent_color = "#b84dff"

log_output = tk.Text(root, bg="#121212", fg=text_color, font=font_normal, height=10, width=60)
log_output.place(x=30, y=170)

def log(message):
    log_output.insert(tk.END, f"{message}\n")
    log_output.see(tk.END)

def install_pack():
    log("Installing PRO SHOTGUN PACK...")
    root.after(1000, lambda: log("Applying shotgun tweaks..."))
    root.after(2000, lambda: log("Syncing settings to Zenn mode..."))
    root.after(3000, lambda: log("Enabling low latency mode..."))
    root.after(4000, lambda: log("PRO PACK READY ✅"))
    root.after(5000, lambda: messagebox.showinfo("Done", "PRO SHOTGUN PACK successfully applied!"))

def apply_config():
    log("Applying custom config...")
    root.after(1000, lambda: log("Settings optimized for box fights & endgames."))
    root.after(2000, lambda: log("Precision mode: ENABLED"))

def launch_game():
    log("Launching Fortnite...")
    root.after(1500, lambda: log("Game not found (simulated). Please install Fortnite."))

tk.Label(root, text="PRO SHOTGUN PACK", font=font_title, fg=accent_color, bg="#1a1a1a").pack(pady=20)
tk.Label(root, text="Used by Zenn, Tickle, Roar, Sjay & more", font=font_normal, fg=text_color, bg="#1a1a1a").pack()

tk.Button(root, text="Install Pack", command=install_pack, font=font_normal, bg=accent_color, fg="white", width=20).place(x=160, y=100)
tk.Button(root, text="Apply Config", command=apply_config, font=font_normal, bg=accent_color, fg="white", width=20).place(x=160, y=130)
tk.Button(root, text="Launch Game", command=launch_game, font=font_normal, bg=accent_color, fg="white", width=20).place(x=160, y=160)

root.mainloop()
