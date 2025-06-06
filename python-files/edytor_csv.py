import customtkinter as ctk
from tkinter import ttk, messagebox
import csv
import os

# Definiowanie wyglądu aplikacji (System, Dark, Light)
ctk.set_appearance_mode(System)
ctk.set_default_color_theme(blue)

class CSVEditor(ctk.CTk)
    def __init__(self)
        super().__init__()

        # --- Konfiguracja okna głównego ---
        self.title(Edytor Plików CSV)
        self.geometry(900x600)
        self.minsize(600, 400)
        self.protocol(WM_DELETE_WINDOW, self.on_closing)

        # --- Nazwa pliku CSV ---
        self.filename = dane.csv
        self.fieldnames = [Imię, Nazwisko, Opis]

        # --- Inicjalizacja danych (tworzy plik, jeśli nie istnieje) ---
        self.initialize_csv()

        # --- Główne ramki interfejsu ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky=nsew)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)


        # --- Ramka z tabelą (Treeview) ---
        tree_frame = ctk.CTkFrame(self.main_frame)
        tree_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=nsew)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        # Stylizacja Treeview
        style = ttk.Style()
        style.theme_use(default)
        style.configure(Treeview,
                        background=#2b2b2b,
                        foreground=white,
                        rowheight=25,
                        fieldbackground=#2b2b2b,
                        bordercolor=#333333,
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#2a3a54')])
        style.configure(Treeview.Heading,
                        background=#565b5e,
                        foreground=white,
                        relief=flat)
        style.map(Treeview.Heading,
                  background=[('active', '#3484F0')])

        self.tree = ttk.Treeview(tree_frame, columns=self.fieldnames, show='headings')

        # Definiowanie nagłówków
        for col in self.fieldnames
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor='w')

        self.tree.grid(row=0, column=0, sticky=nsew)

        # Scrollbar dla Treeview
        scrollbar = ctk.CTkScrollbar(tree_frame, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind('TreeviewSelect', self.on_item_select)

        # --- Ramka edycji danych ---
        edit_frame = ctk.CTkFrame(self.main_frame)
        edit_frame.grid(row=1, column=0, padx=10, pady=10, sticky=ew)
        edit_frame.grid_columnconfigure(1, weight=1)

        # Pola do wprowadzania danych
        self.imie_var = ctk.StringVar()
        self.nazwisko_var = ctk.StringVar()

        ctk.CTkLabel(edit_frame, text=Imię).grid(row=0, column=0, padx=10, pady=5, sticky=w)
        self.imie_entry = ctk.CTkEntry(edit_frame, textvariable=self.imie_var)
        self.imie_entry.grid(row=0, column=1, padx=10, pady=5, sticky=ew)

        ctk.CTkLabel(edit_frame, text=Nazwisko).grid(row=1, column=0, padx=10, pady=5, sticky=w)
        self.nazwisko_entry = ctk.CTkEntry(edit_frame, textvariable=self.nazwisko_var)
        self.nazwisko_entry.grid(row=1, column=1, padx=10, pady=5, sticky=ew)

        ctk.CTkLabel(edit_frame, text=Opis).grid(row=2, column=0, padx=10, pady=5, sticky=w)
        self.opis_textbox = ctk.CTkTextbox(edit_frame, height=80)
        self.opis_textbox.grid(row=2, column=1, padx=10, pady=5, sticky=ew)


        # --- Ramka z przyciskami ---
        button_frame = ctk.CTkFrame(self.main_frame, fg_color=transparent)
        button_frame.grid(row=2, column=0, padx=10, pady=10, sticky=ew)
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.update_button = ctk.CTkButton(button_frame, text=Aktualizuj Zaznaczony Rekord, command=self.update_record)
        self.update_button.grid(row=0, column=0, padx=5, pady=5, sticky=ew)

        self.add_button = ctk.CTkButton(button_frame, text=Dodaj Nowy Rekord, command=self.add_record)
        self.add_button.grid(row=0, column=1, padx=5, pady=5, sticky=ew)

        self.delete_button = ctk.CTkButton(button_frame, text=Usuń Zaznaczony Rekord, command=self.delete_record, fg_color=#c0392b, hover_color=#e74c3c)
        self.delete_button.grid(row=0, column=2, padx=5, pady=5, sticky=ew)

        self.save_button = ctk.CTkButton(self.main_frame, text=Zapisz wszystkie zmiany do pliku CSV, command=self.save_csv)
        self.save_button.grid(row=3, column=0, padx=10, pady=10, sticky=ew)

        # --- Status bar ---
        self.status_bar = ctk.CTkLabel(self, text=Gotowy., anchor=w, fg_color=#343638, text_color=white)
        self.status_bar.grid(row=1, column=0, sticky=ew, padx=1, pady=1)

        # --- Ładowanie danych ---
        self.load_csv()

    def initialize_csv(self)
        Tworzy przykładowy plik CSV, jeśli nie istnieje.
        if not os.path.exists(self.filename)
            try
                with open(self.filename, 'w', newline='', encoding='utf-8') as csvfile
                    writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                    writer.writeheader()
                    writer.writerow({'Imię' 'Jan', 'Nazwisko' 'Kowalski', 'Opis' 'Przykładowy opis dla Jana.'})
                    writer.writerow({'Imię' 'Anna', 'Nazwisko' 'Nowak', 'Opis' 'Anna jest programistką.'})
            except IOError as e
                messagebox.showerror(Błąd Pliku, fNie można utworzyć pliku {self.filename} {e})
                self.destroy()

    def load_csv(self)
        Ładuje dane z pliku CSV do tabeli Treeview.
        # Czyszczenie starych danych
        for item in self.tree.get_children()
            self.tree.delete(item)

        try
            with open(self.filename, mode='r', newline='', encoding='utf-8') as csvfile
                reader = csv.DictReader(csvfile)
                for row in reader
                    # Upewnij się, że wszystkie klucze istnieją
                    values = [row.get(col, ) for col in self.fieldnames]
                    self.tree.insert('', 'end', values=values)
            self.update_status(fPomyślnie załadowano dane z {self.filename})
        except FileNotFoundError
            messagebox.showerror(Błąd, fPlik {self.filename} nie został znaleziony.)
            self.update_status(fBłąd Plik {self.filename} nie został znaleziony.)
        except Exception as e
            messagebox.showerror(Błąd Odczytu, fWystąpił błąd podczas odczytu pliku {e})
            self.update_status(fBłąd odczytu pliku {e})

    def on_item_select(self, event)
        Wyświetla dane zaznaczonego rekordu w polach edycji.
        selected_items = self.tree.selection()
        if not selected_items
            return

        selected_item = selected_items[0]
        values = self.tree.item(selected_item, 'values')

        self.imie_var.set(values[0])
        self.nazwisko_var.set(values[1])
        self.opis_textbox.delete('1.0', 'end')
        self.opis_textbox.insert('1.0', values[2])
        self.update_status(Zaznaczono rekord. Możesz go edytować.)


    def update_record(self)
        Aktualizuje dane w zaznaczonym wierszu Treeview.
        selected_items = self.tree.selection()
        if not selected_items
            messagebox.showwarning(Brak zaznaczenia, Proszę zaznaczyć rekord, który chcesz zaktualizować.)
            return

        selected_item = selected_items[0]
        new_values = [
            self.imie_var.get(),
            self.nazwisko_var.get(),
            self.opis_textbox.get('1.0', 'end-1c') # -1c usuwa znak nowej linii
        ]
        self.tree.item(selected_item, values=new_values)
        self.update_status(Rekord zaktualizowany w tabeli. Kliknij 'Zapisz', aby zachować zmiany w pliku.)


    def add_record(self)
        Dodaje nowy rekord do Treeview na podstawie danych z pól edycji.
        new_values = [
            self.imie_var.get(),
            self.nazwisko_var.get(),
            self.opis_textbox.get('1.0', 'end-1c')
        ]
        if not new_values[0] or not new_values[1]
            messagebox.showwarning(Brak danych, Pola 'Imię' i 'Nazwisko' nie mogą być puste.)
            return

        self.tree.insert('', 'end', values=new_values)
        # Czyszczenie pól po dodaniu
        self.imie_var.set()
        self.nazwisko_var.set()
        self.opis_textbox.delete('1.0', 'end')
        self.update_status(Dodano nowy rekord. Zapisz zmiany, aby zachować go w pliku.)


    def delete_record(self)
        Usuwa zaznaczony rekord z Treeview.
        selected_items = self.tree.selection()
        if not selected_items
            messagebox.showwarning(Brak zaznaczenia, Proszę zaznaczyć rekord, który chcesz usunąć.)
            return

        if messagebox.askyesno(Potwierdzenie, Czy na pewno chcesz usunąć zaznaczony rekord)
            for selected_item in selected_items
                self.tree.delete(selected_item)
            self.update_status(Rekord usunięty. Zapisz zmiany, aby usunąć go z pliku.)

    def save_csv(self)
        Zapisuje wszystkie dane z Treeview do pliku CSV.
        try
            with open(self.filename, mode='w', newline='', encoding='utf-8') as csvfile
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writeheader()
                for item_id in self.tree.get_children()
                    values = self.tree.item(item_id, 'values')
                    row_dict = {self.fieldnames[i] values[i] for i in range(len(self.fieldnames))}
                    writer.writerow(row_dict)
            messagebox.showinfo(Sukces, fWszystkie zmiany zostały pomyślnie zapisane w pliku {self.filename}.)
            self.update_status(fZapisano zmiany w {self.filename}.)
        except IOError as e
            messagebox.showerror(Błąd Zapisu, fNie można zapisać pliku {self.filename} {e})
            self.update_status(fBłąd zapisu pliku {e})

    def update_status(self, message)
        Aktualizuje tekst na pasku statusu.
        self.status_bar.configure(text=message)
        self.update_idletasks()

    def on_closing(self)
        Wyświetla pytanie przy zamykaniu aplikacji.
        if messagebox.askokcancel(Zamknij, Czy chcesz zamknąć aplikację Niezapisane zmiany zostaną utracone.)
            self.destroy()


if __name__ == __main__
    app = CSVEditor()
    app.mainloop()
