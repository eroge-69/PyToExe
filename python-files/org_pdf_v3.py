import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import shutil
from PyPDF2 import PdfReader, PdfWriter
import threading


class PDFOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Organizer per Formato Foglio")
        self.root.geometry("700x650")
        
        # Variabili per i percorsi
        self.selected_path = tk.StringVar()
        self.destination_path = tk.StringVar()
        
        # Variabile per la ricerca ricorsiva
        self.search_subfolders = tk.BooleanVar(value=True)
        
        # Dizionario dei formati carta (in punti: 1 punto = 1/72 pollici)
        self.paper_formats = {
            'A0': (2384, 3370),
            'A1': (1684, 2384),
            'A2': (1191, 1684),
            'A3': (842, 1191),
            'A4': (595, 842),
            'A5': (420, 595)
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurazione della griglia
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        # Etichetta e campo per la selezione cartella sorgente
        ttk.Label(main_frame, text="Cartella sorgente (PDF da organizzare):").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        # Frame per il percorso sorgente e bottone
        source_frame = ttk.Frame(main_frame)
        source_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        source_frame.columnconfigure(0, weight=1)
        
        # Campo di testo per il percorso sorgente
        self.path_entry = ttk.Entry(source_frame, textvariable=self.selected_path, width=50)
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Bottone per selezionare cartella sorgente
        ttk.Button(source_frame, text="Sfoglia", command=self.select_source_folder).grid(
            row=0, column=1
        )
        
        # Etichetta e campo per la cartella di destinazione
        ttk.Label(main_frame, text="Cartella destinazione (dove creare le sottocartelle):").grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        # Frame per il percorso destinazione e bottone
        dest_frame = ttk.Frame(main_frame)
        dest_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        dest_frame.columnconfigure(0, weight=1)
        
        # Campo di testo per il percorso destinazione
        self.dest_entry = ttk.Entry(dest_frame, textvariable=self.destination_path, width=50)
        self.dest_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Bottone per selezionare cartella destinazione
        ttk.Button(dest_frame, text="Sfoglia", command=self.select_destination_folder).grid(
            row=0, column=1
        )
        
        # Checkbox per la ricerca nelle sottocartelle
        self.subfolder_check = ttk.Checkbutton(
            main_frame, 
            text="Cerca PDF anche nelle sottocartelle", 
            variable=self.search_subfolders
        )
        self.subfolder_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Frame per i bottoni delle operazioni
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Bottone per organizzare
        self.organize_button = ttk.Button(
            buttons_frame, 
            text="Organizza PDF", 
            command=self.start_organization
        )
        self.organize_button.grid(row=0, column=0, padx=(0, 10))
        
        # Bottone per unire
        self.merge_button = ttk.Button(
            buttons_frame, 
            text="Unisci PDF per Formato", 
            command=self.start_merging
        )
        self.merge_button.grid(row=0, column=1)
        
        # Area di testo per i log
        ttk.Label(main_frame, text="Log operazioni:").grid(
            row=6, column=0, sticky=(tk.W, tk.N), pady=(0, 5)
        )
        
        self.log_text = scrolledtext.ScrolledText(
            main_frame, 
            width=70, 
            height=12,
            state='disabled'
        )
        self.log_text.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Barra di progresso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Etichetta per lo status
        self.status_label = ttk.Label(main_frame, text="Pronto per iniziare", foreground="green")
        self.status_label.grid(row=9, column=0, columnspan=2, pady=(5, 0))
    
    def select_source_folder(self):
        """Apre il dialog per selezionare la cartella sorgente"""
        folder = filedialog.askdirectory(title="Seleziona la cartella contenente i PDF")
        if folder:
            self.selected_path.set(folder)
            # Se non è stata specificata una destinazione, usa la stessa cartella
            if not self.destination_path.get():
                self.destination_path.set(folder)
    
    def select_destination_folder(self):
        """Apre il dialog per selezionare la cartella di destinazione"""
        folder = filedialog.askdirectory(title="Seleziona dove creare le sottocartelle")
        if folder:
            self.destination_path.set(folder)
    
    def find_pdf_files(self, root_path):
        """Trova tutti i file PDF nella cartella e opzionalmente nelle sottocartelle"""
        pdf_files = []
        
        if self.search_subfolders.get():
            # Ricerca ricorsiva
            for root, dirs, files in os.walk(root_path):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        full_path = os.path.join(root, file)
                        # Calcola il percorso relativo per il log
                        rel_path = os.path.relpath(full_path, root_path)
                        pdf_files.append((full_path, rel_path, file))
        else:
            # Solo la cartella principale
            for file in os.listdir(root_path):
                full_path = os.path.join(root_path, file)
                if file.lower().endswith('.pdf') and os.path.isfile(full_path):
                    pdf_files.append((full_path, file, file))
        
        return pdf_files
    
    def log_message(self, message):
        """Aggiunge un messaggio al log"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update_idletasks()
    
    def get_pdf_page_size(self, pdf_path):
        """Rileva le dimensioni della prima pagina del PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                if len(pdf_reader.pages) == 0:
                    return None
                
                page = pdf_reader.pages[0]
                mediabox = page.mediabox
                
                # Dimensioni in punti
                width = float(mediabox.width)
                height = float(mediabox.height)
                
                return (width, height)
        except Exception as e:
            self.log_message(f"Errore nella lettura di {os.path.basename(pdf_path)}: {str(e)}")
            return None
    
    def identify_paper_format(self, dimensions):
        """Identifica il formato carta basato sulle dimensioni"""
        if not dimensions:
            return "Sconosciuto"
        
        width, height = dimensions
        
        # Normalizza le dimensioni (può essere in landscape o portrait)
        min_dim = min(width, height)
        max_dim = max(width, height)
        
        # Tolleranza per variazioni nelle dimensioni (5%)
        tolerance = 0.05
        
        for format_name, (format_width, format_height) in self.paper_formats.items():
            format_min = min(format_width, format_height)
            format_max = max(format_width, format_height)
            
            # Controlla se le dimensioni corrispondono con la tolleranza
            if (abs(min_dim - format_min) / format_min <= tolerance and
                abs(max_dim - format_max) / format_max <= tolerance):
                return format_name
        
        return "Sconosciuto"
    
    def organize_pdfs(self):
        """Organizza i PDF nella cartella selezionata"""
        source_path = self.selected_path.get().strip()
        dest_path = self.destination_path.get().strip()
        
        if not source_path:
            messagebox.showerror("Errore", "Seleziona prima la cartella sorgente!")
            return
        
        if not dest_path:
            messagebox.showerror("Errore", "Seleziona prima la cartella di destinazione!")
            return
        
        if not os.path.exists(source_path):
            messagebox.showerror("Errore", "La cartella sorgente non esiste!")
            return
        
        if not os.path.exists(dest_path):
            messagebox.showerror("Errore", "La cartella di destinazione non esiste!")
            return
        
        search_type = "ricorsiva (incluse sottocartelle)" if self.search_subfolders.get() else "solo cartella principale"
        self.log_message(f"Inizio organizzazione - Ricerca: {search_type}")
        self.log_message(f"Sorgente: {source_path}")
        self.log_message(f"Destinazione: {dest_path}")
        self.log_message("-" * 50)
        
        # Trova tutti i file PDF
        pdf_files = self.find_pdf_files(source_path)
        
        if not pdf_files:
            self.log_message("Nessun file PDF trovato nella cartella selezionata.")
            self.status_label.config(text="ℹ Nessun file PDF trovato nella cartella", foreground="orange")
            return
        
        self.log_message(f"Trovati {len(pdf_files)} file PDF")
        
        # Conta i file per formato
        format_counts = {}
        processed = 0
        errors = 0
        
        for pdf_full_path, pdf_rel_path, pdf_filename in pdf_files:
            # Rileva le dimensioni del PDF
            dimensions = self.get_pdf_page_size(pdf_full_path)
            paper_format = self.identify_paper_format(dimensions)
            
            # Crea la sottocartella se non esiste nella destinazione
            subfolder_name = f"Formato_{paper_format}"
            subfolder_path = os.path.join(dest_path, subfolder_name)
            
            try:
                os.makedirs(subfolder_path, exist_ok=True)
                
                # Copia il file
                destination = os.path.join(subfolder_path, pdf_filename)
                
                # Se il file di destinazione esiste già, aggiungi un numero
                counter = 1
                original_destination = destination
                while os.path.exists(destination):
                    name, ext = os.path.splitext(pdf_filename)
                    new_name = f"{name}_{counter}{ext}"
                    destination = os.path.join(subfolder_path, new_name)
                    counter += 1
                
                shutil.copy2(pdf_full_path, destination)
                
                # Mostra il percorso relativo nel log se diverso dal nome file
                display_path = pdf_rel_path if pdf_rel_path != pdf_filename else pdf_filename
                self.log_message(f"✓ {display_path} → {subfolder_name} ({paper_format}) [COPIATO]")
                
                # Conta per statistiche
                format_counts[paper_format] = format_counts.get(paper_format, 0) + 1
                processed += 1
                
            except Exception as e:
                display_path = pdf_rel_path if pdf_rel_path != pdf_filename else pdf_filename
                self.log_message(f"✗ Errore copiando {display_path}: {str(e)}")
                errors += 1
        
        # Statistiche finali
        self.log_message("-" * 50)
        self.log_message("RIEPILOGO:")
        self.log_message(f"File elaborati: {processed}")
        self.log_message(f"Errori: {errors}")
        self.log_message("\nDistribuzione per formato:")
        for format_name, count in format_counts.items():
            self.log_message(f"  {format_name}: {count} file")
        
        # Aggiorna lo status invece del popup
        if errors == 0:
            status_text = f"✓ Organizzazione completata! File elaborati: {processed}"
            status_color = "green"
        else:
            status_text = f"⚠ Organizzazione completata con errori. File elaborati: {processed}, Errori: {errors}"
            status_color = "orange"
            
        self.status_label.config(text=status_text, foreground=status_color)
    
    def merge_pdfs_by_format(self):
        """Unisce tutti i PDF dello stesso formato in un unico file"""
        dest_path = self.destination_path.get().strip()
        
        if not dest_path:
            messagebox.showerror("Errore", "Seleziona prima la cartella di destinazione!")
            return
        
        if not os.path.exists(dest_path):
            messagebox.showerror("Errore", "La cartella di destinazione non esiste!")
            return
        
        self.log_message(f"Inizio unione PDF nella cartella: {dest_path}")
        self.log_message("-" * 50)
        
        # Trova tutte le sottocartelle di formato
        format_folders = [d for d in os.listdir(dest_path) 
                         if os.path.isdir(os.path.join(dest_path, d)) and d.startswith('Formato_')]
        
        if not format_folders:
            self.log_message("Nessuna cartella di formato trovata. Esegui prima l'organizzazione.")
            self.status_label.config(text="ℹ Nessuna cartella di formato trovata", foreground="orange")
            return
        
        self.log_message(f"Trovate {len(format_folders)} cartelle di formato")
        
        merged_count = 0
        total_files = 0
        
        for folder_name in format_folders:
            folder_full_path = os.path.join(dest_path, folder_name)
            
            # Trova tutti i PDF nella sottocartella
            pdf_files = [f for f in os.listdir(folder_full_path) 
                        if f.lower().endswith('.pdf') and 
                        os.path.isfile(os.path.join(folder_full_path, f)) and
                        not f.startswith('0000_')]  # Esclude i file già uniti
            
            if not pdf_files:
                self.log_message(f"Nessun PDF da unire in {folder_name}")
                continue
            
            if len(pdf_files) == 1:
                self.log_message(f"Solo un PDF in {folder_name}, unione non necessaria")
                continue
            
            # Ordina i file alfabeticamente
            pdf_files.sort()
            
            self.log_message(f"Unione di {len(pdf_files)} PDF in {folder_name}:")
            
            try:
                # Crea il writer per il PDF unito
                pdf_writer = PdfWriter()
                
                # Aggiungi tutte le pagine di tutti i PDF
                for pdf_file in pdf_files:
                    pdf_path = os.path.join(folder_full_path, pdf_file)
                    self.log_message(f"  - Aggiungendo {pdf_file}")
                    
                    try:
                        with open(pdf_path, 'rb') as file:
                            pdf_reader = PdfReader(file)
                            for page in pdf_reader.pages:
                                pdf_writer.add_page(page)
                    except Exception as e:
                        self.log_message(f"    ✗ Errore leggendo {pdf_file}: {str(e)}")
                        continue
                
                # Estrai il formato dal nome della cartella
                format_type = folder_name.replace('Formato_', '')
                output_filename = f"0000_Formato_{format_type}.pdf"
                output_path = os.path.join(folder_full_path, output_filename)
                
                # Salva il PDF unito
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                
                self.log_message(f"✓ Creato: {output_filename} ({len(pdf_files)} file uniti)")
                merged_count += 1
                total_files += len(pdf_files)
                
            except Exception as e:
                self.log_message(f"✗ Errore nell'unione per {folder_name}: {str(e)}")
        
        # Statistiche finali
        self.log_message("-" * 50)
        self.log_message("RIEPILOGO UNIONE:")
        self.log_message(f"Formati elaborati: {merged_count}")
        self.log_message(f"File totali uniti: {total_files}")
        
        # Aggiorna lo status invece del popup
        if merged_count > 0:
            status_text = f"✓ Unione completata! Formati elaborati: {merged_count}, File uniti: {total_files}"
            status_color = "green"
        else:
            status_text = "ℹ Nessuna unione necessaria o possibile"
            status_color = "blue"
            
        self.status_label.config(text=status_text, foreground=status_color)
    
    def start_organization(self):
        """Avvia l'organizzazione in un thread separato"""
        self.organize_button.config(state='disabled')
        self.merge_button.config(state='disabled')
        self.status_label.config(text="🔄 Organizzazione in corso...", foreground="blue")
        self.progress.start()
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
        # Esegui in thread separato per non bloccare l'interfaccia
        thread = threading.Thread(target=self.run_organization)
        thread.daemon = True
        thread.start()
    
    def run_organization(self):
        """Esegue l'organizzazione e ripristina l'interfaccia"""
        try:
            self.organize_pdfs()
        finally:
            self.root.after(0, self.finish_operation)
    
    def start_merging(self):
        """Avvia l'unione in un thread separato"""
        self.organize_button.config(state='disabled')
        self.merge_button.config(state='disabled')
        self.status_label.config(text="🔄 Unione PDF in corso...", foreground="blue")
        self.progress.start()
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
        # Esegui in thread separato per non bloccare l'interfaccia
        thread = threading.Thread(target=self.run_merging)
        thread.daemon = True
        thread.start()
    
    def run_merging(self):
        """Esegue l'unione e ripristina l'interfaccia"""
        try:
            self.merge_pdfs_by_format()
        finally:
            self.root.after(0, self.finish_operation)
    
    def finish_operation(self):
        """Ripristina l'interfaccia dopo qualsiasi operazione"""
        self.progress.stop()
        self.organize_button.config(state='normal')
        self.merge_button.config(state='normal')


def main():
    root = tk.Tk()
    app = PDFOrganizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
