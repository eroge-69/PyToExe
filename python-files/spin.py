import tkinter as tk
from tkinter import messagebox
import random

# === Leaderboard initiële lijst leeg ===
leaderboard = []
scores = {}
current_index = 0

# === Rad configuratie ===
num_sectors = 12
colors = ["#4CAF50", "#FFD700", "#E53935"]  # groen, geel, rood

# === Tkinter setup ===
root = tk.Tk()
root.title("🎡 Spinwheel met Handmatige Punten")
root.geometry("1000x700")
root.configure(bg="white")

# Frame voor rad en leaderboard
frame = tk.Frame(root, bg="white")
frame.pack(expand=True, fill="both", padx=20, pady=20)

# Canvas voor rad
canvas_size = 500
canvas = tk.Canvas(frame, width=canvas_size, height=canvas_size, bg="white", highlightthickness=0)
canvas.grid(row=0, column=0, padx=(50,20), pady=20)

# Leaderboard frame
leaderboard_frame = tk.Frame(frame, bg="#f0f0f0", bd=2, relief="raised")
leaderboard_frame.grid(row=0, column=1, padx=(50,50), pady=20, sticky="n")

# Leaderboard label
score_label = tk.Label(leaderboard_frame, text="🏆 Leaderboard", font=("Helvetica", 16, "bold"),
                       fg="#333333", bg="#f0f0f0", justify="left", padx=15, pady=15)
score_label.pack()

# Entry voor naam toevoegen
entry_frame = tk.Frame(leaderboard_frame, bg="#f0f0f0")
entry_frame.pack(pady=10)
name_entry = tk.Entry(entry_frame, font=("Helvetica", 14))
name_entry.pack(side="left")
def add_name():
    name = name_entry.get().strip()
    if name and name not in leaderboard:
        leaderboard.append(name)
        scores[name] = 0
        name_entry.delete(0, "end")
        update_all()
add_button = tk.Button(entry_frame, text="Toevoegen", command=add_name)
add_button.pack(side="left", padx=5)

# Knop om alle namen te wissen
def clear_leaderboard():
    global leaderboard, current_index, scores
    leaderboard = []
    scores = {}
    current_index = 0
    update_all()
clear_button = tk.Button(leaderboard_frame, text="Wis alle namen", command=clear_leaderboard, bg="#FF5555", fg="white")
clear_button.pack(pady=10)

# === Functies Leaderboard ===
def show_points(event):
    widget = event.widget
    clicked_name = widget.cget("text").split(" - ")[0].replace("➡ ", "")
    points = scores.get(clicked_name, 0)
    messagebox.showinfo("Punten", f"{clicked_name} heeft {points} punten!")

def update_leaderboard():
    for widget in leaderboard_frame.winfo_children():
        if hasattr(widget, "is_player_label") and widget.is_player_label:
            widget.destroy()
    sorted_board = sorted(leaderboard, key=lambda x: scores.get(x,0), reverse=True)
    text = "🏆 Leaderboard\n\n"
    score_label.config(text=text)
    for i, player in enumerate(sorted_board):
        pointer = "➡ " if i == sorted_board.index(leaderboard[current_index % len(leaderboard)]) else ""
        player_text = f"{pointer}{player} - {scores[player]} pts"
        lbl = tk.Label(leaderboard_frame, text=player_text, font=("Helvetica", 14), bg="#f0f0f0", anchor="w")
        lbl.pack(fill="x", padx=10)
        lbl.bind("<Button-1>", show_points)
        lbl.is_player_label = True

def add_points(player, amount):
    scores[player] += amount
    update_all()

# Frame voor puntenknoppen
points_frame = tk.Frame(leaderboard_frame, bg="#f0f0f0")
points_frame.pack(pady=10)

def create_points_buttons():
    for player in leaderboard:
        frame = tk.Frame(points_frame, bg="#f0f0f0")
        frame.pack(pady=2)
        tk.Label(frame, text=player, font=("Helvetica", 12), width=12, anchor="w", bg="#f0f0f0").pack(side="left")
        tk.Button(frame, text="+100", command=lambda p=player: add_points(p, 100), bg="#E53935", fg="white").pack(side="left", padx=2)
        tk.Button(frame, text="+50", command=lambda p=player: add_points(p, 50), bg="#FFD700").pack(side="left", padx=2)
        tk.Button(frame, text="+25", command=lambda p=player: add_points(p, 25), bg="#4CAF50", fg="white").pack(side="left", padx=2)

def refresh_points_buttons():
    for widget in points_frame.winfo_children():
        widget.destroy()
    create_points_buttons()

def update_all():
    update_leaderboard()
    refresh_points_buttons()

# === Rad tekenen ===
radius = canvas_size // 2 - 30
center = canvas_size // 2
angle = 0
def draw_wheel(angle=0):
    canvas.delete("wheel")
    sector_colors = [colors[i % len(colors)] for i in range(num_sectors)]
    for i in range(num_sectors):
        start = (360 / num_sectors) * i + angle
        extent = 360 / num_sectors
        canvas.create_arc(center - radius, center - radius,
                          center + radius, center + radius,
                          start=start, extent=extent,
                          fill=sector_colors[i], outline="white", width=3, tags="wheel")
    canvas.create_oval(center - radius - 5, center - radius - 5,
                       center + radius + 5, center + radius + 5,
                       outline="#222222", width=5, tags="wheel")

def draw_pointer():
    canvas.delete("pointer")
    canvas.create_polygon(center - 18, center - radius - 30,
                          center + 18, center - radius - 30,
                          center, center - radius - 2,
                          fill="#222222", outline="#000000", width=2, tags="pointer")

# === Spatiebalk spin ===
spinning = False
speed = 0

def animate():
    global angle, speed, spinning
    if spinning:
        angle += speed
        draw_wheel(angle)
        draw_pointer()
        speed *= 0.97
        if speed > 0.05:
            root.after(20, animate)
        else:
            spinning = False

def spin_wheel(event=None):
    global spinning, speed
    if spinning:
        return
    spinning = True
    speed = random.uniform(12, 18)
    animate()

# === Start UI ===
root.bind("<space>", spin_wheel)
draw_wheel()
draw_pointer()
update_all()
root.mainloop()
