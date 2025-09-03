import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog, scrolledtext
import os
import json
from datetime import datetime
import shutil
import binascii

class PatchCreationDialog(simpledialog.Dialog):
    """Okno dialogowe do tworzenia nowej modyfikacji"""
    def __init__(self, parent, changes):
        self.changes = changes
        self.patch_name = ""
        self.patch_description = ""
        super().__init__(parent)
        
    def body(self, master):
        ttk.Label(master, text="Nazwa modyfikacji:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(master, width=40)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(master, text="Opis:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.desc_entry = ttk.Entry(master, width=40)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(master, text=f"Liczba zmian: {len(self.changes)}").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Wyświetlanie podsumowania zmian
        changes_frame = ttk.LabelFrame(master, text="Zmiany w modyfikacji")
        changes_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
        
        tree = ttk.Treeview(changes_frame, columns=('address', 'original', 'new'), show='headings', height=min(5, len(self.changes)))
        tree.heading('address', text='Adres')
        tree.heading('original', text='Oryginalna wartość')
        tree.heading('new', text='Nowa wartość')
        tree.column('address', width=100)
        tree.column('original', width=100)
        tree.column('new', width=100)
        
        for change in self.changes:
            tree.insert('', 'end', values=(
                f"0x{change['address']:08X}",
                f"0x{change['original_value']:02X}",
                f"0x{change['new_value']:02X}"
            ))
        
        vsb = ttk.Scrollbar(changes_frame, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(fill=tk.BOTH, expand=True)
        
        return self.name_entry  # Initial focus
    
    def validate(self):
        self.patch_name = self.name_entry.get().strip()
        self.patch_description = self.desc_entry.get().strip()
        
        if not self.patch_name:
            messagebox.showerror("Błąd", "Nazwa modyfikacji nie może być pusta")
            return False
            
        return True
    
    def apply(self):
        self.result = {
            "name": self.patch_name,
            "description": self.patch_description,
            "changes": self.changes
        }


class HexViewerDialog(simpledialog.Dialog):
    """Okno dialogowe do przeglądania zawartości pliku w formacie hex"""
    def __init__(self, parent, file_path, dialog_title="Podgląd HEX"):
        self.file_path = file_path
        self.dialog_title = dialog_title  # Zmiana nazwy zmiennej
        super().__init__(parent)
        
    def body(self, master):
        self.geometry("800x600")
        self.title(self.dialog_title)  # Użycie nowej nazwy
        
        # Tworzenie obszaru tekstowego z paskiem przewijania
        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=100, height=30)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Wczytanie i wyświetlenie zawartości pliku
        self.load_file_content()
        
        return self.text_area
    
    def load_file_content(self):
        try:
            with open(self.file_path, 'rb') as f:
                content = f.read()
                hex_content = binascii.hexlify(content).decode('utf-8')
                
                # Formatowanie hex do czytelniejszej postaci
                formatted_hex = ""
                for i in range(0, len(hex_content), 2):
                    if i % 32 == 0:
                        formatted_hex += f"\n0x{i//2:08X}:  "
                    formatted_hex += hex_content[i:i+2] + " "
                
                self.text_area.insert(tk.END, formatted_hex)
                self.text_area.configure(state='disabled')
        except Exception as e:
            self.text_area.insert(tk.END, f"Błąd podczas wczytywania pliku: {str(e)}")
            self.text_area.configure(state='disabled')


class BinComparatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional ECU Binary Comparator")
        self.root.geometry("1200x800")
        
        # Zmienne przechowujące ścieżki do plików
        self.file1_path = tk.StringVar()
        self.file2_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.patches_path = tk.StringVar()
        
        # Słownik modyfikacji: {nazwa: {opis, zmiany}}
        self.patches = {}
        
        # Aktualnie zaznaczone zmiany do modyfikacji
        self.selected_changes = []
        
        # Historia operacji
        self.history = []
        
        # Inicjalizacja interfejsu
        self.create_widgets()
        
    def create_widgets(self):
        # Tworzenie zakładek
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Zakładka porównywania
        self.comparison_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.comparison_tab, text="Porównywanie")
        
        # Zakładka zarządzania modyfikacjami
        self.patches_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.patches_tab, text="Modyfikacje")
        
        # Zakładka aplikowania zmian
        self.apply_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.apply_tab, text="Aplikuj zmiany")
        
        # Zakładka historii
        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="Historia")
        
        # Budowanie zakładek
        self.build_comparison_tab()
        self.build_patches_tab()
        self.build_apply_tab()
        self.build_history_tab()
        
    def build_comparison_tab(self):
        # Sekcja wyboru plików
        file_select_frame = ttk.LabelFrame(self.comparison_tab, text="Wybierz pliki do porównania", padding="10")
        file_select_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Plik 1
        file1_frame = ttk.Frame(file_select_frame)
        file1_frame.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(file1_frame, text="Plik BIN 1 (oryginał):").grid(row=0, column=0, sticky=tk.W)
        file1_entry = ttk.Entry(file1_frame, textvariable=self.file1_path, width=60)
        file1_entry.grid(row=0, column=1, padx=5)
        ttk.Button(file1_frame, text="Przeglądaj...", 
                  command=lambda: self.browse_file(self.file1_path)).grid(row=0, column=2)
        ttk.Button(file1_frame, text="Podgląd HEX", 
                  command=lambda: self.show_hex_view(self.file1_path.get(), "Podgląd HEX - Plik 1")).grid(row=0, column=3, padx=5)
        
        # Plik 2
        file2_frame = ttk.Frame(file_select_frame)
        file2_frame.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(file2_frame, text="Plik BIN 2 (modyfikowany):").grid(row=0, column=0, sticky=tk.W)
        file2_entry = ttk.Entry(file2_frame, textvariable=self.file2_path, width=60)
        file2_entry.grid(row=0, column=1, padx=5)
        ttk.Button(file2_frame, text="Przeglądaj...", 
                  command=lambda: self.browse_file(self.file2_path)).grid(row=0, column=2)
        ttk.Button(file2_frame, text="Podgląd HEX", 
                  command=lambda: self.show_hex_view(self.file2_path.get(), "Podgląd HEX - Plik 2")).grid(row=0, column=3, padx=5)
        
        # Sekcja wyników
        result_frame = ttk.LabelFrame(self.comparison_tab, text="Wynik porównania", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        
        # Ramka z przyciskami i wyszukiwaniem
        result_controls = ttk.Frame(result_frame)
        result_controls.pack(fill=tk.X, pady=5)
        
        ttk.Label(result_controls, text="Wyszukaj:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(result_controls, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(result_controls, text="Szukaj", command=self.search_results).pack(side=tk.LEFT, padx=5)
        
        # Treeview dla wyników
        self.result_tree = ttk.Treeview(result_frame, columns=('address', 'value1', 'value2'), show='headings')
        self.result_tree.heading('address', text='Adres (hex)')
        self.result_tree.heading('value1', text='Wartość w pliku 1')
        self.result_tree.heading('value2', text='Wartość w pliku 2')
        self.result_tree.column('address', width=120, anchor=tk.CENTER)
        self.result_tree.column('value1', width=120, anchor=tk.CENTER)
        self.result_tree.column('value2', width=120, anchor=tk.CENTER)
        
        vsb = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_tree.yview)
        vsb.pack(side='right', fill='y')
        hsb = ttk.Scrollbar(result_frame, orient="horizontal", command=self.result_tree.xview)
        hsb.pack(side='bottom', fill='x')
        
        self.result_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.result_tree.pack(fill=tk.BOTH, expand=True)
        
        # Checkbox do zaznaczania zmian
        self.result_tree.bind('<ButtonRelease-1>', self.toggle_change_selection)
        
        # Przyciski akcji
        button_frame = ttk.Frame(self.comparison_tab)
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Button(button_frame, text="Porównaj pliki", command=self.compare_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Zaznacz wszystkie", command=self.select_all_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Utwórz modyfikację", command=self.create_patch_from_selection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Wyczyść wyniki", command=self.clear_results).pack(side=tk.LEFT, padx=5)
        
        # Etykieta z informacją o zaznaczonych zmianach
        self.selection_info = ttk.Label(button_frame, text="Zaznaczono 0 zmian")
        self.selection_info.pack(side=tk.RIGHT, padx=10)
        
    def build_patches_tab(self):
        # Sekcja zarządzania modyfikacjami
        manage_frame = ttk.LabelFrame(self.patches_tab, text="Zarządzaj modyfikacjami", padding="10")
        manage_frame.pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Label(manage_frame, text="Plik modyfikacji:").grid(row=0, column=0, sticky=tk.W)
        patches_entry = ttk.Entry(manage_frame, textvariable=self.patches_path, width=60)
        patches_entry.grid(row=0, column=1, padx=5)
        ttk.Button(manage_frame, text="Przeglądaj...", command=self.browse_patches_file).grid(row=0, column=2)
        
        # Przyciski
        btn_frame = ttk.Frame(manage_frame)
        btn_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(btn_frame, text="Wczytaj modyfikacje", command=self.load_patches).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Zapisz modyfikacje", command=self.save_patches).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Wyczyść modyfikacje", command=self.clear_patches).pack(side=tk.LEFT, padx=5)
        
        # Lista modyfikacji
        list_frame = ttk.LabelFrame(self.patches_tab, text="Lista modyfikacji", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        
        self.patches_tree = ttk.Treeview(list_frame, columns=('name', 'description', 'changes_count'), show='headings')
        self.patches_tree.heading('name', text='Nazwa modyfikacji')
        self.patches_tree.heading('description', text='Opis')
        self.patches_tree.heading('changes_count', text='Liczba zmian')
        self.patches_tree.column('name', width=200)
        self.patches_tree.column('description', width=350)
        self.patches_tree.column('changes_count', width=100, anchor=tk.CENTER)
        
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.patches_tree.yview)
        vsb.pack(side='right', fill='y')
        self.patches_tree.configure(yscrollcommand=vsb.set)
        self.patches_tree.pack(fill=tk.BOTH, expand=True)
        
        # Przyciski do zarządzania listą
        btn_frame2 = ttk.Frame(list_frame)
        btn_frame2.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame2, text="Podgląd modyfikacji", command=self.view_patch).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="Usuń modyfikację", command=self.delete_patch).pack(side=tk.LEFT, padx=5)
        
    def build_apply_tab(self):
        # Sekcja aplikowania zmian
        apply_frame = ttk.LabelFrame(self.apply_tab, text="Zastosuj modyfikację do pliku", padding="10")
        apply_frame.pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Label(apply_frame, text="Plik źródłowy:").grid(row=0, column=0, sticky=tk.W)
        self.source_path = tk.StringVar()
        source_entry = ttk.Entry(apply_frame, textvariable=self.source_path, width=60)
        source_entry.grid(row=0, column=1, padx=5)
        ttk.Button(apply_frame, text="Przeglądaj...", 
                  command=lambda: self.browse_file(self.source_path)).grid(row=0, column=2)
        ttk.Button(apply_frame, text="Podgląd HEX", 
                  command=lambda: self.show_hex_view(self.source_path.get(), "Podgląd HEX - Źródło")).grid(row=0, column=3, padx=5)
        
        ttk.Label(apply_frame, text="Plik wynikowy:").grid(row=1, column=0, sticky=tk.W)
        self.target_path = tk.StringVar()
        target_entry = ttk.Entry(apply_frame, textvariable=self.target_path, width=60)
        target_entry.grid(row=1, column=1, padx=5)
        ttk.Button(apply_frame, text="Przeglądaj...", 
                  command=lambda: self.browse_save_file(self.target_path)).grid(row=1, column=2)
        
        # Wybór modyfikacji
        ttk.Label(apply_frame, text="Modyfikacja:").grid(row=2, column=0, sticky=tk.W)
        self.selected_patch = tk.StringVar()
        patches_combobox = ttk.Combobox(apply_frame, textvariable=self.selected_patch, width=58)
        patches_combobox.grid(row=2, column=1, padx=5, sticky=tk.W)
        self.patches_combobox = patches_combobox
        
        # Przyciski
        btn_frame = ttk.Frame(apply_frame)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        ttk.Button(btn_frame, text="Zastosuj modyfikację", command=self.apply_patch).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Podgląd zmian", command=self.preview_patch).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Waliduj plik", command=self.validate_file).pack(side=tk.LEFT, padx=5)
        
        # Sekcja podglądu zmian
        preview_frame = ttk.LabelFrame(self.apply_tab, text="Podgląd zmian", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Pasek przewijania
        scrollbar = ttk.Scrollbar(self.preview_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.preview_text.yview)
    
    def build_history_tab(self):
        # Sekcja historii
        history_frame = ttk.LabelFrame(self.history_tab, text="Historia operacji", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tworzenie obszaru tekstowego z paskiem przewijania
        self.history_text = scrolledtext.ScrolledText(history_frame, wrap=tk.WORD, width=100, height=30)
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.history_text.configure(state='disabled')
        
        # Przycisk czyszczenia historii
        btn_frame = ttk.Frame(history_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Wyczyść historię", command=self.clear_history).pack(side=tk.RIGHT, padx=5)
    
    def add_history_entry(self, operation, details):
        """Dodaje wpis do historii"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {operation}\n{details}\n{'='*80}\n"
        self.history.append(entry)
        
        # Aktualizuj widok historii
        self.history_text.configure(state='normal')
        self.history_text.insert(tk.END, entry)
        self.history_text.configure(state='disabled')
        self.history_text.see(tk.END)
    
    def clear_history(self):
        """Czyści historię operacji"""
        self.history = []
        self.history_text.configure(state='normal')
        self.history_text.delete(1.0, tk.END)
        self.history_text.configure(state='disabled')
        self.add_history_entry("Historia wyczyszczona", "Wszystkie wpisy historii zostały usunięte")
    
    def show_hex_view(self, file_path, dialog_title="Podgląd HEX"):
        """Wyświetla podgląd hex pliku"""
        if not file_path:
            messagebox.showwarning("Brak pliku", "Wybierz plik przed użyciem podglądu HEX")
            return
            
        if not os.path.exists(file_path):
            messagebox.showerror("Błąd", "Plik nie istnieje")
            return
            
        HexViewerDialog(self.root, file_path, dialog_title)
        self.add_history_entry(f"Podgląd HEX: {dialog_title}", f"Ścieżka: {file_path}")
    
    def browse_file(self, path_var):
        filename = filedialog.askopenfilename(
            title="Wybierz plik BIN",
            filetypes=(("Pliki binarne", "*.bin"), ("Wszystkie pliki", "*.*"))
        )
        if filename:
            path_var.set(filename)
    
    def browse_save_file(self, path_var):
        filename = filedialog.asksaveasfilename(
            title="Zapisz plik",
            defaultextension=".bin",
            filetypes=(("Pliki binarne", "*.bin"), ("Wszystkie pliki", "*.*"))
        )
        if filename:
            path_var.set(filename)
    
    def browse_patches_file(self):
        filename = filedialog.asksaveasfilename(
            title="Zapisz modyfikacje",
            defaultextension=".json",
            filetypes=(("Pliki JSON", "*.json"), ("Wszystkie pliki", "*.*"))
        )
        if filename:
            self.patches_path.set(filename)
    
    def toggle_change_selection(self, event):
        item = self.result_tree.identify_row(event.y)
        if not item:
            return
            
        values = self.result_tree.item(item, 'values')
        
        # Sprawdź czy kliknięto na różnicę (a nie nagłówek)
        if len(values) < 3 or not values[0].startswith("0x"):
            return
        
        address = int(values[0], 16)
        original_value = int(values[1], 16)
        new_value = int(values[2], 16)
        
        # Sprawdź czy zmiana jest już zaznaczona
        change_index = next((i for i, c in enumerate(self.selected_changes) 
                           if c['address'] == address), -1)
        
        if change_index >= 0:
            # Usuń zaznaczenie
            self.selected_changes.pop(change_index)
            self.result_tree.item(item, tags=('',))
        else:
            # Dodaj zaznaczenie
            self.selected_changes.append({
                'address': address,
                'original_value': original_value,
                'new_value': new_value
            })
            self.result_tree.item(item, tags=('selected',))
        
        # Aktualizuj tagi wizualne
        self.result_tree.tag_configure('selected', background='#E0F0FF')
        self.selection_info.config(text=f"Zaznaczono {len(self.selected_changes)} zmian")
    
    def select_all_changes(self):
        """Automatycznie zaznacza wszystkie różnice w plikach"""
        self.selected_changes = []
        for child in self.result_tree.get_children():
            values = self.result_tree.item(child, 'values')
            if len(values) >= 3 and values[0].startswith("0x"):
                address = int(values[0], 16)
                original_value = int(values[1], 16)
                new_value = int(values[2], 16)
                
                self.selected_changes.append({
                    'address': address,
                    'original_value': original_value,
                    'new_value': new_value
                })
                self.result_tree.item(child, tags=('selected',))
        
        self.result_tree.tag_configure('selected', background='#E0F0FF')
        self.selection_info.config(text=f"Zaznaczono {len(self.selected_changes)} zmian")
        self.add_history_entry("Zaznaczono wszystkie zmiany", f"Liczba zaznaczonych zmian: {len(self.selected_changes)}")
    
    def clear_results(self):
        self.result_tree.delete(*self.result_tree.get_children())
        self.selected_changes = []
        self.selection_info.config(text="Zaznaczono 0 zmian")
    
    def compare_files(self):
        file1 = self.file1_path.get()
        file2 = self.file2_path.get()
        
        if not file1 or not file2:
            messagebox.showerror("Błąd", "Wybierz oba pliki do porównania!")
            return
        
        try:
            self.clear_results()
            
            # Porównanie plików
            result = self.compare_bin_files(file1, file2)
            
            # Wyświetlenie wyników
            self.display_results(result)
            
            # Dodanie do historii
            status = "IDENTYCZNE" if result['is_same'] else "RÓŻNIĄCE SIĘ"
            self.add_history_entry(
                f"Porównano pliki: {os.path.basename(file1)} i {os.path.basename(file2)}", 
                f"Status: {status}, Różnice: {result['different_bytes']}"
            )
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas porównywania:\n{str(e)}")
            self.add_history_entry("Błąd podczas porównywania", str(e))
    
    def compare_bin_files(self, file1, file2, chunk_size=1024):
        differences = {
            'total_bytes': 0,
            'different_bytes': 0,
            'file1_size': 0,
            'file2_size': 0,
            'differences': [],
            'is_same': False,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            # Sprawdzenie rozmiarów plików
            f1.seek(0, 2)
            f2.seek(0, 2)
            file1_size = f1.tell()
            file2_size = f2.tell()
            differences['file1_size'] = file1_size
            differences['file2_size'] = file2_size
            
            if file1_size != file2_size:
                differences['is_same'] = False
                return differences
            
            f1.seek(0)
            f2.seek(0)
            
            address = 0
            while True:
                chunk1 = f1.read(chunk_size)
                chunk2 = f2.read(chunk_size)
                
                if not chunk1 and not chunk2:
                    break
                
                if len(chunk1) != len(chunk2):
                    differences['is_same'] = False
                    return differences
                
                for i in range(len(chunk1)):
                    if chunk1[i] != chunk2[i]:
                        differences['different_bytes'] += 1
                        differences['differences'].append({
                            'address': address + i,
                            'file1_value': chunk1[i],
                            'file2_value': chunk2[i]
                        })
                
                address += len(chunk1)
                differences['total_bytes'] = address
            
            differences['is_same'] = differences['different_bytes'] == 0
            return differences
    
    def display_results(self, result):
        # Dodajemy nagłówek
        self.result_tree.insert('', 'end', values=(
            f"--- WYNIK PORÓWNANIA ---", 
            f"Data: {result['timestamp']}", 
            f"Rozmiar plików: {result['file1_size']} bajtów"
        ), tags=('header',))
        
        if result['file1_size'] != result['file2_size']:
            self.result_tree.insert('', 'end', values=(
                "PLIKI RÓŻNEJ DŁUGOŚCI!", 
                f"Plik 1: {result['file1_size']} bajtów", 
                f"Plik 2: {result['file2_size']} bajtów"
            ), tags=('error',))
            return
        
        if result['is_same']:
            self.result_tree.insert('', 'end', values=(
                "PLIKI IDENTYCZNE", 
                f"Porównano {result['total_bytes']} bajtów", 
                f"Znaleziono 0 różnic"
            ), tags=('success',))
        else:
            self.result_tree.insert('', 'end', values=(
                "PLIKI RÓŻNIĄCE SIĘ", 
                f"Porównano {result['total_bytes']} bajtów", 
                f"Znaleziono {result['different_bytes']} różnic"
            ), tags=('warning',))
            
            # Dodajemy różnice
            for diff in result['differences']:
                addr = diff['address']
                val1 = diff['file1_value']
                val2 = diff['file2_value']
                
                self.result_tree.insert('', 'end', values=(
                    f"0x{addr:08X}", 
                    f"0x{val1:02X}", 
                    f"0x{val2:02X}"
                ))
        
        # Konfiguracja tagów dla kolorowania
        self.result_tree.tag_configure('header', background='#E0E0E0', font=('TkDefaultFont', 10, 'bold'))
        self.result_tree.tag_configure('success', background='#DFF0D8', font=('TkDefaultFont', 10, 'bold'))
        self.result_tree.tag_configure('warning', background='#FCF8E3', font=('TkDefaultFont', 10, 'bold'))
        self.result_tree.tag_configure('error', background='#F2DEDE', font=('TkDefaultFont', 10, 'bold'))
    
    def create_patch_from_selection(self):
        if not self.selected_changes:
            messagebox.showerror("Błąd", "Nie zaznaczono żadnych zmian do zapisania")
            return
        
        dialog = PatchCreationDialog(self.root, self.selected_changes)
        
        if hasattr(dialog, 'result') and dialog.result:
            patch_name = dialog.result['name']
            self.patches[patch_name] = dialog.result
            self.update_patches_list()
            
            # Dodanie do historii
            self.add_history_entry(
                f"Utworzono modyfikację: {patch_name}", 
                f"Liczba zmian: {len(self.selected_changes)}"
            )
            
            messagebox.showinfo("Sukces", f"Utworzono modyfikację: {patch_name}")
            self.selected_changes = []
            self.clear_results()
    
    def update_patches_list(self):
        self.patches_tree.delete(*self.patches_tree.get_children())
        for name, patch in self.patches.items():
            self.patches_tree.insert('', 'end', values=(
                patch['name'],
                patch['description'],
                len(patch['changes'])
            ))
        
        # Aktualizuj combobox w zakładce aplikowania
        self.patches_combobox['values'] = list(self.patches.keys())
        if self.patches:
            self.patches_combobox.current(0)
    
    def save_patches(self):
        if not self.patches:
            messagebox.showinfo("Brak modyfikacji", "Nie utworzono żadnych modyfikacji.")
            return
        
        filename = self.patches_path.get()
        if not filename:
            filename = filedialog.asksaveasfilename(
                title="Zapisz modyfikacje",
                defaultextension=".json",
                filetypes=(("Pliki JSON", "*.json"), ("Wszystkie pliki", "*.*"))
            )
            if filename:
                self.patches_path.set(filename)
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.patches, f, indent=4)
                messagebox.showinfo("Sukces", f"Modyfikacje zapisane do {filename}")
                self.add_history_entry("Zapisano modyfikacje", f"Plik: {filename}")
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się zapisać: {str(e)}")
                self.add_history_entry("Błąd zapisu modyfikacji", str(e))
    
    def load_patches(self):
        filename = self.patches_path.get()
        if not filename:
            filename = filedialog.askopenfilename(
                title="Wczytaj modyfikacje",
                filetypes=(("Pliki JSON", "*.json"), ("Wszystkie pliki", "*.*"))
            )
            if filename:
                self.patches_path.set(filename)
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.patches = json.load(f)
                self.update_patches_list()
                messagebox.showinfo("Sukces", f"Modyfikacje wczytane z {filename}")
                self.add_history_entry("Wczytano modyfikacje", f"Plik: {filename}")
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się wczytać: {str(e)}")
                self.add_history_entry("Błąd wczytywania modyfikacji", str(e))
    
    def clear_patches(self):
        self.patches = {}
        self.update_patches_list()
        self.add_history_entry("Wyczyszczono modyfikacje", "Wszystkie modyfikacje zostały usunięte")
    
    def view_patch(self):
        selected = self.patches_tree.selection()
        if not selected:
            messagebox.showerror("Błąd", "Wybierz modyfikację do podglądu")
            return
        
        item = self.patches_tree.item(selected[0])
        values = item['values']
        patch_name = values[0]
        patch = self.patches[patch_name]
        
        # Tworzenie okna podglądu
        view_window = tk.Toplevel(self.root)
        view_window.title(f"Podgląd modyfikacji: {patch_name}")
        view_window.geometry("600x400")
        
        # Nagłówek
        header_frame = ttk.Frame(view_window, padding="10")
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text=f"Nazwa: {patch['name']}", font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(header_frame, text=f"Opis: {patch['description']}").pack(anchor=tk.W)
        ttk.Label(header_frame, text=f"Liczba zmian: {len(patch['changes'])}").pack(anchor=tk.W)
        
        # Lista zmian
        changes_frame = ttk.LabelFrame(view_window, text="Zmiany", padding="10")
        changes_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tree = ttk.Treeview(changes_frame, columns=('address', 'original', 'new'), show='headings')
        tree.heading('address', text='Adres (hex)')
        tree.heading('original', text='Oryginalna wartość')
        tree.heading('new', text='Nowa wartość')
        tree.column('address', width=150, anchor=tk.CENTER)
        tree.column('original', width=150, anchor=tk.CENTER)
        tree.column('new', width=150, anchor=tk.CENTER)
        
        for change in patch['changes']:
            tree.insert('', 'end', values=(
                f"0x{change['address']:08X}",
                f"0x{change['original_value']:02X}",
                f"0x{change['new_value']:02X}"
            ))
        
        vsb = ttk.Scrollbar(changes_frame, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(fill=tk.BOTH, expand=True)
    
    def delete_patch(self):
        selected = self.patches_tree.selection()
        if not selected:
            messagebox.showerror("Błąd", "Wybierz modyfikację do usunięcia")
            return
        
        item = self.patches_tree.item(selected[0])
        patch_name = item['values'][0]
        
        if messagebox.askyesno("Potwierdzenie", f"Czy na pewno usunąć modyfikację '{patch_name}'?"):
            del self.patches[patch_name]
            self.patches_tree.delete(selected[0])
            self.update_patches_list()
            self.add_history_entry("Usunięto modyfikację", f"Nazwa: {patch_name}")
    
    def apply_patch(self):
        source = self.source_path.get()
        target = self.target_path.get()
        patch_name = self.selected_patch.get()
        
        if not source or not target:
            messagebox.showerror("Błąd", "Wybierz plik źródłowy i docelowy")
            return
        
        if not patch_name or patch_name not in self.patches:
            messagebox.showerror("Błąd", "Wybierz modyfikację do zastosowania")
            return
        
        patch = self.patches[patch_name]
        
        try:
            # Kopiujemy plik źródłowy do docelowego
            shutil.copyfile(source, target)
            
            # Otwieramy plik docelowy do modyfikacji
            with open(target, 'r+b') as f:
                # Stosujemy każdą zmianę z modyfikacji
                for change in patch['changes']:
                    f.seek(change['address'])
                    f.write(bytes([change['new_value']]))  # Poprawiony błąd składniowy
            
            messagebox.showinfo("Sukces", f"Modyfikacja '{patch_name}' została pomyślnie zastosowana")
            self.preview_patch()
            
            # Dodanie do historii
            self.add_history_entry(
                f"Zastosowano modyfikację: {patch_name}", 
                f"Plik źródłowy: {source}\nPlik wynikowy: {target}"
            )
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas aplikowania modyfikacji:\n{str(e)}")
            self.add_history_entry("Błąd aplikowania modyfikacji", str(e))
    
    def validate_file(self):
        """Waliduje, czy plik źródłowy pasuje do wybranej modyfikacji"""
        source = self.source_path.get()
        patch_name = self.selected_patch.get()
        
        if not source:
            messagebox.showerror("Błąd", "Wybierz plik źródłowy")
            return
        
        if not patch_name or patch_name not in self.patches:
            messagebox.showerror("Błąd", "Wybierz modyfikację do walidacji")
            return
        
        patch = self.patches[patch_name]
        errors = []
        
        try:
            with open(source, 'rb') as f:
                for change in patch['changes']:
                    f.seek(change['address'])
                    current_value = f.read(1)[0]
                    if current_value != change['original_value']:
                        errors.append({
                            'address': change['address'],
                            'expected': change['original_value'],
                            'actual': current_value
                        })
            
            if errors:
                error_msg = "Znaleziono niezgodności:\n"
                for error in errors:
                    error_msg += f"Adres 0x{error['address']:08X}: " \
                                f"Oczekiwano 0x{error['expected']:02X}, " \
                                f"Znaleziono 0x{error['actual']:02X}\n"
                
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(tk.END, error_msg)
                messagebox.showwarning("Walidacja nie powiodła się", "Plik źródłowy nie pasuje do modyfikacji")
                self.add_history_entry(
                    f"Walidacja nie powiodła się: {patch_name}", 
                    f"Liczba błędów: {len(errors)}"
                )
            else:
                messagebox.showinfo("Sukces", "Plik źródłowy jest zgodny z modyfikacją")
                self.add_history_entry(
                    f"Walidacja powiodła się: {patch_name}", 
                    "Plik źródłowy jest zgodny z modyfikacją"
                )
                
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas walidacji:\n{str(e)}")
            self.add_history_entry("Błąd walidacji", str(e))
    
    def preview_patch(self):
        source = self.source_path.get()
        patch_name = self.selected_patch.get()
        
        if not source:
            messagebox.showerror("Błąd", "Wybierz plik źródłowy")
            return
        
        if not patch_name or patch_name not in self.patches:
            messagebox.showerror("Błąd", "Wybierz modyfikację do podglądu")
            return
        
        patch = self.patches[patch_name]
        
        try:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"Podgląd modyfikacji: {patch_name}\n")
            self.preview_text.insert(tk.END, f"Opis: {patch['description']}\n")
            self.preview_text.insert(tk.END, f"Liczba zmian: {len(patch['changes'])}\n\n")
            
            with open(source, 'rb') as f:
                # Pobieramy oryginalne wartości
                original_values = {}
                for change in patch['changes']:
                    f.seek(change['address'])
                    original_values[change['address']] = f.read(1)[0]
            
            # Wyświetlamy zmiany
            self.preview_text.insert(tk.END, "Adres (hex) | Oryginalna wartość | Nowa wartość\n")
            self.preview_text.insert(tk.END, "-"*60 + "\n")
            
            for change in patch['changes']:
                addr = change['address']
                original = original_values.get(addr, 0)
                self.preview_text.insert(tk.END, 
                    f"0x{addr:08X} | 0x{original:02X} | 0x{change['new_value']:02X}\n")
            
            # Kolorowanie nagłówka
            self.preview_text.tag_configure("header", font=("TkDefaultFont", 10, "bold"))
            self.preview_text.tag_add("header", "1.0", "4.0")
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas generowania podglądu:\n{str(e)}")
    
    def search_results(self):
        """Wyszukuje wpisy w wynikach porównania"""
        search_term = self.search_var.get().strip().lower()
        
        if not search_term:
            return
        
        # Usuń obecne zaznaczenie
        for item in self.result_tree.selection():
            self.result_tree.selection_remove(item)
        
        # Przeszukaj wszystkie elementy
        found = False
        for child in self.result_tree.get_children():
            values = self.result_tree.item(child, 'values')
            if any(search_term in str(value).lower() for value in values):
                self.result_tree.selection_add(child)
                self.result_tree.see(child)
                found = True
        
        if not found:
            messagebox.showinfo("Wyszukiwanie", "Nie znaleziono pasujących wyników")


if __name__ == "__main__":
    root = tk.Tk()
    app = BinComparatorApp(root)
    
    # Dodanie początkowej wiadomości do historii
    app.add_history_entry(
        "Aplikacja uruchomiona", 
        f"ECU Binary Comparator v1.5\nData: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    root.mainloop()