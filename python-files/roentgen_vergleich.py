
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import fitz  # PyMuPDF

def extract_z1_data(pdf_path):
    doc = fitz.open(pdf_path)
    z1_data = []
    for page in doc:
        text = page.get_text()
        lines = text.split('\n')
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 3:
                try:
                    pat_num = int(parts[0])
                    last_name = parts[1].strip(",")
                    z1_data.append((pat_num, last_name))
                except ValueError:
                    continue
    return pd.DataFrame(z1_data, columns=["Nummer", "Nachname"])

def extract_byzz_data(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    byzz_data = []
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) >= 3:
            try:
                nummer = int(parts[0])
                vorname = parts[1]
                nachname = parts[2]
                byzz_data.append((nummer, vorname, nachname))
            except ValueError:
                continue
    return pd.DataFrame(byzz_data, columns=["Nummer", "Vorname", "Nachname"])

def vergleichen():
    txt_path = filedialog.askopenfilename(title="BYZZ .txt-Datei auswählen", filetypes=[("Textdateien", "*.txt")])
    pdf_path = filedialog.askopenfilename(title="Z1 .pdf-Datei auswählen", filetypes=[("PDF-Dateien", "*.pdf")])

    if not txt_path or not pdf_path:
        messagebox.showerror("Fehler", "Beide Dateien müssen ausgewählt werden.")
        return

    df_byzz = extract_byzz_data(txt_path)
    df_z1 = extract_z1_data(pdf_path)
    df_missing = df_byzz[~df_byzz["Nummer"].isin(df_z1["Nummer"])]

    if df_missing.empty:
        messagebox.showinfo("Ergebnis", "Alle Röntgenbilder wurden abgerechnet.")
    else:
        export_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel-Datei", "*.xlsx")], title="Speichern unter")
        if export_path:
            df_missing.to_excel(export_path, index=False)
            messagebox.showinfo("Erfolg", f"{len(df_missing)} Einträge gespeichert unter:\n{export_path}")

def main():
    root = tk.Tk()
    root.title("Röntgen-Abgleich BYZZ ↔ Z1")
    root.geometry("400x200")

    label = tk.Label(root, text="Röntgenvergleich: BYZZ vs Z1", font=("Arial", 14))
    label.pack(pady=20)

    btn = tk.Button(root, text="Dateien auswählen und vergleichen", command=vergleichen, font=("Arial", 12))
    btn.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
