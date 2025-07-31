import os
import tkinter as tk
import tkinter.messagebox as messagebox
import math
import random

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Hexes(tk.Canvas):
    def __init__(self, master, hex_size, hex_positions, *args, **kwargs):
        canvas_size = hex_size * 5
        super().__init__(master, width=canvas_size * 3, height=canvas_size * 3, *args, **kwargs)
        self.hex_size = hex_size
        center_x = (canvas_size / 2) + (hex_size * 3)
        center_y = (canvas_size / 2)
        self.center_x = center_x
        self.center_y = center_y

        self.hex_positions = hex_positions  # Geldige hex-posities

        # Terreintypes en afbeeldingen laden
        self.terrain_types = ["bos", "water", "woestijn"]
        self.terrain_images = {
            "bos": tk.PhotoImage(file="images/terrain_forest.png"),
            "water": tk.PhotoImage(file="images/terrain_ocean.png"),
            "woestijn": tk.PhotoImage(file="images/terrain_desert.png"),
        }

        self.hex_terrain_map = {}

        # Teken hexen en willekeurige terreinen
        for (x_step, y_step) in hex_positions:
            x = center_x + ((x_step - (y_step / 2)) * (hex_size * math.sqrt(3)))
            y = center_y + (y_step * (hex_size * 1.5))
            self.draw_hex(x, y)

            terrain = random.choice(self.terrain_types)
            self.hex_terrain_map[(x_step, y_step)] = terrain
            self.create_image(x, y, image=self.terrain_images[terrain])

        # Startposities pionnen
        self.pawn_yellow_x_steps = 0
        self.pawn_yellow_y_steps = 0
        self.pawn_red_x_steps = 4
        self.pawn_red_y_steps = 4

        # Laad pion afbeeldingen
        self.pawn_yellow_image = tk.PhotoImage(file="images/pawn_yellow.png")
        pawn_x = center_x + ((self.pawn_yellow_x_steps - (self.pawn_yellow_y_steps / 2)) * (hex_size * math.sqrt(3)))
        pawn_y = center_y + (self.pawn_yellow_y_steps * (hex_size * 1.5))
        self.pawn_yellow_id = self.create_image(pawn_x, pawn_y, image=self.pawn_yellow_image)

        self.pawn_red_image = tk.PhotoImage(file="images/pawn_red.png")
        pawn_x = center_x + ((self.pawn_red_x_steps - (self.pawn_red_y_steps / 2)) * (hex_size * math.sqrt(3)))
        pawn_y = center_y + (self.pawn_red_y_steps * (hex_size * 1.5))
        self.pawn_red_id = self.create_image(pawn_x, pawn_y, image=self.pawn_red_image)

        # Begin met geel aan de beurt
        self.current_player = "yellow"
        self.game_over = False

        # Stappen per terrein per speler (start 5 per terrein)
        self.steps_left = {
            "yellow": {terrain: 5 for terrain in self.terrain_types},
            "red": {terrain: 5 for terrain in self.terrain_types}
        }

        # Labels voor stappen tonen (wordt ingesteld in UI setup)

    def draw_hex(self, x, y):
        size = self.hex_size
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.radians(angle_deg)
            px = x + size * math.cos(angle_rad)
            py = y + size * math.sin(angle_rad)
            points.append(px)
            points.append(py)
        self.create_polygon(points, outline='black', fill='lightblue', width=2)

    def is_valid_position(self, x, y):
        return (x, y) in self.hex_positions

    def update_pawn_position(self, player):
        if player == "yellow":
            new_x = self.center_x + ((self.pawn_yellow_x_steps - (self.pawn_yellow_y_steps / 2)) * (self.hex_size * math.sqrt(3)))
            new_y = self.center_y + (self.pawn_yellow_y_steps * (self.hex_size * 1.5))
            self.coords(self.pawn_yellow_id, new_x, new_y)
        else:
            new_x = self.center_x + ((self.pawn_red_x_steps - (self.pawn_red_y_steps / 2)) * (self.hex_size * math.sqrt(3)))
            new_y = self.center_y + (self.pawn_red_y_steps * (self.hex_size * 1.5))
            self.coords(self.pawn_red_id, new_x, new_y)

    def update_step_labels(self):
        # Wordt door UI ingesteld, roept dit aan na elke zet om labels up to date te houden
        if hasattr(self, 'step_labels'):
            for player in ("yellow", "red"):
                naam = "Geel" if player == "yellow" else "Rood"
                text = f"{naam} stappen over: "
                text += ", ".join(f"{terrain}: {self.steps_left[player][terrain]}" for terrain in self.terrain_types)
                self.step_labels[player].config(text=text)

    def can_move(self, player):
        # Check alle 6 mogelijke zetten voor deze speler
        x = self.pawn_yellow_x_steps if player == "yellow" else self.pawn_red_x_steps
        y = self.pawn_yellow_y_steps if player == "yellow" else self.pawn_red_y_steps

        # Alle mogelijke buurposities in hex-coördinaten (6 richtingen)
        neighbors = [
            (x + 1, y),       # rechts
            (x - 1, y),       # links
            (x + 1, y + 1),   # rechtsonder
            (x, y + 1),       # linksonder
            (x, y - 1),       # rechtsboven
            (x - 1, y - 1),   # linksboven
        ]

        for (nx, ny) in neighbors:
            if not self.is_valid_position(nx, ny):
                continue
            terrain = self.hex_terrain_map.get((nx, ny))
            if terrain is None:
                continue
            if self.steps_left[player][terrain] > 0:
                return True  # Er is minstens één geldige zet mogelijk
        return False  # Geen geldige zet

    def try_move(self, new_x, new_y, error_msg):
        if self.game_over:
            return False

        if not self.is_valid_position(new_x, new_y):
            messagebox.showerror("Invalid Move", error_msg)
            return False

        terrain = self.hex_terrain_map.get((new_x, new_y))
        if terrain is None:
            messagebox.showerror("Invalid Move", "Onbekend terrein!")
            return False

        if self.steps_left[self.current_player][terrain] <= 0:
            messagebox.showerror("Invalid Move", f"Geen stappen meer voor terrein {terrain}. Kies een andere zet.")
            # Niet wisselen van beurt, speler mag opnieuw kiezen
            return False

        # Zet door en aftrekken stappen
        self.steps_left[self.current_player][terrain] -= 1

        if self.current_player == "yellow":
            self.pawn_yellow_x_steps = new_x
            self.pawn_yellow_y_steps = new_y
            self.update_pawn_position("yellow")

            # Check tikkertje (overlap)
            if (new_x, new_y) == (self.pawn_red_x_steps, self.pawn_red_y_steps):
                self.delete(self.pawn_red_id)
                messagebox.showinfo("Spel afgelopen", "Geel heeft gewonnen!")
                self.game_over = True
                return True

            # Wissel beurt, maar check eerst of volgende speler kan zetten
            self.current_player = "red"
            if not self.can_move("red"):
                messagebox.showinfo("Spel afgelopen", "Rood kan niet zetten. Geel wint!")
                self.game_over = True

        else:
            self.pawn_red_x_steps = new_x
            self.pawn_red_y_steps = new_y
            self.update_pawn_position("red")

            if (new_x, new_y) == (self.pawn_yellow_x_steps, self.pawn_yellow_y_steps):
                self.delete(self.pawn_yellow_id)
                messagebox.showinfo("Spel afgelopen", "Rood heeft gewonnen!")
                self.game_over = True
                return True

            self.current_player = "yellow"
            if not self.can_move("yellow"):
                messagebox.showinfo("Spel afgelopen", "Geel kan niet zetten. Rood wint!")
                self.game_over = True

        self.update_step_labels()
        return True

    # Beweging functies blijven hetzelfde (move_pawn_right, etc.)

    def move_pawn_right(self):
        if self.game_over:
            return
        if self.current_player == "yellow":
            new_x = self.pawn_yellow_x_steps + 1
            new_y = self.pawn_yellow_y_steps
            self.try_move(new_x, new_y, "Pion kan niet verder naar rechts bewegen!")
        else:
            new_x = self.pawn_red_x_steps + 1
            new_y = self.pawn_red_y_steps
            self.try_move(new_x, new_y, "Pion kan niet verder naar rechts bewegen!")

    def move_pawn_left(self):
        if self.game_over:
            return
        if self.current_player == "yellow":
            new_x = self.pawn_yellow_x_steps - 1
            new_y = self.pawn_yellow_y_steps
            self.try_move(new_x, new_y, "Pion kan niet verder naar links bewegen!")
        else:
            new_x = self.pawn_red_x_steps - 1
            new_y = self.pawn_red_y_steps
            self.try_move(new_x, new_y, "Pion kan niet verder naar links bewegen!")

    def move_pawn_bottom_right(self):
        if self.game_over:
            return
        if self.current_player == "yellow":
            new_x = self.pawn_yellow_x_steps + 1
            new_y = self.pawn_yellow_y_steps + 1
            self.try_move(new_x, new_y, "Pion kan niet verder naar rechtsonder bewegen!")
        else:
            new_x = self.pawn_red_x_steps + 1
            new_y = self.pawn_red_y_steps + 1
            self.try_move(new_x, new_y, "Pion kan niet verder naar rechtsonder bewegen!")

    def move_pawn_bottom_left(self):
        if self.game_over:
            return
        if self.current_player == "yellow":
            new_x = self.pawn_yellow_x_steps
            new_y = self.pawn_yellow_y_steps + 1
            self.try_move(new_x, new_y, "Pion kan niet verder naar linksonder bewegen!")
        else:
            new_x = self.pawn_red_x_steps
            new_y = self.pawn_red_y_steps + 1
            self.try_move(new_x, new_y, "Pion kan niet verder naar linksonder bewegen!")

    def move_pawn_top_right(self):
        if self.game_over:
            return
        if self.current_player == "yellow":
            new_x = self.pawn_yellow_x_steps
            new_y = self.pawn_yellow_y_steps - 1
            self.try_move(new_x, new_y, "Pion kan niet verder naar rechtsboven bewegen!")
        else:
            new_x = self.pawn_red_x_steps
            new_y = self.pawn_red_y_steps - 1
            self.try_move(new_x, new_y, "Pion kan niet verder naar rechtsboven bewegen!")

    def move_pawn_top_left(self):
        if self.game_over:
            return
        if self.current_player == "yellow":
            new_x = self.pawn_yellow_x_steps - 1
            new_y = self.pawn_yellow_y_steps - 1
            self.try_move(new_x, new_y, "Pion kan niet verder naar linksboven bewegen!")
        else:
            new_x = self.pawn_red_x_steps - 1
            new_y = self.pawn_red_y_steps - 1
            self.try_move(new_x, new_y, "Pion kan niet verder naar linksboven bewegen!")


if __name__ == "__main__":
    hex_positions = [
        (0, 0), (1, 0), (2, 0), (3, 0),
        (0, 1), (1, 1), (2, 1), (3, 1), (4, 1),
        (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2),
        (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3),
        (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4),
        (2, 5), (3, 5), (4, 5), (5, 5), (6, 5),
        (3, 6), (4, 6), (5, 6), (6, 6)
    ]

    root = tk.Tk()
    root.title("Hexagons Map")

    frame = tk.Frame(root)
    frame.pack()

    canvas = Hexes(root, hex_size=35, hex_positions=hex_positions)
    canvas.pack()

    # Laad afbeeldingen pijlen
    arrow_top_right_img = tk.PhotoImage(file="images/arrow_top_right.png")
    arrow_top_left_img = tk.PhotoImage(file="images/arrow_top_left.png")
    arrow_right_img = tk.PhotoImage(file="images/arrow_right.png")
    arrow_left_img = tk.PhotoImage(file="images/arrow_left.png")
    arrow_bottom_right_img = tk.PhotoImage(file="images/arrow_bottom_right.png")
    arrow_bottom_left_img = tk.PhotoImage(file="images/arrow_bottom_left.png")

    # Plaats knoppen in grid
    button_top_left = tk.Button(frame, image=arrow_top_left_img, command=canvas.move_pawn_top_left)
    button_top_left.grid(row=0, column=1)

    button_top_right = tk.Button(frame, image=arrow_top_right_img, command=canvas.move_pawn_top_right)
    button_top_right.grid(row=0, column=3)

    button_left = tk.Button(frame, image=arrow_left_img, command=canvas.move_pawn_left)
    button_left.grid(row=1, column=0)

    button_right = tk.Button(frame, image=arrow_right_img, command=canvas.move_pawn_right)
    button_right.grid(row=1, column=4)

    button_bottom_left = tk.Button(frame, image=arrow_bottom_left_img, command=canvas.move_pawn_bottom_left)
    button_bottom_left.grid(row=2, column=1)

    button_bottom_right = tk.Button(frame, image=arrow_bottom_right_img, command=canvas.move_pawn_bottom_right)
    button_bottom_right.grid(row=2, column=3)

    dot_img = tk.PhotoImage(file="images/red_dot.png")
    dot_label = tk.Label(frame, image=dot_img)
    dot_label.grid(row=1, column=2)

    # Stappen labels tonen
    step_labels_frame = tk.Frame(root)
    step_labels_frame.pack(pady=10)

    step_label_yellow = tk.Label(step_labels_frame, text="", fg="goldenrod", font=("Arial", 12))
    step_label_yellow.pack()

    step_label_red = tk.Label(step_labels_frame, text="", fg="red", font=("Arial", 12))
    step_label_red.pack()

    # Koppelen labels aan canvas voor update
    canvas.step_labels = {
        "yellow": step_label_yellow,
        "red": step_label_red
    }
    canvas.update_step_labels()

    turn_frame = tk.Frame(root)
    turn_frame.pack(pady=5)

    turn_text_label = tk.Label(turn_frame, text="Beurt: ", font=("Arial", 14))
    turn_text_label.pack(side="left")

    turn_color_label = tk.Label(turn_frame, text="Geel", font=("Arial", 14, "bold"), fg="goldenrod")
    turn_color_label.pack(side="left")

    def update_turn_label():
        if canvas.current_player == "yellow":
            turn_color_label.config(text="Geel", fg="goldenrod")
        else:
            turn_color_label.config(text="Rood", fg="red")


    # Haak try_move aan om beurt label te updaten
    original_try_move = canvas.try_move
    def try_move_and_update(new_x, new_y, error_msg):
        result = original_try_move(new_x, new_y, error_msg)
        update_turn_label()
        return result
    canvas.try_move = try_move_and_update

    root.mainloop()
