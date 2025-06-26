# ===================================================================================
#  AI MetaEmbedder Pro - The Definitive Edition
#  A professional desktop application for generating and managing
#  stock photography metadata using AI.
#
#  Features:
#  - AI-powered Title, Tag, and Description generation via Gemini.
#  - Robust metadata embedding for JPG, PNG, and SVG files.
#  - Manual metadata editing and single-file embedding.
#  - Multi-format CSV export for major stock sites (Adobe, Shutterstock, etc.).
#  - Stable, non-blocking UI with background processing.
#  - Dark/Light theme support.
# ===================================================================================

import sys
import os
import json
import csv
import re
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog,
    QProgressBar, QSlider, QGroupBox, QListWidget,
    QMessageBox, QComboBox, QDialog, QDialogButtonBox, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon

# --- APPLICATION STYLING ---
DARK_STYLE = """
    QWidget { background-color: #2b2b2b; color: #f0f0f0; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; }
    QMainWindow, QDialog { background-color: #2b2b2b; }
    QDialog { border: 1px solid #4a4a4a; }
    QGroupBox { border: 1px solid #3c3c3c; border-radius: 5px; margin-top: 1ex; font-weight: bold; }
    QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 5px; }
    QPushButton { background-color: #4a4a4a; border: 1px solid #3c3c3c; padding: 8px; border-radius: 4px; }
    QPushButton:hover { background-color: #5a5a5a; }
    QPushButton:pressed { background-color: #6a6a6a; }
    QPushButton:disabled { background-color: #383838; color: #787878; }
    QLineEdit, QTextEdit, QListWidget, QComboBox { background-color: #3c3c3c; border: 1px solid #5a5a5a; border-radius: 4px; padding: 5px; }
    QComboBox::drop-down { border: none; } QComboBox::down-arrow { image: url(none); }
    QSlider::groove:horizontal { border: 1px solid #5a5a5a; height: 8px; background: #3c3c3c; margin: 2px 0; border-radius: 4px; }
    QSlider::handle:horizontal { background: #007ad9; border: 1px solid #005a9e; width: 18px; margin: -5px 0; border-radius: 9px; }
    QProgressBar { border: 1px solid #5a5a5a; border-radius: 4px; text-align: center; color: #f0f0f0; }
    QProgressBar::chunk { background-color: #007ad9; border-radius: 3px; }
"""

# --- WORKER THREAD FOR NON-BLOCKING API CALLS ---
class GenerationWorker(QThread):
    result_ready = pyqtSignal(str, dict)
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal()
    def __init__(self, api_key, file_paths, prompt):
        super().__init__(); self.api_key = api_key; self.file_paths = file_paths; self.prompt = prompt; self.is_running = True
    def run(self):
        try: genai.configure(api_key=self.api_key); model = genai.GenerativeModel('gemini-1.5-flash-latest')
        except Exception as e: self.error_occurred.emit(f"API Key config failed: {e}"); self.finished.emit(); return
        for i, file_path in enumerate(self.file_paths):
            if not self.is_running: break
            try:
                with Image.open(file_path) as img:
                    if img.mode != 'RGB': img = img.convert('RGB')
                    response = model.generate_content([self.prompt, img], request_options={"timeout": 120})
                clean_text = response.text.strip().replace("```json", "").replace("```", "")
                result_json = json.loads(clean_text); self.result_ready.emit(file_path, result_json)
            except Exception as e: self.error_occurred.emit(f"Failed to analyze '{os.path.basename(file_path)}':\n\n{e}")
            self.progress_updated.emit(int(((i + 1) / len(self.file_paths)) * 100))
        self.finished.emit()
    def stop(self): self.is_running = False

# --- DIALOG FOR CHOOSING CSV EXPORT FORMATS ---
class ExportDialog(QDialog):
    def __init__(self, sites, parent=None):
        super().__init__(parent); self.setWindowTitle("Select Export Formats"); self.setMinimumWidth(300); self.sites = sites
        self.checkboxes = {}; layout = QVBoxLayout(self); groupbox = QGroupBox("Choose sites to export CSV for:")
        form_layout = QVBoxLayout()
        for site in self.sites: self.checkboxes[site] = QCheckBox(site); self.checkboxes[site].setChecked(True); form_layout.addWidget(self.checkboxes[site])
        groupbox.setLayout(form_layout); layout.addWidget(groupbox); button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept); button_box.rejected.connect(self.reject); layout.addWidget(button_box)
    def get_selected_sites(self): return [site for site, checkbox in self.checkboxes.items() if checkbox.isChecked()]

# =================================================
# ---               MAIN APPLICATION            ---
# =================================================
class AIMetaEmbedderPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_key = None; self.is_dark_mode = True; self.config_file = "config.json"
        self.generation_thread = None; self.generated_data = {}
        self.CSV_FORMATS = {
            "Adobe Stock": {"headers": ["Filename", "Title", "Keywords"], "keyword_separator": "; "},
            "Shutterstock": {"headers": ["Filename", "Description", "Keywords"], "keyword_separator": ", "},
            "Getty/iStock": {"headers": ["File Name", "Caption/Description", "Title", "Keywords"], "keyword_separator": ", "},
            "Generic CSV": {"headers": ["Filename", "Title", "Description", "Keywords"], "keyword_separator": ", "}
        }
        self.init_ui(); self.load_api_key(); self.apply_theme()

    # -------------------------------------------------------------------
    # --- UI CREATION METHODS
    # -------------------------------------------------------------------
    def init_ui(self):
        self.setWindowTitle("AI MetaEmbedder Pro - The Final Version"); self.setGeometry(100, 100, 1200, 800)
        central_widget = QWidget(); self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(); left_pane_layout = QVBoxLayout()
        left_pane_layout.addWidget(self.create_file_group(), 3); left_pane_layout.addWidget(self.create_api_group(), 1)
        right_pane_layout = QVBoxLayout(); right_pane_layout.addWidget(self.create_controls_group())
        right_pane_layout.addWidget(self.create_metadata_group()); top_widget = QWidget(); top_widget.setLayout(main_layout)
        main_layout.addLayout(left_pane_layout, 1); main_layout.addLayout(right_pane_layout, 2)
        bottom_pane_layout = QVBoxLayout(); bottom_pane_layout.addLayout(self.create_action_buttons())
        bottom_pane_layout.addLayout(self.create_status_bar()); final_layout = QVBoxLayout(central_widget)
        final_layout.addWidget(top_widget); final_layout.addLayout(bottom_pane_layout)

    def create_action_buttons(self):
        layout = QHBoxLayout()
        self.generate_button = QPushButton("🚀 Generate All"); self.generate_button.setToolTip("Generate metadata for all listed files using AI")
        self.generate_button.setStyleSheet("background-color: #007AD9; font-weight: bold; color: white;"); self.generate_button.clicked.connect(self.start_generation)
        self.embed_all_button = QPushButton("🖼️ Embed All"); self.embed_all_button.setToolTip("Embed the generated metadata into all supported files (JPG, PNG, SVG)")
        self.embed_all_button.clicked.connect(self.embed_metadata_all)
        self.embed_selected_button = QPushButton("✍️ Embed for Selected"); self.embed_selected_button.setToolTip("Embed the text you manually entered on the right into the single selected file")
        self.embed_selected_button.clicked.connect(self.embed_metadata_for_selected)
        self.export_csv_button = QPushButton("💾 Export for Stock Sites..."); self.export_csv_button.setToolTip("Export CSV files for all listed files")
        self.export_csv_button.clicked.connect(self.open_export_dialog)
        self.embed_all_button.setEnabled(False); self.export_csv_button.setEnabled(False); self.embed_selected_button.setEnabled(False)
        layout.addWidget(self.generate_button, 2); layout.addWidget(self.embed_all_button, 1)
        layout.addWidget(self.embed_selected_button, 1); layout.addWidget(self.export_csv_button, 1); return layout
        
    def create_file_group(self):
        group = QGroupBox("📁 File Selection"); layout = QVBoxLayout(); button_layout = QHBoxLayout()
        self.select_files_button = QPushButton("Select Files"); self.select_files_button.clicked.connect(self.select_files)
        self.clear_list_button = QPushButton("Clear List"); self.clear_list_button.clicked.connect(self.clear_file_list)
        button_layout.addWidget(self.select_files_button); button_layout.addWidget(self.clear_list_button)
        self.file_list_widget = QListWidget(); self.file_list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addLayout(button_layout); layout.addWidget(self.file_list_widget); group.setLayout(layout); return group
        
    def create_api_group(self):
        group = QGroupBox("🔐 API Configuration"); layout = QVBoxLayout(); hbox = QHBoxLayout()
        self.api_key_input = QLineEdit(); self.api_key_input.setPlaceholderText("Enter your Gemini API Key..."); self.api_key_input.setEchoMode(QLineEdit.Password)
        self.validate_save_button = QPushButton("Validate & Save"); self.validate_save_button.clicked.connect(self.validate_and_save_api_key); hbox.addWidget(self.api_key_input)
        hbox.addWidget(self.validate_save_button); self.api_status_label = QLabel("Status: Not Validated")
        self.api_status_label.setAlignment(Qt.AlignCenter); layout.addLayout(hbox); layout.addWidget(self.api_status_label); group.setLayout(layout); return group

    def create_controls_group(self):
        group = QGroupBox("⚙️ Generation & Embedding Controls"); layout = QVBoxLayout()
        self.title_slider = self.create_slider(layout, "Title Words:", 5, 20); self.desc_slider = self.create_slider(layout, "Description Words:", 20, 100)
        self.tags_slider = self.create_slider(layout, "Number of Tags:", 10, 50); rating_layout = QHBoxLayout()
        rating_layout.addWidget(QLabel("Star Rating:")); self.rating_combo = QComboBox()
        self.rating_combo.addItems(["No Rating", "⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]); self.rating_combo.setCurrentIndex(5)
        rating_layout.addWidget(self.rating_combo); layout.addLayout(rating_layout)
        layout.addWidget(QLabel("Negative/Excluded Words (comma-separated):")); self.neg_words_input = QLineEdit()
        self.neg_words_input.setPlaceholderText("e.g., text, blur, ugly, signature"); layout.addWidget(self.neg_words_input); group.setLayout(layout); return group
        
    def create_metadata_group(self):
        group = QGroupBox("📝 Metadata Editor"); layout = QVBoxLayout(); self.title_output = QTextEdit(); self.title_output.setPlaceholderText("Title appears here...")
        self.tags_output = QTextEdit(); self.tags_output.setPlaceholderText("Tags appear here, comma-separated..."); self.desc_output = QTextEdit()
        self.desc_output.setPlaceholderText("Description appears here..."); layout.addWidget(QLabel("Title:")); layout.addWidget(self.title_output, 1)
        layout.addWidget(QLabel("Tags/Keywords:")); layout.addWidget(self.tags_output, 1); layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.desc_output, 2); group.setLayout(layout); return group

    def create_status_bar(self):
        layout = QHBoxLayout(); self.progress_bar = QProgressBar(); self.stats_label = QLabel("Ready")
        self.theme_toggle_button = QPushButton("☀️"); self.theme_toggle_button.setFixedWidth(40); self.theme_toggle_button.setToolTip("Toggle Dark/Light Theme")
        self.theme_toggle_button.clicked.connect(self.toggle_theme); layout.addWidget(self.progress_bar, 1); layout.addWidget(self.stats_label)
        layout.addWidget(self.theme_toggle_button); return layout
        
    def create_slider(self, layout, text, min_val, max_val):
        h_layout = QHBoxLayout(); label = QLabel(text); slider = QSlider(Qt.Horizontal); slider.setRange(min_val, max_val)
        value_label = QLabel(f"{slider.value()}"); slider.valueChanged.connect(lambda val, lbl=value_label: lbl.setText(str(val)))
        h_layout.addWidget(label, 1); h_layout.addWidget(slider, 3); h_layout.addWidget(value_label, 0); layout.addLayout(h_layout)
        slider.setValue((min_val + max_val) // 2); return slider

    # -------------------------------------------------------------------
    # --- CORE LOGIC & WORKFLOWS
    # -------------------------------------------------------------------
    def embed_metadata_for_selected(self):
        selected_items = self.file_list_widget.selectedItems()
        if not selected_items: QMessageBox.warning(self, "No File Selected", "Please select a single file from the list to embed manual data."); return
        file_path = selected_items[0].text()
        manual_data = {
            "title": self.title_output.toPlainText(),
            "tags": [tag.strip() for tag in self.tags_output.toPlainText().split(',') if tag.strip()],
            "description": self.desc_output.toPlainText()
        }
        if not any(manual_data.values()): QMessageBox.warning(self, "No Data Entered", "Please enter a title, tags, or description."); return
        self.process_embedding([file_path], {file_path: manual_data})

    def embed_metadata_all(self):
        if not self.generated_data: QMessageBox.warning(self, "No Generated Data", "Please use 'Generate All' first."); return
        self.process_embedding(list(self.generated_data.keys()), self.generated_data)

    def process_embedding(self, file_paths, data_source):
        reply = QMessageBox.question(self, "Confirm Embedding", f"This will attempt to modify {len(file_paths)} files.\n(Note: Only JPG, PNG, and SVG are supported for embedding).", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No: return
        success_count, fail_count, skipped_count = 0, 0, 0
        rating = self.rating_combo.currentIndex()
        for file_path in file_paths:
            data = data_source.get(file_path)
            if not data: continue
            try:
                title = data.get("title", ""); tags = data.get("tags", []); description = data.get("description", "")
                ext = os.path.splitext(file_path)[1].lower()
                if ext in ['.jpg', '.jpeg']:
                    img = Image.open(file_path)
                    try: exif_bytes = img.info['exif']; exif_dict = piexif.load(exif_bytes)
                    except (KeyError, ValueError): exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
                    exif_dict["0th"][piexif.ImageIFD.ImageDescription] = description.encode('utf-8')
                    exif_dict["0th"][piexif.ImageIFD.XPTitle] = title.encode('utf-16le')
                    exif_dict["0th"][piexif.ImageIFD.XPKeywords] = (";".join(tags) + '\0').encode('utf-16le')
                    if rating > 0: exif_dict["0th"][piexif.ImageIFD.Rating] = rating
                    else:
                        if piexif.ImageIFD.Rating in exif_dict["0th"]: del exif_dict["0th"][piexif.ImageIFD.Rating]
                    new_exif_bytes = piexif.dump(exif_dict); img.save(file_path, "jpeg", exif=new_exif_bytes); success_count += 1
                elif ext == '.png':
                    with Image.open(file_path) as img:
                        png_info = PngInfo(); png_info.add_text("Title", title); png_info.add_text("Description", description)
                        png_info.add_text("Keywords", ", ".join(tags))
                        if rating > 0: png_info.add_text("Rating", str(rating))
                        img.save(file_path, "PNG", pnginfo=png_info)
                    success_count += 1
                elif ext == '.svg':
                    ET.register_namespace('', "http://www.w3.org/2000/svg"); ET.register_namespace('rdf', "http://www.w3.org/1999/02/22-rdf-syntax-ns#"); ET.register_namespace('dc', "http://purl.org/dc/elements/1.1/")
                    tree = ET.parse(file_path); root = tree.getroot()
                    for md in root.findall('{http://www.w3.org/2000/svg}metadata'): root.remove(md)
                    metadata_el = ET.Element('metadata'); rdf_el = ET.SubElement(metadata_el, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF')
                    work_el = ET.SubElement(rdf_el, '{http://purl.org/dc/elements/1.1/}Work')
                    ET.SubElement(work_el, '{http://purl.org/dc/elements/1.1/}title').text = title; ET.SubElement(work_el, '{http://purl.org/dc/elements/1.1/}description').text = description
                    subject_el = ET.SubElement(work_el, '{http://purl.org/dc/elements/1.1/}subject'); bag_el = ET.SubElement(subject_el, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag')
                    for tag in tags: ET.SubElement(bag_el, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li').text = tag
                    root.insert(0, metadata_el); tree.write(file_path, encoding='utf-8', xml_declaration=True); success_count += 1
                else: skipped_count += 1
            except Exception as e: print(f"ERROR embedding {os.path.basename(file_path)}: {e}"); fail_count += 1
        QMessageBox.information(self, "Embedding Complete", f"Successfully embedded: {success_count} files.\nSkipped (unsupported format): {skipped_count} files.\nFailed: {fail_count} files.")

    # -------------------------------------------------------------------
    # --- EVENT HANDLERS & STATE MANAGEMENT
    # -------------------------------------------------------------------
    def on_selection_changed(self):
        self.embed_selected_button.setEnabled(len(self.file_list_widget.selectedItems()) == 1)
        selected_items = self.file_list_widget.selectedItems()
        if len(selected_items) == 1: self.display_metadata_for_file(selected_items[0].text())
        
    def display_metadata_for_file(self, file_path):
        data = self.generated_data.get(file_path)
        if data: self.title_output.setText(data.get("title", "")); self.tags_output.setText(", ".join(data.get("tags", []))); self.desc_output.setText(data.get("description", ""))
        else: self.title_output.clear(); self.tags_output.clear(); self.desc_output.clear()

    def select_files(self):
        file_filter = "All Supported Files (*.jpg *.jpeg *.png *.svg *.eps *.ai *.psd);;Images (*.jpg *.jpeg *.png);;Vectors (*.svg *.eps *.ai);;Photoshop (*.psd)"
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", file_filter)
        if files:
            self.file_list_widget.addItems(files); self.stats_label.setText(f"Total files: {self.file_list_widget.count()}")
            self.reset_state_for_new_files()

    def clear_file_list(self):
        self.file_list_widget.clear(); self.reset_state_for_new_files()
        self.stats_label.setText("Ready")
        
    def reset_state_for_new_files(self):
        self.generated_data.clear(); self.embed_all_button.setEnabled(False); self.export_csv_button.setEnabled(False)
        self.embed_selected_button.setEnabled(False); self.title_output.clear(); self.tags_output.clear()
        self.desc_output.clear(); self.progress_bar.setValue(0)

    def on_generation_complete(self):
        self.generate_button.setText("🚀 Generate All"); success_count = len(self.generated_data); total_count = self.file_list_widget.count()
        self.stats_label.setText(f"Completed: {success_count}/{total_count} files processed.")
        if self.generated_data: self.embed_all_button.setEnabled(True); self.export_csv_button.setEnabled(True)

    def handle_result(self, file_path, data):
        title = data.get("title", ""); cleaned_title = re.sub(r'[^\w\s.,-]', '', title).strip(); data['title'] = cleaned_title
        self.generated_data[file_path] = data

    def start_generation(self):
        if self.generation_thread and self.generation_thread.isRunning(): self.generation_thread.stop(); self.generate_button.setText("🚀 Generate All"); return
        if not self.api_key: QMessageBox.warning(self, "API Key Required", "Please validate and save your Gemini API key first."); return
        file_paths = [self.file_list_widget.item(i).text() for i in range(self.file_list_widget.count())]
        if not file_paths: QMessageBox.warning(self, "No Files", "Please select some image files first."); return
        self.reset_state_for_new_files()
        prompt = self.build_prompt(); self.generate_button.setText("⏹️ Stop Generation"); self.stats_label.setText("Processing...");
        self.generation_thread = GenerationWorker(self.api_key, file_paths, prompt); self.generation_thread.result_ready.connect(self.handle_result)
        self.generation_thread.error_occurred.connect(self.handle_error); self.generation_thread.progress_updated.connect(self.update_progress)
        self.generation_thread.finished.connect(self.on_generation_complete); self.generation_thread.start()

    def build_prompt(self):
        title_words = self.title_slider.value(); desc_words = self.desc_slider.value(); tag_count = self.tags_slider.value(); neg_words = self.neg_words_input.text()
        return f"""Analyze the image for a stock photography website. Your response MUST be a single, valid JSON object. JSON structure: {{"title": "string", "tags": ["string"], "description": "string"}}. Constraints: 1. `title`: ~{title_words} words. The title must NOT contain any special symbols like ©, ™, ®, _, *, or emojis. 2. `tags`: JSON array of exactly {tag_count} relevant, lowercase keywords. 3. `description`: ~{desc_words} words. 4. Exclusions: Do not use these concepts: {neg_words if neg_words else "None"}."""

    def open_export_dialog(self):
        if not self.generated_data: QMessageBox.warning(self, "No Data", "Please generate metadata before exporting."); return
        dialog = ExportDialog(self.CSV_FORMATS.keys(), self)
        if dialog.exec_() == QDialog.Accepted:
            if selected_sites := dialog.get_selected_sites(): self.execute_export(selected_sites)

    def execute_export(self, selected_sites):
        save_directory = QFileDialog.getExistingDirectory(self, "Select Directory to Save CSV Files");
        if not save_directory: return
        exported_files = []
        for site in selected_sites:
            format_info = self.CSV_FORMATS[site]; file_name = f"export_{site.replace(' ', '_').replace('/', '_').lower()}.csv"
            file_path = os.path.join(save_directory, file_name)
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile); writer.writerow(format_info["headers"])
                # To handle cases where metadata wasn't generated for all files
                for i in range(self.file_list_widget.count()):
                    img_path = self.file_list_widget.item(i).text()
                    data = self.generated_data.get(img_path, {}) # Get data or an empty dict
                    filename = os.path.basename(img_path); title = data.get('title', ''); description = data.get('description', '')
                    keywords = format_info["keyword_separator"].join(data.get('tags', []))
                    if site == "Adobe Stock": row = [filename, title, keywords]
                    elif site == "Shutterstock": row = [filename, description, keywords]
                    elif site == "Getty/iStock": row = [filename, description, title, keywords]
                    else: row = [filename, title, description, keywords]
                    writer.writerow(row)
            exported_files.append(file_name)
        QMessageBox.information(self, "Export Successful", f"Successfully exported:\n\n" + "\n".join(exported_files) + f"\n\nTo directory:\n{save_directory}")

    # -------------------------------------------------------------------
    # --- HELPER & UTILITY METHODS
    # -------------------------------------------------------------------
    def load_api_key(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f: config = json.load(f); key = config.get("api_key")
                if key: self.api_key = key; self.api_key_input.setText(key); self.validate_key_silently()
            except Exception: self.api_status_label.setText("Status: Error loading key"); self.api_status_label.setStyleSheet("color: #FF5733;")
    def save_api_key(self, key):
        with open(self.config_file, 'w') as f: json.dump({"api_key": key}, f)
    def validate_key_silently(self):
        self.api_status_label.setText("Status: Validating...");
        try: genai.configure(api_key=self.api_key); genai.GenerativeModel('gemini-1.5-flash-latest').count_tokens("validate"); self.api_status_label.setText("Status: Validated ✅"); self.api_status_label.setStyleSheet("color: #33FF99;")
        except Exception: self.api_key = None; self.api_status_label.setText("Status: Invalid Key ❌"); self.api_status_label.setStyleSheet("color: #FF5733;")
    def validate_and_save_api_key(self):
        key = self.api_key_input.text().strip();
        if not key: QMessageBox.warning(self, "API Key Missing", "Please enter an API key."); return
        self.api_key = key
        try:
            genai.configure(api_key=self.api_key); genai.GenerativeModel('gemini-1.5-flash-latest').count_tokens("validate"); self.save_api_key(self.api_key)
            self.api_status_label.setText("Status: Validated & Saved ✅"); self.api_status_label.setStyleSheet("color: #33FF99;"); QMessageBox.information(self, "Success", "API Key has been validated and saved!")
        except Exception as e: self.api_key = None; self.api_status_label.setText("Status: Invalid Key ❌"); self.api_status_label.setStyleSheet("color: #FF5733;"); QMessageBox.critical(self, "Validation Failed", f"The API key is invalid or a network error occurred.\n\nError: {e}")
    def update_progress(self, value): self.progress_bar.setValue(value); total = self.file_list_widget.count(); processed = int(total * (value / 100)); self.stats_label.setText(f"Processing: {processed}/{total}")
    def handle_error(self, error_message): QMessageBox.critical(self, "Generation Error", f"An error occurred:\n\n{error_message}"); self.on_generation_complete()
    def toggle_theme(self): self.is_dark_mode = not self.is_dark_mode; self.apply_theme()
    def apply_theme(self):
        self.setStyleSheet(DARK_STYLE if self.is_dark_mode else ""); self.theme_toggle_button.setText("☀️" if self.is_dark_mode else "🌙")
        if self.is_dark_mode or not self.is_dark_mode: self.generate_button.setStyleSheet("background-color: #007AD9; font-weight: bold; color: white;")
    def closeEvent(self, event):
        if self.generation_thread and self.generation_thread.isRunning(): self.generation_thread.stop(); self.generation_thread.wait()
        event.accept()

# --- APPLICATION ENTRY POINT ---
if __name__ == '__main__':
    if hasattr(Qt, 'AA_EnableHighDpiScaling'): QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'): QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    window = AIMetaEmbedderPro()
    window.show()
    sys.exit(app.exec_())