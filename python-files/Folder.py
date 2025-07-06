import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def select_source():
    folder = filedialog.askdirectory()
    if folder:
        source_var.set(folder)

def select_dest_base():
    folder = filedialog.askdirectory()
    if folder:
        dest_base_var.set(folder)

def select_text_file():
    file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file:
        text_file_var.set(file)

def clear_log():
    """Clear the contents of the log box."""
    log_text.delete("1.0", tk.END)

# ---------------------------------------------------------------------------
# Core functionality
# ---------------------------------------------------------------------------

def create_project_folder():
    """Validate inputs, build the base project structure, and start copying."""
    project_name = project_name_var.get().strip()
    if not project_name:
        messagebox.showerror("Error", "Please enter a project name.")
        return

    src = source_var.get()
    dest_base = dest_base_var.get()
    txt_file = text_file_var.get()

    # Validate base paths early
    if not os.path.isdir(src):
        messagebox.showerror("Error", "Invalid source folder path.")
        return
    if not os.path.isdir(dest_base):
        messagebox.showerror("Error", "Invalid destination base folder path.")
        return
    if not os.path.isfile(txt_file):
        messagebox.showerror("Error", "Invalid text file path.")
        return

    # Create project folder
    project_folder = os.path.join(dest_base, project_name)
    os.makedirs(project_folder, exist_ok=True)

    # Create default sub‑folders
    default_subfolders = [
        "ASSETS",
        "DAILIES",
        "FINAL_OUTPUT",
        "FROM_CILENT",
        "PREPRODUCTION",
        "PROD",
        "SCAN",
        "SHOT_PROD",
        "TO_CLIENT",
        "WORKFILES",
    ]

    for sub in default_subfolders:
        os.makedirs(os.path.join(project_folder, sub), exist_ok=True)

    # Log creation of base project structure
    clear_log()
    log("Project '%s' created with default sub‑folders.\n" % project_name)

    # Kick off the copy process
    shot_prod_folder = os.path.join(project_folder, "SHOT_PROD")
    copy_folders(shot_prod_folder)


def copy_folders(shot_prod_folder):
    """Read shot names from text file and copy assets into each."""
    src = source_var.get()
    txt_file = text_file_var.get()

    try:
        with open(txt_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as exc:
        messagebox.showerror("Error", f"Unable to read text file:\n{exc}")
        return

    total = len(lines)
    if total == 0:
        messagebox.showinfo("Nothing to do", "The text file is empty.")
        return

    progress_bar["maximum"] = total
    progress_bar["value"] = 0
    app.update_idletasks()

    for count, folder_name in enumerate(lines, start=1):
        dest_folder = os.path.join(shot_prod_folder, folder_name)

        # Skip / overwrite prompt if destination exists
        if os.path.exists(dest_folder):
            answer = messagebox.askyesnocancel(
                "Folder already exists",
                f"The folder '{dest_folder}' already exists.\n\nYes → Overwrite contents\nNo  → Skip this folder\nCancel → Abort the entire copy process",
            )
            if answer is None:  # Cancel
                log("\nCopy process aborted by user.\n")
                return
            elif answer is False:  # Skip
                log(f"[{count}/{total}] Skipped existing folder: {dest_folder}\n")
                progress_bar.step()
                continue
            # If answer is True, we proceed and overwrite

        try:
            os.makedirs(dest_folder, exist_ok=True)
            log(f"[{count}/{total}] Processing folder: {dest_folder}\n")
            copy_tree_or_files(src, dest_folder)
            log("    Copy completed.\n")
        except Exception as exc:
            log("    ERROR: %s\n" % exc)

        progress_bar.step()
        app.update_idletasks()

    log("\nAll done! Copying process completed successfully.")


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def log(msg: str):
    """Write a message to the log box and auto‑scroll to the end."""
    log_text.insert(tk.END, msg)
    log_text.see(tk.END)


def copy_tree_or_files(src_dir: str, dest_dir: str):
    """Copy the entire folder tree or individual files from src_dir into dest_dir."""
    # shutil.copytree cannot copy into an existing directory unless Python 3.8+
    # with dirs_exist_ok=True.
    try:
        shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
    except Exception:
        # Fallback: walk and copy each item (slower but more granular error handling)
        for root, dirs, files in os.walk(src_dir):
            rel_root = os.path.relpath(root, src_dir)
            target_root = os.path.join(dest_dir, rel_root)
            os.makedirs(target_root, exist_ok=True)
            for d in dirs:
                os.makedirs(os.path.join(target_root, d), exist_ok=True)
            for file in files:
                src_path = os.path.join(root, file)
                dst_path = os.path.join(target_root, file)
                try:
                    shutil.copy2(src_path, dst_path)
                except Exception as file_exc:
                    log(f"        Failed to copy {src_path}: {file_exc}\n")


# ---------------------------------------------------------------------------
# GUI setup
# ---------------------------------------------------------------------------

app = tk.Tk()
app.title("Reflection Project Creation")
app.geometry("700x550")

# Optional: Set window icon (auto path detection)
try:
    icon_path = os.path.join(os.path.dirname(__file__), "logo.ico")
    if os.path.exists(icon_path):
        app.iconbitmap(icon_path)
except Exception:
    pass  # Ignore icon issues in cross‑platform scenarios

# StringVars
source_var = tk.StringVar()
dest_base_var = tk.StringVar()
text_file_var = tk.StringVar()
project_name_var = tk.StringVar()

# Layout helpers
PAD_X = 6
PAD_Y = 4
ENTRY_WIDTH = 60

# Project name
row = 0
label_project = tk.Label(app, text="Project Name:")
label_project.grid(row=row, column=0, sticky="w", padx=PAD_X, pady=PAD_Y)
entry_project = tk.Entry(app, textvariable=project_name_var, width=ENTRY_WIDTH)
entry_project.grid(row=row, column=1, sticky="we", padx=PAD_X, pady=PAD_Y)
row += 1

# Source folder
tk.Label(app, text="Sub‑Folders Source:").grid(row=row, column=0, sticky="w", padx=PAD_X, pady=PAD_Y)
entry_source = tk.Entry(app, textvariable=source_var, width=ENTRY_WIDTH)
entry_source.grid(row=row, column=1, sticky="we", padx=PAD_X, pady=PAD_Y)
tk.Button(app, text="Browse", command=select_source).grid(row=row, column=2, padx=PAD_X, pady=PAD_Y)
row += 1

# Destination base folder
tk.Label(app, text="Destination Base Folder:").grid(row=row, column=0, sticky="w", padx=PAD_X, pady=PAD_Y)
entry_dest = tk.Entry(app, textvariable=dest_base_var, width=ENTRY_WIDTH)
entry_dest.grid(row=row, column=1, sticky="we", padx=PAD_X, pady=PAD_Y)
tk.Button(app, text="Browse", command=select_dest_base).grid(row=row, column=2, padx=PAD_X, pady=PAD_Y)
row += 1

# Text file with shot names
tk.Label(app, text="Text File with Folder Names:").grid(row=row, column=0, sticky="w", padx=PAD_X, pady=PAD_Y)
entry_text_file = tk.Entry(app, textvariable=text_file_var, width=ENTRY_WIDTH)
entry_text_file.grid(row=row, column=1, sticky="we", padx=PAD_X, pady=PAD_Y)
tk.Button(app, text="Browse", command=select_text_file).grid(row=row, column=2, padx=PAD_X, pady=PAD_Y)
row += 1

# Action buttons
btn_create = tk.Button(app, text="Create Project & Start Copying", command=create_project_folder, bg="#d9534f", fg="white")
btn_create.grid(row=row, column=0, columnspan=2, sticky="we", padx=PAD_X, pady=(PAD_Y * 2))
btn_clear = tk.Button(app, text="Clear Log", command=clear_log)
btn_clear.grid(row=row, column=2, padx=PAD_X, pady=(PAD_Y * 2))
row += 1

# Progress bar
progress_bar = ttk.Progressbar(app, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=row, column=0, columnspan=3, sticky="we", padx=PAD_X, pady=(0, PAD_Y))
row += 1

# Scrolled text log
log_text = scrolledtext.ScrolledText(app, width=90, height=15)
log_text.grid(row=row, column=0, columnspan=3, padx=PAD_X, pady=PAD_Y)

# Make the UI responsive
app.columnconfigure(1, weight=1)

# ---------------------------------------------------------------------------
# Start the Tkinter main loop
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.mainloop()