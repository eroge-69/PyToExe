# main.py - PDF Anonymizer Completo
# Applicazione per anonimizzazione PDF e JSON con mappatura coerente

import sys
import os
import json
import random
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QLabel, QTextEdit, QFileDialog, QProgressBar, 
    QCheckBox, QListWidget, QMessageBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QSplitter, QGroupBox, QComboBox, QSpinBox,
    QListWidgetItem, QAbstractItemView, QHeaderView
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

# Importi condizionali per le librerie PDF e NLP
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("PyMuPDF non trovato - funzionalità PDF limitate")

try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False
    print("spaCy non trovato - usato riconoscimento pattern base")


class ReplacementManager:
    """Gestisce la mappatura persistente delle sostituzioni per garantire coerenza"""

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
            "Fondazione Scientifica", "Ente Pubblico", "Società Tecnologica", "Consulenza Avanzata",
            "Organizzazione Professionale", "Servizi Integrati", "Sviluppo Sostenibile"
        ]

        self.fantasy_places = [
            "Verona", "Padova", "Genova", "Perugia", "Modena", "Pisa", "Brescia", 
            "Parma", "Trento", "Trieste", "Bolzano", "Ancona", "Rimini"
        ]

    def get_replacement(self, entity_type: str, original: str) -> str:
        """Ottiene sostituzione coerente per un'entità"""
        if original in self.mapping:
            return self.mapping[original]

        # Genera nuova sostituzione
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

    def import_mapping(self, filepath: str):
        """Importa mappatura da file JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.mapping = data.get('mappings', {})
                self.entity_counters = data.get('counters', self.entity_counters)
            return True
        except Exception as e:
            print(f"Errore import mappatura: {e}")
            return False

    def export_mapping(self, filepath: str):
        """Esporta mappatura su file JSON"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0',
                'mappings': self.mapping,
                'counters': self.entity_counters,
                'statistics': {
                    'total_mappings': len(self.mapping),
                    'entities_by_type': {k: v for k, v in self.entity_counters.items() if v > 0}
                }
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Errore export mappatura: {e}")
            return False


class FileProcessor:
    """Processore per file PDF e JSON con riconoscimento entità"""

    def __init__(self, replacement_manager: ReplacementManager):
        self.manager = replacement_manager
        self.nlp = None

        # Inizializza spaCy se disponibile
        if HAS_SPACY:
            try:
                self.nlp = spacy.load("it_core_news_sm")
            except OSError:
                print("Modello spaCy it_core_news_sm non trovato")
                self.nlp = None

    def extract_text(self, filepath: str) -> str:
        """Estrae testo da file PDF o JSON"""
        try:
            if filepath.lower().endswith('.json'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2, ensure_ascii=False)

            elif filepath.lower().endswith('.pdf') and HAS_PYMUPDF:
                doc = fitz.open(filepath)
                text = ""
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()
                return text

            else:
                # Fallback per file di testo
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()

        except Exception as e:
            print(f"Errore estrazione testo da {filepath}: {e}")
            return ""

    def detect_entities(self, text: str) -> List[Dict]:
        """Rileva entità nel testo usando spaCy o pattern regex"""
        entities = []

        if self.nlp:
            # Usa spaCy per riconoscimento avanzato
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "ORG", "LOC"]:
                    entities.append({
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char
                    })
        else:
            # Pattern regex di base per entità comuni
            import re

            # Pattern email
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            for match in re.finditer(email_pattern, text):
                entities.append({
                    "text": match.group(),
                    "label": "EMAIL", 
                    "start": match.start(),
                    "end": match.end()
                })

            # Pattern telefono italiano
            phone_pattern = r'\b(?:0[0-9]{1,3}[-\s]?)?[0-9]{6,8}\b'
            for match in re.finditer(phone_pattern, text):
                entities.append({
                    "text": match.group(),
                    "label": "PHONE",
                    "start": match.start(), 
                    "end": match.end()
                })

        return entities

    def anonymize_text(self, text: str, entities: List[Dict]) -> str:
        """Anonimizza testo sostituendo le entità"""
        # Ordina entità per posizione (dalla fine all'inizio)
        entities_sorted = sorted(entities, key=lambda x: x["start"], reverse=True)

        anonymized_text = text
        for entity in entities_sorted:
            replacement = self.manager.get_replacement(entity["label"], entity["text"])
            anonymized_text = (anonymized_text[:entity["start"]] + 
                             replacement + 
                             anonymized_text[entity["end"]:])

        return anonymized_text

    def save_anonymized_file(self, original_path: str, anonymized_text: str) -> str:
        """Salva file anonimizzato"""
        path_obj = Path(original_path)
        output_path = path_obj.parent / f"{path_obj.stem}_anonimizzato{path_obj.suffix}"

        try:
            if original_path.lower().endswith('.json'):
                # Per JSON, parse e re-serialize
                try:
                    data = json.loads(anonymized_text)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                except:
                    # Fallback su testo semplice
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(anonymized_text)
            else:
                # Per tutti gli altri file, salva come testo
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(anonymized_text)

            return str(output_path)

        except Exception as e:
            print(f"Errore salvataggio file: {e}")
            return ""


class ProcessingWorker(QThread):
    """Worker thread per anonimizzazione in background"""

    progress = pyqtSignal(int)
    file_processed = pyqtSignal(str, str, int)  # filepath, output_path, entities_count
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, file_processor: FileProcessor, file_paths: List[str], options: Dict):
        super().__init__()
        self.file_processor = file_processor
        self.file_paths = file_paths
        self.options = options

    def run(self):
        try:
            total_files = len(self.file_paths)

            for i, filepath in enumerate(self.file_paths):
                # Estrai testo
                text = self.file_processor.extract_text(filepath)
                if not text:
                    continue

                # Rileva entità
                entities = self.file_processor.detect_entities(text)

                # Filtra entità in base alle opzioni
                filtered_entities = []
                for entity in entities:
                    if (entity["label"] == "PERSON" and self.options.get("anonymize_persons", True)) or \
                       (entity["label"] == "ORG" and self.options.get("anonymize_orgs", True)) or \
                       (entity["label"] == "LOC" and self.options.get("anonymize_places", True)) or \
                       (entity["label"] == "EMAIL" and self.options.get("anonymize_emails", True)) or \
                       (entity["label"] == "PHONE" and self.options.get("anonymize_phones", True)):
                        filtered_entities.append(entity)

                # Anonimizza
                anonymized_text = self.file_processor.anonymize_text(text, filtered_entities)

                # Salva file
                output_path = self.file_processor.save_anonymized_file(filepath, anonymized_text)

                # Emetti segnale progresso
                progress_value = int((i + 1) * 100 / total_files)
                self.progress.emit(progress_value)
                self.file_processed.emit(filepath, output_path, len(filtered_entities))

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Finestra principale dell'applicazione"""

    def __init__(self):
        super().__init__()
        self.replacement_manager = ReplacementManager()
        self.file_processor = FileProcessor(self.replacement_manager)
        self.files_to_process = []
        self.processed_files = []

        self.init_ui()
        self.apply_style()

        # Timer per auto-save periodico delle mappature
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave_mappings)
        self.autosave_timer.start(300000)  # 5 minuti

    def init_ui(self):
        """Inizializza interfaccia utente"""
        self.setWindowTitle("PDF Anonymizer - Anonimizzazione Avanzata Documenti")
        self.setGeometry(100, 100, 1200, 800)

        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principale
        main_layout = QVBoxLayout(central_widget)

        # Barra dei controlli superiore
        self.create_control_bar(main_layout)

        # Splitter per divisione principale
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Pannello sinistro - File e controlli
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # Pannello destro - Risultati e anteprima
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([400, 800])

        # Barra di stato
        self.statusBar().showMessage("Pronto - Carica file per iniziare")

    def create_control_bar(self, parent_layout):
        """Crea barra controlli superiore"""
        control_layout = QHBoxLayout()

        # Pulsanti principali
        self.import_mapping_btn = QPushButton("🔄 Importa Mappatura")
        self.import_mapping_btn.clicked.connect(self.import_mapping)

        self.add_files_btn = QPushButton("📁 Aggiungi File")
        self.add_files_btn.clicked.connect(self.add_files)

        self.process_btn = QPushButton("🚀 Avvia Anonimizzazione")
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setEnabled(False)

        self.clear_btn = QPushButton("🗑️ Cancella Tutto")
        self.clear_btn.clicked.connect(self.clear_all)

        control_layout.addWidget(self.import_mapping_btn)
        control_layout.addWidget(self.add_files_btn) 
        control_layout.addWidget(self.process_btn)
        control_layout.addWidget(self.clear_btn)
        control_layout.addStretch()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        control_layout.addWidget(self.progress_bar)

        parent_layout.addLayout(control_layout)

    def create_left_panel(self) -> QWidget:
        """Crea pannello sinistro con file e opzioni"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Sezione file
        files_group = QGroupBox("File da Processare")
        files_layout = QVBoxLayout(files_group)

        self.files_list = QListWidget()
        self.files_list.setSelectionMode(QAbstractItemView.MultiSelection)
        files_layout.addWidget(self.files_list)

        files_info_layout = QHBoxLayout()
        self.files_count_label = QLabel("File: 0")
        self.remove_selected_btn = QPushButton("Rimuovi Selezionati")
        self.remove_selected_btn.clicked.connect(self.remove_selected_files)

        files_info_layout.addWidget(self.files_count_label)
        files_info_layout.addWidget(self.remove_selected_btn)
        files_layout.addLayout(files_info_layout)

        left_layout.addWidget(files_group)

        # Opzioni anonimizzazione
        options_group = QGroupBox("Opzioni Anonimizzazione")
        options_layout = QVBoxLayout(options_group)

        self.anonymize_persons = QCheckBox("👤 Persone")
        self.anonymize_persons.setChecked(True)
        self.anonymize_orgs = QCheckBox("🏢 Organizzazioni") 
        self.anonymize_orgs.setChecked(True)
        self.anonymize_places = QCheckBox("📍 Luoghi")
        self.anonymize_places.setChecked(True)
        self.anonymize_emails = QCheckBox("📧 Email")
        self.anonymize_emails.setChecked(True)
        self.anonymize_phones = QCheckBox("📱 Telefoni")
        self.anonymize_phones.setChecked(True)

        options_layout.addWidget(self.anonymize_persons)
        options_layout.addWidget(self.anonymize_orgs)
        options_layout.addWidget(self.anonymize_places)
        options_layout.addWidget(self.anonymize_emails)
        options_layout.addWidget(self.anonymize_phones)

        left_layout.addWidget(options_group)

        # Statistiche mappatura
        stats_group = QGroupBox("Statistiche Mappatura")
        stats_layout = QVBoxLayout(stats_group)

        self.mapping_stats_label = QLabel("Mappature totali: 0")
        self.entities_stats_label = QLabel("Entità per tipo: -")

        stats_layout.addWidget(self.mapping_stats_label)
        stats_layout.addWidget(self.entities_stats_label)

        left_layout.addWidget(stats_group)
        left_layout.addStretch()

        return left_widget

    def create_right_panel(self) -> QWidget:
        """Crea pannello destro con risultati"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Tab widget per diverse viste
        self.tab_widget = QTabWidget()

        # Tab mappature
        mappings_widget = QWidget()
        mappings_layout = QVBoxLayout(mappings_widget)

        self.mappings_table = QTableWidget()
        self.mappings_table.setColumnCount(3)
        self.mappings_table.setHorizontalHeaderLabels(["Originale", "Sostituzione", "Tipo"])
        self.mappings_table.horizontalHeader().setStretchLastSection(True)
        mappings_layout.addWidget(self.mappings_table)

        self.tab_widget.addTab(mappings_widget, "🔄 Mappature")

        # Tab file processati
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["File Originale", "File Anonimizzato", "Entità", "Stato"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        results_layout.addWidget(self.results_table)

        self.tab_widget.addTab(results_widget, "📄 File Processati")

        # Tab anteprima
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)

        preview_splitter = QSplitter(Qt.Vertical)

        # Testo originale
        original_group = QGroupBox("Testo Originale (anteprima)")
        original_layout = QVBoxLayout(original_group)
        self.original_preview = QTextEdit()
        self.original_preview.setReadOnly(True)
        self.original_preview.setMaximumHeight(200)
        original_layout.addWidget(self.original_preview)
        preview_splitter.addWidget(original_group)

        # Testo anonimizzato
        anonymized_group = QGroupBox("Testo Anonimizzato (anteprima)")
        anonymized_layout = QVBoxLayout(anonymized_group)
        self.anonymized_preview = QTextEdit()
        self.anonymized_preview.setReadOnly(True)
        self.anonymized_preview.setMaximumHeight(200)
        anonymized_layout.addWidget(self.anonymized_preview)
        preview_splitter.addWidget(anonymized_group)

        preview_layout.addWidget(preview_splitter)

        self.tab_widget.addTab(preview_widget, "👁️ Anteprima")

        right_layout.addWidget(self.tab_widget)

        return right_widget

    def apply_style(self):
        """Applica stile moderno all'applicazione"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }

            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }

            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #45a049;
            }

            QPushButton:pressed {
                background-color: #3d8b40;
            }

            QPushButton:disabled {
                background-color: #cccccc;
            }

            QCheckBox {
                spacing: 5px;
            }

            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }

            QTableWidget {
                gridline-color: #cccccc;
                background-color: white;
            }

            QTableWidget::item {
                padding: 4px;
            }

            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }

            QTabBar::tab {
                background-color: #e1e1e1;
                padding: 8px 12px;
                margin-right: 2px;
            }

            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #4CAF50;
            }
        """)

    def add_files(self):
        """Aggiunge file alla lista"""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Seleziona File da Anonimizzare",
            "",
            "File Supportati (*.pdf *.json *.txt);;PDF Files (*.pdf);;JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
        )

        for file_path in files:
            if file_path not in self.files_to_process:
                self.files_to_process.append(file_path)
                item = QListWidgetItem(os.path.basename(file_path))
                item.setData(Qt.UserRole, file_path)
                self.files_list.addItem(item)

        self.update_files_count()
        self.process_btn.setEnabled(len(self.files_to_process) > 0)

    def remove_selected_files(self):
        """Rimuove file selezionati"""
        selected_items = self.files_list.selectedItems()
        for item in selected_items:
            file_path = item.data(Qt.UserRole)
            if file_path in self.files_to_process:
                self.files_to_process.remove(file_path)
            self.files_list.takeItem(self.files_list.row(item))

        self.update_files_count()
        self.process_btn.setEnabled(len(self.files_to_process) > 0)

    def update_files_count(self):
        """Aggiorna contatore file"""
        self.files_count_label.setText(f"File: {len(self.files_to_process)}")

    def clear_all(self):
        """Cancella tutto"""
        reply = QMessageBox.question(
            self, 
            "Conferma", 
            "Vuoi cancellare tutti i file e le mappature?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.files_to_process.clear()
            self.processed_files.clear()
            self.files_list.clear()
            self.replacement_manager = ReplacementManager()
            self.file_processor.manager = self.replacement_manager

            self.update_files_count()
            self.update_mappings_display()
            self.update_results_display()
            self.process_btn.setEnabled(False)

    def import_mapping(self):
        """Importa mappatura da file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Importa Mappatura", 
            "",
            "JSON Files (*.json);;All Files (*)"
        )

        if filepath and self.replacement_manager.import_mapping(filepath):
            QMessageBox.information(self, "Successo", "Mappatura importata correttamente!")
            self.update_mappings_display()
            self.update_stats_display()
        elif filepath:
            QMessageBox.warning(self, "Errore", "Impossibile importare la mappatura!")

    def start_processing(self):
        """Avvia elaborazione file"""
        if not self.files_to_process:
            return

        # Opzioni di anonimizzazione
        options = {
            'anonymize_persons': self.anonymize_persons.isChecked(),
            'anonymize_orgs': self.anonymize_orgs.isChecked(),
            'anonymize_places': self.anonymize_places.isChecked(),
            'anonymize_emails': self.anonymize_emails.isChecked(),
            'anonymize_phones': self.anonymize_phones.isChecked(),
        }

        # Avvia worker thread
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.process_btn.setEnabled(False)

        self.worker = ProcessingWorker(self.file_processor, self.files_to_process.copy(), options)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.file_processed.connect(self.on_file_processed)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.error.connect(self.on_processing_error)
        self.worker.start()

        self.statusBar().showMessage("Elaborazione in corso...")

    def on_file_processed(self, filepath: str, output_path: str, entities_count: int):
        """Gestisce completamento elaborazione singolo file"""
        self.processed_files.append({
            'original': filepath,
            'anonymized': output_path,
            'entities': entities_count,
            'status': 'Completato' if output_path else 'Errore'
        })

        self.update_results_display()
        self.update_mappings_display()
        self.update_stats_display()

    def on_processing_finished(self):
        """Gestisce completamento elaborazione"""
        self.progress_bar.setVisible(False)
        self.process_btn.setEnabled(True)

        total_processed = len([f for f in self.processed_files if f['status'] == 'Completato'])
        QMessageBox.information(
            self,
            "Elaborazione Completata",
            f"Elaborati {total_processed} file con successo!\n"
            f"Mappature totali: {len(self.replacement_manager.mapping)}"
        )

        self.statusBar().showMessage("Elaborazione completata")

    def on_processing_error(self, error_msg: str):
        """Gestisce errore elaborazione"""
        self.progress_bar.setVisible(False)
        self.process_btn.setEnabled(True)
        QMessageBox.critical(self, "Errore", f"Errore durante elaborazione:\n{error_msg}")
        self.statusBar().showMessage("Errore elaborazione")

    def update_mappings_display(self):
        """Aggiorna visualizzazione mappature"""
        self.mappings_table.setRowCount(len(self.replacement_manager.mapping))

        for i, (original, replacement) in enumerate(self.replacement_manager.mapping.items()):
            # Determina tipo entità (approssimativo)
            entity_type = "PERSON"  # Default
            if "@" in original:
                entity_type = "EMAIL"
            elif any(c.isdigit() for c in original):
                entity_type = "PHONE"
            elif "Organizzazione" in replacement or "Istituto" in replacement:
                entity_type = "ORG"
            elif "Località" in replacement:
                entity_type = "LOC"

            self.mappings_table.setItem(i, 0, QTableWidgetItem(original))
            self.mappings_table.setItem(i, 1, QTableWidgetItem(replacement))
            self.mappings_table.setItem(i, 2, QTableWidgetItem(entity_type))

    def update_results_display(self):
        """Aggiorna visualizzazione risultati"""
        self.results_table.setRowCount(len(self.processed_files))

        for i, file_info in enumerate(self.processed_files):
            self.results_table.setItem(i, 0, QTableWidgetItem(os.path.basename(file_info['original'])))
            self.results_table.setItem(i, 1, QTableWidgetItem(
                os.path.basename(file_info['anonymized']) if file_info['anonymized'] else 'N/A'
            ))
            self.results_table.setItem(i, 2, QTableWidgetItem(str(file_info['entities'])))
            self.results_table.setItem(i, 3, QTableWidgetItem(file_info['status']))

    def update_stats_display(self):
        """Aggiorna statistiche"""
        total_mappings = len(self.replacement_manager.mapping)
        self.mapping_stats_label.setText(f"Mappature totali: {total_mappings}")

        entities_text = ", ".join([f"{k}: {v}" for k, v in self.replacement_manager.entity_counters.items() if v > 0])
        self.entities_stats_label.setText(f"Entità per tipo: {entities_text if entities_text else 'N/A'}")

    def autosave_mappings(self):
        """Salvataggio automatico mappature"""
        if len(self.replacement_manager.mapping) > 0:
            temp_path = os.path.join(os.path.expanduser("~"), ".pdf_anonymizer_temp.json")
            self.replacement_manager.export_mapping(temp_path)

    def closeEvent(self, event):
        """Gestisce chiusura applicazione"""
        if len(self.replacement_manager.mapping) > 0:
            reply = QMessageBox.question(
                self,
                "Salva Mappature",
                "Vuoi salvare le corrispondenze prima di uscire?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Yes:
                filepath, _ = QFileDialog.getSaveFileName(
                    self,
                    "Salva Mappature",
                    f"mappature_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    "JSON Files (*.json);;All Files (*)"
                )

                if filepath:
                    if self.replacement_manager.export_mapping(filepath):
                        QMessageBox.information(self, "Successo", "Mappature salvate correttamente!")
                        event.accept()
                    else:
                        QMessageBox.warning(self, "Errore", "Errore nel salvataggio!")
                        event.ignore()
                else:
                    event.ignore()

            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Funzione principale"""
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Anonymizer")
    app.setApplicationVersion("1.0")

    # Controlla dipendenze
    missing_deps = []
    if not HAS_PYMUPDF:
        missing_deps.append("PyMuPDF (per elaborazione PDF)")
    if not HAS_SPACY:
        missing_deps.append("spaCy (per riconoscimento entità avanzato)")

    if missing_deps:
        msg = QMessageBox()
        msg.setWindowTitle("Dipendenze Mancanti")
        msg.setText("Alcune funzionalità potrebbero essere limitate:\n\n" + "\n".join(missing_deps))
        msg.setInformativeText("L'applicazione funzionerà comunque con funzionalità di base.")
        msg.exec_()

    # Crea e mostra finestra principale
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
