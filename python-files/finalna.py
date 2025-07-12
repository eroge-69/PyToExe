import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, Menu, scrolledtext
import json
import datetime
import os
import csv
import shutil
import subprocess
import platform

DATA_FILE = "products.json"
PDF_DIR = "pdf_notes"

class ProductManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Menadżer Produktów - Katarzyna Kuruc")
        self.root.geometry("1200x800")  # Powiększone okno

        self.products = {}
        self.sales = {}
        self.next_index = 1
        self.next_sale_index = 1
        self.load_data()

        # --- Menu ---
        menubar = Menu(root)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Eksportuj CSV", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Zakończ", command=root.quit)
        menubar.add_cascade(label="Plik", menu=file_menu)

        edit_menu = Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Dodaj produkt", command=self.add_product)
        edit_menu.add_command(label="Edytuj produkt", command=self.edit_product)
        edit_menu.add_command(label="Usuń produkt", command=self.delete_product)
        menubar.add_cascade(label="Edycja", menu=edit_menu)

        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="O programie", command=self.show_about)
        menubar.add_cascade(label="Pomoc", menu=help_menu)

        root.config(menu=menubar)

        # --- Layout frames ---
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10,0))

        # --- Search area ---
        search_frame = tk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0,10))

        tk.Label(search_frame, text="Wyszukaj po ID lub nazwie:").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Szukaj", command=self.search_by_id_or_name).pack(side=tk.LEFT)
        tk.Button(search_frame, text="Pokaż wszystkie", command=self.refresh_listbox).pack(side=tk.LEFT, padx=5)

        # --- Listbox with products ---
        self.listbox = tk.Listbox(left_frame, width=40, height=30)
        self.listbox.pack(fill=tk.Y, expand=True)
        self.listbox.bind("<Double-Button-1>", self.show_product_details)

        # --- Buttons under listbox ---
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Dodaj Produkt", width=15, command=self.add_product).grid(row=0, column=0, padx=3, pady=3)
        tk.Button(btn_frame, text="Edytuj Produkt", width=15, command=self.edit_product).grid(row=0, column=1, padx=3, pady=3)
        tk.Button(btn_frame, text="Usuń Produkt", width=15, command=self.delete_product).grid(row=0, column=2, padx=3, pady=3)

        tk.Button(btn_frame, text="Dodaj Komentarz", width=15, command=self.add_comment).grid(row=1, column=0, padx=3, pady=3)
        tk.Button(btn_frame, text="Edytuj Komentarze", width=15, command=self.edit_comments).grid(row=1, column=1, padx=3, pady=3)
        tk.Button(btn_frame, text="Pokaż Komentarze", width=15, command=self.show_comments).grid(row=1, column=2, padx=3, pady=3)

        tk.Button(btn_frame, text="Podłącz PDF", width=15, command=self.attach_pdf).grid(row=2, column=0, padx=3, pady=3)
        tk.Button(btn_frame, text="Pokaż PDF", width=15, command=self.show_pdf).grid(row=2, column=1, padx=3, pady=3)
        tk.Button(btn_frame, text="Usuń PDF", width=15, command=self.remove_pdf).grid(row=2, column=2, padx=3, pady=3)

        tk.Button(btn_frame, text="Dodaj Sprzedaż", width=15, command=self.add_sale).grid(row=3, column=0, padx=3, pady=3)
        tk.Button(btn_frame, text="Edytuj Sprzedaż", width=15, command=self.edit_sale).grid(row=3, column=1, padx=3, pady=3)
        tk.Button(btn_frame, text="Usuń Sprzedaż", width=15, command=self.delete_sale).grid(row=3, column=2, padx=3, pady=3)

        tk.Button(btn_frame, text="Pokaż Sprzedaże", width=15, command=self.show_sales_for_product).grid(row=4, column=0, padx=3, pady=3)
        tk.Button(btn_frame, text="Wszystkie Zakupy", width=15, command=self.show_all_sales).grid(row=4, column=1, padx=3, pady=3)

        # --- Right panel: Product details ---
        details_label = tk.Label(right_frame, text="Szczegóły produktu", font=("Arial", 14, "bold"))
        details_label.pack(anchor=tk.W)

        self.details_text = scrolledtext.ScrolledText(right_frame, width=55, height=35, state=tk.DISABLED, wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True)

        self.refresh_listbox()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.products = data.get("products", {})
                    self.sales = data.get("sales", {})
                    self.next_index = data.get("next_index", 1)
                    self.next_sale_index = data.get("next_sale_index", 1)
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się wczytać danych:\n{e}")

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "products": self.products,
                    "sales": self.sales,
                    "next_index": self.next_index,
                    "next_sale_index": self.next_sale_index
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać danych:\n{e}")

    def refresh_listbox(self, filtered_products=None):
        self.listbox.delete(0, tk.END)
        products_to_show = filtered_products if filtered_products is not None else self.products
        for idx, prod in sorted(products_to_show.items()):
            display = f"{idx}: {prod['name']}"
            self.listbox.insert(tk.END, display)
        self.clear_details()

    def clear_details(self):
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        self.details_text.config(state=tk.DISABLED)

    def show_product_details(self, event=None):
        prod_id = self.get_selected_product_id()
        if not prod_id:
            return
        prod = self.products[prod_id]

        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)

        self.details_text.insert(tk.END, f"ID: {prod_id}\n")
        self.details_text.insert(tk.END, f"Nazwa: {prod['name']}\n\n")
        self.details_text.insert(tk.END, f"Informacje:\n{prod['info']}\n\n")

        comments = prod.get('comments', [])
        if comments:
            self.details_text.insert(tk.END, "Komentarze:\n")
            for c in comments:
                self.details_text.insert(tk.END, f"- {c}\n")
        else:
            self.details_text.insert(tk.END, "Brak komentarzy.\n")

        pdf_path = prod.get('pdf_path')
        if pdf_path:
            self.details_text.insert(tk.END, f"\nPodłączony PDF: {os.path.basename(pdf_path)}\n")
        else:
            self.details_text.insert(tk.END, "\nBrak podłączonego PDF.\n")

        self.details_text.config(state=tk.DISABLED)

    def get_selected_product_id(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Brak zaznaczenia", "Proszę zaznaczyć produkt na liście.")
            return None
        idx_str = self.listbox.get(sel[0]).split(":")[0]
        return idx_str

    def add_product(self):
        while True:
            index = simpledialog.askstring("Dodaj produkt", "Podaj indeks produktu (puste = auto):", parent=self.root)
            if index is None:
                return  # anulowano
            index = index.strip()
            if index == "":
                index = str(self.next_index)
                self.next_index += 1
                break
            elif index in self.products:
                messagebox.showwarning("Błąd", "Produkt o takim indeksie już istnieje. Wpisz inny.", parent=self.root)
            else:
                break

        name = simpledialog.askstring("Dodaj produkt", "Nazwa produktu:", parent=self.root)
        if not name:
            return
        info = simpledialog.askstring("Dodaj produkt", "Informacje o produkcie:", parent=self.root)
        if info is None:
            return
        self.products[index] = {
            "name": name,
            "info": info,
            "comments": [],
            "pdf_path": None
        }
        try:
            idx_num = int(index)
            if idx_num >= self.next_index:
                self.next_index = idx_num + 1
        except:
            pass

        self.save_data()
        self.refresh_listbox()

    def edit_product(self):
        prod_id = self.get_selected_product_id()
        if not prod_id:
            return
        prod = self.products[prod_id]

        name = simpledialog.askstring("Edytuj produkt", "Nazwa produktu:", initialvalue=prod['name'], parent=self.root)
        if not name:
            return
        info = simpledialog.askstring("Edytuj produkt", "Informacje o produkcie:", initialvalue=prod['info'], parent=self.root)
        if info is None:
            return

        prod['name'] = name
        prod['info'] = info
        self.save_data()
        self.refresh_listbox()

    def delete_product(self):
        prod_id = self.get_selected_product_id()
        if not prod_id:
            return
        confirm = messagebox.askyesno("Usuń produkt", "Czy na pewno chcesz usunąć produkt?", parent=self.root)
        if confirm:
            # usuń pdf jeśli jest
            pdf_path = self.products[prod_id].get('pdf_path')
            if pdf_path and os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except:
                    pass
            self.products.pop(prod_id, None)
            # usuń sprzedaże produktu
            sales_to_remove = [sid for sid, sale in self.sales.items() if sale['product_id'] == prod_id]
            for sid in sales_to_remove:
                self.sales.pop(sid, None)
            self.save_data()
            self.refresh_listbox()

    def add_comment(self):
        prod_id = self.get_selected_product_id()
        if not prod_id:
            return
        comment = simpledialog.askstring("Dodaj komentarz", "Treść komentarza:", parent=self.root)
        if comment is None or comment.strip() == "":
            return
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.products[prod_id]['comments'].append(f"[{timestamp}] {comment.strip()}")
        self.save_data()
        messagebox.showinfo("Komentarz dodany", "Komentarz został dodany do produktu.", parent=self.root)

    def edit_comments(self):
        prod_id = self.get_selected_product_id()
        if not prod_id:
            return
        comments = self.products[prod_id].get('comments', [])
        if not comments:
            messagebox.showinfo("Edycja komentarzy", "Brak komentarzy do edycji.", parent=self.root)
            return
        comments_text = "\n\n".join(comments)

        edit_win = tk.Toplevel(self.root)
        edit_win.title(f"Edycja komentarzy: {self.products[prod_id]['name']}")
        edit_win.geometry("600x400")

        text_widget = tk.Text(edit_win, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, comments_text)

        def save_and_close():
            new_text = text_widget.get("1.0", tk.END).strip()
            if new_text == "":
                self.products[prod_id]['comments'] = []
            else:
                self.products[prod_id]['comments'] = [c.strip() for c in new_text.split("\n\n")]
            self.save_data()
            edit_win.destroy()
            messagebox.showinfo("Edycja komentarzy", "Komentarze zostały zapisane.", parent=self.root)

        btn_frame = tk.Frame(edit_win)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Zapisz", command=save_and_close).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Anuluj", command=edit_win.destroy).pack(side=tk.LEFT, padx=5)

    def show_comments(self):
        prod_id = self.get_selected_product_id()
        if not prod_id:
            return
        comments = self.products[prod_id].get('comments', [])
        if not comments:
            messagebox.showinfo("Komentarze", "Brak komentarzy dla tego produktu.", parent=self.root)
            return
        messagebox.showinfo(f"Komentarze: {self.products[prod_id]['name']}", "\n\n".join(comments), parent=self.root)

    def attach_pdf(self):
        prod_id = self.get_selected_product_id()
        if not prod_id:
            return
        file_path = filedialog.askopenfilename(title="Wybierz plik PDF", filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return
        if not os.path.exists(PDF_DIR):
            os.makedirs(PDF_DIR)
        dest_path = os.path.join(PDF_DIR, f"{prod_id}.pdf")
        try:
            shutil.copy(file_path, dest_path)
            self.products[prod_id]['pdf_path'] = dest_path
            self.save_data()
            messagebox.showinfo("PDF podłączony", "Plik PDF został podłączony do produktu.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Błąd kopiowania PDF", f"Nie udało się skopiować pliku:\n{e}", parent=self.root)

    def show_pdf(self):
        prod_id = self.get_selected_product_id()
        if not prod_id:
            return
        pdf_path = self.products[prod_id].get('pdf_path')
        if not pdf_path or not os.path.exists(pdf_path):
            messagebox.showinfo("Brak PDF", "Produkt nie ma podłączonego pliku PDF.", parent=self.root)
            return

        try:
            if platform.system() == 'Windows':
                os.startfile(pdf_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', pdf_path])
            else:  # Linux i inne
                subprocess.Popen(['xdg-open', pdf_path])
        except Exception as e:
            messagebox.showerror("Błąd otwierania PDF", f"Nie udało się otworzyć pliku PDF:\n{e}", parent=self.root)

    def remove_pdf(self):
        prod_id = self.get_selected_product_id()
        if not prod_id:
            return
        pdf_path = self.products[prod_id].get('pdf_path')
        if not pdf_path:
            messagebox.showinfo("Brak PDF", "Produkt nie ma podłączonego pliku PDF.", parent=self.root)
            return
        confirm = messagebox.askyesno("Usuń PDF", "Czy na pewno chcesz usunąć podłączony plik PDF?", parent=self.root)
        if confirm:
            try:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                self.products[prod_id]['pdf_path'] = None
                self.save_data()
                messagebox.showinfo("Usunięto PDF", "Plik PDF został usunięty.", parent=self.root)
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się usunąć pliku PDF:\n{e}", parent=self.root)

    def add_sale(self):
        prod_id = self.get_selected_product_id()
        if not prod_id:
            return

        buyer = simpledialog.askstring("Dodaj sprzedaż", "Nabywca:", parent=self.root)
        if not buyer:
            return
        qty_str = simpledialog.askstring("Dodaj sprzedaż", "Ilość:", parent=self.root)
        if not qty_str:
            return
        try:
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError
        except:
            messagebox.showwarning("Błąd", "Ilość musi być liczbą całkowitą większą od 0.", parent=self.root)
            return

        sale_id = str(self.next_sale_index)
        self.next_sale_index += 1

        self.sales[sale_id] = {
            "product_id": prod_id,
            "buyer": buyer,
            "quantity": qty
        }
        self.save_data()
        messagebox.showinfo("Sprzedaż dodana", "Sprzedaż została dodana.", parent=self.root)

    def edit_sale(self):
        sale_id = self.select_sale_for_product()
        if not sale_id:
            return
        sale = self.sales[sale_id]

        buyer = simpledialog.askstring("Edytuj sprzedaż", "Nabywca:", initialvalue=sale['buyer'], parent=self.root)
        if not buyer:
            return
        qty_str = simpledialog.askstring("Edytuj sprzedaż", "Ilość:", initialvalue=str(sale['quantity']), parent=self.root)
        if not qty_str:
            return
        try:
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError
        except:
            messagebox.showwarning("Błąd", "Ilość musi być liczbą całkowitą większą od 0.", parent=self.root)
            return

        sale['buyer'] = buyer
        sale['quantity'] = qty
        self.save_data()
        messagebox.showinfo("Sprzedaż zaktualizowana", "Dane sprzedaży zostały zaktualizowane.", parent=self.root)

    def delete_sale(self):
        sale_id = self.select_sale_for_product()
        if not sale_id:
            return
        confirm = messagebox.askyesno("Usuń sprzedaż", "Czy na pewno chcesz usunąć tę sprzedaż?", parent=self.root)
        if confirm:
            self.sales.pop(sale_id, None)
            self.save_data()
            messagebox.showinfo("Sprzedaż usunięta", "Sprzedaż została usunięta.", parent=self.root)

    def select_sale_for_product(self):
        prod_id = self.get_selected_product_id()
        if not prod_id:
            return None
        related_sales = {sid: sale for sid, sale in self.sales.items() if sale['product_id'] == prod_id}
        if not related_sales:
            messagebox.showinfo("Brak sprzedaży", "Dla tego produktu nie ma zapisanych sprzedaży.", parent=self.root)
            return None

        sel_win = tk.Toplevel(self.root)
        sel_win.title("Wybierz sprzedaż")
        sel_win.geometry("400x300")

        lb = tk.Listbox(sel_win)
        lb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for sid, sale in sorted(related_sales.items()):
            lb.insert(tk.END, f"{sid}: {sale['buyer']} - {sale['quantity']} szt.")

        selected_id = {"val": None}

        def select_and_close():
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning("Wybór", "Proszę wybrać sprzedaż.", parent=sel_win)
                return
            selected_id["val"] = lb.get(sel[0]).split(":")[0]
            sel_win.destroy()

        btn_frame = tk.Frame(sel_win)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Wybierz", command=select_and_close).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Anuluj", command=sel_win.destroy).pack(side=tk.LEFT, padx=5)

        sel_win.transient(self.root)
        sel_win.grab_set()
        self.root.wait_window(sel_win)
        return selected_id["val"]

    def show_sales_for_product(self):
        prod_id = self.get_selected_product_id()
        if not prod_id:
            return
        related_sales = [sale for sale in self.sales.values() if sale['product_id'] == prod_id]
        if not related_sales:
            messagebox.showinfo("Sprzedaże", "Dla tego produktu nie ma zapisanych sprzedaży.", parent=self.root)
            return
        lines = [f"Nabywca: {sale['buyer']}, Ilość: {sale['quantity']}" for sale in related_sales]
        messagebox.showinfo(f"Sprzedaże: {self.products[prod_id]['name']}", "\n".join(lines), parent=self.root)

    def show_all_sales(self):
        if not self.sales:
            messagebox.showinfo("Wszystkie zakupy", "Brak zapisanych zakupów.", parent=self.root)
            return
        lines = []
        for sale in self.sales.values():
            prod_name = self.products.get(sale['product_id'], {}).get('name', "Nieznany produkt")
            lines.append(f"Produkt: {prod_name}, Nabywca: {sale['buyer']}, Ilość: {sale['quantity']}")
        all_sales_win = tk.Toplevel(self.root)
        all_sales_win.title("Wszystkie zakupy")
        all_sales_win.geometry("600x400")

        text = scrolledtext.ScrolledText(all_sales_win, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, "\n".join(lines))
        text.config(state=tk.DISABLED)

    def search_by_id_or_name(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            self.refresh_listbox()
            return
        filtered = {}
        for idx, prod in self.products.items():
            if query in idx.lower() or query in prod['name'].lower():
                filtered[idx] = prod
        self.refresh_listbox(filtered_products=filtered)

    def export_csv(self):
        filename = filedialog.asksaveasfilename(title="Zapisz jako CSV", defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        try:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Nazwa", "Informacje", "Komentarze", "PDF", "Sprzedaże"])
                for idx, prod in self.products.items():
                    comments = " | ".join(prod.get("comments", []))
                    pdf_file = os.path.basename(prod.get("pdf_path")) if prod.get("pdf_path") else ""
                    sales_for_prod = [sale for sale in self.sales.values() if sale["product_id"] == idx]
                    sales_str = "; ".join([f"{s['buyer']}({s['quantity']})" for s in sales_for_prod])
                    writer.writerow([idx, prod["name"], prod["info"], comments, pdf_file, sales_str])
            messagebox.showinfo("Eksport CSV", "Dane zostały wyeksportowane.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Błąd eksportu", f"Nie udało się wyeksportować danych:\n{e}", parent=self.root)

    def show_about(self):
        messagebox.showinfo("O programie", "Menadżer Produktów - Katarzyna Kuruc\nWersja 1.1 useable\nAutor: Patryk Kuruc", parent=self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductManagerApp(root)
    root.mainloop()
