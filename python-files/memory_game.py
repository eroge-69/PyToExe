import os

import json
import random
import time
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk

# Настройки папок
BASE_DIR = r"C:\Users\MykytaMarin\Desktop\Memory\memory\puge wan laf"
CARDS_DIR = os.path.join(BASE_DIR, "cards")
HIGHSCORE_FILE = os.path.join(BASE_DIR, "highscores.json")

# Базовый размер карт
BASE_CARD_WIDTH = 190
BASE_CARD_HEIGHT = 290

# Настройки уровней 
LEVELS = [
    {"pairs": 2, "moves": 6},
    {"pairs": 3, "moves": 8},
    {"pairs": 4, "moves": 10},
    {"pairs": 5, "moves": 12},
    {"pairs": 6, "moves": 14},
    {"pairs": 7, "moves": 16},
    {"pairs": 8, "moves": 18},
    {"pairs": 9, "moves": 20},
    {"pairs": 10, "moves": 22},
    {"pairs": 11, "moves": 24},
    {"pairs": 12, "moves": 26},
    {"pairs": 14, "moves": 28},
]

class MemoryGame:
    def __init__(self, root, player_name, difficulty, level_index=0, total_score=0):
        self.root = root
        self.player_name = player_name
        self.difficulty = difficulty
        self.level_index = level_index
        self.level_data = LEVELS[level_index]
        self.level = level_index + 1
        self.total_score = total_score

        # Ходы с учётом сложности
        self.max_moves = self.level_data["moves"]
        if difficulty == "Лёгкий":
            self.max_moves += 2
        elif difficulty == "Сложный":
            self.max_moves -= 2

        self.moves_left = self.max_moves
        self.total_pairs = self.level_data["pairs"]
        self.start_time = None
        self.flipped_cards = []
        self.found_pairs = 0

        # Dev Mode
        self.dev_mode = False

        self.load_images()
        self.create_ui()

    def load_images(self):
        """Загрузка картинок для текущего уровня с автоуменьшением"""
        level_folder = os.path.join(CARDS_DIR, f"level{self.level}")
        if not os.path.exists(level_folder):
            messagebox.showerror("Ошибка", f"Папка {level_folder} не найдена!")
            self.root.destroy()
            return

        window_width = self.root.winfo_screenwidth() - 100
        window_height = self.root.winfo_screenheight() - 200

        columns = min(self.total_pairs, 9)
        rows = (self.total_pairs * 2 + columns - 1) // columns

        required_width = columns * (BASE_CARD_WIDTH + 10)
        required_height = rows * (BASE_CARD_HEIGHT + 10)

        scale_w = window_width / required_width
        scale_h = window_height / required_height
        scale = min(scale_w, scale_h, 1.0)

        card_width = int(BASE_CARD_WIDTH * scale)
        card_height = int(BASE_CARD_HEIGHT * scale)

        self.CARD_WIDTH = card_width
        self.CARD_HEIGHT = card_height

        self.card_images = []
        for file in os.listdir(level_folder):
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                img_path = os.path.join(level_folder, file)
                img = Image.open(img_path).resize((card_width, card_height))
                self.card_images.append(ImageTk.PhotoImage(img))

        if len(self.card_images) < self.total_pairs:
            messagebox.showerror("Ошибка", f"В папке {level_folder} недостаточно картинок!")
            self.root.destroy()

        self.card_back = ImageTk.PhotoImage(
            Image.new("RGB", (card_width, card_height), color="gray")
        )

    def create_ui(self):
        self.root.configure(bg="#2e2e2e")

        # Горячие клавиши для Dev Mode
        self.root.bind("<F12>", self.toggle_dev_mode)
        self.root.bind("<F1>", self.reveal_all_cards)
        self.root.bind("<F2>", self.add_moves)
        self.root.bind("<F3>", self.win_level)

        self.info_frame = tk.Frame(self.root, bg="#2e2e2e")
        self.info_frame.pack(pady=10)

        self.moves_label = tk.Label(
            self.info_frame,
            text=f"Уровень {self.level} — Осталось ходов: {self.moves_left}",
            bg="#2e2e2e", fg="white"
        )
        self.moves_label.pack(side=tk.LEFT, padx=20)

        self.time_label = tk.Label(
            self.info_frame,
            text="Время: 0 сек",
            bg="#2e2e2e", fg="white"
        )
        self.time_label.pack(side=tk.LEFT, padx=20)

        self.score_label = tk.Label(
            self.info_frame,
            text=f"Общий счёт: {self.total_score}",
            bg="#2e2e2e", fg="white"
        )
        self.score_label.pack(side=tk.LEFT, padx=20)

        self.board_frame = tk.Frame(self.root, bg="#2e2e2e")
        self.board_frame.pack()

        self.create_board()

        self.start_time = time.time()
        self.update_timer()

    def create_board(self):
        cards = self.card_images[:self.total_pairs] * 2
        random.shuffle(cards)
        self.cards_on_board = []

        columns = min(self.total_pairs, 9)
        for i, img in enumerate(cards):
            btn = tk.Button(
                self.board_frame,
                image=self.card_back,
                command=lambda idx=i: self.flip_card(idx)
            )
            btn.grid(row=i // columns, column=i % columns, padx=5, pady=5)
            self.cards_on_board.append({"button": btn, "image": img, "flipped": False})

    def flip_card(self, idx):
        card = self.cards_on_board[idx]
        if card["flipped"] or len(self.flipped_cards) == 2:
            return

        card["button"].config(image=card["image"])
        card["flipped"] = True
        self.flipped_cards.append(idx)

        if len(self.flipped_cards) == 2:
            self.root.after(1000, self.check_match)

    def check_match(self):
        idx1, idx2 = self.flipped_cards
        card1 = self.cards_on_board[idx1]
        card2 = self.cards_on_board[idx2]

        if card1["image"] == card2["image"]:
            self.found_pairs += 1
        else:
            card1["button"].config(image=self.card_back)
            card1["flipped"] = False
            card2["button"].config(image=self.card_back)
            card2["flipped"] = False

        self.moves_left -= 1
        self.moves_label.config(text=f"Уровень {self.level} — Осталось ходов: {self.moves_left}")
        self.flipped_cards = []

        if self.found_pairs == self.total_pairs:
            self.level_complete()
        elif self.moves_left <= 0:
            messagebox.showinfo("Поражение", "Ходы закончились!")
            self.root.destroy()

    def level_complete(self):
        elapsed = int(time.time() - self.start_time)
        score = self.calculate_score(elapsed)
        self.total_score += score

        self.save_highscore(elapsed, score)

        if self.level_index + 1 < len(LEVELS):
            self.root.destroy()
            root = tk.Tk()
            MemoryGame(root, self.player_name, self.difficulty, self.level_index + 1, self.total_score)
            root.mainloop()
        else:
            messagebox.showinfo("Победа!", f"Вы прошли все уровни!\nВаш общий счёт: {self.total_score}")
            self.root.destroy()

    def calculate_score(self, elapsed_time):
        return (self.level * 100) + (self.moves_left * 10) - (elapsed_time // 5)

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        self.time_label.config(text=f"Время: {elapsed} сек")
        self.root.after(1000, self.update_timer)

    def save_highscore(self, elapsed_time, score):
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                highscores = json.load(f)
        else:
            highscores = {}

        level_key = f"Level {self.level}"
        if level_key not in highscores:
            highscores[level_key] = []

        highscores[level_key].append({
            "name": self.player_name,
            "level": self.level,
            "moves_left": self.moves_left,
            "time": elapsed_time,
            "score": score
        })

        highscores[level_key] = sorted(highscores[level_key], key=lambda x: x["score"], reverse=True)[:5]

        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(highscores, f, ensure_ascii=False, indent=4)

    # ===== ЧИТЫ =====
    def toggle_dev_mode(self, event=None):
        self.dev_mode = not self.dev_mode
        if self.dev_mode:
            messagebox.showinfo("Dev Mode", "Режим разработчика включен")
        else:
            messagebox.showinfo("Dev Mode", "Режим разработчика выключен")

    def reveal_all_cards(self, event=None):
        if self.dev_mode:
            for card in self.cards_on_board:
                card["button"].config(image=card["image"])
                card["flipped"] = True

    def add_moves(self, event=None):
        if self.dev_mode:
            self.moves_left += 5
            self.moves_label.config(text=f"Уровень {self.level} — Осталось ходов: {self.moves_left}")

    def win_level(self, event=None):
        if self.dev_mode:
            self.found_pairs = self.total_pairs
            self.level_complete()


def choose_name_and_difficulty():
    name_window = tk.Tk()
    name_window.withdraw()
    player_name = simpledialog.askstring("Ваше имя", "Введите ваше имя:")
    if not player_name:
        player_name = "Игрок"
    name_window.destroy()

    def start_game(diff):
        diff_window.destroy()
        root = tk.Tk()
        MemoryGame(root, player_name, diff)
        root.mainloop()

    diff_window = tk.Tk()
    diff_window.title("Выбор сложности")

    tk.Label(diff_window, text="Выберите сложность:", font=("Arial", 14)).pack(pady=10)
    tk.Button(diff_window, text="Лёгкий", width=15, height=2, command=lambda: start_game("Лёгкий")).pack(pady=5)
    tk.Button(diff_window, text="Средний", width=15, height=2, command=lambda: start_game("Средний")).pack(pady=5)
    tk.Button(diff_window, text="Сложный", width=15, height=2, command=lambda: start_game("Сложный")).pack(pady=5)

    diff_window.mainloop()


if __name__ == "__main__":
    choose_name_and_difficulty()
