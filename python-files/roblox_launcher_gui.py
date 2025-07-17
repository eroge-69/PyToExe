import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import os
import subprocess

LOZINKA = "0013"

IGRE = {'Roblox Početna': 'https://www.roblox.com', 'Grow a Garden': 'https://www.roblox.com/games/2759512150/Grow-a-Garden', 'Blox Fruits': 'https://www.roblox.com/games/2753915549/Blox-Fruits', 'Work at a Pizza Place': 'https://www.roblox.com/games/192800/Work-at-a-Pizza-Place'}

class RobloxLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Portable Roblox Launcher")
        self.geometry("400x250")
        self.resizable(False, False)
        self.configure(bg="#1e1e1e")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Roblox Launcher", font=("Segoe UI", 16, "bold"), fg="lime", bg="#1e1e1e").pack(pady=10)
        self.password_entry = tk.Entry(self, show="*", width=25, font=("Segoe UI", 11))
        self.password_entry.pack()
        self.password_entry.focus()

        self.selected_game = tk.StringVar(value="Odaberi igru")
        self.dropdown = ttk.Combobox(self, textvariable=self.selected_game, values=list(IGRE.keys()), state="readonly", width=35)
        self.dropdown.pack(pady=15)

        tk.Button(self, text="Pokreni", command=self.launch_game, width=20, bg="lime", fg="black", font=("Segoe UI", 11, "bold")).pack()

    def launch_game(self):
        entered_password = self.password_entry.get()
        if entered_password != LOZINKA:
            messagebox.showerror("Greška", "Pogrešna lozinka.")
            return

        game = self.selected_game.get()
        if game not in IGRE:
            messagebox.showwarning("Upozorenje", "Odaberi igru iz izbornika.")
            return

        url = IGRE[game]
        webbrowser.open(url)

        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            versions_dir = os.path.join(current_dir, "Versions")
            versions = sorted([d for d in os.listdir(versions_dir) if d.startswith("version-")], reverse=True)
            if versions:
                roblox_path = os.path.join(versions_dir, versions[0], "RobloxPlayerBeta.exe")
                subprocess.Popen(roblox_path)
        except Exception as e:
            print("Nije moguće pokrenuti Roblox klijent:", e)

if __name__ == "__main__":
    app = RobloxLauncher()
    app.mainloop()
