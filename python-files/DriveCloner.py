import os
import shutil
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from concurrent.futures import ThreadPoolExecutor, as_completed

# Global control flags
cancel_flag = False
pause_event = threading.Event()
pause_event.set()
lock = threading.Lock()

bytes_copied = 0
start_time = 0


def browse_source():
    folder = filedialog.askdirectory(title="Select Source Directory")
    if folder:
        source_entry.delete(0, tk.END)
        source_entry.insert(0, folder)


def browse_destination():
    folder = filedialog.askdirectory(title="Select Destination Directory")
    if folder:
        dest_entry.delete(0, tk.END)
        dest_entry.insert(0, folder)


def count_files_and_size(directory):
    total_files = 0
    total_size = 0
    for root, _, files in os.walk(directory):
        total_files += len(files)
        for f in files:
            try:
                total_size += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total_files, total_size


def copy_directory():
    global cancel_flag, bytes_copied, start_time
    cancel_flag = False
    bytes_copied = 0
    pause_event.set()
    start_time = time.time()
    status_label.config(text="Copying...", fg="blue")
    speed_label.config(text="Speed: 0 MB/s")
    thread = threading.Thread(target=copy_directory_thread, daemon=True)
    thread.start()


def cancel_copy():
    global cancel_flag
    cancel_flag = True
    status_label.config(text="Cancelling...", fg="orange")


def pause_copy():
    pause_event.clear()
    status_label.config(text="Paused", fg="orange")


def resume_copy():
    pause_event.set()
    status_label.config(text="Copying...", fg="blue")


def copy_file(src_file, dest_file):
    global cancel_flag, bytes_copied

    if cancel_flag:
        return False

    pause_event.wait()

    if os.path.exists(dest_file):
        if os.path.getsize(src_file) == os.path.getsize(dest_file):
            return True

    shutil.copy2(src_file, dest_file)

    file_size = os.path.getsize(dest_file)
    with lock:
        bytes_copied += file_size

    return True


def copy_directory_thread():
    global cancel_flag, start_time, bytes_copied

    source = source_entry.get()
    destination = dest_entry.get()

    if not source or not destination:
        messagebox.showwarning("Warning", "Please select both source and destination directories.")
        status_label.config(text="Ready", fg="black")
        return

    dest_path = os.path.join(destination, os.path.basename(source))
    os.makedirs(dest_path, exist_ok=True)

    try:
        file_tasks = []
        for root_dir, _, files in os.walk(source):
            rel_path = os.path.relpath(root_dir, source)
            dest_dir = os.path.join(dest_path, rel_path)
            os.makedirs(dest_dir, exist_ok=True)
            for file in files:
                src_file = os.path.join(root_dir, file)
                dest_file = os.path.join(dest_dir, file)
                file_tasks.append((src_file, dest_file))

        total_files, total_size = count_files_and_size(source)
        progress_bar["maximum"] = total_files
        progress_bar["value"] = 0
        percent_label.config(text="0%")

        copied_files = 0
        last_speed_update_time = time.time()

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(copy_file, src, dst): (src, dst) for src, dst in file_tasks}

            for future in as_completed(futures):
                if cancel_flag:
                    status_label.config(text="Aborted", fg="red")
                    messagebox.showinfo("Aborted", "Copy operation was aborted.")
                    return

                result = future.result()
                if result:
                    with lock:
                        copied_files += 1
                        progress_bar["value"] = copied_files
                        percent = int((copied_files / total_files) * 100)
                        percent_label.config(text=f"{percent}%")

                        current_time = time.time()
                        if current_time - last_speed_update_time >= 1.0:
                            elapsed = current_time - start_time
                            if elapsed > 0:
                                speed = (bytes_copied / (1024 * 1024)) / elapsed
                                speed_label.config(text=f"Speed: {speed:.2f} MB/s")
                            last_speed_update_time = 0.2

                        root.update_idletasks()

        if not cancel_flag:
            status_label.config(text="Completed", fg="green")
            speed_label.config(text="Speed: 0 MB/s")
            messagebox.showinfo("Success", f"Directory copied successfully to:\n{dest_path}")

    except Exception as e:
        status_label.config(text="Error", fg="red")
        messagebox.showerror("Error", f"An error occurred:\n{e}")


# GUI setup
root = tk.Tk()
root.title(" Bill's Directory Copier ©2025")
root.geometry("350x350")

# Source selection
tk.Label(root, text="Source:").pack(pady=5)
source_entry = tk.Entry(root, width=50)
source_entry.pack()
tk.Button(root, text="Browse", command=browse_source, bg="green", fg="white").pack(pady=2)


# Destination selection
tk.Label(root, text="Destination:").pack(pady=5)
dest_entry = tk.Entry(root, width=50)
dest_entry.pack()
tk.Button(root, text="Browse", command=browse_destination, bg="green", fg="white").pack(pady=2)

# Progress bar + percentage
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

percent_label = tk.Label(root, text="0%", font=("Arial", 12))
percent_label.pack()

# Buttons frame
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Copy", command=copy_directory, bg="green", fg="white").pack(side="left", padx=5)
tk.Button(btn_frame, text="Pause", command=pause_copy, bg="orange", fg="white").pack(side="left", padx=5)
tk.Button(btn_frame, text="Resume", command=resume_copy, bg="blue", fg="white").pack(side="left", padx=5)
tk.Button(btn_frame, text="Abort", command=cancel_copy, bg="red", fg="white").pack(side="left", padx=5)

# Status label
status_label = tk.Label(root, text="Ready", font=("Arial", 12), fg="black")
status_label.pack(pady=5)

# Speed label
speed_label = tk.Label(root, text="Speed: 0 MB/s", font=("Arial", 12), fg="purple")
speed_label.pack(pady=5)

root.mainloop()
