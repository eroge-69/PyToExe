import tkinter as tk
from tkinter import ttk
import random

# --- JUTSU LIST WITH CLAN AND DOJUTSU FIELDS ---
    #{"name": "", "type": "", "power": , "clan": "", "dojutsu": },
JUTSU_LIST = [
    {"name": "adamantine chain bind", "type": "control", "power": 5, "clan": "Uzumaki", "dojutsu": False},
    {"name": "Byakugou no Jutsu", "type": "healing", "power": 5, "clan": "Haruno", "dojutsu": False},
    {"name": "Kage Bunshin no Jutsu", "type": "offensive", "power": 3, "clan": "Leaf", "dojutsu": False},
    {"name": "Amaterasu", "type": "offensive", "power": 7, "clan": "Uchiha", "dojutsu": True},
    {"name": "Chidori", "type": "offensive", "power": 6, "clan": "Uchiha", "dojutsu": False},
    {"name": "Fire Style: Fireball Jutsu", "type": "offensive", "power": 4, "clan": "All", "dojutsu": False},
    {"name": "Healing Jutsu", "type": "healing", "power": 4, "clan": "All", "dojutsu": False},
    {"name": "Shadow Possession Jutsu", "type": "control", "power": 3, "clan": "Nara", "dojutsu": False},
    {"name": "Water Style: Water Dragon", "type": "offensive", "power": 5, "clan": "All", "dojutsu": False},
    {"name": "Wind Style: Vacuum Sphere", "type": "offensive", "power": 4, "clan": "All", "dojustu": False},
    {"name": "Insect Swarm", "type": "offensive", "power": 6, "clan": "Aburame", "dojutsu": False},
    {"name": "Kitty Cat Claw", "type": "offensive", "power": 4, "clan": "Izuno", "dojutsu": True},
    {"name": "Fang Over Fang", "type": "offensive", "power": 4, "clan": "Inuzuka", "dojutsu": False},
    {"name": "Eight Inner Gates", "type": "offensive", "power": 5, "clan": "Lee", "dojutsu": True },

]

# --- NAME COMPONENTS ---
FIRST_NAMES = ["Naruto", "Sakura", "Sasuke", "Kakashi", "Shikamaru", "Ino", "Kotetsu", "Izumo", "Genma", "Hiruzen"]
LAST_NAMES = ["Uzumaki", "Haruno", "Uchiha", "Hatake", "Nara", "Yamanaka", "Inuzuka", "Izuno", "Aburame", "Lee", "Saruttobi", "Senju"]

def generate_name():
    first = random.choice(FIRST_NAMES).capitalize()
    last = random.choice(LAST_NAMES).capitalize()
    full = f"{first} {last}"
    return full[0].upper() + full[1:].lower(), last  # name, clan

# --- SHINOBI CLASS ---
class Shinobi:
    def __init__(self, village):
        self.name, self.clan = generate_name()
        self.village = village
        # Assign jutsus only allowed by clan
        self.jutsu = [dict(j, base_power=j["power"]) for j in JUTSU_LIST if j["clan"] in (self.clan, "All")]
        if len(self.jutsu) > 3:
            self.jutsu = random.sample(self.jutsu, k=3)
        self.alive = True
        self.health = 10
        self.level = 1
        self.kills = 0
        self.dojutsu_active = False

    def activate_dojutsu(self):
        for j in self.jutsu:
            if j.get("dojutsu"):  # <-- safer
                print(f"{self.name} activated dojutsu: {j['name']}")

    def deactivate_dojutsu(self):
          for j in self.jutsu:
                if j.get("dojutsu"):  # safer than j["dojutsu"]
                    print(f"{self.name} deactivated dojutsu: {j['name']}")

    def __str__(self):
        return f"{self.name} ({self.clan}, {self.village})"

# --- KAGE GAME CLASS ---
class KageGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Kage Command — Naruto-Style RTS (Tkinter)")
        self.turn = 1
        self.player_village = "Leaf"
        self.gold = 100
        self.combat_logs = []

        # Player shinobi
        self.shinobi = [Shinobi(self.player_village) for _ in range(3)]

        # Allies and AI villages
        self.allies = {}
        self.nations = ["Sand", "Mist", "Stone", "Cloud"]
        self.ai = {n: {"gold": 80, "shinobi": [Shinobi(n) for _ in range(3)],
                       "personality": random.choice(["aggressive", "balanced", "defensive"])} for n in self.nations}

        # GUI Frames
        self.menu_frame = tk.Frame(root, bg="black")
        self.action_frame = tk.Frame(root, bg="darkblue")
        self.map_frame = tk.Frame(root, bg="saddlebrown")
        self.shinobi_frame = tk.Frame(root, bg="darkblue")
        self.log_frame = tk.Frame(root, bg="gray20")

        self.show_menu()

    # --- CLEAR FRAME ---
    def clear_frame(self):
        for frame in [self.menu_frame, self.action_frame, self.map_frame, self.shinobi_frame, self.log_frame]:
            for widget in frame.winfo_children():
                widget.destroy()
            frame.pack_forget()

    # --- MENU ---
    def show_menu(self):
        self.clear_frame()
        tk.Label(self.menu_frame, text=f"Turn {self.turn}", fg="white", bg="black", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.menu_frame, text=f"Gold: {self.gold}", fg="white", bg="black").pack()
        alive = [s for s in self.shinobi if s.alive]
        tk.Label(self.menu_frame, text=f"Shinobi: {len(alive)}", fg="white", bg="black").pack(pady=5)
        tk.Label(self.menu_frame, text="Allies: " + ", ".join(self.allies.keys()) if self.allies else "Allies: None", fg="white", bg="black").pack(pady=5)

        tk.Button(self.menu_frame, text="Recruit Shinobi", command=self.recruit_shinobi, width=20).pack(pady=5)
        tk.Button(self.menu_frame, text="Form Alliance", command=self.form_alliance_menu, width=20).pack(pady=5)
        tk.Button(self.menu_frame, text="View Map", command=self.show_map, width=20).pack(pady=5)
        tk.Button(self.menu_frame, text="View Shinobi", command=self.show_shinobi, width=20).pack(pady=5)
        tk.Button(self.menu_frame, text="War!", command=self.start_war, width=20, bg="red", fg="white").pack(pady=10)
        tk.Button(self.menu_frame, text="Combat Logs", command=self.show_logs, width=20).pack(pady=5)

        self.menu_frame.pack(fill="both", expand=True)

    # --- RECRUITMENT ---
    def recruit_shinobi(self):
        self.clear_frame()
        cost = 20
        if self.gold >= cost:
            self.gold -= cost
            new = Shinobi(self.player_village)
            self.shinobi.append(new)
            jutsu_names = ", ".join([j["name"] for j in new.jutsu])
            msg = f"Recruited shinobi {new.name} of clan {new.clan} with jutsu: {jutsu_names}"
        else:
            msg = "Not enough gold!"
        tk.Label(self.action_frame, text=msg, fg="white", bg="darkblue").pack(pady=20)
        tk.Button(self.action_frame, text="Back to Menu", command=self.show_menu).pack()
        self.action_frame.pack(fill="both", expand=True)

    # --- SHINOBI LIST ---
    def show_shinobi(self):
        self.clear_frame()
        canvas = tk.Canvas(self.shinobi_frame, bg="darkblue", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.shinobi_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="darkblue")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for s in self.shinobi:
            status = "Alive" if s.alive else "Down"
            tk.Button(
                scrollable_frame,
                text=f"{s.name} [{s.village}] ({s.clan}) - {status}",
                width=40,
                command=lambda s=s: self.show_shinobi_details(s)  # Pass the shinobi
            ).pack(pady=2)


        tk.Button(scrollable_frame, text="Back to Menu", command=self.show_menu).pack(pady=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.shinobi_frame.pack(fill="both", expand=True)
    
    def show_shinobi_details(self, shinobi):
        self.clear_frame()
        tk.Label(self.action_frame, text=f"Name: {shinobi.name}", fg="white", bg="darkblue", font=("Arial", 14)).pack(pady=5)
        tk.Label(self.action_frame, text=f"Clan: {shinobi.clan}", fg="white", bg="darkblue").pack(pady=2)
        tk.Label(self.action_frame, text=f"Village: {shinobi.village}", fg="white", bg="darkblue").pack(pady=2)
        tk.Label(self.action_frame, text=f"Health: {shinobi.health}", fg="white", bg="darkblue").pack(pady=2)
        tk.Label(self.action_frame, text=f"Kills: {shinobi.kills}", fg="white", bg="darkblue").pack(pady=2)
        tk.Label(self.action_frame, text="Jutsus:", fg="white", bg="darkblue").pack(pady=5)
        for j in shinobi.jutsu:
            tk.Label(self.action_frame, text=f"- {j['name']} (Power: {j['power']})", fg="white", bg="darkblue").pack(pady=1)
        tk.Button(self.action_frame, text="Back to Shinobi List", command=self.show_shinobi).pack(pady=10)
        self.action_frame.pack(fill="both", expand=True)


    # --- ALLIANCE ---
    def form_alliance_menu(self):
        self.clear_frame()
        tk.Label(self.action_frame, text="Form Alliance:", fg="white", bg="darkblue").pack(pady=10)
        for n in self.nations:
            if n not in self.allies:
                tk.Button(self.action_frame, text=f"Form alliance with {n}", command=lambda n=n: self.form_alliance(n)).pack(pady=5)
        tk.Button(self.action_frame, text="Back to Menu", command=self.show_menu).pack(pady=10)
        self.action_frame.pack(fill="both", expand=True)

    def form_alliance(self, nation):
        self.allies[nation] = self.ai[nation]
        self.show_menu()

    # --- MAP ---
    def show_map(self):
        self.clear_frame()
        tk.Label(self.map_frame, text="Map Overview:", fg="white", bg="saddlebrown", font=("Arial", 14)).pack(pady=10)
        for n in self.nations:
            status = "Ally" if n in self.allies else "Enemy"
            tk.Label(self.map_frame, text=f"{n}: {status}", fg="white", bg="saddlebrown").pack(pady=2)
        tk.Button(self.map_frame, text="Back to Menu", command=self.show_menu).pack(pady=10)
        self.map_frame.pack(fill="both", expand=True)

    # --- WAR COMBAT ---
    def start_war(self):
        self.clear_frame()
        # Ask player which nation to attack
        tk.Label(self.action_frame, text="Select a nation to attack:", fg="white", bg="darkblue").pack(pady=10)
        
        for n in self.nations:
            if n not in self.allies:
                tk.Button(self.action_frame, text=n, 
                          command=lambda n=n: self.resolve_war(n)).pack(pady=5)
        
        tk.Button(self.action_frame, text="Back to Menu", command=self.show_menu).pack(pady=10)
        self.action_frame.pack(fill="both", expand=True)

    def resolve_war(self, enemy):
        self.clear_frame()
        enemy_army = self.ai[enemy]["shinobi"]
        alive_player = [s for s in self.shinobi if s.alive]

        battle_num = 1
        self.combat_logs.append(f"--- Battle against {enemy} ---")

        # Full-team battle loop: each side attacks in turn until all on one side are down
        while any(s.alive for s in alive_player) and any(s.alive for s in enemy_army):
            self.combat_logs.append(f"Battle {battle_num}:")
            # Player attacks
            for p in alive_player:
                if not p.alive:
                    continue
                p.activate_dojutsu()
                targets = [e for e in enemy_army if e.alive]
                if not targets:
                    break
                e = random.choice(targets)
                jutsu_p = random.choice(p.jutsu)
                e.health -= jutsu_p["power"]
                log_msg = f"{p.name} used {jutsu_p['name']} on {e.name} ({e.health if e.health>0 else 0} HP left)"
                if e.health <= 0:
                    e.alive = False
                    p.kills += 1
                    log_msg += " — Target defeated!"
                self.combat_logs.append(log_msg)
                p.deactivate_dojutsu()

            # Enemy attacks
            for e in enemy_army:
                if not e.alive:
                    continue
                targets = [p for p in alive_player if p.alive]
                if not targets:
                    break
                p = random.choice(targets)
                jutsu_e = random.choice(e.jutsu)
                p.health -= jutsu_e["power"]
                log_msg = f"{e.name} used {jutsu_e['name']} on {p.name} ({p.health if p.health>0 else 0} HP left)"
                if p.health <= 0:
                    p.alive = False
                    log_msg += " — Target defeated!"
                self.combat_logs.append(log_msg)

            battle_num += 1

        # Determine winner
        if any(s.alive for s in alive_player):
            self.combat_logs.append(f"Victory against {enemy}!")
            self.gold += 50
        else:
            self.combat_logs.append(f"Defeat against {enemy}...")
            self.gold = max(0, self.gold - 20)

        tk.Label(self.action_frame, text=f"War against {enemy} ended. Check Combat Logs.", fg="white", bg="darkblue").pack(pady=20)
        tk.Button(self.action_frame, text="Back to Menu", command=self.show_menu).pack()
        self.action_frame.pack(fill="both", expand=True)
        # --- LOGS ---
    def show_logs(self):
        self.clear_frame()
        tk.Label(self.log_frame, text="Combat Logs:", fg="white", bg="gray20", font=("Arial", 14)).pack(pady=10)
        canvas = tk.Canvas(self.log_frame, bg="gray20", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.log_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="gray20")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for log in self.combat_logs:
            tk.Label(scrollable_frame, text=log, fg="white", bg="gray20").pack(pady=2)
        tk.Button(scrollable_frame, text="Back to Menu", command=self.show_menu).pack(pady=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.log_frame.pack(fill="both", expand=True)

# --- RUN GAME ---
root = tk.Tk()
game = KageGame(root)
root.mainloop()
