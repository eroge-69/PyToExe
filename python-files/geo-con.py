# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog, messagebox, font as tkFont
from PIL import Image, ImageTk 
import re
import os
import sys

# --- Wersja programu ---
PROGRAM_VERSION = "1.0.0" 

# --- Funkcja do określania ścieżki zasobów w trybie PyInstallera ---
def resource_path(relative_path):
    """Zwraca absolutną ścieżkę do zasobu, działa zarówno w trybie deweloperskim, jak i po spakowaniu PyInstallerem."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def process_html_to_txt(html_file_path, output_file_path):
    # ... (kod funkcji process_html_to_txt bez zmian) ...
    try:
        with open(html_file_path, 'r', encoding='windows-1250') as f:
            html_content = f.read()
    except FileNotFoundError:
        messagebox.showerror("Błąd pliku", f"Plik '{html_file_path}' nie został znaleziony.")
        return False
    except Exception as e:
        messagebox.showerror("Błąd odczytu HTML", f"Błąd podczas odczytu pliku HTML: {e}")
        return False

    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')

    if not table:
        messagebox.showerror("Błąd parsowania", "Nie znaleziono tabeli w pliku HTML. Upewnij się, że plik ma poprawną strukturę tabeli.")
        return False

    extracted_data = []
    rows = table.find_all('tr')[2:]

    for row in rows:
        cols = row.find_all('td')
        
        if len(cols) >= 5:
            numer_inny_val = cols[2].get_text(strip=True).replace('&nbsp;', '')
            x_val = cols[3].get_text(strip=True).replace('&nbsp;', '')
            y_val = cols[4].get_text(strip=True).replace('&nbsp;', '')
            
            final_line = f"{numer_inny_val} {x_val} {y_val}"
            extracted_data.append(final_line)

    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            for line in extracted_data:
                f.write(line + '\n')
        messagebox.showinfo("Sukces!", f"Pomyślnie przetworzono plik i zapisano do:\n'{output_file_path}'.")
        return True
    except Exception as e:
        messagebox.showerror("Błąd zapisu TXT", f"Błąd podczas zapisu pliku tekstowego: {e}")
        return False


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # Tytuł okna z wersją programu
        self.title(f"GEO-CON {PROGRAM_VERSION} - GEO ARCUS SP. Z O.O.")
        self.geometry("550x450") # Rozmiar okna (dostosowany pod logo)
        self.resizable(False, False)
        self.configure(bg="#e0e0e0")

        # --- Ustawienie ikony okna na pasku zadań/w nagłówku ---
        ICON_FILE_NAME = "geo-con.ico" # Nazwa pliku ICO, użytego jako ikona pliku .exe
        try:
            # Tkinter potrafi bezpośrednio ładować pliki .ico za pomocą iconbitmap
            # Ważne: iconbitmap najlepiej działa z plikami .ico
            icon_path = resource_path(ICON_FILE_NAME)
            self.iconbitmap(icon_path)
        except tk.TclError: # Typowy błąd, gdy plik ICO nie może być załadowany
            print(f"Ostrzeżenie: Nie można załadować ikony okna '{ICON_FILE_NAME}'. Sprawdź, czy plik istnieje i jest prawidłowy.")
        except Exception as e:
            print(f"Inny błąd podczas ładowania ikony okna: {e}")

        # Definiowanie niestandardowych czcionek
        self.title_font = tkFont.Font(family="Helvetica", size=16, weight="bold")
        self.label_font = tkFont.Font(family="Arial", size=10)
        self.button_font = tkFont.Font(family="Arial", size=12, weight="bold")
        self.footer_font = tkFont.Font(family="Arial", size=8, slant="italic")
        self.version_font = tkFont.Font(family="Arial", size=7, slant="italic")

        # --- Obszar na logo (z resource_path) ---
        LOGO_FILE_NAME = "logo.png" # Nazwa pliku logo, upewnij się, że taka jest!
        try:
            logo_path = resource_path(LOGO_FILE_NAME)
            self.logo_image_pil = Image.open(logo_path)
            self.logo_image_pil = self.logo_image_pil.resize((250, 80), Image.Resampling.LANCZOS)
            
            self.logo_photo = ImageTk.PhotoImage(self.logo_image_pil) 
            self.logo_display_label = tk.Label(self, image=self.logo_photo, bg="#e0e0e0")
            self.logo_display_label.image = self.logo_photo
            self.logo_display_label.pack(pady=(10, 10))

        except FileNotFoundError:
            print(f"Błąd: Plik logo '{LOGO_FILE_NAME}' nie został znaleziony. Upewnij się, że jest w tym samym folderze co skrypt i że używasz opcji '--add-data' w PyInstallerze. Logo nie zostanie wyświetlone w GUI.")
            self.label_title_fallback = tk.Label(self, text="Konwerter HTML na TXT",
                                         font=self.title_font, bg="#e0e0e0", fg="#333333")
            self.label_title_fallback.pack(pady=(10, 10))
        except Exception as e:
            print(f"Błąd podczas ładowania logo '{LOGO_FILE_NAME}': {e}")
            self.label_title_fallback = tk.Label(self, text="Konwerter HTML na TXT",
                                         font=self.title_font, bg="#e0e0e0", fg="#333333")
            self.label_title_fallback.pack(pady=(10, 10))

        # Ramka główna dla lepszego rozmieszczenia (centrowanie)
        main_frame = tk.Frame(self, bg="#e0e0e0", padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        # Etykieta informacyjna
        self.label_info = tk.Label(main_frame, text="Wybierz plik HTML, aby przekonwertować go do pliku TXT.\n"
                                                      "Wygenerowany plik pojawi się w tym samym folderze co plik źródłowy.",
                                     font=self.label_font, bg="#e0e0e0", fg="#555555", wraplength=450)
        self.label_info.pack(pady=(0, 20))

        # Etykieta do wyświetlania wybranej ścieżki pliku
        self.selected_file_path_var = tk.StringVar()
        self.selected_file_path_var.set("Nie wybrano pliku.")
        self.label_selected_file = tk.Label(main_frame, textvariable=self.selected_file_path_var,
                                            font=self.label_font, bg="#f0f0f0", fg="#005500",
                                            relief=tk.SUNKEN, bd=1, padx=5, pady=5)
        self.label_selected_file.pack(fill="x", pady=(0, 15))

        # Przycisk do wyboru pliku (niebieski kolor)
        self.select_button = tk.Button(main_frame, text="Wybierz plik HTML do przetworzenia",
                                        command=self._select_file_and_process,
                                        font=self.button_font, bg="#1E90FF", fg="white", # Niebieski kolor (DodgerBlue)
                                        activebackground="#0072E3", activeforeground="white", # Ciemniejszy niebieski po najechaniu
                                        padx=15, pady=8, relief=tk.RAISED, bd=2)
        self.select_button.pack(pady=10)

        # Stopka z informacją o prawach autorskich
        self.label_footer = tk.Label(self, text=f"© 2025 GEO ARCUS SP. Z O.O. Wszelkie prawa zastrzeżone.",
                                     font=self.footer_font, bg="#e0e0e0", fg="#777777")
        self.label_footer.pack(side="bottom", anchor="s", pady=5)

        # Etykieta z wersją programu na dole
        self.version_label = tk.Label(self, text=f"Wersja: {PROGRAM_VERSION}",
                                     font=self.version_font, bg="#e0e0e0", fg="#999999")
        self.version_label.pack(side="bottom", anchor="se", padx=10, pady=2)


    def _select_file_and_process(self):
        file_path = filedialog.askopenfilename(
            title="Wybierz plik HTML do konwersji",
            filetypes=[("Pliki HTML", "*.html"), ("Wszystkie pliki", "*.*")]
        )

        if file_path:
            self.selected_file_path_var.set(f"Wybrano: {os.path.basename(file_path)}")
            self.update_idletasks()
            self._process_file(file_path)
        else:
            self.selected_file_path_var.set("Nie wybrano pliku.")

    def _process_file(self, file_path):
        directory = os.path.dirname(file_path)
        output_file_name = "Wykaz punktów współrzędnych OSNOWY ewid.txt"
        output_full_path = os.path.join(directory, output_file_name)

        process_html_to_txt(file_path, output_full_path)
        
        self.selected_file_path_var.set("Operacja zakończona.")

if __name__ == "__main__":
    app = App()
    app.mainloop()