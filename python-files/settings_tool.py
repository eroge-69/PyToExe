import json
import tkinter as tk
from tkinter import ttk

settings_path = "settings.json"

def save():
    settings = {
        "humour_level": humour.get(),
        "drama_intensity": drama.get(),
        "max_rivals": rivals.get(),
        "auto_run": auto_run.get(),
        "news_type": news_type.get(),
        "save_history": history.get(),
        "language_tone": tone.get(),
        "allow_memes": memes.get(),
        "team_orders": team.get(),
        "experimental_mode": expt.get()
    }
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
    root.destroy()

root = tk.Tk()
root.title("Story Mod Settings")

humour = tk.IntVar(value=3)
drama = tk.IntVar(value=7)
rivals = tk.IntVar(value=5)
auto_run = tk.BooleanVar(value=True)
news_type = tk.StringVar(value="Headline + Full Article")
history = tk.BooleanVar(value=True)
tone = tk.StringVar(value="Tabloid")
memes = tk.BooleanVar(value=True)
team = tk.BooleanVar(value=False)
expt = tk.BooleanVar(value=False)

tk.Scale(root, label="Humour Level", variable=humour, from_=1, to=5, orient="horizontal").pack()
tk.Scale(root, label="Drama Intensity", variable=drama, from_=1, to=10, orient="horizontal").pack()
tk.Scale(root, label="Max Rivals", variable=rivals, from_=1, to=10, orient="horizontal").pack()
tk.Checkbutton(root, text="Auto Run After Race", variable=auto_run).pack()
tk.Label(root, text="News Type").pack(); tk.OptionMenu(root, news_type, "Headline Only", "Headline + Full Article").pack()
tk.Checkbutton(root, text="Save Drama History", variable=history).pack()
tk.Label(root, text="Language Tone").pack(); tk.OptionMenu(root, tone, "Professional", "Tabloid", "Internet-style").pack()
tk.Checkbutton(root, text="Allow Meme Injection", variable=memes).pack()
tk.Checkbutton(root, text="Force Team Orders Mode", variable=team).pack()
tk.Checkbutton(root, text="Experimental Mode", variable=expt).pack()
tk.Button(root, text="Save", command=save).pack(pady=10)

root.mainloop()
