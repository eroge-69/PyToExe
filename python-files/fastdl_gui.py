import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import bz2

# --- DARK MODE FARBSKALA ---
BG_DARK = "#222831"
BG_CARD = "#393e46"
FG_LIGHT = "#eeeeee"
ACCENT = "#00adb5"
BTN_HOVER = "#2d353e"

# ---- FASTDL TOOL ----

server_files_list = []
fastdl_files_list = []

def compress_file(src, dest):
    with open(src, 'rb') as f_in, bz2.open(dest + '.bz2', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

def copy_structure_and_compress(src, server_base, fastdl_base):
    server_files_list.clear()
    fastdl_files_list.clear()
    if os.path.isfile(src):
        rel_path = os.path.basename(src)
        server_path = os.path.join(server_base, rel_path)
        fastdl_path = os.path.join(fastdl_base, rel_path)
        os.makedirs(os.path.dirname(server_path), exist_ok=True)
        os.makedirs(os.path.dirname(fastdl_path), exist_ok=True)
        shutil.copy2(src, server_path)
        compress_file(src, fastdl_path)
        server_files_list.append(rel_path.replace("\\", "/"))
        fastdl_files_list.append((rel_path + ".bz2").replace("\\", "/"))
    else:
        src_parent = os.path.dirname(src)
        for root, dirs, files in os.walk(src):
            rel_dir = os.path.relpath(root, src_parent)
            for file in files:
                rel_file_path = os.path.join(rel_dir, file).replace("\\", "/")
                src_file = os.path.join(root, file)
                server_file = os.path.join(server_base, rel_dir, file)
                fastdl_file = os.path.join(fastdl_base, rel_dir, file)
                os.makedirs(os.path.dirname(server_file), exist_ok=True)
                os.makedirs(os.path.dirname(fastdl_file), exist_ok=True)
                shutil.copy2(src_file, server_file)
                compress_file(src_file, fastdl_file)
                server_files_list.append(rel_file_path)
                fastdl_files_list.append(rel_file_path + ".bz2")

def write_filelist(dest):
    filelist_path = os.path.join(dest, "filelist.txt")
    with open(filelist_path, "w", encoding="utf-8") as f:
        f.write("Server:\n")
        for line in server_files_list:
            f.write(f"{line}\n")
        f.write("\nFastDL:\n")
        for line in fastdl_files_list:
            f.write(f"{line}\n")
    return filelist_path

# --- GUI FUNKTIONEN ---
def show_menu():
    clear_frame()
    main_frame.config(bg=BG_DARK)
    tk.Label(main_frame, text="FastDL TOOLKIT", font=("Segoe UI", 28, "bold"), bg=BG_DARK, fg=ACCENT).pack(pady=(50, 8))
    tk.Label(main_frame, text="Willkommen!", font=("Segoe UI", 16), bg=BG_DARK, fg=FG_LIGHT).pack(pady=(0, 36))
    style_button(
        tk.Button(main_frame, text="FastDL Compiler", font=("Segoe UI", 16), width=20, height=2, 
                  command=show_compiler)
    ).pack(pady=12)

def show_compiler():
    clear_frame()
    main_frame.config(bg=BG_CARD)
    tk.Label(main_frame, text="FastDL Compiler", font=("Segoe UI", 22, "bold"), bg=BG_CARD, fg=ACCENT).pack(pady=(30,10), anchor="w", padx=28)

    # Quelle (Label und Entry in einer Zeile, linksbündig)
    row = tk.Frame(main_frame, bg=BG_CARD)
    row.pack(padx=28, anchor="w")
    tk.Label(row, text="Quelle (Datei oder Ordner):", font=("Segoe UI", 12), bg=BG_CARD, fg=FG_LIGHT).pack(side="left")
    
    entry_row = tk.Frame(main_frame, bg=BG_CARD)
    entry_row.pack(padx=28, pady=(0,0), anchor="w")
    src_entry = tk.Entry(entry_row, textvariable=source_var, width=54, font=("Segoe UI", 11), 
                         bg=BG_DARK, fg=FG_LIGHT, insertbackground=FG_LIGHT, borderwidth=2, relief="groove")
    src_entry.pack(side="left")

    # Buttons direkt UNTER dem Entry und linksbündig, in einer eigenen Zeile
    src_btn_frame = tk.Frame(main_frame, bg=BG_CARD)
    src_btn_frame.pack(padx=28, anchor="w", pady=(0,3))
    style_button(
        tk.Button(src_btn_frame, text="Datei auswählen", command=select_source_file)
    ).pack(side="left", padx=(0,7))
    style_button(
        tk.Button(src_btn_frame, text="Ordner auswählen", command=select_source_folder)
    ).pack(side="left", padx=(0,7))

    # Ziel
    dest_row = tk.Frame(main_frame, bg=BG_CARD)
    dest_row.pack(padx=28, pady=(10,0), anchor="w")
    tk.Label(dest_row, text="Zielordner:", font=("Segoe UI", 12), bg=BG_CARD, fg=FG_LIGHT).pack(side="left")
    
    dest_entry_row = tk.Frame(main_frame, bg=BG_CARD)
    dest_entry_row.pack(padx=28, anchor="w")
    dest_entry = tk.Entry(dest_entry_row, textvariable=dest_var, width=54, font=("Segoe UI", 11), 
                          bg=BG_DARK, fg=FG_LIGHT, insertbackground=FG_LIGHT, borderwidth=2, relief="groove")
    dest_entry.pack(side="left")
    style_button(
        tk.Button(dest_entry_row, text="Ziel auswählen", command=select_dest)
    ).pack(side="left", padx=(7,0))

    # Checkbox für Listenfunktion
    check_row = tk.Frame(main_frame, bg=BG_CARD)
    check_row.pack(padx=28, pady=(12,0), anchor="w")
    tk.Checkbutton(
        check_row,
        text='Dateiliste (filelist.txt) nach dem Vorgang erstellen',
        variable=filelist_var,
        font=("Segoe UI", 11),
        bg=BG_CARD, fg=FG_LIGHT,
        selectcolor=BG_DARK,
        activebackground=BG_CARD,
        activeforeground=ACCENT
    ).pack(side="left")

    # Start & zurück
    btn_frame = tk.Frame(main_frame, bg=BG_CARD)
    btn_frame.pack(pady=(24, 0))
    style_button(
        tk.Button(btn_frame, text="Start", font=("Segoe UI", 13, "bold"), width=12, height=2, bg=ACCENT, fg=BG_DARK, command=start_process)
    ).pack(side="left", padx=10)
    style_button(
        tk.Button(btn_frame, text="Zurück zum Menü", font=("Segoe UI", 11), width=14, command=show_menu)
    ).pack(side="left", padx=10)

def clear_frame():
    for widget in main_frame.winfo_children():
        widget.destroy()

def style_button(btn):
    btn.configure(bg=BG_DARK, fg=ACCENT, activebackground=BTN_HOVER, activeforeground=FG_LIGHT, 
                  relief="flat", borderwidth=0, font=("Segoe UI", 12))
    def on_enter(e): btn['bg'] = BTN_HOVER
    def on_leave(e): btn['bg'] = BG_DARK
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def select_source_file():
    path = filedialog.askopenfilename(title="Datei auswählen")
    if path:
        source_var.set(path)

def select_source_folder():
    path = filedialog.askdirectory(title="Ordner auswählen")
    if path:
        source_var.set(path)

def select_dest():
    path = filedialog.askdirectory(title="Zielordner auswählen")
    if path:
        dest_var.set(path)

def start_process():
    src = source_var.get()
    dest = dest_var.get()
    if not src or not dest:
        messagebox.showwarning("Fehler", "Bitte Quelle und Ziel auswählen.")
        return
    server_dir = os.path.join(dest, "Server")
    fastdl_dir = os.path.join(dest, "FastDL")
    try:
        copy_structure_and_compress(src, server_dir, fastdl_dir)
        if filelist_var.get():
            write_filelist(dest)
            msg = "Vorgang abgeschlossen!\nQuelle wurde entfernt.\nEine Datei 'filelist.txt' wurde erstellt."
        else:
            msg = "Vorgang abgeschlossen!\nQuelle wurde entfernt."
        try:
            if os.path.isfile(src):
                os.remove(src)
            elif os.path.isdir(src):
                shutil.rmtree(src)
        except Exception as e:
            messagebox.showerror("Fehler beim Löschen", f"Datei/Ordner konnte nicht gelöscht werden:\n{e}")
        messagebox.showinfo("Fertig", msg)
    except Exception as e:
        messagebox.showerror("Fehler", str(e))

# -- ROOT SETUP --
root = tk.Tk()
root.title("FastDL Toolkit")
root.geometry("650x500")
root.configure(bg=BG_DARK)
root.resizable(False, False)

main_frame = tk.Frame(root, bg=BG_DARK)
main_frame.pack(fill="both", expand=True)

source_var = tk.StringVar()
dest_var = tk.StringVar()
filelist_var = tk.BooleanVar(value=True)  # Standard: Listenfunktion aktiv

show_menu()
root.mainloop()
