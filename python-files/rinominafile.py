import os
import shutil
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog
import filetype

# === CONFIG ===
NON_TROVATO = "Non_Trovato"

MAGIC_SIGNATURES = {
    b"\xFF\xD8\xFF": "jpg",
    b"\x89PNG": "png",
    b"GIF87a": "gif",
    b"GIF89a": "gif",
    b"BM": "bmp",
    b"II*\x00": "tif",
    b"MM\x00*": "tif",
    b"ftypheic": "heic",
    b"ftypheix": "heic",
    b"ftypisom": "mp4",
    b"ftypmp42": "mp4",
    b"ftypM4V": "m4v",
    b"\x1A\x45\xDF\xA3": "mkv",
    b"RIFF": None,
    b"OggS": "ogg",
    b"fLaC": "flac",
    b"ID3": "mp3",
    b"%PDF": "pdf",
    b"PK\x03\x04": "zip",
    b"Rar!": "rar",
    b"7z\xBC\xAF'": "7z",
    b"\x1F\x8B": "gz",
    b"BZh": "bz2",
    b"ustar": "tar",
    b"ISO": "iso",
    b"SQLite": "sqlite",
    b"\xCA\xFE\xBA\xBE": "class",
}

OFFICE_HINTS = {
    "word/": "docx",
    "ppt/": "pptx",
    "xl/": "xlsx"
}


def rileva_estensione(file_path):
    try:
        with open(file_path, "rb") as f:
            header = f.read(512)
    except:
        return None

    for sig, est in MAGIC_SIGNATURES.items():
        if header.startswith(sig):
            if sig == b"RIFF":
                if b"WAVE" in header[8:16]:
                    return "wav"
                elif b"AVI " in header[8:16]:
                    return "avi"
            if est == "zip":
                try:
                    data = header.decode(errors="ignore")
                    for hint, real_ext in OFFICE_HINTS.items():
                        if hint in data:
                            return real_ext
                except:
                    pass
            return est

    kind = filetype.guess(file_path)
    if kind is not None:
        return kind.extension

    return None


def genera_nome_unico(path):
    counter = 1
    new_path = path
    while new_path.exists():
        new_path = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        counter += 1
    return new_path


def rinomina_file(file_path, nuova_estensione, log_callback):
    original = Path(file_path)
    new_name = original.with_suffix(f".{nuova_estensione}")
    if new_name != original:
        new_name = genera_nome_unico(new_name)
        try:
            os.rename(original, new_name)
            log_callback(f"[✔] {original.name} → {new_name.name}")
        except Exception as e:
            log_callback(f"[❌] Errore nel rinominare {original.name}: {e}")


def sposta_non_trovato(file_path, base_dir, log_callback):
    destinazione_dir = Path(base_dir) / NON_TROVATO
    destinazione_dir.mkdir(exist_ok=True)
    destinazione = genera_nome_unico(destinazione_dir / Path(file_path).name)
    try:
        shutil.move(file_path, destinazione)
        log_callback(f"[⚠] Non riconosciuto: {file_path} → {destinazione}")
    except Exception as e:
        log_callback(f"[❌] Errore nello spostare {file_path}: {e}")


class AnalizzatoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizzatore file")
        self.stop_flag = False

        # Pulsante selezione cartella
        self.btn_scegli = ttk.Button(root, text="Seleziona cartella", command=self.scegli_cartella)
        self.btn_scegli.pack(pady=5)

        # Barra avanzamento
        self.progress = ttk.Progressbar(root, length=400, mode="determinate")
        self.progress.pack(pady=5)

        # Area log
        self.log = tk.Text(root, height=15, width=60)
        self.log.pack(pady=5)

        # Pulsanti di controllo
        self.frame_btn = tk.Frame(root)
        self.frame_btn.pack(pady=5)

        self.btn_annulla = ttk.Button(self.frame_btn, text="Annulla", command=self.annulla)
        self.btn_annulla.grid(row=0, column=0, padx=5)

        self.btn_riavvia = ttk.Button(self.frame_btn, text="Riavvia", command=self.riavvia)
        self.btn_riavvia.grid(row=0, column=1, padx=5)

        self.btn_fine = ttk.Button(self.frame_btn, text="Fine", command=root.quit)
        self.btn_fine.grid(row=0, column=2, padx=5)

    def log_msg(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.root.update_idletasks()

    def scegli_cartella(self):
        cartella = filedialog.askdirectory(title="📁 Seleziona la cartella da analizzare")
        if cartella:
            self.start_analisi(cartella)

    def start_analisi(self, base_dir):
        self.stop_flag = False
        files = [str(Path(r) / f) for r, _, fs in os.walk(base_dir) for f in fs]
        total = len(files)
        self.progress["value"] = 0
        self.progress["maximum"] = total

        def worker():
            for idx, file_path in enumerate(files, start=1):
                if self.stop_flag:
                    self.log_msg("❌ Analisi interrotta dall'utente.")
                    return
                est = rileva_estensione(file_path)
                if est:
                    rinomina_file(file_path, est, self.log_msg)
                else:
                    sposta_non_trovato(file_path, base_dir, self.log_msg)
                self.progress["value"] = idx
            self.log_msg("\n✅ Analisi completata!")

        threading.Thread(target=worker, daemon=True).start()

    def annulla(self):
        self.stop_flag = True

    def riavvia(self):
        self.stop_flag = True
        self.log.delete(1.0, tk.END)
        self.progress["value"] = 0
        self.scegli_cartella()


if __name__ == "__main__":
    root = tk.Tk()
    app = AnalizzatoreGUI(root)
    root.mainloop()
