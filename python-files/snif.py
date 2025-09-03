import os
import time
import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
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

class DiskHandler(FileSystemEventHandler):
    def __init__(self, destination_path):
        self.destination_path = os.path.abspath(destination_path)  # Normaliser le chemin
        self.excluded_folder = os.path.abspath(r"C:\Users\SALAM\Desktop\Temp SNIFFER")  # Dossier à exclure
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

    def on_created(self, event):
        try:
            src_path = os.path.abspath(event.src_path)  # Normaliser le chemin source

            # Ignorer les événements dans le dossier exclu
            if src_path.startswith(self.excluded_folder):
                print(f"Événement ignoré dans le dossier exclu: {src_path}")
                return

            item_name = os.path.basename(src_path)

            # Ignorer les fichiers avec l'extension .tmp
            if not event.is_directory and src_path.lower().endswith('.tmp'):
                print(f"Fichier .tmp ignoré: {item_name}")
                return

            # Construire le chemin de destination en préservant la structure du disque
            relative_path = os.path.relpath(src_path, "C:\\")
            dest_path = os.path.join(self.destination_path, relative_path)

            # Créer les dossiers parents si nécessaire
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            # Si c'est un dossier, copier récursivement
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                print(f"Dossier ajouté et copié: {item_name} -> {dest_path}")
            # Si c'est un fichier, copier directement
            else:
                shutil.copy2(src_path, dest_path)
                print(f"Fichier ajouté et copié: {item_name} -> {dest_path}")

        except PermissionError:
            print(f"Erreur de permission pour {src_path}: accès refusé.")
        except Exception as e:
            print(f"Erreur lors de la copie de {src_path}: {e}")

def monitor_disk(disk_path, destination_path):
    event_handler = DiskHandler(destination_path)
    observer = Observer()
    observer.schedule(event_handler, disk_path, recursive=True)  # Surveillance récursive
    observer.start()
    print(f"Surveillance du disque {disk_path} démarrée...")
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
        self.root.title("Surveillance du Disque C:\\")
        self.root.geometry("400x300")
        ctk.set_appearance_mode("System")  # Modes: "Light", "Dark", "System"
        ctk.set_default_color_theme("blue")  # Thèmes: "blue", "green", "dark-blue"

        # Variables
        self.disk_path = ctk.StringVar(value="C:\\")  # Par défaut, surveiller C:\
        self.destination_path = ctk.StringVar()

        # Interface
        self.label_disk = ctk.CTkLabel(root, text="Disque à surveiller: C:\\ (fixe)")
        self.label_disk.pack(pady=10)

        self.label_dest = ctk.CTkLabel(root, text="Dossier de destination:")
        self.label_dest.pack(pady=10)

        self.entry_dest = ctk.CTkEntry(root, textvariable=self.destination_path, width=300)
        self.entry_dest.pack(pady=5)

        self.button_browse_dest = ctk.CTkButton(root, text="Parcourir", command=self.browse_dest)
        self.button_browse_dest.pack(pady=5)

        self.button_start = ctk.CTkButton(root, text="Démarrer la surveillance", command=self.start_monitoring)
        self.button_start.pack(pady=20)

        # Dossier de destination par défaut
        self.destination_path.set(r"C:\Users\SALAM\Desktop\Temp SNIFFER\TempFiles")

    def browse_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            self.destination_path.set(folder)

    def start_monitoring(self):
        disk_folder = self.disk_path.get()
        destination_folder = self.destination_path.get()

        if not os.path.exists(disk_folder):
            messagebox.showerror("Erreur", "Le disque à surveiller n'existe pas !")
            return
        if not destination_folder:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier de destination !")
            return

        try:
            self.button_start.configure(state="disabled")
            self.root.update()
            monitor_disk(disk_folder, destination_folder)
        except PermissionError:
            messagebox.showerror("Erreur", "Permission refusée pour surveiller certains dossiers. Exécutez en mode administrateur.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite: {e}")
        finally:
            self.button_start.configure(state="normal")

if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()
