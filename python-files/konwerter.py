import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import os
from datetime import datetime

class LoadstoneToTrekkerConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Konwerter Loadstone do Trekker Breeze")
        self.root.geometry("400x200")
        self.file_path_var = tk.StringVar()
        self.file_label = tk.Label(root, textvariable=self.file_path_var, wraplength=350)
        self.file_label.pack(pady=10)
        self.browse_button = tk.Button(root, text="Przeglądaj", command=self.browse_file)
        self.browse_button.pack(pady=10)
        self.convert_button = tk.Button(root, text="Konwertuj", command=self.convert_file)
        self.convert_button.pack(pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Pliki tekstowe", "*.txt"), ("Wszystkie pliki", "*.*")])
        if file_path:
            self.file_path_var.set(file_path)

    def convert_to_decimal(self, coord):
        try:
            return str(float(coord) / 100000)
        except ValueError:
            return None

    def truncate_field(self, value, max_length):
        """Skraca wartość do maksymalnej liczby znaków."""
        return value[:max_length] if value else ""

    def convert_file(self):
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("Błąd", "Proszę wybrać plik do konwersji!")
            return

        input_dir = os.path.dirname(file_path)
        input_filename = os.path.splitext(os.path.basename(file_path))[0]
        output_csv = os.path.join(input_dir, f"{input_filename}_converted.csv")
        summary_file = os.path.join(input_dir, f"{input_filename}_summary.txt")

        total_lines = 0
        successful_lines = 0
        error_lines = []

        try:
            try:
                infile = open(file_path, 'r', encoding='utf-8')
            except UnicodeDecodeError:
                infile = open(file_path, 'r', encoding='cp1252')

            with infile, open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
                outfile.write("; Plik CSV dla Trekker Breeze - przetworzone z Loadstone\n")

                for line in infile:
                    line = line.strip()
                    total_lines += 1
                    if not line or line.startswith(';'):
                        continue

                    parts = line.split(',', 2)
                    if len(parts) != 3:
                        error_lines.append((line, "Nieprawidłowa liczba pól (oczekiwano 3)"))
                        continue

                    name = self.truncate_field(parts[0].strip('"'), 40)
                    latitude = self.convert_to_decimal(parts[1])
                    longitude = self.convert_to_decimal(parts[2])

                    if latitude is None or longitude is None:
                        error_lines.append((line, "Błąd konwersji współrzędnych"))
                        continue

                    # Definiowanie pól z limitami znaków
                    favorite = self.truncate_field("0", 1)
                    category = self.truncate_field("0000", 4)
                    description = self.truncate_field("DESTINATION", 100)
                    street_no = self.truncate_field("", 20)
                    street_name = self.truncate_field("", 100)
                    town_name = self.truncate_field("", 100)
                    province = self.truncate_field("", 30)
                    postal_code = self.truncate_field("", 15)
                    country_name = self.truncate_field("", 25)
                    phone_number = self.truncate_field("", 20)
                    activated = self.truncate_field("", 0)
                    audio_path = self.truncate_field("", 0)

                    row = [
                        longitude,
                        latitude,
                        name,
                        favorite,
                        category,
                        description,
                        street_no,
                        street_name,
                        town_name,
                        province,
                        postal_code,
                        country_name,
                        phone_number,
                        activated,
                        audio_path
                    ]
                    writer.writerow(row)
                    successful_lines += 1

            with open(summary_file, 'w', encoding='utf-8') as summary:
                summary.write(f"Podsumowanie konwersji - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                summary.write(f"Plik wejściowy: {file_path}\n")
                summary.write(f"Plik wyjściowy: {output_csv}\n")
                summary.write(f"Całkowita liczba linii: {total_lines}\n")
                summary.write(f"Poprawnie przekonwertowane linie: {successful_lines}\n")
                summary.write(f"Błędne linie: {total_lines - successful_lines}\n")
                summary.write("\nSzczegóły błędów:\n")
                if error_lines:
                    for err_line, reason in error_lines:
                        summary.write(f"- Linia: {err_line}\n  Powód: {reason}\n")
                else:
                    summary.write("Brak błędów.\n")

            messagebox.showinfo("Sukces", f"Konwersja zakończona.\nPlik CSV: {output_csv}\nPodsumowanie: {summary_file}")
            self.root.destroy()
            os.startfile(input_dir)

        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas konwersji: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoadstoneToTrekkerConverter(root)
    root.mainloop()
