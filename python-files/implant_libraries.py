import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import glob
import re
from datetime import datetime

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "directory": "",
            "show_implants": False,
            "show_teeth": False
        }

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def extract_info(filepath, show_implants, show_teeth):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    implant_data = re.findall(
        r"<ImplantLibraryEntryDisplayInformation>(.*?)</ImplantLibraryEntryDisplayInformation>", content)
    if not implant_data:
        return None

    result = ""

    if show_implants and not show_teeth:
        entries = re.findall(
            r"<ToothLibraryToothNumber>(.*?)</ToothLibraryToothNumber>.*?<ImplantLibraryEntryDisplayInformation>(.*?)</ImplantLibraryEntryDisplayInformation>",
            content,
            re.DOTALL
        )
        for tooth, implant in entries:
            result += f"{tooth} ===> {implant}\n"

    elif show_implants and show_teeth:
        tooth_lib_name_match = re.search(
            r"<ToothLibraryName>(.*?)</ToothLibraryName>", content)
        if tooth_lib_name_match:
            result += "TOOTH LIBRARY: " + \
                tooth_lib_name_match.group(1) + "\n"

        entries = re.findall(
            r"<ToothLibraryToothNumber>(.*?)</ToothLibraryToothNumber>.*?<ImplantLibraryEntryDisplayInformation>(.*?)</ImplantLibraryEntryDisplayInformation>",
            content,
            re.DOTALL
        )
        for tooth, implant in entries:
            result += f"{tooth} ===> {implant}\n"

    return result.strip() if result else None


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Implant and Tooth Library Viewer")
        self.root.geometry("900x600")

        self.config = load_config()

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.create_widgets()
        self.update_patient_list()

    def create_widgets(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(pady=10, fill='x')

        ttk.Button(top_frame, text="Select Directory", command=self.select_directory).pack(side="left", padx=5)

        self.implant_var = tk.BooleanVar(value=self.config["show_implants"])
        ttk.Checkbutton(top_frame, text="Show Implant Libraries", variable=self.implant_var,
                        command=self.update_config).pack(side="left")

        self.teeth_var = tk.BooleanVar(value=self.config["show_teeth"])
        ttk.Checkbutton(top_frame, text="Show Tooth Libraries", variable=self.teeth_var,
                        command=self.update_config).pack(side="left")

        ttk.Button(top_frame, text="Refresh List", command=self.update_patient_list).pack(side="left", padx=5)

        ttk.Label(top_frame, text="Search Patient:").pack(side="left", padx=(20, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_patients())
        ttk.Entry(top_frame, textvariable=self.search_var, width=25).pack(side="left")

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10)

        self.listbox = tk.Listbox(main_frame, width=40)
        self.listbox.pack(side="left", fill="y", padx=(0, 10))
        self.listbox.bind("<<ListboxSelect>>", self.show_patient_info)

        self.info_text = tk.Text(main_frame, wrap="word")
        self.info_text.pack(side="left", fill="both", expand=True)

        export_button = ttk.Button(self.root, text="Export to .txt", command=self.export_info)
        export_button.pack(pady=10)

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.config["directory"] = directory
            save_config(self.config)
            self.update_patient_list()

    def update_config(self):
        self.config["show_implants"] = self.implant_var.get()
        self.config["show_teeth"] = self.teeth_var.get()
        save_config(self.config)
        self.update_patient_list()

    def update_patient_list(self):
        self.all_patients = []
        self.listbox.delete(0, tk.END)
        directory = self.config["directory"]

        if not os.path.isdir(directory):
            messagebox.showwarning("Invalid Directory", "Please select a valid directory.")
            return

        files = glob.glob(os.path.join(directory, "**", "*.constructionInfo"), recursive=True)
        files = sorted(files, key=lambda x: os.path.getmtime(x), reverse=True)

        for f in files:
            info = extract_info(f, self.config["show_implants"], self.config["show_teeth"])
            if info:
                patient_name = os.path.splitext(os.path.basename(f))[0]
                self.all_patients.append((patient_name, info))

        self.filter_patients()

    def filter_patients(self):
        search_term = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        self.filtered_patients = []

        for name, info in self.all_patients:
            if search_term in name.lower():
                self.listbox.insert(tk.END, name)
                self.filtered_patients.append((name, info))

    def show_patient_info(self, event):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            _, info = self.filtered_patients[index]
            self.info_text.delete("1.0", tk.END)
            self.info_text.insert(tk.END, info)

    def export_info(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("No selection", "Please select a patient to export.")
            return

        index = selection[0]
        patient_name, info = self.filtered_patients[index]

        content = f"Patient: {patient_name}\n\n{info.strip()}"

        file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text File", "*.txt")])
        if file:
            with open(file, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Exported", "Information successfully exported.")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
