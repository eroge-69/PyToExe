import os
import tkinter as tk
from tkinter import filedialog, messagebox
import datetime

# Global data
current_folder = ""
all_files = []
masked_to_original = {}
txt_totals = {}
dealer_names = {}
today_draws = []

valid_dealer_prefixes = ("A", "E", "S")

def load_today_draw_numbers():
    global today_draws
    today_draws.clear()
    try:
        with open("Today.txt", "r") as file:
            for line in file:
                clean = line.strip().upper()
                if clean:
                    today_draws.append(clean)
        today_draws.sort()
    except FileNotFoundError:
        messagebox.showwarning("Missing File", "Today.txt not found.")

def load_dealer_names():
    try:
        with open("name.txt", "r") as f:
            for line in f:
                parts = line.strip().split(None, 1)
                if len(parts) == 2:
                    dealer_names[parts[0].upper()] = parts[1]
    except FileNotFoundError:
        messagebox.showwarning("Missing File", "name.txt not found.")

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
    if draw_no.upper() not in today_draws:
        return None, None, None

    txt_name = f"{dealer_code} Returns {draw_no} {file_date}"
    total = txt_totals.get(txt_name, "")
    total_str = f" | Total: {total}" if total else ""
    display_text = f"{dealer_code:<10}{draw_no:<12}{file_date}{total_str}"
    return display_text, (dealer_code.upper(), draw_no.upper()), dealer_code.upper()

def apply_search_filter():
    query = search_var.get().strip().lower()
    filtered = [f for f in all_files if f.lower().startswith(query)] if query else all_files

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

    count_label.config(text=f"Dealer {dealer_code_found} - Total Files: {dealer_file_count}" if dealer_code_found else "")

def update_listbox(display_list):
    listbox.delete(0, tk.END)
    if not display_list:
        listbox.insert(tk.END, "No files found.")
        return
    for line in display_list:
        listbox.insert(tk.END, line)

def build_summary_lines():
    dealers = {
        code: {
            "name": name,
            "draws": {draw: 0 for draw in today_draws}
        } for code, name in dealer_names.items()
    }

    for (dealer_code, draw_no), entries in masked_to_original.items():
        for _, filename in entries:
            filepath = os.path.join(current_folder, filename)
            total = 0
            try:
                with open(filepath, "r") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                            start, end = int(parts[0]), int(parts[1])
                            if end >= start:
                                total += end - start + 1
            except:
                continue

            if dealer_code in dealers and draw_no in dealers[dealer_code]["draws"]:
                dealers[dealer_code]["draws"][draw_no] += total

    header = "No,D/Code,Files,Name," + ",".join(today_draws)
    lines = [header]

    for i, (dealer_code, info) in enumerate(sorted(dealers.items()), 1):
        file_count = sum(1 for (d, _) in masked_to_original if d == dealer_code)
        row = [str(i).zfill(2), dealer_code, str(file_count), info['name']]
        for draw_code in today_draws:
            total = info['draws'].get(draw_code, 0)
            row.append("-" if total == 0 else str(total))
        lines.append(",".join(row))

    return lines

def export_summary_to_csv():
    lines = build_summary_lines()
    if not lines:
        messagebox.showwarning("Export Failed", "No data to export.")
        return

    today_str = datetime.date.today().isoformat()
    default_name = f"summary_{today_str}.csv"
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=default_name, filetypes=[("CSV files", "*.csv")])
    if not save_path:
        return

    try:
        with open(save_path, "w", newline="", encoding="utf-8") as f:
            # Top: Simulate right-aligned date
            f.write(",,,,,,,,,,Date: " + today_str + "\n")
            f.write("National Lotteries Board\n")
            f.write("Return Check List\n\n")

            # Main Table
            for line in lines:
                f.write(line + "\n")

            # Footer
            f.write("\n")
            f.write("Checked By (Returns Section) :.................. \n")
            f.write("Confirm By (IT Division) :.................. \n")
            f.write("Received By (Tickets Stores) :..................\n")
            f.write("\n")
            f.write("IT Cheking Start Time :..................        IT Cheking End Time : ..................\n")

        messagebox.showinfo("Export Complete", f"Summary exported to:\n{save_path}")
    except Exception as e:
        messagebox.showerror("Export Failed", str(e))

def update_datetime():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    datetime_label.config(text=f"Date & Time: {now}")
    root.after(1000, update_datetime)

# GUI Setup
root = tk.Tk()
root.title("Return Summary Viewer")
root.geometry("1000x580")

# Header Frame
header_frame = tk.Frame(root)
header_frame.pack(fill=tk.X, pady=5)

title_label = tk.Label(header_frame, text="National Lotteries Board", font=("Calibri", 20, "bold"), fg="darkblue")
title_label.pack()

datetime_label = tk.Label(header_frame, text="", font=("Calibri", 12), fg="green")
datetime_label.pack()
update_datetime()

# Control Buttons and Search
top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, pady=5, padx=10)

browse_btn = tk.Button(top_frame, text="Browse Folder", command=browse_folder, font=("Calibri", 12))
browse_btn.pack(side=tk.LEFT)

export_btn = tk.Button(top_frame, text="Export to CSV", command=export_summary_to_csv, font=("Calibri", 12))
export_btn.pack(side=tk.LEFT, padx=10)

search_label = tk.Label(top_frame, text="Search (Dealer Code):", font=("Calibri", 12))
search_label.pack(side=tk.RIGHT)

search_var = tk.StringVar()
search_entry = tk.Entry(top_frame, textvariable=search_var, font=("Calibri", 12), width=20)
search_entry.pack(side=tk.RIGHT, padx=5)
search_var.trace_add("write", lambda *args: apply_search_filter())

# Listbox
listbox = tk.Listbox(root, width=120, height=20, font=("Courier New", 12))
listbox.pack(padx=10, pady=10)

# File count display
count_label = tk.Label(root, text="", font=("Calibri", 14), fg="blue")
count_label.pack(pady=(0, 10))

# Start
load_today_draw_numbers()
load_dealer_names()
refresh_file_list()
root.mainloop()
