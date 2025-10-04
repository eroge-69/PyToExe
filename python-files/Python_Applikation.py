import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

class ResellingManager:
    def __init__(self, root):
        self.root = root
        self.root.title("ResellingManager")
        self.products = []

        self.filename = "reselling_data.csv"

        # Farben definieren
        bg_color = "#dcdcdc"
        entry_bg = "#f0f0f0"
        button_bg = "#b0b0b0"
        text_color = "#333333"

        self.root.configure(bg=bg_color)

        # === Such- & Filterbereich ===
        search_frame = tk.Frame(root, bg=bg_color)
        search_frame.pack(pady=10, fill=tk.X)

        self.search_var = tk.StringVar()

        tk.Label(search_frame, text="🔍 Suche:", bg=bg_color, fg=text_color).pack(side=tk.LEFT, padx=5)
        tk.Entry(search_frame, textvariable=self.search_var, bg=entry_bg, fg=text_color, width=30).pack(side=tk.LEFT, padx=5)

        button_config = {"bg": button_bg, "fg": "black", "padx": 10, "pady": 5}
        tk.Button(search_frame, text="Suchen", command=self.search_products, **button_config).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Nur Nicht Angekommen", command=self.show_not_arrived, **button_config).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Alle Anzeigen", command=self.update_table, **button_config).pack(side=tk.LEFT, padx=5)

        # === Eingabeformular ===
        entry_frame = tk.LabelFrame(root, text="📝 Neues Produkt", bg=bg_color, fg=text_color, padx=10, pady=10)
        entry_frame.pack(padx=10, pady=10, fill=tk.X)

        self.entries = {}
        self.fields = ["Name", "Beschreibung", "Zustand", "Menge", "Eingekauft fuer", "Verkauft fuer"]

        for i, field in enumerate(self.fields):
            tk.Label(entry_frame, text=field, bg=bg_color, fg=text_color).grid(row=0, column=i, padx=5, pady=2)
            entry = tk.Entry(entry_frame, bg=entry_bg, fg=text_color, width=15)
            entry.grid(row=1, column=i, padx=5)
            self.entries[field] = entry

        self.entries["Zustand"] = ttk.Combobox(entry_frame, values=["Gebraucht", "Neu", "Neu (Sonstige)"], width=13)
        self.entries["Zustand"].grid(row=1, column=2)

        self.arrived_var = tk.BooleanVar()
        tk.Checkbutton(entry_frame, text="Angekommen", variable=self.arrived_var, bg=bg_color, fg=text_color).grid(row=1, column=len(self.fields), padx=10)

        tk.Button(entry_frame, text="➕ Produkt Hinzufuegen", command=self.add_product, **button_config).grid(row=1, column=len(self.fields)+1, padx=10)

        # === Tabelle ===
        table_frame = tk.Frame(root, bg=bg_color)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#e6e6e6",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="#e6e6e6",
                        bordercolor="#999999",
                        borderwidth=1)
        style.map('Treeview', background=[('selected', '#a3a3a3')])

        columns = self.fields + ["Angekommen"]
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor='center')

        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.tag_configure('not_arrived', background='#ffb3b3')  # rot
        self.tree.tag_configure('arrived', background='#d9d9d9')      # grau

        # === Buttons unten ===
        bottom_frame = tk.Frame(root, bg=bg_color)
        bottom_frame.pack(pady=10)

        tk.Button(bottom_frame, text="🗑️ Ausgewähltes Produkt löschen", command=self.delete_selected_product, **button_config).pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="💾 Speichern", command=self.save_to_file, **button_config).pack(side=tk.LEFT, padx=5)

        # === Summen-Anzeige ===
        summary_frame = tk.Frame(root, bg=bg_color)
        summary_frame.pack(pady=10)

        self.total_buy_label = tk.Label(summary_frame, text="Gesamt Einkauf: 0.00 €", bg=bg_color, fg="black", font=("Arial", 10, "bold"))
        self.total_buy_label.pack(side=tk.LEFT, padx=20)

        self.total_sell_label = tk.Label(summary_frame, text="Gesamt Verkauf: 0.00 €", bg=bg_color, fg="black", font=("Arial", 10, "bold"))
        self.total_sell_label.pack(side=tk.LEFT, padx=20)

        # === Lade gespeicherte Daten ===
        self.load_from_file()

    def add_product(self):
        data = []
        for field in self.fields:
            value = self.entries[field].get()
            data.append(value)

        arrived = self.arrived_var.get()
        data.append("Ja" if arrived else "Nein")
        self.products.append(data)
        self.update_table()
        self.save_to_file()  # 🔁 Auto-Speichern

        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.arrived_var.set(False)

    def delete_selected_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Keine Auswahl", "Bitte wähle eine Zeile aus, die du löschen möchtest.")
            return

        confirm = messagebox.askyesno("Bestätigen", "Möchtest du das ausgewählte Produkt wirklich löschen?")
        if not confirm:
            return

        item_values = self.tree.item(selected_item, "values")
        self.tree.delete(selected_item)

        try:
            self.products.remove(list(item_values))
        except ValueError:
            pass

        self.update_summary()
        self.save_to_file()  # 🔁 Auto-Speichern

    def update_table(self, filtered=None):
        self.tree.delete(*self.tree.get_children())
        items = filtered if filtered is not None else self.products
        for product in items:
            tag = 'not_arrived' if product[-1] == "Nein" else 'arrived'
            self.tree.insert("", "end", values=product, tags=(tag,))

        self.update_summary()

    def update_summary(self):
        total_buy = 0.0
        total_sell = 0.0

        for product in self.products:
            try:
                buy = float(product[4].replace(",", "."))
                sell = float(product[5].replace(",", "."))
                total_buy += buy
                total_sell += sell
            except ValueError:
                pass

        self.total_buy_label.config(text=f"Gesamt Einkauf: {total_buy:.2f} €")
        self.total_sell_label.config(text=f"Gesamt Verkauf: {total_sell:.2f} €")

    def search_products(self):
        query = self.search_var.get().lower()
        filtered = [p for p in self.products if any(query in str(field).lower() for field in p)]
        self.update_table(filtered)

    def show_not_arrived(self):
        filtered = [p for p in self.products if p[-1] == "Nein"]
        self.update_table(filtered)

    def save_to_file(self):
        try:
            with open(self.filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(self.products)
            # messagebox.showinfo("Gespeichert", "Daten wurden erfolgreich gespeichert.")  # optional
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

    def load_from_file(self):
        if not os.path.exists(self.filename):
            return
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                self.products = list(reader)
                self.update_table()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Datei: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ResellingManager(root)
    root.mainloop()
