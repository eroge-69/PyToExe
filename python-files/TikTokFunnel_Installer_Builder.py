import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import shutil

def select_iss_file():
    filepath = filedialog.askopenfilename(filetypes=[("Inno Setup Script", "*.iss")])
    if filepath:
        iss_path.set(filepath)

def select_output_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_path.set(folder)

def compile_installer():
    iss_file = iss_path.get()
    output_dir = output_path.get()

    if not iss_file or not output_dir:
        messagebox.showerror("Fehler", "Bitte .iss-Datei und Ausgabeverzeichnis auswählen.")
        return

    try:
        # Inno Setup Compiler suchen (Standardpfad)
        iscc_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
        if not os.path.exists(iscc_path):
            raise FileNotFoundError("ISCC.exe nicht gefunden. Stelle sicher, dass Inno Setup installiert ist.")

        # Kompilierung
        subprocess.run([iscc_path, iss_file], check=True)

        # Installer-Datei verschieben
        output_filename = "TikTokFunnel_Setup.exe"
        documents_dir = os.path.expanduser("~/Documents")
        built_installer = os.path.join(documents_dir, output_filename)

        if os.path.exists(built_installer):
            shutil.move(built_installer, os.path.join(output_dir, output_filename))
            messagebox.showinfo("Erfolg", f"Installer erfolgreich erstellt:
{output_filename}")
        else:
            messagebox.showerror("Fehler", "Installer konnte nicht gefunden werden.")

    except Exception as e:
        messagebox.showerror("Fehler", str(e))

# GUI erstellen
root = tk.Tk()
root.title("TikTok Funnel – Installer Generator")

iss_path = tk.StringVar()
output_path = tk.StringVar()

tk.Label(root, text="Inno Setup .iss-Datei:").pack(pady=(10,0))
tk.Entry(root, textvariable=iss_path, width=60).pack()
tk.Button(root, text="Durchsuchen", command=select_iss_file).pack()

tk.Label(root, text="Zielordner für Setup-Datei:").pack(pady=(10,0))
tk.Entry(root, textvariable=output_path, width=60).pack()
tk.Button(root, text="Ordner wählen", command=select_output_folder).pack()

tk.Button(root, text="Installer erstellen", command=compile_installer, bg="#4CAF50", fg="white", padx=10, pady=5).pack(pady=20)

root.mainloop()