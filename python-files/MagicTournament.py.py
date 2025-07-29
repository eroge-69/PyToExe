import tkinter as tk
from tkinter import messagebox, ttk
import random

class Player:
    def __init__(self, name):
        self.name = name
        self.match_wins = 0
        self.firsts = 0
        self.opponents = set()
        self.games_won = 0
        self.games_played = 0

    def game_win_percentage(self):
        return (self.games_won / self.games_played*100) if self.games_played > 0 else 0.0

class Match:
    def __init__(self, player1, player2, first_player):
        self.player1 = player1
        self.player2 = player2
        self.first_player = first_player
        self.scores = {player1: 0, player2: 0}
        self.completed = False

class TournamentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Magic Tournament Manager")

        self.players = []
        self.round = 0
        self.matches = []
        self.completed_rounds = []
        self.current_match_window = None

        self.setup_ui()

    def setup_ui(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        tk.Label(self.frame, text="Player Name:").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(self.frame)
        self.name_entry.grid(row=0, column=1, sticky="ew")
        tk.Button(self.frame, text="Add Player", command=self.add_player).grid(row=0, column=2, padx=5)

        self.player_listbox = tk.Listbox(self.frame, height=10, width=40)
        self.player_listbox.grid(row=1, column=0, columnspan=3, pady=5, sticky="ew")

        tk.Button(self.frame, text="Start Round", command=self.start_round).grid(row=2, column=0, pady=5)
        tk.Button(self.frame, text="Show Standings", command=self.show_standings).grid(row=2, column=1, pady=5)
        tk.Button(self.frame, text="Reset Tournament", command=self.reset_tournament).grid(row=2, column=2, pady=5)

        self.frame.columnconfigure(1, weight=1)

    def add_player(self):
        name = self.name_entry.get().strip()
        if name and name not in [p.name for p in self.players]:
            self.players.append(Player(name))
            self.player_listbox.insert(tk.END, name)
            self.name_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Invalid", "Name is empty or already added.")

    def reset_tournament(self):
        if self.current_match_window:
            self.current_match_window.destroy()
            self.current_match_window = None
        self.players.clear()
        self.player_listbox.delete(0, tk.END)
        self.round = 0
        self.matches.clear()
        self.completed_rounds.clear()
        messagebox.showinfo("Reset", "Tournament has been reset.")

    def start_round(self):
        if len(self.players) < 2:
            messagebox.showerror("Not Enough Players", "Add at least 2 players.")
            return

        if self.current_match_window and not all(m.completed for m in self.matches):
            messagebox.showwarning("Round Incomplete", "Finish all matches before starting a new round.")
            return

        self.round += 1
        raw_pairs = self.swiss_pairings()
        if not raw_pairs:
            messagebox.showinfo("No Pairings", "No valid pairings available. Tournament might be over.")
            self.round -= 1
            return

        self.matches = []
        self.current_match_window = tk.Toplevel(self.root)
        self.current_match_window.title(f"Round {self.round} - Best of 3")

        tk.Label(self.current_match_window, text=f"Round {self.round} Pairings (Best of 3)").pack(pady=5)

        for p1, p2 in raw_pairs:
            first = self.choose_first_player(p1, p2)
            match = Match(p1, p2, first)
            self.matches.append(match)

            frame = tk.Frame(self.current_match_window, bd=2, relief=tk.SUNKEN, padx=5, pady=5)
            frame.pack(pady=4, fill=tk.X)

            status_var = tk.StringVar(value=f"{p1.name} vs {p2.name} — {first.name} goes first")
            label = tk.Label(frame, textvariable=status_var)
            label.pack(anchor=tk.W)

            def make_result_callback(match, result_box, status_var):
                def callback(event):
                    if match.completed:
                        return
                    try:
                        score1, score2 = map(int, result_box.get().split('-'))
                    except ValueError:
                        return

                    match.completed = True
                    match.scores[match.player1] = score1
                    match.scores[match.player2] = score2

                    # Update match wins
                    if score1 > score2:
                        match.player1.match_wins += 1
                        status_var.set(f"{match.player1.name} wins {score1}-{score2}")
                    elif score2 > score1:
                        match.player2.match_wins += 1
                        status_var.set(f"{match.player2.name} wins {score2}-{score1}")
                    else:
                        status_var.set(f"Draw: {score1}-{score2}")

                    # Update games won/played
                    match.player1.games_won += score1
                    match.player2.games_won += score2
                    match.player1.games_played += (score1 + score2)
                    match.player2.games_played += (score1 + score2)

                return callback

            result_box = ttk.Combobox(frame, values=["2-0", "2-1", "1-2", "0-2", "1-1", "0-0"], width=6)
            result_box.pack(pady=2)
            result_box.bind("<<ComboboxSelected>>", make_result_callback(match, result_box, status_var))

        self.completed_rounds.append(self.matches)

    def choose_first_player(self, p1, p2):
        if p1.firsts < p2.firsts:
            chosen = p1
        elif p2.firsts < p1.firsts:
            chosen = p2
        else:
            chosen = random.choice([p1, p2])
        chosen.firsts += 1
        return chosen

    def show_standings(self):
    # Calculate Opponents' Game Win % (OGWP)
        ogwp_map = {}
        for player in self.players:
            if not player.opponents:
                ogwp_map[player.name] = 0.0
            else:
                total_ogwp = 0
                for opp_name in player.opponents:
                    opp = next((p for p in self.players if p.name == opp_name), None)
                    if opp:
                        total_ogwp += opp.game_win_percentage()
                ogwp_map[player.name] = total_ogwp / len(player.opponents) if player.opponents else 0.0

        standings = sorted(
            self.players,
            key=lambda p: (
                -p.match_wins,
                -p.game_win_percentage(),
                -ogwp_map.get(p.name, 0),
                -p.firsts,
                p.name
            )
        )

    # Create new window for standings table
        win = tk.Toplevel(self.root)
        win.title("Standings")

        columns = ("Name", "Match Wins", "Game Win %", "Opp GW %", "Firsts")
        tree = ttk.Treeview(win, columns=columns, show="headings", height=15)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Define headings and column widths
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER, width=100)

    # Insert standings rows
        for p in standings:
            tree.insert(
                "",
                "end",
                values=(
                    p.name,
                    p.match_wins,
                    f"{p.game_win_percentage():.3f}",
                    f"{ogwp_map.get(p.name, 0):.3f}",
                    p.firsts
                )
            )


    def swiss_pairings(self):
        sorted_players = sorted(self.players, key=lambda p: (-p.match_wins, p.firsts, p.name))
        used = set()
        pairings = []

        print(f"--- Round {self.round} Swiss Pairings ---")
        print("Players sorted:", [p.name for p in sorted_players])

        for i, p1 in enumerate(sorted_players):
            if p1 in used:
                continue

            opponent = None
            for p2 in sorted_players[i+1:]:
                if p2 not in used and p2.name not in p1.opponents:
                    opponent = p2
                    break

            if not opponent:
                for p2 in sorted_players[i+1:]:
                    if p2 not in used:
                        opponent = p2
                        break

            if opponent:
                pairings.append((p1, opponent))
                used.add(p1)
                used.add(opponent)
                p1.opponents.add(opponent.name)
                opponent.opponents.add(p1.name)
                print(f"Paired {p1.name} with {opponent.name}")
            else:
                print(f"No opponent found for {p1.name}")

        if len(self.players) % 2 == 1 and len(used) < len(self.players):
            for p in sorted_players:
                if p not in used:
                    p.match_wins += 1
                    messagebox.showinfo("Bye", f"{p.name} gets a bye and 1 match win.")
                    print(f"{p.name} gets a bye")
                    break

        print(f"Total pairs: {len(pairings)}")
        return pairings

if __name__ == "__main__":
    root = tk.Tk()
    app = TournamentApp(root)
    root.mainloop()
