import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Global variables
current_folder = ""
all_files = []
masked_to_original = {}
txt_totals = {}
dealer_names = {}

# Constants
valid_draw_prefixes = ("MSE", "GSE", "MPE", "DNE", "NJE", "HAE", "ADE", "SDE")
valid_dealer_prefixes = ("A", "E", "S")
draw_labels = {
    "MSE": "Maha",
    "GSE": "Govi",
    "MPE": "Mega",
    "DNE": "Dana",
    "NJE": "Jaya",
    "HAE": "Hand",
    "ADE": "Ada",
    "SDE": "Suba"
}

def load_today_draw_numbers():
    draw_numbers = set()
    try:
        with open("Today.txt", "r") as file:
            for line in file:
                clean = line.strip().upper()
                if clean:
                    draw_numbers.add(clean)
    except FileNotFoundError:
        messagebox.showwarning("Missing File", "Today.txt not found in app folder.")
    return draw_numbers

def load_dealer_names():
    try:
        with open("name.txt", "r") as f:
            for line in f:
                parts = line.strip().split(None, 1)
                if len(parts) == 2:
                    dealer_names[parts[0].upper()] = parts[1]
    except FileNotFoundError:
        messagebox.showwarning("Missing File", "name.txt not found.")

today_draws = load_today_draw_numbers()
load_dealer_names()

def load_txt_totals():
    txt_totals.clear()
    for filename in all_files:
        filepath = os.path.join(current_folder, filename)
        name_no_ext = os.path.splitext(filename)[0]
        total = 0
        try:
            with open(filepath, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        start, end = int(parts[0]), int(parts[1])
                        if end >= start:
                            total += (end - start + 1)
            txt_totals[name_no_ext] = total
        except Exception as e:
            print(f"Failed to read {filename}: {e}")

def browse_folder():
    global current_folder, all_files
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        current_folder = folder_selected
        try:
            files = [f for f in os.listdir(current_folder) if f.lower().endswith(".txt")]
            files.sort()
            all_files = files
            load_txt_totals()
            apply_search_filter()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")

def refresh_file_list():
    if current_folder:
        try:
            files = [f for f in os.listdir(current_folder) if f.lower().endswith(".txt")]
            files.sort()
            global all_files
            all_files = files
            load_txt_totals()
            apply_search_filter()
        except Exception as e:
            messagebox.showerror("Error", f"Could not refresh folder:\n{e}")
    root.after(5000, refresh_file_list)

def mask_filename(filename):
    filename_no_ext = os.path.splitext(filename)[0]
    parts = filename_no_ext.strip().split()
    if len(parts) != 4:
        return None, None, None

    dealer_code, keyword, draw_no, file_date = parts

    if not dealer_code.startswith(valid_dealer_prefixes):
        return None, None, None
    if keyword.lower() != "returns":
        return None, None, None
    if not draw_no.startswith(valid_draw_prefixes):
        return None, None, None
    if draw_no.upper() not in today_draws:
        return None, None, None

    txt_name = f"{dealer_code} Returns {draw_no} {file_date}"
    total = txt_totals.get(txt_name, "")
    total_str = f" | Total: {total}" if total else ""
    display_text = f"{dealer_code:<10}{draw_no:<12}{file_date}{total_str}"
    return display_text, (dealer_code.upper(), draw_no.upper()), dealer_code.upper()

def apply_search_filter():
    query = search_var.get().strip().lower()
    if query:
        filtered = [f for f in all_files if f.lower().startswith(query)]
    else:
        filtered = all_files

    processed = []
    masked_to_original.clear()
    dealer_file_count = 0
    dealer_code_found = None

    for f in filtered:
        visible, key, dealer_code = mask_filename(f)
        if visible and key:
            masked_to_original.setdefault(key, []).append((visible, f))
            processed.append(visible)
            if dealer_code and dealer_code.lower() == query:
                dealer_file_count += 1
                dealer_code_found = dealer_code

    processed.sort(key=lambda x: x[:10].strip())
    update_listbox(processed)

    if dealer_code_found:
        count_label.config(text=f"Dealer {dealer_code_found} - Total Files: {dealer_file_count}")
    else:
        count_label.config(text="")

def update_listbox(display_list):
    listbox.delete(0, tk.END)
    if not display_list:
        listbox.insert(tk.END, "No files found.")
        return
    for line in display_list:
        listbox.insert(tk.END, line)

def show_detailed_total(filename):
    filepath = os.path.join(current_folder, filename)
    calculations = []
    total = 0

    try:
        with open(filepath, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    start, end = int(parts[0]), int(parts[1])
                    if end >= start:
                        count = end - start + 1
                        total += count
                        calculations.append(f"({start}-{end})+1")
    except Exception as e:
        messagebox.showerror("Error", f"Error reading {filename}:\n{e}")
        return

    expression = " + ".join(calculations)
    result = f"Total = {expression} = {total}"

    win = tk.Toplevel(root)
    win.title(f"Total Breakdown - {filename}")
    win.geometry("800x300")
    txt = tk.Text(win, font=("Courier New", 12), wrap=tk.WORD)
    txt.pack(fill=tk.BOTH, expand=True)
    txt.insert(tk.END, result)
    txt.config(state=tk.DISABLED)

def on_double_click(event):
    selection = listbox.curselection()
    if not selection:
        return

    clicked_line = listbox.get(selection[0]).strip()
    parts = clicked_line.split()
    if len(parts) < 3:
        return

    dealer_code = parts[0].upper()
    draw_no = parts[1].upper()
    key = (dealer_code, draw_no)

    if key in masked_to_original:
        if len(masked_to_original[key]) == 1:
            _, filename = masked_to_original[key][0]
            show_detailed_total(filename)
        else:
            win = tk.Toplevel(root)
            win.title(f"Choose File - {dealer_code} {draw_no}")
            lb = tk.Listbox(win, font=("Courier New", 12), width=80)
            lb.pack(padx=10, pady=10)
            filenames = [f for _, f in masked_to_original[key]]
            for f in filenames:
                lb.insert(tk.END, f)

            def select():
                idx = lb.curselection()
                if idx:
                    show_detailed_total(filenames[idx[0]])
                    win.destroy()

            btn = tk.Button(win, text="View Calculation", command=select)
            btn.pack(pady=5)

def print_summary():
    if not masked_to_original:
        messagebox.showinfo("Print Summary", "No valid data to print.")
        return

    dealers = {}
    for (dealer_code, draw_no), entries in masked_to_original.items():
        for _, filename in entries:
            base = os.path.splitext(filename)[0]
            filepath = os.path.join(current_folder, filename)
            total = 0

            try:
                with open(filepath, "r") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                            start, end = int(parts[0]), int(parts[1])
                            if end >= start:
                                total += (end - start + 1)
            except Exception as e:
                print(f"Failed to read {filename}: {e}")
                continue

            dealers.setdefault(dealer_code, {
                "name": dealer_names.get(dealer_code, "Unknown"),
                "draws": {k: 0 for k in valid_draw_prefixes}
            })

            if draw_no in dealers[dealer_code]["draws"]:
                dealers[dealer_code]["draws"][draw_no] += total

    header = f"{'No':<4}{'D/Code':<8}{'Name':<25}" + "".join(f"{draw_labels[k]:<14}" for k in valid_draw_prefixes)
    summary_lines = [header, "-" * len(header)]

    for i, (dealer_code, info) in enumerate(sorted(dealers.items()), 1):
        row = f"{str(i).zfill(2):<4}{dealer_code:<8}{info['name']:<25}"
        for draw_code in valid_draw_prefixes:
            total = info['draws'].get(draw_code, 0)
            row += f"{total}".ljust(14)
        summary_lines.append(row)

    win = tk.Toplevel(root)
    win.title("Print Summary")
    win.geometry("1100x500")
    txt = tk.Text(win, font=("Courier New", 11), wrap=tk.NONE)
    txt.pack(fill=tk.BOTH, expand=True)
    txt.insert(tk.END, "\n".join(summary_lines))
    txt.config(state=tk.DISABLED)

# --- GUI Setup ---
root = tk.Tk()
root.title("TXT File Name Viewer - Filtered by Today.txt")
root.geometry("1000x550")

top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, pady=5, padx=10)

browse_btn = tk.Button(top_frame, text="Browse Folder", command=browse_folder, font=("Calibri", 12))
browse_btn.pack(side=tk.LEFT)

print_btn = tk.Button(top_frame, text="Print Summary", command=print_summary, font=("Calibri", 12))
print_btn.pack(side=tk.LEFT, padx=10)

search_label = tk.Label(top_frame, text="Search (Dealer Code):", font=("Calibri", 12))
search_label.pack(side=tk.RIGHT)

search_var = tk.StringVar()
search_entry = tk.Entry(top_frame, textvariable=search_var, font=("Calibri", 12), width=20)
search_entry.pack(side=tk.RIGHT, padx=5)
search_var.trace_add("write", lambda *args: apply_search_filter())

listbox = tk.Listbox(root, width=120, height=20, font=("Courier New", 12))
listbox.pack(padx=10, pady=10)
listbox.bind("<Double-Button-1>", on_double_click)

count_label = tk.Label(root, text="", font=("Calibri", 14), fg="blue")
count_label.pack(pady=(0, 10))

refresh_file_list()
root.mainloop()
