import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import random
from datetime import datetime, date

SAVE_FILE = "gacha_save.json"

CHARACTER_POOLS = {
    "Common": ["Gon (Casual)", "Killua (Casual)", "Leorio", "Kurapika", "Hanzo", "Ponzu"],
    "Rare": ["Gon (Hunter)", "Killua (Yo-Yo)", "Hisoka", "Bisky", "Shalnark"],
    "Epic": ["Chrollo", "Illumi", "Zeno", "Feitan", "Uvogin"],
    "Legendary": ["Meruem", "Netero", "Adult Gon", "King Zoldyck"]
}

RARITY_CHANCES = {"Common": 60, "Rare": 25, "Epic": 10, "Legendary": 5}
SELL_VALUES = {"Common": 5, "Rare": 20, "Epic": 50, "Legendary": 150}

ACHIEVEMENTS = [
    {"name": "First Summon", "condition": lambda d: len(d["characters"]) >= 1, "reward": 50},
    {"name": "Collector", "condition": lambda d: len(d["characters"]) >= 10, "reward": 200},
    {"name": "Epic Collector", "condition": lambda d: sum(1 for c in d["characters"] if c["rarity"] == "Epic") >= 3, "reward": 300},
    {"name": "Legendary Hunter", "condition": lambda d: any(c["rarity"] == "Legendary" for c in d["characters"]), "reward": 500},
]

def load_data():
    defaults = {
        "gold": 200,
        "characters": [],
        "last_daily": "",
        "achievements": []
    }
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # If file is empty or corrupted, use defaults
            data = defaults.copy()
        # Ensure all keys exist (backwards compatibility)
        for key, value in defaults.items():
            if key not in data:
                data[key] = value
        return data
    return defaults
def save_data(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HxH Gacha")
        self.geometry("500x400")

        self.data = load_data()
        self.check_daily_reward()

        # Generate hourly banner ONCE
        self.banner = self.generate_hourly_banner()

        self.frames = {}
        for F in (MainMenu, SummonMenu, SettingsMenu, AboutMenu):
            frame = F(self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainMenu)
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.bind_all("<Control-Shift-Alt-R>", self.refresh_banner)
    def show_frame(self, menu_class):
        self.frames[menu_class].update_display() if hasattr(self.frames[menu_class], "update_display") else None
        self.frames[menu_class].tkraise()

    def on_exit(self):
        save_data(self.data)
        self.destroy()

    def check_daily_reward(self):
        today_str = str(date.today())
        if self.data["last_daily"] != today_str:
            self.data["gold"] += 100
            self.data["last_daily"] = today_str
            messagebox.showinfo("Daily Reward", "You got 100 gold for logging in today!")
            save_data(self.data)
    def refresh_banner(self, event=None):
        if SummonMenu in self.frames:
            self.frames[SummonMenu].update_display(force_refresh=True)
            messagebox.showinfo("Banner Refreshed", "The banner has been refreshed!")


    def check_achievements(self):
        unlocked = []
        for ach in ACHIEVEMENTS:
            if ach["name"] not in self.data["achievements"] and ach["condition"](self.data):
                self.data["achievements"].append(ach["name"])
                self.data["gold"] += ach["reward"]
                unlocked.append(f"{ach['name']} (+{ach['reward']} gold)")
        if unlocked:
            messagebox.showinfo("Achievements Unlocked", "\n".join(unlocked))

    def generate_hourly_banner(self):
        # Use UTC hour to make banner consistent for everyone
        hour_seed = int(datetime.utcnow().strftime("%Y%m%d%H"))
        rng = random.Random(hour_seed)
        return {
            "Common": rng.sample(CHARACTER_POOLS["Common"], 4),
            "Rare": rng.sample(CHARACTER_POOLS["Rare"], 3),
            "Epic": rng.sample(CHARACTER_POOLS["Epic"], 2),
            "Legendary": rng.sample(CHARACTER_POOLS["Legendary"], 1)
        }

class MainMenu(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#2c2f33")
        tk.Label(self, text="Main Menu", font=("Arial", 20), bg="#2c2f33", fg="white").pack(pady=20)
        ttk.Button(self, text="Summon!", command=lambda: master.show_frame(SummonMenu)).pack(pady=10)
        ttk.Button(self, text="Settings", command=lambda: master.show_frame(SettingsMenu)).pack(pady=10)
        ttk.Button(self, text="About", command=lambda: master.show_frame(AboutMenu)).pack(pady=10)
        ttk.Button(self, text="Exit", command=master.on_exit).pack(pady=10)

class SummonMenu(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#1e1e1e")
        self.master = master
        tk.Label(self, text="Summon Menu", font=("Arial", 20), bg="#1e1e1e", fg="white").pack(pady=10)
        self.banner_label = tk.Label(self, font=("Arial", 14), bg="#1e1e1e", fg="white")
        self.banner_label.pack(pady=5)
        self.gold_label = tk.Label(self, font=("Arial", 14), bg="#1e1e1e", fg="white")
        self.gold_label.pack(pady=5)

        ttk.Button(self, text="Summon (50 Gold)", command=self.summon).pack(pady=5)
        ttk.Button(self, text="Sell Character", command=self.sell_character).pack(pady=5)
        ttk.Button(self, text="View Characters", command=self.show_characters).pack(pady=5)
        ttk.Button(self, text="Back", command=lambda: master.show_frame(MainMenu)).pack(pady=20)
        self.update_display()

    def update_display(self):
        banner_text = "Current Banner:\n"
        for rarity, chars in self.master.banner.items():
            banner_text += f"{rarity}: {', '.join(chars)}\n"
        self.banner_label.config(text=banner_text.strip())
        self.gold_label.config(text=f"Gold: {self.master.data['gold']}")

    def summon(self):
        if self.master.data["gold"] < 50:
            messagebox.showerror("Not enough gold", "You need at least 50 gold to summon!")
            return
        self.master.data["gold"] -= 50
        rarity = self.pick_rarity()
        pool = self.master.banner[rarity]
        character = random.choice(pool)
        self.master.data["characters"].append({"name": character, "rarity": rarity})
        self.update_display()
        messagebox.showinfo("Summon Result", f"You got {character} ({rarity})!")
        self.master.check_achievements()

    def pick_rarity(self):
        roll = random.randint(1, 100)
        cumulative = 0
        for rarity, chance in RARITY_CHANCES.items():
            cumulative += chance
            if roll <= cumulative:
                return rarity
        return "Common"

    def show_characters(self):
        if not self.master.data["characters"]:
            messagebox.showinfo("Characters", "You haven't summoned anyone yet!")
            return
        chars = "\n".join([f"{c['name']} ({c['rarity']})" for c in self.master.data["characters"]])
        messagebox.showinfo("Your Characters", chars)

    def sell_character(self):
        if not self.master.data["characters"]:
            messagebox.showinfo("Sell", "You have no characters to sell.")
            return
        choices = [f"{c['name']} ({c['rarity']})" for c in self.master.data["characters"]]
        choice = simpledialog.askstring("Sell Character", f"Type the exact name to sell:\n{', '.join(choices)}")
        if choice:
            for i, c in enumerate(self.master.data["characters"]):
                if choice.lower() == f"{c['name']} ({c['rarity']})".lower():
                    self.master.data["gold"] += SELL_VALUES[c["rarity"]]
                    del self.master.data["characters"][i]
                    messagebox.showinfo("Sold", f"Sold {c['name']} for {SELL_VALUES[c['rarity']]} gold.")
                    self.update_display()
                    save_data(self.master.data)
                    return
            messagebox.showerror("Error", "Character not found.")

class SettingsMenu(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#23272a")
        tk.Label(self, text="Settings", font=("Arial", 20), bg="#23272a", fg="white").pack(pady=20)
        ttk.Button(self, text="Back", command=lambda: master.show_frame(MainMenu)).pack(pady=20)

class AboutMenu(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#1e2124")
        tk.Label(self, text="About", font=("Arial", 20), bg="#1e2124", fg="white").pack(pady=20)
        tk.Label(self, text="HxH Gacha Game with daily rewards, selling, and achievements.",
                 bg="#1e2124", fg="white", justify="center").pack(pady=10)
        ttk.Button(self, text="Back", command=lambda: master.show_frame(MainMenu)).pack(pady=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()
