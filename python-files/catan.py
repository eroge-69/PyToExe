import tkinter as tk
from tkinter import ttk

class CatanCardTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Catan Cards Tracker")

        self.resources = [
            ("Wood", "🌲"),
            ("Brick", "🧱"),
            ("Sheep", "🐑"),
            ("Wheat", "🌾"),
            ("Ore", "⛰️")
        ]

        self.players = ["You", "Opponent"]

        self.counts = {player: {resource: 0 for resource, _ in self.resources} for player in self.players}
        self.builds = ["Roads", "Settlements", "Cities", "Dev Cards"]
        self.build_counts = {player: {build: 0 for build in self.builds} for player in self.players}

        self.frames = {}

        self.create_ui()

    def create_ui(self):
        for p_idx, player in enumerate(self.players):
            player_frame = ttk.LabelFrame(self.root, text=player, padding="10")
            player_frame.grid(row=0, column=p_idx, padx=10, pady=10, sticky="n")

            # Resource trackers
            for idx, (resource, icon) in enumerate(self.resources):
                frame = ttk.Frame(player_frame, padding="5")
                frame.grid(row=idx, column=0, sticky="w")
                self.frames[(player, resource)] = frame

                label = ttk.Label(frame, text=f"{icon} {resource}", width=12)
                label.pack(side="left")

                minus_btn = ttk.Button(frame, text="-", width=2,
                                       command=lambda p=player, r=resource: self.decrement(p, r))
                minus_btn.pack(side="left")

                count_label = ttk.Label(frame, text="0", width=4)
                count_label.pack(side="left")

                plus_btn = ttk.Button(frame, text="+", width=2,
                                      command=lambda p=player, r=resource: self.increment(p, r))
                plus_btn.pack(side="left")

                frame.count_label = count_label

            # Builds
            builds_frame = ttk.LabelFrame(player_frame, text="Builds", padding="5")
            builds_frame.grid(row=len(self.resources), column=0, pady=5, sticky="w")

            for b_idx, build in enumerate(self.builds):
                b_frame = ttk.Frame(builds_frame, padding="3")
                b_frame.grid(row=b_idx, column=0, sticky="w")
                self.frames[(player, build)] = b_frame

                b_label = ttk.Label(b_frame, text=build, width=12)
                b_label.pack(side="left")

                minus_btn = ttk.Button(b_frame, text="-", width=2,
                                       command=lambda p=player, b=build: self.decrement_build(p, b))
                minus_btn.pack(side="left")

                count_label = ttk.Label(b_frame, text="0", width=4)
                count_label.pack(side="left")

                plus_btn = ttk.Button(b_frame, text="+", width=2,
                                      command=lambda p=player, b=build: self.increment_build(p, b))
                plus_btn.pack(side="left")

                b_frame.count_label = count_label

    def increment(self, player, resource):
        self.counts[player][resource] += 1
        self.update_count(player, resource)

    def decrement(self, player, resource):
        if self.counts[player][resource] > 0:
            self.counts[player][resource] -= 1
            self.update_count(player, resource)

    def update_count(self, player, resource):
        frame = self.frames[(player, resource)]
        frame.count_label.config(text=str(self.counts[player][resource]))

    def increment_build(self, player, build):
        self.build_counts[player][build] += 1
        self.update_build_count(player, build)

    def decrement_build(self, player, build):
        if self.build_counts[player][build] > 0:
            self.build_counts[player][build] -= 1
            self.update_build_count(player, build)

    def update_build_count(self, player, build):
        frame = self.frames[(player, build)]
        frame.count_label.config(text=str(self.build_counts[player][build]))


if __name__ == "__main__":
    root = tk.Tk()
    app = CatanCardTracker(root)
    root.mainloop()
