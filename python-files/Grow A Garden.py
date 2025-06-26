import tkinter as tk
from tkinter import messagebox
import time
import threading

# --- Game Settings ---
SEEDS = {
    "🌱 Carrot": {"price": 5, "growth_time": 10, "sell_price": 15},
    "🌻 Sunflower": {"price": 8, "growth_time": 15, "sell_price": 25},
    "🍅 Tomato": {"price": 6, "growth_time": 12, "sell_price": 20}
}
GRID_SIZE = 4  # 4x4 garden

class PlantTile:
    def __init__(self, button):
        self.button = button
        self.seed_type = None
        self.planted_time = None
        self.state = "empty"

    def plant(self, seed_type):
        self.seed_type = seed_type
        self.planted_time = time.time()
        self.state = "growing"
        self.update_button("🌿 Growing")
        threading.Thread(target=self.grow).start()

    def grow(self):
        time.sleep(SEEDS[self.seed_type]["growth_time"])
        self.state = "grown"
        self.update_button("✅ Ready")

    def harvest(self):
        if self.state == "grown":
            self.state = "empty"
            self.update_button("🟩")
            return self.seed_type
        return None

    def update_button(self, text):
        self.button.config(text=text)

class GardenGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🌸 Grow a Garden!")
        self.coins = 50
        self.inventory = {}
        self.selected_seed = None
        self.tiles = []

        self.style_ui()
        self.create_ui()

    def style_ui(self):
        self.root.configure(bg="#f0fff0")

    def create_ui(self):
        # Coins + Inventory
        self.top_frame = tk.Frame(self.root, bg="#dfffd6")
        self.top_frame.pack(fill="x")

        self.coins_label = tk.Label(self.top_frame, text=f"💰 Coins: {self.coins}", font=("Helvetica", 14), bg="#dfffd6")
        self.coins_label.pack(side="left", padx=10)

        self.inventory_label = tk.Label(self.top_frame, text="🎒 Inventory: {}", font=("Helvetica", 14), bg="#dfffd6")
        self.inventory_label.pack(side="right", padx=10)

        # Garden Grid
        self.garden_frame = tk.Frame(self.root, bg="#e8ffe8", padx=10, pady=10)
        self.garden_frame.pack()

        for r in range(GRID_SIZE):
            row = []
            for c in range(GRID_SIZE):
                btn = tk.Button(self.garden_frame, text="🟩", font=("Helvetica", 16), width=6, height=3,
                                command=lambda row=r, col=c: self.plant_or_harvest(row, col))
                btn.grid(row=r, column=c, padx=5, pady=5)
                row.append(PlantTile(btn))
            self.tiles.append(row)

        # Seed Seller
        self.seed_frame = tk.Frame(self.root, bg="#fff7e6", pady=10)
        self.seed_frame.pack(fill="x")

        tk.Label(self.seed_frame, text="🧺 Seed Seller", font=("Helvetica", 14, "bold"), bg="#fff7e6").pack()
        for seed in SEEDS:
            tk.Button(self.seed_frame, text=f"{seed} - ${SEEDS[seed]['price']}", bg="#fff0c1",
                      command=lambda s=seed: self.select_seed(s)).pack(pady=2)

        # Sell Stand
        self.sell_frame = tk.Frame(self.root, bg="#fef0f0", pady=10)
        self.sell_frame.pack(fill="x")

        tk.Label(self.sell_frame, text="💵 Sell Stand", font=("Helvetica", 14, "bold"), bg="#fef0f0").pack()
        tk.Button(self.sell_frame, text="🧺 Sell All Crops", bg="#ffc0cb", command=self.sell_crops).pack(pady=5)

    def select_seed(self, seed):
        self.selected_seed = seed
        messagebox.showinfo("Seed Selected", f"You selected: {seed}")

    def plant_or_harvest(self, r, c):
        tile = self.tiles[r][c]
        if tile.state == "empty":
            if not self.selected_seed:
                messagebox.showwarning("No Seed", "Select a seed first!")
                return
            if self.coins < SEEDS[self.selected_seed]["price"]:
                messagebox.showerror("Not enough coins", "You need more coins!")
                return
            self.coins -= SEEDS[self.selected_seed]["price"]
            tile.plant(self.selected_seed)
        elif tile.state == "grown":
            harvested = tile.harvest()
            if harvested:
                self.inventory[harvested] = self.inventory.get(harvested, 0) + 1
        self.update_labels()

    def sell_crops(self):
        total = 0
        for crop, count in self.inventory.items():
            sell_price = SEEDS[crop]["sell_price"]
            total += count * sell_price
        self.coins += total
        self.inventory.clear()
        messagebox.showinfo("Sold", f"You earned ${total}!")
        self.update_labels()

    def update_labels(self):
        self.coins_label.config(text=f"💰 Coins: {self.coins}")
        self.inventory_label.config(text=f"🎒 Inventory: {self.inventory}")

# Run game
if __name__ == "__main__":
    root = tk.Tk()
    game = GardenGame(root)
    root.mainloop()
