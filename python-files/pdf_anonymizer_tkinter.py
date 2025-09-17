#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Anonymizer - Versione Semplificata con Tkinter
Interfaccia grafica nativa Python senza dipendenze esterne
Compatibile con compilatori online che supportano Tkinter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import os


class ReplacementManager:
    """Gestisce la mappatura delle sostituzioni per garantire coerenza"""

    def __init__(self):
        self.mapping: Dict[str, str] = {}
        self.entity_counters: Dict[str, int] = {
            'PERSON': 0, 'ORG': 0, 'LOC': 0, 'EMAIL': 0, 'PHONE': 0
        }

        # Nomi di fantasia italiani
        self.fantasy_names = [
            "Marco Bianchi", "Laura Neri", "Andrea Conti", "Silvia Rossi",
            "Davide Ferrari", "Elena Ricci", "Matteo Romano", "Francesca Greco",
            "Alessandro Marino", "Giulia Costa", "Simone Moretti", "Valentina Galli",
            "Francesco Lombardi", "Chiara Esposito", "Giovanni Barbieri", "Federica Bruno"
        ]

        self.fantasy_orgs = [
            "Istituto Centrale", "Azienda Moderna", "Centro Ricerche", "Gruppo Industriale",
            "Fondazione Scientifica", "Ente Pubblico", "Società Tecnologica", "Consulenza Avanzata"
        ]

        self.fantasy_places = [
            "Verona", "Padova", "Genova", "Perugia", "Modena", "Pisa", "Brescia", "Parma"
        ]

    def get_replacement(self, entity_type: str, original: str) -> str:
        """Ottiene sostituzione coerente per un'entità"""
        if original in self.mapping:
            return self.mapping[original]

        replacement = self._generate_replacement(entity_type, original)
        self.mapping[original] = replacement
        return replacement

    def _generate_replacement(self, entity_type: str, original: str) -> str:
        """Genera sostituzione basata sul tipo di entità"""
        if entity_type == "PERSON":
            if self.entity_counters['PERSON'] < len(self.fantasy_names):
                replacement = self.fantasy_names[self.entity_counters['PERSON']]
            else:
                replacement = f"Persona_{self.entity_counters['PERSON'] + 1}"
            self.entity_counters['PERSON'] += 1

        elif entity_type == "ORG":
            if self.entity_counters['ORG'] < len(self.fantasy_orgs):
                replacement = self.fantasy_orgs[self.entity_counters['ORG']]
            else:
                replacement = f"Organizzazione_{self.entity_counters['ORG'] + 1}"
            self.entity_counters['ORG'] += 1

        elif entity_type == "LOC":
            if self.entity_counters['LOC'] < len(self.fantasy_places):
                replacement = self.fantasy_places[self.entity_counters['LOC']]
            else:
                replacement = f"Località_{self.entity_counters['LOC'] + 1}"
            self.entity_counters['LOC'] += 1

        elif entity_type == "EMAIL":
            domain = original.split('@')[1] if '@' in original else "esempio.it"
            user = f"utente{self.entity_counters['EMAIL'] + 1}"
            replacement = f"{user}@{domain}"
            self.entity_counters['EMAIL'] += 1

        elif entity_type == "PHONE":
            replacement = f"0{random.randint(1,9)}-{random.randint(1000000,9999999)}"
            self.entity_counters['PHONE'] += 1

        else:
            replacement = "[ANONIMIZZATO]"

        return replacement

    def export_mapping(self, filepath: str):
        """Esporta mappatura su file JSON"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0',
            'mappings': self.mapping,
            'counters': self.entity_counters
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_mapping(self, filepath: str):
        """Importa mappatura da file JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.mapping = data.get('mappings', {})
            self.entity_counters = data.get('counters', self.entity_counters)


class FileProcessor:
    """Processore semplificato per file usando solo regex"""

    def __init__(self, replacement_manager: ReplacementManager):
        self.manager = replacement_manager

    def extract_text(self, filepath: str) -> str:
        """Estrae testo da file"""
        try:
            if filepath.lower().endswith('.json'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2, ensure_ascii=False)
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore lettura file: {e}")
            return ""

    def detect_entities_regex(self, text: str) -> List[Dict]:
        """Rileva entità usando regex"""
        entities = []

        # Pattern email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entities.append({
                "text": match.group(),
                "label": "EMAIL",
                "start": match.start(),
                "end": match.end()
            })

        # Pattern telefono
        phone_pattern = r'\b(?:0[0-9]{1,3}[-\s]?)?[0-9]{6,8}\b'
        for match in re.finditer(phone_pattern, text):
            entities.append({
                "text": match.group(),
                "label": "PHONE",
                "start": match.start(),
                "end": match.end()
            })

        # Pattern nomi (euristica)
        name_patterns = [
            r'\b(?:Dr\.|Dott\.|Prof\.|Ing\.)?\s*[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            r'\b[A-Z][a-z]+\s+(?:De|Del|Della|Di|Da)\s+[A-Z][a-z]+\b'
        ]

        for pattern in name_patterns:
            for match in re.finditer(pattern, text):
                entities.append({
                    "text": match.group().strip(),
                    "label": "PERSON",
                    "start": match.start(),
                    "end": match.end()
                })

        # Pattern organizzazioni (euristica)
        org_patterns = [
            r'\b(?:Università|Ospedale|Istituto|Azienda|Società)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
            r'\b[A-Z][a-z]+\s+(?:S\.p\.A\.|S\.r\.l\.|S\.n\.c\.)\b'
        ]

        for pattern in org_patterns:
            for match in re.finditer(pattern, text):
                entities.append({
                    "text": match.group().strip(),
                    "label": "ORG",
                    "start": match.start(),
                    "end": match.end()
                })

        return entities

    def anonymize_text(self, text: str, entities: List[Dict]) -> str:
        """Anonimizza testo sostituendo le entità"""
        entities_sorted = sorted(entities, key=lambda x: x["start"], reverse=True)

        anonymized_text = text
        for entity in entities_sorted:
            replacement = self.manager.get_replacement(entity["label"], entity["text"])
            anonymized_text = (anonymized_text[:entity["start"]] + 
                             replacement + 
                             anonymized_text[entity["end"]:])

        return anonymized_text


class PDFAnonymizerApp:
    """Applicazione principale con interfaccia Tkinter"""

    def __init__(self, root):
        self.root = root
        self.replacement_manager = ReplacementManager()
        self.file_processor = FileProcessor(self.replacement_manager)
        self.files_to_process = []

        self.setup_ui()

    def setup_ui(self):
        """Configura interfaccia utente"""
        self.root.title("PDF Anonymizer - Versione Semplificata")
        self.root.geometry("1000x700")

        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurazione griglia
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Titolo
        title_label = ttk.Label(main_frame, text="🔒 PDF Anonymizer", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Pannello controlli
        self.setup_controls_panel(main_frame)

        # Pannello principale
        self.setup_main_panel(main_frame)

        # Barra di stato
        self.status_var = tk.StringVar(value="Pronto - Aggiungi file per iniziare")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                       pady=(10, 0))

    def setup_controls_panel(self, parent):
        """Pannello controlli superiore"""
        controls_frame = ttk.LabelFrame(parent, text="Controlli", padding="10")
        controls_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), 
                           padx=(0, 10))

        # Pulsanti principali
        ttk.Button(controls_frame, text="📁 Aggiungi File", 
                  command=self.add_files).grid(row=0, column=0, pady=5, sticky=tk.W)

        ttk.Button(controls_frame, text="🔄 Importa Mappatura", 
                  command=self.import_mapping).grid(row=1, column=0, pady=5, sticky=tk.W)

        self.process_btn = ttk.Button(controls_frame, text="🚀 Avvia Anonimizzazione", 
                                     command=self.start_processing, state='disabled')
        self.process_btn.grid(row=2, column=0, pady=5, sticky=tk.W)

        ttk.Button(controls_frame, text="🗑️ Cancella Tutto", 
                  command=self.clear_all).grid(row=3, column=0, pady=5, sticky=tk.W)

        # Lista file
        ttk.Label(controls_frame, text="File da Processare:").grid(row=4, column=0, 
                                                                   pady=(20, 5), sticky=tk.W)

        self.files_listbox = tk.Listbox(controls_frame, height=6)
        self.files_listbox.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Button(controls_frame, text="Rimuovi Selezionato", 
                  command=self.remove_selected_file).grid(row=6, column=0, pady=5, sticky=tk.W)

        # Opzioni anonimizzazione
        ttk.Label(controls_frame, text="Opzioni:").grid(row=7, column=0, 
                                                        pady=(20, 5), sticky=tk.W)

        self.options_frame = ttk.Frame(controls_frame)
        self.options_frame.grid(row=8, column=0, sticky=(tk.W, tk.E))

        self.anonymize_persons = tk.BooleanVar(value=True)
        self.anonymize_orgs = tk.BooleanVar(value=True)
        self.anonymize_emails = tk.BooleanVar(value=True)
        self.anonymize_phones = tk.BooleanVar(value=True)

        ttk.Checkbutton(self.options_frame, text="👤 Persone", 
                       variable=self.anonymize_persons).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(self.options_frame, text="🏢 Organizzazioni", 
                       variable=self.anonymize_orgs).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(self.options_frame, text="📧 Email", 
                       variable=self.anonymize_emails).grid(row=2, column=0, sticky=tk.W)
        ttk.Checkbutton(self.options_frame, text="📱 Telefoni", 
                       variable=self.anonymize_phones).grid(row=3, column=0, sticky=tk.W)

        controls_frame.columnconfigure(0, weight=1)

    def setup_main_panel(self, parent):
        """Pannello principale con notebook"""
        notebook = ttk.Notebook(parent)
        notebook.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Tab Anteprima
        preview_frame = ttk.Frame(notebook)
        notebook.add(preview_frame, text="👁️ Anteprima")

        # Testo originale
        ttk.Label(preview_frame, text="Testo Originale:").grid(row=0, column=0, 
                                                               sticky=tk.W, pady=(0, 5))
        self.original_text = scrolledtext.ScrolledText(preview_frame, height=12, 
                                                      wrap=tk.WORD)
        self.original_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), 
                               pady=(0, 10))

        # Testo anonimizzato
        ttk.Label(preview_frame, text="Testo Anonimizzato:").grid(row=2, column=0, 
                                                                  sticky=tk.W, pady=(0, 5))
        self.anonymized_text = scrolledtext.ScrolledText(preview_frame, height=12, 
                                                        wrap=tk.WORD, state='disabled')
        self.anonymized_text.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(1, weight=1)
        preview_frame.rowconfigure(3, weight=1)

        # Tab Mappature
        mappings_frame = ttk.Frame(notebook)
        notebook.add(mappings_frame, text="🔄 Mappature")

        # Tabella mappature
        columns = ('Originale', 'Sostituzione', 'Tipo')
        self.mappings_tree = ttk.Treeview(mappings_frame, columns=columns, 
                                         show='headings', height=15)

        for col in columns:
            self.mappings_tree.heading(col, text=col)
            self.mappings_tree.column(col, width=150)

        mappings_scrollbar = ttk.Scrollbar(mappings_frame, orient=tk.VERTICAL, 
                                          command=self.mappings_tree.yview)
        self.mappings_tree.configure(yscrollcommand=mappings_scrollbar.set)

        self.mappings_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        mappings_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Pulsanti export
        export_frame = ttk.Frame(mappings_frame)
        export_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky=tk.W)

        ttk.Button(export_frame, text="💾 Salva Mappature", 
                  command=self.export_mapping).grid(row=0, column=0, padx=(0, 10))

        # Statistiche
        self.stats_label = ttk.Label(export_frame, text="Mappature: 0")
        self.stats_label.grid(row=0, column=1)

        mappings_frame.columnconfigure(0, weight=1)
        mappings_frame.rowconfigure(0, weight=1)

    def add_files(self):
        """Aggiungi file alla lista"""
        files = filedialog.askopenfilenames(
            title="Seleziona File da Anonimizzare",
            filetypes=[
                ("File Supportati", "*.txt *.json *.pdf"),
                ("Text files", "*.txt"),
                ("JSON files", "*.json"), 
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )

        for file_path in files:
            if file_path not in self.files_to_process:
                self.files_to_process.append(file_path)
                self.files_listbox.insert(tk.END, Path(file_path).name)

        self.process_btn.config(state='normal' if self.files_to_process else 'disabled')
        self.status_var.set(f"File aggiunti: {len(self.files_to_process)}")

    def remove_selected_file(self):
        """Rimuovi file selezionato"""
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            self.files_listbox.delete(index)
            del self.files_to_process[index]

        self.process_btn.config(state='normal' if self.files_to_process else 'disabled')

    def clear_all(self):
        """Cancella tutto"""
        if messagebox.askyesno("Conferma", "Cancellare tutti i file e le mappature?"):
            self.files_to_process.clear()
            self.files_listbox.delete(0, tk.END)
            self.replacement_manager = ReplacementManager()
            self.file_processor.manager = self.replacement_manager

            self.original_text.delete(1.0, tk.END)
            self.anonymized_text.config(state='normal')
            self.anonymized_text.delete(1.0, tk.END)
            self.anonymized_text.config(state='disabled')

            self.update_mappings_display()
            self.process_btn.config(state='disabled')
            self.status_var.set("Tutto cancellato")

    def import_mapping(self):
        """Importa mappature da file"""
        filepath = filedialog.askopenfilename(
            title="Importa Mappature",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filepath:
            try:
                self.replacement_manager.import_mapping(filepath)
                self.update_mappings_display()
                messagebox.showinfo("Successo", "Mappature importate correttamente!")
                self.status_var.set("Mappature importate")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore importazione: {e}")

    def export_mapping(self):
        """Esporta mappature su file"""
        if not self.replacement_manager.mapping:
            messagebox.showwarning("Attenzione", "Nessuna mappatura da salvare!")
            return

        filepath = filedialog.asksaveasfilename(
            title="Salva Mappature",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filepath:
            try:
                self.replacement_manager.export_mapping(filepath)
                messagebox.showinfo("Successo", "Mappature salvate correttamente!")
                self.status_var.set(f"Mappature salvate: {filepath}")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore salvataggio: {e}")

    def start_processing(self):
        """Avvia elaborazione file"""
        if not self.files_to_process:
            return

        self.status_var.set("Elaborazione in corso...")
        self.process_btn.config(state='disabled')

        try:
            for i, file_path in enumerate(self.files_to_process):
                # Estrai testo
                text = self.file_processor.extract_text(file_path)
                if not text:
                    continue

                # Rileva entità
                entities = self.file_processor.detect_entities_regex(text)

                # Filtra in base alle opzioni
                filtered_entities = []
                for entity in entities:
                    if ((entity["label"] == "PERSON" and self.anonymize_persons.get()) or
                        (entity["label"] == "ORG" and self.anonymize_orgs.get()) or
                        (entity["label"] == "EMAIL" and self.anonymize_emails.get()) or
                        (entity["label"] == "PHONE" and self.anonymize_phones.get())):
                        filtered_entities.append(entity)

                # Anonimizza
                anonymized = self.file_processor.anonymize_text(text, filtered_entities)

                # Salva file anonimizzato
                output_path = str(Path(file_path).parent / f"{Path(file_path).stem}_anonimizzato{Path(file_path).suffix}")
                with open(output_path, 'w', encoding='utf-8') as f:
                    if file_path.lower().endswith('.json'):
                        try:
                            data = json.loads(anonymized)
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        except:
                            f.write(anonymized)
                    else:
                        f.write(anonymized)

                # Mostra anteprima del primo file
                if i == 0:
                    self.original_text.delete(1.0, tk.END)
                    self.original_text.insert(1.0, text[:1000] + "..." if len(text) > 1000 else text)

                    self.anonymized_text.config(state='normal')
                    self.anonymized_text.delete(1.0, tk.END)
                    self.anonymized_text.insert(1.0, anonymized[:1000] + "..." if len(anonymized) > 1000 else anonymized)
                    self.anonymized_text.config(state='disabled')

            self.update_mappings_display()

            messagebox.showinfo("Completato", 
                              f"Elaborati {len(self.files_to_process)} file!\n"
                              f"Mappature totali: {len(self.replacement_manager.mapping)}")

            self.status_var.set("Elaborazione completata")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante elaborazione: {e}")
            self.status_var.set("Errore elaborazione")
        finally:
            self.process_btn.config(state='normal')

    def update_mappings_display(self):
        """Aggiorna visualizzazione mappature"""
        # Cancella esistenti
        for item in self.mappings_tree.get_children():
            self.mappings_tree.delete(item)

        # Aggiungi mappature
        for original, replacement in self.replacement_manager.mapping.items():
            # Determina tipo (approssimativo)
            entity_type = "PERSON"
            if "@" in original:
                entity_type = "EMAIL"
            elif any(c.isdigit() for c in original):
                entity_type = "PHONE"
            elif any(word in replacement for word in ["Organizzazione", "Istituto", "Azienda"]):
                entity_type = "ORG"

            self.mappings_tree.insert('', tk.END, values=(original, replacement, entity_type))

        # Aggiorna statistiche
        total = len(self.replacement_manager.mapping)
        self.stats_label.config(text=f"Mappature: {total}")

    def on_closing(self):
        """Gestisce chiusura applicazione"""
        if self.replacement_manager.mapping:
            if messagebox.askyesno("Salva Mappature", 
                                 "Vuoi salvare le mappature prima di uscire?"):
                self.export_mapping()

        self.root.destroy()


def main():
    """Funzione principale"""
    root = tk.Tk()
    app = PDFAnonymizerApp(root)

    # Gestisce chiusura finestra
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Avvia applicazione
    root.mainloop()


if __name__ == "__main__":
    main()
