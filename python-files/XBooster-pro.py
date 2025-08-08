import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import platform
import os
import shutil
import psutil
import gc
import tempfile
import subprocess

# Key valide e admin
VALID_KEYS = [f"XBOOST-{i}" for i in range(1, 201)]
ADMIN_KEYS = ["ADMIN"]  # admin key semplice

class XBoosterProApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("XBooster PRO")
        self.geometry("450x450")
        self.configure(bg="#2f2f2f")
        self.license_key = None
        self.is_admin = False

        # Opzioni di boost (default True)
        self.boost_ram = tk.BooleanVar(value=True)
        self.boost_temp = tk.BooleanVar(value=True)
        self.boost_disk = tk.BooleanVar(value=True)

        if not self.ask_license():
            messagebox.showinfo("Licenza", "Licenza non valida. Programma chiuso.")
            self.destroy()
            exit()

        self.create_widgets()
        self.log("Benvenuto in XBooster PRO")

    def ask_license(self):
        while True:
            key = simpledialog.askstring("Licenza", "Inserisci la tua licenza:")
            if key is None:
                return False  # Utente ha annullato
            if key in VALID_KEYS or key in ADMIN_KEYS:
                self.license_key = key
                self.is_admin = key in ADMIN_KEYS
                messagebox.showinfo("Licenza", "Licenza accettata!")
                return True
            else:
                messagebox.showerror("Licenza", "Licenza non valida. Riprova.")

    def create_widgets(self):
        self.logo = tk.Label(self, text="XBooster", font=("Arial", 36, "bold"), fg="purple", bg="#2f2f2f")
        self.logo.pack(pady=15)

        self.btn_boost = tk.Button(self, text="Avvia Boost Completo", font=("Arial", 14), bg="#5a2a82", fg="white", command=self.do_boost)
        self.btn_boost.pack(pady=10)

        if self.is_admin:
            self.btn_admin = tk.Button(self, text="Admin Panel", font=("Arial", 14), bg="#333", fg="white", command=self.open_admin_panel)
            self.btn_admin.pack(pady=10)

        self.logbox = tk.Text(self, height=10, bg="#1e1e1e", fg="white", state="disabled", font=("Consolas", 10))
        self.logbox.pack(fill="both", expand=True, padx=15, pady=15)

    def log(self, message):
        self.logbox.config(state="normal")
        self.logbox.insert("end", message + "\n")
        self.logbox.see("end")
        self.logbox.config(state="disabled")
        self.update()

    def do_boost(self):
        self.log("Inizio boost...")
        try:
            if self.boost_ram.get():
                self.free_ram()
            if self.boost_temp.get():
                self.clean_temp_files()
            if self.boost_disk.get():
                self.optimize_disk()
            self.log("Boost completato!")
        except Exception as e:
            self.log(f"Errore durante boost: {e}")

    def free_ram(self):
        self.log("Liberazione RAM in corso...")
        gc.collect()
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                if proc.info['memory_info'].rss > 100*1024*1024:
                    self.log(f"Processo pesante: {proc.info['name']} ({proc.info['pid']})")
            except:
                pass
        self.log("RAM liberata (tentativo).")

    def clean_temp_files(self):
        self.log("Pulizia file temporanei...")
        temp_dir = tempfile.gettempdir()
        try:
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                        self.log(f"Cancellato file: {filename}")
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        self.log(f"Cancellata cartella: {filename}")
                except Exception as e:
                    self.log(f"Errore cancellazione {filename}: {e}")
        except Exception as e:
            self.log(f"Errore nella pulizia temp: {e}")
        self.log("File temporanei puliti.")

    def optimize_disk(self):
        self.log("Ottimizzazione disco (solo Windows)...")
        if platform.system() == "Windows":
            try:
                subprocess.run("defrag C: /U /V", shell=True)
                self.log("Deframmentazione completata.")
            except Exception as e:
                self.log(f"Errore deframmentazione: {e}")
        else:
            self.log("Ottimizzazione disco non supportata su questo OS.")

    def open_admin_panel(self):
        admin_win = tk.Toplevel(self)
        admin_win.title("Admin Panel")
        admin_win.geometry("350x250")
        admin_win.configure(bg="#3a3a3a")

        tk.Label(admin_win, text="Impostazioni Boost", bg="#3a3a3a", fg="white", font=("Arial", 14, "bold")).pack(pady=10)

        cb_ram = tk.Checkbutton(admin_win, text="Boost RAM", variable=self.boost_ram, bg="#3a3a3a", fg="white", font=("Arial", 12))
        cb_ram.pack(anchor="w", padx=20)

        cb_temp = tk.Checkbutton(admin_win, text="Pulizia File Temporanei", variable=self.boost_temp, bg="#3a3a3a", fg="white", font=("Arial", 12))
        cb_temp.pack(anchor="w", padx=20)

        cb_disk = tk.Checkbutton(admin_win, text="Ottimizzazione Disco", variable=self.boost_disk, bg="#3a3a3a", fg="white", font=("Arial", 12))
        cb_disk.pack(anchor="w", padx=20)

        # Info generali
        info = (
            f"Versione: PRO 1.0\n"
            f"Chiavi valide: {len(VALID_KEYS)}\n"
            f"Licenza attiva: {self.license_key}\n"
            f"ID Macchina: {platform.node()}\n"
            f"Accesso admin: {'Sì' if self.is_admin else 'No'}"
        )
        tk.Label(admin_win, text=info, bg="#3a3a3a", fg="white", font=("Consolas", 10), justify="left").pack(pady=10)

        btn_close = tk.Button(admin_win, text="Chiudi", command=admin_win.destroy)
        btn_close.pack(pady=5)

if __name__ == "__main__":
    import psutil
    app = XBoosterProApp()
    app.mainloop()
