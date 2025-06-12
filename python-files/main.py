import tkinter as tk
from tkinter import messagebox

AREAS = [
    "Watchtower", "Inn", "Field 1", "Field 2", "Well",
    "Animal Pen", "Shrine", "Granary", "Burial Grounds", "Passage"
]
GREEN = "Green"
RONIN_STATS = {
    "Hayai": {"vitality": 5},
    "Kabe": {"vitality": 7},
    "Musashi": {"vitality": 4},
    "Taiko": {"vitality": 5},
    "Tasuke": {"vitality": 3},
    "Yobu": {"vitality": 3},
    "Yumi": {"vitality": 3},
}
MAX_ROUNDS = 8

class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("7 Ronin")
        self.main_menu()

    def main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="7 Ronin", font=("Arial", 24)).pack(pady=20)
        tk.Button(self.root, text="Rozpocznij grę", font=("Arial", 14), command=self.start_game).pack(pady=10)

    def start_game(self):
        self.round = 1
        self.phase = "Planning"
        self.attacker_pool = 40
        self.selected_ronin = None
        self.selected_area = None
        self.selected_ninja_area = None
        self.ninja_markers_in_area = {area: 0 for area in AREAS + [GREEN]}
        self.wounds_on_ronin = {ronin: 0 for ronin in RONIN_STATS}
        self.eliminated_ronin = set()
        self.defender_moves = {}
        self.setup_ui()

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.label = tk.Label(self.root, text=f"Runda {self.round} — Planning (Defender)", font=("Arial", 14))
        self.label.pack()
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack()
        self.area_buttons = {}
        for area in AREAS:
            btn = tk.Button(self.board_frame, text=area, width=15, height=3,
                            command=lambda a=area: self.select_area(a))
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            self.area_buttons[area] = btn
        self.green_btn = tk.Button(self.root, text="Green (1 Ninja max)", bg="lightgreen", command=self.green_click)
        self.green_btn.pack(pady=5)
        self.ronin_frame = tk.Frame(self.root)
        self.ronin_frame.pack(pady=10)
        self.ronin_buttons = {}
        for ronin in RONIN_STATS:
            btn = tk.Button(self.ronin_frame, text=ronin, width=10,
                            command=lambda r=ronin: self.select_ronin(r))
            btn.pack(side=tk.LEFT, padx=2)
            self.ronin_buttons[ronin] = btn
        self.ninja_frame = tk.Frame(self.root)
        self.ninja_frame.pack(pady=10)
        tk.Label(self.ninja_frame, text="Rozmieszczanie Ninja: wybierz obszar").pack()
        self.ninja_entry = tk.Entry(self.ninja_frame, width=5)
        self.ninja_entry.pack()
        self.place_ninja_btn = tk.Button(self.ninja_frame, text="Dodaj Ninja", command=self.place_ninja)
        self.place_ninja_btn.pack()
        self.finish_btn = tk.Button(self.root, text="Zakończ planowanie", command=self.finish_planning)
        self.finish_btn.pack(pady=10)
        self.combat_btn = tk.Button(self.root, text="Rozpocznij fazę walki", command=self.combat_phase)
        self.combat_btn.pack(pady=10)
        self.combat_btn["state"] = tk.DISABLED

    def select_area(self, area):
        self.selected_area = area
        if self.phase == "Planning (Defender)":
            self.place_ronin()
        else:
            self.selected_ninja_area = area

    def select_ronin(self, ronin):
        self.selected_ronin = ronin

    def green_click(self):
        if self.phase == "Planning (Attacker)":
            if self.ninja_markers_in_area[GREEN] >= 1 or self.attacker_pool <= 0:
                return
            self.ninja_markers_in_area[GREEN] += 1
            self.attacker_pool -= 1
            self.green_btn["text"] = f"Green ({self.ninja_markers_in_area[GREEN]})"

    def place_ronin(self):
        if self.selected_ronin and self.selected_area and self.selected_area not in self.defender_moves:
            self.defender_moves[self.selected_area] = self.selected_ronin
            self.area_buttons[self.selected_area]["text"] += f"\n[{self.selected_ronin}]"
            self.ronin_buttons[self.selected_ronin]["state"] = tk.DISABLED
            self.selected_ronin = None
            self.selected_area = None

    def place_ninja(self):
        if not self.selected_ninja_area:
            return
        try:
            count = int(self.ninja_entry.get())
        except ValueError:
            return
        if 1 <= count <= 5 and self.attacker_pool >= count:
            self.ninja_markers_in_area[self.selected_ninja_area] += count
            self.attacker_pool -= count
            self.area_buttons[self.selected_ninja_area]["text"] += f"\nNinja: {self.ninja_markers_in_area[self.selected_ninja_area]}"

    def finish_planning(self):
        if self.phase == "Planning (Defender)":
            if len(self.defender_moves) < 7:
                return
            self.phase = "Planning (Attacker)"
            self.label["text"] = "Faza: Planning (Attacker)"
        else:
            self.phase = "Combat"
            self.label["text"] = "Faza: Combat"
            self.finish_btn["state"] = tk.DISABLED
            self.combat_btn["state"] = tk.NORMAL

    def combat_phase(self):
        summary = f"Runda {self.round} — Faza walki:\n"
        occupied_areas = 0
        self.round += 1

        for area, ronin in self.defender_moves.items():
            if ronin in self.eliminated_ronin:
                continue
            ninjas = self.ninja_markers_in_area.get(area, 0)
            if ninjas == 0:
                continue
            wounds = min(ninjas, RONIN_STATS[ronin]["vitality"] - self.wounds_on_ronin[ronin])
            self.wounds_on_ronin[ronin] += wounds
            if self.wounds_on_ronin[ronin] >= RONIN_STATS[ronin]["vitality"]:
                self.eliminated_ronin.add(ronin)
                summary += f"{ronin} zostaje wyeliminowany!\n"

        for area in AREAS:
            if self.ninja_markers_in_area[area] > 0 and area not in self.defender_moves:
                occupied_areas += 1

        summary += f"Zajęte obszary przez ninja: {occupied_areas}\n"

        if occupied_areas >= 5:
            self.end_game("Ninja zwyciężyli zajmując 5 obszarów!")
            return
        if len(self.eliminated_ronin) == 7:
            self.end_game("Ninja zwyciężyli eliminując wszystkich roninów!")
            return
        if self.attacker_pool == 0 and all(self.ninja_markers_in_area[a] == 0 for a in AREAS):
            self.end_game("Ronini zwyciężyli eliminując wszystkich ninja!")
            return
        if self.round > MAX_ROUNDS:
            self.end_game("Ronini zwyciężyli przetrwawszy 8 rund!")
            return

        self.phase = "Planning"
        self.label["text"] = f"Runda {self.round} — Planning (Defender)"
        self.combat_btn["state"] = tk.DISABLED
        self.finish_btn["state"] = tk.NORMAL
        self.reset_for_next_round()

    def end_game(self, message):
        if messagebox.askyesno("Koniec gry", f"{message}\nCzy chcesz zagrać ponownie?"):
            self.start_game()
        else:
            self.main_menu()

    def reset_for_next_round(self):
        self.defender_moves = {}
        for ronin in self.ronin_buttons:
            if ronin not in self.eliminated_ronin:
                self.ronin_buttons[ronin]["state"] = tk.NORMAL
        for area in AREAS:
            self.area_buttons[area]["text"] = area

if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
print('Hello world!')