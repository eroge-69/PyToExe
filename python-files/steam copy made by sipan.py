import tkinter as tk
from tkinter import messagebox
import subprocess
import os

# Replace with your game list and paths
games = {
    "Minecraft": r"C:\Games\Minecraft\MinecraftLauncher.exe",
    "Doom Eternal": r"C:\Games\DoomEternal\DoomEternal.exe",
    "Celeste": r"C:\Games\Celeste\Celeste.exe"
}

def launch_game(game_name):
    path = games[game_name]
    if os.path.exists(path):
        try:
            subprocess.Popen(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {game_name}:\n{e}")
    else:
        messagebox.showerror("Not Found", f"Game not found at path:\n{path}")

# GUI Setup
root = tk.Tk()
root.title("My Game Launcher")
root.geometry("400x300")
root.config(bg="#1b2838")

tk.Label(root, text="Game Library", font=("Arial", 16), fg="white", bg="#1b2838").pack(pady=10)

for game in games:
    tk.Button(
        root,
        text=game,
        command=lambda g=game: launch_game(g),
        width=25,
        height=2,
        bg="#66c0f4",
        fg="black",
        font=("Arial", 12)
    ).pack(pady=5)

root.mainloop()
