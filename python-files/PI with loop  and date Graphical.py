import os
import shutil
import tkinter as tk

# === CONFIG ===
part2 = "4040623"  # <- This will be updated in-place
# ==============

def update_part2_in_script(new_value):
    """Rewrites the current script to update the part2 value."""
    script_path = os.path.realpath(__file__)
    with open(script_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.startswith("part2 = "):
            lines[i] = f'part2 = "{new_value}"  # <- This will be updated in-place\n'
            break

    with open(script_path, "w", encoding="utf-8") as file:
        file.writelines(lines)

def create_folder_and_copy_excel(part1, part2):
    folder_name = f"X{part1}-{part2}"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    source_file = "PI.xlsx"
    if not os.path.exists(source_file):
        return  # Silent failure if file is missing

    base_name, ext = os.path.splitext(os.path.basename(source_file))
    new_file_name = f"X{part1}-{part2} {base_name}{ext}"
    destination_file = os.path.join(folder_name, new_file_name)

    try:
        shutil.copy(source_file, destination_file)
    except:
        pass  # Silent on failure

def on_submit(event=None):
    part1 = entry_id.get().strip()
    if part1:
        create_folder_and_copy_excel(part1, part2)
        entry_id.delete(0, tk.END)

def on_change_date():
    global part2
    new_date = entry_id.get().strip()
    if new_date:
        part2 = new_date
        update_part2_in_script(part2)
        label_date.config(text=f"Date: {part2}")
        entry_id.delete(0, tk.END)

# GUI Setup
root = tk.Tk()
root.title("Excel Copier")
root.resizable(False, False)

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

label_date = tk.Label(frame, text=f"Date: {part2}", font=("Arial", 10))
label_date.pack(pady=(0, 5))

entry_id = tk.Entry(frame, width=30, font=("Arial", 12))
entry_id.pack()
entry_id.focus()

entry_id.bind("<Return>", on_submit)  # Pressing Enter triggers submit

btn_frame = tk.Frame(frame)
btn_frame.pack(pady=(5, 0))

submit_btn = tk.Button(btn_frame, text="Create", width=12, command=on_submit)
submit_btn.grid(row=0, column=0, padx=5)

date_btn = tk.Button(btn_frame, text="Set Date", width=12, command=on_change_date)
date_btn.grid(row=0, column=1, padx=5)

root.mainloop()
