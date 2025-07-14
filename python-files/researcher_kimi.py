# search_app.py
import sys
import re
import json
import time
import requests
import numpy as np
import fitz  # PyMuPDF
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
                             QSlider, QLabel, QCheckBox, QSpinBox, QPushButton,
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QMessageBox, QFileDialog, QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sentence_transformers import SentenceTransformer
from duckduckgo_search import DDGS
from scholarly import scholarly
import trafilatura
from bs4 import BeautifulSoup
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter

# ========== Configuration ==========
CONFIG = {
    "models": {
        "relevance": "cross-encoder/ms-marco-MiniLM-L-6-v2",
        "summarization": "Falconsai/text_summarization",
        "embedding": "sentence-transformers/all-MiniLM-L6-v2"
    },
    "search_engines": ["Google Scholar", "DuckDuckGo"],
    "presets": ["Official Data", "Reputable Data", "All Data"],
    "cache_dir": "./model_cache",
    "max_results": 50
}

# ========== Utility Functions ==========
def load_quantized_model(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=CONFIG["cache_dir"])
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, cache_dir=CONFIG["cache_dir"]
    )
    return tokenizer, model

def extract_main_content(html):
    try:
        return trafilatura.extract(html, include_comments=False, include_tables=False) or ""
    except Exception:
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup(["script", "style", "header", "footer", "nav"]):
            tag.decompose()
        return soup.get_text(" ", strip=True)

def extract_text_from_pdf(pdf_bytes):
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception:
        return ""

# ========== Core Search Engine ==========
class SearchEngine:
    def __init__(self):
        self.relevance_tokenizer, self.relevance_model = load_quantized_model(
            CONFIG["models"]["relevance"]
        )
        self.embedding_model = SentenceTransformer(CONFIG["models"]["embedding"])

        self.summarizer = pipeline(
            "summarization",
            model=CONFIG["models"]["summarization"],
            tokenizer=CONFIG["models"]["summarization"]
        )

        self.official_domains = ['.gov', '.edu', '.ac.', '.org', '.int']
        self.reputable_domains = self.official_domains + [
            'nytimes.com', 'bbc.com', 'reuters.com', 'apnews.com',
            'wsj.com', 'theguardian.com', 'nature.com', 'sciencemag.org'
        ]
        self.full_text_cache = {}

    # ---------------- Search dispatcher ----------------
    def search(self, query, engine, preset, confidence_cutoff, time_range,
               use_full_text=False, max_results=CONFIG["max_results"]):
        results = []

        if engine == "Google Scholar":
            try:
                scholar_results = scholarly.search_pubs(
                    query, year_low=time_range[0], year_high=time_range[1]
                )
                for i, item in enumerate(scholar_results):
                    if len(results) >= max_results:
                        break
                    result = {
                        'title': item.bib.get('title', ''),
                        'url': item.bib.get('url', ''),
                        'snippet': item.bib.get('abstract', ''),
                        'year': int(item.bib.get('year', 0)) if str(item.bib.get('year', '')).isdigit() else 0,
                        'source': 'Google Scholar',
                        'content': '',
                        'pdf_url': ''
                    }
                    try:
                        result['pdf_url'] = item.get('eprint', '') or (item.bib.get('url') if item.bib.get('url', '').endswith('.pdf') else '')
                    except Exception:
                        pass
                    results.append(result)
            except Exception as e:
                print("Google Scholar error:", e)

        elif engine == "DuckDuckGo":
            # Map numeric range to DuckDuckGo timelimit
            timelimit_map = {(2025, 2025): 'd', (2024, 2025): 'w', (2023, 2025): 'm'}
            timelimit = timelimit_map.get(time_range, 'y')
            try:
                with DDGS() as ddgs:
                    ddgs_results = ddgs.text(query, timelimit=timelimit, max_results=max_results)
                    for item in ddgs_results:
                        if len(results) >= max_results:
                            break
                        result = {
                            'title': item.get('title', ''),
                            'url': item.get('href', ''),
                            'snippet': item.get('body') or '',
                            'year': self.extract_year(item),
                            'source': 'DuckDuckGo',
                            'content': '',
                            'pdf_url': ''
                        }
                        results.append(result)
            except Exception as e:
                print("DuckDuckGo error:", e)

        results = self.apply_preset_filter(results, preset)
        results = self.process_results(results, query, confidence_cutoff, use_full_text)
        return results

    # ---------------- Helpers ----------------
    def extract_year(self, item):
        m = re.search(r'\b(19|20)\d{2}\b', str(item.get('body', '')))
        return int(m.group()) if m else 0

    def apply_preset_filter(self, results, preset):
        if preset == "Official Data":
            return [r for r in results if any(d in r['url'] for d in self.official_domains)]
        elif preset == "Reputable Data":
            return [r for r in results if any(d in r['url'] for d in self.reputable_domains)]
        return results

    def process_results(self, results, query, confidence_cutoff, use_full_text=False):
        processed = []
        for result in results:
            try:
                cache_key = result.get('pdf_url') or result['url']
                if cache_key in self.full_text_cache:
                    result['content'] = self.full_text_cache[cache_key]
                else:
                    if result['source'] == 'Google Scholar' and use_full_text:
                        if result.get('pdf_url'):
                            try:
                                r = requests.get(result['pdf_url'], timeout=10)
                                if r.status_code == 200 and 'application/pdf' in r.headers.get('content-type', '').lower():
                                    result['content'] = extract_text_from_pdf(r.content)
                                else:
                                    result['content'] = extract_main_content(r.text)
                                self.full_text_cache[cache_key] = result['content']
                            except Exception:
                                result['content'] = result['snippet']
                        else:
                            result['content'] = result['snippet']
                    else:
                        if result['source'] == 'Google Scholar':
                            result['content'] = result['snippet']
                        else:
                            r = requests.get(result['url'], timeout=10)
                            result['content'] = extract_main_content(r.text)
                            self.full_text_cache[cache_key] = result['content']

                features = self.relevance_tokenizer(
                    [query, result['content'][:2000]],
                    padding=True, truncation=True, return_tensors="pt", max_length=512
                )
                score = self.relevance_model(**features).logits.squeeze().item()
                result['confidence'] = float(1 / (1 + np.exp(-score)))
                if result['confidence'] >= confidence_cutoff:
                    processed.append(result)
            except Exception as e:
                print("Process result error:", e)
        return processed

    # ---------------- Summaries & exports ----------------
    def summarize_results(self, results, query, use_full_text=False):
        if not results:
            return "No relevant results found."

        context = []
        for r in results:
            src = f"Source: {r['url']}\n"
            content = (r['content'][:5000] if use_full_text else r['content'][:1000]) or ''
            context.append(src + content)
        full_context = "\n\n".join(context).strip()
        if not full_context:
            return "No usable content found for summarization."

        summary = self.summarizer(
            full_context, max_length=300, min_length=100, do_sample=False
        )[0]['summary_text']
        citations = "\n\nSources:\n" + "\n".join([r['url'] for r in results])
        return summary + citations

    def search_within_results(self, results, new_query, use_full_text=False):
        contents = [r['content'][:2000] for r in results]
        if not contents:
            return results
        embeddings = self.embedding_model.encode(contents)
        query_emb = self.embedding_model.encode([new_query])
        sims = np.dot(embeddings, query_emb.T).flatten()
        for r, s in zip(results, sims):
            r['confidence'] = float(s)
        return results

    def export_bibtex(self, results):
        db = BibDatabase()
        db.entries = []
        for r in results:
            entry = {
                'ENTRYTYPE': 'article' if r['source'] == 'Google Scholar' else 'misc',
                'ID': re.sub(r'\W+', '', r['title'])[:20],
                'title': r['title'],
                'url': r['url'],
                'year': str(r['year']),
                'author': 'Unknown',
                'abstract': r['snippet'][:500]
            }
            db.entries.append(entry)
        writer = BibTexWriter()
        return writer.write(db)

# ========== GUI ==========
class SearchThread(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, engine, **kwargs):
        super().__init__()
        self.engine = engine
        self.kwargs = kwargs

    def run(self):
        try:
            results = self.engine.search(**self.kwargs)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

class SearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = SearchEngine()
        self.results = []
        self.init_ui()
        self.setWindowTitle("Neural Search Assistant")
        self.resize(1200, 900)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # ---- Parameters form ----
        form = QFormLayout()
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Enter your question...")
        form.addRow("Query:", self.query_input)

        self.engine_combo = QComboBox()
        self.engine_combo.addItems(CONFIG["search_engines"])
        form.addRow("Search Engine:", self.engine_combo)

        self.preset_combo = QComboBox()
        self.preset_combo.addItems(CONFIG["presets"])
        form.addRow("Data Preset:", self.preset_combo)

        conf_h = QHBoxLayout()
        self.conf_slider = QSlider(Qt.Horizontal)
        self.conf_slider.setRange(0, 100)
        self.conf_slider.setValue(70)
        self.conf_label = QLabel("0.70")
        conf_h.addWidget(self.conf_slider)
        conf_h.addWidget(self.conf_label)
        form.addRow("Confidence Cutoff:", conf_h)

        year_h = QHBoxLayout()
        self.start_year = QLineEdit()
        self.start_year.setPlaceholderText("Start")
        self.end_year = QLineEdit()
        self.end_year.setPlaceholderText("End")
        year_h.addWidget(self.start_year)
        year_h.addWidget(QLabel("to"))
        year_h.addWidget(self.end_year)
        form.addRow("Time Range:", year_h)

        self.use_full = QCheckBox("Use full text for analysis (slower)")
        self.use_full.setChecked(False)
        form.addRow(self.use_full)

        max_h = QHBoxLayout()
        max_h.addWidget(QLabel("Max results:"))
        self.max_spin = QSpinBox()
        self.max_spin.setRange(1, 100)
        self.max_spin.setValue(CONFIG["max_results"])
        max_h.addWidget(self.max_spin)
        form.addRow(max_h)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.start_search)
        form.addRow(search_btn)

        layout.addLayout(form)

        # ---- Tabs ----
        tabs = QTabWidget()
        self.all_table = QTableWidget()
        self.all_table.setColumnCount(7)
        self.all_table.setHorizontalHeaderLabels(
            ["Title", "Source", "Year", "Confidence", "URL", "PDF", "Preview"])
        self.all_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.filt_table = QTableWidget()
        self.filt_table.setColumnCount(7)
        self.filt_table.setHorizontalHeaderLabels(
            ["Title", "Source", "Year", "Confidence", "URL", "PDF", "Preview"])
        self.filt_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        summary_w = QWidget()
        QVBoxLayout(summary_w).addWidget(QLabel("Summary:"))
        QVBoxLayout(summary_w).addWidget(self.summary_text)

        tabs.addTab(self.all_table, "All Results")
        tabs.addTab(self.filt_table, "Filtered Results")
        tabs.addTab(summary_w, "Summary")
        layout.addWidget(tabs)

        # ---- Actions ----
        act = QHBoxLayout()
        self.refine_box = QLineEdit()
        self.refine_box.setPlaceholderText("Search within results...")
        act.addWidget(self.refine_box)
        refine_btn = QPushButton("Refine Search")
        refine_btn.clicked.connect(self.refine_search)
        act.addWidget(refine_btn)
        export_btn = QPushButton("Export to BibTeX")
        export_btn.clicked.connect(self.export_results)
        act.addWidget(export_btn)
        layout.addLayout(act)

        # ---- Signals ----
        self.conf_slider.valueChanged.connect(
            lambda v: self.conf_label.setText(f"{v/100:.2f}"))

    # ---- Slots ----
    def start_search(self):
        query = self.query_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Input", "Enter a query")
            return
        try:
            conf = self.conf_slider.value() / 100
            start = int(self.start_year.text()) if self.start_year.text() else 1900
            end = int(self.end_year.text()) if self.end_year.text() else 2100
            use_full = self.use_full.isChecked()
            max_res = self.max_spin.value()
        except ValueError:
            QMessageBox.warning(self, "Input", "Invalid year")
            return

        self.statusBar().showMessage("Searching...")
        self.thread = SearchThread(
            self.engine,
            query=query,
            engine=self.engine_combo.currentText(),
            preset=self.preset_combo.currentText(),
            confidence_cutoff=conf,
            time_range=(start, end),
            use_full_text=use_full,
            max_results=max_res
        )
        self.thread.finished.connect(self.display_results)
        self.thread.error.connect(self.show_error)
        self.thread.start()

    def display_results(self, results):
        self.results = results
        self.statusBar().showMessage(f"Found {len(results)} results", 5000)
        self.fill_table(self.all_table, results)
        conf = self.conf_slider.value() / 100
        filt = [r for r in results if r['confidence'] >= conf]
        self.fill_table(self.filt_table, filt)
        summary = self.engine.summarize_results(
            filt, self.query_input.text(), self.use_full.isChecked())
        self.summary_text.setPlainText(summary)

    def fill_table(self, table, results):
        table.setRowCount(len(results))
        for i, r in enumerate(results):
            table.setItem(i, 0, QTableWidgetItem(r['title'][:120]))
            table.setItem(i, 1, QTableWidgetItem(r['source']))
            table.setItem(i, 2, QTableWidgetItem(str(r['year'])))
            table.setItem(i, 3, QTableWidgetItem(f"{r['confidence']:.3f}"))
            table.setItem(i, 4, QTableWidgetItem(r['url'][:100]))
            pdf_item = QTableWidgetItem("Available" if r.get('pdf_url') else "N/A")
            pdf_item.setFlags(pdf_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(i, 5, pdf_item)
            preview = (r['content'][:200] + "…") if r['content'] else ""
            table.setItem(i, 6, QTableWidgetItem(preview))
        table.sortItems(3, Qt.DescendingOrder)

    def refine_search(self):
        q = self.refine_box.text().strip()
        if not q:
            QMessageBox.warning(self, "Input", "Enter refinement query")
            return
        use_full = self.use_full.isChecked()
        refined = self.engine.search_within_results(self.results, q, use_full)
        conf = self.conf_slider.value() / 100
        filt = [r for r in refined if r['confidence'] >= conf]
        self.fill_table(self.all_table, refined)
        self.fill_table(self.filt_table, filt)
        summary = self.engine.summarize_results(filt, q, use_full)
        self.summary_text.setPlainText(summary)

    def export_results(self):
        if not self.results:
            QMessageBox.warning(self, "Export", "No results")
            return
        conf = self.conf_slider.value() / 100
        filt = [r for r in self.results if r['confidence'] >= conf]
        bib = self.engine.export_bibtex(filt)
        path, _ = QFileDialog.getSaveFileName(self, "Save BibTeX", "", "BibTeX (*.bib)")
        if path:
            if not path.endswith('.bib'):
                path += '.bib'
            open(path, 'w', encoding='utf-8').write(bib)
            QMessageBox.information(self, "Export", "Saved to " + path)

    def show_error(self, msg):
        self.statusBar().showMessage("Error: " + msg, 10000)
        QMessageBox.critical(self, "Search Error", msg)

# ========== Run ==========
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SearchApp()
    win.show()
    sys.exit(app.exec_())