import os
import json
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import subprocess

# Datei zum Speichern der Spiele
SAVE_FILE = os.path.join(os.path.expanduser("~"), "Downloads", "games.json")

class GameLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("stickmanlauncher")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")  # "dark" oder "light"
        ctk.set_default_color_theme("blue")

        self.games = self.load_games()

        # UI-Elemente
        self.title_label = ctk.CTkLabel(self, text="sup!", font=("Arial", 24))
        self.title_label.pack(pady=10)

        self.game_frame = ctk.CTkFrame(self)
        self.game_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.add_game_button = ctk.CTkButton(self, text="➕ Add Game", command=self.add_game)
        self.add_game_button.pack(pady=10)

        self.display_games()

    def load_games(self):
        """Lädt gespeicherte Spiele aus der JSON-Datei"""
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r") as file:
                return json.load(file)
        return []

    def save_games(self):
        """Speichert die aktuellen Spiele in die JSON-Datei"""
        with open(SAVE_FILE, "w") as file:
            json.dump(self.games, file, indent=4)

    def add_game(self):
        """Öffnet eine Dateiauswahl, um eine `.exe`-Datei hinzuzufügen"""
        exe_path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])
        if not exe_path:
            return

        game_name = os.path.basename(exe_path)
        
        # Frage nach einem Bild für das Spiel
        img_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.ico")])
        if not img_path:
            img_path = "default_game.png"  # Falls kein Bild gewählt wurde, Standard-Bild

        # Spiel in die Liste hinzufügen
        new_game = {"name": game_name, "path": exe_path, "image": img_path}
        self.games.append(new_game)
        
        self.save_games()  # Speichern
        self.display_games()  # Spiele anzeigen

    def display_games(self):
        """Zeigt alle gespeicherten Spiele an"""
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        for index, game in enumerate(self.games):
            frame = ctk.CTkFrame(self.game_frame)
            frame.pack(fill="x", pady=5, padx=10)

            # Spiel-Bild laden
            img = Image.open(game["image"])
            img = img.resize((50, 50))
            img = ImageTk.PhotoImage(img)

            img_label = tk.Label(frame, image=img, cursor="hand2")
            img_label.image = img
            img_label.pack(side="left", padx=10)
            img_label.bind("<Button-1>", lambda e, path=game["path"]: self.launch_game(path))

            # Spielname
            label = ctk.CTkLabel(frame, text=game["name"], font=("Arial", 16))
            label.pack(side="left", padx=10)

            # Bearbeiten-Button
            edit_button = ctk.CTkButton(frame, text="✏️ Edit", command=lambda i=index: self.edit_game(i))
            edit_button.pack(side="right", padx=10)

            # Entfernen-Button
            remove_button = ctk.CTkButton(frame, text="❌", width=40, command=lambda g=game: self.remove_game(g))
            remove_button.pack(side="right", padx=10)

    def launch_game(self, exe_path):
        """Startet das ausgewählte Spiel"""
        subprocess.Popen(exe_path, shell=True)

    def remove_game(self, game):
        """Entfernt ein Spiel aus der Liste"""
        self.games.remove(game)
        self.save_games()
        self.display_games()

    def edit_game(self, index):
        """Bearbeiten des Namens und des Logos eines Spiels"""
        game = self.games[index]
        
        # Neues Nameingabefeld
        new_name = ctk.CTkInputDialog(self, text="Gib einen neuen Namen für das Spiel ein:", initial_value=game["name"])
        new_name = new_name.get_input()
        if new_name:
            game["name"] = new_name

        # Neues Bild wählen
        new_img_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.ico")])
        if new_img_path:
            game["image"] = new_img_path

        self.save_games()  # Speichern
        self.display_games()  # Spiele erneut anzeigen

if __name__ == "__main__":
    app = GameLauncher()
    app.mainloop()
