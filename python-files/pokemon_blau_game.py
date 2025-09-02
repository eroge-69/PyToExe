
import random
import tkinter as tk
from tkinter import messagebox

# Define basic game data
pokemon_list = ["Pikachu", "Charmander", "Bulbasaur", "Squirtle", "Jigglypuff", "Meowth"]
item_list = ["Potion", "Pokéball", "Antidote", "Rare Candy", "Escape Rope"]

class PokemonGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Pokémon Blau")
        self.canvas = tk.Canvas(root, width=400, height=400, bg="lightgreen")
        self.canvas.pack()

        self.player = self.canvas.create_rectangle(190, 190, 210, 210, fill="blue")
        self.root.bind("<KeyPress>", self.move_player)

        self.encounter_chance = 0.2
        self.item_chance = 0.1

    def move_player(self, event):
        moves = {"Up": (0, -10), "Down": (0, 10), "Left": (-10, 0), "Right": (10, 0)}
        if event.keysym in moves:
            dx, dy = moves[event.keysym]
            self.canvas.move(self.player, dx, dy)
            self.check_for_encounter()
            self.check_for_item()

    def check_for_encounter(self):
        if random.random() < self.encounter_chance:
            pokemon = random.choice(pokemon_list)
            messagebox.showinfo("Pokémon Encounter!", f"Ein wildes {pokemon} erscheint!")

    def check_for_item(self):
        if random.random() < self.item_chance:
            item = random.choice(item_list)
            messagebox.showinfo("Item gefunden!", f"Du hast ein {item} gefunden!")

# Create and run the game window
root = tk.Tk()
game = PokemonGame(root)
root.mainloop()
