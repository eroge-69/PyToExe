
import tkinter as tk
from tkinter import simpledialog

# Constants
MAX_PLAYERS = 20
MIN_PLAYERS = 2

class ScoreboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("멀티 점수판")
        self.players = []
        self.scores = []
        self.entries = []
        self.labels = []

        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=10)

        self.select_players()

    def select_players(self):
        num = simpledialog.askinteger("플레이어 수 선택", f"{MIN_PLAYERS}명 이상 {MAX_PLAYERS}명 이하로 입력하세요:", minvalue=MIN_PLAYERS, maxvalue=MAX_PLAYERS)
        if num:
            self.setup_scoreboard(num)

    def setup_scoreboard(self, num_players):
        for i in range(num_players):
            frame = tk.Frame(self.root)
            frame.pack(pady=5)

            name_entry = tk.Entry(frame, width=15)
            name_entry.insert(0, f"플레이어 {i+1}")
            name_entry.grid(row=0, column=0)

            score_label = tk.Label(frame, text="0", width=5, font=("Helvetica", 16))
            score_label.grid(row=0, column=1)

            btn_plus = tk.Button(frame, text="+1", command=lambda i=i: self.update_score(i, 1))
            btn_plus.grid(row=0, column=2)

            btn_minus = tk.Button(frame, text="-1", command=lambda i=i: self.update_score(i, -1))
            btn_minus.grid(row=0, column=3)

            self.entries.append(name_entry)
            self.labels.append(score_label)
            self.scores.append(0)

        reset_btn = tk.Button(self.root, text="전체 초기화", command=self.reset_scores)
        reset_btn.pack(pady=10)

    def update_score(self, index, delta):
        self.scores[index] += delta
        self.labels[index].config(text=str(self.scores[index]))

    def reset_scores(self):
        for i in range(len(self.scores)):
            self.scores[i] = 0
            self.labels[i].config(text="0")

# Run the app
root = tk.Tk()
app = ScoreboardApp(root)
root.mainloop()
