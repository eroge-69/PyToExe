
import tkinter as tk
from tkinter import ttk, messagebox
import shutil
import os
import subprocess

font_packages = {
    "CWW": r"\\parfedvapp01.emea.corp.ipgnetwork.com\deploy$\___Fonts\CWW\Fonts",
    "FUB": r"\\parfedvapp01.emea.corp.ipgnetwork.com\deploy$\___Fonts\FUB\Fonts",
    "MEW": r"\\parfedvapp01.emea.corp.ipgnetwork.com\deploy$\___Fonts\MEW\Fonts",
    "INI": r"\\parfedvapp01.emea.corp.ipgnetwork.com\deploy$\___Fonts\INI\Fonts",
    "IPG": r"\\parfedvapp01.emea.corp.ipgnetwork.com\deploy$\___Fonts\IPG\Fonts",
    "MBW MEW": r"\\parfedvapp01.emea.corp.ipgnetwork.com\deploy$\___Fonts\Mediabrands\Fonts",
    "UMW": r"\\parfedvapp01.emea.corp.ipgnetwork.com\deploy$\___Fonts\UMW\Fonts"
}

def copy_fonts(source_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    for file in os.listdir(dest_dir):
        os.remove(os.path.join(dest_dir, file))
    for file in os.listdir(source_dir):
        if file.lower().endswith(".ttf") or file.lower().endswith(".otf"):
            shutil.copy2(os.path.join(source_dir, file), dest_dir)

def generate_msi(package_name):
    source_dir = font_packages[package_name]
    dest_dir = r"C:\Temp\Fonts"

    try:
        copy_fonts(source_dir, dest_dir)
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nella copia dei font:\n{e}")
        return

    try:
        ps1_script = r"C:\Temp\fonts_wix.ps1"
        subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", ps1_script], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Errore", f"Errore nell'esecuzione di fonts_wix.ps1:\n{e}")
        return

    try:
        output_name = f"{package_name}_fonts_Installer.msi"
        subprocess.run(["wix", "build", r"C:\Temp\fonts.wxs", "-o", fr"C:\Temp\{output_name}"], check=True)
        messagebox.showinfo("Successo", f"MSI creato con successo:\n{output_name}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Errore", f"Errore nella compilazione MSI:\n{e}")

def create_gui():
    root = tk.Tk()
    root.title("Font MSI Builder")
    root.geometry("400x180")
    root.resizable(False, False)

    label = tk.Label(root, text="Seleziona il pacchetto font:", font=("Segoe UI", 10))
    label.pack(pady=10)

    selected_pkg = tk.StringVar()
    combo = ttk.Combobox(root, textvariable=selected_pkg, values=list(font_packages.keys()), state="readonly", font=("Segoe UI", 10))
    combo.pack(pady=5)
    combo.current(0)

    def on_generate():
        pkg = selected_pkg.get()
        if pkg:
            generate_msi(pkg)

    generate_btn = tk.Button(root, text="Genera MSI", command=on_generate, font=("Segoe UI", 10), width=20)
    generate_btn.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
