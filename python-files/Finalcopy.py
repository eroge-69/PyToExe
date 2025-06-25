import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import datetime
import threading
import subprocess
import tempfile

# Global data
current_folder = ""
all_files = []
masked_to_original = {}
txt_totals = {}
dealer_names = {}
today_draws = []
dealer_data = {}
DATA_FILE = "dealer_data.json"

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


def save_dealer_data():
    with open(DATA_FILE, "w") as f:
        json.dump(dealer_data, f, indent=2)


def load_dealer_data():
    global dealer_data
    dealer_data.clear()
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                dealer_data = json.load(f)
        except json.JSONDecodeError:
            dealer_data = {}

    renew_cutoff = datetime.datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    if datetime.datetime.now().hour < 8:
        renew_cutoff -= datetime.timedelta(days=1)

    for dealer, info in list(dealer_data.items()):
        ts = datetime.datetime.fromisoformat(info["timestamp"])
        if ts < renew_cutoff:
            new_code = datetime.datetime.now().strftime("%H%M%S")[-3:]
            dealer_data[dealer] = {
                "code": new_code,
                "timestamp": datetime.datetime.now().isoformat()
            }

    save_dealer_data()


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
        except:
            continue


def browse_folder():
    global current_folder
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        current_folder = folder_selected
        threading.Thread(target=load_files_and_refresh, daemon=True).start()


def load_files_and_refresh():
    global all_files
    try:
        files = [f for f in os.listdir(current_folder) if f.lower().endswith(".txt")]
        files.sort()
        all_files = files
        load_txt_totals()
        root.after(0, apply_search_filter)
    except Exception as e:
        messagebox.showerror("Error", f"Could not open folder:\n{e}")


def refresh_file_list():
    if current_folder:
        threading.Thread(target=load_files_and_refresh, daemon=True).start()
    root.after(20000, refresh_file_list)


def mask_filename(filename):
    name_no_ext = os.path.splitext(filename)[0]
    parts = name_no_ext.strip().split()
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

    code_str = ""
    if dealer_code.upper() in dealer_data:
        code_str = f" | Code: {dealer_data[dealer_code.upper()]['code']}"

    display = f"{dealer_code:<10}{draw_no:<12}{file_date}{total_str}{code_str}"
    return display, (dealer_code.upper(), draw_no.upper()), dealer_code.upper()


def apply_search_filter():
    query = search_var.get().strip().lower()
    if not query:
        generate_code_var.set(False)

    filtered = [f for f in all_files if f.lower().startswith(query)] if query else all_files

    masked_to_original.clear()
    processed = []
    dealer_file_count = 0
    dealer_code_found = None

    for f in filtered:
        display, key, dealer = mask_filename(f)
        if display and key:
            masked_to_original.setdefault(key, []).append((display, f))
            processed.append(display)
            if dealer and dealer.lower() == query:
                dealer_file_count += 1
                dealer_code_found = dealer

    processed.sort()
    update_listbox(processed)
    count_label.config(text=f"Dealer {dealer_code_found} - Total Files: {dealer_file_count}" if dealer_code_found else "")


def update_listbox(lines):
    listbox.delete(0, tk.END)
    if not lines:
        listbox.insert(tk.END, "No files found.")
    for line in lines:
        listbox.insert(tk.END, line)


def on_generate_code_toggle():
    query = search_var.get().strip().upper()
    if generate_code_var.get() and query in dealer_names:
        if query not in dealer_data:
            new_code = datetime.datetime.now().strftime("%H%M%S")[-3:]
            dealer_data[query] = {
                "code": new_code,
                "timestamp": datetime.datetime.now().isoformat()
            }
            save_dealer_data()
    apply_search_filter()


def build_summary_lines():
    dealers = {
        code: {
            "name": name,
            "draws": {draw: 0 for draw in today_draws}
        } for code, name in dealer_names.items()
    }

    for (dealer, draw), entries in masked_to_original.items():
        for _, filename in entries:
            path = os.path.join(current_folder, filename)
            total = 0
            try:
                with open(path, "r") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                            start, end = int(parts[0]), int(parts[1])
                            if end >= start:
                                total += end - start + 1
            except:
                continue
            if dealer in dealers and draw in dealers[dealer]["draws"]:
                dealers[dealer]["draws"][draw] += total

    header = "No,D/Code,Files,Name," + ",".join(today_draws) + ",Code"
    lines = [header]
    for i, (dealer, info) in enumerate(sorted(dealers.items()), 1):
        count = sum(1 for (d, _) in masked_to_original if d == dealer)
        row = [str(i).zfill(2), dealer, str(count), info['name']]
        for draw in today_draws:
            val = info["draws"].get(draw, 0)
            row.append("-" if val == 0 else str(val))
        row.append(dealer_data.get(dealer, {}).get("code", ""))
        lines.append(",".join(row))
    return lines


def export_summary_to_csv():
    lines = build_summary_lines()
    if not lines:
        messagebox.showwarning("Export Failed", "No data to export.")
        return

    today_str = datetime.date.today().isoformat()
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f"summary_{today_str}.csv", filetypes=[("CSV files", "*.csv")])
    if not save_path:
        return

    try:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(",,,,,,,,,,Date: " + today_str + "\n")
            f.write("National Lotteries Board\nReturn Check List\n\n")
            for line in lines:
                f.write(line + "\n")
            f.write("\nChecked By (Returns Section): ..................\n")
            f.write("Confirm By (IT Division): ..................\n")
            f.write("Received By (Tickets Stores): ..................\n")
            f.write("IT Checking Start Time: ..........  End Time: ..........\n")

        messagebox.showinfo("Export Complete", f"Saved to:\n{save_path}")
    except Exception as e:
        messagebox.showerror("Export Failed", str(e))


def print_summary():
    lines = build_summary_lines()
    if not lines:
        messagebox.showwarning("Print Failed", "No data to print.")
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as temp:
        today_str = datetime.date.today().isoformat()
        temp.write("National Lotteries Board\nReturn Check List\n\n")
        temp.write("Date: " + today_str + "\n\n")
        for line in lines:
            temp.write(line + "\n")
        temp.write("\nChecked By (Returns Section): ..................\n")
        temp.write("Confirm By (IT Division): ..................\n")
        temp.write("Received By (Tickets Stores): ..................\n")
        temp.write("IT Checking Start Time: ..........  End Time: ..........\n")

    subprocess.run(["notepad", "/p", temp.name])


def update_datetime():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    datetime_label.config(text=f"Date & Time: {now}")
    root.after(1000, update_datetime)


# GUI Setup
root = tk.Tk()
root.title("Return Summary Viewer")
root.geometry("1000x600")

header_frame = tk.Frame(root)
header_frame.pack()
tk.Label(header_frame, text="National Lotteries Board", font=("Calibri", 20, "bold"), fg="darkblue").pack()
datetime_label = tk.Label(header_frame, text="", font=("Calibri", 12), fg="green")
datetime_label.pack()
update_datetime()

top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, pady=5, padx=10)
tk.Button(top_frame, text="Browse Folder", command=browse_folder, font=("Calibri", 12)).pack(side=tk.LEFT)
tk.Button(top_frame, text="Export to CSV", command=export_summary_to_csv, font=("Calibri", 12)).pack(side=tk.LEFT, padx=10)
tk.Button(top_frame, text="Print A4", command=print_summary, font=("Calibri", 12)).pack(side=tk.LEFT, padx=10)
generate_code_var = tk.BooleanVar()
tk.Checkbutton(top_frame, text="Generate Code", variable=generate_code_var, command=on_generate_code_toggle, font=("Calibri", 12)).pack(side=tk.RIGHT)
tk.Label(top_frame, text="Search (Dealer Code):", font=("Calibri", 12)).pack(side=tk.RIGHT)
search_var = tk.StringVar()
tk.Entry(top_frame, textvariable=search_var, font=("Calibri", 12), width=20).pack(side=tk.RIGHT, padx=5)
search_var.trace_add("write", lambda *args: apply_search_filter())

listbox = tk.Listbox(root, width=120, height=20, font=("Courier New", 12))
listbox.pack(padx=10, pady=10)

count_label = tk.Label(root, text="", font=("Calibri", 14), fg="blue")
count_label.pack()

# Init
load_today_draw_numbers()
load_dealer_names()
load_dealer_data()
root.after(20000, refresh_file_list)

root.mainloop()
