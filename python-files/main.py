import tkinter as tk
from tkinter import messagebox, scrolledtext
import random

class Team
    def __init__(self, name, player1, player2)
        self.name = name
        self.player1 = player1
        self.player2 = player2
        self.points = 0
        self.active = True
        self.opponents = []

class Match
    def __init__(self, team1, team2)
        self.team1 = team1
        self.team2 = team2
        self.team1_score = [, ]  # index 0 = player1, index 1 = player2
        self.team2_score = [, ]

class TournamentApp
    def __init__(self, root)
        self.root = root
        self.root.title(2v2 Turnier-Manager)
        self.teams = []
        self.round = 1
        self.matches = []
        self.current_frame = None
        self.setup_team_entry()

    def setup_team_entry(self)
        self.clear_frame()
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        tk.Label(frame, text=Teamname).grid(row=0, column=0)
        tk.Label(frame, text=Spieler 1).grid(row=1, column=0)
        tk.Label(frame, text=Spieler 2).grid(row=2, column=0)

        team_name = tk.Entry(frame)
        player1 = tk.Entry(frame)
        player2 = tk.Entry(frame)

        team_name.grid(row=0, column=1)
        player1.grid(row=1, column=1)
        player2.grid(row=2, column=1)

        tk.Button(frame, text=Team hinzufügen, command=lambda self.add_team(team_name, player1, player2)).grid(row=3, column=0, columnspan=2, pady=5)
        tk.Button(frame, text=Turnier starten, command=self.start_tournament).grid(row=4, column=0, columnspan=2)

        self.team_display = tk.Text(frame, width=40, height=10, state=disabled)
        self.team_display.grid(row=5, column=0, columnspan=2, pady=10)

        self.current_frame = frame

    def add_team(self, name_entry, p1_entry, p2_entry)
        name, p1, p2 = name_entry.get(), p1_entry.get(), p2_entry.get()
        if not name or not p1 or not p2
            messagebox.showwarning(Fehler, Alle Felder müssen ausgefüllt werden.)
            return
        self.teams.append(Team(name, p1, p2))
        name_entry.delete(0, tk.END)
        p1_entry.delete(0, tk.END)
        p2_entry.delete(0, tk.END)
        self.update_team_display()

    def update_team_display(self)
        self.team_display.config(state=normal)
        self.team_display.delete(1.0, tk.END)
        for team in self.teams
            self.team_display.insert(tk.END, f{team.name} {team.player1}, {team.player2}n)
        self.team_display.config(state=disabled)

    def start_tournament(self)
        if len(self.teams)  2
            messagebox.showwarning(Fehler, Mindestens zwei Teams benötigt.)
            return
        self.show_round()

    def show_round(self)
        self.clear_frame()
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        active_teams = [team for team in self.teams if team.active]
        random.shuffle(active_teams)
        self.matches = []

        for i in range(0, len(active_teams), 2)
            if i + 1 = len(active_teams)
                break
            team1 = active_teams[i]
            team2 = active_teams[i + 1]
            team1.opponents.append(team2)
            team2.opponents.append(team1)
            match = Match(team1, team2)
            self.matches.append(match)

        for match in self.matches
            match_frame = tk.LabelFrame(frame, text=f{match.team1.name} vs {match.team2.name}, padx=5, pady=5)
            match_frame.pack(padx=10, pady=10, fill=x)

            for index, (p1, p2) in enumerate([(match.team1.player1, match.team2.player1), (match.team1.player2, match.team2.player2)])
                subframe = tk.Frame(match_frame)
                subframe.pack(pady=2)
                tk.Label(subframe, text=f{p1} vs {p2}).pack(side=left)
                tk.Button(subframe, text=f{p1} gewinnt, command=lambda m=match, i=index self.score_match(m, i, t1)).pack(side=left)
                tk.Button(subframe, text=f{p2} gewinnt, command=lambda m=match, i=index self.score_match(m, i, t2)).pack(side=left)
                tk.Button(subframe, text=Unentschieden, command=lambda m=match, i=index self.score_match(m, i, draw)).pack(side=left)

            drop_btn = tk.Button(match_frame, text=Team AUSSTEIGEN lassen, command=lambda m=match self.drop_team(m, frame))
            drop_btn.pack(pady=5)

        tk.Button(frame, text=Nächste Runde, command=self.next_round).pack(pady=10)
        tk.Button(frame, text=Turnier beenden, command=self.show_results).pack()

        self.live_result = scrolledtext.ScrolledText(frame, width=60, height=10)
        self.live_result.pack(pady=10)
        self.update_live_standings()

        self.current_frame = frame

    def score_match(self, match, index, result)
        prev_result = match.team1_score[index], match.team2_score[index]

        # Falls identisch – tue nichts
        if ((result == t1 and prev_result == (win, loss)) or
            (result == t2 and prev_result == (loss, win)) or
            (result == draw and prev_result == (draw, draw)))
            return

        # Punkte zurücknehmen
        if prev_result[0] == win
            match.team1.points -= 3 if self.is_priority(match.team1, index) else 2
        elif prev_result[0] == draw
            match.team1.points -= 1
        if prev_result[1] == win
            match.team2.points -= 3 if self.is_priority(match.team2, index) else 2
        elif prev_result[1] == draw
            match.team2.points -= 1

        # Neues Ergebnis
        if result == t1
            match.team1_score[index] = win
            match.team2_score[index] = loss
            match.team1.points += 3 if self.is_priority(match.team1, index) else 2
        elif result == t2
            match.team1_score[index] = loss
            match.team2_score[index] = win
            match.team2.points += 3 if self.is_priority(match.team2, index) else 2
        elif result == draw
            match.team1_score[index] = draw
            match.team2_score[index] = draw
            match.team1.points += 1
            match.team2.points += 1

        self.update_live_standings()

    def is_priority(self, team, index)
        # index 0 = player1, 1 = player2
        if team.player1 == team.player2
            return False
        if index == 0
            return self.round % 2 == 1
        else
            return self.round % 2 == 0

    def drop_team(self, match, frame)
        match.team1.active = False
        match.team2.active = True
        match.team2.points += 3 if self.round % 2 == 1 else 2
        match.team2.points += 3 if self.round % 2 == 0 else 2
        self.show_round()

    def next_round(self)
        self.round += 1
        self.show_round()

    def show_results(self)
        self.clear_frame()
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        sorted_teams = sorted(self.teams, key=lambda t t.points, reverse=True)

        result = scrolledtext.ScrolledText(frame, width=60, height=20)
        result.pack()
        result.insert(tk.END, Abschlusstabellenn)
        for i, team in enumerate(sorted_teams, start=1)
            status =  if team.active else (Ausgeschieden)
            result.insert(tk.END, f{i}. {team.name} - {team.points} Punkte {status}n)

        self.current_frame = frame

    def update_live_standings(self)
        self.live_result.delete(1.0, tk.END)
        sorted_teams = sorted(self.teams, key=lambda t t.points, reverse=True)
        for i, team in enumerate(sorted_teams, start=1)
            status =  if team.active else (Ausgeschieden)
            self.live_result.insert(tk.END, f{i}. {team.name} - {team.points} Punkte {status}n)

    def clear_frame(self)
        if self.current_frame
            self.current_frame.destroy()

if __name__ == __main__
    root = tk.Tk()
    app = TournamentApp(root)
    root.mainloop()
