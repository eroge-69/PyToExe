import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd
import json
import os

class ExcelToJsonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel → JSON Converter")
        self.excel_path = None
        self.json_str = ""

        # Bouton pour charger le fichier Excel
        self.load_btn = tk.Button(root, text="Charger Excel", command=self.load_excel)
        self.load_btn.pack(pady=8)

        # Bouton pour convertir en JSON
        self.convert_btn = tk.Button(root, text="Convertir en JSON", command=self.convert_to_json, state=tk.DISABLED)
        self.convert_btn.pack(pady=8)

        # Nouveau bouton pour convertir JSON → Excel
        self.json_to_excel_btn = tk.Button(root, text="JSON → Excel", command=self.json_to_excel)
        self.json_to_excel_btn.pack(pady=8)

        # Zone de texte scrollable pour afficher le JSON
        self.text_area = scrolledtext.ScrolledText(root, width=90, height=30, font=("Consolas", 10))
        self.text_area.pack(padx=8, pady=8)

    def load_excel(self):
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier Excel",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        if file_path:
            self.excel_path = file_path
            self.convert_btn.config(state=tk.NORMAL)
            messagebox.showinfo("Fichier chargé", f"Fichier sélectionné :\n{os.path.basename(file_path)}")
        else:
            self.excel_path = None
            self.convert_btn.config(state=tk.DISABLED)

    def convert_to_json(self):
        try:
            df = pd.read_excel(self.excel_path)
            data = df.to_dict(orient='records')
            self.json_str = json.dumps(data, ensure_ascii=False, indent=2)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, self.json_str)
            messagebox.showinfo("Conversion réussie", "Conversion Excel → JSON effectuée !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la conversion :\n{str(e)}")

    def json_to_excel(self):
        json_text = self.text_area.get(1.0, tk.END).strip()
        if not json_text:
            messagebox.showerror("Erreur", "La zone de texte JSON est vide !")
            return
        try:
            data = json.loads(json_text)
            # Si le JSON est un dictionnaire unique, on le met dans une liste
            if isinstance(data, dict):
                data = [data]
            df = pd.DataFrame(data)
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx *.xls")],
                title="Enregistrer sous..."
            )
            if save_path:
                df.to_excel(save_path, index=False)
                messagebox.showinfo("Succès", f"Fichier Excel enregistré :\n{save_path}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la conversion JSON → Excel :\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelToJsonApp(root)
    root.mainloop()


