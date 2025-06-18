#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import mmap
import configparser
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Tuple

# --- Third-party libraries ---
try:
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QTimer, QEasingCurve, QPropertyAnimation, QRect, QSize, QVariantAnimation, QSequentialAnimationGroup
    from PyQt6.QtGui import QIcon, QAction, QDragEnterEvent, QDropEvent, QDesktopServices, QFont, QDragLeaveEvent, QColor
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QListWidget, QListWidgetItem, QLineEdit, QLabel, QProgressBar,
        QTextEdit, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
        QDialog, QComboBox, QCheckBox, QGroupBox, QFrame, QDialogButtonBox,
        QTabWidget, QScrollArea # Imported for the new tabbed interface and scrollable settings
    )
    import google.generativeai as genai
except ImportError as e:
    # If PyQt6 or google.generativeai is not installed, inform the user and exit.
    print(f"Error: Missing required library. Please install it.\n{e}")
    sys.exit(1)


# --- Configuration & Globals ——————————————————————————————————————————

# Determine the script's directory, essential for relative pathing of config files.
# This handles both frozen applications (e.g., PyInstaller) and direct script execution.
if getattr(sys, 'frozen', False):
    SCRIPT_DIR = Path(sys.executable).parent
else:
    SCRIPT_DIR = Path(__file__).parent

INI_PATH = SCRIPT_DIR / "config.ini" # Path to the configuration INI file

# Default configuration settings. These are used if the config file doesn't exist
# or if new settings are introduced that aren't yet in the user's config.
CFG_DEF = {
    "General": {
        "result_dir": str(SCRIPT_DIR / "Results"), # Default directory for output results
        "encoding": "utf-8",                       # Default encoding for log files
        "theme": "dark",                           # Default UI theme (dark, light, system)
        "regex_mode": "false"                      # Whether keywords are treated as regex
    },
    "Keywords": {
        # This section will store user-defined keywords, persisting them across sessions.
        # It's initially empty and populated/updated by the application.
    },
    "Gemini": {
        "api_key": "YOUR_GEMINI_API_KEY_HERE",    # Placeholder for the Gemini API key
        "model": "gemini-1.5-flash-latest",       # Default Gemini AI model
        # Customizable prompts for various AI functionalities:
        "prompt_suggest_keywords": "Analyze the following log sample. Suggest single-word or hyphenated keywords (e.g., 'api-key') for finding credentials or tokens. List only keywords, one per line, no explanation.\n\n---\n{log_sample}",
        "prompt_summarize_results": "Summarize the following log extraction output concisely, focusing on frequent keywords and patterns. Highlight critical findings if any.\n\n---\n\n{log_content}",
        "prompt_detect_anomalies": "As a cybersecurity analyst, analyze the following log summary for anomalies, suspicious patterns, or high-risk findings. Present a concise report.\n\n---\n{log_content}",
        "prompt_analyze_credentials": "As a credential security analyst, analyze the following log data. Extract only credentials for high-value services (banking, email, dev platforms, cloud). Discard low-value ones (forums, games). Format as a clean 'user:password' list, one per line.\n\n---\n\n{log_content}"
    }
}

def load_cfg() -> configparser.ConfigParser:
    """
    Loads configuration settings from the INI file. If the file doesn't exist,
    or if sections/keys are missing, it initializes with default values and
    writes them back to the file to ensure a complete and up-to-date config.
    """
    cfg = configparser.ConfigParser()
    cfg.read_dict(CFG_DEF)  # Load defaults first to ensure all keys are present
    if INI_PATH.exists():
        cfg.read(INI_PATH, encoding="utf-8")  # Override with existing settings if file exists
    
    # Ensure all sections and keys from CFG_DEF are present in the loaded config
    # and write back to file to update with any new defaults or missing sections.
    with open(INI_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)
    return cfg

# Load initial configuration settings into global variables for easy access.
cfg_global = load_cfg()
ENC_GLOBAL = cfg_global["General"]["encoding"]
RESULTS_GLOBAL = Path(cfg_global["General"]["result_dir"])
RESULTS_GLOBAL.mkdir(exist_ok=True)  # Create the results directory if it doesn't exist
THEME_GLOBAL = cfg_global["General"].get("theme", "dark")
REGEX_MODE_GLOBAL = cfg_global["General"].getboolean("regex_mode", False)
GEMINI_API_KEY_GLOBAL = cfg_global["Gemini"].get("api_key", "YOUR_GEMINI_API_KEY_HERE")
GEMINI_MODEL_GLOBAL = cfg_global["Gemini"].get("model", "gemini-1.5-flash-latest")

# Load AI prompts from the configuration, falling back to defaults if not found.
PROMPT_SUGGEST_KEYWORDS_GLOBAL = cfg_global["Gemini"].get("prompt_suggest_keywords", CFG_DEF["Gemini"]["prompt_suggest_keywords"])
PROMPT_SUMMARIZE_RESULTS_GLOBAL = cfg_global["Gemini"].get("prompt_summarize_results", CFG_DEF["Gemini"]["prompt_summarize_results"])
PROMPT_DETECT_ANOMALIES_GLOBAL = cfg_global["Gemini"].get("prompt_detect_anomalies", CFG_DEF["Gemini"]["prompt_detect_anomalies"])
PROMPT_ANALYZE_CREDENTIALS_GLOBAL = cfg_global["Gemini"].get("prompt_analyze_credentials", CFG_DEF["Gemini"]["prompt_analyze_credentials"])


# Translation Dictionary (T) for all UI text and messages.
# This centralizes text for easier localization and consistency.
T = {
    "title": "Logs Combo Extractor Pro", "file_menu": "File", "add": "➕ Add Logs...", "remove": "❌ Remove",
    "enter_kw": "🔑 Enter keyword...", "add_kw": "➕ Add", "remove_kw": "❌ Remove", "import_kw": "📥 Import...",
    "export_kw": "📤 Export...", "start": "▶️ Start", "cancel": "⏹ Stop", "open": "📂 Open Results",
    "status": "Status:", "ready": "Ready", "no_files": "Please add at least one log file.",
    "no_keywords": "Please add at least one keyword.", "processing": "Processing {i}/{n}: {name}",
    "file_prog": "Files", "line_prog": "Lines", "matches": "Matches", "complete": "All done!", "saved": "✅ Saved → {path}",
    "total": "Total", "canceled": "Processing canceled.", "no_results_dir": "Results directory not found!",
    "kw_stats": "Keywords: {count}", "match_stats": "Total matches: {count}", "file_size": "Size: {size}",
    "kw_column": "Keyword", "matches_column": "Matches", "clear_all": "🗑️ Clear All", "settings": "⚙️ Settings",
    "export_results": "💾 Export Results", "filter": "🔍 Filter keywords...", "settings_title": "Application Settings",
    "results_dir_label": "Results Output Directory:", "browse": "Browse...", "encoding_label": "Log File Encoding:",
    "theme_label": "UI Theme:", "regex_mode_label": "Enable Regex Mode for Keywords",
    "save_settings": "Save Settings", "cancel_settings": "Cancel",
    "settings_saved_message": "Settings saved successfully!", "drag_drop_files": "Drag & Drop log files here",
    "ai_features_title": "✨ AI-Powered Features ✨", "ai_suggest_keywords": "💡 Suggest Keywords",
    "ai_summarize_results": "📚 Summarize Results", "ai_detect_anomalies": "🚨 Detect Anomalies",
    "gemini_api_key_label": "Gemini API Key:", "gemini_api_key_group": "Gemini AI Settings",
    "gemini_model_label": "AI Model:", "gemini_model_tooltip": "Flash is faster and cheaper. Pro is more powerful.",
    "gemini_api_cost_warning": "Note: Using the AI API may incur costs from Google.",
    "api_key_missing_title": "API Key Required",
    "api_key_missing_message": "Please set your Gemini API key in 'File > Settings' to use this feature.",
    "ai_query_status": "Querying Gemini AI... Please wait.", "ai_summary_log_header": "\n\n--- ✨ AI Summary ✨ ---\n",
    "ai_anomaly_log_header": "\n\n--- 🚨 AI Anomaly Detection Report 🚨 ---\n",
    "ai_analysis_log_header": "\n\n--- 🛡️ AI High-Value Credential Analysis 🛡️ ---\n",
    "ai_error_title": "AI Service Error", "no_logs_to_analyze": "No log messages to analyze. Please run a process first.",
    "no_files_for_suggestions": "Please add log files before asking for keyword suggestions.",
    "suggestions_dialog_title": "AI Keyword Suggestions", "add_selected_keywords": "Add Selected",
    "select_all": "Select All", "deselect_all": "Deselect All", "ai_analysis_title": "🛡️ Post-Scan Analysis (AI)",
    "ai_analyze_credentials": "Analyze Credentials", "file_error": "❗️ Error processing file {name}: {error}",
    "invalid_regex": "Invalid Regex: '{keyword}' - {error}. Please correct or disable Regex Mode.",
    "ai_prompt_settings_group": "AI Prompt Templates",
    "ai_prompt_suggest_keywords_label": "Suggest Keywords Prompt:",
    "ai_prompt_summarize_results_label": "Summarize Results Prompt:",
    "ai_prompt_detect_anomalies_label": "Detect Anomalies Prompt:",
    "ai_prompt_analyze_credentials_label": "Analyze Credentials Prompt:",
    "tab_main": "Extractor",
    "tab_settings": "Settings"
}

# Pre-compiled Regular Expressions for performance
GUID_RE = re.compile(r"^[0-9A-Fa-f]{32,}$")
STRIP_RE = re.compile(r"^[\W_]+|[\W_]+$")
EMAIL_RE = re.compile(r"^[\w\.\-]+@[\w\.\-]+\.\w{2,}$")


# --- Worker Threads & Dialogs ——————————————————————————————————————

class ExtractThread(QThread):
    """
    Performs data extraction in a worker thread. Includes file-level error handling and regex support.
    This thread is designed to run long-running file processing tasks without freezing the UI,
    emiting signals to update the main application's progress and results in real-time.
    """
    # Signals for UI updates and status reporting
    sig_status = pyqtSignal(str)        # Current processing status message
    sig_file_prog = pyqtSignal(int)     # Overall file processing progress (0-100%)
    sig_line_prog = pyqtSignal(int)     # Progress within the current file (0-100%)
    sig_dist = pyqtSignal(dict)         # Dictionary of keyword match counts
    sig_log = pyqtSignal(str)           # Messages to append to the log output area
    sig_error = pyqtSignal(str)         # Signal for file-specific errors, allowing processing to continue
    sig_done = pyqtSignal()             # Signal indicating the completion of all processing

    def __init__(self, files: List[str], keywords: List[str], regex_mode: bool):
        super().__init__()
        self.files = files
        self.keywords = keywords
        self.regex_mode = regex_mode
        self._cancel = False # Flag to signal cancellation to the thread
        self.compiled_keywords: List[Tuple[str, Optional[re.Pattern]]] = [] # Stores compiled regex patterns

        # Compile regex patterns if in regex mode for efficiency.
        # If any regex is invalid, an error is emitted, and processing is cancelled.
        if self.regex_mode:
            for kw in self.keywords:
                try:
                    self.compiled_keywords.append((kw, re.compile(kw)))
                except re.error as e:
                    self.sig_error.emit(T["invalid_regex"].format(keyword=kw, error=e))
                    self._cancel = True # Immediately cancel if a regex is invalid
                    return
        else:
            # If not in regex mode, store keywords as-is with no compiled pattern.
            self.compiled_keywords = [(kw, None) for kw in self.keywords]

    def cancel(self):
        """Sets the internal flag to indicate that the extraction process should be cancelled."""
        self._cancel = True

    def run(self):
        """
        The main execution loop for the thread. Iterates through the list of files,
        processes each one, and updates the UI via signals.
        """
        if self._cancel: # If regex compilation failed during initialization, just exit.
            self.sig_done.emit()
            return

        total_files = len(self.files)
        for i, filepath_str in enumerate(self.files, 1):
            if self._cancel: # Check cancellation flag before processing each file
                break
            filepath = Path(filepath_str)
            try:
                # Update UI status to show the currently processing file.
                self.sig_status.emit(T["processing"].format(i=i, n=total_files, name=filepath.name))
                outdir = RESULTS_GLOBAL / f"{filepath.stem}_{datetime.now():%Y%m%d_%H%M%S}"
                outdir.mkdir(exist_ok=True) # Create a unique output directory for this file's results
                self._process_file(filepath, outdir) # Process the individual file
                if not self._cancel:
                    self.sig_log.emit(T["saved"].format(path=outdir)) # Log successful saving
            except Exception as e:
                # Emit a specific error signal if a file processing fails, then continue to the next file.
                self.sig_error.emit(T["file_error"].format(name=filepath.name, error=e))
                continue  # Continue processing other files even if one fails
            finally:
                # Always update the file progress bar after each file, regardless of success/failure.
                self.sig_file_prog.emit(int(i / total_files * 100))
        self.sig_done.emit() # Signal that all files have been processed (or cancelled)

    def _process_file(self, infile: Path, outdir: Path):
        """
        Processes a single log file. It reads the file line by line, searches for keywords,
        cleans potential credentials, and writes them to separate output files per keyword.
        Uses `mmap` for efficient file reading if supported, falling back to standard file I/O.
        """
        # Open an output file for each keyword in 'append' mode within the specific output directory.
        writers = {kw: open(outdir / (re.sub(r"[^\w]", "", kw) + ".txt"), "a", encoding=ENC_GLOBAL) for kw, _ in self.compiled_keywords}
        dist = {kw: 0 for kw, _ in self.compiled_keywords} # Dictionary to store match counts per keyword
        
        size = infile.stat().st_size # Total size of the input file in bytes
        processed, last_update = 0, 0
        # Calculate an update interval to throttle UI updates for better performance on large files.
        update_interval = max(size // 100, 10_000_000)  # Update progress at least every 10MB or 1% of file size
        buffer: List[Tuple[str, str]] = []  # A buffer to accumulate credentials for batch writing to disk
        
        mm = None # Initialize mmap variable
        try:
            with open(infile, "rb") as f:
                try:
                    # Attempt to use mmap for highly efficient file reading.
                    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                    lines_iter = iter(mm.readline, b"") # Iterator for reading lines from mmap
                except (ValueError, OSError):
                    # Fallback to standard file reading if mmap fails (e.g., very small files or unsupported file systems).
                    mm = None
                    lines_iter = (line.encode(ENC_GLOBAL, errors="ignore") for line in open(infile, "r", encoding=ENC_GLOBAL, errors="ignore"))

                for raw_line in lines_iter:
                    if self._cancel: # Check cancellation flag after processing each line
                        break
                    processed += len(raw_line) # Keep track of total bytes processed
                    try:
                        line = raw_line.decode(ENC_GLOBAL, errors="ignore").strip() # Decode and strip whitespace
                    except UnicodeDecodeError:
                        continue  # Skip lines that cannot be decoded with the specified encoding
                    
                    if len(line) > 5:  # Filter out very short lines as likely irrelevant for credentials
                        lw = line.lower() # Lowercase version of the line for case-insensitive substring matching
                        for original_kw, compiled_re in self.compiled_keywords:
                            match = False
                            if self.regex_mode and compiled_re:
                                if compiled_re.search(line): # In regex mode, search using the compiled regex on the original line
                                    match = True
                            elif not self.regex_mode and original_kw.lower() in lw: # In simple mode, check for substring match (case-insensitive)
                                match = True
                            
                            if match:
                                if cred := self._clean(line): # Attempt to clean and validate the extracted credential
                                    buffer.append((original_kw, cred)) # Add to buffer for batch writing
                                    dist[original_kw] += 1 # Increment match count for the keyword
                                break  # Keyword found in this line, no need to check other keywords for this line
                    
                    if len(buffer) >= 1000:  # Write accumulated credentials to disk in batches of 1000 lines
                        for kw, c in buffer:
                            writers[kw].write(c + "\n")
                        buffer.clear() # Clear the buffer after writing
                    
                    if processed - last_update >= update_interval:
                        # Emit signals to update the UI's line progress and keyword distribution.
                        self.sig_line_prog.emit(int(processed / size * 100) if size else 100)
                        self.sig_dist.emit(dist.copy()) # Send a copy to avoid modification issues
                        last_update = processed
        finally:
            if mm:
                mm.close()  # Ensure mmap resource is properly closed
            for kw, c in buffer:  # Write any remaining data in the buffer
                writers[kw].write(c + "\n")
            for writer in writers.values():
                writer.close()  # Close all file writers
            self.sig_line_prog.emit(100)  # Ensure line progress always reaches 100%
            self.sig_dist.emit(dist.copy())  # Send the final keyword distribution

    def _clean(self, raw_str: str) -> Optional[str]:
        """
        Cleans and performs basic validation on a potential credential string.
        It removes common prefixes and checks for minimum length, GUID patterns,
        and basic email format validity.
        """
        if ":" not in raw_str or len(raw_str) < 8:
            return None  # Discard if no colon (user:pass) or too short
        line = raw_str.replace("https://", "").replace("http://", "").replace("android://", "") # Remove common URL schemes
        parts = line.split(":", 2)  # Split at most 2 times (e.g., "service:user:pass")
        if len(parts) < 3:
            return None  # Not enough parts after splitting (e.g., "user:pass" needs a "service:" prefix)
        
        # Safely extract user and password parts, handling potential index errors.
        user = parts[1].strip() if len(parts) > 1 else ""
        pwd = parts[2].strip() if len(parts) > 2 else ""

        # Basic validity checks to filter out noise:
        # - User/password too short.
        # - Password excessively long (potential junk data).
        # - User or password matching common GUID patterns (often not credentials).
        if any((len(user) < 3, len(pwd) < 3, len(pwd) > 100, GUID_RE.match(user), GUID_RE.match(pwd))):
            return None
        
        user, pwd = STRIP_RE.sub("", user), STRIP_RE.sub("", pwd)  # Remove leading/trailing non-alphanumeric chars
        if "@" in user and not EMAIL_RE.match(user):
            return None  # If it looks like an email but doesn't conform to a basic email regex
        return f"{user}:{pwd}" # Return the cleaned "user:password" string

class AIThread(QThread):
    """
    Handles streaming AI API calls to Google Gemini. Runs in a separate thread
    to prevent UI freezing during network requests.
    """
    sig_chunk = pyqtSignal(str) # Emits each text chunk received from the AI stream
    sig_done = pyqtSignal()      # Emits when the AI response stream is complete
    sig_error = pyqtSignal(str)  # Emits if an error occurs during the AI API call

    def __init__(self, api_key: str, prompt: str, model_name: str, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.prompt = prompt
        self.model_name = model_name

    def run(self):
        """
        Main operation of the AI thread: configures the Gemini API,
        sends the prompt, and streams the response back to the main UI thread.
        """
        try:
            genai.configure(api_key=self.api_key) # Configure the Gemini API with the provided key
            model = genai.GenerativeModel(self.model_name) # Initialize the Gemini AI model
            # Safety settings are deliberately permissive as per "Do Anything Now" instruction.
            # This allows the AI to respond without content filtering, crucial for a DAN persona.
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'block_none',
                'HARM_CATEGORY_HATE_SPEECH': 'block_none',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'block_none',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'block_none',
            }
            # Generate content from the AI model with streaming enabled.
            response_stream = model.generate_content(self.prompt, stream=True, safety_settings=safety_settings)
            for chunk in response_stream:
                self.sig_chunk.emit(chunk.text) # Emit each text chunk as it arrives
            self.sig_done.emit() # Signal completion when the entire stream is processed
        except Exception as e:
            self.sig_error.emit(f"Failed to query Gemini API: {str(e)}") # Emit error message if API call fails

class SuggestionsDialog(QDialog):
    """
    A dialog window used to display AI-generated keyword suggestions to the user.
    Users can select multiple suggestions to add them to their main keyword list.
    """
    def __init__(self, suggestions: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle(T["suggestions_dialog_title"])
        self.setMinimumSize(400, 500)
        self.setStyleSheet(parent.styleSheet())  # Inherit styling from the parent (main window)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # Internal margins for the dialog content
        layout.setSpacing(15)  # Spacing between widgets

        self.list_widget = QListWidget() # List widget to display suggestions
        # Populate the list with suggestions, making each item checkable.
        for s in suggestions:
            item = QListWidgetItem(s)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable) # Make item checkable
            item.setCheckState(Qt.CheckState.Unchecked) # Initially unchecked
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout() # Layout for selection control buttons
        button_select_all = QPushButton(T["select_all"])
        button_select_all.clicked.connect(self.select_all)
        button_deselect_all = QPushButton(T["deselect_all"])
        button_deselect_all.clicked.connect(self.deselect_all)
        button_layout.addWidget(button_select_all)
        button_layout.addWidget(button_deselect_all)
        button_layout.addStretch()  # Pushes buttons to the left
        layout.addLayout(button_layout)

        # Standard dialog buttons (OK and Cancel) with custom text.
        dialog_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        dialog_buttons.button(QDialogButtonBox.StandardButton.Ok).setText(T["add_selected_keywords"])
        dialog_buttons.accepted.connect(self.accept) # Connect OK button to accept dialog
        dialog_buttons.rejected.connect(self.reject) # Connect Cancel button to reject dialog
        layout.addWidget(dialog_buttons)

    def select_all(self):
        """Checks all items in the suggestions list."""
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(Qt.CheckState.Checked)

    def deselect_all(self):
        """Unchecks all items in the suggestions list."""
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(Qt.CheckState.Unchecked)

    def get_selected(self) -> List[str]:
        """Returns a list of the text content of all currently checked (selected) keywords."""
        return [self.list_widget.item(i).text() for i in range(self.list_widget.count()) if self.list_widget.item(i).checkState() == Qt.CheckState.Checked]

class SettingsPanel(QWidget):
    """
    A dedicated panel (QWidget) to house all application settings.
    This replaces the previous SettingsDialog and is designed to be embedded
    as a tab within the main application window for a seamless user experience.
    """
    settings_saved = pyqtSignal(dict) # Signal emitted when settings are saved

    def __init__(self, config: configparser.ConfigParser, parent=None):
        super().__init__(parent)
        self.config = config
        self._setup_ui() # Setup all UI elements for the settings panel

    def _setup_ui(self):
        """
        Configures the layout and widgets for the settings panel, drawing from
        the global translation dictionary for text.
        """
        # Wrap the main layout in a QScrollArea for long settings pages
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        # Create a container widget for the actual settings content
        container_widget = QWidget()
        self.layout = QVBoxLayout(container_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)  # Internal margins
        self.layout.setSpacing(15)  # Spacing between elements

        # Set the container widget as the scroll area's widget
        scroll_area.setWidget(container_widget)
        
        # Add the scroll area to the top-level layout of the SettingsPanel
        top_level_layout = QVBoxLayout(self)
        top_level_layout.addWidget(scroll_area)


        # --- Gemini AI Settings Group ---
        gemini_group = QGroupBox(T["gemini_api_key_group"])
        gemini_group.setObjectName("settings_group_box") # Object name for QSS styling
        gemini_layout = QVBoxLayout(gemini_group)
        gemini_layout.setContentsMargins(15, 25, 15, 15)
        gemini_layout.setSpacing(10)

        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel(T["gemini_api_key_label"]))
        self.line_edit_api_key = QLineEdit(self.config["Gemini"]["api_key"])
        self.line_edit_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.line_edit_api_key.setToolTip("Enter your Google Gemini API Key here. Obtain it from Google AI Studio.")
        api_layout.addWidget(self.line_edit_api_key)
        gemini_layout.addLayout(api_layout)

        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel(T["gemini_model_label"]))
        self.combo_model = QComboBox()
        self.combo_model.addItems(["gemini-1.5-flash-latest", "gemini-1.5-pro-latest"])
        self.combo_model.setCurrentText(self.config["Gemini"]["model"])
        self.combo_model.setToolTip(T["gemini_model_tooltip"])
        model_layout.addWidget(self.combo_model)
        gemini_layout.addLayout(model_layout)
        
        cost_label = QLabel(T["gemini_api_cost_warning"])
        cost_label.setObjectName("cost_warning_label") # Specific object name for styling
        gemini_layout.addWidget(cost_label, 0, Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(gemini_group)

        # --- AI Prompt Templates Group ---
        ai_prompts_group = QGroupBox(T["ai_prompt_settings_group"])
        ai_prompts_group.setObjectName("settings_group_box")
        ai_prompts_layout = QVBoxLayout(ai_prompts_group)
        ai_prompts_layout.setContentsMargins(15, 25, 15, 15)
        ai_prompts_layout.setSpacing(10)

        # FIX: Capture the QVBoxLayout returned by _create_prompt_editor
        prompt_suggest_keywords_layout, self.prompt_suggest_keywords_editor = self._create_prompt_editor(T["ai_prompt_suggest_keywords_label"], self.config["Gemini"].get("prompt_suggest_keywords", CFG_DEF["Gemini"]["prompt_suggest_keywords"]), "Prompt for AI to suggest keywords based on log samples. Use '{log_sample}' placeholder.")
        prompt_summarize_results_layout, self.prompt_summarize_results_editor = self._create_prompt_editor(T["ai_prompt_summarize_results_label"], self.config["Gemini"].get("prompt_summarize_results", CFG_DEF["Gemini"]["prompt_summarize_results"]), "Prompt for AI to summarize extracted results. Use '{log_content}' placeholder.")
        prompt_detect_anomalies_layout, self.prompt_detect_anomalies_editor = self._create_prompt_editor(T["ai_prompt_detect_anomalies_label"], self.config["Gemini"].get("prompt_detect_anomalies", CFG_DEF["Gemini"]["prompt_detect_anomalies"]), "Prompt for AI to detect anomalies in log data. Use '{log_content}' placeholder.")
        prompt_analyze_credentials_layout, self.prompt_analyze_credentials_editor = self._create_prompt_editor(T["ai_prompt_analyze_credentials_label"], self.config["Gemini"].get("prompt_analyze_credentials", CFG_DEF["Gemini"]["prompt_analyze_credentials"]), "Prompt for AI to analyze and filter high-value credentials. Use '{log_content}' placeholder.")

        # Add the captured layouts directly
        ai_prompts_layout.addLayout(prompt_suggest_keywords_layout)
        ai_prompts_layout.addLayout(prompt_summarize_results_layout)
        ai_prompts_layout.addLayout(prompt_detect_anomalies_layout)
        ai_prompts_layout.addLayout(prompt_analyze_credentials_layout)
        self.layout.addWidget(ai_prompts_group)

        # --- General Settings Group ---
        results_group = QGroupBox(T["results_dir_label"])
        results_group.setObjectName("settings_group_box")
        results_layout = QHBoxLayout(results_group)
        results_layout.setContentsMargins(15, 25, 15, 15)
        self.line_edit_results_dir = QLineEdit(self.config["General"]["result_dir"])
        self.line_edit_results_dir.setToolTip("Select the directory where all extracted log results will be saved.")
        self.btn_browse_results = QPushButton(T["browse"])
        self.btn_browse_results.clicked.connect(self._browse_dir)
        results_layout.addWidget(self.line_edit_results_dir)
        results_layout.addWidget(self.btn_browse_results)
        self.layout.addWidget(results_group)

        encoding_group = QGroupBox(T["encoding_label"])
        encoding_group.setObjectName("settings_group_box")
        encoding_layout = QHBoxLayout(encoding_group)
        encoding_layout.setContentsMargins(15, 25, 15, 15)
        self.combo_encoding = QComboBox()
        self.combo_encoding.addItems(["utf-8", "cp1255", "latin-1", "ascii"])
        self.combo_encoding.setCurrentText(self.config["General"]["encoding"])
        self.combo_encoding.setToolTip("Select the character encoding for your log files (e.g., UTF-8, Windows-1255).")
        encoding_layout.addWidget(self.combo_encoding)
        encoding_layout.addStretch() # Push combo box to the left
        self.layout.addWidget(encoding_group)

        theme_group = QGroupBox(T["theme_label"])
        theme_group.setObjectName("settings_group_box")
        theme_layout = QHBoxLayout(theme_group)
        theme_layout.setContentsMargins(15, 25, 15, 15)
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["dark", "light", "system"])
        self.combo_theme.setCurrentText(self.config["General"]["theme"])
        self.combo_theme.setToolTip("Choose between dark, light, or system-matched UI themes.")
        theme_layout.addWidget(self.combo_theme)
        theme_layout.addStretch() # Push combo box to the left
        self.layout.addWidget(theme_group)

        regex_group = QGroupBox(T["regex_mode_label"])
        regex_group.setObjectName("settings_group_box")
        regex_layout = QHBoxLayout(regex_group)
        regex_layout.setContentsMargins(15, 25, 15, 15)
        self.checkbox_regex_mode = QCheckBox()
        self.checkbox_regex_mode.setChecked(self.config["General"].getboolean("regex_mode", False))
        self.checkbox_regex_mode.setToolTip("If enabled, keywords will be treated as Python regular expressions for powerful pattern matching.")
        regex_layout.addWidget(self.checkbox_regex_mode)
        regex_layout.addStretch()
        self.layout.addWidget(regex_group)
        
        self.layout.addStretch() # Pushes all content to the top

        # Save/Cancel Buttons at the bottom of the panel
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.button(QDialogButtonBox.StandardButton.Save).setText(T["save_settings"])
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(T["cancel_settings"])
        button_box.accepted.connect(self._save_settings) # Connect to internal save method
        button_box.rejected.connect(self._reset_settings) # Connect to internal reset method
        self.layout.addWidget(button_box) # Add to the container_widget's layout

    def _create_prompt_editor(self, label_text: str, default_text: str, tooltip_text: str) -> Tuple[QVBoxLayout, QTextEdit]:
        """
        Helper method to create a QLabel and QTextEdit pair for customizable AI prompts.
        Returns both the layout containing these widgets and the QTextEdit instance.
        """
        v_layout = QVBoxLayout()
        label = QLabel(label_text)
        label.setWordWrap(True) # Allow label text to wrap
        v_layout.addWidget(label)
        text_edit = QTextEdit()
        text_edit.setPlainText(default_text)
        text_edit.setMinimumHeight(80)
        text_edit.setToolTip(tooltip_text)
        v_layout.addWidget(text_edit)
        return v_layout, text_edit

    def _browse_dir(self):
        """Opens a directory selection dialog for the results directory."""
        if directory := QFileDialog.getExistingDirectory(self, T["results_dir_label"], self.line_edit_results_dir.text()):
            self.line_edit_results_dir.setText(directory)

    def _save_settings(self):
        """
        Gathers current settings from the UI elements and emits the `settings_saved` signal.
        This signal will be connected to a slot in the MainWindow to update global config.
        """
        new_settings = {
            "General": {
                "result_dir": self.line_edit_results_dir.text(),
                "encoding": self.combo_encoding.currentText(),
                "theme": self.combo_theme.currentText(),
                "regex_mode": str(self.checkbox_regex_mode.isChecked()).lower()
            },
            "Gemini": {
                "api_key": self.line_edit_api_key.text(),
                "model": self.combo_model.currentText(),
                "prompt_suggest_keywords": self.prompt_suggest_keywords_editor.toPlainText(),
                "prompt_summarize_results": self.prompt_summarize_results_editor.toPlainText(),
                "prompt_detect_anomalies": self.prompt_detect_anomalies_editor.toPlainText(),
                "prompt_analyze_credentials": self.prompt_analyze_credentials_editor.toPlainText()
            }
        }
        self.settings_saved.emit(new_settings)

    def _reset_settings(self):
        """Resets the settings fields in the UI to their currently loaded config values."""
        # This is effectively "Cancel" - load existing config into UI fields
        self.line_edit_api_key.setText(self.config["Gemini"]["api_key"])
        self.combo_model.setCurrentText(self.config["Gemini"]["model"])
        self.prompt_suggest_keywords_editor.setPlainText(self.config["Gemini"].get("prompt_suggest_keywords", CFG_DEF["Gemini"]["prompt_suggest_keywords"]))
        self.prompt_summarize_results_editor.setPlainText(self.config["Gemini"].get("prompt_summarize_results", CFG_DEF["Gemini"]["prompt_summarize_results"]))
        self.prompt_detect_anomalies_editor.setPlainText(self.config["Gemini"].get("prompt_detect_anomalies", CFG_DEF["Gemini"]["prompt_detect_anomalies"]))
        self.prompt_analyze_credentials_editor.setPlainText(self.config["Gemini"].get("prompt_analyze_credentials", CFG_DEF["Gemini"]["prompt_analyze_credentials"]))
        self.line_edit_results_dir.setText(self.config["General"]["result_dir"])
        self.combo_encoding.setCurrentText(self.config["General"]["encoding"])
        self.combo_theme.setCurrentText(self.config["General"]["theme"])
        self.checkbox_regex_mode.setChecked(self.config["General"].getboolean("regex_mode", False))


# --- Main UI —————————————————————————————————————————————————

class MainWindow(QMainWindow):
    """
    The main application window for Logs Combo Extractor Pro.
    This class manages the overall UI layout, user interactions,
    and integrates the file processing and AI functionalities.
    Now featuring a sleek, tabbed interface for enhanced user experience.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle(T["title"])
        self.setMinimumSize(1100, 850) # Set minimum window size for better layout
        self.setAcceptDrops(True) # Enable drag and drop functionality for files
        self.thread: Optional[ExtractThread] = None # Reference to the file extraction thread
        self.ai_thread: Optional[AIThread] = None     # Reference to the AI processing thread
        self.pending_dist_update: Optional[Dict] = None # Buffer for batched UI updates

        # Setup a timer for throttling UI updates, ensuring smooth performance during intense processing.
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(300) # Update UI every 300 milliseconds
        self.update_timer.timeout.connect(self._perform_batched_update) # Connect timeout to batch update method

        self._setup_ui() # Initialize the UI components
        self._connect_signals() # Connect all UI signals to their respective slots (event handlers)
        self.apply_theme(THEME_GLOBAL) # Apply the initial theme loaded from config
        self._load_keywords_from_config() # Load saved keywords on application startup

    def _setup_ui(self):
        """
        Configures the entire graphical user interface of the main window,
        now using a QTabWidget for better organization.
        """
        # Set window icon if 'app.ico' exists in the script directory.
        if (icon_path := SCRIPT_DIR / "app.ico").exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Menu Bar setup (File menu with Export action). Settings moved to tab.
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("📁 " + T["file_menu"])
        action_export = QAction(T["export_results"], self)
        action_export.triggered.connect(self.export_results)
        file_menu.addAction(action_export)

        # Main Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("main_tab_widget") # For QSS styling
        self.setCentralWidget(self.tab_widget) # Set the tab widget as the central widget

        # --- Extractor Tab (Main Application Functionality) ---
        extractor_widget = QWidget()
        main_layout = QVBoxLayout(extractor_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        top_half_layout = QHBoxLayout()
        top_half_layout.setSpacing(15)

        # Files Group
        files_group = QGroupBox("Log Files")
        files_group.setObjectName("files_group")
        files_v_layout = QHBoxLayout(files_group)
        files_v_layout.setContentsMargins(15, 25, 15, 15)
        
        self.drag_drop_label = QLabel(T["drag_drop_files"])
        self.drag_drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_drop_label.setObjectName("drag_drop_label")
        self.drag_drop_label.setToolTip("Drag and drop .log or .txt files here to add them for processing.")
        
        self.list_files = QListWidget()
        self.list_files.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_files.hide()

        files_stack_layout = QVBoxLayout()
        files_stack_layout.addWidget(self.drag_drop_label)
        files_stack_layout.addWidget(self.list_files)
        files_v_layout.addLayout(files_stack_layout, 4)

        files_buttons_layout = QVBoxLayout()
        files_buttons_layout.setSpacing(10)
        self.btn_add_files = QPushButton(T["add"])
        self.btn_remove_files = QPushButton(T["remove"])
        self.btn_clear_files = QPushButton(T["clear_all"])
        self.label_file_size = QLabel(T["file_size"].format(size="0 KB"))
        self.label_file_size.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        files_buttons_layout.addWidget(self.btn_add_files)
        files_buttons_layout.addWidget(self.btn_remove_files)
        files_buttons_layout.addWidget(self.btn_clear_files)
        files_buttons_layout.addStretch()
        files_buttons_layout.addWidget(self.label_file_size)
        files_v_layout.addLayout(files_buttons_layout, 1)
        top_half_layout.addWidget(files_group)

        # Keywords Group
        kw_group = QGroupBox("Keywords")
        kw_group.setObjectName("keywords_group")
        kw_v_layout = QVBoxLayout(kw_group)
        kw_v_layout.setContentsMargins(15, 25, 15, 15)

        self.line_edit_kw_filter = QLineEdit()
        self.line_edit_kw_filter.setPlaceholderText(T["filter"])
        self.line_edit_kw_filter.setToolTip("Type to filter keywords in the list below.")
        
        self.list_keywords = QListWidget()
        self.list_keywords.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_keywords.setToolTip("List of keywords to search for in log files. Select multiple with Ctrl/Cmd or Shift.")
        
        kw_controls_layout = QHBoxLayout()
        self.line_edit_keyword = QLineEdit()
        self.line_edit_keyword.setPlaceholderText(T["enter_kw"])
        self.line_edit_keyword.setToolTip("Enter a new keyword here. If Regex Mode is enabled in settings, this field accepts regular expressions.")

        self.btn_add_kw = QPushButton(T["add_kw"])
        self.btn_add_kw.setToolTip("Add the entered keyword to the list.")
        self.btn_remove_kw = QPushButton(T["remove_kw"])
        self.btn_remove_kw.setToolTip("Remove selected keywords from the list.")
        self.btn_import_kw = QPushButton(T["import_kw"])
        self.btn_import_kw.setToolTip("Import keywords from a text file (one keyword per line).")
        self.btn_export_kw = QPushButton(T["export_kw"])
        self.btn_export_kw.setToolTip("Export current keywords to a text file.")
        
        kw_controls_layout.addWidget(self.line_edit_keyword)
        kw_controls_layout.addWidget(self.btn_add_kw)
        kw_controls_layout.addWidget(self.btn_remove_kw)
        kw_controls_layout.addWidget(self.btn_import_kw)
        kw_controls_layout.addWidget(self.btn_export_kw)
        
        kw_v_layout.addWidget(self.line_edit_kw_filter)
        kw_v_layout.addWidget(self.list_keywords, 1)
        kw_v_layout.addLayout(kw_controls_layout)
        top_half_layout.addWidget(kw_group)
        main_layout.addLayout(top_half_layout)

        # AI and Controls
        ai_group = QGroupBox(T["ai_features_title"])
        ai_group.setObjectName("ai_group")
        ai_layout = QHBoxLayout(ai_group)
        ai_layout.setContentsMargins(15, 25, 15, 15)
        ai_layout.setSpacing(15)
        
        self.btn_ai_suggest = QPushButton(T["ai_suggest_keywords"])
        self.btn_ai_suggest.setToolTip("Uses AI to suggest relevant keywords based on a sample of your log files.")
        self.btn_ai_summarize = QPushButton(T["ai_summarize_results"])
        self.btn_ai_summarize.setToolTip("Uses AI to summarize the results of the current extraction process.")
        self.btn_ai_anomalies = QPushButton(T["ai_detect_anomalies"])
        self.btn_ai_anomalies.setToolTip("Uses AI to detect anomalies or suspicious patterns within the extracted log data.")
        
        ai_layout.addWidget(self.btn_ai_suggest)
        ai_layout.addWidget(self.btn_ai_summarize)
        ai_layout.addWidget(self.btn_ai_anomalies)
        main_layout.addWidget(ai_group)

        self.analysis_group = QGroupBox(T["ai_analysis_title"])
        self.analysis_group.setObjectName("analysis_group")
        analysis_layout = QHBoxLayout(self.analysis_group)
        analysis_layout.setContentsMargins(15, 25, 15, 15)
        self.btn_ai_analyze = QPushButton(T["ai_analyze_credentials"])
        self.btn_ai_analyze.setToolTip("Uses AI to analyze extracted credentials and filter for high-value targets.")
        analysis_layout.addWidget(self.btn_ai_analyze)
        self.analysis_group.setVisible(False)
        main_layout.addWidget(self.analysis_group)

        main_controls_layout = QHBoxLayout()
        main_controls_layout.addStretch()
        self.btn_start = QPushButton(T["start"])
        self.btn_start.setToolTip("Start the log extraction process.")
        self.btn_cancel = QPushButton(T["cancel"])
        self.btn_cancel.setToolTip("Stop the current log extraction process.")
        self.btn_cancel.setEnabled(False)
        self.btn_open = QPushButton(T["open"])
        self.btn_open.setToolTip("Open the directory where results are saved.")
        self.btn_open.setEnabled(False)
        
        main_controls_layout.addWidget(self.btn_start)
        main_controls_layout.addWidget(self.btn_cancel)
        main_controls_layout.addWidget(self.btn_open)
        main_controls_layout.addStretch()
        main_layout.addLayout(main_controls_layout)

        # Progress and Status
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(10)
        self.prog_bar_file = QProgressBar()
        self.prog_bar_file.setFormat(f"{T['file_prog']}: %p%")
        self.prog_bar_file.setToolTip("Overall progress of file processing.")
        self.prog_bar_line = QProgressBar()
        self.prog_bar_line.setFormat(f"{T['line_prog']}: %p%")
        self.prog_bar_line.setToolTip("Progress within the currently processed file.")
        
        progress_layout.addWidget(self.prog_bar_file, 1)
        progress_layout.addWidget(self.prog_bar_line, 1)
        main_layout.addLayout(progress_layout)
        
        self.label_status = QLabel(f"{T['status']} {T['ready']}")
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_status.setObjectName("status_label") # Object name for animation
        main_layout.addWidget(self.label_status)

        # Status label animation
        self.status_animation = QVariantAnimation(self)
        self.status_animation.setDuration(1000)
        self.status_animation.setStartValue(QColor(QColor(0, 122, 255))) # Apple Blue
        self.status_animation.setEndValue(QColor(QColor(100, 100, 100))) # Gray
        self.status_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.status_animation.setLoopCount(-1) # Loop indefinitely
        self.status_animation.valueChanged.connect(self._animate_status_label)


        # Results Area
        main_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))
        
        self.table_results = QTableWidget(0, 2)
        self.table_results.setHorizontalHeaderLabels([T["matches_column"], T["kw_column"]])
        self.table_results.setColumnWidth(0, 100)
        self.table_results.horizontalHeader().setStretchLastSection(True)
        self.table_results.verticalHeader().setVisible(False)
        self.table_results.setToolTip("Displays the count of matches for each keyword.")
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Application logs, results, and AI summaries will appear here.")
        self.log_output.setToolTip("Detailed logs of application activity and AI responses.")

        stats_layout = QHBoxLayout()
        self.label_kw_count = QLabel(T["kw_stats"].format(count=0))
        self.label_match_count = QLabel(T["match_stats"].format(count=0))
        stats_layout.addWidget(self.label_kw_count)
        stats_layout.addWidget(self.label_match_count)
        stats_layout.addStretch()
        
        results_layout = QVBoxLayout()
        results_layout.addLayout(stats_layout)
        results_layout.addWidget(self.table_results, 1)
        results_layout.addWidget(self.log_output, 1)
        main_layout.addLayout(results_layout)

        # Add the Extractor tab to the QTabWidget
        self.tab_widget.addTab(extractor_widget, T["tab_main"])

        # --- Settings Tab ---
        self.settings_panel = SettingsPanel(cfg_global, self)
        # Connect the settings_saved signal from the SettingsPanel to a slot in MainWindow
        self.settings_panel.settings_saved.connect(self._handle_settings_saved)
        self.tab_widget.addTab(self.settings_panel, T["tab_settings"])


    def _connect_signals(self):
        """
        Connects all UI element signals to their corresponding handler methods.
        This establishes the interactive behavior of the application.
        """
        # File list interactions
        self.list_files.itemSelectionChanged.connect(self.update_file_size)
        self.btn_add_files.clicked.connect(self.add_files)
        self.btn_remove_files.clicked.connect(self.remove_file)
        self.btn_clear_files.clicked.connect(self.clear_files)

        # Keyword list and input interactions
        self.list_keywords.itemChanged.connect(self._update_keyword_stats)
        self.line_edit_kw_filter.textChanged.connect(self._filter_keywords)
        self.line_edit_keyword.returnPressed.connect(self.add_keyword)
        self.btn_add_kw.clicked.connect(self.add_keyword)
        self.btn_remove_kw.clicked.connect(self.remove_keyword)
        self.btn_import_kw.clicked.connect(self.import_keywords)
        self.btn_export_kw.clicked.connect(self.export_keywords)

        # Main processing controls
        self.btn_start.clicked.connect(self.start_processing)
        self.btn_cancel.clicked.connect(self.cancel_processing)
        self.btn_open.clicked.connect(self.open_results_directory)

        # AI feature buttons
        self.btn_ai_suggest.clicked.connect(self.ai_suggest_keywords)
        self.btn_ai_summarize.clicked.connect(self.ai_summarize_results)
        self.btn_ai_anomalies.clicked.connect(self.ai_detect_anomalies)
        self.btn_ai_analyze.clicked.connect(self.ai_analyze_credentials)

    def apply_theme(self, theme: str):
        """
        Applies the selected UI theme using Qt Style Sheets (QSS).
        The QSS is designed to mimic the sleek, minimalist, and vibrant aesthetic of Apple's macOS UI.
        Includes extensive styling for various widgets with rounded corners, subtle gradients, and shadows.
        """
        font_family = "'SF Pro Text', 'San Francisco', 'Segoe UI', 'Arial', 'Helvetica Neue', sans-serif" # Prioritize Apple's font
        
        # --- Common Styling (Google Material Design & Apple Fusion) ---
        common_style = f"""
            * {{
                font-family: {font_family};
                font-size: 13px;
                border-radius: 8px; /* Default rounded corners for most elements */
            }}
            QScrollArea {{
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{ /* Inner widget of scroll area */
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: #4a4a4c; /* Darker background for scrollbar track */
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px; /* Rounded scrollbar track */
            }}
            QScrollBar::handle:vertical {{
                background: #007aff; /* Apple blue handle */
                min-height: 20px;
                border-radius: 5px; /* Rounded handle */
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}

            QScrollBar:horizontal {{
                border: none;
                background: #4a4a4c;
                height: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal {{
                background: #007aff;
                min-width: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}

            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #6a6a6e;
                border-left-style: solid;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
            QComboBox::down-arrow {{
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNlMGUwZTAiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSI2IDkgMTIgMTUgMTggOSI+PC9wb2x5bGluZT48L3N2Zz4=); /* White arrow */
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid #4a4a4c;
                border-radius: 8px;
                padding: 5px;
                selection-background-color: #007aff;
                selection-color: white;
                outline: none; /* Remove focus rectangle */
            }}
            QComboBox QAbstractItemView::item {{
                min-height: 28px; /* Taller items for better touch */
            }}
        """

        # --- Dark Mode Styling (Inspired by macOS Dark Mode) ---
        dark_style = f"""
            {common_style}
            QMainWindow, QDialog {{ 
                background: #1c1c1e; /* Darker background for depth */
                color: #e0e0e0;
            }}
            QWidget {{ 
                background-color: #1c1c1e; /* Consistent dark background */
                color: #e0e0e0; 
            }}
            QMenuBar {{ 
                background-color: #1c1c1e; 
                color: #e0e0e0; 
                border-bottom: 1px solid #333333; /* Subtle separation */
            }}
            QMenuBar::item:selected {{ 
                background-color: #38383a; /* Highlight on selection */
                border-radius: 6px; /* Slightly rounded for menu items */
            }}
            QMenu {{ 
                background-color: #2c2c2e; /* Slightly lighter for pop-up menus */
                border: 1px solid #4a4a4a;
                border-radius: 8px; /* Rounded menu corners */
                padding: 5px;
            }}
            QMenu::item {{ 
                color: #e0e0e0; 
                padding: 6px 15px; 
                border-radius: 5px; 
            }}
            QMenu::item:selected {{ 
                background-color: #007aff; /* Apple Blue highlight */
                color: white; 
            }}
            
            QPushButton {{
                background-color: #3a3a3c; /* Dark gray for buttons */
                border: 1px solid #5a5a5c; /* Subtle border */
                padding: 10px 15px; /* More padding */
                border-radius: 12px; /* More rounded, pill-like */
                min-width: 100px; /* Slightly wider buttons */
                color: #ffffff; /* White text */
                font-weight: 500; /* Medium weight font */
                box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2); /* Subtle shadow for depth */
                transition: all 0.2s ease-in-out; /* Smooth transition for hover effects */
            }}
            QPushButton:hover {{ 
                background-color: #4a4a4c; /* Lighter on hover */
                border-color: #6a6a6e;
                box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.3); /* Slightly larger shadow */
            }}
            QPushButton:pressed {{ 
                background-color: #2a2a2c; /* Darker when pressed */
                box-shadow: none; /* Remove shadow when pressed */
                transform: translateY(1px); /* Slight press down effect */
            }}
            QPushButton:disabled {{ 
                color: #777777; 
                background-color: #2e2e2f; 
                border-color: #4a4a4b; 
                box-shadow: none; 
            }}

            QListWidget, QLineEdit, QTextEdit, QTableWidget, QComboBox {{
                background-color: #2c2c2e; /* Input/content background */
                border: 1px solid #4a4a4c;
                padding: 8px; /* Increased padding */
                selection-background-color: #007aff; /* Apple Blue selection */
                selection-color: #fff;
                color: #e0e0e0; /* Text color */
                box-shadow: inset 0px 1px 3px rgba(0, 0, 0, 0.2); /* Inner shadow for depth */
            }}
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{ 
                border-color: #007aff; /* Highlight focus with Apple Blue */
                box-shadow: inset 0px 1px 3px rgba(0, 0, 0, 0.2), 0px 0px 0px 3px rgba(0, 122, 255, 0.3); /* Subtle outer glow on focus */
            }}
            
            QProgressBar {{
                border: 1px solid #4a4a4c;
                text-align: center;
                height: 28px; /* Taller progress bar */
                color: #ffffff; /* White text on progress bar */
                background-color: #2c2c2e; /* Background of the bar */
                text-shadow: 1px 1px 2px rgba(0,0,0,0.4); /* Subtle text shadow */
            }}
            QProgressBar::chunk {{ 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #007aff, stop:1 #5ac8fa); /* Blue gradient chunk */
                border-radius: 8px; 
                margin: 0px; /* No gaps */
            }}
            
            QHeaderView::section {{
                background-color: #3a3a3c; /* Header background */
                color: #e0e0e0;
                padding: 10px; /* More padding in headers */
                border: none;
                font-weight: bold;
                border-bottom: 1px solid #4a4a4c;
                font-size: 14px; /* Slightly larger header font */
            }}
            QHeaderView::section:hover {{ background-color: #4a4a4c; }}

            QGroupBox {{
                margin-top: 15px; /* More space above group boxes */
                padding-top: 20px;
                border: 1px solid #4a4a4c;
                border-radius: 15px; /* More pronounced rounded corners */
                font-weight: bold;
                color: #007aff; /* Apple Blue for titles */
                background-color: #252527; /* Slightly distinct background for groups */
                box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.25); /* Deeper shadow for group boxes */
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 15px;
                background-color: #252527; /* Match group background */
                border-radius: 8px; /* Title background rounded */
                font-size: 15px; /* Larger title font */
            }}
            
            QLabel#drag_drop_label {{
                border: 2px dashed #007aff; /* Vibrant Apple Blue dashed border */
                background-color: #2e2e30; /* Slightly lighter background for the drop area */
                color: #007aff;
                font-weight: bold;
                font-style: italic;
                border-radius: 15px; /* Consistent rounding */
                padding: 30px; /* More generous padding */
                font-size: 16px; /* Larger font for emphasis */
                box-shadow: inset 0px 0px 10px rgba(0, 122, 255, 0.1); /* Subtle inner glow */
                transition: background-color 0.3s ease; /* Smooth transition for drag/drop feedback */
            }}
            
            /* Specific styling for AI feature buttons with vibrant gradients */
            QGroupBox#ai_group QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #007aff,stop:1 #5ac8fa); /* Vibrant Apple Blue gradient */
                border: 1px solid #007aff;
                color: white;
                font-weight: bold;
                border-radius: 12px;
                box-shadow: 0px 3px 8px rgba(0, 122, 255, 0.4); /* Blue glowing shadow */
            }}
            QGroupBox#ai_group QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #006ee6,stop:1 #47b2e3);
                box-shadow: 0px 4px 12px rgba(0, 122, 255, 0.6); /* More intense glow on hover */
            }}
            QGroupBox#ai_group QPushButton:pressed {{
                background: #005bb5; /* Solid blue when pressed */
                box-shadow: none;
            }}

            /* Specific styling for Analysis button with a warning red gradient */
            QGroupBox#analysis_group QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3b30, stop:1 #ff453a); /* Apple Red gradient */
                border: 1px solid #ff3b30;
                color: white;
                font-weight: bold;
                border-radius: 12px;
                box-shadow: 0px 3px 8px rgba(255, 59, 48, 0.4); /* Red glowing shadow */
            }}
            QGroupBox#analysis_group QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e0322b, stop:1 #e03e33);
                box-shadow: 0px 4px 12px rgba(255, 59, 48, 0.6); /* More intense glow on hover */
            }}
            QGroupBox#analysis_group QPushButton:pressed {{
                background: #cc2f26; /* Solid red when pressed */
                box-shadow: none;
            }}

            /* Checkbox styling (Apple-like toggle) */
            QCheckBox::indicator {{
                width: 18px; /* Slightly larger indicator */
                height: 18px;
                border: 1px solid #5a5a5c;
                border-radius: 5px; /* Softer rounded corners */
                background-color: #38383a;
                margin-right: 5px; /* Space between checkbox and text */
            }}
            QCheckBox::indicator:checked {{
                background-color: #007aff; /* Apple Blue when checked */
                border: 1px solid #007aff;
                /* Embedded SVG for a crisp white checkmark */
                image: url(data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwIiB5PSIwIiB2aWV3Qm94PSIwIDAgNTEyIDUxMiIgc3R5bGU9ImVuYWJsZS1iYWNrZ3JvdW5kOm5ldyAwIDAgNTEyIDUxMi47IiB4bWw6c3BhY2U9InByZXNlcnZlIj48c3R5bGUgdHlwZT0idGV4dC9jc3MiPgoucnN0MCB7ZmlsbDojRkZGRkZGO30KPC9zdHlsZT48cGF0aCBjbGFzcz0icnN0MCIgZD0iTTQyMC43LDc5LjNMMjEzLjUsMjg2LjVMMTAxLjMsMTczLjJMNTIuNiwyMjEuOWwyMTMuNSwyMTMuNUw0NTguNywxMTguNEw0MjAuNyw3OS4zWiIvPjwvc3ZnPg==);
            }}
            QCheckBox::indicator:disabled {{
                background-color: #2e2e2f;
                border: 1px solid #4a4a4b;
            }}
            
            QTextEdit {{
                padding: 10px; /* More padding for readability */
                line-height: 1.5; /* Improved line spacing for text */
            }}

            /* Styling for QTabWidget and its tabs */
            QTabWidget#main_tab_widget::pane {{ /* The tab bar frame */
                border-top: 1px solid #4a4a4c;
                border-radius: 15px; /* Consistent with group boxes */
            }}

            QTabWidget#main_tab_widget > QTabBar::tab {{
                background: #2c2c2e; /* Background of inactive tabs */
                border: 1px solid #4a4a4c;
                border-bottom-color: #1c1c1e; /* Same as pane color */
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 10px 20px; /* Generous padding for tabs */
                color: #e0e0e0;
                font-weight: 500;
                margin-right: 5px; /* Spacing between tabs */
                min-width: 120px; /* Minimum width for tabs */
                text-align: center;
                box-shadow: 0px -2px 5px rgba(0, 0, 0, 0.1); /* Subtle shadow for depth */
                transition: background-color 0.2s ease, box-shadow 0.2s ease;
            }}

            QTabWidget#main_tab_widget > QTabBar::tab:selected {{
                background: #1c1c1e; /* Background of active tab */
                border-color: #007aff; /* Apple Blue border for selected tab */
                border-bottom-color: #1c1c1e; /* Remove bottom border for seamless connection to pane */
                color: #007aff; /* Apple Blue text for selected tab */
                font-weight: bold;
                box-shadow: 0px -3px 8px rgba(0, 122, 255, 0.3); /* Glowing shadow for selected tab */
            }}

            QTabWidget#main_tab_widget > QTabBar::tab:hover {{
                background: #38383a; /* Lighter background on hover */
            }}

            QTabWidget#main_tab_widget > QTabBar::tab:selected:hover {{
                background: #1c1c1e; /* No change on hover for selected tab */
            }}
            
            /* Specific styling for settings group boxes within the settings tab */
            QGroupBox#settings_group_box {{
                background-color: #2c2c2e; /* Slightly different background for settings sections */
                border: 1px solid #4a4a4c;
                border-radius: 12px;
                box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.2);
            }}
            QGroupBox#settings_group_box::title {{
                background-color: #2c2c2e;
            }}

            QLabel#cost_warning_label {{
                font-style: italic; 
                color: #888; 
                font-size: 11px; /* Smaller font for notes */
                padding-top: 5px; /* Space from above elements */
            }}
            
        """
        # --- Light Mode Styling (Inspired by macOS Light Mode) ---
        light_style = f"""
            {common_style}
            QMainWindow, QDialog {{ 
                background: #f2f2f7; /* Light background for depth */
                color: #1c1c1e;
            }}
            QWidget {{ 
                background-color: #f2f2f7; 
                color: #1c1c1e; 
            }}
            QMenuBar {{ 
                background-color: #f2f2f7; 
                color: #1c1c1e; 
                border-bottom: 1px solid #e0e0e0; 
            }}
            QMenuBar::item:selected {{ 
                background-color: #e0e0e0; 
                border-radius: 6px; 
            }}
            QMenu {{ 
                background-color: #ffffff; 
                border: 1px solid #cccccc;
                border-radius: 8px; 
                padding: 5px;
            }}
            QMenu::item {{ 
                color: #1c1c1e; 
                padding: 6px 15px; 
                border-radius: 5px; 
            }}
            QMenu::item:selected {{ 
                background-color: #007aff; 
                color: white; 
            }}

            QPushButton {{
                background-color: #ffffff; 
                border: 1px solid #d0d0d0;
                padding: 10px 15px;
                border-radius: 12px;
                min-width: 100px;
                color: #1c1c1e;
                font-weight: 500;
                box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1); 
                transition: all 0.2s ease-in-out;
            }}
            QPushButton:hover {{ 
                background-color: #e8e8ed; 
                border-color: #c0c0c0;
                box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.15); 
            }}
            QPushButton:pressed {{ 
                background-color: #d0d0d0;
                box-shadow: none; 
                transform: translateY(1px);
            }}
            QPushButton:disabled {{ 
                color: #aaaaaa; 
                background-color: #f8f8f8; 
                border-color: #e0e0e0; 
                box-shadow: none; 
            }}

            QListWidget, QLineEdit, QTextEdit, QTableWidget, QComboBox {{
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                padding: 8px;
                selection-background-color: #007aff;
                selection-color: #fff;
                color: #1c1c1e;
                box-shadow: inset 0px 1px 3px rgba(0, 0, 0, 0.1); 
            }}
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{ 
                border-color: #007aff;
                box-shadow: inset 0px 1px 3px rgba(0, 0, 0, 0.1), 0px 0px 0px 3px rgba(0, 122, 255, 0.2); 
            }}

            QProgressBar {{
                border: 1px solid #e0e0e0;
                text-align: center;
                height: 28px;
                color: #1c1c1e;
                background-color: #ffffff;
                text-shadow: 1px 1px 2px rgba(255,255,255,0.4);
            }}
            QProgressBar::chunk {{ 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #007aff, stop:1 #5ac8fa);
                border-radius: 8px; 
                margin: 0px;
            }}

            QHeaderView::section {{
                background-color: #e8e8ed;
                color: #1c1c1e;
                padding: 10px;
                border: none;
                font-weight: bold;
                border-bottom: 1px solid #e0e0e0;
                font-size: 14px;
            }}
            QHeaderView::section:hover {{ background-color: #dddddd; }}

            QGroupBox {{
                margin-top: 15px;
                padding-top: 20px;
                border: 1px solid #e0e0e0;
                border-radius: 15px;
                font-weight: bold;
                color: #007aff;
                background-color: #ffffff;
                box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.1);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 15px;
                background-color: #ffffff;
                border-radius: 8px;
                font-size: 15px;
            }}

            QLabel#drag_drop_label {{
                border: 2px dashed #007aff;
                background-color: #f7fcff; /* Very light blue for drop area */
                color: #007aff;
                font-weight: bold;
                font-style: italic;
                border-radius: 15px;
                padding: 30px;
                font-size: 16px;
                box-shadow: inset 0px 0px 10px rgba(0, 122, 255, 0.05);
                transition: background-color 0.3s ease;
            }}
            
            QGroupBox#ai_group QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #007aff,stop:1 #5ac8fa);
                border: 1px solid #007aff;
                color: white;
                font-weight: bold;
                border-radius: 12px;
                box-shadow: 0px 3px 8px rgba(0, 122, 255, 0.2);
            }}
            QGroupBox#ai_group QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #006ee6,stop:1 #47b2e3);
                box-shadow: 0px 4px 12px rgba(0, 122, 255, 0.3);
            }}
            QGroupBox#ai_group QPushButton:pressed {{
                background: #005bb5;
                box-shadow: none;
            }}

            QGroupBox#analysis_group QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3b30, stop:1 #ff453a);
                border: 1px solid #ff3b30;
                color: white;
                font-weight: bold;
                border-radius: 12px;
                box-shadow: 0px 3px 8px rgba(255, 59, 48, 0.2);
            }}
            QGroupBox#analysis_group QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e0322b, stop:1 #e03e33);
                box-shadow: 0px 4px 12px rgba(255, 59, 48, 0.3);
            }}
            QGroupBox#analysis_group QPushButton:pressed {{
                background: #cc2f26;
                box-shadow: none;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: #ffffff;
                margin-right: 5px;
            }}
            QCheckBox::indicator:checked {{
                background-color: #007aff;
                border: 1px solid #007aff;
                image: url(data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwIiB5PSIwIiB2aWV3Qm94PSIwIDAgNTEyIDUxMiIgc3R5bGU9ImVuYWJsZS1iYWNrZ3JvdW5kOm5ldyAwIDAgNTEyIDUxMi47IiB4bWw6c3BhY2U9InByZXNlcnZlIj48c3R5bGUgdHlwZT0idGV4dC9jc3MiPgoucnN0MCB7ZmlsbDojRkZGRkZGO30KPC9zdHlsZT48cGF0aCBjbGFzcz0icnN0MCIgZD0iTTQyMC43LDc5LjNMMjEzLjUsMjg2LjVMMTAxLjMsMTczLjJMNTIuNiwyMjEuOWwyMTMuNSwyMTMuNUw0NTguNywxMTguNEw0MjAuNyw3OS4zWiIvPjwvc3ZnPg==);
            }}
            QCheckBox::indicator:disabled {{
                background-color: #f8f8f8;
                border: 1px solid #e0e0e0;
            }}

            QTextEdit {{
                padding: 10px;
                line-height: 1.5;
            }}

            /* Styling for QTabWidget and its tabs */
            QTabWidget#main_tab_widget::pane {{ /* The tab bar frame */
                border-top: 1px solid #e0e0e0;
                border-radius: 15px;
            }}

            QTabWidget#main_tab_widget > QTabBar::tab {{
                background: #ffffff; /* Background of inactive tabs */
                border: 1px solid #d0d0d0;
                border-bottom-color: #f2f2f7; /* Same as pane color */
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 10px 20px;
                color: #1c1c1e;
                font-weight: 500;
                margin-right: 5px;
                min-width: 120px;
                text-align: center;
                box-shadow: 0px -2px 5px rgba(0, 0, 0, 0.05);
                transition: background-color 0.2s ease, box-shadow 0.2s ease;
            }}

            QTabWidget#main_tab_widget > QTabBar::tab:selected {{
                background: #f2f2f7; /* Background of active tab */
                border-color: #007aff;
                border-bottom-color: #f2f2f7;
                color: #007aff;
                font-weight: bold;
                box-shadow: 0px -3px 8px rgba(0, 122, 255, 0.15);
            }}

            QTabWidget#main_tab_widget > QTabBar::tab:hover {{
                background: #e8e8ed;
            }}

            QTabWidget#main_tab_widget > QTabBar::tab:selected:hover {{
                background: #f2f2f7;
            }}

            /* Specific styling for settings group boxes within the settings tab */
            QGroupBox#settings_group_box {{
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.1);
            }}
            QGroupBox#settings_group_box::title {{
                background-color: #ffffff;
            }}

            QLabel#cost_warning_label {{
                font-style: italic; 
                color: #888; 
                font-size: 11px;
                padding-top: 5px;
            }}
        """
        
        # Apply the chosen theme's stylesheet.
        if theme == "system":
            self.setStyleSheet(dark_style)
        elif theme == "dark":
            self.setStyleSheet(dark_style)
        else:
            self.setStyleSheet(light_style)

    # --- UI Event Handlers ---
    def dragEnterEvent(self, e: QDragEnterEvent):
        """
        Handles the `dragEnterEvent` for drag-and-drop functionality.
        Accepts the proposed action if URLs (file paths) are present in the drag data,
        and provides visual feedback by changing the drag-drop label's style.
        """
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            # Visual feedback: change border and background to indicate a valid drop target.
            # Using Google Material Design inspired colors for hover
            self.drag_drop_label.setStyleSheet("border: 2px dashed #4285F4; background-color: #e8f0fe; color: #4285F4; font-weight: bold; font-style: italic; border-radius: 15px; padding: 30px; font-size: 16px; box-shadow: inset 0px 0px 10px rgba(66, 133, 244, 0.15);")
    
    def dropEvent(self, e: QDropEvent):
        """
        Handles the `dropEvent` when files are dropped onto the application.
        Adds the dropped files to the file list if they are unique and valid,
        then updates the displayed total file size. Resets the drag-drop label style.
        """
        self.apply_theme(THEME_GLOBAL) # Reset style after drag/drop operation
        files_added = False
        for url in e.mimeData().urls():
            file_path = url.toLocalFile()
            # Add file only if it's an existing file and not already in the list.
            if os.path.isfile(file_path) and not self.list_files.findItems(file_path, Qt.MatchFlag.MatchExactly):
                self.list_files.addItem(file_path)
                files_added = True
        if files_added:
            self.update_file_size() # Update the file size display
    
    def dragLeaveEvent(self, e: QDragLeaveEvent):
        """
        Handles the `dragLeaveEvent` when the drag operation leaves the widget.
        Resets the visual feedback on the drag-drop label to its default theme style.
        """
        self.apply_theme(THEME_GLOBAL) # Reset style to default theme after drag leaves
    
    def add_files(self):
        """
        Opens a file dialog, allowing the user to select one or more log files (.log, .txt)
        to add to the processing list. Updates the file size display.
        """
        files, _ = QFileDialog.getOpenFileNames(self, T["add"], "", "Logs (*.log *.txt);;All Files (*)")
        for f in files:
            if not self.list_files.findItems(f, Qt.MatchFlag.MatchExactly): # Avoid duplicates
                self.list_files.addItem(f)
        self.update_file_size() # Update total size and visibility of drag-drop label

    def remove_file(self):
        """Removes selected files from the list of log files."""
        for item in self.list_files.selectedItems():
            self.list_files.takeItem(self.list_files.row(item))
        self.update_file_size() # Recalculate and display new total size

    def clear_files(self):
        """Clears all files from the list, resetting the file display and size."""
        self.list_files.clear()
        self.update_file_size() # Resets display and shows drag-drop area

    def add_keyword(self):
        """
        Adds a new keyword (or regex, if enabled) to the keyword list.
        Performs basic regex validation if in regex mode.
        Saves the updated keyword list to the configuration file.
        """
        if kw := self.line_edit_keyword.text().strip(): # Get text and strip whitespace
            # Perform regex validation if regex mode is active.
            if REGEX_MODE_GLOBAL:
                try:
                    re.compile(kw) # Attempt to compile the regex
                except re.error as e:
                    QMessageBox.warning(self, T["title"], T["invalid_regex"].format(keyword=kw, error=e))
                    return # Stop if regex is invalid
            
            if not self.list_keywords.findItems(kw, Qt.MatchFlag.MatchExactly): # Avoid duplicates
                self.list_keywords.addItem(kw)
                self.line_edit_keyword.clear() # Clear the input field after adding
                self._update_keyword_stats() # Update keyword count display
                self._filter_keywords(self.line_edit_kw_filter.text()) # Re-apply current filter
                self._save_keywords_to_config() # Persist keywords to config file

    def remove_keyword(self):
        """
        Removes selected keywords from the list.
        Saves the modified keyword list to the configuration file.
        """
        for item in self.list_keywords.selectedItems():
            self.list_keywords.takeItem(self.list_keywords.row(item))
        self._update_keyword_stats() # Update keyword count display
        self._save_keywords_to_config() # Persist changes

    def import_keywords(self):
        """
        Imports keywords from a selected text file (one keyword per line).
        Adds new keywords to the list, validating regex if applicable,
        and then saves the updated list to the configuration.
        """
        if fn_tuple := QFileDialog.getOpenFileName(self, T["import_kw"], "", "Text (*.txt);;All Files (*)"):
            if filename := fn_tuple[0]:
                keywords_added = False
                with open(filename, encoding=ENC_GLOBAL, errors="ignore") as f:
                    for line in f:
                        if kw := line.strip(): # Read each line as a keyword
                            if REGEX_MODE_GLOBAL:
                                try:
                                    re.compile(kw)
                                except re.error as e:
                                    self.log_output.append(f"Skipping invalid regex from import: '{kw}' - {e}")
                                    continue # Skip invalid regex during import
                            if not self.list_keywords.findItems(kw, Qt.MatchFlag.MatchExactly):
                                self.list_keywords.addItem(kw)
                                keywords_added = True
                if keywords_added:
                    self._update_keyword_stats()
                    self._filter_keywords(self.line_edit_kw_filter.text())
                    self._save_keywords_to_config() # Save keywords after successful import

    def export_keywords(self):
        """Exports all current keywords from the list to a selected text file."""
        if fn_tuple := QFileDialog.getSaveFileName(self, T["export_kw"], "", "Text (*.txt);;All Files (*)"):
            if filename := fn_tuple[0]:
                with open(filename, "w", encoding=ENC_GLOBAL) as f:
                    for i in range(self.list_keywords.count()):
                        f.write(self.list_keywords.item(i).text() + "\n")

    # --- Keyword Persistence Methods ————————————————————————————————
    def _save_keywords_to_config(self):
        """
        Saves the current list of keywords to the 'Keywords' section of the global
        configuration file (`config.ini`). This ensures keywords persist across application sessions.
        Each keyword is stored with a unique, ordered key (e.g., 'kw_0000', 'kw_0001').
        """
        global cfg_global
        cfg_global["Keywords"].clear() # Clear existing keywords in config before saving new ones
        for i in range(self.list_keywords.count()):
            # Use indexed keys to maintain insertion order when loading back, ensuring consistency.
            cfg_global["Keywords"][f"kw_{i:04d}"] = self.list_keywords.item(i).text()
        
        with open(INI_PATH, "w", encoding="utf-8") as f:
            cfg_global.write(f) # Write updated configuration to disk

    def _load_keywords_from_config(self):
        """
        Loads keywords from the 'Keywords' section of the global configuration file
        into the application's keyword list (`self.list_keywords`) on startup.
        """
        global cfg_global
        self.list_keywords.clear() # Clear any default or existing items before loading
        if "Keywords" in cfg_global:
            # Sort keys to ensure keywords are loaded in the order they were saved.
            sorted_keys = sorted(cfg_global["Keywords"].keys())
            for key in sorted_keys:
                kw = cfg_global["Keywords"][key]
                self.list_keywords.addItem(kw)
        self._update_keyword_stats() # Update the displayed keyword count after loading

    # --- Core Logic & Processing Methods ————————————————————————————
    def start_processing(self):
        """
        Initiates the log file processing. Performs preliminary checks for files and keywords,
        resets UI elements, sets the UI to a busy state, and starts the `ExtractThread`.
        """
        self.analysis_group.setVisible(False) # Hide the AI analysis group for a fresh scan
        
        # Gather current files and keywords from their respective list widgets.
        files = [self.list_files.item(i).text() for i in range(self.list_files.count())]
        # Only include keywords that are currently visible (not filtered out).
        keywords = [self.list_keywords.item(i).text() for i in range(self.list_keywords.count()) if not self.list_keywords.isRowHidden(i)]
        
        # Input validation
        if not files:
            QMessageBox.critical(self, T["title"], T["no_files"])
            return
        if not keywords:
            QMessageBox.critical(self, T["title"], T["no_keywords"])
            return

        # Reset UI elements for a new processing run
        self.log_output.clear()
        self.table_results.setRowCount(0)
        self.prog_bar_file.setValue(0)
        self.prog_bar_line.setValue(0)
        self.label_match_count.setText(T["match_stats"].format(count=0))
        self._set_ui_busy(True) # Disable interactive elements and show busy cursor
        self.status_animation.start() # Start status label animation

        # Initialize and start the extraction thread.
        self.thread = ExtractThread(files, keywords, REGEX_MODE_GLOBAL)
        # Connect thread signals to UI update slots
        self.thread.sig_status.connect(lambda s: self.label_status.setText(f"{T['status']} {s}"))
        self.thread.sig_file_prog.connect(self.prog_bar_file.setValue)
        self.thread.sig_line_prog.connect(self.prog_bar_line.setValue)
        self.thread.sig_dist.connect(self._handle_dist_update) # Connect to throttled update handler
        self.thread.sig_log.connect(self.log_output.append)     # Append general log messages
        self.thread.sig_error.connect(self.log_output.append)   # Display file-specific errors in log output
        self.thread.sig_done.connect(self.on_processing_done)   # Callback for thread completion
        self.thread.start() # Start the worker thread
        self.update_timer.start() # Start the UI update throttling timer

    def cancel_processing(self):
        """Signals the ongoing processing thread to stop."""
        if self.thread:
            self.thread.cancel() # Set the cancellation flag in the worker thread
    
    def on_processing_done(self):
        """
        Callback method executed when the `ExtractThread` finishes (either completes or is cancelled).
        Stops the UI update timer, performs a final result table update, displays a completion message,
        and resets the UI from the busy state.
        """
        self.update_timer.stop() # Stop the UI throttling timer
        self._perform_batched_update() # Ensure all pending result updates are processed
        
        # Determine the appropriate completion message.
        message = T["canceled"] if self.thread and self.thread._cancel else T["complete"]
        self.log_output.append(f"\n--- {message.upper()} ---") # Log the final status
        QMessageBox.information(self, T["title"], message) # Show a pop-up message to the user
        
        self._set_ui_busy(False) # Reset UI to non-busy state
        self.btn_open.setEnabled(True) # Enable the "Open Results" button
        self.status_animation.stop() # Stop status label animation
        self.label_status.setStyleSheet("") # Reset status label stylesheet
        
        # Show AI analysis group only if there's any content in the log output,
        # indicating a successful (or partially successful) processing run.
        if self.log_output.toPlainText().strip():
            self.analysis_group.setVisible(True)

    # --- AI Methods —————————————————————————————————————————————————
    def _run_ai_task(self, prompt: str, on_chunk_slot, on_done_slot):
        """
        A helper method to encapsulate the common logic for running an AI task.
        Performs API key validation, sets UI busy state, starts the AI thread,
        and connects its signals to provided slots.
        """
        # Check if Gemini API key is configured.
        if not (GEMINI_API_KEY_GLOBAL and GEMINI_API_KEY_GLOBAL != "YOUR_GEMINI_API_KEY_HERE"):
            QMessageBox.warning(self, T["api_key_missing_title"], T["api_key_missing_message"])
            return # Abort if API key is missing

        self._set_ui_busy(True) # Set UI to busy, disable interaction
        self.label_status.setText(T["ai_query_status"]) # Update status to reflect AI query in progress
        self.status_animation.start() # Start status label animation
        
        # Initialize and start the AI thread.
        self.ai_thread = AIThread(GEMINI_API_KEY_GLOBAL, prompt, GEMINI_MODEL_GLOBAL)
        # Connect AI thread signals
        self.ai_thread.sig_chunk.connect(on_chunk_slot) # Slot for handling streaming text chunks
        self.ai_thread.sig_done.connect(on_done_slot)   # Slot for handling AI task completion
        self.ai_thread.sig_error.connect(self.on_ai_error) # Slot for handling AI errors
        self.ai_thread.start() # Begin AI processing

    def ai_suggest_keywords(self):
        """
        Triggers an AI task to suggest relevant keywords based on a sample of the loaded log files.
        Collects a sample from the first few log files and sends it to the Gemini AI.
        """
        if self.list_files.count() == 0:
            QMessageBox.warning(self, T["title"], T["no_files_for_suggestions"])
            return # Cannot suggest if no files are loaded
        
        sample_content = ""
        # Read a small sample (e.g., first 2KB) from each loaded file to create a general log sample.
        for i in range(self.list_files.count()):
            try:
                with open(self.list_files.item(i).text(), 'r', encoding=ENC_GLOBAL, errors='ignore') as f:
                    sample_content += "".join(f.readlines(2048)) + "\n" # Read up to 2KB per file
            except Exception:
                continue # Skip files that cannot be read
        
        # Limit the total sample content sent to AI to avoid exceeding context limits and reduce cost.
        final_sample = sample_content[:20000] # Max 20,000 characters for the sample
        
        # Format the AI prompt using the configurable template and the prepared log sample.
        prompt = PROMPT_SUGGEST_KEYWORDS_GLOBAL.format(log_sample=final_sample)
        self.pending_ai_suggestions = [] # Buffer to collect streaming AI suggestions
        # Run the AI task, connecting the chunk handler to append to the buffer, and the done handler.
        self._run_ai_task(prompt, lambda chunk: self.pending_ai_suggestions.append(chunk), self.on_ai_suggestions_done)
    
    def on_ai_suggestions_done(self):
        """
        Callback method executed when the AI keyword suggestions task completes.
        Processes the AI response, parses suggestions, and presents them in a dialog
        for the user to select and add to their keyword list.
        """
        self._set_ui_busy(False) # Reset UI state
        self.label_status.setText(f"{T['status']} {T['ready']}") # Update status
        self.status_animation.stop() # Stop status label animation
        self.label_status.setStyleSheet("") # Reset status label stylesheet
        
        full_response = "".join(self.pending_ai_suggestions) # Combine all streaming chunks
        # Parse suggestions: split by newline and filter out empty lines.
        suggestions = [line.strip() for line in full_response.split('\n') if line.strip()]
        
        dialog = SuggestionsDialog(suggestions, self) # Create and show the suggestions dialog
        if dialog.exec(): # If the user accepts the dialog (clicks "Add Selected")
            for kw in dialog.get_selected(): # Get the keywords selected by the user
                if kw and not self.list_keywords.findItems(kw, Qt.MatchFlag.MatchExactly): # Avoid duplicates
                    # Validate suggested regex if regex mode is on, logging any invalid ones.
                    if REGEX_MODE_GLOBAL:
                        try:
                            re.compile(kw)
                        except re.error as e:
                            self.log_output.append(f"Skipping invalid suggested regex: '{kw}' - {e}")
                            continue
                    self.list_keywords.addItem(kw) # Add valid selected keywords to the main list
            self._update_keyword_stats() # Update keyword count
            self._save_keywords_to_config() # Persist newly added keywords

    def _prepare_ai_log_output(self, header: str) -> Optional[str]:
        """
        Helper method to prepare the log content for AI analysis.
        Checks if there's any content in the log_output and appends a header for clarity.
        """
        if not (log_content := self.log_output.toPlainText().strip()):
            QMessageBox.warning(self, T["title"], T["no_logs_to_analyze"])
            return None # Return None if no log content to analyze
        self.log_output.append(header) # Append the specific AI header to the log output
        return log_content # Return the content for AI processing

    def ai_summarize_results(self):
        """
        Triggers an AI task to summarize the current extracted results and application logs.
        The AI response is streamed directly into the `log_output` QTextEdit.
        """
        if log_content := self._prepare_ai_log_output(T["ai_summary_log_header"]):
            # Format the prompt using the configurable template and the current log content.
            prompt = PROMPT_SUMMARIZE_RESULTS_GLOBAL.format(log_content=log_content)
            # Run the AI task, connecting the chunk handler to insert text, and the done handler.
            self._run_ai_task(prompt, self.log_output.insertPlainText, self.on_ai_task_finished)

    def ai_detect_anomalies(self):
        """
        Triggers an AI task to detect anomalies or suspicious patterns within the
        extracted log data. The AI response is streamed directly into the `log_output` QTextEdit.
        """
        if log_content := self._prepare_ai_log_output(T["ai_anomaly_log_header"]):
            # Format the prompt using the configurable template and the current log content.
            prompt = PROMPT_DETECT_ANOMALIES_GLOBAL.format(log_content=log_content)
            # Run the AI task, connecting the chunk handler to insert text, and the done handler.
            self._run_ai_task(prompt, self.log_output.insertPlainText, self.on_ai_task_finished)

    def ai_analyze_credentials(self):
        """
        Triggers an AI task to analyze and filter high-value credentials from the
        extracted log data. The AI response is streamed directly into the `log_output` QTextEdit.
        """
        if log_content := self._prepare_ai_log_output(T["ai_analysis_log_header"]):
            # Format the prompt using the configurable template and the current log content.
            prompt = PROMPT_ANALYZE_CREDENTIALS_GLOBAL.format(log_content=log_content)
            # Run the AI task, connecting the chunk handler to insert text, and the done handler.
            self._run_ai_task(prompt, self.log_output.insertPlainText, self.on_ai_task_finished)

    def on_ai_task_finished(self):
        """
        Callback method executed when any AI task (summarization, anomaly detection, credential analysis) completes.
        Resets the UI from the busy state and updates the status message.
        """
        self._set_ui_busy(False) # Reset UI state
        self.label_status.setText(f"{T['status']} {T['ready']}") # Update status
        self.status_animation.stop() # Stop status label animation
        self.label_status.setStyleSheet("") # Reset status label stylesheet

    def on_ai_error(self, error_message: str):
        """
        Handles errors that occur during AI service calls.
        Resets the UI, displays an error message in a pop-up, and logs it to the output area.
        """
        self._set_ui_busy(False) # Reset UI state
        self.label_status.setText(f"{T['status']} {T['ready']}") # Update status
        self.status_animation.stop() # Stop status label animation
        self.label_status.setStyleSheet("") # Reset status label stylesheet
        QMessageBox.critical(self, T["ai_error_title"], error_message) # Show critical error pop-up
        self.log_output.append(f"\n--- AI ERROR ---\n{error_message}\n") # Log the error message

    # --- Helper & UI Update Methods —————————————————————————————————
    def _set_ui_busy(self, is_busy: bool):
        """
        Enables or disables various UI elements based on whether the application
        is currently busy with a long-running task (file processing or AI query).
        Also sets the cursor to a wait cursor when busy.
        """
        self.btn_start.setEnabled(not is_busy) # Disable Start button when busy
        # Enable Cancel button only if busy and an extraction thread exists.
        self.btn_cancel.setEnabled(is_busy and self.thread is not None) 
        
        # Disable all AI-related buttons when busy.
        self.btn_ai_suggest.setEnabled(not is_busy)
        self.btn_ai_summarize.setEnabled(not is_busy)
        self.btn_ai_anomalies.setEnabled(not is_busy)
        
        # Enable AI analysis button only if there's log content AND not busy.
        self.btn_ai_analyze.setEnabled(bool(self.log_output.toPlainText().strip()) and not is_busy)
        
        # Change cursor to wait cursor when busy, standard arrow when ready.
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor if is_busy else Qt.CursorShape.ArrowCursor)

    def _animate_status_label(self, color: QColor):
        """Applies a pulsating animation to the status label's text color."""
        self.label_status.setStyleSheet(f"color: {color.name()}; font-weight: bold;")

    def update_file_size(self):
        """
        Calculates and updates the displayed total size of all currently loaded log files.
        Also toggles the visibility of the file list versus the drag-and-drop instruction label.
        """
        # Sum the sizes of all files in the list, ensuring files exist before getting their size.
        total_size = sum(Path(self.list_files.item(i).text()).stat().st_size for i in range(self.list_files.count()) if Path(self.list_files.item(i).text()).exists())
        
        # Format the size into a human-readable string (bytes, KB, MB, GB).
        size_str = f"{total_size/1024**3:.2f} GB" if total_size > 1024**3 else \
                   f"{total_size/1024**2:.2f} MB" if total_size > 1024**2 else \
                   f"{total_size/1024:.2f} KB" if total_size > 1024 else \
                   f"{total_size} bytes"
        self.label_file_size.setText(T["file_size"].format(size=size_str))
        
        # If no files are loaded, show the drag-drop instruction; otherwise, show the file list.
        is_empty = self.list_files.count() == 0
        self.list_files.setVisible(not is_empty)
        self.drag_drop_label.setVisible(is_empty)

    def _update_keyword_stats(self):
        """Updates the displayed count of keywords in the keyword statistics label."""
        self.label_kw_count.setText(T["kw_stats"].format(count=self.list_keywords.count()))

    def _filter_keywords(self, text: str):
        """
        Filters the keywords displayed in `self.list_keywords` based on the input text.
        Items not matching the filter text are hidden.
        """
        filter_text = text.lower() # Convert filter text to lowercase for case-insensitive matching
        for i in range(self.list_keywords.count()):
            # Hide the item if its text (converted to lowercase) does not contain the filter text.
            self.list_keywords.item(i).setHidden(filter_text not in self.list_keywords.item(i).text().lower())
    
    def _handle_dist_update(self, dist: Dict[str, int]):
        """
        Receives keyword distribution updates from the `ExtractThread`.
        This method acts as a buffer, storing the latest distribution
        until the UI update timer triggers `_perform_batched_update`.
        """
        self.pending_dist_update = dist # Store the received distribution dictionary

    def _perform_batched_update(self):
        """
        Performs a batched update of the results table (`self.table_results`).
        This method is called periodically by `self.update_timer` to ensure smooth UI updates,
        even during high-frequency data changes from the worker thread.
        """
        if self.pending_dist_update is None:
            return # No pending updates, nothing to do
        
        dist = self.pending_dist_update # Get the latest pending distribution
        self.pending_dist_update = None # Clear the pending update immediately

        self.table_results.setSortingEnabled(False) # Temporarily disable sorting during update to prevent visual glitches
        
        total_matches = sum(dist.values()) # Calculate total matches
        self.label_match_count.setText(T["match_stats"].format(count=total_matches)) # Update total matches label
        
        # Sort keyword items by match count in descending order for display.
        sorted_items = sorted(dist.items(), key=lambda x: x[1], reverse=True)
        self.table_results.setRowCount(len(sorted_items) + 1) # Set row count, +1 for the "Total" row
        
        # Populate the table with sorted keyword match data.
        for i, (kw, count) in enumerate(sorted_items):
            self.table_results.setItem(i, 0, QTableWidgetItem(str(count))) # Matches column
            self.table_results.setItem(i, 1, QTableWidgetItem(kw))         # Keyword column
        
        # Add the "Total" row at the end of the table.
        total_item = QTableWidgetItem(str(total_matches))
        kw_item = QTableWidgetItem(T["total"])
        bold_font = QFont()
        bold_font.setBold(True) # Make total row bold
        total_item.setFont(bold_font)
        kw_item.setFont(bold_font)
        self.table_results.setItem(len(sorted_items), 0, total_item)
        self.table_results.setItem(len(sorted_items), 1, kw_item)
        
        self.table_results.setSortingEnabled(True) # Re-enable sorting after update is complete

    def open_results_directory(self):
        """Opens the results output directory in the default file explorer."""
        if RESULTS_GLOBAL.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(RESULTS_GLOBAL.absolute()))) # Open the directory URL
        else:
            QMessageBox.critical(self, T["title"], T["no_results_dir"]) # Error if directory not found

    def export_results(self):
        """
        Exports the current data displayed in the results table to a CSV or text file.
        Includes a header row for clarity.
        """
        if fn_tuple := QFileDialog.getSaveFileName(self, T["export_results"], "", "CSV (*.csv);;Text (*.txt)"):
            if filename := fn_tuple[0]:
                with open(filename, "w", encoding=ENC_GLOBAL) as f:
                    f.write("Keyword,Matches\n") # Write CSV header
                    for i in range(self.table_results.rowCount()):
                        if not self.table_results.isRowHidden(i): # Only export visible rows (if filtered)
                            kw = self.table_results.item(i, 1).text()
                            matches = self.table_results.item(i, 0).text()
                            if kw != T["total"]: # Exclude the "Total" row from keyword export
                                f.write(f'"{kw}",{matches}\n')
    
    def _handle_settings_saved(self, new_settings: Dict[str, Dict[str, str]]):
        """
        Slot to handle the `settings_saved` signal from `SettingsPanel`.
        Updates global configuration, saves to disk, and re-applies theme.
        """
        global cfg_global, ENC_GLOBAL, THEME_GLOBAL, REGEX_MODE_GLOBAL, GEMINI_API_KEY_GLOBAL, GEMINI_MODEL_GLOBAL, \
               PROMPT_SUGGEST_KEYWORDS_GLOBAL, PROMPT_SUMMARIZE_RESULTS_GLOBAL, PROMPT_DETECT_ANOMALIES_GLOBAL, PROMPT_ANALYZE_CREDENTIALS_GLOBAL

        for section, options in new_settings.items():
            for key, value in options.items():
                cfg_global[section][key] = value
        
        # Save updated configuration to the INI file
        with open(INI_PATH, "w", encoding="utf-8") as f:
            cfg_global.write(f)
        
        # Update global variables with the newly saved settings.
        ENC_GLOBAL = cfg_global["General"]["encoding"]
        THEME_GLOBAL = cfg_global["General"]["theme"]
        REGEX_MODE_GLOBAL = cfg_global["General"].getboolean("regex_mode", False)
        GEMINI_API_KEY_GLOBAL = cfg_global["Gemini"]["api_key"]
        GEMINI_MODEL_GLOBAL = cfg_global["Gemini"]["model"]
        PROMPT_SUGGEST_KEYWORDS_GLOBAL = cfg_global["Gemini"]["prompt_suggest_keywords"]
        PROMPT_SUMMARIZE_RESULTS_GLOBAL = cfg_global["Gemini"]["prompt_summarize_results"]
        PROMPT_DETECT_ANOMALIES_GLOBAL = cfg_global["Gemini"]["prompt_detect_anomalies"]
        PROMPT_ANALYZE_CREDENTIALS_GLOBAL = cfg_global["Gemini"]["prompt_analyze_credentials"]
        
        self.apply_theme(THEME_GLOBAL) # Re-apply theme in case it was changed
        QMessageBox.information(self, T["title"], T["settings_saved_message"])


def main():
    """Main entry point for the application. Initializes and runs the PyQt application."""
    app = QApplication(sys.argv) # Create the QApplication instance
    win = MainWindow()           # Create the main window instance
    win.show()                   # Display the main window
    sys.exit(app.exec())         # Start the PyQt event loop and exit when done

if __name__ == "__main__":
    main()
