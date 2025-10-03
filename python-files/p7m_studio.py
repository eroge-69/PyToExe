import os
import subprocess
import zipfile
import shutil
import tkinter as tk
import base64
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

class P7MExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Estrazione File XML da P7M e ZIP")
        self.root.geometry("700x550")
        
        # Cartelle di destinazione
        self.importami_path = r"C:\Importami"
        self.errori_path = os.path.join(self.importami_path, "Errori")
        
        # Crea le cartelle se non esistono
        os.makedirs(self.importami_path, exist_ok=True)
        os.makedirs(self.errori_path, exist_ok=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titolo
        title_label = ttk.Label(main_frame, text="Estrazione File da Archivi ZIP", 
                               font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Pulsanti per caricare ZIP
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        self.btn_carica_zip_singolo = ttk.Button(btn_frame, text="Carica File ZIP Singolo", 
                                                command=self.carica_zip_singolo)
        self.btn_carica_zip_singolo.grid(row=0, column=0, padx=(0, 10))
        
        self.btn_carica_zip_multipli = ttk.Button(btn_frame, text="Carica File ZIP Multipli", 
                                                 command=self.carica_zip_multipli)
        self.btn_carica_zip_multipli.grid(row=0, column=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Etichetta stato
        self.lbl_stato = ttk.Label(main_frame, text="Pronto")
        self.lbl_stato.grid(row=3, column=0, columnspan=2)
        
        # Area di testo per il log
        self.text_log = tk.Text(main_frame, height=20, width=80)
        self.text_log.grid(row=4, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar per l'area di testo
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.text_log.yview)
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
        self.text_log.configure(yscrollcommand=scrollbar.set)
        
        # Frame per le statistiche
        stats_frame = ttk.LabelFrame(main_frame, text="Riepilogo", padding="5")
        stats_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Etichette per le statistiche
        self.lbl_zip_elaborati = ttk.Label(stats_frame, text="ZIP elaborati: 0/0")
        self.lbl_zip_elaborati.grid(row=0, column=0, padx=5, sticky=tk.W)
        
        self.lbl_totali = ttk.Label(stats_frame, text="File totali: 0")
        self.lbl_totali.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        self.lbl_elaborati = ttk.Label(stats_frame, text="File elaborati: 0")
        self.lbl_elaborati.grid(row=1, column=0, padx=5, sticky=tk.W)
        
        self.lbl_errori = ttk.Label(stats_frame, text="File con errori: 0")
        self.lbl_errori.grid(row=1, column=1, padx=5, sticky=tk.W)
        
        self.lbl_ignorati = ttk.Label(stats_frame, text="File ignorati: 0")
        self.lbl_ignorati.grid(row=1, column=2, padx=5, sticky=tk.W)
        
        # Pulsanti azioni
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=6, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        self.btn_pulisci = ttk.Button(actions_frame, text="Pulisci Log", 
                                     command=self.pulisci_log)
        self.btn_pulisci.grid(row=0, column=0, padx=(0, 10))
        
        self.btn_apri_cartella = ttk.Button(actions_frame, text="Apri Cartella Importami", 
                                           command=self.apri_cartella_importami)
        self.btn_apri_cartella.grid(row=0, column=1)
        
        # Configurazione del grid per il ridimensionamento
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Inizializza statistiche
        self.reset_statistiche()
        
    def reset_statistiche(self):
        """Resetta le statistiche"""
        self.file_totali = 0
        self.file_elaborati = 0
        self.file_errori = 0
        self.file_ignorati = 0
        self.zip_totali = 0
        self.zip_elaborati = 0
        self.aggiorna_statistiche()
        
    def log(self, messaggio):
        """Aggiunge un messaggio al log"""
        self.text_log.insert(tk.END, messaggio + "\n")
        self.text_log.see(tk.END)
        self.root.update_idletasks()
        
    def pulisci_log(self):
        """Pulisce l'area di testo del log"""
        self.text_log.delete(1.0, tk.END)
        
    def aggiorna_statistiche(self):
        """Aggiorna le statistiche nell'interfaccia"""
        self.lbl_zip_elaborati.config(text=f"ZIP elaborati: {self.zip_elaborati}/{self.zip_totali}")
        self.lbl_totali.config(text=f"File totali: {self.file_totali}")
        self.lbl_elaborati.config(text=f"File elaborati: {self.file_elaborati}")
        self.lbl_errori.config(text=f"File con errori: {self.file_errori}")
        self.lbl_ignorati.config(text=f"File ignorati: {self.file_ignorati}")
        
    def aggiorna_progresso(self, valore=None, massimo=None):
        """Aggiorna la progress bar"""
        if massimo is not None:
            self.progress['maximum'] = massimo
        if valore is not None:
            self.progress['value'] = valore
        self.root.update_idletasks()
        
    def aggiorna_stato(self, messaggio):
        """Aggiorna l'etichetta di stato"""
        self.lbl_stato.config(text=messaggio)
        self.root.update_idletasks()
        
    def carica_zip_singolo(self):
        """Carica un singolo file ZIP"""
        file_path = filedialog.askopenfilename(
            title="Seleziona file ZIP",
            filetypes=[("File ZIP", "*.zip"), ("Tutti i file", "*.*")]
        )
        
        if file_path:
            self.elabora_zip_multipli([file_path])
        
    def carica_zip_multipli(self):
        """Carica più file ZIP contemporaneamente"""
        file_paths = filedialog.askopenfilenames(
            title="Seleziona file ZIP",
            filetypes=[("File ZIP", "*.zip"), ("Tutti i file", "*.*")]
        )
        
        if file_paths:
            self.elabora_zip_multipli(file_paths)
            
    def elabora_zip_multipli(self, zip_paths):
        """Elabora più file ZIP"""
        self.reset_statistiche()
        self.zip_totali = len(zip_paths)
        self.aggiorna_statistiche()
        self.aggiorna_progresso(0, self.zip_totali)
        
        self.log(f"Inizio elaborazione di {self.zip_totali} file ZIP")
        self.log("=" * 60)
        
        try:
            for i, zip_path in enumerate(zip_paths, 1):
                nome_zip = os.path.basename(zip_path)
                self.aggiorna_stato(f"Elaborando: {nome_zip}")
                self.aggiorna_progresso(i)
                
                self.log(f"\n[{i}/{self.zip_totali}] Elaborazione: {nome_zip}")
                self.log("-" * 40)
                
                successo = self.elabora_zip_singolo(zip_path)
                
                if successo:
                    self.zip_elaborati += 1
                    self.aggiorna_statistiche()
                else:
                    self.log(f"ERRORE nell'elaborazione di {nome_zip}")
            
            self.log("=" * 60)
            self.log("Elaborazione completata!")
            self.aggiorna_stato("Completato")
            
            # Mostra riepilogo finale
            messagebox.showinfo("Completato", 
                              f"Elaborazione terminata!\n\n"
                              f"ZIP elaborati: {self.zip_elaborati}/{self.zip_totali}\n"
                              f"File totali: {self.file_totali}\n"
                              f"File elaborati: {self.file_elaborati}\n"
                              f"File con errori: {self.file_errori}\n"
                              f"File ignorati (metaDato): {self.file_ignorati}")
                              
        except Exception as e:
            self.log(f"ERRORE durante l'elaborazione: {str(e)}")
            messagebox.showerror("Errore", f"Si è verificato un errore: {str(e)}")
            self.aggiorna_stato("Errore")
            
    def elabora_zip_singolo(self, zip_path):
        """Elabora un singolo file ZIP"""
        # Cartella temporanea per l'estrazione
        temp_dir = os.path.join(os.path.dirname(zip_path), f"temp_extract_{os.path.basename(zip_path)}")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Estrai tutto dallo ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                
            # Elabora i file estratti
            self.elabora_cartella(temp_dir)
            return True
            
        except Exception as e:
            self.log(f"ERRORE nell'estrazione ZIP: {str(e)}")
            return False
            
        finally:
            # Pulisci la cartella temporanea
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                self.log(f"Avviso: impossibile pulire cartella temporanea: {str(e)}")
            
    def elabora_cartella(self, cartella):
        """Elabora i file in una cartella"""
        for item in os.listdir(cartella):
            item_path = os.path.join(cartella, item)
            
            # Se è una cartella, elabora ricorsivamente
            if os.path.isdir(item_path):
                self.elabora_cartella(item_path)
                continue
                
            # Ignora i file "metaDato" - NON vengono spostati da nessuna parte
            if "metadato" in item.lower():
                self.file_ignorati += 1
                self.file_totali += 1
                self.aggiorna_statistiche()
                self.log(f"IGNORATO (metaDato): {item}")
                continue
                
            self.file_totali += 1
            self.aggiorna_statistiche()
            
            # Gestisci i file in base all'estensione
            if item.lower().endswith('.xml'):
                self.gestisci_xml(item_path, item)
            elif item.lower().endswith('.p7m'):
                self.gestisci_p7m(item_path, item)
            else:
                self.log(f"Tipo file non supportato: {item}")
                self.sposta_file_errore(item_path, item, "Tipo file non supportato")
                
    def gestisci_xml(self, file_path, nome_file):
        """Gestisce i file XML spostandoli in Importami"""
        try:
            dest_path = os.path.join(self.importami_path, nome_file)
            
            # Gestisci eventuali duplicati
            counter = 1
            base_name = Path(nome_file).stem
            extension = Path(nome_file).suffix
            
            while os.path.exists(dest_path):
                new_name = f"{base_name}_{counter}{extension}"
                dest_path = os.path.join(self.importami_path, new_name)
                counter += 1
                
            shutil.copy2(file_path, dest_path)
            self.file_elaborati += 1
            self.aggiorna_statistiche()
            self.log(f"XML spostato: {nome_file} → {os.path.basename(dest_path)}")
            
        except Exception as e:
            self.file_errori += 1
            self.aggiorna_statistiche()
            self.log(f"ERRORE XML {nome_file}: {str(e)}")
            self.sposta_file_errore(file_path, nome_file, str(e))
            
    def gestisci_p7m(self, file_path, nome_file):
        """Gestisce i file P7M decodificandoli"""
        try:
            # Nome per il file XML risultante
            nome_xml = nome_file[:-4] + ".xml"  # Rimuove .p7m e aggiunge .xml
            xml_temp_path = os.path.join(os.path.dirname(file_path), nome_xml)
            
            # Decodifica il file P7M
            if self.estrai_xml_da_p7m_completo(file_path, xml_temp_path):
                # Sposta il file XML risultante
                self.gestisci_xml(xml_temp_path, nome_xml)
            else:
                raise Exception("Estrazione P7M fallita con tutti i metodi")
                
        except Exception as e:
            self.file_errori += 1
            self.aggiorna_statistiche()
            self.log(f"ERRORE P7M {nome_file}: {str(e)}")
            self.sposta_file_errore(file_path, nome_file, str(e))
    
    def estrai_xml_da_p7m_completo(self, path_p7m, path_xml_out):
        """Estrae XML da file P7M con tutti i metodi possibili"""
        
        # METODO 1: Verifica se è in base64 e decodifica
        if self.estrai_da_base64(path_p7m, path_xml_out):
            self.log("  ✓ Successo con decodifica Base64")
            return True
        
        # METODO 2: OpenSSL standard
        comandi_openssl = [
            {"nome": "SMIME DER", "cmd": ["openssl", "smime", "-verify", "-noverify", "-in", path_p7m, "-inform", "DER", "-out", path_xml_out]},
            {"nome": "SMIME PEM", "cmd": ["openssl", "smime", "-verify", "-noverify", "-in", path_p7m, "-inform", "PEM", "-out", path_xml_out]},
            {"nome": "SMIME automatico", "cmd": ["openssl", "smime", "-verify", "-noverify", "-in", path_p7m, "-out", path_xml_out]},
        ]
        
        for formato in comandi_openssl:
            try:
                self.log(f"  Tentativo OpenSSL: {formato['nome']}")
                result = subprocess.run(
                    formato['cmd'], 
                    capture_output=True, 
                    text=True, 
                    timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode == 0 and self.verifica_file_xml_valido(path_xml_out):
                    self.log(f"  ✓ Successo con {formato['nome']}")
                    return True
                else:
                    self.log(f"  ✗ Fallito")
            except:
                self.log(f"  ✗ Errore")
            self.pulisci_file_temp(path_xml_out)
        
        # METODO 3: Estrazione manuale dal contenuto
        if self.estrai_xml_manuale(path_p7m, path_xml_out):
            self.log("  ✓ Successo con estrazione manuale")
            return True
        
        return False
    
    def estrai_da_base64(self, path_p7m, path_xml_out):
        """Tenta di decodificare il file come base64"""
        try:
            with open(path_p7m, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Verifica se sembra base64 (caratteri base64, lunghezza multipla di 4)
            if (len(content) % 4 == 0 and 
                all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=" for c in content)):
                
                self.log("  Rilevato formato Base64, tentativo decodifica...")
                
                # Prova a decodificare
                decoded_bytes = base64.b64decode(content)
                
                # Verifica se il contenuto decodificato è XML
                try:
                    decoded_text = decoded_bytes.decode('utf-8')
                    if '<?xml' in decoded_text or '<FatturaElettronica' in decoded_text:
                        with open(path_xml_out, 'w', encoding='utf-8') as f_out:
                            f_out.write(decoded_text)
                        return True
                except:
                    pass
                
                # Se la decodifica UTF-8 fallisce, prova a salvare come binario e verificare
                with open(path_xml_out, 'wb') as f_out:
                    f_out.write(decoded_bytes)
                
                if self.verifica_file_xml_valido(path_xml_out):
                    return True
            
            return False
            
        except Exception as e:
            self.log(f"  ✗ Errore decodifica Base64: {str(e)}")
            return False
    
    def estrai_xml_manuale(self, path_p7m, path_xml_out):
        """Tenta di estrarre XML manualmente analizzando il file"""
        try:
            # Prova come testo
            with open(path_p7m, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Cerca direttamente l'XML nel file
            xml_start = content.find('<?xml')
            if xml_start == -1:
                xml_start = content.find('<FatturaElettronica')
            
            if xml_start != -1:
                # Trovato inizio XML, cerca la fine
                xml_end = content.find('</FatturaElettronica>', xml_start)
                if xml_end != -1:
                    xml_end += len('</FatturaElettronica>')
                    xml_content = content[xml_start:xml_end]
                    
                    with open(path_xml_out, 'w', encoding='utf-8') as f_out:
                        f_out.write(xml_content)
                    
                    if self.verifica_file_xml_valido(path_xml_out):
                        return True
            
            # Se non trova come testo, prova come binario
            with open(path_p7m, 'rb') as f:
                binary_content = f.read()
            
            # Cerca pattern XML in binario
            xml_patterns = [b'<?xml', b'<FatturaElettronica']
            for pattern in xml_patterns:
                start_idx = binary_content.find(pattern)
                if start_idx != -1:
                    # Cerca la fine
                    end_pattern = b'</FatturaElettronica>'
                    end_idx = binary_content.find(end_pattern, start_idx)
                    if end_idx != -1:
                        end_idx += len(end_pattern)
                        xml_binary = binary_content[start_idx:end_idx]
                        
                        with open(path_xml_out, 'wb') as f_out:
                            f_out.write(xml_binary)
                        
                        if self.verifica_file_xml_valido(path_xml_out):
                            return True
            
            return False
            
        except Exception as e:
            self.log(f"  ✗ Estrazione manuale fallita: {str(e)}")
            return False
    
    def verifica_file_xml_valido(self, file_path):
        """Verifica se il file XML estratto è valido"""
        try:
            if not os.path.exists(file_path):
                return False
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return False
            
            # Leggi le prime righe per verificare che sia XML
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_lines = f.read(1000)
            
            # Verifica che contenga tag XML delle fatture elettroniche
            if '<?xml' in first_lines or '<FatturaElettronica' in first_lines:
                return True
            
            return False
            
        except:
            return False
    
    def pulisci_file_temp(self, file_path):
        """Pulisce un file temporaneo"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
            
    def sposta_file_errore(self, file_path, nome_file, motivo):
        """Sposta un file problematico nella cartella errori"""
        try:
            # Assicurati che la cartella errori esista
            os.makedirs(self.errori_path, exist_ok=True)
            
            dest_path = os.path.join(self.errori_path, nome_file)
            
            # Gestisci eventuali duplicati
            counter = 1
            base_name = Path(nome_file).stem
            extension = Path(nome_file).suffix
            
            while os.path.exists(dest_path):
                new_name = f"{base_name}_{counter}{extension}"
                dest_path = os.path.join(self.errori_path, new_name)
                counter += 1
                
            shutil.copy2(file_path, dest_path)
            self.log(f"File errore spostato: {nome_file} → {os.path.basename(dest_path)}")
            self.log(f"  Motivo: {motivo}")
            
        except Exception as e:
            self.log(f"ERRORE CRITICO durante lo spostamento in errori: {str(e)}")
            
    def apri_cartella_importami(self):
        """Apre la cartella Importami nell'esplora file"""
        try:
            if os.path.exists(self.importami_path):
                os.startfile(self.importami_path)
            else:
                messagebox.showwarning("Attenzione", f"La cartella {self.importami_path} non esiste.")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile aprire la cartella: {str(e)}")

def main():
    root = tk.Tk()
    app = P7MExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()