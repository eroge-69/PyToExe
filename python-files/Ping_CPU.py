import tkinter as tk
from tkinter import ttk
import pandas as pd
import platform
import subprocess
import threading
import time

FILE_EXCEL = "hosts.xlsx"
REFRESH_INTERVAL = 5  # secondi

def ping(host):
    """
    Esegue un ping all'host e restituisce True/False
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        result = subprocess.run(
            ["ping", param, "1", host],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception:
        return False

class PingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor Connessioni IP")
        self.tree = ttk.Treeview(root, columns=("Descrizione", "IP", "Stato"), show="headings")
        self.tree.heading("Descrizione", text="Descrizione")
        self.tree.heading("IP", text="Indirizzo IP")
        self.tree.heading("Stato", text="Stato")
        self.tree.column("Descrizione", width=200)
        self.tree.column("IP", width=150)
        self.tree.column("Stato", width=120)
        self.tree.pack(fill="both", expand=True)

        # Legge il file Excel
        self.df = pd.read_excel(FILE_EXCEL)
        self.hosts = list(self.df.itertuples(index=False, name=None))

        # Popola tabella
        for desc, ip in self.hosts:
            self.tree.insert("", "end", values=(desc, ip, "In attesa..."))

        # Avvia il thread di aggiornamento
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()

    def update_loop(self):
        while True:
            for i, (desc, ip) in enumerate(self.hosts):
                status = "OK" if ping(ip) else "NO CONNECTION"
                color = "green" if status == "OK" else "red"
                self.tree.set(self.tree.get_children()[i], "Stato", status)
                self.tree.tag_configure("green", foreground="green")
                self.tree.tag_configure("red", foreground="red")
                self.tree.item(self.tree.get_children()[i], tags=(color,))
            time.sleep(REFRESH_INTERVAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = PingApp(root)
    root.mainloop()
