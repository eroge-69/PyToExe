python --versionimport tkinter as tk
from tkinter import ttk, messagebox

class Team:
    def __init__(self, name):
        self.name = name
        self.points = 0
        self.matches_played = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.goals_for = 0
        self.goals_against = 0

    def update_stats(self, goals_for, goals_against):
        self.matches_played += 1
        self.goals_for += goals_for
        self.goals_against += goals_against
        if goals_for > goals_against:
            self.points += 3
            self.wins += 1
        elif goals_for == goals_against:
            self.points += 1
            self.draws += 1
        else:
            self.losses += 1

    def goal_difference(self):
        return self.goals_for - self.goals_against

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Super 12 Tournament Manager")
        self.geometry("750x550")

        self.groups = {
            "A": ["A1", "A2", "A3"],
            "B": ["B1", "B2", "B3"],
            "C": ["C1", "C2", "C3"],
            "D": ["D1", "D2", "D3"]
        }

        # Internal team tracking: group → position → Team
        self.teams = {g: {pos: Team(pos) for pos in pos_list} for g, pos_list in self.groups.items()}
        # Custom name mapping: group → position → custom name
        self.named_teams = {g: {pos: pos for pos in pos_list} for g, pos_list in self.groups.items()}

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, expand=True, fill="both")

        self.frame_name_teams = tk.Frame(self.notebook)
        self.frame_matches = tk.Frame(self.notebook)
        self.frame_rankings = tk.Frame(self.notebook)

        self.notebook.add(self.frame_name_teams, text="Name Teams")
        self.notebook.add(self.frame_matches, text="Enter Matches")
        self.notebook.add(self.frame_rankings, text="Group Rankings")

        self.create_name_teams_tab()
        self.create_match_tab()
        self.create_rankings_tab()

    def create_name_teams_tab(self):
        tk.Label(self.frame_name_teams, text="Select Group:").pack()
        self.name_group_var = tk.StringVar()
        self.name_group_dropdown = ttk.Combobox(self.frame_name_teams, textvariable=self.name_group_var, state="readonly")
        self.name_group_dropdown['values'] = list(self.groups.keys())
        self.name_group_dropdown.pack()
        self.name_group_dropdown.bind("<<ComboboxSelected>>", self.show_team_name_entries)

        self.team_name_entries = {}

    def show_team_name_entries(self, event=None):
        for widget in self.frame_name_teams.winfo_children()[2:]:
            widget.destroy()

        group = self.name_group_var.get()
        if group:
            self.team_name_entries = {}
            for pos in self.groups[group]:
                frame = tk.Frame(self.frame_name_teams)
                frame.pack(pady=2)
                tk.Label(frame, text=f"{pos}: ").pack(side=tk.LEFT)
                entry = tk.Entry(frame)
                entry.pack(side=tk.LEFT)
                entry.insert(0, self.named_teams[group][pos])
                self.team_name_entries[pos] = entry
            tk.Button(self.frame_name_teams, text="Save Names", command=self.save_team_names).pack(pady=10)

    def save_team_names(self):
        group = self.name_group_var.get()
        for pos, entry in self.team_name_entries.items():
            name = entry.get().strip()
            if name:
                self.named_teams[group][pos] = name
                self.teams[group][pos].name = name
        messagebox.showinfo("Saved", f"Team names for Group {group} updated.")

    def create_match_tab(self):
        tk.Label(self.frame_matches, text="Select Group:").pack()
        self.group_var = tk.StringVar()
        self.group_dropdown = ttk.Combobox(self.frame_matches, textvariable=self.group_var, state="readonly")
        self.group_dropdown['values'] = list(self.groups.keys())
        self.group_dropdown.pack()
        self.group_dropdown.bind("<<ComboboxSelected>>", self.update_team_dropdowns)

        self.team1_var = tk.StringVar()
        self.team2_var = tk.StringVar()

        tk.Label(self.frame_matches, text="Team 1:").pack()
        self.team1_dropdown = ttk.Combobox(self.frame_matches, textvariable=self.team1_var, state="readonly")
        self.team1_dropdown.pack()

        tk.Label(self.frame_matches, text="Team 1 Score:").pack()
        self.team1_score_entry = tk.Entry(self.frame_matches)
        self.team1_score_entry.pack()

        tk.Label(self.frame_matches, text="Team 2:").pack()
        self.team2_dropdown = ttk.Combobox(self.frame_matches, textvariable=self.team2_var, state="readonly")
        self.team2_dropdown.pack()

        tk.Label(self.frame_matches, text="Team 2 Score:").pack()
        self.team2_score_entry = tk.Entry(self.frame_matches)
        self.team2_score_entry.pack()

        tk.Button(self.frame_matches, text="Add Match", command=self.add_match).pack(pady=10)

    def update_team_dropdowns(self, event=None):
        group = self.group_var.get()
        if group:
            team_names = list(self.named_teams[group].values())
            self.team1_dropdown['values'] = team_names
            self.team2_dropdown['values'] = team_names

    def add_match(self):
        group = self.group_var.get()
        team1_name = self.team1_var.get()
        team2_name = self.team2_var.get()

        try:
            score1 = int(self.team1_score_entry.get())
            score2 = int(self.team2_score_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Scores must be integers.")
            return

        if team1_name == team2_name:
            messagebox.showerror("Invalid Match", "Teams must be different.")
            return

        # Find internal position keys
        pos1 = pos2 = None
        for pos, name in self.named_teams[group].items():
            if name == team1_name:
                pos1 = pos
            if name == team2_name:
                pos2 = pos

        if not pos1 or not pos2:
            messagebox.showerror("Team Error", "One or both team names not found.")
            return

        t1 = self.teams[group][pos1]
        t2 = self.teams[group][pos2]

        t1.update_stats(score1, score2)
        t2.update_stats(score2, score1)

        self.team1_score_entry.delete(0, tk.END)
        self.team2_score_entry.delete(0, tk.END)

        messagebox.showinfo("Match Added", f"{team1_name} {score1} - {score2} {team2_name} (Group {group})")

    def create_rankings_tab(self):
        tk.Label(self.frame_rankings, text="Select Group to Show Rankings:").pack()
        self.rank_group_var = tk.StringVar()
        self.rank_group_dropdown = ttk.Combobox(self.frame_rankings, textvariable=self.rank_group_var, state="readonly")
        self.rank_group_dropdown['values'] = list(self.groups.keys())
        self.rank_group_dropdown.pack()
        tk.Button(self.frame_rankings, text="Show Rankings", command=self.show_rankings).pack(pady=10)

        self.rankings_text = tk.Text(self.frame_rankings, height=20, width=90)
        self.rankings_text.pack()

    def show_rankings(self):
        group = self.rank_group_var.get()
        if group not in self.teams:
            return

        teams = list(self.teams[group].values())
        teams.sort(key=lambda t: (t.points, t.goal_difference(), t.goals_for), reverse=True)

        self.rankings_text.delete(1.0, tk.END)
        self.rankings_text.insert(tk.END, f"Rankings for Group {group}\n")
        self.rankings_text.insert(tk.END, "Pos | Team Name      | MP | W | D | L | GF | GA | GD | Pts\n")
        self.rankings_text.insert(tk.END, "-" * 70 + "\n")
        for i, team in enumerate(teams, 1):
            self.rankings_text.insert(tk.END,
                f"{i:>3} | {team.name:<15} | {team.matches_played:^2} | {team.wins:^2} | {team.draws:^2} | {team.losses:^2} | {team.goals_for:^3} | {team.goals_against:^3} | {team.goal_difference():^3} | {team.points:^3}\n")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
