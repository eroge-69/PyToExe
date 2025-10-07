import os
import tkinter as tk
from tkinter import filedialog
import csv

def get_folder_path():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Ordner auswählen")
    return folder_selected

def collect_folder_data(base_path):
    folder_data = []
    for root, dirs, files in os.walk(base_path):
        if root == base_path:
            continue  # Skip the base folder itself
        subfolder_name = os.path.relpath(root, base_path)

        # Filter only files (ignore subfolders)
        file_list = [f for f in files if os.path.isfile(os.path.join(root, f))]
        file_list_str = "\n".join(file_list) if file_list else ""
        folder_data.append((subfolder_name, file_list_str))
    return folder_data

def write_to_excel(folder_data, output_file):
    try:
        # Use utf-8-sig for Excel compatibility with umlauts
        with open(output_file, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(["Subfolder", "Files"])
            for subfolder, files in folder_data:
                writer.writerow([subfolder, files])
    except PermissionError:
        print(f"\n❌ Fehler: Die Datei '{output_file}' ist möglicherweise geöffnet.")
        print("Bitte  Datei schließen und  Skript erneut ausführen.")
        return False
    return True

def main():
    print("📁 Bitte Ordner auswählen...")
    folder_path = get_folder_path()
    if not folder_path:
        print("⚠️ Kein Ordner ausgewählt. Das Programm wird beendet.")
        input("\nDrücken Sie die Eingabetaste zum Schließen...")
        return

    folder_data = collect_folder_data(folder_path)
    output_file = os.path.join(folder_path, "folder_file_list.csv")
    success = write_to_excel(folder_data, output_file)

    if success:
        print(f"\n✅ Erfolg! Die Datei wurde gespeichert unter:\n{output_file}")
    input("\nDrücken Sie die Eingabetaste zum Schließen...")


main()