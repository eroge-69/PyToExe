import tkinter as tk
from PIL import Image, ImageTk
import math
import random

# Constantes
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400
PADDLE_HEIGHT = 80
BALL_SIZE = 40
PADDLE_SPEED = 20
WINNING_SCORE = 10

# Liste des persos et noms fichiers associés (sans extension)
PERSOS = [
    "BrBrPatapim",
    "ChimpanziniBananini",
    "BonbardiloCrocodilo",
    "CactoHippopotamo",
    "Asterion"
]

class PongGame:
    def __init__(self, root, ball_speed, player_character_name):
        self.root = root
        self.ball_speed = ball_speed
        self.player_character_name = player_character_name
        self.game_running = True
        self.player_score = 0
        self.ai_score = 0
        # IA plus lente pour que ce soit jouable :
        self.ai_max_speed = ball_speed * 0.25  # --> réduit à 25% (avant 50%)

        self.setup_ui()
        self.reset_positions()
        self.game_loop()

    def setup_ui(self):
        self.canvas = tk.Canvas(self.root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.canvas.pack()

        # Fond
        background_image = Image.open("fond.png").resize((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background_photo = ImageTk.PhotoImage(background_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_photo)

        # Raquette joueur : image perso agrandie de 30%
        original_player_image = Image.open(f"{self.player_character_name}.png")
        target_height = int(PADDLE_HEIGHT * 1.3)
        ratio = target_height / original_player_image.height
        new_width = int(original_player_image.width * ratio)
        new_height = int(original_player_image.height * ratio)
        self.player_width = new_width
        self.player_height = new_height
        resized_player_image = original_player_image.resize((new_width, new_height))
        self.player_photo = ImageTk.PhotoImage(resized_player_image)
        self.player_paddle_pos_x = 20 + new_width // 2
        self.player_paddle_pos_y = WINDOW_HEIGHT // 2
        self.player_paddle = self.canvas.create_image(self.player_paddle_pos_x, self.player_paddle_pos_y, image=self.player_photo)

        # Raquette ordi : image ordi agrandie de 30%
        original_ai_image = Image.open("ordi.png")
        target_height_ai = int(PADDLE_HEIGHT * 1.3)
        ratio_ai = target_height_ai / original_ai_image.height
        new_width_ai = int(original_ai_image.width * ratio_ai)
        new_height_ai = int(original_ai_image.height * ratio_ai)
        self.ai_width = new_width_ai
        self.ai_height = new_height_ai
        resized_ai_image = original_ai_image.resize((new_width_ai, new_height_ai))
        self.ai_photo = ImageTk.PhotoImage(resized_ai_image)
        self.ai_paddle_pos_x = WINDOW_WIDTH - 30 - new_width_ai // 2
        self.ai_paddle_pos_y = WINDOW_HEIGHT // 2
        self.ai_paddle = self.canvas.create_image(self.ai_paddle_pos_x, self.ai_paddle_pos_y, image=self.ai_photo)

        # Balle : image qui tourne
        original_ball_image = Image.open("balle.png").resize((BALL_SIZE, BALL_SIZE))
        self.original_ball_image = original_ball_image
        self.ball_photo = ImageTk.PhotoImage(original_ball_image)
        self.ball_image_obj = self.canvas.create_image(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, image=self.ball_photo)

        # Texte score (rouge avec contour noir)
        self.score_shadow = self.canvas.create_text(WINDOW_WIDTH // 2 + 1, 20 + 1, text="0 - 0", font=("Arial", 24, "bold"), fill="black")
        self.score_text = self.canvas.create_text(WINDOW_WIDTH // 2, 20, text="0 - 0", font=("Arial", 24, "bold"), fill="red")

        # Variables
        self.rotation_angle = 0
        self.keys_pressed = {"z": False, "s": False, "up": False, "down": False}

        # Vitesse balle direction aléatoire proche horizontale
        angle_deg = random.choice([30, 45, 60, 120, 135, 150])
        angle_rad = math.radians(angle_deg)
        self.ball_dx = self.ball_speed * math.cos(angle_rad)
        self.ball_dy = self.ball_speed * math.sin(angle_rad)
        if random.choice([True, False]):
            self.ball_dx = -self.ball_dx

        # Bind clavier
        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)

        # Pour affichage fin jeu
        self.win_text = None
        self.win_shadow = None
        self.replay_button = None

    def reset_positions(self):
        self.player_score = 0
        self.ai_score = 0
        self.update_score_display()
        self.reset_ball()
        self.player_paddle_pos_y = WINDOW_HEIGHT // 2
        self.canvas.coords(self.player_paddle, self.player_paddle_pos_x, self.player_paddle_pos_y)
        self.ai_paddle_pos_y = WINDOW_HEIGHT // 2
        self.canvas.coords(self.ai_paddle, self.ai_paddle_pos_x, self.ai_paddle_pos_y)
        self.game_running = True

    def key_press(self, event):
        key = event.keysym.lower()
        if key in self.keys_pressed:
            self.keys_pressed[key] = True

    def key_release(self, event):
        key = event.keysym.lower()
        if key in self.keys_pressed:
            self.keys_pressed[key] = False

    def move_player_paddle(self):
        coords = self.canvas.coords(self.player_paddle)
        y = coords[1]
        move_up = self.keys_pressed["z"] or self.keys_pressed["up"]
        move_down = self.keys_pressed["s"] or self.keys_pressed["down"]
        if move_up and y - self.player_height // 2 > 0:
            new_y = y - PADDLE_SPEED
            if new_y - self.player_height // 2 < 0:
                new_y = self.player_height // 2
            self.canvas.coords(self.player_paddle, self.player_paddle_pos_x, new_y)
        if move_down and y + self.player_height // 2 < WINDOW_HEIGHT:
            new_y = y + PADDLE_SPEED
            if new_y + self.player_height // 2 > WINDOW_HEIGHT:
                new_y = WINDOW_HEIGHT - self.player_height // 2
            self.canvas.coords(self.player_paddle, self.player_paddle_pos_x, new_y)

    def move_ai_paddle(self):
        ball_coords = self.canvas.coords(self.ball_image_obj)
        ai_coords = self.canvas.coords(self.ai_paddle)
        ball_y = ball_coords[1]
        paddle_y = ai_coords[1]
        dy = ball_y - paddle_y
        if abs(dy) > 1:
            move = max(-self.ai_max_speed, min(self.ai_max_speed, dy))
            new_y = paddle_y + move
            half_height = self.ai_height // 2
            if new_y - half_height < 0:
                new_y = half_height
            elif new_y + half_height > WINDOW_HEIGHT:
                new_y = WINDOW_HEIGHT - half_height
            self.canvas.coords(self.ai_paddle, self.ai_paddle_pos_x, new_y)
            self.ai_paddle_pos_y = new_y

    def check_collision(self, ball_coords, paddle_coords):
        bx, by = ball_coords
        px1, py1, px2, py2 = paddle_coords
        return (px1 <= bx <= px2) and (py1 <= by <= py2)

    def update_score_display(self):
        self.canvas.itemconfig(self.score_text, text=f"{self.player_score} - {self.ai_score}")
        self.canvas.itemconfig(self.score_shadow, text=f"{self.player_score} - {self.ai_score}")

    def rotate_ball(self):
        self.rotation_angle = (self.rotation_angle + 10) % 360
        rotated = self.original_ball_image.rotate(self.rotation_angle)
        self.ball_photo = ImageTk.PhotoImage(rotated)
        self.canvas.itemconfig(self.ball_image_obj, image=self.ball_photo)

    def reset_ball(self):
        self.canvas.coords(self.ball_image_obj, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        angle_deg = random.choice([30, 45, 60, 120, 135, 150])
        angle_rad = math.radians(angle_deg)
        self.ball_dx = self.ball_speed * math.cos(angle_rad)
        self.ball_dy = self.ball_speed * math.sin(angle_rad)
        if random.choice([True, False]):
            self.ball_dx = -self.ball_dx

    def show_game_over(self, winner_text):
        self.game_running = False
        self.win_shadow = self.canvas.create_text(WINDOW_WIDTH // 2 + 2, WINDOW_HEIGHT // 2 - 28 + 2,
                                                  text=winner_text, font=("Arial", 28, "bold"), fill="black")
        self.win_text = self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 28,
                                                text=winner_text, font=("Arial", 28, "bold"), fill="red")
        self.replay_button = tk.Button(self.root, text="Rejouer", font=("Arial", 16), command=self.restart_game)
        self.canvas.create_window(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20, window=self.replay_button)

    def restart_game(self):
        if self.win_text:
            self.canvas.delete(self.win_text)
            self.win_text = None
        if self.win_shadow:
            self.canvas.delete(self.win_shadow)
            self.win_shadow = None
        if self.replay_button:
            self.replay_button.destroy()
            self.replay_button = None

        self.reset_positions()
        self.game_running = True
        self.game_loop()

    def move_ball(self):
        self.canvas.move(self.ball_image_obj, self.ball_dx, self.ball_dy)
        bx, by = self.canvas.coords(self.ball_image_obj)

        # Collision haut/bas
        if by - BALL_SIZE // 2 <= 0 or by + BALL_SIZE // 2 >= WINDOW_HEIGHT:
            self.ball_dy = -self.ball_dy

        # Collision avec raquette joueur
        player_coords = self.canvas.coords(self.player_paddle)
        px1 = player_coords[0] - self.player_width // 2
        py1 = player_coords[1] - self.player_height // 2
        px2 = player_coords[0] + self.player_width // 2
        py2 = player_coords[1] + self.player_height // 2

        # Collision avec raquette IA
        ai_coords = self.canvas.coords(self.ai_paddle)
        ax1 = ai_coords[0] - self.ai_width // 2
        ay1 = ai_coords[1] - self.ai_height // 2
        ax2 = ai_coords[0] + self.ai_width // 2
        ay2 = ai_coords[1] + self.ai_height // 2

        if self.check_collision((bx, by), (px1, py1, px2, py2)) and self.ball_dx < 0:
            self.ball_dx = -self.ball_dx
        elif self.check_collision((bx, by), (ax1, ay1, ax2, ay2)) and self.ball_dx > 0:
            self.ball_dx = -self.ball_dx

        # Buts
        if bx < 0:
            self.ai_score += 1
            self.update_score_display()
            self.reset_ball()
        elif bx > WINDOW_WIDTH:
            self.player_score += 1
            self.update_score_display()
            self.reset_ball()

    def game_loop(self):
        if self.game_running:
            self.move_player_paddle()  # 👈 AJOUT ICI
            self.move_ai_paddle()
            self.move_ball()
            self.rotate_ball()

            if self.player_score >= WINNING_SCORE:
                self.show_game_over("Vous avez gagné !")
                return
            elif self.ai_score >= WINNING_SCORE:
                self.show_game_over("Thung Thung Sahour a gagné !")
                return

            self.root.after(30, self.game_loop)


class Menu:
    def __init__(self, root):
        self.root = root
        self.root.title("Menu Pong")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg="black")

        self.label_title = tk.Label(root, text="Choisissez la vitesse de la balle", font=("Arial", 24), fg="white", bg="black")
        self.label_title.pack(pady=10)

        self.ball_speed_var = tk.IntVar(value=10)

        self.speed_scale = tk.Scale(root, from_=1, to=20, orient=tk.HORIZONTAL, variable=self.ball_speed_var, length=400)
        self.speed_scale.pack(pady=10)

        self.label_perso = tk.Label(root, text="Choisissez votre personnage :", font=("Arial", 24), fg="white", bg="black")
        self.label_perso.pack(pady=10)

        self.selected_perso = tk.StringVar(value=PERSOS[0])
        self.perso_buttons = []

        self.frame_perso = tk.Frame(root, bg="black")
        self.frame_perso.pack()

        for perso in PERSOS:
            try:
                img = Image.open(f"{perso}.png").resize((100, 100), Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Erreur chargement image {perso}: {e}")
                continue
            rb = tk.Radiobutton(self.frame_perso, image=photo, variable=self.selected_perso, value=perso, indicatoron=0, selectcolor="red", bg="black")
            rb.image = photo  # pour éviter que l'image soit garbage collected
            rb.pack(side=tk.LEFT, padx=10)
            self.perso_buttons.append(rb)

        self.button_start = tk.Button(root, text="Jouer", font=("Arial", 24), command=self.start_game)
        self.button_start.pack(pady=20)

    def start_game(self):
        ball_speed = self.ball_speed_var.get()
        player_char = self.selected_perso.get()

        self.root.destroy()
        root2 = tk.Tk()
        game = PongGame(root2, ball_speed, player_char)
        root2.mainloop()

def main():
    root = tk.Tk()
    menu = Menu(root)
    root.mainloop()

if __name__ == "__main__":
    main()