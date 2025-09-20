import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pywhatkit
import os
import threading
import time
import json
import pandas as pd
from datetime import datetime

# --- Global variables to store the path and type of the selected media ---
media_path = None
media_type = None # Will be 'image' or 'video'
GROUPS_FILE = "whatsapp_groups.json"
HISTORY_FILE = "sending_history.json"

# --- Global flags for controlling the sending thread ---
sending_paused = False
sending_cancelled = False
scheduling_active = False

# --- Analytics Functions ---

def load_history():
    """Loads sending history from the JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r') as f:
            content = f.read()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return []

def save_to_history(successful, failed):
    """Saves the result of a sending campaign to the history file."""
    history = load_history()
    new_entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "successful_count": len(successful),
        "failed_count": len(failed),
        "successful_numbers": successful,
        "failed_numbers": [str(f) for f in failed]
    }
    history.append(new_entry)
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)
    except IOError as e:
        print(f"Error saving history: {e}")

def update_dashboard_analytics():
    """Calculates and displays analytics on the dashboard."""
    history = load_history()
    total_sent = sum(entry.get("successful_count", 0) for entry in history)
    total_campaigns = len(history)
    last_campaign_date = "N/A"
    if history:
        try:
            sorted_history = sorted(history, key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d %H:%M:%S"))
            last_campaign_date = sorted_history[-1].get("date", "N/A").split(" ")[0]
        except (ValueError, KeyError):
            last_campaign_date = "Invalid Date"
    if 'dashboard_sent_count_label' in globals() and dashboard_sent_count_label.winfo_exists():
        dashboard_sent_count_label.config(text=str(total_sent))
        dashboard_campaign_count_label.config(text=str(total_campaigns))
        dashboard_last_campaign_label.config(text=last_campaign_date)

# --- Group Management Functions ---

def load_groups_from_file():
    if not os.path.exists(GROUPS_FILE): return {}
    try:
        with open(GROUPS_FILE, 'r') as f:
            content = f.read()
            return json.loads(content) if content else {}
    except (json.JSONDecodeError, IOError):
        messagebox.showerror("File Error", f"Could not read '{GROUPS_FILE}'. A new one will be created.")
        return {}

def save_groups_to_file(groups):
    try:
        with open(GROUPS_FILE, 'w') as f:
            json.dump(groups, f, indent=4)
    except IOError as e:
        messagebox.showerror("File Error", f"Could not save groups: {e}")

def update_main_groups_dropdown():
    groups = load_groups_from_file()
    group_names = list(groups.keys())
    if 'groups_combobox' in globals() and groups_combobox.winfo_exists():
        groups_combobox['values'] = group_names
        if group_names:
            groups_combobox.set('')
        else:
            groups_combobox.set('No groups available')
    if 'dashboard_group_count_label' in globals() and dashboard_group_count_label.winfo_exists():
        dashboard_group_count_label.config(text=str(len(group_names)))


def load_selected_group_into_main_list():
    group_name = groups_combobox.get()
    if not group_name or group_name == 'No groups available':
        messagebox.showwarning("Selection Error", "Please select a group to load.")
        return
    groups = load_groups_from_file()
    if group_name in groups:
        if numbers_listbox.get(0, tk.END) and not messagebox.askyesno("Confirm Load", "This will replace the current list of numbers. Continue?"):
            return
        numbers_listbox.delete(0, tk.END)
        for number in groups[group_name]:
            numbers_listbox.insert(tk.END, number)
        messagebox.showinfo("Success", f"Group '{group_name}' loaded.")
    else:
        messagebox.showerror("Error", f"Group '{group_name}' not found.")

def open_group_manager():
    manager_window = tk.Toplevel(root)
    manager_window.title("Group Manager")
    manager_window.geometry("800x550")
    manager_window.configure(bg="#ECE5DD")
    manager_window.transient(root)
    manager_window.grab_set()

    manager_window.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (manager_window.winfo_width() // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (manager_window.winfo_height() // 2)
    manager_window.geometry(f"+{x}+{y}")
    manager_window.minsize(650, 450)

    def populate_groups_listbox():
        groups_listbox.delete(0, tk.END)
        for group_name in sorted(load_groups_from_file().keys()):
            groups_listbox.insert(tk.END, group_name)
    
    def clear_editor_fields():
        group_name_editor_entry.delete(0, tk.END)
        numbers_editor_text.delete("1.0", tk.END)
        groups_listbox.selection_clear(0, tk.END)

    def on_group_select(event):
        if not groups_listbox.curselection(): return
        selected_group = groups_listbox.get(groups_listbox.curselection()[0])
        groups = load_groups_from_file()
        group_name_editor_entry.delete(0, tk.END); numbers_editor_text.delete("1.0", tk.END)
        group_name_editor_entry.insert(0, selected_group)
        numbers_editor_text.insert("1.0", "\n".join(groups.get(selected_group, [])))

    def import_from_file():
        file_path = filedialog.askopenfilename(
            title="Select Excel or CSV File",
            filetypes=(("Spreadsheet files", "*.xlsx *.xls *.csv"), ("All files", "*.*")),
            parent=manager_window
        )
        if not file_path: return

        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, header=None, dtype=str)
            else:
                df = pd.read_excel(file_path, header=None, dtype=str)
            
            if df.empty:
                messagebox.showwarning("Empty File", "The selected file is empty.", parent=manager_window)
                return
            
            numbers_from_file = df.iloc[:, 0].dropna().astype(str).tolist()

            for item in numbers_from_file:
                if item.count('+') > 1 or ',' in item:
                    messagebox.showerror(
                        "Format Error",
                        "Invalid file format.\n\nPlease ensure each phone number is in its own row (one cell per number), one below the other.",
                        parent=manager_window
                    )
                    return

            valid_numbers = [num.strip() for num in numbers_from_file if num.strip().startswith('+')]
            invalid_count = len(numbers_from_file) - len(valid_numbers)

            if not valid_numbers:
                messagebox.showerror("No Valid Numbers", f"No valid numbers starting with '+' were found.\nSkipped {invalid_count} entries.", parent=manager_window)
                return

            current_text = numbers_editor_text.get("1.0", tk.END).strip()
            if current_text and messagebox.askyesno("Confirm", "Add imported numbers to the existing list?\n('No' will replace the list)", parent=manager_window):
                existing_numbers = set(current_text.split('\n'))
                new_numbers_to_add = [num for num in valid_numbers if num not in existing_numbers]
                if new_numbers_to_add:
                    numbers_editor_text.insert(tk.END, "\n" * (1 if current_text else 0) + "\n".join(new_numbers_to_add))
            else:
                numbers_editor_text.delete("1.0", tk.END)
                numbers_editor_text.insert("1.0", "\n".join(valid_numbers))
            
            summary = f"Imported {len(valid_numbers)} numbers." + (f"\nSkipped {invalid_count} invalid entries." if invalid_count else "")
            messagebox.showinfo("Import Complete", summary, parent=manager_window)
        except Exception as e:
            messagebox.showerror("Import Error", f"An error occurred: {e}", parent=manager_window)

    def export_group_to_csv():
        group_name = group_name_editor_entry.get().strip()
        numbers_raw = numbers_editor_text.get("1.0", tk.END).strip()
        if not numbers_raw:
            messagebox.showwarning("Input Error", "There are no numbers to export.", parent=manager_window)
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"{group_name}_export.csv" if group_name else "contacts.csv",
            parent=manager_window
        )
        if not file_path: return

        try:
            numbers = [num.strip() for num in numbers_raw.split('\n') if num.strip()]
            df = pd.DataFrame(numbers, columns=["Numbers"])
            df.to_csv(file_path, index=False)
            messagebox.showinfo("Success", f"Group exported successfully to:\n{file_path}", parent=manager_window)
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred: {e}", parent=manager_window)

    def save_group_from_editor():
        group_name = group_name_editor_entry.get().strip()
        if not group_name:
            messagebox.showwarning("Input Error", "Group name cannot be empty.", parent=manager_window); return
        numbers_raw = numbers_editor_text.get("1.0", tk.END).strip()
        numbers = [num.strip() for num in numbers_raw.split('\n') if num.strip() and num.startswith('+')]
        if not numbers:
            messagebox.showwarning("Input Error", "Please add at least one valid number (starting with '+').", parent=manager_window); return
        groups = load_groups_from_file()
        groups[group_name] = numbers
        save_groups_to_file(groups)
        populate_groups_listbox()
        update_main_groups_dropdown()
        messagebox.showinfo("Success", f"Group '{group_name}' saved.", parent=manager_window)

    def delete_group_from_list():
        if not groups_listbox.curselection():
            messagebox.showwarning("Selection Error", "Please select a group to delete.", parent=manager_window); return
        group_to_delete = groups_listbox.get(groups_listbox.curselection()[0])
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{group_to_delete}'?", parent=manager_window):
            groups = load_groups_from_file()
            if group_to_delete in groups:
                del groups[group_to_delete]
                save_groups_to_file(groups); populate_groups_listbox(); update_main_groups_dropdown(); clear_editor_fields()
                messagebox.showinfo("Success", "Group deleted.", parent=manager_window)

    def duplicate_group():
        if not groups_listbox.curselection():
            messagebox.showwarning("Selection Error", "Please select a group to duplicate.", parent=manager_window); return
        original_group_name = groups_listbox.get(groups_listbox.curselection()[0])
        groups = load_groups_from_file()
        if original_group_name in groups:
            new_group_name = f"{original_group_name} (Copy)"
            i = 1
            while new_group_name in groups:
                new_group_name = f"{original_group_name} (Copy {i+1})"
                i += 1
            groups[new_group_name] = list(groups[original_group_name])
            save_groups_to_file(groups)
            populate_groups_listbox()
            update_main_groups_dropdown()
            for idx, name in enumerate(groups_listbox.get(0, tk.END)):
                if name == new_group_name:
                    groups_listbox.selection_set(idx)
                    on_group_select(None)
                    break
            messagebox.showinfo("Success", f"Group duplicated as '{new_group_name}'.", parent=manager_window)

    def clear_numbers_editor():
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all numbers from the editor?", parent=manager_window):
            numbers_editor_text.delete("1.0", tk.END)

    def remove_duplicate_numbers():
        numbers_list = [num.strip() for num in numbers_editor_text.get("1.0", tk.END).strip().split('\n') if num.strip()]
        if not numbers_list:
            messagebox.showwarning("No Numbers", "No numbers to process.", parent=manager_window); return
        unique_numbers = sorted(list(set(numbers_list)))
        numbers_editor_text.delete("1.0", tk.END); numbers_editor_text.insert("1.0", "\n".join(unique_numbers))
        messagebox.showinfo("Duplicates Removed", f"Removed {len(numbers_list) - len(unique_numbers)} duplicate(s).", parent=manager_window)

    def sort_numbers_editor():
        numbers_list = [num.strip() for num in numbers_editor_text.get("1.0", tk.END).strip().split('\n') if num.strip()]
        if not numbers_list:
            messagebox.showwarning("No Numbers", "No numbers to sort.", parent=manager_window); return
        numbers_list.sort()
        numbers_editor_text.delete("1.0", tk.END); numbers_editor_text.insert("1.0", "\n".join(numbers_list))
        messagebox.showinfo("Numbers Sorted", "Numbers have been sorted.", parent=manager_window)

    manager_window.columnconfigure(0, weight=1); manager_window.rowconfigure(0, weight=1)
    paned_window = ttk.PanedWindow(manager_window, orient=tk.HORIZONTAL)
    paned_window.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    left_pane = ttk.Frame(paned_window, padding=5, style="App.TFrame"); paned_window.add(left_pane, weight=1)
    left_pane.columnconfigure(0, weight=1); left_pane.rowconfigure(1, weight=1)
    ttk.Label(left_pane, text="Existing Groups", font=('Helvetica', 12, 'bold'), foreground=TITLE_COLOR, background=BG_COLOR).grid(row=0, column=0, sticky="w", pady=(0,5))
    list_frame = ttk.Frame(left_pane, style="App.TFrame")
    list_frame.grid(row=1, column=0, sticky="nsew")
    list_frame.rowconfigure(0, weight=1); list_frame.columnconfigure(0, weight=1)
    groups_listbox = tk.Listbox(list_frame, bg="white", fg="black", relief='solid', borderwidth=1, exportselection=False, font=('Helvetica', 10))
    groups_listbox.grid(row=0, column=0, sticky="nsew"); groups_listbox.bind("<<ListboxSelect>>", on_group_select)
    listbox_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=groups_listbox.yview); listbox_scrollbar.grid(row=0, column=1, sticky="ns"); groups_listbox.config(yscrollcommand=listbox_scrollbar.set)
    group_action_frame = ttk.Frame(left_pane, style="App.TFrame")
    group_action_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10,0))
    group_action_frame.columnconfigure(0, weight=1); group_action_frame.columnconfigure(1, weight=1)
    ttk.Button(group_action_frame, text="New Group", command=clear_editor_fields, style="Std.TButton").grid(row=0, column=0, sticky="ew", padx=(0, 5))
    ttk.Button(group_action_frame, text="Delete Group", command=delete_group_from_list, style="Std.TButton").grid(row=0, column=1, sticky="ew", padx=(5, 0))
    ttk.Button(group_action_frame, text="Duplicate Group", command=duplicate_group, style="Std.TButton").grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5,0))

    right_pane = ttk.Frame(paned_window, padding=10, style="App.TFrame"); paned_window.add(right_pane, weight=2)
    right_pane.columnconfigure(1, weight=1); right_pane.rowconfigure(2, weight=1)
    ttk.Label(right_pane, text="Group Name:", font=('Helvetica', 11, 'bold'), background=BG_COLOR).grid(row=0, column=0, sticky="w", pady=2)
    group_name_editor_entry = ttk.Entry(right_pane, font=('Helvetica', 10)); group_name_editor_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2, padx=(5,0))
    ttk.Label(right_pane, text="Numbers (one per line, start with '+'):", font=('Helvetica', 11, 'bold'), background=BG_COLOR).grid(row=1, column=0, sticky="w", pady=(10,2))
    
    text_editor_frame = ttk.Frame(right_pane, style="App.TFrame")
    text_editor_frame.grid(row=2, column=0, columnspan=3, sticky="nsew")
    text_editor_frame.rowconfigure(0, weight=1); text_editor_frame.columnconfigure(0, weight=1)
    numbers_editor_text = tk.Text(text_editor_frame, height=10, bg="white", fg="black", relief='solid', borderwidth=1, insertbackground='black', font=('Helvetica', 10))
    numbers_editor_text.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
    text_scrollbar = ttk.Scrollbar(text_editor_frame, orient="vertical", command=numbers_editor_text.yview)
    text_scrollbar.grid(row=0, column=1, sticky="ns"); numbers_editor_text.config(yscrollcommand=text_scrollbar.set)
    
    numbers_actions_frame = ttk.Frame(right_pane, style="App.TFrame")
    numbers_actions_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(5,0))
    for i in range(4): numbers_actions_frame.columnconfigure(i, weight=1)
    ttk.Button(numbers_actions_frame, text="Import (Excel/CSV)", command=import_from_file, style="Std.TButton").grid(row=0, column=0, sticky="ew", padx=(0,5))
    ttk.Button(numbers_actions_frame, text="Clear", command=clear_numbers_editor, style="Std.TButton").grid(row=0, column=1, sticky="ew", padx=(5,5))
    ttk.Button(numbers_actions_frame, text="Remove Duplicates", command=remove_duplicate_numbers, style="Std.TButton").grid(row=0, column=2, sticky="ew", padx=(5,5))
    ttk.Button(numbers_actions_frame, text="Sort", command=sort_numbers_editor, style="Std.TButton").grid(row=0, column=3, sticky="ew", padx=(5,0))

    bottom_buttons_frame = ttk.Frame(right_pane, style="App.TFrame"); bottom_buttons_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(10,0))
    bottom_buttons_frame.columnconfigure(0, weight=1); bottom_buttons_frame.columnconfigure(1, weight=1)
    ttk.Button(bottom_buttons_frame, text="Export to CSV", command=export_group_to_csv, style="Std.TButton").grid(row=0, column=0, sticky="ew", padx=(0,5), ipady=3)
    ttk.Button(bottom_buttons_frame, text="Save Group", command=save_group_from_editor, style="Send.TButton").grid(row=0, column=1, sticky="ew", padx=(5,0), ipady=3)

    populate_groups_listbox()


# --- Main Application Functions ---

def select_image():
    """Opens a file dialog to select only image files."""
    global media_path, media_type
    path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=(("Image files", "*.jpg *.jpeg *.png *.gif"), ("All files", "*.*"))
    )
    if path:
        media_path = path
        media_type = 'image'
        filename_label.config(text=os.path.basename(path), foreground="#075E54", font=('Helvetica', 10, 'bold'))

def select_video():
    """Opens a file dialog to select only video files."""
    global media_path, media_type
    path = filedialog.askopenfilename(
        title="Select a Video",
        filetypes=(("Video files", "*.mp4 *.mov *.avi *.mkv"), ("All files", "*.*"))
    )
    if path:
        media_path = path
        media_type = 'video'
        filename_label.config(text=os.path.basename(path), foreground="#075E54", font=('Helvetica', 10, 'bold'))


def add_number():
    number = phone_entry.get().strip()
    if number and number.startswith('+'):
        if number not in numbers_listbox.get(0, tk.END):
            numbers_listbox.insert(tk.END, number); phone_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Duplicate", "This number is already in the list.")
    elif number:
        messagebox.showwarning("Invalid Format", "Number must start with a country code (e.g., +1, +91).")

def remove_number():
    for index in reversed(numbers_listbox.curselection()): numbers_listbox.delete(index)

def import_numbers_to_main_list():
    """Imports numbers from an Excel or CSV file into the main numbers_listbox."""
    file_path = filedialog.askopenfilename(
        title="Select Excel or CSV File with Numbers",
        filetypes=(("Spreadsheet files", "*.xlsx *.xls *.csv"), ("All files", "*.*"))
    )
    if not file_path:
        return

    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, header=None, dtype=str)
        else:
            df = pd.read_excel(file_path, header=None, dtype=str)
        
        if df.empty:
            messagebox.showwarning("Empty File", "The selected file contains no data.")
            return
        
        numbers_from_file = df.iloc[:, 0].dropna().astype(str).tolist()
        
        for item in numbers_from_file:
            if item.count('+') > 1 or ',' in item:
                messagebox.showerror(
                    "Format Error",
                    "Invalid file format.\n\n"
                    "Please ensure each phone number is in its own row (one cell per number), one below the other.\n\n"
                    "Correct Example:\n"
                    "Cell A1: +923171234567\n"
                    "Cell A2: +923001234567"
                )
                return

        valid_numbers = [num.strip() for num in numbers_from_file if num.strip().startswith('+')]
        existing_numbers = set(numbers_listbox.get(0, tk.END))
        
        new_numbers_added = 0
        for number in valid_numbers:
            if number not in existing_numbers:
                numbers_listbox.insert(tk.END, number)
                existing_numbers.add(number)
                new_numbers_added += 1
        
        total_in_file = len(numbers_from_file)
        skipped_count = total_in_file - new_numbers_added
        
        messagebox.showinfo(
            "Import Complete",
            f"Successfully added {new_numbers_added} new number(s).\n"
            f"Skipped {skipped_count} number(s) (invalid format or already in list)."
        )

    except Exception as e:
        messagebox.showerror("Import Error", f"An error occurred while reading the file:\n{e}")


def update_status(message, value=None):
    if root.winfo_exists():
        root.after(0, lambda: status_label.config(text=message))
        if value is not None:
            root.after(0, lambda: progress_bar.config(value=value))

def update_report_lists(successful, failed):
    if root.winfo_exists():
        success_listbox.delete(0, tk.END); fail_listbox.delete(0, tk.END)
        for num in successful: success_listbox.insert(tk.END, num)
        for info in failed: fail_listbox.insert(tk.END, info)

def send_message_thread():
    """
    This function runs on a separate thread to send messages.
    This is the "anti-lock" mechanism, preventing the GUI from freezing.
    """
    global sending_paused, sending_cancelled
    phone_numbers = numbers_listbox.get(0, tk.END)
    caption = caption_entry.get("1.0", tk.END).strip()
    progress_bar['maximum'] = len(phone_numbers)
    successful, failed = [], []

    try:
        normalized_media_path = os.path.normpath(media_path)
    except TypeError:
        messagebox.showerror("Error", "No media file was selected.")
        reset_sending_controls()
        return

    for i, number in enumerate(phone_numbers):
        while sending_paused:
            update_status(f"Paused... ({i}/{len(phone_numbers)})", i)
            time.sleep(1)
        if sending_cancelled:
            update_status(f"Process cancelled by user. ({i}/{len(phone_numbers)})", i)
            break
        update_status(f"Sending to {i+1}/{len(phone_numbers)}: {number}", i + 1)
        
        try:
            if media_type == 'image':
                # Image ke liye 'sendwhats_image' bilkul theek kaam karta hai
                pywhatkit.sendwhats_image(number, normalized_media_path, caption, wait_time=20, tab_close=True, close_time=5)
            elif media_type == 'video':
                # Video ke liye 'sendfile' istemal karein taake woh usay process na kare
                # Note: 'sendfile' function caption support nahi karta.
                pywhatkit.sendfile(number, normalized_media_path, wait_time=30, tab_close=True, close_time=5)
            else:
                raise ValueError("No media or unsupported media type selected.")
                
            successful.append(number)
            time.sleep(2)
        except Exception as e:
            print("---------------------------------------------------------")
            print(f"ERROR: Failed to send media to {number}")
            print(f"MEDIA TYPE: {media_type}")
            print(f"FILE PATH: {normalized_media_path}")
            print(f"PYWHATKIT ERROR DETAILS: {e}")
            print("---------------------------------------------------------")
            
            failed.append(f"{number} (Error: See console for details)")
    
    if not sending_cancelled and (successful or failed):
        save_to_history(successful, failed)
    
    if root.winfo_exists():
        root.after(0, update_report_lists, successful, failed)
        final_message = "Process Cancelled!" if sending_cancelled else "Process Complete!"
        messagebox.showinfo("Sending Report", f"{final_message}\n\nSent: {len(successful)}\nFailed: {len(failed)}")
        reset_sending_controls()


def schedule_message_thread(target_time):
    global sending_cancelled, scheduling_active
    scheduling_active = True
    update_ui_for_scheduling(True)

    while datetime.now() < target_time:
        if sending_cancelled:
            update_status("Schedule cancelled by user.")
            reset_sending_controls()
            return
        remaining = target_time - datetime.now()
        days, rem = divmod(remaining.total_seconds(), 86400)
        hours, rem = divmod(rem, 3600)
        mins, secs = divmod(rem, 60)
        status_text = f"Waiting... Time left: {int(hours):02}:{int(mins):02}:{int(secs):02}"
        if days > 0: status_text = f"Waiting... Time left: {int(days)}d {int(hours):02}h"
        update_status(status_text)
        time.sleep(1)

    if not sending_cancelled:
        update_status("Scheduled time reached. Starting process...")
        start_sending_process(scheduled=True)
    scheduling_active = False

def validate_inputs():
    if not numbers_listbox.get(0, tk.END):
        messagebox.showerror("Validation Error", "The recipient list is empty.")
        return False
    if not media_path:
        messagebox.showerror("Validation Error", "Please select a media file (image or video) to send.")
        return False
    if not media_type:
        messagebox.showerror("Validation Error", "The selected media file type is not supported.")
        return False
    return True

def start_sending_process(scheduled=False):
    if not scheduled and not validate_inputs(): return
    global sending_paused, sending_cancelled
    sending_paused = False; sending_cancelled = False
    success_listbox.delete(0, tk.END); fail_listbox.delete(0, tk.END)
    send_button.config(state=tk.DISABLED); schedule_button.config(state=tk.DISABLED)
    pause_button.config(state=tk.NORMAL); resume_button.config(state=tk.DISABLED)
    cancel_button.config(state=tk.NORMAL)
    progress_bar['value'] = 0
    status_label.config(text="Starting process...")
    if not scheduled:
        messagebox.showinfo("Process Starting", f"Sending to {len(numbers_listbox.get(0, tk.END))} numbers.\n\nDo not close your browser.")
    threading.Thread(target=send_message_thread, daemon=True).start()

def start_scheduling_process():
    if not validate_inputs(): return
    
    date_str = schedule_date_entry.get().strip()
    hour_str = schedule_hour_combo.get()
    min_str = schedule_min_combo.get()

    if not date_str or not hour_str or not min_str:
        messagebox.showerror("Input Error", "Please provide a complete date and time for scheduling.")
        return
        
    try:
        target_time = datetime.strptime(f"{date_str} {hour_str}:{min_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        messagebox.showerror("Format Error", "Invalid date or time format.\nPlease use YYYY-MM-DD for date.")
        return

    if target_time < datetime.now():
        messagebox.showerror("Time Error", "Scheduled time must be in the future.")
        return

    global sending_cancelled
    sending_cancelled = False
    threading.Thread(target=schedule_message_thread, args=(target_time,), daemon=True).start()

def pause_sending():
    global sending_paused
    sending_paused = True
    pause_button.config(state=tk.DISABLED)
    resume_button.config(state=tk.NORMAL)

def resume_sending():
    global sending_paused
    sending_paused = False
    pause_button.config(state=tk.NORMAL)
    resume_button.config(state=tk.DISABLED)

def cancel_action():
    global sending_cancelled
    action = "schedule" if scheduling_active else "sending process"
    if messagebox.askyesno("Confirm", f"Are you sure you want to cancel the current {action}?"):
        sending_cancelled = True
        if scheduling_active:
             reset_sending_controls()

def reset_sending_controls():
    global sending_paused, sending_cancelled, scheduling_active
    if root.winfo_exists():
        sending_paused = False; sending_cancelled = False; scheduling_active = False
        root.after(0, update_ui_for_scheduling, False)
        root.after(0, lambda: status_label.config(text="Waiting for input..."))
        root.after(0, update_dashboard_analytics)

def update_ui_for_scheduling(is_scheduling):
    if root.winfo_exists():
        state = tk.DISABLED if is_scheduling else tk.NORMAL
        send_button.config(state=state)
        schedule_button.config(state=state)
        pause_button.config(state=tk.DISABLED)
        resume_button.config(state=tk.DISABLED)
        cancel_button.config(state=tk.NORMAL if is_scheduling else tk.DISABLED)


# ==============================================================================
# GUI Setup
# ==============================================================================
root = tk.Tk(); root.title("WhatsApp Bulk Sender"); root.geometry("850x700"); root.configure(bg="#ECE5DD")
BG_COLOR="#ECE5DD"; NAV_BG_COLOR="#075E54"; NAV_ACTIVE_BG_COLOR="#128C7E"; TITLE_COLOR="#128C7E"; TEXT_COLOR="#000000"
style = ttk.Style(); style.theme_use('clam')
style.configure("TFrame", background=BG_COLOR)
style.configure("App.TFrame", background=BG_COLOR)
style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=('Helvetica', 10))
style.configure("TLabelFrame", background=BG_COLOR, bordercolor=TITLE_COLOR, relief="solid")
style.configure("TLabelFrame.Label", background=BG_COLOR, foreground=TITLE_COLOR, font=('Helvetica', 11, 'bold'))

for btn_style, color, active_color, disabled_color in [
    ("Send.TButton", "#25D366", "#1DAA53", "#B0E1B8"), ("Pause.TButton", "#FFC107", "#E0A800", "#FFE9A9"),
    ("Resume.TButton", "#17A2B8", "#138496", "#A4DDE6"), ("Cancel.TButton", "#DC3545", "#C82333", "#F2B1B7"),
    ("Schedule.TButton", "#6C757D", "#5A6268", "#C8CBCE")
]:
    style.configure(btn_style, foreground="white", background=color, font=('Helvetica', 10, 'bold'), borderwidth=0)
    style.map(btn_style, background=[('active', active_color), ('disabled', disabled_color)])

style.configure("Std.TButton", background="white", foreground=TITLE_COLOR, font=('Helvetica', 10, 'bold'), borderwidth=1, bordercolor=TITLE_COLOR, relief='solid')
style.map("Std.TButton", background=[('active', '#E0E0E0')])

nav_frame = tk.Frame(root, bg=NAV_BG_COLOR, width=180); nav_frame.pack(side="left", fill="y"); nav_frame.pack_propagate(False)
main_frame = tk.Frame(root, bg=BG_COLOR); main_frame.pack(side="left", fill="both", expand=True)
content_frames = {}
for F in ("Dashboard", "Send Message"):
    frame = ttk.Frame(main_frame, style="App.TFrame"); content_frames[F] = frame; frame.grid(row=0, column=0, sticky="nsew")
main_frame.grid_rowconfigure(0, weight=1); main_frame.grid_columnconfigure(0, weight=1)

def show_frame(frame_name):
    frame = content_frames[frame_name]; frame.tkraise()
    for name, button in nav_buttons.items():
        button.config(bg=NAV_ACTIVE_BG_COLOR if name == frame_name else NAV_BG_COLOR)
    if frame_name == "Dashboard": update_dashboard_analytics()

app_title = tk.Label(nav_frame, text="WhatsApp Sender", font=('Helvetica', 14, 'bold'), bg=NAV_BG_COLOR, fg='white', pady=15, wraplength=160); app_title.pack()
nav_buttons = {}
for option in ["Dashboard", "Send Message", "Manage Groups"]:
    cmd = open_group_manager if option == "Manage Groups" else lambda o=option: show_frame(o)
    btn = tk.Button(nav_frame, text=option, font=('Helvetica', 11, 'bold'), bg=NAV_BG_COLOR, fg='white', relief='flat', anchor='w', padx=20, pady=10, command=cmd)
    btn.pack(fill='x'); nav_buttons[option] = btn

dashboard_frame = content_frames["Dashboard"]
tk.Label(dashboard_frame, text="Message Analytics Dashboard", font=('Helvetica', 18, 'bold'), bg=BG_COLOR, fg=TITLE_COLOR).pack(pady=(20, 10))
tk.Label(dashboard_frame, text="Lifetime statistics from all your campaigns.", font=('Helvetica', 11), bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(0, 30))
stats_frame = ttk.Frame(dashboard_frame, style="App.TFrame"); stats_frame.pack(pady=20, padx=30, fill='x')
labels_data = ["Total Messages Sent:", "Total Campaigns:", "Last Campaign Date:", "Total Saved Groups:"]
dashboard_labels = {}
for i, text in enumerate(labels_data):
    tk.Label(stats_frame, text=text, font=('Helvetica', 14), bg=BG_COLOR).grid(row=i, column=0, padx=10, pady=5, sticky='w')
    label = tk.Label(stats_frame, text="0", font=('Helvetica', 14, 'bold'), bg=BG_COLOR, fg=TITLE_COLOR)
    label.grid(row=i, column=1, padx=10, pady=5, sticky='w')
    dashboard_labels[text] = label
dashboard_sent_count_label = dashboard_labels["Total Messages Sent:"]
dashboard_campaign_count_label = dashboard_labels["Total Campaigns:"]
dashboard_last_campaign_label = dashboard_labels["Last Campaign Date:"]
dashboard_group_count_label = dashboard_labels["Total Saved Groups:"]

sender_container = content_frames["Send Message"]
canvas = tk.Canvas(sender_container, bg=BG_COLOR, highlightthickness=0); scrollbar = ttk.Scrollbar(sender_container, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set); canvas.pack(side="left", fill="both", expand=True); scrollbar.pack(side="right", fill="y")
scrollable_frame = ttk.Frame(canvas, style="App.TFrame", padding=(20,20,40,20))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

group_frame = ttk.LabelFrame(scrollable_frame, text="Load Group", padding="10"); group_frame.pack(fill='x', padx=5, pady=(0, 15))
groups_combobox = ttk.Combobox(group_frame, state="readonly", font=('Helvetica', 10)); groups_combobox.pack(side='left', fill='x', expand=True, padx=(0, 5))
ttk.Button(group_frame, text="Load", command=load_selected_group_into_main_list, style="Std.TButton").pack(side='left')

phone_label = ttk.Label(scrollable_frame, text="Recipients"); phone_label.pack(fill="x", padx=5, pady=(0, 5), anchor='w')
phone_frame = ttk.Frame(scrollable_frame); phone_frame.pack(fill='x', padx=5)
phone_entry = tk.Entry(phone_frame, font=('Helvetica', 10), bg='white', fg=TEXT_COLOR, relief='solid', borderwidth=1, insertbackground=TEXT_COLOR); phone_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
ttk.Button(phone_frame, text="Add", command=add_number, style="Std.TButton").pack(side='right')

list_frame = ttk.Frame(scrollable_frame); list_frame.pack(fill='both', expand=True, padx=5, pady=5)
numbers_listbox = tk.Listbox(list_frame, height=5, font=('Helvetica', 10), bg='white', fg=TEXT_COLOR, relief='solid', borderwidth=1, selectmode=tk.EXTENDED); numbers_listbox.pack(side='left', fill='both', expand=True)
list_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=numbers_listbox.yview); list_scrollbar.pack(side='right', fill='y'); numbers_listbox.config(yscrollcommand=list_scrollbar.set)

list_actions_frame = ttk.Frame(scrollable_frame)
list_actions_frame.pack(fill='x', padx=5, pady=5)
ttk.Button(list_actions_frame, text="Import from File (Excel/CSV)", command=import_numbers_to_main_list, style="Std.TButton").pack(side='left', expand=True, fill='x', padx=(0, 5))
ttk.Button(list_actions_frame, text="Remove Selected", command=remove_number, style="Std.TButton").pack(side='left', expand=True, fill='x', padx=(5, 0))


media_button_frame = ttk.Frame(scrollable_frame)
media_button_frame.pack(pady=(15, 5))
ttk.Button(media_button_frame, text="Select Image File", command=select_image, style="Std.TButton").pack(side='left', padx=5)
ttk.Button(media_button_frame, text="Select Video File", command=select_video, style="Std.TButton").pack(side='left', padx=5)

filename_label = ttk.Label(scrollable_frame, text="No media selected", foreground="grey", font=('Helvetica', 9)); filename_label.pack()

ttk.Label(scrollable_frame, text="Caption (for images only):").pack(fill="x", padx=5, pady=(15, 5), anchor='w')
caption_entry = tk.Text(scrollable_frame, height=2, font=('Helvetica', 10), bg='white', fg=TEXT_COLOR, relief='solid', borderwidth=1, insertbackground=TEXT_COLOR); caption_entry.pack(fill="x", padx=5)

schedule_frame = ttk.LabelFrame(scrollable_frame, text="Schedule Message", padding="10"); schedule_frame.pack(fill='x', padx=5, pady=(20, 5))
ttk.Label(schedule_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=(0,5))
schedule_date_entry = ttk.Entry(schedule_frame); schedule_date_entry.grid(row=0, column=1, padx=5)
schedule_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
ttk.Label(schedule_frame, text="Time (24h):").grid(row=0, column=2, padx=(10,5))
schedule_hour_combo = ttk.Combobox(schedule_frame, width=5, values=[f"{h:02}" for h in range(24)]); schedule_hour_combo.grid(row=0, column=3)
schedule_min_combo = ttk.Combobox(schedule_frame, width=5, values=[f"{m:02}" for m in range(60)]); schedule_min_combo.grid(row=0, column=4, padx=5)
schedule_hour_combo.set(datetime.now().strftime("%H")); schedule_min_combo.set(f"{(datetime.now().minute + 2) % 60:02}")

control_frame = ttk.Frame(scrollable_frame); control_frame.pack(pady=(10, 10))
send_button = ttk.Button(control_frame, text="Send Now", style="Send.TButton", command=start_sending_process); send_button.grid(row=0, column=0, padx=5, ipady=3)
schedule_button = ttk.Button(control_frame, text="Schedule", style="Schedule.TButton", command=start_scheduling_process); schedule_button.grid(row=0, column=1, padx=5, ipady=3)
pause_button = ttk.Button(control_frame, text="Pause", style="Pause.TButton", command=pause_sending, state=tk.DISABLED); pause_button.grid(row=0, column=2, padx=5, ipady=3)
resume_button = ttk.Button(control_frame, text="Resume", style="Resume.TButton", command=resume_sending, state=tk.DISABLED); resume_button.grid(row=0, column=3, padx=5, ipady=3)
cancel_button = ttk.Button(control_frame, text="Cancel", style="Cancel.TButton", command=cancel_action, state=tk.DISABLED); cancel_button.grid(row=0, column=4, padx=5, ipady=3)

status_label = ttk.Label(scrollable_frame, text="Waiting for input...", font=('Helvetica', 9)); status_label.pack(fill="x", padx=5)
progress_bar = ttk.Progressbar(scrollable_frame, orient='horizontal', mode='determinate'); progress_bar.pack(fill='x', padx=5, pady=5)

report_frame = ttk.LabelFrame(scrollable_frame, text="Sending Report (Current Campaign)", padding="10"); report_frame.pack(fill='x', expand=True, padx=5, pady=(15, 5))
report_container = ttk.Frame(report_frame); report_container.pack(fill='both', expand=True); report_container.columnconfigure(0, weight=1); report_container.columnconfigure(1, weight=1)
success_frame = ttk.Frame(report_container); success_frame.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
ttk.Label(success_frame, text="✅ Sent To:").pack(anchor="w")
success_listbox = tk.Listbox(success_frame, height=4, font=('Helvetica', 9), bg='#DCF8C6', fg=TEXT_COLOR, relief='solid', borderwidth=1); success_listbox.pack(side='left', fill='both', expand=True)
fail_frame = ttk.Frame(report_container); fail_frame.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
ttk.Label(fail_frame, text="❌ Failed To Send To:").pack(anchor="w")
fail_listbox = tk.Listbox(fail_frame, height=4, font=('Helvetica', 9), bg='#FFDEDE', fg=TEXT_COLOR, relief='solid', borderwidth=1); fail_listbox.pack(side='left', fill='both', expand=True)

# ==============================================================================
# --- Application Start ---
# ==============================================================================
if __name__ == "__main__":
    # Application ko direct start karein
    show_frame("Dashboard")
    update_main_groups_dropdown()
    update_dashboard_analytics()
    root.mainloop()