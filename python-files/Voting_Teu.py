import ctypes
import tkinter as tk
from tkinter import messagebox

ctypes.windll.shcore.SetProcessDpiAwareness(1)

Marks = [3.5, 2.5, 1.5, -0.5]
Tiers = ["S", "A", "B", "D"]

def calculate():
    try:
        Vote = [int(entry.get()) for entry in entries]

        if sum(Vote) == 0:
            messagebox.showerror("Errot", "The sum of the number of votes cannot be 0")
            return

        max_vote = max(Vote)
        min_vote = min(Vote)
        most_indices = [i for i, v in enumerate(Vote) if v == max_vote]
        least_indices = [i for i, v in enumerate(Vote) if v == min_vote]

        FinalScore = 0
        for i in range(4):
            if i in most_indices:
                weight = 1.175 if len(most_indices) > 1 else 1.35
            elif i in least_indices:
                weight = 0.775 if len(least_indices) > 1 else 0.65
            else:
                weight = 1
            FinalScore += Marks[i] * Vote[i] * weight

        FinalScore /= sum(Vote)
        FinalScore = round(FinalScore, 4)

        if FinalScore >= 3:
            tier = "S Tier"
        elif FinalScore >= 2:
            tier = "A Tier"
        elif FinalScore >= 1:
            tier = "B Tier"
        else:
            tier = "Dawg"
        result_label.config(text=f"Final Score: {FinalScore}  →  {tier}", fg="#87CEEB")

    except ValueError:
        messagebox.showerror("Error", "Please make sure the number of votes is entered correctly")

root = tk.Tk()
root.title("Tier Voting Calculator")
root.geometry("1024x768")
root.config(bg="#191f2a")

title_label = tk.Label(root, text="Tier Voting Calculator", font=("Arial", 20, "bold"), fg="white", bg="#191f2a")
title_label.pack(pady=15, expand=True) 

frame = tk.Frame(root, bg="#191f2a")
frame.pack(expand=True)

entries = []
for i, tier in enumerate(Tiers):
    tk.Label(frame, text=f"{tier} Tier Votes:", font=("Arial", 14), fg="white", bg="#191f2a").grid(row=i, column=0, padx=15, pady=10, sticky="e")
    e = tk.Entry(frame, font=("Arial", 14), width=10)
    e.grid(row=i, column=1, padx=15, pady=10)
    entries.append(e)

calculate_botton = tk.Button(root, text="Calculate", font=("Arial", 14, "bold"), bg="#006bb1", fg="white", width=15, command=calculate)
calculate_botton.pack(pady=15)

result_label = tk.Label(root, text="", font=("Arial", 16, "bold"), bg="#191f2a")
result_label.pack(pady=15, expand=True)

root.mainloop()
