import os
import tkinter as tk
from tkinter import filedialog, messagebox

current_folder = ""
all_files = []
masked_to_original = {}

valid_draw_prefixes = ("MSE", "GSE", "MPE", "DNE", "NJE", "HAE", "ADE", "SDE")
valid_dealer_prefixes = ("A", "E", "S")

# Load draw numbers from Today.txt
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

today_draws = load_today_draw_numbers()

def browse_folder():
    global current_folder, all_files
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        current_folder = folder_selected
        try:
            files = [
                f for f in os.listdir(current_folder)
                if os.path.isfile(os.path.join(current_folder, f)) and f.lower().endswith(".pdf")
            ]
            files.sort()
            all_files = files
            apply_search_filter()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")

def refresh_file_list():
    if current_folder:
        try:
            files = [
                f for f in os.listdir(current_folder)
                if os.path.isfile(os.path.join(current_folder, f)) and f.lower().endswith(".pdf")
            ]
            files.sort()
            global all_files
            all_files = files
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

    display_text = f"{dealer_code:<10}{draw_no:<12}{file_date}"
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

    # Update dealer count label
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
        original_files = [orig_file for _, orig_file in masked_to_original[key]]
        messagebox.showinfo(f"All files for {dealer_code} {draw_no}", "\n".join(original_files))
    else:
        messagebox.showinfo("Not found", "No original files available for selection.")

# --- GUI Setup ---
root = tk.Tk()
root.title("PDF File Name Viewer - Filtered by Today.txt")
root.geometry("1000x550")

top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, pady=5, padx=10)

browse_btn = tk.Button(top_frame, text="Browse Folder", command=browse_folder, font=("Calibri", 12))
browse_btn.pack(side=tk.LEFT)

search_label = tk.Label(top_frame, text="Search (Dealer Code):", font=("Calibri", 12))
search_label.pack(side=tk.RIGHT)

search_var = tk.StringVar()
search_entry = tk.Entry(top_frame, textvariable=search_var, font=("Calibri", 12), width=20)
search_entry.pack(side=tk.RIGHT, padx=5)
search_var.trace_add("write", lambda *args: apply_search_filter())

listbox = tk.Listbox(root, width=120, height=20, font=("Courier New", 12))
listbox.pack(padx=10, pady=10)
listbox.bind("<Double-Button-1>", on_double_click)

# --- Bottom Label for Count ---
count_label = tk.Label(root, text="", font=("Calibri", 14), fg="blue")
count_label.pack(pady=(0, 10))

refresh_file_list()
root.mainloop()
