import os
import shutil
import time
import datetime
import threading
import queue
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Die folgende Bibliothek wird benötigt, um mit Outlook zu interagieren.
# Installieren Sie sie mit: pip install pywin32
try:
    import win32com.client as win32
    import pythoncom
except ImportError:
    win32 = None
    pythoncom = None

# Definiere die Standard-Quell- und Zielordner.
# Wichtiger Hinweis: Verwenden Sie Forward Slashes (/) für bessere Kompatibilität.
DEFAULT_SOURCE_FOLDER = r"C:/KyoScan"
DEFAULT_DESTINATION_FOLDER = r"C:/Users/DRKairport/OneDrive - Deutsches Rotes Kreuz - Kreisverband Köln e.V/Dateien von Erste-Hilfe-Station-Flughafen - DRK Köln e.V_ - !Gemeinsam.26/07_Checklisten"

class NewFileHandler(FileSystemEventHandler):
    """
    Ein Event-Handler, der auf neue Dateien im Quellordner reagiert.
    Die on_created-Methode sendet Nachrichten an die GUI über eine Queue.
    """
    def __init__(self, app_instance):
        super().__init__()
        self.app_instance = app_instance

    def on_created(self, event):
        """
        Wird aufgerufen, wenn eine neue Datei erstellt wird.
        """
        # Initialisiere COM für diesen Thread, bevor Outlook verwendet wird.
        if pythoncom:
            pythoncom.CoInitialize()
            
        try:
            if not event.is_directory:
                source_file = event.src_path
                
                # Stelle sicher, dass der Pfad eine Datei ist (und keine Zwischenordner-Ereignisse)
                if os.path.isfile(source_file):
                    self.app_instance.log_message("-" * 50)
                    self.app_instance.log_message(f"Neue Datei gefunden: '{source_file}'")
                    
                    try:
                        # Hole das Änderungsdatum der Originaldatei als Timestamp.
                        mtime = os.path.getmtime(source_file)
                        mod_time = datetime.datetime.fromtimestamp(mtime)
                        
                        # Erstelle den Pfad für den Unterordner basierend auf Jahr und Monat.
                        subfolder_path = os.path.join(
                            self.app_instance.destination_folder,
                            mod_time.strftime("%Y"),
                            mod_time.strftime("%m")
                        )
                        
                        # Erstelle das Verzeichnis, wenn es nicht existiert.
                        os.makedirs(subfolder_path, exist_ok=True)

                        # Formatiere das Datum als String (z.B. "2024_08_03").
                        date_str = mod_time.strftime("%Y_%m_%d")
                        
                        # Hole den ursprünglichen Dateinamen und die Dateiendung.
                        _, file_extension = os.path.splitext(os.path.basename(source_file))

                        # Lese den aktuellen Präfix-Wert direkt aus dem GUI-Feld.
                        filename_prefix = self.app_instance.filename_entry.get().strip()

                        # Erstelle den neuen Dateinamen mit dem benutzerdefinierten Präfix, dem Datum und der ursprünglichen Endung.
                        base_filename = f"{filename_prefix}_{date_str}" if filename_prefix else date_str
                        new_filename = f"{base_filename}{file_extension}"
                        
                        # Finde einen eindeutigen Dateinamen, um Überschreibungen zu vermeiden.
                        destination_file = os.path.join(subfolder_path, new_filename)
                        counter = 1
                        while os.path.exists(destination_file):
                            new_filename = f"{base_filename}_{counter}{file_extension}"
                            destination_file = os.path.join(subfolder_path, new_filename)
                            counter += 1
                        
                        # Kopiere die Datei vom Quellordner in den Zielordner und benenne sie um.
                        shutil.copy2(source_file, destination_file)
                        self.app_instance.log_message(f"Datei erfolgreich kopiert und umbenannt nach: '{destination_file}'")
                        
                        # Rufe die Funktion zum Erstellen der Outlook-E-Mail auf und übergebe das Datum
                        self.app_instance.send_outlook_email(destination_file, mod_time)
                            
                        self.app_instance.log_message("-" * 50)
                    
                    except Exception as e:
                        self.app_instance.log_message(f"Fehler beim Kopieren oder Umbenennen der Datei '{source_file}': {e}")
                        self.app_instance.log_message("-" * 50)
        finally:
            # Gib die COM-Ressourcen für diesen Thread frei.
            if pythoncom:
                pythoncom.CoUninitialize()

class PDFMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automatische Dateiüberwachung und Kopierung")
        self.root.geometry("600x600")

        self.source_folder = ""
        self.destination_folder = ""
        self.observer = None
        self.log_queue = queue.Queue()
        
        # UI-Elemente erstellen
        self.create_widgets()
        
        # Überprüfen, ob die Standard-Ordner existieren und sie als Standard setzen
        if os.path.isdir(DEFAULT_SOURCE_FOLDER):
            self.source_folder = DEFAULT_SOURCE_FOLDER
            self.source_path_label.config(text=f"Quellordner: {self.source_folder}")
        if os.path.isdir(DEFAULT_DESTINATION_FOLDER):
            self.destination_folder = DEFAULT_DESTINATION_FOLDER
            self.destination_path_label.config(text=f"Zielordner: {self.destination_folder}")

        # Startet die Überprüfung der Queue in einem regelmäßigen Intervall
        self.root.after(100, self.process_queue)
        
        # NEU: Startet die Überwachung automatisch beim Programmstart, wenn gültige Ordner konfiguriert sind.
        if self.source_folder and self.destination_folder:
            self.start_monitoring()

    def create_widgets(self):
        """Erstellt die Widgets für die Benutzeroberfläche."""
        # Frame für die Ordnerauswahl
        folder_frame = tk.Frame(self.root, padx=10, pady=10)
        folder_frame.pack(fill="x")
        
        # Quellordner
        tk.Label(folder_frame, text="Quellordner:", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.source_path_label = tk.Label(folder_frame, text="Kein Ordner ausgewählt", wraplength=550, justify="left")
        self.source_path_label.pack(fill="x", pady=(0, 5))
        tk.Button(folder_frame, text="Quellordner auswählen", command=self.select_source_folder).pack(pady=(0, 10))
        
        # Zielordner
        tk.Label(folder_frame, text="Zielordner:", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.destination_path_label = tk.Label(folder_frame, text="Kein Ordner ausgewählt", wraplength=550, justify="left")
        self.destination_path_label.pack(fill="x", pady=(0, 5))
        tk.Button(folder_frame, text="Zielordner auswählen", command=self.select_destination_folder).pack(pady=(0, 10))

        # Eingabefeld für den Dateinamen-Präfix
        tk.Label(folder_frame, text="Dateiname-Präfix (optional):", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(10, 0))
        self.filename_entry = tk.Entry(folder_frame)
        self.filename_entry.insert(0, "")
        self.filename_entry.pack(fill="x", pady=(0, 10))
        
        # Frame für die Steuerung
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(fill="x")
        self.start_button = tk.Button(control_frame, text="Überwachung starten", command=self.start_monitoring, font=("Helvetica", 12, "bold"), bg="green", fg="white")
        self.start_button.pack(side="left", padx=(0, 5), expand=True, fill="x")
        self.stop_button = tk.Button(control_frame, text="Überwachung stoppen", command=self.stop_monitoring, font=("Helvetica", 12, "bold"), bg="red", fg="white", state="disabled")
        self.stop_button.pack(side="right", padx=(5, 0), expand=True, fill="x")
        
        # Frame für das Log
        log_frame = tk.Frame(self.root, padx=10, pady=10)
        log_frame.pack(fill="both", expand=True)
        tk.Label(log_frame, text="Aktivitäten-Log:", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled', height=10)
        self.log_text.pack(fill="both", expand=True)

    def log_message(self, message):
        """Fügt eine Nachricht zur Log-Queue hinzu."""
        self.log_queue.put(message)

    def select_source_folder(self):
        """Öffnet einen Dialog zur Auswahl des Quellordners."""
        new_source_folder = filedialog.askdirectory(initialdir=self.source_folder or DEFAULT_SOURCE_FOLDER, title="Wählen Sie den Quellordner")
        if new_source_folder:
            self.source_folder = new_source_folder
            self.source_path_label.config(text=f"Quellordner: {self.source_folder}")
    
    def select_destination_folder(self):
        """Öffnet einen Dialog zur Auswahl des Zielordners."""
        new_destination_folder = filedialog.askdirectory(initialdir=self.destination_folder or DEFAULT_DESTINATION_FOLDER, title="Wählen Sie den Zielordner")
        if new_destination_folder:
            self.destination_folder = new_destination_folder
            self.destination_path_label.config(text=f"Zielordner: {self.destination_folder}")
            
    def start_monitoring(self):
        """Startet die Überwachung des Quellordners in einem separaten Thread."""
        if not self.source_folder or not os.path.isdir(self.source_folder):
            messagebox.showerror("Fehler", "Bitte wählen Sie einen gültigen Quellordner aus.")
            return
        
        if not self.destination_folder or not os.path.isdir(self.destination_folder):
            messagebox.showerror("Fehler", "Bitte wählen Sie einen gültigen Zielordner aus.")
            return

        self.log_message("Überwachung wird gestartet...\n")
        
        try:
            # Wir übergeben jetzt das gesamte Eingabefeld an den Event-Handler.
            event_handler = NewFileHandler(self)
            
            self.observer = Observer()
            self.observer.schedule(event_handler, self.source_folder, recursive=False)
            self.observer.start()

            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            filename_prefix = self.filename_entry.get().strip()
            self.log_message(f"Überwachung von '{self.source_folder}' gestartet.")
            self.log_message(f"Neue Dateien werden mit dem Präfix '{filename_prefix}' und dem Änderungsdatum in den Ordner '{self.destination_folder}' kopiert.")
        
        except Exception as e:
            self.log_message(f"Fehler beim Starten der Überwachung: {e}")
            self.stop_monitoring()

    def stop_monitoring(self):
        """Stoppt die Überwachung."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            
            self.log_message("Überwachung gestoppt.")
            
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
    
    def process_queue(self):
        """Verarbeitet Nachrichten aus der Log-Queue und fügt sie dem Log-Feld hinzu."""
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.log_text.configure(state='normal')
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)  # Scrolle automatisch nach unten
            self.log_text.configure(state='disabled')
            self.log_queue.task_done()
        self.root.after(100, self.process_queue) # Ruft sich selbst in 100ms wieder auf

    def send_outlook_email(self, file_path, mod_time):
        """
        Erstellt eine neue Outlook-E-Mail mit der kopierten Datei als Anhang.
        Diese Funktion ist jetzt Teil der Hauptanwendung, um den Code besser zu strukturieren.
        """
        if not win32:
            self.log_message("Warnung: pywin32 nicht installiert. E-Mail-Funktion ist deaktiviert.")
            return
            
        try:
            # Versuche, eine laufende Outlook-Instanz zu erhalten.
            outlook = win32.GetActiveObject('Outlook.Application')
            self.log_message("Verbunden mit einer laufenden Outlook-Instanz.")
        except:
            # Wenn keine Instanz läuft, erstelle eine neue.
            try:
                outlook = win32.Dispatch('Outlook.Application')
                self.log_message("Neue Outlook-Instanz gestartet.")
            except Exception as e:
                self.log_message(f"Fehler: Konnte Outlook nicht starten oder verbinden: {e}")
                return

        try:
            mail = outlook.CreateItem(0)  # 0 = olMailItem
            
            # Formatiere das Datum für den E-Mail-Text
            date_formatted = mod_time.strftime("%d.%m.%Y")
            
            # Betreff der E-Mail
            mail.Subject = f"Neue Checkliste: {os.path.basename(file_path)}"
            
            # Textkörper der E-Mail mit der neuen Grußformel
            mail.Body = f"Sehr geehrter Herr Burghammer,\n\nim Anhang die Checkliste für den {date_formatted}.\n\nMit freundlichen Grüßen"

            # Setze den Empfänger der E-Mail
            mail.To = 'leitung.fb2@drk-koeln.de'
            
            # Datei als Anhang hinzufügen
            mail.Attachments.Add(file_path)
            
            # E-Mail zur Ansicht öffnen
            mail.Display(True) # True = Modal-Fenster, False = nicht-modal
            
            self.log_message(f"Outlook-E-Mail vorbereitet mit Anhang: '{file_path}'")
        
        except Exception as e:
            self.log_message(f"Fehler beim Erstellen der Outlook-E-Mail: {e}")


# Starte die Anwendung, wenn das Skript ausgeführt wird
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFMonitorApp(root)
    root.mainloop()
