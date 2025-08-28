import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import datetime
import os
import sys

class DateChangerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Date Changer")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Variabili
        self.is_running = False
        self.original_date = None
        
        # Stile
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principale
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titolo
        title_label = ttk.Label(main_frame, text="Date Changer", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Data da impostare
        ttk.Label(main_frame, text="Nuova data:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar(value="03/08/2025")
        date_entry = ttk.Entry(main_frame, textvariable=self.date_var, width=15)
        date_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Tempo di attesa
        ttk.Label(main_frame, text="Tempo (secondi):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.time_var = tk.StringVar(value="5")
        time_entry = ttk.Entry(main_frame, textvariable=self.time_var, width=15)
        time_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Percorso applicazione
        ttk.Label(main_frame, text="Percorso app:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.app_path_var = tk.StringVar(value="C:\\Users\\Utente\\AppData\\Local\\Programs\\Typora\\Typora.exe")
        app_entry = ttk.Entry(main_frame, textvariable=self.app_path_var, width=40)
        app_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Checkbox per aprire l'app
        self.open_app_var = tk.BooleanVar(value=True)
        app_checkbox = ttk.Checkbutton(main_frame, text="Apri applicazione dopo aver cambiato la data", 
                                      variable=self.open_app_var)
        app_checkbox.grid(row=4, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        # Frame per i pulsanti
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        # Pulsante Start/Stop
        self.start_button = ttk.Button(button_frame, text="START", 
                                      command=self.toggle_operation, width=12)
        self.start_button.grid(row=0, column=0, padx=5)
        
        # Pulsante per ripristinare data manualmente
        self.restore_button = ttk.Button(button_frame, text="Ripristina Data", 
                                       command=self.restore_date_manually, 
                                       width=12, state='disabled')
        self.restore_button.grid(row=0, column=1, padx=5)
        
        # Area di stato
        self.status_var = tk.StringVar(value="Pronto")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                               font=('Arial', 10), foreground='blue')
        status_label.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Countdown label
        self.countdown_var = tk.StringVar(value="")
        countdown_label = ttk.Label(main_frame, textvariable=self.countdown_var, 
                                  font=('Arial', 12, 'bold'), foreground='red')
        countdown_label.grid(row=7, column=0, columnspan=2, pady=5)
        
        # Configurazione della griglia
        main_frame.columnconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
    
    def get_current_date(self):
        """Ottiene la data corrente del sistema"""
        try:
            result = subprocess.run(['date', '/t'], capture_output=True, text=True, shell=True)
            return result.stdout.strip()
        except:
            return None
    
    def change_date(self, new_date):
        """Cambia la data del sistema"""
        try:
            # Comando per cambiare la data (richiede privilegi di amministratore)
            subprocess.run(['date', new_date], shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def open_application(self):
        """Apre l'applicazione specificata"""
        try:
            app_path = self.app_path_var.get().strip()
            if app_path and os.path.exists(app_path):
                subprocess.Popen([app_path], shell=True)
                return True
            else:
                messagebox.showwarning("Attenzione", "Il percorso dell'applicazione non esiste!")
                return False
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile aprire l'applicazione: {str(e)}")
            return False
    
    def countdown_timer(self, seconds):
        """Timer con countdown visibile"""
        for i in range(seconds, 0, -1):
            if not self.is_running:  # Se l'operazione è stata fermata
                break
            self.countdown_var.set(f"Ripristino tra: {i} secondi")
            time.sleep(1)
        
        if self.is_running:
            self.countdown_var.set("")
    
    def operation_thread(self):
        """Thread principale per l'operazione"""
        try:
            # Salva la data originale
            self.original_date = self.get_current_date()
            
            # Cambia la data
            new_date = self.date_var.get().strip()
            self.status_var.set("Cambiando data...")
            
            if not self.change_date(new_date):
                messagebox.showerror("Errore", 
                    "Impossibile cambiare la data. Assicurati di eseguire il programma come amministratore!")
                self.reset_ui()
                return
            
            self.status_var.set(f"Data cambiata in: {new_date}")
            
            # Apri l'applicazione se richiesto
            if self.open_app_var.get():
                self.status_var.set("Aprendo applicazione...")
                self.open_application()
            
            # Attendi il tempo specificato con countdown
            wait_time = int(self.time_var.get())
            self.status_var.set("In attesa...")
            self.countdown_timer(wait_time)
            
            # Ripristina la data originale
            if self.is_running and self.original_date:
                self.status_var.set("Ripristinando data originale...")
                if self.change_date(self.original_date):
                    self.status_var.set("Data ripristinata con successo!")
                else:
                    self.status_var.set("Errore nel ripristino della data!")
                    messagebox.showerror("Errore", "Impossibile ripristinare la data originale!")
            
        except ValueError:
            messagebox.showerror("Errore", "Inserire un numero valido per i secondi!")
        except Exception as e:
            messagebox.showerror("Errore", f"Si è verificato un errore: {str(e)}")
        finally:
            self.reset_ui()
    
    def toggle_operation(self):
        """Avvia o ferma l'operazione"""
        if not self.is_running:
            # Validazione input
            try:
                int(self.time_var.get())
            except ValueError:
                messagebox.showerror("Errore", "Inserire un numero valido per i secondi!")
                return
            
            if not self.date_var.get().strip():
                messagebox.showerror("Errore", "Inserire una data valida!")
                return
            
            # Avvia l'operazione
            self.is_running = True
            self.start_button.config(text="STOP", style='Accent.TButton')
            self.restore_button.config(state='normal')
            
            # Avvia il thread
            self.thread = threading.Thread(target=self.operation_thread)
            self.thread.daemon = True
            self.thread.start()
            
        else:
            # Ferma l'operazione
            self.is_running = False
            self.status_var.set("Operazione fermata dall'utente")
            self.countdown_var.set("")
    
    def restore_date_manually(self):
        """Ripristina manualmente la data originale"""
        if self.original_date:
            if self.change_date(self.original_date):
                self.status_var.set("Data ripristinata manualmente!")
                messagebox.showinfo("Successo", "Data ripristinata con successo!")
            else:
                messagebox.showerror("Errore", "Impossibile ripristinare la data!")
        else:
            messagebox.showwarning("Attenzione", "Nessuna data originale salvata!")
    
    def reset_ui(self):
        """Ripristina l'interfaccia utente"""
        self.is_running = False
        self.start_button.config(text="START", style='TButton')
        self.restore_button.config(state='disabled')
        self.countdown_var.set("")
        if not self.status_var.get().startswith("Data ripristinata"):
            self.status_var.set("Pronto")

def main():
    # Controlla se il programma è eseguito come amministratore
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            messagebox.showwarning("Attenzione", 
                "Per modificare la data di sistema, è necessario eseguire il programma come amministratore!\n\n" +
                "Clicca con il tasto destro sul file Python e seleziona 'Esegui come amministratore'.")
    except:
        pass
    
    root = tk.Tk()
    app = DateChangerGUI(root)
    
    # Gestione chiusura finestra
    def on_closing():
        if app.is_running:
            if messagebox.askokcancel("Uscita", "Un'operazione è in corso. Vuoi davvero uscire?"):
                app.is_running = False
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()