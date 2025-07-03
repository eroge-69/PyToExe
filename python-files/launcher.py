import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import simpledialog, messagebox
import os
import subprocess
import shutil
import json

CONFIG_FILE = "scorciatoie.json"
NOTEPADPP_PATH = None  # sarà caricato da JSON

def carica_scorciatoie():
    global NOTEPADPP_PATH
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            NOTEPADPP_PATH = data.get("notepadpp_path", r"D:\Program Files\Notepad++\notepad++.exe")
            return data.get("scorciatoie", [])
    except Exception as e:
        messagebox.showerror("Errore", f"Errore caricamento scorciatoie: {e}")
        NOTEPADPP_PATH = r"D:\Program Files\Notepad++\notepad++.exe"
        return []

def sostituisci_parametri(stringa, valore):
    return stringa.replace("|1", valore)

def copia_con_progresso(src, dest, root):
    try:
        filesize = os.path.getsize(src)
        copied = 0
        block_size = 1024 * 1024  # 1 MB

        progress_win = tb.Toplevel(root)
        progress_win.title("Copia in corso...")
        progress_win.geometry("350x90")
        progress_win.resizable(False, False)
        progress_win.transient(root)
        progress_win.grab_set()
        progress_win.configure(bg="#F0F0F0")

        label = tb.Label(progress_win, text=f"Copia {os.path.basename(src)}...", bootstyle="dark")
        label.pack(pady=(15, 5))

        progress = tb.Progressbar(progress_win, orient="horizontal", length=300, mode="determinate", maximum=filesize)
        progress.pack(pady=(0, 10))

        progress_win.update()

        with open(src, "rb") as fsrc, open(dest, "wb") as fdest:
            while True:
                buf = fsrc.read(block_size)
                if not buf:
                    break
                fdest.write(buf)
                copied += len(buf)
                progress['value'] = copied
                progress_win.update_idletasks()

        progress_win.destroy()
        messagebox.showinfo("Successo", f"File copiato in:\n{dest}")
    except Exception as e:
        messagebox.showerror("Errore", str(e))

def esegui_scorciatoia(s, root):
    try:
        tipo = s['tipo']
        parametro_richiesto = "|1" in str(s)

        valore = ""
        if parametro_richiesto:
            valore = simpledialog.askstring("Parametro", "Inserisci il parametro da sostituire:", parent=root)
            if not valore:
                return

        if tipo == 'open':
            base = s.get('basepath', '')
            path_finale = sostituisci_parametri(base, valore)

            if s.get('editor') == "notepadpp":
                subprocess.Popen([NOTEPADPP_PATH, path_finale])
            else:
                os.startfile(path_finale)

        elif tipo == 'copy':
            src = sostituisci_parametri(s['src'], valore)
            dest_folder = sostituisci_parametri(s['dest'], valore)

            if not os.path.exists(src):
                messagebox.showerror("Errore", f"Il file sorgente non esiste:\n{src}")
                return

            nome_file = os.path.basename(src)
            dest = os.path.join(dest_folder, nome_file)

            copia_con_progresso(src, dest, root)

        elif tipo == 'folder':
            path = sostituisci_parametri(s['path'], valore)
            if os.path.isdir(path):
                os.startfile(path)
            else:
                messagebox.showerror("Errore", f"La cartella non esiste:\n{path}")

        else:
            messagebox.showwarning("Attenzione", f"Tipo sconosciuto: {tipo}")
    except Exception as e:
        messagebox.showerror("Errore", str(e))

def main():
    root = tb.Window(themename="darkly")
    root.title("Launcher")
    root.geometry("420x360")
    root.configure(bg="#F0F0F0")
    root.resizable(False, False)

    style = tb.Style()

# Configuro stile bottone personalizzato
    style.configure("Custom.TButton",
                background="#000000",   # sfondo normale nero
                foreground="white",     # testo bianco
                borderwidth=2,          # bordo spesso 2px
                relief="ridge",         # bordo con effetto rilievo
                focuscolor="",          # niente colore bordo focus
                padding=10)

# Definisco mappa per hover e pressione
    style.map("Custom.TButton",
          background=[("active", "#FECA1D"),    # giallo hover
                      ("pressed", "#e5b800")],  # giallo scuro premuto
          foreground=[("active", "black"),
                      ("pressed", "black")],
          bordercolor=[("active", "#FECA1D"),
                       ("pressed", "#e5b800")])
    
    style.configure("My.TFrame", background="#F0F0F0")
    titolo = tb.Label(root, text="Funzioni", font=("Segoe UI", 20, "bold"), bootstyle="inverse-primary")
    titolo.configure(background="#f0f0f0", foreground="black")
    titolo.pack(pady=(20, 15), fill='x')

    scorciatoie = carica_scorciatoie()

    frame_buttons = tb.Frame(root, style="My.TFrame")
    frame_buttons.pack(pady=10, fill='x', padx=30)

    for s in scorciatoie:
        btn = tb.Button(frame_buttons, text=s['nome'], width=35,
                        bootstyle="dark-warning",
                        style="Custom.TButton",
                        padding=(10, 6),
                        command=lambda s=s: esegui_scorciatoia(s, root))
        btn.pack(pady=6)

    root.mainloop()

if __name__ == "__main__":
    main()
