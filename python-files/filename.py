import os
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Label
import time
import threading

# Globals
current_folder = ""
all_files = []
popup_files = []
popup_window = None

def browse_folder():
    global current_folder, all_files
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        current_folder = folder_selected
        try:
            files = [f for f in os.listdir(current_folder) if os.path.isfile(os.path.join(current_folder, f))]
            files.sort()
            all_files = files
            update_listbox(all_files)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")

def refresh_file_list():
    if current_folder:
        try:
            files = [f for f in os.listdir(current_folder) if os.path.isfile(os.path.join(current_folder, f))]
            files.sort()
            global all_files
            all_files = files
            apply_search_filter()
        except Exception as e:
            messagebox.showerror("Error", f"Could not refresh folder:\n{e}")
    root.after(5000, refresh_file_list)

def apply_search_filter():
    query = search_var.get().strip().lower()
    if query:
        filtered = [f for f in all_files if f.lower().startswith(query)]
    else:
        filtered = all_files
    update_listbox(filtered)

def update_listbox(file_list):
    listbox.delete(0, tk.END)
    if not file_list:
        listbox.insert(tk.END, "No files found.")
        return

    shortened_files = [f[:8] for f in file_list]
    col_width = 16
    columns = 5
    rows = [shortened_files[i:i+columns] for i in range(0, len(shortened_files), columns)]
    for row in rows:
        line = "".join(f"{f:<{col_width}}" for f in row)
        listbox.insert(tk.END, line)

def show_popup(files):
    global popup_window
    if popup_window is not None:
        popup_window.destroy()

    popup_window = Toplevel(root)
    popup_window.title("New Files Detected")
    popup_window.geometry("400x200")
    popup_window.attributes("-topmost", True)

    label = Label(popup_window, text="\n".join(files), font=("Calibri", 12))
    label.pack(padx=20, pady=20)

    def auto_close():
        time.sleep(10)
        try:
            popup_window.destroy()
        except:
            pass

    threading.Thread(target=auto_close, daemon=True).start()

def monitor_selected_folder():
    seen_files = set()
    while True:
        if current_folder:
            try:
                files = os.listdir(current_folder)
                valid_files = [f for f in files if f.lower().endswith(".dbf") and f[0].isalpha() and os.path.isfile(os.path.join(current_folder, f))]
                new_files = [f for f in valid_files if f not in seen_files]

                if new_files:
                    for f in new_files:
                        popup_files.append(f)
                        seen_files.add(f)

                    if len(popup_files) > 5:
                        popup_files[:] = popup_files[-5:]

                    root.after(0, lambda f=popup_files.copy(): show_popup(f))

                time.sleep(2)
            except Exception as e:
                print("Monitor error:", e)
                time.sleep(5)
        else:
            time.sleep(1)

# GUI Setup
root = tk.Tk()
root.title("File Name Viewer")
root.geometry("1000x500")

top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, pady=5, padx=10)

browse_btn = tk.Button(top_frame, text="Browse Folder", command=browse_folder, font=("Calibri", 12))
browse_btn.pack(side=tk.LEFT)

search_label = tk.Label(top_frame, text="Search (first 4 chars):", font=("Calibri", 12))
search_label.pack(side=tk.RIGHT)

search_var = tk.StringVar()
search_entry = tk.Entry(top_frame, textvariable=search_var, font=("Calibri", 12), width=20)
search_entry.pack(side=tk.RIGHT, padx=5)
search_var.trace_add("write", lambda *args: apply_search_filter())

listbox = tk.Listbox(root, width=120, height=20, font=("Courier New", 12))
listbox.pack(padx=10, pady=10)

# Start folder monitoring in a background thread
threading.Thread(target=monitor_selected_folder, daemon=True).start()

refresh_file_list()
root.mainloop()
