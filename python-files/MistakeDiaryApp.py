
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# File to store saved entries
DATA_FILE = "mistake_diary_entries.json"

# Initialize main app window
app = tk.Tk()
app.title("Mistake Diary")
app.geometry("800x800")

# ------------------ Helper Functions ------------------

def save_entry():
    entry = {
        "mistake_no": entry_mistake.get(),
        "subject": entry_subject.get(),
        "chapter": entry_chapter.get(),
        "mcq": entry_mcq.get(),
        "options": {
            "a": entry_a.get(),
            "b": entry_b.get(),
            "c": entry_c.get(),
            "d": entry_d.get()
        },
        "chosen": combo_chosen.get(),
        "correct": combo_correct.get(),
        "reasons": [reason for var, reason in zip(reason_vars, reasons) if var.get()],
        "mood": selected_mood.get(),
        "reflection": text_reflection.get("1.0", tk.END).strip()
    }

    # Load existing data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)

    # Save data
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    messagebox.showinfo("Saved", "Your entry has been saved successfully!")
    clear_form()

def clear_form():
    entry_mistake.delete(0, tk.END)
    entry_subject.delete(0, tk.END)
    entry_chapter.delete(0, tk.END)
    entry_mcq.delete(0, tk.END)
    entry_a.delete(0, tk.END)
    entry_b.delete(0, tk.END)
    entry_c.delete(0, tk.END)
    entry_d.delete(0, tk.END)
    combo_chosen.set("")
    combo_correct.set("")
    for var in reason_vars:
        var.set(False)
    selected_mood.set("")
    text_reflection.delete("1.0", tk.END)

def select_mood(mood):
    selected_mood.set(mood)

# ------------------ UI Layout ------------------

# Mistake Info Frame
frame_info = tk.LabelFrame(app, text="Mistake Info", padx=10, pady=10)
frame_info.pack(fill="x", padx=10, pady=5)

tk.Label(frame_info, text="Mistake #:").grid(row=0, column=0)
entry_mistake = tk.Entry(frame_info, width=10)
entry_mistake.grid(row=0, column=1)

tk.Label(frame_info, text="Subject:").grid(row=0, column=2)
entry_subject = tk.Entry(frame_info, width=15)
entry_subject.grid(row=0, column=3)

tk.Label(frame_info, text="Chapter:").grid(row=0, column=4)
entry_chapter = tk.Entry(frame_info, width=15)
entry_chapter.grid(row=0, column=5)

# MCQ Frame
frame_mcq = tk.LabelFrame(app, text="MCQ & Options", padx=10, pady=10)
frame_mcq.pack(fill="x", padx=10, pady=5)

tk.Label(frame_mcq, text="MCQ:").grid(row=0, column=0, sticky="w")
entry_mcq = tk.Entry(frame_mcq, width=100)
entry_mcq.grid(row=0, column=1, columnspan=3)

tk.Label(frame_mcq, text="a.").grid(row=1, column=0)
entry_a = tk.Entry(frame_mcq, width=30)
entry_a.grid(row=1, column=1)
tk.Label(frame_mcq, text="b.").grid(row=1, column=2)
entry_b = tk.Entry(frame_mcq, width=30)
entry_b.grid(row=1, column=3)

tk.Label(frame_mcq, text="c.").grid(row=2, column=0)
entry_c = tk.Entry(frame_mcq, width=30)
entry_c.grid(row=2, column=1)
tk.Label(frame_mcq, text="d.").grid(row=2, column=2)
entry_d = tk.Entry(frame_mcq, width=30)
entry_d.grid(row=2, column=3)

# Answer Frame
frame_answer = tk.LabelFrame(app, text="Your Answer", padx=10, pady=10)
frame_answer.pack(fill="x", padx=10, pady=5)

tk.Label(frame_answer, text="I Chose Option:").grid(row=0, column=0)
combo_chosen = ttk.Combobox(frame_answer, values=["a", "b", "c", "d"], width=5)
combo_chosen.grid(row=0, column=1)

tk.Label(frame_answer, text="Correct Option Is:").grid(row=0, column=2)
combo_correct = ttk.Combobox(frame_answer, values=["a", "b", "c", "d"], width=5)
combo_correct.grid(row=0, column=3)

# Mistake Reasons Frame
frame_reasons = tk.LabelFrame(app, text="Reasons for Mistake", padx=10, pady=10)
frame_reasons.pack(fill="x", padx=10, pady=5)

reasons = [
    "Didn't know the concept", "Got confused by options", "Guessed randomly",
    "Careless calculation", "Remembered wrong formula/fact", "Overthought",
    "Misread the question", "Was in a hurry", "Other"
]
reason_vars = []
for i, reason in enumerate(reasons):
    var = tk.BooleanVar()
    reason_vars.append(var)
    tk.Checkbutton(frame_reasons, text=reason, variable=var).grid(row=i//3, column=i%3, sticky="w")

# Mood Frame
frame_mood = tk.LabelFrame(app, text="Mood After Mistake", padx=10, pady=10)
frame_mood.pack(fill="x", padx=10, pady=5)

selected_mood = tk.StringVar()
moods = ["😀", "😐", "😢", "😅", "😠", "😡"]
tk.Label(frame_mood, text="Vote:").pack(side="left")
for mood in moods:
    tk.Button(frame_mood, text=mood, width=4, command=lambda m=mood: select_mood(m)).pack(side="left", padx=2)

# Reflection Frame
frame_reflection = tk.LabelFrame(app, text="Reflection", padx=10, pady=10)
frame_reflection.pack(fill="both", expand=True, padx=10, pady=5)

tk.Label(frame_reflection, text="Why did I make this mistake, and how will I avoid it next time?").pack(anchor="w")
text_reflection = tk.Text(frame_reflection, height=5)
text_reflection.pack(fill="x")

# Review Tracker
frame_review = tk.LabelFrame(app, text="Review Tracker", padx=10, pady=10)
frame_review.pack(fill="x", padx=10, pady=5)

tk.Label(frame_review, text="⚪ " * 30).pack()

# Save Button
tk.Button(app, text="Save Entry", command=save_entry, bg="green", fg="white", font=("Arial", 12, "bold")).pack(pady=10)

app.mainloop()
