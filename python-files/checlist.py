import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os

# Checklist items
checklist = [
    "Morning Routine (FC)",
    "Yoga / Meditation",
    "Body Conditioning",
    "Workout (HIIT / Strength / Mobility)",
    "Shower / Hygiene",
    "Skill Learning / Study / Project",
    "Hobbies / Reading",
    "Stretching / Light Walk",
    "Night Routine (Jqs/Kgs)",
    "Sleep (21:00–6:00)"
]

# Short names
activity_names = {
    "Morning Routine (FC)": "Morning Routine",
    "Yoga / Meditation": "Yoga / Meditation",
    "Body Conditioning": "Body Conditioning",
    "Workout (HIIT / Strength / Mobility)": "Workout",
    "Shower / Hygiene": "Shower / Hygiene",
    "Skill Learning / Study / Project": "Skill Learning / Study",
    "Hobbies / Reading": "Hobbies / Reading",
    "Stretching / Light Walk": "Stretching / Light Walk",
    "Night Routine (Jqs/Kgs)": "Night Routine",
    "Sleep (21:00–6:00)": "Sleep"
}

# Save path
save_dir = r"D:\_parent\Document\serious"
os.makedirs(save_dir, exist_ok=True)
filename = os.path.join(save_dir, "Checklist_Report.txt")

# Date suffix function
def get_day_suffix(day):
    if 11 <= day <= 13:
        return 'th'
    last_digit = day % 10
    if last_digit == 1:
        return 'st'
    elif last_digit == 2:
        return 'nd'
    elif last_digit == 3:
        return 'rd'
    else:
        return 'th'

# Update live status based on ticked items
def update_status(*args):
    done_count = sum(var.get() for var in vars_list)
    total = len(checklist)
    if done_count == 0:
        status_text.set("Nothing done")
    elif done_count == total:
        status_text.set("Everything done")
    else:
        status_text.set(f"{done_count}/{total} tasks done")

# Save results to TXT
def save_results():
    undone = [activity_names[checklist[i]] for i, var in enumerate(vars_list) if not var.get()]
    completed_count = len(checklist) - len(undone)
    total_count = len(checklist)
    
    now = datetime.now()
    suffix = get_day_suffix(now.day)
    date_str = f"{now.day}{suffix} {now.strftime('%B %Y')}"
    
    # Build status line
    if completed_count == total_count:
        status = f"{date_str}, everything done. Completed: {completed_count}/{total_count}"
    elif completed_count == 0:
        status = f"{date_str}, nothing done. Completed: {completed_count}/{total_count}"
    else:
        status = f"{date_str}, partial done. Undone: {' | '.join(undone)}. Completed: {completed_count}/{total_count}"
    
    # Append with blank line for separation
    with open(filename, "a", encoding="utf-8") as f:
        f.write("\n" + status + "\n")
    
    messagebox.showinfo("Saved", "Checklist saved!")
    os.startfile(filename)

# --- GUI ---
root = tk.Tk()
root.title("Daily Checklist")

# Smaller size for bottom-right corner
window_width = 350
window_height = 450

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x_offset = screen_width - window_width - 10
y_offset = screen_height - window_height - 40

root.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

font_label = ("Arial", 10)
font_chk = ("Arial", 9)

tk.Label(root, text="End of Day Checklist", font=("Arial", 12, "bold")).pack(pady=5)

frame = tk.Frame(root)
frame.pack()

vars_list = []
status_text = tk.StringVar()
status_text.set("Nothing done")

for item in checklist:
    var = tk.BooleanVar()
    var.trace_add("write", update_status)
    chk = tk.Checkbutton(frame, text=activity_names[item], variable=var, font=font_chk)
    chk.pack(anchor="w")
    vars_list.append(var)

status_label = tk.Label(root, textvariable=status_text, font=font_label, fg="blue")
status_label.pack(pady=5)

tk.Button(root, text="Save Checklist", command=save_results, font=("Arial", 10), bg="green", fg="white").pack(pady=10)

root.mainloop()
