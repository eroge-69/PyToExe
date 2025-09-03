import os
import time
import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import getpass
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Fonction pour installer les modules nécessaires
def install_package(package):
    try:
        __import__(package)
        print(f"{package} est déjà installé.")
    except ImportError:
        print(f"Installation de {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"{package} installé avec succès.")

# Installer les dépendances nécessaires
install_package("watchdog")
install_package("customtkinter")

class TempFolderHandler(FileSystemEventHandler):
    def __init__(self, destination_path):
        self.destination_path = destination_path
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

    def on_created(self, event):
        try:
            src_path = event.src_path
            item_name = os.path.basename(src_path)

            # Ignorer les fichiers avec l'extension .tmp
            if not event.is_directory and src_path.lower().endswith('.tmp'):
                print(f"Fichier .tmp ignoré: {item_name}")
                return

            dest_path = os.path.join(self.destination_path, item_name)

            # Si c'est un dossier, copier récursivement
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                print(f"Dossier ajouté et copié: {item_name} -> {dest_path}")
            # Si c'est un fichier, copier directement
            else:
                shutil.copy2(src_path, dest_path)
                print(f"Fichier ajouté et copié: {item_name} -> {dest_path}")
        except Exception as e:
            print(f"Erreur lors de la copie de {src_path}: {e}")

def monitor_temp_folder(temp_path, destination_path):
    event_handler = TempFolderHandler(destination_path)
    observer = Observer()
    observer.schedule(event_handler, temp_path, recursive=True)  # Surveillance récursive
    observer.start()
    print(f"Surveillance du dossier {temp_path} démarrée...")
    try:
        while True:
            time.sleep(0.001)  # 1ms pour une réactivité maximale
    except KeyboardInterrupt:
        observer.stop()
        print("Surveillance arrêtée.")
    observer.join()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Surveillance de Dossier")
        self.root.geometry("400x300")
        ctk.set_appearance_mode("System")  # Modes: "Light", "Dark", "System"
        ctk.set_default_color_theme("blue")  # Thèmes: "blue", "green", "dark-blue"

        # Variables
        self.temp_path = ctk.StringVar()
        self.destination_path = ctk.StringVar()

        # Interface
        self.label_temp = ctk.CTkLabel(root, text="Dossier à surveiller:")
        self.label_temp.pack(pady=10)

        self.entry_temp = ctk.CTkEntry(root, textvariable=self.temp_path, width=300)
        self.entry_temp.pack(pady=5)

        self.button_browse_temp = ctk.CTkButton(root, text="Parcourir", command=self.browse_temp)
        self.button_browse_temp.pack(pady=5)

        self.label_dest = ctk.CTkLabel(root, text="Dossier de destination:")
        self.label_dest.pack(pady=10)

        self.entry_dest = ctk.CTkEntry(root, textvariable=self.destination_path, width=300)
        self.entry_dest.pack(pady=5)

        self.button_browse_dest = ctk.CTkButton(root, text="Parcourir", command=self.browse_dest)
        self.button_browse_dest.pack(pady=5)

        self.button_start = ctk.CTkButton(root, text="Démarrer la surveillance", command=self.start_monitoring)
        self.button_start.pack(pady=20)

        # Initialiser avec le dossier temporaire par défaut
        username = getpass.getuser()
        default_temp = os.path.join(r"C:\Users", username, r"AppData\Local\Temp")
        self.temp_path.set(default_temp)
        self.destination_path.set(os.path.join(os.path.dirname(os.path.abspath(__file__)), "TempFiles"))

    def browse_temp(self):
        folder = filedialog.askdirectory()
        if folder:
            self.temp_path.set(folder)

    def browse_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            self.destination_path.set(folder)

    def start_monitoring(self):
        temp_folder = self.temp_path.get()
        destination_folder = self.destination_path.get()

        if not os.path.exists(temp_folder):
            messagebox.showerror("Erreur", "Le dossier à surveiller n'existe pas !")
            return
        if not destination_folder:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier de destination !")
            return

        self.button_start.configure(state="disabled")
        self.root.update()
        monitor_temp_folder(temp_folder, destination_folder)
        self.button_start.configure(state="normal")

if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()
