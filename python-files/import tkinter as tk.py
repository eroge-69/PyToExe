import tkinter as tk
from tkinter import ttk

# Mapping für die Multiplikatoren aus dem Dropdown
multiplikatoren = {
    "Dusch-WC Aufsatz": 3,
    "Dusch-WC Komplettanlage": 3,
    "Ersatzteile": 6,
    "Spülsysteme": 3.5
}

class PreisRechner(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Preisrechner")
        self.geometry("400x250")

        # Einkaufspreis
        tk.Label(self, text="Gleitender Einkaufspreis (USD):").pack(pady=(10, 0))
        self.einkaufspreis_entry = tk.Entry(self)
        self.einkaufspreis_entry.pack(pady=5)

        # Dropdown für Produkttyp
        tk.Label(self, text="Warengruppe wählen:").pack(pady=(10, 0))
        self.produkt_var = tk.StringVar()
        self.produkt_dropdown = ttk.Combobox(self, textvariable=self.produkt_var, state="readonly")
        self.produkt_dropdown['values'] = list(multiplikatoren.keys())
        self.produkt_dropdown.current(0)  # Standardwert
        self.produkt_dropdown.pack(pady=5)

        # Berechnen-Button
        self.berechnen_btn = tk.Button(self, text="Berechnen", command=self.berechne_preis)
        self.berechnen_btn.pack(pady=10)

        # Ergebnisfeld
        self.ergebnis_label = tk.Label(self, text="Brutto-Verkaufspreis und UVP: ")
        self.ergebnis_label.pack(pady=10)

        # Fußzeile (unten rechts)
        self.footer_label = tk.Label(
            self,
            text="V25.00.00 | Stand 16.07.2025",
            font=("Arial", 8, "italic"),
            anchor="se"
        )
        self.footer_label.pack(side="bottom", anchor="e", padx=10, pady=5)

    def berechne_preis(self):
        try:
            einkaufspreis = float(self.einkaufspreis_entry.get())
            multiplikator = multiplikatoren[self.produkt_var.get()]
            verkaufspreis = einkaufspreis * multiplikator * 1.39
            self.ergebnis_label.config(text=f"Brutto-Verkaufspreis und UVP: {verkaufspreis:.2f} €")
        except ValueError:
            self.ergebnis_label.config(text="Bitte eine gültige Zahl eingeben.")
        except Exception as e:
            self.ergebnis_label.config(text=f"Fehler: {e}")

if __name__ == "__main__":
    app = PreisRechner()
    app.mainloop()
