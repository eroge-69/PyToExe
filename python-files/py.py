import os
import csv
import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

TOOL_NAME = "PES 2017 Rosters To PlayerAssignments"
AUTHOR = "by Mohamed Alaa"
OUTPUT_FILENAME = "PlayerAssignmentsData.csv"

def convert_csv(filepath):
    try:
        with open(filepath, 'r', newline='', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile, delimiter=';')
            rows = list(reader)

        output_header = [
            'Id', 'IdPlayer', 'IdTeam', 'ShirtNumber', 'Position',
            'Captain', 'Short Free Kick', 'Long Free Kick',
            'Right Corner', 'Left Corner', 'Penalty', 'Value1'
        ]

        output_rows = []
        index = 1

        for row in rows:
            team_id = row['Id']
            total_players = int(row['TotalPlayers'])

            player_ids = [row[f'Player{i+1}'] for i in range(40)]
            shirt_numbers = [row[f'Number{i+1}'] for i in range(40)]
            values = [row.get(f'Value{i+1}', '0') for i in range(40)]

            for i in range(total_players):
                player_id = player_ids[i]
                if player_id == '0':
                    continue

                output_rows.append([
                    index, player_id, team_id, shirt_numbers[i], i,
                    0, 0, 0, 0, 0, 0, values[i]
                ])
                index += 1

        output_dir = os.path.dirname(filepath)
        output_path = os.path.join(output_dir, OUTPUT_FILENAME)

        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile, delimiter=';')
            writer.writerow(output_header)
            writer.writerows(output_rows)

        return output_path

    except Exception as e:
        messagebox.showerror("Error", f"❌ An error occurred:\n{e}")
        return None

def run_gui():
    app = TkinterDnD.Tk()
    app.title(TOOL_NAME)
    app.geometry("600x400")
    style = ttk.Style("cosmo")
    style.master = app

    title_label = ttk.Label(app, text=TOOL_NAME, font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=(15, 5))

    author_label = ttk.Label(app, text=AUTHOR, font=("Segoe UI", 10), foreground="#666")
    author_label.pack()

    status_label = ttk.Label(app, text="", font=("Segoe UI", 11))
    status_label.pack(pady=10)

    def handle_drop(event):
        filepath = event.data.strip().strip('{}')
        if os.path.isfile(filepath) and filepath.lower().endswith('.csv'):
            status_label.config(text="⏳ Converting...", foreground="blue")
            output = convert_csv(filepath)
            if output:
                status_label.config(text=f"✅ Saved as '{OUTPUT_FILENAME}'", foreground="green")
        else:
            status_label.config(text="❌ Please drop a valid .csv file", foreground="red")

    drop_frame = tk.Frame(app, width=500, height=200, bg="#e9ecef", relief="groove", bd=2)
    drop_frame.pack(pady=30)
    drop_frame.pack_propagate(False)

    drop_label = ttk.Label(
        drop_frame,
        text='🗂️ Drag and Drop "Rosters" File here that exported from OptionFile',
        font=("Segoe UI", 13),
        anchor="center",
        wraplength=450,
        justify="center"
    )
    drop_label.pack(expand=True)

    drop_frame.drop_target_register(DND_FILES)
    drop_frame.dnd_bind('<<Drop>>', handle_drop)

    ttk.Label(
        app,
        text=f"The output file will always be saved as '{OUTPUT_FILENAME}' in the same folder.",
        font=("Segoe UI", 9),
        foreground="#555"
    ).pack()

    app.mainloop()

if __name__ == "__main__":
    run_gui()
