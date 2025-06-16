import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import glob
import re
from datetime import datetime
import win32print
import win32api

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"directory": "", "show_implants": True, "show_teeth": True}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def parse_file(filepath, show_implants, show_teeth):
    results = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

        name = os.path.basename(filepath).replace(".constructionInfo", "")
        lines = []

        if show_implants:
            implants = re.findall(r"<ImplantLibraryEntryDisplayInformation>(.*?)</ImplantLibraryEntryDisplayInformation>", content)
            teeth = re.findall(r"<ToothLibraryToothNumber>(.*?)</ToothLibraryToothNumber>", content)
            if implants and teeth:
                for i in range(min(len(implants), len(teeth))):
                    lines.append(f"{teeth[i]} ===> {implants[i]}")
        if show_teeth:
            match = re.search(r"<ToothLibraryName>(.*?)</ToothLibraryName>", content)
            if match:
                lines.append(f"LIBRERIA DE DIENTES: {match.group(1)}")

        if lines:
            return {
                "name": name,
                "path": filepath,
                "modified": os.path.getmtime(filepath),
                "data": lines
            }
    return None

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Explorador de Pacientes")
        self.config = load_config()
        self.results = []

        self.setup_ui()
        if self.config["directory"]:
            self.load_patient_list()

    def setup_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        # Ajustes
        tk.Button(frame, text="Seleccionar Directorio", command=self.select_directory).pack(fill='x')
        self.var_implants = tk.BooleanVar(value=self.config["show_implants"])
        self.var_teeth = tk.BooleanVar(value=self.config["show_teeth"])
        tk.Checkbutton(frame, text="Mostrar Librerías de Implantes", variable=self.var_implants).pack(anchor="w")
        tk.Checkbutton(frame, text="Mostrar Librerías de Dientes", variable=self.var_teeth).pack(anchor="w")
        tk.Button(frame, text="Actualizar Lista de Pacientes", command=self.load_patient_list).pack(fill='x', pady=(5, 10))

        # Lista de pacientes
        self.listbox = tk.Listbox(frame, width=80, height=20)
        self.listbox.pack()
        self.listbox.bind("<<ListboxSelect>>", self.display_patient_data)

        # Resultados
        self.text = tk.Text(frame, height=15)
        self.text.pack()

        # Botones exportar/imprimir
        tk.Button(frame, text="Exportar Resultado a TXT", command=self.export_txt).pack(fill='x', pady=3)
        tk.Button(frame, text="Imprimir Resultado", command=self.print_result).pack(fill='x')

    def select_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.config["directory"] = dir_path
            save_config(self.config)
            self.load_patient_list()

    def load_patient_list(self):
        self.config["show_implants"] = self.var_implants.get()
        self.config["show_teeth"] = self.var_teeth.get()
        save_config(self.config)

        pattern = os.path.join(self.config["directory"], "**", "*.constructionInfo")
        files = glob.glob(pattern, recursive=True)

        parsed_files = []
        for file in files:
            parsed = parse_file(file, self.var_implants.get(), self.var_teeth.get())
            if parsed:
                parsed_files.append(parsed)

        # Ordenar por fecha de modificación
        parsed_files.sort(key=lambda x: x["modified"], reverse=True)
        self.results = parsed_files

        self.listbox.delete(0, tk.END)
        for item in parsed_files:
            self.listbox.insert(tk.END, item["name"])

    def display_patient_data(self, event):
        selection = self.listbox.curselection()
        if selection:
            idx = selection[0]
            data = self.results[idx]
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, f"{data['name']}\n")
            self.text.insert(tk.END, "\n".join(data["data"]))

    def export_txt(self):
        result = self.text.get(1.0, tk.END).strip()
        if not result:
            messagebox.showwarning("Sin datos", "No hay datos para exportar.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(result)
            messagebox.showinfo("Exportación", f"Datos exportados a {path}")

    def print_result(self):
        result = self.text.get(1.0, tk.END).strip()
        if not result:
            messagebox.showwarning("Sin datos", "No hay datos para imprimir.")
            return
        filename = "temp_print.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result)
        win32api.ShellExecute(0, "print", filename, None, ".", 0)

# Ejecutar
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
