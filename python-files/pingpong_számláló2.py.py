import tkinter as tk
from tkinter import ttk, messagebox

class PingPongApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏓 Pingpong Pontszámláló")
        self.root.geometry("1200x800")

        self.setup_variables()
        self.create_widgets()

    def setup_variables(self):
        # Játékállapot
        self.player1 = "Játékos 1"
        self.player2 = "Játékos 2"
        self.server = self.player1
        self.scores = {self.player1: 0, self.player2: 0}
        self.total_points = 0
        self.set_results = []
        self.point_limit = 11
        self.serve_change_every = 2
        self.win_by = 2

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.setup_tab = tk.Frame(self.notebook)
        self.game_tab = tk.Frame(self.notebook)
        self.sets_tab = tk.Frame(self.notebook)

        self.notebook.add(self.setup_tab, text="Beállítások")
        self.notebook.add(self.game_tab, text="Játék")
        self.notebook.add(self.sets_tab, text="Szett eredmények")

        self.create_setup_tab()
        self.create_game_tab()
        self.create_sets_tab()

    def create_setup_tab(self):
        tk.Label(self.setup_tab, text="Pingpong Beállítások", font=("Arial", 32)).pack(pady=20)

        form = tk.Frame(self.setup_tab)
        form.pack(pady=10)

        # Játékosnevek
        tk.Label(form, text="Játékos 1 neve:", font=("Arial", 20)).grid(row=0, column=0, padx=10, pady=10)
        self.name1_entry = tk.Entry(form, font=("Arial", 20), width=15)
        self.name1_entry.grid(row=0, column=1)

        tk.Label(form, text="Játékos 2 neve:", font=("Arial", 20)).grid(row=1, column=0, padx=10, pady=10)
        self.name2_entry = tk.Entry(form, font=("Arial", 20), width=15)
        self.name2_entry.grid(row=1, column=1)

        # Pontlimit
        tk.Label(form, text="Pontlimit:", font=("Arial", 20)).grid(row=2, column=0, padx=10, pady=10)
        self.point_limit_var = tk.IntVar(value=11)
        tk.OptionMenu(form, self.point_limit_var, 5, 11, 21).grid(row=2, column=1)

        # Szervaváltás
        tk.Label(form, text="Szervacsere (pontonként):", font=("Arial", 20)).grid(row=3, column=0, padx=10, pady=10)
        self.serve_every_var = tk.IntVar(value=2)
        tk.OptionMenu(form, self.serve_every_var, 1, 2).grid(row=3, column=1)

        # Indító gomb
        tk.Button(self.setup_tab, text="Játék indítása", font=("Arial", 24),
                  command=self.start_game).pack(pady=30)

    def create_game_tab(self):
        self.score_label = tk.Label(self.game_tab, text="", font=("Arial", 60))
        self.score_label.pack(pady=40)

        self.server_label = tk.Label(self.game_tab, text="", font=("Arial", 40), fg="blue")
        self.server_label.pack()

        button_frame = tk.Frame(self.game_tab)
        button_frame.pack(pady=50)

        self.btn1 = tk.Button(button_frame, text="", font=("Arial", 36), width=15, height=2,
                              command=lambda: self.add_point(self.player1))
        self.btn1.grid(row=0, column=0, padx=50)

        self.btn2 = tk.Button(button_frame, text="", font=("Arial", 36), width=15, height=2,
                              command=lambda: self.add_point(self.player2))
        self.btn2.grid(row=0, column=1, padx=50)

    def create_sets_tab(self):
		self.sets_table = ttk.Treeview(self.sets_tab, columns=("szett", "eredmény", "győztes"), show="headings", height=10)
		self.sets_table.heading("szett", text="Szett #")
		self.sets_table.heading("eredmény", text="Eredmény")
		self.sets_table.heading("győztes", text="Győztes")
    
		self.sets_table.column("szett", width=100, anchor="center")
		self.sets_table.column("eredmény", width=200, anchor="center")
		self.sets_table.column("győztes", width=300, anchor="center")
		self.sets_table.pack(pady=50, expand=True)

    def start_game(self):
        self.player1 = self.name1_entry.get() or "Játékos 1"
        self.player2 = self.name2_entry.get() or "Játékos 2"
        self.point_limit = self.point_limit_var.get()
        self.serve_change_every = self.serve_every_var.get()

        self.scores = {self.player1: 0, self.player2: 0}
        self.total_points = 0
        self.server = self.player1

        self.btn1.config(text=f"{self.player1} +1")
        self.btn2.config(text=f"{self.player2} +1")
        self.update_display()

        self.notebook.select(self.game_tab)

    def update_display(self):
        self.score_label.config(text=f"{self.player1}: {self.scores[self.player1]}    |    {self.player2}: {self.scores[self.player2]}")
        self.server_label.config(text=f"🎾 Szervál: {self.server}")

    def add_point(self, player):
        self.scores[player] += 1
        self.total_points += 1

        # Szervaváltás
        total = self.scores[self.player1] + self.scores[self.player2]
        if self.serve_change_every and total % self.serve_change_every == 0:
            self.server = self.player2 if self.server == self.player1 else self.player1

        self.update_display()
        self.check_win()

    def check_win(self):
        for player in [self.player1, self.player2]:
            if self.scores[player] >= self.point_limit:
                diff = abs(self.scores[self.player1] - self.scores[self.player2])
                if diff >= self.win_by:
                    result = f"{self.scores[self.player1]} - {self.scores[self.player2]}"
                    winner = player
                    self.set_results.append((result, winner))
                    self.sets_table.insert("", "end", values=(len(self.set_results), result, winner))
                    messagebox.showinfo("Szett vége", f"{winner} megnyerte a szettet!\nEredmény: {result}")
                    self.reset_game()

    def reset_game(self):
        self.scores = {self.player1: 0, self.player2: 0}
        self.total_points = 0
        self.server = self.player1
        self.update_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = PingPongApp(root)
    root.mainloop()
