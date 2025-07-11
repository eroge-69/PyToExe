import os
import shutil
from tkinter import *
from tkinter import filedialog, messagebox, ttk
import threading
from datetime import datetime

class BackupTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Festplatten Backup Tool")
        self.root.geometry("600x400")
        
        # Variablen
        self.source_path = StringVar()
        self.dest_path = StringVar()
        self.progress_var = DoubleVar()
        
        self.create_interface()
    
    def create_interface(self):
        # Titel
        Label(self.root, text="Festplatten Backup Tool", 
              font=("Arial", 16, "bold")).pack(pady=10)
        
        # Quellordner
        Frame1 = Frame(self.root)
        Frame1.pack(fill=X, padx=20, pady=5)
        Label(Frame1, text="Quelle:", width=10).pack(side=LEFT)
        Entry(Frame1, textvariable=self.source_path, width=50).pack(side=LEFT, padx=5)
        Button(Frame1, text="Durchsuchen", 
               command=self.select_source).pack(side=RIGHT)
        
        # Zielordner
        Frame2 = Frame(self.root)
        Frame2.pack(fill=X, padx=20, pady=5)
        Label(Frame2, text="Ziel:", width=10).pack(side=LEFT)
        Entry(Frame2, textvariable=self.dest_path, width=50).pack(side=LEFT, padx=5)
        Button(Frame2, text="Durchsuchen", 
               command=self.select_dest).pack(side=RIGHT)
        
        # Optionen
        self.sync_mode = BooleanVar()
        Checkbutton(self.root, text="Synchronisation (löscht Dateien im Ziel, die in der Quelle nicht existieren)", 
                   variable=self.sync_mode).pack(pady=10)
        
        # Buttons
        Button(self.root, text="Backup starten", bg="green", fg="white",
               font=("Arial", 12, "bold"), command=self.start_backup).pack(pady=20)
        
        # Progress Bar
        self.progress = ttk.Progressbar(self.root, variable=self.progress_var, 
                                       maximum=100)
        self.progress.pack(fill=X, padx=20, pady=10)
        
        # Status
        self.status_label = Label(self.root, text="Bereit für Backup", 
                                 fg="blue")
        self.status_label.pack()
        
        # Log
        self.log_text = Text(self.root, height=8, width=70)
        self.log_text.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = Scrollbar(self.root)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
    
    def select_source(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_path.set(folder)
    
    def select_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dest_path.set(folder)
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(END, f"[{timestamp}] {message}\n")
        self.log_text.see(END)
        self.root.update()
    
    def start_backup(self):
        if not self.source_path.get() or not self.dest_path.get():
            messagebox.showerror("Fehler", "Bitte wählen Sie Quell- und Zielordner aus!")
            return
        
        # Backup in separatem Thread starten
        thread = threading.Thread(target=self.backup_files)
        thread.daemon = True
        thread.start()
    
    def backup_files(self):
        try:
            source = self.source_path.get()
            destination = self.dest_path.get()
            
            self.status_label.config(text="Backup läuft...", fg="orange")
            self.log_message("Backup gestartet")
            self.log_message(f"Quelle: {source}")
            self.log_message(f"Ziel: {destination}")
            
            # Dateien zählen
            total_files = sum([len(files) for r, d, files in os.walk(source)])
            self.log_message(f"Gefunden: {total_files} Dateien")
            
            copied_files = 0
            
            for root, dirs, files in os.walk(source):
                for file in files:
                    try:
                        # Pfade erstellen
                        src_file = os.path.join(root, file)
                        rel_path = os.path.relpath(src_file, source)
                        dest_file = os.path.join(destination, rel_path)
                        dest_dir = os.path.dirname(dest_file)
                        
                        # Zielordner erstellen
                        if not os.path.exists(dest_dir):
                            os.makedirs(dest_dir)
                        
                        # Datei kopieren (nur wenn neuer oder nicht vorhanden)
                        if not os.path.exists(dest_file) or \
                           os.path.getmtime(src_file) > os.path.getmtime(dest_file):
                            shutil.copy2(src_file, dest_file)
                            self.log_message(f"Kopiert: {rel_path}")
                        
                        copied_files += 1
                        progress = (copied_files / total_files) * 100
                        self.progress_var.set(progress)
                        
                    except Exception as e:
                        self.log_message(f"Fehler bei {file}: {str(e)}")
            
            self.status_label.config(text="Backup erfolgreich abgeschlossen!", fg="green")
            self.log_message("Backup abgeschlossen!")
            messagebox.showinfo("Erfolg", "Backup wurde erfolgreich abgeschlossen!")
            
        except Exception as e:
            self.status_label.config(text="Backup fehlgeschlagen!", fg="red")
            self.log_message(f"Fehler: {str(e)}")
            messagebox.showerror("Fehler", f"Backup fehlgeschlagen: {str(e)}")

if __name__ == "__main__":
    root = Tk()
    app = BackupTool(root)
    root.mainloop()