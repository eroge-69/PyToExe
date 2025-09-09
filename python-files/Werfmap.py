import os
import tkinter as tk
from tkinter import filedialog, messagebox

class WerfMapMaker:
    def __init__(self, root):
        self.root = root
        self.root.title("Werf Map Maker")
        self.root.geometry("400x200")
        self.root.resizable(False, False)

        # Werfnummer label + invoerveld
        tk.Label(root, text="Werfnummer:").pack(pady=5)
        self.werfnummer_entry = tk.Entry(root, width=30)
        self.werfnummer_entry.pack(pady=5)

        # Locatie label + knop
        self.locatie = tk.StringVar()
        tk.Button(root, text="Kies locatie", command=self.kies_locatie).pack(pady=5)
        self.locatie_label = tk.Label(root, text="Geen locatie gekozen", fg="gray")
        self.locatie_label.pack(pady=5)

        # Start knop
        tk.Button(root, text="Maak mapstructuur", command=self.maak_mappen, bg="#4CAF50", fg="white").pack(pady=10)

    def kies_locatie(self):
        gekozen = filedialog.askdirectory(title="Kies een locatie voor de map")
        if gekozen:
            self.locatie.set(gekozen)
            self.locatie_label.config(text=gekozen, fg="black")

    def maak_mappen(self):
        werfnummer = self.werfnummer_entry.get().strip()
        if not werfnummer:
            messagebox.showwarning("Fout", "Voer een werfnummer in.")
            return
        if not self.locatie.get():
            messagebox.showwarning("Fout", "Kies een locatie.")
            return

        hoofdmap = os.path.join(self.locatie.get(), f"{werfnummer}-2d")

        submappen = [
            f"{werfnummer} - 1 - Werfadministratie",
            f"{werfnummer} - Architect",
            f"{werfnummer} - Info + Bestellingen LE - OA",
            f"{werfnummer} - Magazijn KB",
            f"{werfnummer} - Meerwerken",
            f"{werfnummer} - Nevenaannemers",
            f"{werfnummer} - Offertefase",
            f"{werfnummer} - Opmeting",
            f"{werfnummer} - Scans",
            f"{werfnummer} - Stabiliteitsstudie"
        ]

        try:
            os.makedirs(hoofdmap, exist_ok=True)
            for submap in submappen:
                os.makedirs(os.path.join(hoofdmap, submap), exist_ok=True)
            messagebox.showinfo("Succes", f"De mapstructuur is aangemaakt in:\n{hoofdmap}")
        except Exception as e:
            messagebox.showerror("Fout", f"Er is iets misgegaan:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WerfMapMaker(root)
    root.mainloop()
