import tkinter as tk
from tkinter import messagebox
import datetime

try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

class TTScoringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Table Tennis Match Scorer")
        self.root.attributes("-fullscreen", False)  # Fullscreen
        self.root.configure(bg="#525658")  # App background color
        self.match_type = 3
        self.history = []

        self.player_a = "Player A"
        self.player_b = "Player B"

        self.color_options = ["dark green", "red", "dark blue", "orange"]
        self.color_index_a = 0
        self.color_index_b = 1

        self.get_player_names()

    def get_player_names(self):
        self.name_window = tk.Toplevel(self.root)
        self.name_window.title("Enter Player Names")
        self.name_window.geometry("300x200")
        self.name_window.grab_set()

        tk.Label(self.name_window, text="Player A Name:").pack(pady=5)
        self.name_a_entry = tk.Entry(self.name_window)
        self.name_a_entry.pack(pady=5)

        tk.Label(self.name_window, text="Player B Name:").pack(pady=5)
        self.name_b_entry = tk.Entry(self.name_window)
        self.name_b_entry.pack(pady=5)

        tk.Button(self.name_window, text="Start Match", command=self.set_names).pack(pady=10)

    def set_names(self):
        a = self.name_a_entry.get().strip()
        b = self.name_b_entry.get().strip()
        if a: self.player_a = a
        if b: self.player_b = b
        self.name_window.destroy()
        self.setup_ui()
        self.reset_match()

    def setup_ui(self):
        tk.Label(self.root, text="Match Type:", font=("Arial", 16), bg="#525658").pack()
        self.match_var = tk.StringVar(value="3")
        tk.OptionMenu(self.root, self.match_var, "3", "5", "7", command=self.change_match_type).pack()

        self.score_frame = tk.Frame(self.root, bg="#525658")
        self.score_frame.pack(pady=30)

        self.player_a_frame = tk.Frame(self.score_frame, bg=self.color_options[self.color_index_a], padx=20, pady=20)
        self.player_a_frame.grid(row=0, column=0, padx=30)

        self.score_a_label = tk.Label(self.player_a_frame, text=f"{self.player_a}\n0", font=("Arial", 28), bg=self.color_options[self.color_index_a], fg="white")
        self.score_a_label.pack()

        tk.Button(self.player_a_frame, text=f"Add Point {self.player_a}", command=lambda: self.add_point('A')).pack(pady=10)
        tk.Button(self.player_a_frame, text="Change Color", command=self.change_color_a).pack()

        self.player_b_frame = tk.Frame(self.score_frame, bg=self.color_options[self.color_index_b], padx=20, pady=20)
        self.player_b_frame.grid(row=0, column=1, padx=30)

        self.score_b_label = tk.Label(self.player_b_frame, text=f"{self.player_b}\n0", font=("Arial", 28), bg=self.color_options[self.color_index_b], fg="white")
        self.score_b_label.pack()

        tk.Button(self.player_b_frame, text=f"Add Point {self.player_b}", command=lambda: self.add_point('B')).pack(pady=10)
        tk.Button(self.player_b_frame, text="Change Color", command=self.change_color_b).pack()

        self.controls_frame = tk.Frame(self.root, bg="#525658")
        self.controls_frame.pack(pady=20)

        tk.Button(self.controls_frame, text="Undo", command=self.undo, width=12, height=2).grid(row=0, column=0, padx=10)
        tk.Button(self.controls_frame, text="Reset Match", command=self.reset_match, width=12, height=2).grid(row=0, column=1, padx=10)
        tk.Button(self.controls_frame, text="Exit Fullscreen", command=self.exit_fullscreen, width=12, height=2).grid(row=0, column=2, padx=10)

        self.status_label = tk.Label(self.root, text="", font=("Arial", 20), bg="#525658")
        self.status_label.pack(pady=20)

    def change_color_a(self):
        self.color_index_a = (self.color_index_a + 1) % len(self.color_options)
        color = self.color_options[self.color_index_a]
        self.player_a_frame.config(bg=color)
        self.score_a_label.config(bg=color)

    def change_color_b(self):
        self.color_index_b = (self.color_index_b + 1) % len(self.color_options)
        color = self.color_options[self.color_index_b]
        self.player_b_frame.config(bg=color)
        self.score_b_label.config(bg=color)

    def exit_fullscreen(self):
        self.root.attributes("-fullscreen", False)

    def change_match_type(self, value):
        self.match_type = int(value)
        self.reset_match()

    def reset_match(self):
        self.games_to_win = (self.match_type // 2) + 1
        self.points_a = 0
        self.points_b = 0
        self.games_a = 0
        self.games_b = 0
        self.game_number = 1
        self.history.clear()
        self.update_display()

    def add_point(self, player):
        self.history.append((self.points_a, self.points_b, self.games_a, self.games_b))
        if player == 'A':
            self.points_a += 1
        else:
            self.points_b += 1

        self.check_game_winner()
        self.update_display()

    def undo(self):
        if not self.history:
            return
        self.points_a, self.points_b, self.games_a, self.games_b = self.history.pop()
        self.update_display()

    def check_game_winner(self):
        if max(self.points_a, self.points_b) >= 11 and abs(self.points_a - self.points_b) >= 2:
            if self.points_a > self.points_b:
                self.games_a += 1
                self.show_custom_popup(f"{self.player_a} wins Game {self.game_number}")
            else:
                self.games_b += 1
                self.show_custom_popup(f"{self.player_b} wins Game {self.game_number}")
            self.game_number += 1
            self.points_a = 0
            self.points_b = 0

            if self.games_a == self.games_to_win:
                self.match_end(self.player_a)
            elif self.games_b == self.games_to_win:
                self.match_end(self.player_b)

    def match_end(self, winner):
        self.show_custom_popup(f"🏆 {winner} wins the MATCH!")
        self.save_summary(winner)
        self.reset_match()

    def show_custom_popup(self, message):
        if SOUND_AVAILABLE:
            winsound.MessageBeep()
        popup = tk.Toplevel(self.root)
        popup.title("Info")
        popup.geometry("500x200")
        popup.configure(bg="#222222")
        popup.grab_set()

        tk.Label(popup, text=message, font=("Arial", 20), fg="white", bg="#222222").pack(pady=30)
        tk.Button(popup, text="OK", command=popup.destroy, font=("Arial", 14)).pack()

    def update_display(self):
        self.score_a_label.config(text=f"{self.player_a}\n{self.points_a}")
        self.score_b_label.config(text=f"{self.player_b}\n{self.points_b}")
        self.status_label.config(
            text=f"Game: {self.game_number} | {self.player_a}: {self.games_a}  {self.player_b}: {self.games_b}"
        )

    def save_summary(self, winner):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        summary = (
            f"Match Summary ({now}):\n"
            f"{self.player_a} vs {self.player_b}\n"
            f"Winner: {winner}\n"
            f"Final Score: {self.player_a} {self.games_a} - {self.player_b} {self.games_b}\n"
            f"{'-'*40}\n"
        )
        with open("match_summary.txt", "a") as f:
            f.write(summary)

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = TTScoringApp(root)
    root.mainloop()
