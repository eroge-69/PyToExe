# --- Gra Wędkarska z obsługą grafik ---
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os, random, time, pickle
import pygame

pygame.mixer.init()
catch_sound = pygame.mixer.Sound("sounds/catch.wav")
miss_sound = pygame.mixer.Sound("sounds/miss.wav")
click_sound = pygame.mixer.Sound("sounds/click.wav")

# --- Funkcja pomocnicza do ładowania obrazków ---
def load_image(path, size=(80, 80)):
    try:
        img = Image.open(path)
        img = img.resize(size, Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)
    except:
        return None

# --- Rzadkości ryb ---
RARITIES = {
    "pospolita":   {"catch_chance": 0.25, "xp": 5, "coins": 10, "speed": 2},
    "zwykła":      {"catch_chance": 0.20, "xp": 10, "coins": 15, "speed": 2.2},
    "częsta":      {"catch_chance": 0.15, "xp": 15, "coins": 25, "speed": 2.6},
    "średnia":     {"catch_chance": 0.10, "xp": 20, "coins": 35, "speed": 3},
    "niezła":      {"catch_chance": 0.08, "xp": 30, "coins": 50, "speed": 3.5},
    "rzadka":      {"catch_chance": 0.07, "xp": 50, "coins": 80, "speed": 4},
    "cenna":       {"catch_chance": 0.05, "xp": 70, "coins": 120, "speed": 4.5},
    "epicka":      {"catch_chance": 0.04, "xp": 100, "coins": 200, "speed": 5},
    "mityczna":    {"catch_chance": 0.025, "xp": 150, "coins": 400, "speed": 6},
    "legendarna":  {"catch_chance": 0.015, "xp": 250, "coins": 750, "speed": 7},
    "Boss": {
    "catch_chance": 0.005,  # bardzo rzadka
    "xp": 500,
    "coins": 1500,
    "speed": 8
    },
}
RARITY_WINS = {
    "pospolita": 1,
    "zwykła": 1,
    "częsta": 2,
    "średnia": 3,
    "niezła": 4,
    "rzadka": 5,
    "cenna": 6,
    "epicka": 6,
    "mityczna": 7,
    "legendarna": 8,
    "Boss": 8,
}

# --- Wędki ---
RODS = [
    {"name": "Kij leszczowy", "price": 0, "zone_size": 30, "img": "img/rods/kij_leszczowy.png"},
    {"name": "Wędka bambusowa", "price": 200, "zone_size": 40, "img": "img/rods/wedka_bambusowa.png"},
    {"name": "Wędka pro", "price": 500, "zone_size": 50, "img": "img/rods/wedka_pro.png"},
    {"name": "Wędka mistrza", "price": 1000, "zone_size": 60, "img": "img/rods/wedka_mistrza.png"},
# Nowe wędki:
    {"name": "Wędka szczęścia", "price": 1500, "zone_size": 65, "img": "img/rods/wedka_szczescia.png", "bonus_luck": 0.05},
    {"name": "Wędka błyskawicy", "price": 2000, "zone_size": 70, "img": "img/rods/wedka_blyskawicy.png", "speed_boost": 0.9},
    {"name": "Wędka legend", "price": 3000, "zone_size": 75, "img": "img/rods/wedka_legend.png"},
    {"name": "Wędka astralna", "price": 4000, "zone_size": 80, "img": "img/rods/wedka_astralna.png", "bonus_rare": 0.1},
    {"name": "Wędka chaosu", "price": 5000, "zone_size": 90, "img": "img/rods/wedka_chaosu.png", "randomize_effect": True},
]
# --- Przynęty ---
BAITS = [
    {"name": "Robak", "price": 0, "bonus": 0.00, "img": "img/bait/robak.png"},
    {"name": "Czerwony robak", "price": 200, "bonus": 0.02, "img": "img/bait/czerwony_robak.png"},
    {"name": "Larwa ochotka", "price": 400, "bonus": 0.04, "img": "img/bait/larwa_ochotka.png"},
    {"name": "Krewetka wodna", "price": 700, "bonus": 0.07, "img": "img/bait/krewetka_wodna.png"},
    {"name": "Złoty plankton", "price": 1200, "bonus": 0.10, "img": "img/bait/zloty_plankton.png"},
]

# --- Ryby ---
SPOT_PRICES = {
    "Staw Miejski": 0,
    "Laguna Słoneczna": 700,
    "Jezioro Magmy": 900,
    "Zalew Królewski": 1100,
    "Zatoka Lodowych Szeptów": 1300,
    "Rzeka Cieni": 1500,
    "Głębie Kosmiczne": 1700,
    "Bagna Wieczności": 1900,
    "Ocean Mechaniczny": 2100,
}
FISHES = {
    "Staw Miejski": [
        {"name": "Płotka", "rarity": "pospolita", "img": "img/fish/plotka.png"},
        {"name": "Karp", "rarity": "zwykła", "img": "img/fish/karp.png"},
        {"name": "Okoń", "rarity": "częsta", "img": "img/fish/okon.png"},
        {"name": "Leszcz", "rarity": "średnia", "img": "img/fish/leszcz.png"},
        {"name": "Sandacz", "rarity": "niezła", "img": "img/fish/sandacz.png"},
        {"name": "Szczupak", "rarity": "rzadka", "img": "img/fish/szczupak.png"},
        {"name": "Węgorz", "rarity": "cenna", "img": "img/fish/wegorz.png"},
        {"name": "Troć", "rarity": "epicka", "img": "img/fish/troc.png"},
        {"name": "Łosoś", "rarity": "mityczna", "img": "img/fish/losos.png"},
        {"name": "Jesiotr Złoty", "rarity": "legendarna", "img": "img/fish/jesiotr_zloty.png"},
        {"name": "Carpzilla", "rarity": "Boss", "img": "img/fish/boss_carpzilla.png"}
    ]
}
# --- Dodajemy 3 nowe łowiska z 20 rybami tematycznymi każde ---

FISHES["Laguna Słoneczna"] = [
    {"name": n, "rarity": r} for n, r in zip([
        "Błyskotka", "Tropikalny Karaś", "Neonowa Płoć", "Tęczowy Karp", "Paletka",
        "Rafańczyk", "Lśniący Okoń", "Pasiasty Lin", "Kolorowy Leszcz", "Bananowy Sum",
        "Słoneczny Sandacz", "Turkusowy Szczupak", "Lazurowy Węgorz", "Koralowa Troć", "Perłowy Łosoś",
        "Księżniczka Pustyni", "Syrena", "Książę Fal", "Delfinowy Duch", "Tropikalny Feniks"
        ,"Słoneczny Tytan"
    ], [
        "pospolita", "pospolita", "zwykła", "zwykła", "częsta",
        "częsta", "częsta", "średnia", "średnia", "niezła",
        "niezła", "rzadka", "cenna", "epicka", "epicka",
        "epicka", "mityczna", "mityczna", "mityczna", "legendarna",
        "Boss"
    ])
]

FISHES["Jezioro Magmy"] = [
    {"name": n, "rarity": r} for n, r in zip([
        "Płomień Płoć", "Żar Karaś", "Rozgrzany Karp", "Liniowiec Magmowy", "Czerwony Leszcz",
        "Wulkaniczny Okoń", "Gorący Sum", "Lawowy Sandacz", "Popielny Szczupak", "Siarkowy Węgorz",
        "Troć Lawy", "Łosoś Ziemi", "Pstrąg Popiołu", "Skarb Magmy", "Brzana Ognia",
        "Płomienista Sielawa", "Dymny Rekin", "Feniks Lawy", "Smok Podziemi", "Cesarz Ognia"
        ,"Władca Lawy"
    ], [
        "pospolita", "pospolita", "zwykła", "zwykła", "częsta",
        "częsta", "częsta", "średnia", "średnia", "niezła",
        "niezła", "rzadka", "cenna", "epicka", "epicka",
        "epicka", "mityczna", "mityczna", "mityczna", "legendarna",
        "Boss"
    ])
]

FISHES["Zalew Królewski"] = [
    {"name": n, "rarity": r} for n, r in zip([
        "Dworska Płoć", "Złoty Karaś", "Koronny Karp", "Książęcy Lin", "Herbowy Leszcz",
        "Błękitny Okoń", "Szlachetny Sum", "Srebrny Sandacz", "Szmaragdowy Szczupak", "Platynowy Węgorz",
        "Rubinowa Troć", "Diamentowy Łosoś", "Jadeitowy Pstrąg", "Szafirowa Brzana", "Topazowa Sielawa",
        "Ryba Królewska", "Ryba Herbowa", "Królowa Wód", "Rybi Regent", "Rybi Cesarz"
        ,"Imperialna Bestia"
    ], [
        "pospolita", "pospolita", "zwykła", "zwykła", "częsta",
        "częsta", "częsta", "średnia", "średnia", "niezła",
        "niezła", "rzadka", "cenna", "epicka", "epicka",
        "epicka", "mityczna", "mityczna", "mityczna", "legendarna",
        "Boss"
    ])
]
FISHES["Zatoka Lodowych Szeptów"] = [
    {"name": n, "rarity": r} for n, r in zip([
        "Lodowa Płoć", "Zamarznięty Karaś", "Śnieżny Karp", "Lodowy Lin", "Szronowy Leszcz",
        "Biały Okoń", "Zimny Sum", "Mroźny Sandacz", "Soplowy Szczupak", "Arkticzny Węgorz",
        "Troć Śnieżna", "Polarny Łosoś", "Pstrąg Szronowy", "Zimowy Skarb", "Królowa Lodu",
        "Złoty Yeti", "Strażnik Zatoki", "Pani Zimy", "Lodowy Feniks", "Mroźny Smok"
        ,"Lodowy Kolos"
    ], [
        "pospolita", "pospolita", "zwykła", "zwykła", "częsta",
        "częsta", "częsta", "średnia", "średnia", "niezła",
        "niezła", "rzadka", "cenna", "epicka", "epicka",
        "epicka", "mityczna", "mityczna", "mityczna", "legendarna",
        "Boss"
    ])
]
FISHES["Rzeka Cieni"] = [
    {"name": n, "rarity": r} for n, r in zip([
        "Ciemna Płoć", "Mroczny Karaś", "Upiorny Karp", "Widmowy Lin", "Czarny Leszcz",
        "Zmierzchowy Okoń", "Duszny Sum", "Cienisty Sandacz", "Mglisty Szczupak", "Głęboki Węgorz",
        "Troć Północy", "Czarny Łosoś", "Widmowy Pstrąg", "Cień Brzany", "Skradająca się Sielawa",
        "Upiorna Syrena", "Ryba Przeklęta", "Strażnik Ciemności", "Mroczny Duch", "Cień Króla"
        ,"Król Mroku"
    ], [
        "pospolita", "pospolita", "zwykła", "zwykła", "częsta",
        "częsta", "częsta", "średnia", "średnia", "niezła",
        "niezła", "rzadka", "cenna", "epicka", "epicka",
        "epicka", "mityczna", "mityczna", "mityczna", "legendarna",
        "Boss"
    ])
]
FISHES["Głębie Kosmiczne"] = [
    {"name": n, "rarity": r} for n, r in zip([
        "Gwiezdna Płoć", "Orbitalny Karaś", "Galaktyczny Karp", "Astrolin", "Nebularny Leszcz",
        "Meteorowy Okoń", "Kosmiczny Sum", "Plazmowy Sandacz", "Czarna Szczupak", "Quarkowy Węgorz",
        "Troć Kosmiczna", "Łosoś Andromedy", "Pstrąg Pulsarowy", "Brzana Komety", "Sielawa Saturna",
        "Władca Orbit", "Księżniczka Mgławicy", "Ryba Hypernova", "Feniks Kosmosu", "Strażnik Galaktyki"
        ,"Galaktyczny Strażnik"
    ], [
        "pospolita", "pospolita", "zwykła", "zwykła", "częsta",
        "częsta", "częsta", "średnia", "średnia", "niezła",
        "niezła", "rzadka", "cenna", "epicka", "epicka",
        "epicka", "mityczna", "mityczna", "mityczna", "legendarna",
        "Boss"
    ])
]
FISHES["Bagna Wieczności"] = [
    {"name": n, "rarity": r} for n, r in zip([
        "Błotna Płoć", "Mętny Karaś", "Grząski Karp", "Bagienny Lin", "Zarośnięty Leszcz",
        "Oślizgły Okoń", "Gnijący Sum", "Szlamowy Sandacz", "Zielony Szczupak", "Stęchły Węgorz",
        "Troć Bagienna", "Zgniły Łosoś", "Reliktowy Pstrąg", "Szczur Wodny", "Topielcowa Sielawa",
        "Cień Przodków", "Ryba Wieczności", "Dusza Bagniska", "Pradawny Władca", "Król Topielców"
        ,"Topielczy Władca"
    ], [
        "pospolita", "pospolita", "zwykła", "zwykła", "częsta",
        "częsta", "częsta", "średnia", "średnia", "niezła",
        "niezła", "rzadka", "cenna", "epicka", "epicka",
        "epicka", "mityczna", "mityczna", "mityczna", "legendarna",
        "Boss"
    ])
]
FISHES["Ocean Mechaniczny"] = [
    {"name": n, "rarity": r} for n, r in zip([
        "Cyfrowa Płoć", "Mecha-Karaś", "Hydro-Karp", "Chipowy Lin", "Zębaty Leszcz",
        "Okoń Zasilany", "Sum Trybikowy", "Sandacz Syntetyczny", "Szczupak Optyczny", "Węgorz Prądowy",
        "Troć Obwodowa", "Łosoś Bioniczny", "Pstrąg Nano", "Brzana Sztuczna", "Sielawa Energetyczna",
        "Dron Rybny", "Neuro-Ryba", "Golem Wodny", "Feniks Techniczny", "Cybernetyczny Król"
        ,"Cyber Kraken"
    ], [
        "pospolita", "pospolita", "zwykła", "zwykła", "częsta",
        "częsta", "częsta", "średnia", "średnia", "niezła",
        "niezła", "rzadka", "cenna", "epicka", "epicka",
        "epicka", "mityczna", "mityczna", "mityczna", "legendarna",
        "Boss"
    ])
]


# --- Klasa gracza ---
class Player:
    def __init__(self):
        self.level = 1
        self.xp = 0
        self.coins = 100
        self.cooldown_active = False
        self.cooldown_end_time = 0
        self.spot = "Staw Miejski"
        self.unlocked_spots = {"Staw Miejski"}
        self.rod_index = 0
        self.bait_index = 0
        self.journal = set()

    def xp_to_next_level(self):
        return int(100 * (self.level ** 1.5))

    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_to_next_level():
            self.xp -= self.xp_to_next_level()
            self.level += 1

    def gain_coins(self, amount):
        self.coins += amount

    def get_zone_size(self):
        return RODS[self.rod_index]["zone_size"]

    def get_bait_bonus(self):
        return BAITS[self.bait_index]["bonus"]

    def unlock_spot(self, name):
        self.unlocked_spots.add(name)

# --- Zapis/Wczytanie gry ---
SAVE_FILE = "savegame.pkl"

def save_game():
    try:
        with open(SAVE_FILE, "wb") as f:
            pickle.dump(player, f)
        messagebox.showinfo("Zapisano", "Gra została zapisana.")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie udało się zapisać gry:\n{e}")

def load_game():
    global player
    try:
        with open(SAVE_FILE, "rb") as f:
            loaded_player = pickle.load(f)
            if isinstance(loaded_player, Player):
                player = loaded_player
                update_stats()
                update_spot_menu()
                messagebox.showinfo("Wczytano", "Gra została wczytana.")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie udało się wczytać gry:\n{e}")
# --- Start GUI ---
player = Player()
root = tk.Tk()
root.title("Gra Wędkarska z grafikami")
root.geometry("600x500")

stats_var = tk.StringVar()
cooldown_var = tk.StringVar()
try:
    pygame.mixer.music.load("sounds/music.mp3")  # lub .ogg
    pygame.mixer.music.set_volume(0.5)  # Głośność 0.0–1.0
    pygame.mixer.music.play(-1)  # -1 = zapętlona muzyka
except Exception as e:
    print(f"Nie udało się załadować muzyki: {e}")

def update_stats():
    stats_var.set(f"Poziom: {player.level} | XP: {player.xp}/{player.xp_to_next_level()} | Monety: {player.coins}")
    update_cooldown_display()

def update_cooldown_display():
    if player.cooldown_active:
        remaining = max(0, player.cooldown_end_time - time.time())
        cooldown_var.set(f"Cooldown: {remaining:.1f}s")
        if remaining > 0:
            root.after(100, update_cooldown_display)
        else:
            cooldown_var.set("")
            player.cooldown_active = False
    else:
        cooldown_var.set("")

tk.Label(root, textvariable=stats_var, font=("Arial", 12)).pack(pady=5)
tk.Label(root, textvariable=cooldown_var, font=("Arial", 10), fg="red").pack()

def generate_fish_weight(rarity, spot):
    # Maksymalna waga zależna od łowiska
    spot_max_weights = {
        "Staw Miejski": 10,
        "Laguna Słoneczna": 50,
        "Jezioro Magmy": 100,
        "Zalew Królewski": 500,
        "Zatoka Lodowych Szeptów": 1000,
        "Rzeka Cieni": 1500,
        "Głębie Kosmiczne": 2000,
        "Bagna Wieczności": 3000,
        "Ocean Mechaniczny": 3000
    }
    max_weight = spot_max_weights.get(spot, 10)

    # Rzadkość wpływa na prawdopodobieństwo większej wagi
    rarity_index = list(RARITIES.keys()).index(rarity)
    weight_bias = 1.0 - (rarity_index / len(RARITIES))  # 1.0 (pospolita) do ~0 (legendarna)

    # Dolna granica też zależy od rzadkości – epickie mogą być lekkie
    min_weight = max(0.3, 0.01 * max_weight)
    upper_weight = max(min_weight + 0.1, max_weight * weight_bias)

    return round(random.uniform(min_weight, upper_weight), 2)

def start_minigame(fish_data=None, remaining_wins=None):
    if fish_data is None:
        fish_list = FISHES[player.spot]
        weights = [RARITIES[f["rarity"]]["catch_chance"] * (1 + player.get_bait_bonus()) for f in fish_list]
        fish = random.choices(fish_list, weights=weights)[0]
        weight = generate_fish_weight(fish["rarity"], player.spot)
        total_wins_required = RARITY_WINS[fish["rarity"]]
        remaining_wins = total_wins_required
    else:
        fish = fish_data["fish"]
        weight = fish_data["weight"]

    fish_list = FISHES[player.spot]
    weights = [RARITIES[f["rarity"]]["catch_chance"] * (1 + player.get_bait_bonus()) for f in fish_list]
    fish = random.choices(fish_list, weights=weights)[0]
    weight = generate_fish_weight(fish["rarity"], player.spot)
    rarity = fish["rarity"]
    data = RARITIES[rarity]
    base_speed = data["speed"]
    rod_quality_factor = 1.0 - (player.rod_index / (len(RODS) - 1)) * 0.4
    # od 1.0 do 0.6
    speed = base_speed * rod_quality_factor

    zone_size = player.get_zone_size()

    rarity_order = list(RARITIES.keys())
    rarity_index = rarity_order.index(rarity)
    spot_cost = SPOT_PRICES.get(player.spot, 0)
    cost_factor = min(1.0, spot_cost / 2000)  # Zakładamy max koszt ~2000
    # Skalowanie od rzadkości
    rarity_factor = min(1.0, rarity_index / (len(rarity_order) - 1))  # 0.0 (pospolita) do 1.0 (legendarna)

    # Skalowanie od kosztu
    cost_factor = min(1.0, spot_cost / 2000)  # 0.0 (tanie) do 1.0 (bardzo drogie)

    # Trudność: łącznie rzadkość + koszt (po 40% wagi), 20% minimum
    difficulty_scale = max(0.2, 1.0 - (0.4 * rarity_factor + 0.4 * cost_factor))

    weight_factor = max(0.4, 1.2 - (weight / 10))  # cięższa ryba = mniejszy pasek
    bar_height = max(6, int(zone_size * difficulty_scale * weight_factor))




    win = tk.Toplevel(root)
    win.title(f"{fish['name']} ({rarity})")
    win.geometry("300x300")

    canvas = tk.Canvas(win, width=300, height=300)
    canvas.pack()

    center = 150  # Środek nowego większego obszaru
    zone_y1 = center - zone_size // 2
    zone_y2 = center + zone_size // 2

    canvas.create_rectangle(50, zone_y1, 250, zone_y2, fill="green")

    bar = canvas.create_rectangle(50, 10, 250, 10 + bar_height, fill="red")

    fish_img = load_image(fish.get("img", ""), (100, 100))
    if fish_img:
        tk.Label(win, image=fish_img).pack()
        win.image_ref = fish_img

    direction = 1

    def move_bar():
        nonlocal direction
        coords = canvas.coords(bar)
        if coords[1] <= 0:
            direction = 1
        elif coords[3] >= 300:
            direction = -1
        canvas.move(bar, 0, direction * speed)
        win.after(20, move_bar)

    def stop_game():
        nonlocal remaining_wins
        coords = canvas.coords(bar)
        y = (coords[1] + coords[3]) / 2
        if zone_y1 <= y <= zone_y2:
            remaining_wins -= 1
            if remaining_wins > 0:
                win.destroy()
                start_minigame(fish_data={"fish": fish, "weight": weight}, remaining_wins=remaining_wins)
            else:
                player.gain_xp(data["xp"])
                coins = int(data["coins"] * (0.8 + weight / 10))  # premia za wagę
                player.gain_coins(coins)
                player.journal.add((fish["name"], rarity, fish.get("img")))
                update_stats()
                catch_sound.play()
                messagebox.showinfo("Złowiono", f"{fish['name']} ({rarity})\nWaga: {weight} kg\n+{data['xp']} XP, +{coins} monet")
                win.destroy()
        else:
            miss_sound.play()
            messagebox.showinfo("Pudło", f"Ryba {fish['name']} ({rarity}) uciekła!")
            win.destroy()


    win.bind("<space>", lambda e: stop_game())
    tk.Label(win, text="Wciśnij SPACJĘ aby zatrzymać!").pack(pady=5)
    move_bar()

def fish_action():
    if player.cooldown_active:
        click_sound.play()
        messagebox.showinfo("Czekaj", "Poczekaj aż cooldown się zakończy.")
        return
    player.cooldown_active = True
    player.cooldown_end_time = time.time() + 3
    update_cooldown_display()
    start_minigame()

tk.Button(root, text="🎣 Łów ryby", font=("Arial", 14), command=fish_action).pack(padx=10, pady=5)
# --- Sklep ---
def open_shop():
    shop = tk.Toplevel(root)
    shop.title("🛒 Sklep")
    shop.geometry("500x400")

    notebook = ttk.Notebook(shop)
    notebook.pack(expand=True, fill="both")

    # --- Wędki ---
    frame_rods = tk.Frame(notebook)
    notebook.add(frame_rods, text="Wędki")
    for i, rod in enumerate(RODS):
        rod_img = load_image(rod["img"])
        label = f"{rod['name']} ({'obecna' if i == player.rod_index else f'{rod['price']} monet'})"
        tk.Label(frame_rods, text=label).grid(row=i, column=1, sticky="w")
        if rod_img:
            img_label = tk.Label(frame_rods, image=rod_img)
            img_label.image = rod_img
            img_label.grid(row=i, column=0)
        if i != player.rod_index:
            tk.Button(frame_rods, text="Kup", command=lambda i=i: buy_rod(i, shop)).grid(row=i, column=2)

    # --- Przynęty ---
    frame_baits = tk.Frame(notebook)
    notebook.add(frame_baits, text="Przynęty")
    for i, bait in enumerate(BAITS):
        bait_img = load_image(bait["img"])
        label = f"{bait['name']} ({'używana' if i == player.bait_index else f'{bait['price']} monet'})"
        tk.Label(frame_baits, text=label).grid(row=i, column=1, sticky="w")
        if bait_img:
            img_label = tk.Label(frame_baits, image=bait_img)
            img_label.image = bait_img
            img_label.grid(row=i, column=0)
        if i != player.bait_index:
            tk.Button(frame_baits, text="Kup", command=lambda i=i: buy_bait(i, shop)).grid(row=i, column=2)

    # --- Łowiska ---
    frame_spots = tk.Frame(notebook)
    notebook.add(frame_spots, text="Łowiska")
    for i, spot in enumerate(FISHES.keys()):
        if spot in player.unlocked_spots:
            label = f"{spot} (odblokowane)"
        else:
            price = 500 + i * 200
            label = f"{spot} - {price} monet"
            tk.Button(frame_spots, text="Kup", command=lambda s=spot, p=price: buy_spot(s, p, shop)).grid(row=i, column=1)
        tk.Label(frame_spots, text=label).grid(row=i, column=0, sticky="w")

def buy_rod(i, window):
    rod = RODS[i]
    if player.coins >= rod["price"]:
        player.coins -= rod["price"]
        player.rod_index = i
        update_stats()
        window.destroy()
        open_shop()
    else:
        messagebox.showwarning("Brak środków", "Nie masz wystarczająco monet.")

def buy_bait(i, window):
    bait = BAITS[i]
    if player.coins >= bait["price"]:
        player.coins -= bait["price"]
        player.bait_index = i
        update_stats()
        window.destroy()
        open_shop()
    else:
        messagebox.showwarning("Brak środków", "Nie masz wystarczająco monet.")

def buy_spot(name, price, window):
    if player.coins >= price:
        player.coins -= price
        player.unlock_spot(name)
        update_stats()
        update_spot_menu()
        window.destroy()
        open_shop()
    else:
        messagebox.showwarning("Brak środków", "Nie masz wystarczająco monet.")

tk.Button(root, text="🛍 Sklep", command=open_shop).pack(padx=10, pady=5)
# --- Wybór łowiska ---
spot_var = tk.StringVar()

def update_spot_menu():
    spot_menu["menu"].delete(0, "end")
    for spot in sorted(player.unlocked_spots):
        spot_menu["menu"].add_command(label=spot, command=tk._setit(spot_var, spot, change_spot))
    spot_var.set(player.spot)

def change_spot(*args):
    player.spot = spot_var.get()
    update_stats()

tk.Label(root, text="Wybierz łowisko:").pack()
spot_menu = tk.OptionMenu(root, spot_var, "")
spot_menu.pack()
update_spot_menu()

# --- Dziennik rybaka ---
def open_journal():
    top = tk.Toplevel(root)
    top.title("📘 Dziennik złowionych ryb")

    canvas = tk.Canvas(top, width=400, height=400)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    if not player.journal:
        tk.Label(scrollable_frame, text="Brak zapisanych ryb").pack(pady=10)
    else:
        for name, rarity, img_path in sorted(player.journal):
            frame = tk.Frame(scrollable_frame)
            frame.pack(padx=10, pady=5, anchor="w")
            image = load_image(img_path, size=(64, 64))
            if image:
                tk.Label(frame, image=image).pack(side="left")
                frame.image_ref = image
            tk.Label(frame, text=f"{name} ({rarity})", font=("Arial", 10)).pack(side="left", padx=10)

tk.Button(root, text="📘 Dziennik", command=open_journal).pack(padx=10, pady=5)

# --- Zapis/Wczytanie gry ---
tk.Button(root, text="💾 Zapisz grę", command=save_game).pack(padx=10, pady=5)
tk.Button(root, text="📂 Wczytaj grę", command=load_game).pack(padx=10, pady=5)

# --- Uruchomienie gry ---
update_stats()
root.mainloop()
