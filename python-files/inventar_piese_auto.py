import tkinter as tk
from tkinter import ttk, messagebox
import csv
import json
import os

class InventoryApp:
    DATA_FILE = "inventar.csv"
    CONFIG_FILE = "config.json"
    LABELS = ["Denumire", "Cod", "Cantitate", "Locatie"]

    def __init__(self, root):
        self.root = root
        self.root.title("Gestiune Inventar Piese Auto")
        
        self.data = []
        self.history = []
        self.config = {}

        self.load_data()
        self.load_config()

        self.create_widgets()
        self.apply_config()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_data(self):
        try:
            if os.path.exists(self.DATA_FILE):
                with open(self.DATA_FILE, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.data = list(reader)
        except (IOError, csv.Error) as e:
            messagebox.showerror("Eroare la citire", f"Nu s-a putut citi fișierul de inventar: {e}")
            self.data = []

    def save_data(self):
        try:
            if not self.data:
                if os.path.exists(self.DATA_FILE):
                    os.remove(self.DATA_FILE)
                return
            
            with open(self.DATA_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.LABELS)
                writer.writeheader()
                writer.writerows(self.data)
        except (IOError, csv.Error) as e:
            messagebox.showerror("Eroare la scriere", f"Nu s-a putut salva fișierul de inventar: {e}")

    def save_state_for_undo(self):
        self.history.append(list(self.data))
        if len(self.history) > 20:
            del self.history[0]

    def load_config(self):
        self.config = {"window_geometry": "800x600", "column_widths": {}}
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            messagebox.showwarning("Atenție", f"Nu s-a putut citi fișierul de configurare: {e}. Se va folosi configurația implicită.")

    def save_config(self):
        try:
            self.config["window_geometry"] = self.root.geometry()
            column_widths = {col: self.tree.column(col, "width") for col in self.LABELS}
            self.config["column_widths"] = column_widths
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            messagebox.showerror("Eroare", f"Nu s-a putut salva configurația: {e}")

    def apply_config(self):
        self.root.geometry(self.config.get("window_geometry", "800x600"))
        column_widths = self.config.get("column_widths", {})
        if column_widths:
            for col, width in column_widths.items():
                self.tree.column(col, width=width)

    def on_closing(self):
        self.save_config()
        self.save_data()
        self.root.destroy()

    def create_widgets(self):
        input_frame = ttk.LabelFrame(self.root, text="Adaugă / Caută Produs")
        input_frame.pack(padx=10, pady=10, fill="x")

        self.entries = {}
        for i, label_text in enumerate(self.LABELS):
            ttk.Label(input_frame, text=label_text).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            entry = ttk.Entry(input_frame, width=40)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
            self.entries[label_text] = entry
            entry.bind("<Return>", lambda event=None: self.add_item())
            
        input_frame.grid_columnconfigure(1, weight=1)

        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=len(self.LABELS), columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Adaugă", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Căutare", command=self.search_item).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Afișează tot", command=lambda: self.refresh_treeview(self.data)).pack(side="left", padx=5)

        self.tree = ttk.Treeview(self.root, columns=self.LABELS, show="headings", selectmode='extended')
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        for col in self.LABELS:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c), anchor="w")
            self.tree.column(col, anchor="w")

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Delete>", self.delete_item)
        self.tree.bind("<Double-1>", self.modify_item)

        self.refresh_treeview()
        
        copyright_label = ttk.Label(self.root, text="© 2025 ing.Radu Moscu", foreground="gray", font=("Arial", 10))
        copyright_label.pack(side="bottom", anchor="se", padx=5, pady=2)

    def refresh_treeview(self, data=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        display_data = data if data is not None else self.data
        for item in display_data:
            self.tree.insert("", "end", values=list(item.values()))

    def validate_input(self, item):
        if not all(item.values()):
            messagebox.showerror("Eroare", "Toate câmpurile trebuie completate.")
            return False
        
        try:
            int(item["Cantitate"])
        except ValueError:
            messagebox.showerror("Eroare", "Câmpul 'Cantitate' trebuie să fie un număr întreg.")
            return False
            
        return True

    def add_item(self, event=None):
        item = {label: self.entries[label].get().strip() for label in self.LABELS}
        
        if not self.validate_input(item):
            return

        if any(prod["Cod"] == item["Cod"] for prod in self.data):
            messagebox.showerror("Eroare", f"Un produs cu codul '{item['Cod']}' există deja.")
            return

        self.save_state_for_undo()
        self.data.append(item)
        self.refresh_treeview()
        
        # Păstrează valoarea din câmpurile 'Denumire', 'Cantitate' și 'Locatie'.
        self.entries["Denumire"].delete(0, tk.END)
        self.entries["Cod"].delete(0, tk.END)
        self.entries["Denumire"].focus()
        
        messagebox.showinfo("Succes", "Produsul a fost adăugat.")

    def search_item(self):
        search_criteria = {
            label: self.entries[label].get().strip().lower() for label in self.LABELS
        }

        results = [
            item for item in self.data 
            if all(
                not value or value in item[key].lower()
                for key, value in search_criteria.items()
            )
        ]
        
        self.refresh_treeview(results)

    def delete_item(self, event=None):
        selected_items = self.tree.selection()
        
        if not selected_items:
            messagebox.showwarning("Atenție", "Niciun produs selectat pentru ștergere.")
            return

        item_codes_to_delete = [self.tree.item(item_id)["values"][1] for item_id in selected_items]
        
        message = (f"Ești sigur că vrei să ștergi produsul cu codul '{item_codes_to_delete[0]}'?"
                   if len(item_codes_to_delete) == 1
                   else f"Ești sigur că vrei să ștergi cele {len(item_codes_to_delete)} produse selectate?")

        if messagebox.askyesno("Confirmare", message):
            self.save_state_for_undo()
            self.data = [item for item in self.data if item["Cod"] not in item_codes_to_delete]
            self.refresh_treeview()
            messagebox.showinfo("Succes", f"{len(item_codes_to_delete)} produse au fost șterse.")

    def show_context_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        item_ids = self.tree.selection()
        
        if len(item_ids) == 1:
            menu.add_command(label="Modifică produs", command=self.modify_item)
            menu.add_command(label="Șterge produs", command=self.delete_item)
        elif len(item_ids) > 1:
            menu.add_command(label="Șterge produsele selectate", command=self.delete_item)

        if len(item_ids) > 0:
            menu.add_separator()
        
        if self.history:
            menu.add_command(label="Anulează ultima acțiune (Undo)", command=self.undo)
        else:
            menu.add_command(label="Anulează ultima acțiune (Undo)", state="disabled")
        
        menu.post(event.x_root, event.y_root)

    def modify_item(self, event=None):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Atenție", "Niciun produs selectat pentru modificare.")
            return
        
        item_values = self.tree.item(selected_item)["values"]
        original_item = {self.LABELS[i]: item_values[i] for i in range(len(self.LABELS))}
        
        modify_window = tk.Toplevel(self.root)
        modify_window.title(f"Modifică Produs - {original_item['Cod']}")
        modify_window.transient(self.root)
        modify_window.grab_set()

        modify_entries = {}
        for i, label_text in enumerate(self.LABELS):
            ttk.Label(modify_window, text=label_text).grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(modify_window)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, original_item[label_text])
            modify_entries[label_text] = entry

        modify_entries["Cod"].config(state="readonly")

        def save_changes():
            new_item = {label: modify_entries[label].get().strip() for label in self.LABELS}
            
            if not self.validate_input(new_item):
                return

            self.save_state_for_undo()
            
            for i, item in enumerate(self.data):
                if item["Cod"] == original_item["Cod"]:
                    self.data[i] = new_item
                    break
            
            self.refresh_treeview()
            modify_window.destroy()
            messagebox.showinfo("Succes", "Produsul a fost modificat.")
            
        ttk.Button(modify_window, text="Salvează", command=save_changes).grid(row=len(self.LABELS), columnspan=2, pady=10)

    def sort_column(self, col):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        
        is_numeric = col == "Cantitate"
        
        if is_numeric:
            try:
                l.sort(key=lambda t: int(t[0]), reverse=self.tree.heading(col, "text").startswith("▼"))
            except ValueError:
                l.sort(key=lambda t: t[0].lower(), reverse=self.tree.heading(col, "text").startswith("▼"))
        else:
            l.sort(key=lambda t: t[0].lower(), reverse=self.tree.heading(col, "text").startswith("▼"))
            
        new_text = f"▲ {col}" if self.tree.heading(col, "text").startswith("▼") else f"▼ {col}"
        self.tree.heading(col, text=new_text, anchor="w")
        for index, (_, k) in enumerate(l):
            self.tree.move(k, '', index)

    def undo(self):
        if self.history:
            self.data = self.history.pop()
            self.refresh_treeview()
            messagebox.showinfo("Anulare", "Ultima modificare a fost anulată.")
        else:
            messagebox.showwarning("Atenție", "Nu mai există acțiuni de anulat.")

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()