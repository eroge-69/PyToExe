import sys
import os
import re
import time
from datetime import datetime
from threading import Thread, Event
import sqlite3
import json
import hashlib

import numpy as np
import pandas as pd
import joblib
import easyocr
import cv2
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from difflib import SequenceMatcher

# PDF support (optional - will work without these if not installed)
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("PDF support not available. Install pdfplumber for PDF file support.")

from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread, QMetaType, QDate, QMetaObject, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap, QTextCursor
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                              QLabel, QPushButton, QTextEdit, QSpinBox, QDoubleSpinBox, 
                              QCheckBox, QGroupBox, QFormLayout, QLineEdit, QWidget,
                              QDialog, QDialogButtonBox, QMessageBox, QTableWidget, 
                              QTableWidgetItem, QVBoxLayout,QGridLayout, QHBoxLayout, QFileDialog,
                              QInputDialog, QCalendarWidget, QDateEdit, QComboBox, QSplitter, QTabWidget,
                              QListWidget, QSizePolicy)

# ----------------------------
# Config / defaults
# ----------------------------
EXCEL_DEFAULT = "aug-copy.xlsx"
MODEL_DIR = "models"
CLASSIFIER_PATH = os.path.join(MODEL_DIR, "part_classifier.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "part_vectorizer.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "name_encoder.pkl")
SEARCH_INDEX_PATH = os.path.join(MODEL_DIR, "search_index.pkl")

# Digits-only pattern: first block 5–12 digits, optional dash/space/underscore, last block exactly 4 digits
# We will reformat to XXXXX-XXXX after matching
PART_NUMBER_REGEX = re.compile(r"\b(\d{5,12})[-_\s]?(\d{4})\b")

def normalize_ocr_text(text: str) -> str:
    # Normalize OCR quirks: unify dashes, remove extra whitespace, fix common confusions
    t = text.upper()
    # normalize unicode dashes to '-'
    t = t.replace('\u2013', '-').replace('\u2014', '-').replace('\u2212', '-')
    # common OCR confusions
    t = t.replace('O', '0')  # letter O to zero
    t = t.replace('I', '1')  # I to 1
    t = t.replace('L', '1')  # L to 1
    t = t.replace('S', '5')  # S to 5
    t = t.replace('B', '8')  # B to 8 (sometimes)
    # collapse whitespace
    t = re.sub(r"\s+", " ", t)
    return t

# OCR detection interval (frames) to avoid heavy CPU every frame
DEFAULT_OCR_EVERY_N_FRAMES = 5

# Enhanced OCR Accuracy Configuration
OCR_AUTO_CORRECT_DICT = {
    # Common OCR mistakes to correct part numbers
    '12345-6789': '12345-6789',  # Example mapping
    'ABCDE-1234': '12345-1234',  # Letters to numbers
    '1234S-5678': '12345-5678',  # S to 5
    '1234O-5678': '12340-5678',  # O to 0
    '1234I-5678': '12341-5678',  # I to 1
    '1234L-5678': '12341-5678',  # L to 1
    '1234B-5678': '12348-5678',  # B to 8
    '1234G-5678': '12346-5678',  # G to 6
    '1234Z-5678': '12342-5678',  # Z to 2
    '1234A-5678': '12344-5678',  # A to 4
    '1234E-5678': '12343-5678',  # E to 3
    '1234T-5678': '12347-5678',  # T to 7
    '1234N-5678': '12349-5678',  # N to 9
    '1234U-5678': '12340-5678',  # U to 0
    '1234D-5678': '12340-5678',  # D to 0
}

# Fuzzy matching thresholds
FUZZY_SIMILARITY_THRESHOLD = 0.85
FUZZY_PARTIAL_RATIO_THRESHOLD = 80
FUZZY_TOKEN_SORT_RATIO_THRESHOLD = 75

# OCR confidence thresholds
OCR_HIGH_CONFIDENCE = 0.8
OCR_MEDIUM_CONFIDENCE = 0.6
OCR_LOW_CONFIDENCE = 0.4

# ----------------------------
# Helper: ensure model dir
# ----------------------------
os.makedirs(MODEL_DIR, exist_ok=True)

# ----------------------------
# Worker / Signals
# ----------------------------
class Communicate(QObject):
    frame_ready = pyqtSignal(np.ndarray)
    detection = pyqtSignal(str, str, float)  # part_number, name, confidence
    log = pyqtSignal(str)
    spares_updated = pyqtSignal()  # Signal when spares are updated
    
    def __init__(self):
        super().__init__()
        # Ensure this object is in the main thread
        if QApplication.instance():
            self.moveToThread(QApplication.instance().thread())




# ----------------------------
# Main App
# ----------------------------
class PartScannerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Part Scanner - Stocktake System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        
        # Initialize components
        self._init_db()
        self._init_variables()
        self._build_ui()
        
        # Initialize communication after UI is built
        self.comm = Communicate()
        # Use queued connections for thread safety
        self.comm.frame_ready.connect(self.update_image, Qt.QueuedConnection)
        self.comm.detection.connect(self.show_detection, Qt.QueuedConnection)
        self.comm.log.connect(self.append_log, Qt.QueuedConnection)
        self.comm.spares_updated.connect(self._refresh_spares_views, Qt.QueuedConnection)
        
        # Register QTextCursor for cross-thread communication
        # Use QMetaType to ensure proper registration
        QMetaType.type("QTextCursor")

        # Auto-load models on startup with proper thread handling
        QTimer.singleShot(100, self._load_models_worker)
        
        # Load OCR corrections with proper thread handling
        QTimer.singleShot(200, self._load_ocr_corrections)
        
        # Load admin settings
        self._load_admin_settings()
        
        # Start autosave timer in main thread with longer interval to reduce timer warnings
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self._autosave_state)
        self.autosave_timer.start(1000)  # Every 1 second instead of 100ms
        
        # Stop event for camera thread
        self.stop_event = Event()
        
        # Process frame counter
        self.process_frame_counter = 0
        self.min_text_len = 3
        self.fuzzy_fallback = True
        
        # Load UI state after UI is built
        self._load_ui_state()

    def _init_variables(self):
        self.reader = None  # easyocr.Reader (lazy init)
        self.clf = None  # legacy support
        self.vectorizer = None  # TF-IDF vectorizer
        self.nn = None  # nearest neighbors
        self.index_part_numbers = None  # part numbers for nn
        self.index_names = None  # names for nn
        self.exact_map = {}  # exact part_number -> name mapping
        
        # Camera and OCR
        self.capture = None
        self.cam_thread = None
        self.ocr_every_n = 10  # OCR every N frames
        self.detection_rate_fps = 100  # Detection rate in FPS
        self.draw_boxes = True  # Draw detection boxes
        
        # ML parameters
        self.nn_max_distance = 1  # cosine distance threshold
        self.duplicate_suppress_s = 1.0  # duplicate suppression seconds
        
        # Database
        # self.conn is initialized in _init_db(), don't overwrite it here
        self._undo_stack = []  # recent stock_count IDs for undo
        self._recent_seen = {}  # part_text -> last_emit_ts
        
        # UI elements (created early to avoid errors)
        self.log_text = None
        self.camera_label = None
        self.src_input = None
        self.btn_start_src = None
        self.btn_stop_cam = None
        self.spin_ocr_interval = None
        self.cb_draw_boxes = None
        self.btn_train = None
        self.spin_distance = None
        self.spin_dup_s = None
        self.btn_reset_cam = None
        self.btn_reset_seen = None
        self.btn_reset_models = None

        # btn_undo removed
        self.btn_view_spares = None
        self.btn_view_used = None
        self.btn_view_issued = None
        self.btn_stocktake = None
        self.btn_import_spares_excel = None
        self.btn_data_comparison = None
        self.btn_admin = None
        
        # Admin system variables
        self.admin_password = None
        self.admin_enabled = False
        self.locked_areas = set()  # Set of locked area names
        # Custom areas functionality removed
        self.admin_session_active = False
        
        # Session timeout tracking
        self.admin_session_timeout = 15 * 60  # 15 minutes in seconds
        self.admin_last_activity = None
        self.session_timer = None
        
        # OCR and detection constants
        self._PART_NUMBER_REGEX = re.compile(r"(\d{5,12})[-_\s]?(\d{4})")

    def _normalize_part_number_str(self, value: str) -> str:
        """Normalize arbitrary text to canonical part number format XXXXX-XXXX.
        Returns original stripped value if no pattern match found."""
        try:
            if value is None:
                return ""
            # unify dashes/underscores/spaces
            text = re.sub(r"[\s_]+", "-", text)
            m = self._PART_NUMBER_REGEX.search(text)
            if not m:
                # Try global pattern as fallback
                m2 = PART_NUMBER_REGEX.search(text)
                if not m2:
                    return text
                normalized = f"{m2.group(1)}-{m2.group(2)}"
                if normalized != text:
                    self.append_log(f"Normalize PN: '{text}' -> '{normalized}'")
                return normalized
            normalized = f"{m.group(1)}-{m.group(2)}"
            if normalized != text:
                self.append_log(f"Normalize PN: '{text}' -> '{normalized}'")
            return normalized
        except Exception:
            return str(value).strip() if value is not None else ""

    def _parse_quantity_value(self, value) -> int:
        """Parse a quantity from diverse cell contents.
        Accepts numbers, numeric strings, and strings with units like '25 EA' or 'Qty: 10'.
        Returns 0 if not parseable."""
        try:
            if value is None:
                return 0
            # If numeric
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return int(value)
            s = str(value).strip()
            if s == "" or s.lower() == "nan":
                return 0
            # Find first integer in the string
            m = re.search(r"(-?\d+)", s)
            if m:
                return int(m.group(1))
            return 0
        except Exception:
            return 0

    def _sanitize_name(self, name: str, part_number: str) -> str:
        """Remove any appearance of the part number (in common variants) from a name/description field.
        Trims separators and whitespace after removal."""
        try:
            if not name:
                return ""
            if not part_number:
                return name.strip()
            text = str(name)
            pn = str(part_number)
            # Build variants: with dash, without dash, with spaces/underscores
            pn_variants = set()
            pn_variants.add(pn)
            pn_compact = pn.replace('-', '')
            pn_variants.add(pn_compact)
            pn_variants.add(pn.replace('-', ' '))
            pn_variants.add(pn.replace('-', '_'))
            # Also consider any digits-only segments of the PN
            m = self._PART_NUMBER_REGEX.search(pn)
            if m:
                pn_variants.add(f"{m.group(1)}{m.group(2)}")
            # Remove case-insensitively
            for var in sorted(pn_variants, key=len, reverse=True):
                if not var:
                    continue
                text = re.sub(re.escape(var), '', text, flags=re.IGNORECASE)
            # Clean leftover separators
            text = re.sub(r"[-_]+", ' ', text)
            text = re.sub(r"\s+", ' ', text).strip()
            return text
        except Exception:
            return str(name).strip()

    def _is_db_ready(self):
        """Check if database is ready for operations"""
        if self.conn is None:
            self.append_log("Database not initialized. Please restart the application.")
            return False
        try:
            # Test the connection
            cur = self.conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
            return True
        except Exception as e:
            self.append_log(f"Database connection error: {e}")
            return False

    def _normalize_ocr_text(self, text):
        """Normalize OCR text to correct common errors with advanced techniques"""
        if not text:
            return ""
        
        # Advanced OCR error corrections
        advanced_replacements = {
            # Common OCR errors: O->0, I/L->1, S->5, B->8
            'O': '0', 'o': '0',
            'I': '1', 'i': '1', 'L': '1', 'l': '1',
            'S': '5', 's': '5',
            'B': '8', 'b': '8',
            'G': '6', 'g': '6',
            'Z': '2', 'z': '2',
            # Additional common errors
            'A': '4', 'a': '4',  # A often misread as 4
            'E': '3', 'e': '3',  # E sometimes as 3
            'T': '7', 't': '7',  # T occasionally as 7
            'N': '9', 'n': '9',  # N sometimes as 9
            'U': '0', 'u': '0',  # U as 0
            'D': '0', 'd': '0',  # D as 0
        }
        
        # Apply advanced replacements
        for old, new in advanced_replacements.items():
            text = text.replace(old, new)
        
        # Remove common OCR artifacts
        text = re.sub(r'[^\w\d\-_\s]', '', text)  # Remove special characters except allowed ones
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        
        # Normalize separators (handle various formats)
        text = re.sub(r'[-_\s]+', '-', text)
        
        # Handle common OCR patterns
        text = re.sub(r'(\d+)[\s\-_]*(\d{4})', r'\1-\2', text)  # Ensure proper format
        
        # Remove leading/trailing separators
        text = text.strip('-')
        
        return text

    def _enhanced_ocr_correction(self, text):
        """Enhanced OCR correction using auto-correct dictionary and fuzzy matching"""
        if not text:
            return text, 0.0
        
        original_text = text
        correction_confidence = 0.0
        
        # Step 1: Direct auto-correct dictionary lookup
        if text in OCR_AUTO_CORRECT_DICT:
            corrected_text = OCR_AUTO_CORRECT_DICT[text]
            correction_confidence = 0.95  # High confidence for exact matches
            self.append_log(f"Auto-correct applied: {text} -> {corrected_text}")
            return corrected_text, correction_confidence
        
        # Step 2: Pattern-based corrections
        corrected_text = self._apply_pattern_corrections(text)
        if corrected_text != text:
            correction_confidence = 0.85
            self.append_log(f"Pattern correction applied: {text} -> {corrected_text}")
            return corrected_text, correction_confidence
        
        # Step 3: Fuzzy matching against known part numbers
        fuzzy_result = self._fuzzy_match_part_number(text)
        if fuzzy_result:
            corrected_text, similarity_score = fuzzy_result
            correction_confidence = similarity_score * 0.8  # Scale down fuzzy confidence
            self.append_log(f"Fuzzy match found: {text} -> {corrected_text} (similarity: {similarity_score:.3f})")
            return corrected_text, correction_confidence
        
        return original_text, correction_confidence

    def _apply_pattern_corrections(self, text):
        """Apply pattern-based corrections to OCR text"""
        # Common OCR patterns that need correction
        pattern_corrections = [
            (r'(\d{4,11})[O0](\d{4})', r'\g<1>0\2'),  # Fix O/0 confusion in middle
            (r'(\d{4,11})[I1](\d{4})', r'\g<1>1\2'),  # Fix I/1 confusion in middle
            (r'(\d{4,11})[S5](\d{4})', r'\g<1>5\2'),  # Fix S/5 confusion in middle
            (r'(\d{4,11})[B8](\d{4})', r'\g<1>8\2'),  # Fix B/8 confusion in middle
            (r'(\d{4,11})[G6](\d{4})', r'\g<1>6\2'),  # Fix G/6 confusion in middle
            (r'(\d{4,11})[Z2](\d{4})', r'\g<1>2\2'),  # Fix Z/2 confusion in middle
            (r'(\d{4,11})[A4](\d{4})', r'\g<1>4\2'),  # Fix A/4 confusion in middle
            (r'(\d{4,11})[E3](\d{4})', r'\g<1>3\2'),  # Fix E/3 confusion in middle
            (r'(\d{4,11})[T7](\d{4})', r'\g<1>7\2'),  # Fix T/7 confusion in middle
            (r'(\d{4,11})[N9](\d{4})', r'\g<1>9\2'),  # Fix N/9 confusion in middle
            (r'(\d{4,11})[U0](\d{4})', r'\g<1>0\2'),  # Fix U/0 confusion in middle
            (r'(\d{4,11})[D0](\d{4})', r'\g<1>0\2'),  # Fix D/0 confusion in middle
        ]
        
        corrected_text = text
        for pattern, replacement in pattern_corrections:
            corrected_text = re.sub(pattern, replacement, corrected_text)
        
        return corrected_text

    def _fuzzy_match_part_number(self, text):
        """Fuzzy match OCR text against known part numbers in database"""
        try:
            if not self._is_db_ready():
                return None
            
            cur = self.conn.cursor()
            cur.execute("SELECT part_number FROM spares")
            known_parts = [row[0] for row in cur.fetchall()]
            
            if not known_parts:
                return None
            
            best_match = None
            best_score = 0.0
            
            for known_part in known_parts:
                # Use SequenceMatcher for similarity
                similarity = SequenceMatcher(None, text, known_part).ratio()
                
                if similarity > best_score and similarity >= FUZZY_SIMILARITY_THRESHOLD:
                    best_score = similarity
                    best_match = known_part
            
            if best_match:
                return best_match, best_score
            
            return None
        except Exception as e:
            self.append_log(f"Fuzzy matching error: {e}")
            return None

    def _store_detection_result(self, original_text, corrected_text, correction_confidence, ocr_confidence):
        """Store detection results in database for analysis and improvement"""
        try:
            if not self._is_db_ready():
                return
            
            cur = self.conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ocr_detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    original_text TEXT,
                    corrected_text TEXT,
                    correction_applied BOOLEAN,
                    ocr_confidence REAL,
                    correction_confidence REAL,
                    final_confidence REAL,
                    detection_method TEXT
                )
            """)
            
            correction_applied = original_text != corrected_text
            final_confidence = (ocr_confidence + correction_confidence) / 2
            detection_method = "auto_correct" if correction_applied else "direct_ocr"
            
            cur.execute("""
                INSERT INTO ocr_detections 
                (original_text, corrected_text, correction_applied, ocr_confidence, 
                 correction_confidence, final_confidence, detection_method)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (original_text, corrected_text, correction_applied, ocr_confidence, 
                  correction_confidence, final_confidence, detection_method))
            
            self.conn.commit()
            
        except Exception as e:
            self.append_log(f"Failed to store detection result: {e}")

    def _get_ocr_statistics(self):
        """Get OCR accuracy statistics from stored detections"""
        try:
            if not self._is_db_ready():
                return {}
            
            cur = self.conn.cursor()
            cur.execute("""
                SELECT 
                    COUNT(*) as total_detections,
                    SUM(CASE WHEN correction_applied = 1 THEN 1 ELSE 0 END) as corrections_applied,
                    AVG(ocr_confidence) as avg_ocr_confidence,
                    AVG(correction_confidence) as avg_correction_confidence,
                    AVG(final_confidence) as avg_final_confidence,
                    detection_method,
                    COUNT(*) as method_count
                FROM ocr_detections 
                GROUP BY detection_method
            """)
            
            results = cur.fetchall()
            stats = {
                'total_detections': 0,
                'corrections_applied': 0,
                'avg_ocr_confidence': 0.0,
                'avg_correction_confidence': 0.0,
                'avg_final_confidence': 0.0,
                'methods': {}
            }
            
            for row in results:
                stats['methods'][row[5]] = {
                    'count': row[6],
                    'avg_confidence': row[4]
                }
            
            return stats
            
        except Exception as e:
            self.append_log(f"Failed to get OCR statistics: {e}")
            return {}

    def _show_ocr_statistics(self):
        """Show OCR accuracy statistics dialog"""
        try:
            stats = self._get_ocr_statistics()
            
            dlg = QDialog(self)
            dlg.setWindowTitle("OCR Accuracy Statistics")
            dlg.setMinimumSize(500, 400)
            
            layout = QVBoxLayout()
            
            # Title
            title = QLabel("📊 OCR Detection Statistics")
            title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3; margin-bottom: 10px;")
            layout.addWidget(title)
            
            # Statistics text
            stats_text = QTextEdit()
            stats_text.setReadOnly(True)
            
            if not stats or not stats.get('methods'):
                stats_text.setPlainText("No OCR detection data available yet.\n\nStart scanning parts to collect statistics.")
            else:
                report = "🔍 OCR Detection Report\n"
                report += "=" * 40 + "\n\n"
                
                total_detections = sum(method['count'] for method in stats['methods'].values())
                corrections = sum(method['count'] for method_name, method in stats['methods'].items() 
                                if 'auto_correct' in method_name)
                
                report += f"📈 Total Detections: {total_detections}\n"
                report += f"🔧 Corrections Applied: {corrections}\n"
                report += f"📊 Correction Rate: {(corrections/total_detections*100):.1f}%\n\n"
                
                report += "📋 Detection Methods:\n"
                report += "-" * 25 + "\n"
                
                for method_name, method_data in stats['methods'].items():
                    confidence = method_data.get('avg_confidence', 0)
                    count = method_data.get('count', 0)
                    percentage = (count/total_detections*100) if total_detections > 0 else 0
                    
                    method_display = "Auto-Correct" if "auto_correct" in method_name else "Direct OCR"
                    report += f"• {method_display}: {count} ({percentage:.1f}%) - Avg Confidence: {confidence:.3f}\n"
                
                report += "\n💡 Tips for Better Accuracy:\n"
                report += "-" * 25 + "\n"
                report += "• Ensure good lighting conditions\n"
                report += "• Keep camera steady and focused\n"
                report += "• Clean part labels before scanning\n"
                report += "• Use consistent scanning distance\n"
                report += "• Check auto-correct suggestions\n"
                
                stats_text.setPlainText(report)
            
            layout.addWidget(stats_text)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            export_btn = QPushButton("📤 Export Report")
            export_btn.clicked.connect(lambda: self._export_ocr_report(stats))
            export_btn.setStyleSheet("""
                QPushButton {
                    background: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #45a049;
                }
            """)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dlg.accept)
            close_btn.setStyleSheet("""
                QPushButton {
                    background: #607D8B;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: #546E7A;
                }
            """)
            
            button_layout.addWidget(export_btn)
            button_layout.addStretch()
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            dlg.setLayout(layout)
            
            dlg.exec_()
            # Auto-logout when exiting Admin dialog
            self.admin_session_active = False
            
        except Exception as e:
            self.append_log(f"Failed to show OCR statistics: {e}")
            QMessageBox.critical(self, "Error", f"Failed to show OCR statistics: {e}")

    def _export_ocr_report(self, stats):
        """Export OCR statistics report to file"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export OCR Report", "ocr_report.txt", "Text Files (*.txt)"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write("OCR Detection Report\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    if stats and stats.get('methods'):
                        total_detections = sum(method['count'] for method in stats['methods'].values())
                        corrections = sum(method['count'] for method_name, method in stats['methods'].items() 
                                        if 'auto_correct' in method_name)
                        
                        f.write(f"Total Detections: {total_detections}\n")
                        f.write(f"Corrections Applied: {corrections}\n")
                        f.write(f"Correction Rate: {(corrections/total_detections*100):.1f}%\n\n")
                        
                        f.write("Detection Methods:\n")
                        f.write("-" * 25 + "\n")
                        
                        for method_name, method_data in stats['methods'].items():
                            confidence = method_data.get('avg_confidence', 0)
                            count = method_data.get('count', 0)
                            percentage = (count/total_detections*100) if total_detections > 0 else 0
                            
                            method_display = "Auto-Correct" if "auto_correct" in method_name else "Direct OCR"
                            f.write(f"{method_display}: {count} ({percentage:.1f}%) - Avg Confidence: {confidence:.3f}\n")
                    else:
                        f.write("No OCR detection data available.\n")
                
                self.append_log(f"OCR report exported to: {filename}")
                QMessageBox.information(self, "Success", f"OCR report exported to:\n{filename}")
                
        except Exception as e:
            self.append_log(f"Failed to export OCR report: {e}")
            QMessageBox.critical(self, "Error", f"Failed to export OCR report: {e}")

    def _add_ocr_correction(self, incorrect_text, correct_text):
        """Add a new OCR correction to the auto-correct dictionary"""
        try:
            # Add to runtime dictionary
            OCR_AUTO_CORRECT_DICT[incorrect_text] = correct_text
            
            # Store in database for persistence
            if self._is_db_ready():
                cur = self.conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS ocr_corrections (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        incorrect_text TEXT UNIQUE,
                        correct_text TEXT,
                        added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        usage_count INTEGER DEFAULT 0
                    )
                """)
                
                cur.execute("""
                    INSERT OR REPLACE INTO ocr_corrections (incorrect_text, correct_text, usage_count)
                    VALUES (?, ?, 1)
                """, (incorrect_text, correct_text))
                
                self.conn.commit()
                self.append_log(f"OCR correction added: '{incorrect_text}' -> '{correct_text}'")
                
        except Exception as e:
            self.append_log(f"Failed to add OCR correction: {e}")

    def _load_ocr_corrections(self):
        """Load OCR corrections from database"""
        try:
            if not self._is_db_ready():
                return
            
            cur = self.conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ocr_corrections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incorrect_text TEXT UNIQUE,
                    correct_text TEXT,
                    added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    usage_count INTEGER DEFAULT 0
                )
            """)
            
            cur.execute("SELECT incorrect_text, correct_text FROM ocr_corrections")
            corrections = cur.fetchall()
            
            for incorrect, correct in corrections:
                OCR_AUTO_CORRECT_DICT[incorrect] = correct
            
            self.append_log(f"Loaded {len(corrections)} OCR corrections from database")
            
        except Exception as e:
            self.append_log(f"Failed to load OCR corrections: {e}")

    def _show_ocr_correction_dialog(self):
        """Show dialog to add new OCR corrections"""
        if "ocr_corrections" in self.locked_areas:
            QMessageBox.warning(self, "Access Denied", "OCR corrections are currently locked.")
            return
        try:
            dlg = QDialog(self)
            dlg.setWindowTitle("Add OCR Correction")
            dlg.setMinimumSize(400, 200)
            
            layout = QVBoxLayout()
            
            # Title
            title = QLabel("🔧 Add OCR Auto-Correction")
            title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FF9800; margin-bottom: 10px;")
            layout.addWidget(title)
            
            # Form
            form_layout = QFormLayout()
            
            incorrect_edit = QLineEdit()
            incorrect_edit.setPlaceholderText("Enter incorrect OCR text")
            form_layout.addRow("Incorrect Text:", incorrect_edit)
            
            correct_edit = QLineEdit()
            correct_edit.setPlaceholderText("Enter correct part number")
            form_layout.addRow("Correct Text:", correct_edit)
            
            layout.addLayout(form_layout)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            add_btn = QPushButton("➕ Add Correction")
            add_btn.clicked.connect(lambda: self._handle_add_correction(dlg, incorrect_edit.text(), correct_edit.text()))
            add_btn.setStyleSheet("""
                QPushButton {
                    background: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #45a049;
                }
            """)
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(dlg.reject)
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background: #607D8B;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: #546E7A;
                }
            """)
            
            button_layout.addWidget(add_btn)
            button_layout.addStretch()
            button_layout.addWidget(cancel_btn)
            
            layout.addLayout(button_layout)
            dlg.setLayout(layout)
            
            dlg.exec_()
            
        except Exception as e:
            self.append_log(f"Failed to show OCR correction dialog: {e}")
            QMessageBox.critical(self, "Error", f"Failed to show OCR correction dialog: {e}")

    def _handle_add_correction(self, dialog, incorrect_text, correct_text):
        """Handle adding a new OCR correction"""
        if not incorrect_text.strip() or not correct_text.strip():
            QMessageBox.warning(self, "Warning", "Please enter both incorrect and correct text.")
            return
        
        try:
            self._add_ocr_correction(incorrect_text.strip(), correct_text.strip())
            QMessageBox.information(self, "Success", f"OCR correction added:\n'{incorrect_text}' → '{correct_text}'")
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add correction: {e}")

    def _build_ui(self):
        # Dark Theme Panel-Based Button Layout (2x2 Grid)
        top_button_container = QWidget()
        top_button_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FF6B6B, stop:0.25 #4ECDC4, stop:0.5 #45B7D1, stop:0.75 #96CEB4, stop:1 #FFEAA7);
                border-radius: 15px;
                padding: 8px;
                border: 3px solid qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF9FF3, stop:1 #54A0FF);
            }
        """)
        
        top_button_layout = QHBoxLayout(top_button_container)
        top_button_layout.setContentsMargins(12, 12, 12, 12)
        top_button_layout.setSpacing(10)
        
        # Panel 1: Stock Management (Top-Left)
        stock_panel = QWidget()
        stock_panel.setStyleSheet("""
            QWidget {
                  background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4ECDC4, stop:0.5 #44A08D, stop:1 #093637);
                border: 3px solid #26D0CE;
                border-radius: 15px;
                padding: 8px;
            }
        """)
        stock_layout = QVBoxLayout(stock_panel)
        stock_layout.setContentsMargins(12, 12, 12, 12)
        stock_layout.setSpacing(10)
        
        stock_title = QLabel("Stock Management")
        stock_title.setStyleSheet("""
            QLabel {
                 background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #063062, stop:0.5 #fecfef, stop:1 #2498c1);
                color: #2d3436;
                font-weight: bold;
                font-size: 32px;
                padding: 15px;
                border-radius: 12px;
                margin: 5px;
                border: 2px solid #00b894;
                text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
            }
        """)
        stock_title.setAlignment(Qt.AlignCenter)
        stock_layout.addWidget(stock_title)
        
        # Stock buttons in 2x2 grid
        stock_grid = QGridLayout()
        stock_grid.setSpacing(8)
        
        self.btn_view_spares = QPushButton("📦 View Spares")
        self.btn_view_spares.setMinimumSize(100, 35)
        self.btn_view_spares.clicked.connect(self._view_spares_dialog)
        # Using enhanced styles from styles.css
        
        self.btn_view_used = QPushButton("📤 View Used")
        self.btn_view_used.setMinimumSize(100, 35)
        self.btn_view_used.clicked.connect(self._view_spares_used_dialog)
        # Using enhanced styles from styles.css
        
        self.btn_view_issued = QPushButton("📋 View Issued")
        self.btn_view_issued.setMinimumSize(100, 35)
        self.btn_view_issued.clicked.connect(self._view_spares_issued_dialog)
        # Using enhanced styles from styles.css
        
        self.btn_stocktake = QPushButton("📊 Stocktake")
        self.btn_stocktake.setMinimumSize(100, 35)
        self.btn_stocktake.clicked.connect(self._stocktake_dialog)
        # Using enhanced styles from styles.css
        
        stock_grid.addWidget(self.btn_view_spares, 0, 0)
        stock_grid.addWidget(self.btn_view_used, 0, 1)
        stock_grid.addWidget(self.btn_view_issued, 1, 0)
        stock_grid.addWidget(self.btn_stocktake, 1, 1)
        stock_layout.addLayout(stock_grid)
        
        # Panel 2: Model Operations (Top-Right)
        model_panel = QWidget()
        model_panel.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4ECDC4, stop:0.5 #44A08D, stop:1 #093637);
                border: 3px solid #26D0CE;
                border-radius: 15px;
                padding: 8px;
            }
        """)
        model_layout = QVBoxLayout(model_panel)
        model_layout.setContentsMargins(12, 12, 12, 12)
        model_layout.setSpacing(10)
        
        model_title = QLabel("Model Operations")
        model_title.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #063062, stop:0.5 #fecfef, stop:1 #2498c1);
                color: #2d3436;
                font-weight: bold;
                font-size: 32px;
                padding: 15px;
                border-radius: 12px;
                margin: 5px;
                border: 2px solid #00b894;
                text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
            }
        """)
        model_title.setAlignment(Qt.AlignCenter)
        model_layout.addWidget(model_title)
        
        self.btn_train = QPushButton("🚀 Train Model")
        self.btn_train.setMinimumSize(100, 35)
        self.btn_train.clicked.connect(self.train_model)
        # Using enhanced styles from styles.css
        
        self.btn_model_info = QPushButton("ℹ️ Model Info")
        self.btn_model_info.setMinimumSize(100, 35)
        self.btn_model_info.clicked.connect(self.show_model_info)
        # Using enhanced styles from styles.css
        
        model_layout.addWidget(self.btn_train)
        model_layout.addWidget(self.btn_model_info)
        
        # Panel 3: Data Handling (Bottom-Left)
        data_panel = QWidget()
        data_panel.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4ECDC4, stop:0.5 #44A08D, stop:1 #093637);
                border: 3px solid #26D0CE;
                border-radius: 15px;
                padding: 8px;
            }
        """)
        data_layout = QVBoxLayout(data_panel)
        data_layout.setContentsMargins(12, 12, 12, 12)
        data_layout.setSpacing(10)
        
        data_title = QLabel("Data Handling")
        data_title.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #063062, stop:0.5 #fecfef, stop:1 #2498c1);
                color: #2d3436;
                font-weight: bold;
                font-size: 32px;
                padding: 15px;
                border-radius: 12px;
                margin: 5px;
                border: 2px solid #00b894;
                text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
            }
        """)
        data_title.setAlignment(Qt.AlignCenter)
        data_layout.addWidget(data_title)
        
        # Data buttons in 2x2 grid
        data_grid = QGridLayout()
        data_grid.setSpacing(8)
        
        self.btn_import_spares_excel = QPushButton("📥 Import Excel")
        self.btn_import_spares_excel.setMinimumSize(100, 35)
        self.btn_import_spares_excel.clicked.connect(self._import_spares_excel)
        # Using enhanced styles from styles.css
        
        self.btn_load_excel = QPushButton("📚 Load Data")
        self.btn_load_excel.setMinimumSize(100, 35)
        self.btn_load_excel.clicked.connect(self.load_excel)
        # Using enhanced styles from styles.css
        
        # Removed Reset Cache button
        
        self.btn_data_comparison = QPushButton("📊 Data Comparison")
        self.btn_data_comparison.setMinimumSize(100, 35)
        self.btn_data_comparison.clicked.connect(self._data_comparison_dialog)
        # Using enhanced styles from styles.css
        
        self.btn_admin = QPushButton("🔒 Admin")
        self.btn_admin.setMinimumSize(100, 35)
        self.btn_admin.clicked.connect(self._admin_login_prompt)
        # Using enhanced styles from styles.css
        
        # Removed Reset Models button
        
        data_grid.addWidget(self.btn_import_spares_excel, 0, 0)
        data_grid.addWidget(self.btn_load_excel, 0, 1)
        data_grid.addWidget(self.btn_data_comparison, 1, 0)
        data_grid.addWidget(self.btn_admin, 1, 1)
        # Removed reset buttons from data grid
        data_layout.addLayout(data_grid)
        
        # Panel 4: Tools (Bottom-Right)
        tools_panel = QWidget()
        tools_panel.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4ECDC4, stop:0.5 #44A08D, stop:1 #093637);
                border: 3px solid #26D0CE;
                border-radius: 15px;
                padding: 8px;
            }
        """)
        tools_layout = QVBoxLayout(tools_panel)
        tools_layout.setContentsMargins(12, 12, 12, 12)
        tools_layout.setSpacing(10)
        
        tools_title = QLabel("Tools")
        tools_title.setStyleSheet("""
            QLabel {
                 background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #063062, stop:0.5 #fecfef, stop:1 #2498c1);
                color: #2d3436;
                font-weight: bold;
                font-size: 32px;
                padding: 15px;
                border-radius: 12px;
                margin: 5px;
                border: 2px solid #00b894;
                text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
            }
        """)
        tools_title.setAlignment(Qt.AlignCenter)
        tools_layout.addWidget(tools_title)
        
        self.btn_reset_cam = QPushButton("📷 Reset Camera")
        self.btn_reset_cam.setMinimumSize(100, 35)
        self.btn_reset_cam.clicked.connect(self._reset_camera)
        # Using enhanced styles from styles.css
        
        # Undo button removed
        # Using enhanced styles from styles.css
        
        self.btn_ocr_stats = QPushButton("📊 OCR Stats")
        self.btn_ocr_stats.setMinimumSize(100, 35)
        self.btn_ocr_stats.clicked.connect(self._show_ocr_statistics)
        # Using enhanced styles from styles.css
        
        self.btn_ocr_correction = QPushButton("🔧 OCR Corrections")
        self.btn_ocr_correction.setMinimumSize(100, 35)
        self.btn_ocr_correction.clicked.connect(self._show_ocr_correction_dialog)
        # Using enhanced styles from styles.css
        
        tools_layout.addWidget(self.btn_reset_cam)
        # Undo button removed from layout
        tools_layout.addWidget(self.btn_ocr_stats)
        tools_layout.addWidget(self.btn_ocr_correction)
        
        # Add all panels to the main layout
        top_button_layout.addWidget(stock_panel)
        top_button_layout.addWidget(model_panel)
        top_button_layout.addWidget(data_panel)
        top_button_layout.addWidget(tools_panel)
        
        # Initialize training data
        self.df = None
        
        self.main_layout.addWidget(top_button_container)

        # Camera and Logs Layout
        camera_logs_layout = QHBoxLayout()
        
        # Left side: Camera display
        camera_container = QWidget()
        # Allow camera to expand to maximize available space
        camera_container.setMinimumSize(320, 240)
        camera_container.setStyleSheet("border: 2px solid #4CAF50; border-radius: 8px; background: #1a1a1a;")
        
        camera_inner_layout = QVBoxLayout(camera_container)
        camera_inner_layout.setContentsMargins(15, 15, 15, 15)
        
        camera_title = QLabel("📹 Live Camera Feed")
        camera_title.setStyleSheet("color: #4CAF50; font-size: 30px; font-weight: bold; margin-bottom: 15px; padding: 5px;")
        camera_title.setAlignment(Qt.AlignCenter)
        camera_inner_layout.addWidget(camera_title)
        
        self.camera_label = QLabel("Camera Feed")
        self.camera_label.setMinimumSize(600, 400)
        self.camera_label.setStyleSheet("border: 2px solid #333; background: #000; border-radius: 4px;")
        self.camera_label.setAlignment(Qt.AlignCenter)
        camera_inner_layout.addWidget(self.camera_label)
        
        camera_logs_layout.addWidget(camera_container, stretch=2)
        
        # Right side: Advanced Logs Panel
        logs_container = QWidget()
        # Allow logs to expand and shrink; no fixed width caps
        logs_container.setStyleSheet("border: 2px solid #2196F3; border-radius: 8px; background: #1a1a1a;")
        
        logs_inner_layout = QVBoxLayout(logs_container)
        logs_inner_layout.setContentsMargins(15, 15, 15, 15)
        
        # Logs Header
        logs_header = QHBoxLayout()
        logs_title = QLabel("📋 System Logs")
        logs_title.setStyleSheet("color: #2196F3; font-size: 30px; font-weight: bold; padding: 5px;")
        logs_header.addWidget(logs_title)
        
        # Log controls
        btn_clear_log = QPushButton("🗑️")
        btn_clear_log.setToolTip("Clear Log")
        btn_clear_log.setMaximumSize(30, 30)
        btn_clear_log.clicked.connect(lambda: self.log_text.clear())
        btn_clear_log.setStyleSheet("""
            QPushButton {
                background: #ff4444;
                border: none;
                border-radius: 15px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #ff6666;
            }
        """)
        logs_header.addWidget(btn_clear_log)
        
        btn_save_log = QPushButton("💾")
        btn_save_log.setToolTip("Save Log")
        btn_save_log.setMaximumSize(30, 30)
        btn_save_log.clicked.connect(self._save_log)
        btn_save_log.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                border: none;
                border-radius: 15px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #66bb6a;
            }
        """)
        logs_header.addWidget(btn_save_log)
        
        logs_inner_layout.addLayout(logs_header)
        
        # Advanced Log Text Area
        self.log_text = QTextEdit()
        self.log_text.setMinimumHeight(400)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                line-height: 1.4;
                padding: 8px;
            }
            QTextEdit QScrollBar:vertical {
                background: #21262d;
                width: 12px;
                border-radius: 6px;
            }
            QTextEdit QScrollBar::handle:vertical {
                background: #484f58;
                border-radius: 6px;
                min-height: 20px;
            }
            QTextEdit QScrollBar::handle:vertical:hover {
                background: #5a6169;
            }
            QTextEdit QScrollBar::add-line:vertical,
            QTextEdit QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        logs_inner_layout.addWidget(self.log_text)
        
        # Log Status Bar
        log_status_layout = QHBoxLayout()
        
        self.log_status_label = QLabel("Ready")
        self.log_status_label.setStyleSheet("color: #4CAF50; font-size: 10px;")
        log_status_layout.addWidget(self.log_status_label)
        
        self.log_count_label = QLabel("0 entries")
        self.log_count_label.setStyleSheet("color: #888; font-size: 10px;")
        log_status_layout.addWidget(self.log_count_label)
        
        logs_inner_layout.addLayout(log_status_layout)
        
        camera_logs_layout.addWidget(logs_container, stretch=1)
        
        self.main_layout.addLayout(camera_logs_layout)

        # Control panel
        control_panel = QHBoxLayout()
         
        # Left side - camera controls
        left_controls = QVBoxLayout()
         
        # Camera source selection
        camera_source_group = QGroupBox("Camera Source")
        camera_source_layout = QVBoxLayout()
        src_input_layout = QHBoxLayout()
        src_input_layout.addWidget(QLabel("Camera Index/URL:"))
        self.src_input = QLineEdit()
        self.src_input.setPlaceholderText("0 for PC camera, or IP/URL for phone")
        self.src_input.setText("0")
        src_input_layout.addWidget(self.src_input)
        self.btn_start_src = QPushButton("Start Camera")
        self.btn_start_src.setMinimumSize(120, 36)
        self.btn_start_src.setStyleSheet(
            """
            QPushButton {
                background-color: #22c55e;
                color: #0b1117;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                padding: 8px 14px;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
            QPushButton:pressed {
                background-color: #15803d;
            }
            """
        )
        self.btn_start_src.clicked.connect(self._start_camera)
        src_input_layout.addWidget(self.btn_start_src)
        self.btn_stop_cam = QPushButton("Stop Camera")
        self.btn_stop_cam.setMinimumSize(120, 36)
        self.btn_stop_cam.setStyleSheet(
            """
            QPushButton {
                background-color: #ef4444;
                color: #0b1117;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                padding: 8px 14px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:pressed {
                background-color: #b91c1c;
            }
            """
        )
        self.btn_stop_cam.clicked.connect(self.stop_camera)
        src_input_layout.addWidget(self.btn_stop_cam)
        camera_source_layout.addLayout(src_input_layout)
        camera_source_group.setLayout(camera_source_layout)
        left_controls.addWidget(camera_source_group)
         
        # Camera settings
        camera_settings_group = QGroupBox("Camera Settings")
        camera_settings_layout = QVBoxLayout()
         
        # OCR frame interval
        ocr_layout = QHBoxLayout()
        ocr_layout.addWidget(QLabel("OCR Every N Frames:"))
        self.spin_ocr_interval = QSpinBox()
        self.spin_ocr_interval.setRange(1, 30)
        self.spin_ocr_interval.setValue(self.ocr_every_n)
        self.spin_ocr_interval.valueChanged.connect(self._on_ocr_interval_changed)
        self.spin_ocr_interval.setToolTip("Process OCR every N frames (lower = more frequent detection)")
        ocr_layout.addWidget(self.spin_ocr_interval)
        camera_settings_layout.addLayout(ocr_layout)
        
        # Detection rate control
        detection_rate_layout = QHBoxLayout()
        detection_rate_layout.addWidget(QLabel("Detection Rate (FPS):"))
        self.spin_detection_rate = QSpinBox()
        self.spin_detection_rate.setRange(1, 200)
        self.spin_detection_rate.setValue(100)  # Default 100 FPS
        self.spin_detection_rate.valueChanged.connect(self._on_detection_rate_changed)
        self.spin_detection_rate.setToolTip("Detection processing rate in frames per second (higher = faster detection)")
        detection_rate_layout.addWidget(self.spin_detection_rate)
        camera_settings_layout.addLayout(detection_rate_layout)
         
        # Draw boxes
        self.cb_draw_boxes = QCheckBox("Draw Detection Boxes")
        self.cb_draw_boxes.setChecked(self.draw_boxes)
        camera_settings_layout.addWidget(self.cb_draw_boxes)
         
        camera_settings_group.setLayout(camera_settings_layout)
        left_controls.addWidget(camera_settings_group)
         
        # Training controls - Removed (moved to top)
        # Image file scanning - Removed (moved to top)
         
        control_panel.addLayout(left_controls)
         
        # Right side - management controls
        right_controls = QVBoxLayout()
         
        # Detection quality settings
        quality_group = QGroupBox("Detection Quality")
        quality_layout = QVBoxLayout()
         
        # Distance threshold
        dist_layout = QHBoxLayout()
        dist_layout.addWidget(QLabel("Max Distance:"))
        self.spin_distance = QDoubleSpinBox()
        self.spin_distance.setRange(0.1, 1.0)
        self.spin_distance.setValue(self.nn_max_distance)
        self.spin_distance.setSingleStep(0.05)
        self.spin_distance.valueChanged.connect(self._on_distance_changed)
        dist_layout.addWidget(self.spin_distance)
        quality_layout.addLayout(dist_layout)
         
        # Duplicate suppression
        dup_layout = QHBoxLayout()
        dup_layout.addWidget(QLabel("Duplicate Suppress (s):"))
        self.spin_dup_s = QDoubleSpinBox()
        self.spin_dup_s.setRange(0.5, 10.0)
        self.spin_dup_s.setValue(self.duplicate_suppress_s)
        self.spin_dup_s.setSingleStep(0.5)
        self.spin_dup_s.valueChanged.connect(self._on_dup_suppress_changed)
        dup_layout.addWidget(self.spin_dup_s)
        quality_layout.addLayout(dup_layout)
         
        quality_group.setLayout(quality_layout)
        right_controls.addWidget(quality_group)
         
        # Management controls - Removed (moved to top)
         
        control_panel.addLayout(right_controls)
         
        self.main_layout.addLayout(control_panel)
        
        # Add status bar with developer credits
        status_bar = self._create_status_bar()
        self.main_layout.addWidget(status_bar)
         

    def _create_status_bar(self):
        """Create a professional status bar with developer credits"""
        status_container = QWidget()
        status_container.setFixedHeight(30)
        status_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #1e3a8a, stop:0.5 #3b82f6, stop:1 #1e40af);
                border-top: 2px solid #60a5fa;
                color: #ffffff;
            }
        """)
        
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(10, 5, 10, 5)
        status_layout.setSpacing(15)
        
        # Status message (left side)
        self.status_line = QLabel("Ready")
        self.status_line.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #ffffff;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        status_layout.addWidget(self.status_line)
        
        # Spacer to push developer credits to the right
        status_layout.addStretch()
        
        # Developer credits (right side)
        credits_label = QLabel("Created by PHENIAS MANYASHA | Contact: pheniasmore@gmail.com")
        credits_label.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #e0f2fe;
                font-size: 10px;
                font-style: italic;
            }
        """)
        status_layout.addWidget(credits_label)
        
        return status_container
    


    # ----------------------------
    # Persistence / State
    # ----------------------------
    def _init_db(self):
        try:
            self.db_path = os.path.join(MODEL_DIR, "stocktake.db")
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            if self.conn is None:
                raise Exception("Failed to create database connection")
            
            cur = self.conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS stock_counts ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "ts TEXT NOT NULL,"
                "source TEXT NOT NULL,"
                "part_number TEXT NOT NULL,"
                "name TEXT NOT NULL,"
                "quantity INTEGER NOT NULL"
                ")"
            )
            cur.execute(
                "CREATE TABLE IF NOT EXISTS spares ("
                "part_number TEXT PRIMARY KEY,"
                "name TEXT NOT NULL,"
                "quantity INTEGER NOT NULL DEFAULT 0"
                ")"
            )
            # Add quantity column if upgrading an existing DB
            try:
                cur.execute("ALTER TABLE spares ADD COLUMN quantity INTEGER NOT NULL DEFAULT 0")
            except Exception:
                pass

            # Additional transaction tables
            cur.execute(
                "CREATE TABLE IF NOT EXISTS spares_used ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "ts TEXT NOT NULL,"
                "part_number TEXT NOT NULL,"
                "name TEXT NOT NULL,"
                "quantity INTEGER NOT NULL"
                ")"
            )
            cur.execute(
                "CREATE TABLE IF NOT EXISTS spares_issued ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "ts TEXT NOT NULL,"
                "part_number TEXT NOT NULL,"
                "name TEXT NOT NULL,"
                "quantity INTEGER NOT NULL"
                ")"
            )
            self.conn.commit()
            self._undo_stack = []  # store last inserted ids
            print("Database ready.")  # Use print since log_text not ready yet
        except Exception as e:
            print(f"DB init failed: {e}")  # Use print since log_text not ready yet
            import traceback
            traceback.print_exc()
            self.conn = None  # Ensure connection is None on failure

    def _autosave_state(self):
        """Auto-save UI state"""
        try:
            state = {
                'ocr_every_n': self.ocr_every_n,
                'draw_boxes': self.cb_draw_boxes.isChecked() if self.cb_draw_boxes is not None else self.draw_boxes,
                'nn_max_distance': self.nn_max_distance,
                'duplicate_suppress_s': self.duplicate_suppress_s,
                'camera_source': self.src_input.text() if self.src_input is not None else '0',
            }
            with open('ui_state.json', 'w') as f:
                json.dump(state, f)
        except Exception as e:
            pass  # Silent fail for autosave

    def _on_ocr_interval_changed(self, value):
        self.ocr_every_n = value
        self.append_log(f"OCR interval set to {value} frames")

    def _on_distance_changed(self, value):
        self.nn_max_distance = value
        self.append_log(f"Max distance threshold set to {value}")

    def _on_dup_suppress_changed(self, value):
        self.duplicate_suppress_s = value
        self.append_log(f"Duplicate suppression set to {value} seconds")

    def _on_detection_rate_changed(self, value):
        self.detection_rate_fps = value
        self.append_log(f"Detection rate set to {value} FPS")

    def _reset_camera(self):
        if "camera_controls" in self.locked_areas:
            QMessageBox.warning(self, "Access Denied", "Camera controls are currently locked.")
            return
        self.stop_camera()
        self.append_log("Camera reset")

    def _reset_seen_cache(self):
        self._recent_seen.clear()
        self.append_log("Seen cache cleared")

    def _reset_models(self):
        if "backup_restore" in self.locked_areas:
            QMessageBox.warning(self, "Access Denied", "Backup/restore operations are currently locked.")
            return
        try:
            import os
            if os.path.exists(SEARCH_INDEX_PATH):
                os.remove(SEARCH_INDEX_PATH)
            if os.path.exists(CLASSIFIER_PATH):
                os.remove(CLASSIFIER_PATH)
            if os.path.exists(VECTORIZER_PATH):
                os.remove(VECTORIZER_PATH)
            if os.path.exists(ENCODER_PATH):
                os.remove(ENCODER_PATH)
            self.append_log("All models reset")
        except Exception as e:
            self.append_log(f"Reset models failed: {e}")

    def _undo_last(self):
        """Undo last stock count entry"""
        try:
            if not self._is_db_ready():
                self.append_log("Database not ready. Cannot undo.")
                return
            
            if not self._undo_stack:
                self.append_log("Nothing to undo.")
                return
            last_id = self._undo_stack.pop()
            cur = self.conn.cursor()
            cur.execute("DELETE FROM stock_counts WHERE id = ?", (last_id,))
            self.conn.commit()
            self.append_log(f"Undid stock count entry {last_id}")
        except Exception as e:
            self.append_log(f"Undo failed: {e}")

    def _start_camera(self):
        if "camera_controls" in self.locked_areas:
            QMessageBox.warning(self, "Access Denied", "Camera controls are currently locked.")
            return
        source = self.src_input.text().strip()
        if not source:
            self.append_log("Please enter camera source")
            return
        try:
            if source.isdigit():
                source = int(source)
            self.start_camera(source)
        except Exception as e:
            self.append_log(f"Start camera failed: {e}")


    def update_image(self, frame):
        """Update camera image display"""
        try:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.camera_label.setPixmap(pixmap.scaled(self.camera_label.size(), Qt.KeepAspectRatio))
        except Exception as e:
            self.append_log(f"Update image failed: {e}")

    def show_detection(self, part_number, name, confidence):
        """Show detection result"""
        try:
            self.append_log(f"Detected: {part_number} - {name} (confidence: {confidence:.3f})")
            # Prompt for confirmation and quantity entry
            self._prompt_and_save_detection(part_number, name)
        except Exception as e:
            self.append_log(f"Show detection failed: {e}")

    def append_log(self, message):
        """Append message to log with timestamp and advanced formatting"""
        try:
            if self.log_text is None:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
                return
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            # Color coding based on message type
            color = "#c9d1d9"  # Default color
            if "error" in message.lower() or "failed" in message.lower():
                color = "#ff6b6b"  # Red for errors
            elif "success" in message.lower() or "started" in message.lower():
                color = "#4CAF50"  # Green for success
            elif "warning" in message.lower():
                color = "#ffa726"  # Orange for warnings
            elif "detection" in message.lower():
                color = "#42a5f5"  # Blue for detections
            
            # Format the log entry
            log_entry = f'<span style="color: #888;">[{timestamp}]</span> <span style="color: {color};">{message}</span>'
            
            # Add to log text
            self.log_text.append(log_entry)
            
            # Auto-scroll to bottom
            self.log_text.verticalScrollBar().setValue(
                self.log_text.verticalScrollBar().maximum()
            )
            
            # Update status
            if hasattr(self, 'log_status_label'):
                self.log_status_label.setText("Updated")
                self.log_status_label.setStyleSheet("color: #4CAF50; font-size: 10px;")
            
            # Update count
            if hasattr(self, 'log_count_label'):
                count = len(self.log_text.toPlainText().split('\n'))
                self.log_count_label.setText(f"{count} entries")
            
            # Clear status after 2 seconds - ensure timer is created in main thread
            if hasattr(self, 'log_status_label'):
                # Use QMetaObject.invokeMethod to ensure timer is created in main thread
                QMetaObject.invokeMethod(self, "_delayed_clear_log_status", Qt.QueuedConnection)
                
        except Exception as e:
            print(f"Log append failed: {e}")

    @pyqtSlot()
    def _delayed_clear_log_status(self):
        """Create timer in main thread to clear log status"""
        if hasattr(self, 'log_status_label'):
            QTimer.singleShot(2000, self._clear_log_status)
    
    def _clear_log_status(self):
        """Clear log status label"""
        if hasattr(self, 'log_status_label'):
            self.log_status_label.setText("Ready")

    def _refresh_spares_views(self):
        """Refresh all spares-related views when data is updated"""
        try:
            # Refresh current spares dialog if open
            if hasattr(self, '_current_spares_reload_func') and self._current_spares_reload_func:
                self._current_spares_reload_func()
        except Exception as e:
            self.append_log(f"Refresh spares views failed: {e}")

    def _set_date_range(self, from_date, to_date, period):
        """Set date range based on period selection"""
        try:
            today = QDate.currentDate()
            if period == "today":
                from_date.setDate(today)
                to_date.setDate(today)
            elif period == "week":
                # Start of current week (Monday)
                days_since_monday = today.dayOfWeek() - 1
                monday = today.addDays(-days_since_monday)
                from_date.setDate(monday)
                to_date.setDate(today)
            elif period == "month":
                # Start of current month
                first_day = QDate(today.year(), today.month(), 1)
                from_date.setDate(first_day)
                to_date.setDate(today)
            elif period == "all":
                # Set to a very old date and today
                from_date.setDate(QDate(2020, 1, 1))
                to_date.setDate(today)
        except Exception as e:
            self.append_log(f"Set date range failed: {e}")

    def _load_models_worker(self):
        """Background worker to load models"""
        try:
            self.load_models()
        except Exception as e:
            self.append_log(f"Auto-load models failed: {e}")

    def _autosave_state(self):
        """Auto-save UI state"""
        try:
            state = {
                'ocr_every_n': self.ocr_every_n,
                'draw_boxes': self.cb_draw_boxes.isChecked() if self.cb_draw_boxes is not None else self.draw_boxes,
                'nn_max_distance': self.nn_max_distance,
                'duplicate_suppress_s': self.duplicate_suppress_s,
                'camera_source': self.src_input.text() if self.src_input is not None else '0',
            }
            with open('ui_state.json', 'w') as f:
                json.dump(state, f)
        except Exception as e:
            pass  # Silent fail for autosave

    def _load_ui_state(self):
        """Load saved UI state"""
        try:
            if os.path.exists('ui_state.json'):
                with open('ui_state.json', 'r') as f:
                    state = json.load(f)
                self.ocr_every_n = state.get('ocr_every_n', 5)
                self.draw_boxes = state.get('draw_boxes', True)
                self.nn_max_distance = state.get('nn_max_distance', 0.85)
                self.duplicate_suppress_s = state.get('duplicate_suppress_s', 2.0)
                if self.src_input is not None:
                    self.src_input.setText(state.get('camera_source', '0'))
        except Exception as e:
            pass  # Silent fail for state load

    def _import_spares_excel(self):
        """Import spares from Excel file"""
        if "data_sync" in self.locked_areas:
            QMessageBox.warning(self, "Access Denied", "Data sync operations are currently locked.")
            return
        try:
            if not self._is_db_ready():
                self.append_log("Database not ready. Cannot import spares.")
                return
            
            if not self._check_area_access("import"):
                return
            
            filename, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")
            if filename:
                self.import_spares_excel(filename)
        except Exception as e:
            self.append_log(f"Import Excel failed: {e}")

    def import_spares_excel(self, filename):
        """Import spares from Excel file (optional quantity column, case-insensitive aliases)."""
        try:
            import pandas as pd
            df = pd.read_excel(filename)
            # Normalize columns: lowercase, strip spaces
            normalized_cols = {c: str(c).strip().lower() for c in df.columns}
            df.rename(columns=normalized_cols, inplace=True)

            def find_col(candidates):
                for cand in candidates:
                    if cand in df.columns:
                        return cand
                return None

            pn_col = find_col(['part_number', 'part number', 'part', 'pn', 'partno', 'part_no', 'partnumber', 'code', 'sku', 'item code', 'product code', 'item number', 'item_number'])
            name_col = find_col(['name', 'description', 'part_name', 'part name', 'title', 'product', 'item', 'product name', 'item name'])
            qty_col = find_col(['quantity', 'qty', 'count', 'stock', 'on hand', 'onhand', 'available', 'balance', 'inventory', 'amount'])

            if pn_col is None or name_col is None:
                self.append_log("Excel must have Part Number and Name columns (case-insensitive). Examples: 'part_number', 'name'.")
                return
            
            # Log quantity column status
            if qty_col is None:
                self.append_log("Warning: No quantity column found. Will import all items with default quantity of 1.")
            else:
                self.append_log(f"Using quantity column: {qty_col}")

            # First pass: collect and aggregate data by part number
            part_data = {}  # {part_number: {'name': name, 'total_qty': qty, 'rows': [row_nums]}}
            skipped = 0
            
            for idx, row in df.iterrows():
                part_number_raw = row.get(pn_col, None)
                name_raw = row.get(name_col, None)
                part_number = str(part_number_raw).strip() if part_number_raw is not None else ""
                name = str(name_raw).strip() if name_raw is not None else ""

                quantity = None
                if qty_col is not None:
                    try:
                        q = row.get(qty_col, None)
                        if q is None or (isinstance(q, float) and pd.isna(q)):
                            quantity = None
                        else:
                            quantity = int(float(q))
                            if quantity < 0:
                                quantity = 0
                    except Exception as e:
                        self.append_log(f"Row {idx+1}: Invalid quantity '{q}' for {part_number} - {e}")
                        quantity = None
                else:
                    # Use default quantity of 1 when no quantity column is found
                    quantity = 1

                if part_number and name:
                    if part_number not in part_data:
                        part_data[part_number] = {'name': name, 'total_qty': 0, 'rows': []}
                    
                    # Update name if different (use the last one encountered)
                    part_data[part_number]['name'] = name
                    part_data[part_number]['rows'].append(idx + 1)
                    
                    # Aggregate quantities
                    if quantity is not None:
                        part_data[part_number]['total_qty'] += quantity
                    else:
                        # If any row has None quantity, mark the total as None to keep existing
                        if part_data[part_number]['total_qty'] != 'keep_existing':
                            part_data[part_number]['total_qty'] = 'keep_existing'
                else:
                    self.append_log(f"Row {idx+1}: Skipped - missing part_number or name (pn='{part_number}', name='{name}')")
                    skipped += 1

            # Second pass: insert aggregated data
            imported = 0
            for part_number, data in part_data.items():
                name = data['name']
                total_qty = data['total_qty']
                rows = data['rows']
                
                if total_qty == 'keep_existing':
                    self._upsert_spare(part_number, name)
                    self.append_log(f"Imported {part_number} - {name} (qty: kept existing) from rows {rows}")
                else:
                    self._upsert_spare(part_number, name, total_qty)
                    if len(rows) > 1:
                        self.append_log(f"Imported {part_number} - {name} (total qty: {total_qty}) - aggregated from rows {rows}")
                    else:
                        self.append_log(f"Imported {part_number} - {name} (qty: {total_qty}) from row {rows[0]}")
                imported += 1

            self.append_log(f"Import complete: {imported} imported, {skipped} skipped")
        except Exception as e:
            self.append_log(f"Import Excel failed: {e}")

    def _insert_stock_count(self, source, part_number, name, quantity):
        """Insert stock count record"""
        try:
            if not self._is_db_ready():
                return
            
            cur = self.conn.cursor()
            ts = datetime.now().isoformat()
            cur.execute(
                "INSERT INTO stock_counts(ts, source, part_number, name, quantity) VALUES(?,?,?,?,?)",
                (ts, source, part_number, name, quantity)
            )
            # Store ID for undo
            last_id = cur.lastrowid
            self._undo_stack.append(last_id)
            if len(self._undo_stack) > 5:  # Keep only last 5
                self._undo_stack.pop(0)
            self.conn.commit()
        except Exception as e:
            self.append_log(f"Insert stock count failed: {e}")

    def _upsert_spare(self, part_number, name, quantity=None):
        """Insert or update spare in database"""
        try:
            if not self._is_db_ready():
                return
            
            cur = self.conn.cursor()
            if quantity is not None:
                # Use provided quantity
                cur.execute(
                    "INSERT OR REPLACE INTO spares(part_number, name, quantity) VALUES(?,?,?)",
                    (part_number, name, quantity)
                )
            else:
                # Keep existing quantity or set to 0 if new
                cur.execute("SELECT quantity FROM spares WHERE part_number = ?", (part_number,))
                result = cur.fetchone()
                existing_qty = result[0] if result else 0
                cur.execute(
                    "INSERT OR REPLACE INTO spares(part_number, name, quantity) VALUES(?,?,?)",
                    (part_number, name, existing_qty)
                )
            self.conn.commit()
            # Emit signal to refresh spares views
            self.comm.spares_updated.emit()
        except Exception as e:
            self.append_log(f"Upsert spare failed: {e}")

    def _delete_spares(self, part_numbers):
        """Delete multiple spares"""
        try:
            if not self._is_db_ready():
                self.append_log("Database not ready. Cannot delete spares.")
                return
            
            cur = self.conn.cursor()
            for pn in part_numbers:
                cur.execute("DELETE FROM spares WHERE part_number=?", (pn,))
            self.conn.commit()
            self.append_log(f"Deleted {len(part_numbers)} spares")
        except Exception as e:
            self.append_log(f"Delete spares failed: {e}")

    def _delete_all_spares(self):
        """Delete all spares"""
        if "backup_restore" in self.locked_areas:
            QMessageBox.warning(self, "Access Denied", "Backup/restore operations are currently locked.")
            return
        try:
            if not self._is_db_ready():
                self.append_log("Database not ready. Cannot delete spares.")
                return
            
            cur = self.conn.cursor()
            cur.execute("DELETE FROM spares")
            self.conn.commit()
            self.append_log("Deleted all spares")
        except Exception as e:
            self.append_log(f"Delete all spares failed: {e}")

    def _export_period_dialog(self):
        """Show export period dialog"""
        try:
            dlg = QDialog(self)
            dlg.setWindowTitle("Export Period")
            v = QVBoxLayout()
            
            # Date inputs
            date_layout = QHBoxLayout()
            date_layout.addWidget(QLabel("From:"))
            from_date = QLineEdit()
            from_date.setPlaceholderText("YYYY-MM-DD")
            date_layout.addWidget(from_date)
            date_layout.addWidget(QLabel("To:"))
            to_date = QLineEdit()
            to_date.setPlaceholderText("YYYY-MM-DD")
            date_layout.addWidget(to_date)
            v.addLayout(date_layout)
            
            # Export button
            export_btn = QPushButton("Export")
            export_btn.clicked.connect(lambda: self._export_period(from_date.text(), to_date.text(), dlg))
            v.addWidget(export_btn)
            
            dlg.setLayout(v)
            dlg.exec_()
        except Exception as e:
            self.append_log(f"Export period dialog failed: {e}")

    def _export_period(self, from_date, to_date, dlg):
        """Export stock counts for period"""
        try:
            if not self._is_db_ready():
                self.append_log("Database not ready. Cannot export data.")
                return
            
            if not from_date or not to_date:
                self.append_log("Please enter both dates")
                return
            
            filename, _ = QFileDialog.getSaveFileName(dlg, "Export Stock Counts", f"stock_counts_{from_date}_to_{to_date}.csv", "CSV Files (*.csv)")
            if filename:
                cur = self.conn.cursor()
                cur.execute(
                    "SELECT ts, source, part_number, name, quantity FROM stock_counts WHERE ts >= ? AND ts <= ? ORDER BY ts ASC",
                    (f"{from_date}T00:00:00", f"{to_date}T23:59:59")
                )
                rows = cur.fetchall()
                
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    import csv
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Source", "Part Number", "Name", "Quantity"])
                    writer.writerows(rows)
                
                self.append_log(f"Exported {len(rows)} records to {filename}")
                dlg.accept()
        except Exception as e:
            self.append_log(f"Export period failed: {e}")

    def _view_spares_dialog(self):
        """Show spares management dialog"""
        try:
            if not self._is_db_ready():
                return
            
            if not self._check_area_access("spares"):
                return
            
            dlg = QDialog(self)
            dlg.setWindowTitle("Manage Spares")
            dlg.setSizeGripEnabled(True)
            dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowMaximizeButtonHint)
            v = QVBoxLayout()

            # Search bar
            search_edit = QLineEdit()
            search_edit.setPlaceholderText("Search by part number or name...")
            v.addWidget(search_edit)

            # Add/Update row
            add_layout = QHBoxLayout()
            add_layout.addWidget(QLabel("Part Number:"))
            pn_edit = QLineEdit()
            add_layout.addWidget(pn_edit)
            add_layout.addWidget(QLabel("Name:"))
            nm_edit = QLineEdit()
            add_layout.addWidget(nm_edit)
            add_btn = QPushButton("Add/Update")
            add_btn.setMinimumSize(100, 30)
            add_layout.addWidget(add_btn)
            v.addLayout(add_layout)

            # Table
            table = QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Part Number", "Name", "Quantity"])
            table.setAlternatingRowColors(True)
            table.setSortingEnabled(True)
            
            # Determine access without triggering warnings repeatedly
            has_edit_access = (not self.admin_enabled) or ("edit_amount" not in self.locked_areas) or self.admin_session_active
            # Enable editing only if user has access to edit amounts
            table.setEditTriggers(QTableWidget.DoubleClicked if has_edit_access else QTableWidget.NoEditTriggers)
                
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setSelectionMode(QTableWidget.MultiSelection)
            v.addWidget(table)

            # Actions row: delete selected / delete all / reset quantity / export
            actions_h = QHBoxLayout()
            btn_delete_sel = QPushButton("Delete Selected")
            btn_delete_sel.setMinimumSize(120, 30)
            btn_delete_all = QPushButton("Delete All Spares")
            btn_delete_all.setMinimumSize(150, 30)
            btn_reset_qty = QPushButton("Reset Quantity (Selected)")
            btn_reset_qty.setMinimumSize(180, 30)
            btn_reset_all_qty = QPushButton("Reset All Quantity")
            btn_reset_all_qty.setMinimumSize(150, 30)
            btn_export_spares = QPushButton("Export Spares")
            btn_export_spares.setMinimumSize(140, 30)
            actions_h.addWidget(btn_delete_sel)
            actions_h.addWidget(btn_reset_qty)
            actions_h.addWidget(btn_reset_all_qty)
            actions_h.addWidget(btn_delete_all)
            actions_h.addWidget(btn_export_spares)
            actions_h.addStretch(1)
            v.addLayout(actions_h)

            def reload_table(filter_text: str = ""):
                try:
                    # Prevent itemChanged signals while rebuilding the table
                    table.blockSignals(True)
                    local_has_edit_access = (not self.admin_enabled) or ("edit_amount" not in self.locked_areas) or self.admin_session_active
                    cur = self.conn.cursor()
                    if filter_text:
                        like = f"%{filter_text}%"
                        cur.execute(
                            "SELECT part_number, name, quantity FROM spares WHERE part_number LIKE ? OR name LIKE ? ORDER BY part_number ASC",
                            (like, like),
                        )
                    else:
                        cur.execute("SELECT part_number, name, quantity FROM spares ORDER BY part_number ASC")
                    rows = cur.fetchall()
                    table.setRowCount(len(rows))
                    for i, (pn, nm, qty) in enumerate(rows):
                        # Part Number column (read-only)
                        pn_item = QTableWidgetItem(str(pn))
                        pn_item.setFlags(pn_item.flags() & ~Qt.ItemIsEditable)
                        table.setItem(i, 0, pn_item)
                        
                        # Name column (read-only)
                        nm_item = QTableWidgetItem(str(nm))
                        nm_item.setFlags(nm_item.flags() & ~Qt.ItemIsEditable)
                        table.setItem(i, 1, nm_item)
                        
                        # Quantity column (editable only if access granted)
                        qty_item = QTableWidgetItem(str(qty))
                        if not local_has_edit_access:
                            qty_item.setFlags(qty_item.flags() & ~Qt.ItemIsEditable)
                        table.setItem(i, 2, qty_item)
                    table.resizeColumnsToContents()
                except Exception as e:
                    self.append_log(f"Load spares failed: {e}")
                finally:
                    table.blockSignals(False)

            def on_cell_double_clicked(row: int, col: int):
                try:
                    if col != 2:
                        return
                    # If edit is locked, require password every time and handle edit via dialog (no persistent enabling)
                    if self.admin_enabled and ("edit_amount" in self.locked_areas):
                        pwd, ok = QInputDialog.getText(self, "Admin Required", "Enter admin password:", QLineEdit.Password)
                        if not ok:
                            return
                        if hashlib.md5(pwd.encode()).hexdigest() != (self.admin_password or ""):
                            # Invalid password - invalidate any active session and log attempt
                            self.admin_session_active = False
                            self._save_admin_settings()  # Persist security state immediately
                            self.append_log("Invalid password attempt - admin session invalidated")
                            QMessageBox.warning(self, "Access Denied", "Invalid password. Admin session has been invalidated for security.")
                            return
                        # Prompt for new quantity
                        current_item = table.item(row, col)
                        current_text = current_item.text() if current_item else "0"
                        try:
                            current_val = int(current_text)
                        except Exception:
                            current_val = 0
                        new_val, ok = QInputDialog.getInt(self, "Edit Quantity", "New quantity:", value=current_val, min=0, max=2_000_000)
                        if not ok:
                            return
                        # Persist change
                        pn_item = table.item(row, 0)
                        if pn_item is None:
                            return
                        part_number = pn_item.text().strip()
                        if not self._is_db_ready():
                            return
                        cur = self.conn.cursor()
                        cur.execute("UPDATE spares SET quantity = ? WHERE part_number = ?", (int(new_val), part_number))
                        self.conn.commit()
                        # Update UI without triggering itemChanged logic
                        table.blockSignals(True)
                        if current_item is not None:
                            current_item.setText(str(int(new_val)))
                        table.blockSignals(False)
                        self.comm.spares_updated.emit()
                        return
                except Exception as e:
                    self.append_log(f"Edit access prompt failed: {e}")

            def on_item_changed(item: QTableWidgetItem):
                try:
                    # Only handle edits to Quantity column
                    if item is None or item.column() != 2:
                        return
                    
                    # Check access control before allowing any changes
                    if self.admin_enabled and ("edit_amount" in self.locked_areas) and not self.admin_session_active:
                        # Revert to database value - unauthorized edit attempt
                        row = item.row()
                        pn_item = table.item(row, 0)
                        if pn_item is None:
                            return
                        part_number = pn_item.text().strip()
                        cur = self.conn.cursor()
                        cur.execute("SELECT quantity FROM spares WHERE part_number = ?", (part_number,))
                        db_row = cur.fetchone()
                        actual_qty = db_row[0] if db_row else 0
                        table.blockSignals(True)
                        item.setText(str(actual_qty))
                        table.blockSignals(False)
                        self.append_log("Unauthorized quantity edit attempt blocked - admin access required")
                        QMessageBox.warning(self, "Access Denied", "Admin access required to edit quantities. Changes have been reverted.")
                        return
                    
                    row = item.row()
                    pn_item = table.item(row, 0)
                    if pn_item is None:
                        return
                    part_number = pn_item.text().strip()
                    # Validate integer quantity (>= 0)
                    text_value = (item.text() or "").strip()
                    try:
                        new_qty = int(text_value)
                        if new_qty < 0:
                            raise ValueError("Quantity must be >= 0")
                    except Exception:
                        # Revert to database value if invalid
                        cur = self.conn.cursor()
                        cur.execute("SELECT quantity FROM spares WHERE part_number = ?", (part_number,))
                        db_row = cur.fetchone()
                        actual_qty = db_row[0] if db_row else 0
                        table.blockSignals(True)
                        item.setText(str(actual_qty))
                        table.blockSignals(False)
                        return

                    # Persist change
                    if not self._is_db_ready():
                        return
                    cur = self.conn.cursor()
                    cur.execute(
                        "UPDATE spares SET quantity = ? WHERE part_number = ?",
                        (new_qty, part_number),
                    )
                    self.conn.commit()
                    # Normalize displayed value
                    table.blockSignals(True)
                    item.setText(str(new_qty))
                    table.blockSignals(False)
                    # Notify other views
                    self.comm.spares_updated.emit()
                except Exception as e:
                    self.append_log(f"Auto-save quantity failed: {e}")
            
            # Store reference to reload function for automatic refresh
            self._current_spares_reload_func = reload_table

            def on_add_clicked():
                if "spares_add" in self.locked_areas:
                    if not self.admin_password:
                        QMessageBox.warning(dlg, "Access Denied", "Adding/updating spares is locked and no admin password is set.")
                        return
                    password, ok = QInputDialog.getText(dlg, "Admin Required", "Adding/updating spares is locked. Enter admin password:", QLineEdit.Password)
                    if not ok:
                        return
                    if hashlib.md5(password.encode()).hexdigest() != self.admin_password:
                        QMessageBox.warning(dlg, "Access Denied", "Invalid admin password.")
                        return
                pn = pn_edit.text().strip()
                nm = nm_edit.text().strip()
                if not pn or not nm:
                    self.append_log("Provide both part number and name.")
                    return
                self._upsert_spare(pn, nm)
                pn_edit.clear()
                nm_edit.clear()
                reload_table(search_edit.text().strip())

            def on_delete_selected():
                if "spares_delete_selected" in self.locked_areas:
                    if not self.admin_password:
                        QMessageBox.warning(dlg, "Access Denied", "Deleting selected spares is locked and no admin password is set.")
                        return
                    password, ok = QInputDialog.getText(dlg, "Admin Required", "Deleting selected spares is locked. Enter admin password:", QLineEdit.Password)
                    if not ok:
                        return
                    if hashlib.md5(password.encode()).hexdigest() != self.admin_password:
                        QMessageBox.warning(dlg, "Access Denied", "Invalid admin password.")
                        return
                if "backup_restore" in self.locked_areas:
                    QMessageBox.warning(self, "Access Denied", "Backup/restore operations are currently locked.")
                    return
                try:
                    selected = table.selectionModel().selectedRows()
                    if not selected:
                        self.append_log("No rows selected.")
                        return
                    # Confirm
                    resp = QMessageBox.question(dlg, "Confirm Delete", f"Delete {len(selected)} spare(s)?", QMessageBox.Yes | QMessageBox.No)
                    if resp != QMessageBox.Yes:
                        return
                    part_numbers = []
                    for idx in selected:
                        row = idx.row()
                        item = table.item(row, 0)
                        if item:
                            part_numbers.append(item.text())
                    if part_numbers:
                        self._delete_spares(part_numbers)
                        reload_table(search_edit.text().strip())
                except Exception as e:
                    self.append_log(f"Delete selected failed: {e}")

            def on_delete_all():
                if "spares_delete_all" in self.locked_areas:
                    if not self.admin_password:
                        QMessageBox.warning(dlg, "Access Denied", "Deleting all spares is locked and no admin password is set.")
                        return
                    password, ok = QInputDialog.getText(dlg, "Admin Required", "Deleting all spares is locked. Enter admin password:", QLineEdit.Password)
                    if not ok:
                        return
                    if hashlib.md5(password.encode()).hexdigest() != self.admin_password:
                        QMessageBox.warning(dlg, "Access Denied", "Invalid admin password.")
                        return
                try:
                    resp = QMessageBox.warning(dlg, "Delete ALL Spares", "This will delete ALL spares. Continue?", QMessageBox.Yes | QMessageBox.No)
                    if resp != QMessageBox.Yes:
                        return
                    self._delete_all_spares()
                    reload_table("")
                except Exception as e:
                    self.append_log(f"Delete all failed: {e}")

            def on_reset_quantity_selected():
                if "spares_reset_quantity" in self.locked_areas:
                    if not self.admin_password:
                        QMessageBox.warning(dlg, "Access Denied", "Resetting quantity is locked and no admin password is set.")
                        return
                    password, ok = QInputDialog.getText(dlg, "Admin Required", "Resetting quantity is locked. Enter admin password:", QLineEdit.Password)
                    if not ok:
                        return
                    if hashlib.md5(password.encode()).hexdigest() != self.admin_password:
                        QMessageBox.warning(dlg, "Access Denied", "Invalid admin password.")
                        return
                if "backup_restore" in self.locked_areas:
                    QMessageBox.warning(self, "Access Denied", "Backup/restore operations are currently locked.")
                    return
                try:
                    selected = table.selectionModel().selectedRows()
                    if not selected:
                        self.append_log("No rows selected.")
                        return
                    # Confirm reset
                    resp = QMessageBox.question(dlg, "Reset Quantity", f"Set quantity to 0 for {len(selected)} spare(s)?", QMessageBox.Yes | QMessageBox.No)
                    if resp != QMessageBox.Yes:
                        return
                    # If edit is locked, require password
                    if self.admin_enabled and ("edit_amount" in self.locked_areas):
                        pwd, ok = QInputDialog.getText(dlg, "Admin Required", "Enter admin password:", QLineEdit.Password)
                        if not ok:
                            return
                        if hashlib.md5(pwd.encode()).hexdigest() != (self.admin_password or ""):
                            # Invalid password - invalidate any active session and log attempt
                            self.admin_session_active = False
                            self._save_admin_settings()  # Persist security state immediately
                            self.append_log("Invalid password attempt - admin session invalidated")
                            QMessageBox.warning(dlg, "Access Denied", "Invalid password. Admin session has been invalidated for security.")
                            return
                    # Perform reset
                    cur = self.conn.cursor()
                    count = 0
                    for idx in selected:
                        row = idx.row()
                        item = table.item(row, 0)
                        if not item:
                            continue
                        part_number = item.text()
                        cur.execute("UPDATE spares SET quantity = 0 WHERE part_number = ?", (part_number,))
                        count += 1
                    self.conn.commit()
                    self.append_log(f"Reset quantity to 0 for {count} spare(s)")
                    # Refresh UI
                    reload_table(search_edit.text().strip())
                    self.comm.spares_updated.emit()
                except Exception as e:
                    self.append_log(f"Reset quantity failed: {e}")

            def on_reset_all_quantity():
                if "spares_reset_quantity" in self.locked_areas:
                    if not self.admin_password:
                        QMessageBox.warning(dlg, "Access Denied", "Resetting all quantities is locked and no admin password is set.")
                        return
                    password, ok = QInputDialog.getText(dlg, "Admin Required", "Resetting all quantities is locked. Enter admin password:", QLineEdit.Password)
                    if not ok:
                        return
                    if hashlib.md5(password.encode()).hexdigest() != self.admin_password:
                        QMessageBox.warning(dlg, "Access Denied", "Invalid admin password.")
                        return
                try:
                    resp = QMessageBox.warning(dlg, "Reset ALL Quantities", "This will reset ALL spare quantities to 0. Continue?", QMessageBox.Yes | QMessageBox.No)
                    if resp != QMessageBox.Yes:
                        return
                    cur = self.conn.cursor()
                    cur.execute("UPDATE spares SET quantity = 0")
                    count = cur.rowcount
                    self.conn.commit()
                    self.append_log(f"Reset quantity to 0 for ALL {count} spare(s)")
                    # Refresh UI
                    reload_table(search_edit.text().strip())
                    self.comm.spares_updated.emit()
                except Exception as e:
                    self.append_log(f"Reset all quantities failed: {e}")

            def on_export_spares():
                if "export" in self.locked_areas:
                    QMessageBox.warning(dlg, "Access Denied", "Export functions are currently locked.")
                    return
                try:
                    filename, _ = QFileDialog.getSaveFileName(dlg, "Export Spares", "spares.csv", "CSV Files (*.csv)")
                    if not filename:
                        return
                    cur = self.conn.cursor()
                    filter_text = search_edit.text().strip()
                    if filter_text:
                        like = f"%{filter_text}%"
                        cur.execute(
                            "SELECT part_number, name, quantity FROM spares WHERE part_number LIKE ? OR name LIKE ? ORDER BY part_number ASC",
                            (like, like),
                        )
                    else:
                        cur.execute("SELECT part_number, name, quantity FROM spares ORDER BY part_number ASC")
                    rows = cur.fetchall()
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        import csv
                        writer = csv.writer(f)
                        writer.writerow(["Part Number", "Name", "Quantity"])
                        for pn, nm, qty in rows:
                            writer.writerow([pn, nm, qty])
                    self.append_log(f"Exported {len(rows)} spares to {filename}")
                except Exception as e:
                    self.append_log(f"Export spares failed: {e}")

            add_btn.clicked.connect(on_add_clicked)
            search_edit.textChanged.connect(lambda _: reload_table(search_edit.text().strip()))
            btn_delete_sel.clicked.connect(on_delete_selected)
            btn_delete_all.clicked.connect(on_delete_all)
            btn_reset_all_qty.clicked.connect(on_reset_all_quantity)
            btn_reset_qty.clicked.connect(on_reset_quantity_selected)
            btn_export_spares.clicked.connect(on_export_spares)
            table.cellDoubleClicked.connect(on_cell_double_clicked)
            table.itemChanged.connect(on_item_changed)

            reload_table("")

            btns = QDialogButtonBox(QDialogButtonBox.Close)
            btns.rejected.connect(dlg.reject)
            btns.accepted.connect(dlg.accept)
            v.addWidget(btns)
            dlg.setLayout(v)
            dlg.resize(900, 600)
            dlg.exec_()
            # Auto-logout when exiting this area/dialog
            self.admin_session_active = False
            # Clear the reference when dialog is closed
            if hasattr(self, '_current_spares_reload_func'):
                delattr(self, '_current_spares_reload_func')
        except Exception as e:
            self.append_log(f"View spares failed: {e}")

    def _prompt_and_save_detection(self, part_number: str, predicted_name: str):
        """Prompt user to confirm detection and save to database"""
        try:
            if not self._is_db_ready():
                self.append_log("Database not ready. Cannot save detection.")
                return
            
            # Check current quantity in database
            cur = self.conn.cursor()
            cur.execute("SELECT quantity, name FROM spares WHERE part_number = ?", (part_number,))
            result = cur.fetchone()
            current_qty = result[0] if result else 0
            existing_name = result[1] if result else ""
            
            # Check if part exists in database
            part_exists = result is not None
            
            # Check if this part was recently detected (for "confirmed" tracking)
            now_ts = time.time()
            last_detection = self._recent_seen.get(part_number, 0)
            is_repeated = (now_ts - last_detection) < 60  # Within 60 seconds
            
            # Create confirmation dialog
            dlg = QDialog(self)
            dlg.setWindowTitle("Confirm Detection")
            v = QVBoxLayout()
            v.addWidget(QLabel(f"Detected Part: {part_number}"))
            
            # Show confirmation status for repeated parts
            if is_repeated and part_exists:
                confirmed_label = QLabel("✅ CONFIRMED - Part detected again")
                confirmed_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12px; background: #E8F5E8; padding: 5px; border-radius: 4px;")
                v.addWidget(confirmed_label)
            
            # Show notification if part doesn't exist
            if not part_exists:
                notif_label = QLabel("❌ PART NUMBER DOESN'T EXIST")
                notif_label.setStyleSheet("color: #F44336; font-weight: bold; font-size: 12px; background: #FFEBEE; padding: 5px; border-radius: 4px;")
                v.addWidget(notif_label)
                
                advice_label = QLabel("This part number is not found in the database.")
                advice_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
                v.addWidget(advice_label)
            else:
                # Show current quantity if part exists
                current_info = QLabel(f"Current Quantity: {current_qty}")
                current_info.setStyleSheet("color: #4CAF50; font-weight: bold;")
                v.addWidget(current_info)
            
            name_edit = QLineEdit()
            name_edit.setPlaceholderText("Confirm or edit spare name")
            # seed with existing name, predicted name, or exact map
            if existing_name:
                seed_name = existing_name
            else:
                seed_name = predicted_name
                if hasattr(self, 'exact_map') and part_number in getattr(self, 'exact_map', {}):
                    seed_name = self.exact_map.get(part_number, predicted_name)
            name_edit.setText(seed_name)
            v.addWidget(name_edit)

            qty_edit = QSpinBox()
            qty_edit.setRange(0, 999999)  # More reasonable range
            qty_edit.setValue(0)
            qty_edit.setToolTip("Enter quantity between 0 and 999,999")
            
            qty_label = QLabel("Quantity")
            if current_qty > 0:
                qty_label.setText(f"Quantity (Current Stock: {current_qty})")
            v.addWidget(qty_label)
            v.addWidget(qty_edit)

            # Action selection with proper quantity logic
            action_group = QGroupBox("Action (Select at least one)")
            action_layout = QVBoxLayout()
            
            # Add note about action requirement
            action_note = QLabel("⚠️ You must select at least one action below:")
            action_note.setStyleSheet("color: #FF9800; font-size: 10px; font-weight: bold;")
            action_layout.addWidget(action_note)
            
            rb_used = QCheckBox("Mark as Used (Decrements quantity)")
            rb_issued = QCheckBox("Mark as Issued (Increments quantity)")
            rb_stocktake = QCheckBox("Stocktake Count (Standalone)")
            # Set default state to unchecked
            
            action_layout.addWidget(rb_used)
            action_layout.addWidget(rb_issued)
            action_layout.addWidget(rb_stocktake)
            # Detailed explanation to avoid confusion
            detail_explain = QLabel(
                "Stocktake is standalone: it records counts to the log only and does not change Spares totals.\n"
                "Used decreases Spares totals. Issued increases Spares totals."
            )
            detail_explain.setStyleSheet("color: #9aa0a6; font-size: 11px;")
            action_layout.addWidget(detail_explain)
            action_group.setLayout(action_layout)
            v.addWidget(action_group)

            # For parts that don't exist, disable the form inputs
            if not part_exists:
                name_edit.setEnabled(False)
                qty_edit.setEnabled(False)
                rb_used.setEnabled(False)
                rb_issued.setEnabled(False)
                rb_stocktake.setEnabled(False)

            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            # Make the dialog buttons larger
            for button in buttons.buttons():
                button.setMinimumSize(80, 30)
            v.addWidget(buttons)
            dlg.setLayout(v)
            buttons.accepted.connect(dlg.accept)
            buttons.rejected.connect(dlg.reject)

            # Only process if user accepts the dialog
            if dlg.exec_() == QDialog.Accepted:
                # If part doesn't exist, just log and return
                if not part_exists:
                    self.append_log(f"DETECTION IGNORED: {part_number} - Part number doesn't exist in database")
                    return
                    
                final_name = name_edit.text().strip()
                
                # Validate name
                if final_name == "":
                    QMessageBox.warning(self, "Invalid Input", "Please enter a valid part name.")
                    self.append_log(f"ERROR: Empty part name for {part_number}")
                    return
                
                # Validate quantity with proper error handling
                try:
                    qty = int(qty_edit.value())
                except (ValueError, TypeError):
                    QMessageBox.warning(self, "Invalid Quantity", 
                                      "Please enter a valid numeric quantity (1-999999).")
                    self.append_log(f"ERROR: Invalid quantity value for {part_number} - {final_name}")
                    return
                
                # Check quantity range
                if qty <= 0:
                    QMessageBox.warning(self, "Invalid Quantity", 
                                      "Quantity must be greater than 0.")
                    self.append_log(f"ERROR: Non-positive quantity ({qty}) for {part_number} - {final_name}")
                    return
                
                if qty > 999999:
                    QMessageBox.warning(self, "Invalid Quantity", 
                                      "Quantity cannot exceed 999,999.")
                    self.append_log(f"ERROR: Quantity too large ({qty}) for {part_number} - {final_name}")
                    return
                
                # Check if any action is selected
                if not (rb_used.isChecked() or rb_issued.isChecked() or rb_stocktake.isChecked()):
                    QMessageBox.warning(self, "No Action Selected", 
                                      "Please select at least one action (Used, Issued, or Stocktake) before proceeding.")
                    self.append_log(f"ERROR: No action selected for {part_number} - {final_name}")
                    return
                
                # Additional validation for Used action
                if rb_used.isChecked() and part_exists and qty > current_qty:
                    QMessageBox.warning(self, "Insufficient Stock", 
                                      f"Cannot use {qty} items. Only {current_qty} available in stock.")
                    self.append_log(f"ERROR: Insufficient stock for {part_number} - {final_name} (Requested: {qty}, Available: {current_qty})")
                    return
                
                # Update recent seen timestamp for confirmation tracking
                self._recent_seen[part_number] = now_ts
                
                # Process based on selected action
                if rb_used.isChecked():
                    # Used: Decrement spare parts quantity
                    if part_exists:
                        # Check if we have enough quantity to use
                        if qty > current_qty:
                            QMessageBox.warning(self, "Insufficient Quantity", 
                                              f"Cannot use {qty} items. Only {current_qty} available for {part_number}.")
                            self.append_log(f"ERROR: Insufficient quantity for {part_number} - {final_name} (Requested: {qty}, Available: {current_qty})")
                            return
                        
                        new_qty = current_qty - qty
                        self._upsert_spare(part_number, final_name, new_qty)
                        self._record_spare_used(part_number, final_name, qty)
                        self.append_log(f"USED: {qty} from {part_number} - {final_name} (New Total: {new_qty})")
                    else:
                        QMessageBox.warning(self, "Part Not Found", 
                                          f"Cannot mark as used: {part_number} is not in the database.")
                        self.append_log(f"ERROR: Cannot use {part_number} - {final_name} (Part not in database)")
                        return
                        
                elif rb_issued.isChecked():
                    # Issued: Increment spare parts quantity
                    new_qty = current_qty + qty
                    self._upsert_spare(part_number, final_name, new_qty)
                    self._record_spare_issued(part_number, final_name, qty)
                    self.append_log(f"ISSUED: {qty} to {part_number} - {final_name} (New Total: {new_qty})")
                    
                elif rb_stocktake.isChecked():
                    # Stocktake: Standalone count (no quantity change)
                    self._insert_stock_count(source="camera", part_number=part_number, name=final_name, quantity=qty)
                    self.append_log(
                        f"STOCKTAKE (standalone): Counted {qty} for {part_number} - {final_name}. Spares totals unchanged."
                    )
                    
                else:
                    # This should never happen due to validation above, but just in case
                    self.append_log(f"ERROR: No action selected for {part_number} - {final_name}")
            else:
                # User cancelled - do nothing
                self.append_log(f"Action cancelled for {part_number}")
                
        except Exception as e:
            self.append_log(f"Prompt failed: {e}")



    def train_model(self):
        """Train the ML model"""
        try:
            if not self._check_area_access("models"):
                return
                
            # Check if we have training data
            if not hasattr(self, 'df') or self.df is None:
                self.append_log("No training data loaded. Please load an Excel file first.")
                return
            
            self.append_log("Training started (running in background)...")
            
            # Make a lightweight copy of necessary series to pass to thread
            try:
                part_numbers = self.df['part_number'].astype(str).copy()
                names = self.df['name'].astype(str).copy()
            except Exception as e:
                self.append_log(f"Dataset issue: {e}")
                return
            
            # Start training in background thread
            Thread(target=self._train_worker, args=(part_numbers, names), daemon=True).start()
            
        except Exception as e:
            self.append_log(f"Training failed: {e}")

    def load_excel(self):
        """Load Excel file for training data"""
        try:
            path, _ = QFileDialog.getOpenFileName(self, "Open Excel file", ".", "Excel Files (*.xlsx *.xls)")
            if not path:
                return
            
            df = pd.read_excel(path)
            if 'part_number' not in df.columns or 'name' not in df.columns:
                QMessageBox.warning(self, "Bad file", "Excel must contain 'part_number' and 'name' columns.")
                return
            
            df['part_number'] = df['part_number'].astype(str).str.strip()
            df['name'] = df['name'].astype(str).str.strip()
            self.df = df
            self.append_log(f"Loaded Excel: {path} ({len(df)} rows)")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load Excel: {e}")

    def _ensemble_predict(self, query_part_number, vect_char, vect_word, nn_cosine_char, nn_manhattan_hybrid, nn_l1_char, names_clean, exact_map):
        """Ensemble prediction using multiple models and voting"""
        try:
            # Normalize query
            query_norm = self._normalize_ocr_text(query_part_number)
            
            # Check exact match first (highest priority)
            if query_norm in exact_map:
                return exact_map[query_norm], 1.0, "exact"
            
            # Get predictions from all models
            predictions = []
            
            # Character TF-IDF predictions
            try:
                vec_char_transformed = vect_char.transform([query_norm])
                dist_char, idx_char = nn_cosine_char.kneighbors(vec_char_transformed, return_distance=True)
                for d, i in zip(dist_char[0], idx_char[0]):
                    predictions.append((names_clean[i], 1.0 - d, "cosine_char", d))
            except:
                pass
            
            # Word TF-IDF predictions
            try:
                vec_word_transformed = vect_word.transform([query_norm])
                dist_word, idx_word = nn_cosine_char.kneighbors(vec_word_transformed, return_distance=True)
                for d, i in zip(dist_word[0], idx_word[0]):
                    predictions.append((names_clean[i], 1.0 - d, "cosine_word", d))
            except:
                pass
            
            # Hybrid predictions
            try:
                vec_hybrid = vect_char.transform([query_norm])
                dist_hybrid, idx_hybrid = nn_manhattan_hybrid.kneighbors(vec_hybrid, return_distance=True)
                for d, i in zip(dist_hybrid[0], idx_hybrid[0]):
                    predictions.append((names_clean[i], 1.0 - (d / 100), "manhattan_hybrid", d))
            except:
                pass
            
            # L1 predictions
            try:
                vec_l1 = vect_char.transform([query_norm])
                dist_l1, idx_l1 = nn_l1_char.kneighbors(vec_l1, return_distance=True)
                for d, i in zip(dist_l1[0], idx_l1[0]):
                    predictions.append((names_clean[i], 1.0 - (d / 100), "l1", d))
            except:
                pass
            
            if not predictions:
                return "Unknown", 0.0, "no_predictions"
            
            # Ensemble voting with weighted scores
            name_scores = {}
            for name, score, method, distance in predictions:
                if name not in name_scores:
                    name_scores[name] = {'total_score': 0, 'count': 0, 'min_distance': float('inf')}
                
                # Weight different methods
                weight = 1.0
                if method == "cosine_char":
                    weight = 1.2  # Highest weight for character-level cosine
                elif method == "cosine_word":
                    weight = 1.1
                elif method == "manhattan_hybrid":
                    weight = 0.9
                elif method == "l1":
                    weight = 0.8
                
                name_scores[name]['total_score'] += score * weight
                name_scores[name]['count'] += 1
                name_scores[name]['min_distance'] = min(name_scores[name]['min_distance'], distance)
            
            # Find best prediction
            best_name = None
            best_score = 0
            best_distance = float('inf')
            
            for name, scores in name_scores.items():
                # Average score with count bonus
                avg_score = scores['total_score'] / scores['count']
                count_bonus = min(0.1, scores['count'] * 0.02)  # Bonus for multiple model agreement
                final_score = avg_score + count_bonus
                
                if final_score > best_score:
                    best_score = final_score
                    best_name = name
                    best_distance = scores['min_distance']
            
            return best_name, best_score, f"ensemble_{len(predictions)}_models"
            
        except Exception as e:
            return f"Prediction Error: {e}", 0.0, "error"

    def _train_worker(self, part_numbers, names):
        """Background worker for training with advanced accuracy techniques"""
        try:
            self.comm.log.emit("Starting advanced training for high accuracy...")
            
            # Data preprocessing and augmentation
            part_numbers_clean = []
            names_clean = []
            
            for pn, nm in zip(part_numbers, names):
                pn_str = str(pn).strip()
                nm_str = str(nm).strip()
                
                # Skip empty or invalid entries
                if not pn_str or not nm_str or len(pn_str) < 5:
                    continue
                    
                # Normalize part numbers (consistent format)
                pn_normalized = self._normalize_ocr_text(pn_str)
                
                part_numbers_clean.append(pn_normalized)
                names_clean.append(nm_str)
            
            if len(part_numbers_clean) < 10:
                self.comm.log.emit("Warning: Limited training data. Accuracy may be reduced.")
            
            self.comm.log.emit(f"Training with {len(part_numbers_clean)} clean part numbers...")
            
            # Strategy 1: Character-level TF-IDF with optimized parameters
            self.comm.log.emit("Building character-level TF-IDF vectorizer...")
            vect_char = TfidfVectorizer(
                analyzer='char',
                ngram_range=(2, 6),  # Extended n-gram range for better character patterns
                min_df=1,  # Include all terms
                max_df=0.95,  # Remove very common terms
                sublinear_tf=True,  # Apply sublinear scaling
                use_idf=True,
                smooth_idf=True
            )
            X_vec_char = vect_char.fit_transform(part_numbers_clean)
            
            # Strategy 2: Word-level TF-IDF for longer part numbers
            self.comm.log.emit("Building word-level TF-IDF vectorizer...")
            vect_word = TfidfVectorizer(
                analyzer='word',
                ngram_range=(1, 3),  # Word-level n-grams
                min_df=1,
                max_df=0.95,
                sublinear_tf=True,
                use_idf=True,
                smooth_idf=True
            )
            X_vec_word = vect_word.fit_transform(part_numbers_clean)
            
            # Strategy 3: Hybrid approach - combine character and word features
            self.comm.log.emit("Building hybrid feature matrix...")
            X_vec_hybrid = hstack([X_vec_char, X_vec_word])
            
            # Strategy 4: Exact matching for perfect accuracy
            exact_map = {str(pn): str(nm) for pn, nm in zip(part_numbers_clean, names_clean)}
            
            # Multiple distance metrics for ensemble prediction
            self.comm.log.emit("Training multiple distance models...")
            
            # Model 1: Cosine distance with character TF-IDF
            nn_cosine_char = NearestNeighbors(
                n_neighbors=min(5, len(part_numbers_clean)), 
                metric='cosine',
                algorithm='auto'
            )
            nn_cosine_char.fit(X_vec_char)
            
            # Model 2: Euclidean distance with character TF-IDF
            nn_euclidean_char = NearestNeighbors(
                n_neighbors=min(5, len(part_numbers_clean)), 
                metric='euclidean',
                algorithm='auto'
            )
            nn_euclidean_char.fit(X_vec_char)
            
            # Model 3: Manhattan distance with hybrid features
            nn_manhattan_hybrid = NearestNeighbors(
                n_neighbors=min(5, len(part_numbers_clean)), 
                metric='manhattan',
                algorithm='auto'
            )
            nn_manhattan_hybrid.fit(X_vec_hybrid)
            
            # Model 4: L1 distance (Manhattan) with character TF-IDF
            nn_l1_char = NearestNeighbors(
                n_neighbors=min(5, len(part_numbers_clean)), 
                metric='l1',  # L1 distance is compatible with sparse matrices
                algorithm='auto'
            )
            nn_l1_char.fit(X_vec_char)
            
            # Model 5: L2 distance (Euclidean) with word TF-IDF
            nn_l2_word = NearestNeighbors(
                n_neighbors=min(5, len(part_numbers_clean)), 
                metric='l2',  # L2 distance is compatible with sparse matrices
                algorithm='auto'
            )
            nn_l2_word.fit(X_vec_word)
            

            
            # Save advanced search index
            index_obj = {
                'vectorizer_char': vect_char,
                'vectorizer_word': vect_word,
                'nn_cosine_char': nn_cosine_char,
                'nn_euclidean_char': nn_euclidean_char,
                'nn_manhattan_hybrid': nn_manhattan_hybrid,
                'nn_l1_char': nn_l1_char,
                'nn_l2_word': nn_l2_word,
                'part_numbers': part_numbers_clean,
                'names': names_clean,
                'exact_map': exact_map,
                'training_metadata': {
                    'total_samples': len(part_numbers_clean),
                    'unique_part_numbers': len(set(part_numbers_clean)),
                    'unique_names': len(set(names_clean)),
                    'training_timestamp': datetime.now().isoformat(),
                    'algorithm_version': 'advanced_ensemble_v2'
                }
            }
            
            joblib.dump(index_obj, SEARCH_INDEX_PATH)
            self.comm.log.emit(f"Advanced search index saved to '{SEARCH_INDEX_PATH}'")
            
            # Update runtime references
            self.vectorizer = vect_char  # Keep for backward compatibility
            self.nn = nn_cosine_char     # Keep for backward compatibility
            self.index_part_numbers = part_numbers_clean
            self.index_names = names_clean
            self.exact_map = exact_map
            
            # Store advanced models
            self.advanced_models = index_obj
            
            self.comm.log.emit("Advanced training completed successfully!")
            self.comm.log.emit(f"Trained {len(part_numbers_clean)} samples with ensemble prediction")
            
        except Exception as ex:
            self.comm.log.emit(f"Advanced training failed: {ex}")
            import traceback
            traceback.print_exc()

    def show_model_info(self):
        """Show information about the loaded model"""
        try:
            if hasattr(self, 'advanced_models') and self.advanced_models is not None:
                metadata = self.advanced_models.get('training_metadata', {})
                self.append_log("=== Advanced Ensemble Model Information ===")
                self.append_log(f"Algorithm Version: {metadata.get('algorithm_version', 'unknown')}")
                self.append_log(f"Training Samples: {metadata.get('total_samples', 0)}")
                self.append_log(f"Unique Part Numbers: {metadata.get('unique_part_numbers', 0)}")
                self.append_log(f"Unique Names: {metadata.get('unique_names', 0)}")
                self.append_log(f"Training Date: {metadata.get('training_timestamp', 'unknown')}")
                self.append_log("Distance Metrics: Cosine, Euclidean, Manhattan, L1, L2")
                self.append_log("Vectorization: Character TF-IDF + Word TF-IDF + Hybrid")
                self.append_log("Ensemble Method: Class-based prediction with method-specific weights")
                self.append_log("================================================")
            elif self.vectorizer is not None and self.nn is not None:
                self.append_log("=== Legacy Model Information ===")
                self.append_log(f"Part Numbers: {len(self.index_part_numbers) if self.index_part_numbers else 0}")
                self.append_log(f"Names: {len(self.index_names) if self.index_names else 0}")
                self.append_log("Method: TF-IDF + Nearest Neighbors (Cosine)")
                self.append_log("================================================")
            else:
                self.append_log("No models loaded. Please train or load models first.")
        except Exception as e:
            self.append_log(f"Failed to show model info: {e}")

    def load_models(self):
        """Load trained models"""
        try:
            self.append_log("Loading models...")
            if os.path.exists(SEARCH_INDEX_PATH):
                idx = joblib.load(SEARCH_INDEX_PATH)
                
                # Check if this is an advanced ensemble model
                if 'vectorizer_char' in idx and 'nn_cosine_char' in idx:
                    # Advanced ensemble model
                    self.vectorizer = idx.get('vectorizer_char')  # Backward compatibility
                    self.nn = idx.get('nn_cosine_char')          # Backward compatibility
                    self.index_part_numbers = idx.get('part_numbers')
                    self.index_names = idx.get('names')
                    self.exact_map = idx.get('exact_map', {})
                    
                    # Store advanced models
                    self.advanced_models = idx
                    
                    # Log training metadata
                    metadata = idx.get('training_metadata', {})
                    if metadata:
                        self.append_log(f"Advanced ensemble model loaded:")
                        self.append_log(f"  - {metadata.get('total_samples', 0)} training samples")
                        self.append_log(f"  - {metadata.get('unique_part_numbers', 0)} unique part numbers")
                        self.append_log(f"  - Algorithm: {metadata.get('algorithm_version', 'unknown')}")
                        self.append_log(f"  - Trained: {metadata.get('training_timestamp', 'unknown')}")
                    else:
                        self.append_log("Advanced ensemble model loaded with multiple distance metrics.")
                    
                else:
                    # Legacy model
                    self.vectorizer = idx.get('vectorizer')
                    self.nn = idx.get('nn')
                    self.index_part_numbers = idx.get('part_numbers')
                    self.index_names = idx.get('names')
                    self.exact_map = idx.get('exact_map', {})
                    self.append_log("Loaded legacy search index (vectorizer + nearest-neighbors).")
            else:
                missing = []
                if not os.path.exists(CLASSIFIER_PATH):
                    missing.append("classifier")
                if not os.path.exists(VECTORIZER_PATH):
                    missing.append("vectorizer")
                if not os.path.exists(ENCODER_PATH):
                    missing.append("label encoder")
                if missing:
                    self.append_log(f"Missing: {', '.join(missing)}. Train models to build search index.")
                    return
                # Legacy load for backwards compatibility
                self.clf = joblib.load(CLASSIFIER_PATH)
                self.vectorizer = joblib.load(VECTORIZER_PATH)
                self.label_encoder = joblib.load(ENCODER_PATH)
                self.append_log("Loaded legacy classifier models. Consider retraining to build new search index.")

            # lazy init OCR (also in background)
            if self.reader is None:
                try:
                    self.reader = easyocr.Reader(['en'], gpu=False)
                    self.append_log("Initialized EasyOCR reader.")
                except Exception as ocr_e:
                    self.append_log(f"OCR init failed: {ocr_e}")
        except Exception as e:
            self.append_log(f"Load models failed: {e}")

    def start_camera(self, source=0):
        """Start camera with specified source"""
        try:
            if self.capture is not None:
                self.append_log("Camera already running.")
                return
            
            self.capture = cv2.VideoCapture(source)
            if not self.capture.isOpened():
                self.append_log(f"Cannot open camera source: {source}")
                self.capture = None
                return

            # Ensure OCR reader exists (kick off init in background if missing)
            if self.reader is None:
                self.append_log("Initializing OCR in background...")
                Thread(target=self._init_ocr_worker, daemon=True).start()

            # lazy-load models if not loaded
            if self.clf is None and (self.vectorizer is None or (self.nn is None and self.label_encoder is None)):
                if os.path.exists(CLASSIFIER_PATH) and os.path.exists(VECTORIZER_PATH) and os.path.exists(ENCODER_PATH):
                    self.load_models()
                else:
                    self.append_log("Models not loaded. Predictions will not be available until you Train or Load models.")

            self.stop_event.clear()
            # Use simple threading with proper Qt signal handling
            self.cam_thread = Thread(target=self._camera_loop, daemon=True)
            self.cam_thread.start()
            self.append_log(f"Camera started from source: {source}")
        except Exception as e:
            self.append_log(f"Start camera failed: {e}")

    def stop_camera(self):
        """Stop camera"""
        if "camera_controls" in self.locked_areas:
            QMessageBox.warning(self, "Access Denied", "Camera controls are currently locked.")
            return
        try:
            if self.capture is None:
                return
            self.stop_event.set()
            # give thread time to stop
            import time
            time.sleep(0.2)
            try:
                if self.capture:
                    self.capture.release()
            except Exception:
                pass
            self.capture = None
            self.append_log("Camera stopped.")
        except Exception as e:
            self.append_log(f"Stop camera failed: {e}")


    def _init_ocr_worker(self):
        """Background worker for OCR initialization"""
        try:
            if self.reader is None:
                self.reader = easyocr.Reader(['en'], gpu=False)
                self.append_log("Initialized EasyOCR reader.")
        except Exception as e:
            self.append_log(f"OCR init failed: {e}")

    def _camera_loop(self):
        """Camera processing loop"""
        try:
            self.process_frame_counter = 0
            while not self.stop_event.is_set() and self.capture and self.capture.isOpened():
                ret, frame = self.capture.read()
                if not ret:
                    self.append_log("Frame read failed.")
                    break

                # Update display
                display_frame = frame.copy()

                # Every N frames run OCR & detection
                self.process_frame_counter += 1
                if self.process_frame_counter >= self.ocr_every_n:
                    self.process_frame_counter = 0
                    try:
                        # EasyOCR expects RGB; skip OCR if reader not ready
                        if self.reader is None:
                            raise RuntimeError("OCR not ready yet")
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        results = self.reader.readtext(rgb)

                        best = None  # (score, bbox, part_text, predicted_name, conf)
                        for (bbox, text, conf) in results:
                            # Enhanced OCR processing with correction
                            original_text = text.strip()
                            txt = self._normalize_ocr_text(original_text)
                            
                            # Apply enhanced OCR correction
                            corrected_text, correction_confidence = self._enhanced_ocr_correction(txt)
                            
                            # Extract part number pattern from corrected text
                            m = self._PART_NUMBER_REGEX.search(corrected_text)
                            if not m:
                                continue
                            
                            # Reformat to XXXXXXX-XXXX
                            part_text = f"{m.group(1)}-{m.group(2)}"
                            
                            # Store detection result for analysis
                            self._store_detection_result(original_text, part_text, correction_confidence, conf)
                            
                            # Log correction details if significant
                            if original_text != part_text:
                                self.append_log(f"OCR Correction: '{original_text}' -> '{part_text}' (confidence: {correction_confidence:.3f})")

                            # predict using search index if available
                            predicted_name = "N/A (models not loaded)"
                            confidence_details = ""
                            if hasattr(self, 'advanced_models') and self.advanced_models is not None:
                                # Use advanced ensemble prediction
                                try:
                                    ensemble_result = self._ensemble_predict(
                                        part_text, 
                                        self.advanced_models['vectorizer_char'],
                                        self.advanced_models['vectorizer_word'],
                                        self.advanced_models['nn_cosine_char'],
                                        self.advanced_models['nn_manhattan_hybrid'],
                                        self.advanced_models['nn_l1_char'],
                                        self.advanced_models['names'],
                                        self.advanced_models['exact_map']
                                    )
                                    if len(ensemble_result) >= 2:
                                        predicted_name, confidence_score, method = ensemble_result
                                        confidence_details = f" [{method}]"
                                        if confidence_score >= 0.7:  # Higher threshold for ensemble
                                            score = confidence_score
                                            if best is None or score > best[0]:
                                                best = (score, bbox, part_text, predicted_name, conf)
                                                # Log confidence details
                                                if confidence_score >= 0.9:
                                                    self.append_log(f"High confidence detection: {part_text} -> {predicted_name} (score: {confidence_score:.3f})")
                                                elif confidence_score >= 0.8:
                                                    self.append_log(f"Good confidence detection: {part_text} -> {predicted_name} (score: {confidence_score:.3f})")
                                                else:
                                                    self.append_log(f"Moderate confidence detection: {part_text} -> {predicted_name} (score: {confidence_score:.3f})")
                                except Exception as e:
                                    predicted_name = f"EnsembleErr: {e}"
                                    confidence_details = " [error]"
                            elif self.vectorizer is not None and self.nn is not None and self.index_names is not None:
                                try:
                                    vec = self.vectorizer.transform([part_text])
                                    dist, idx = self.nn.kneighbors(vec, n_neighbors=1, return_distance=True)
                                    d = float(dist[0][0])
                                    match_idx = int(idx[0][0])
                                    predicted_name = self.index_names[match_idx]
                                    confidence_details = f" [legacy_cosine: {1.0-d:.3f}]"
                                    if d <= self.nn_max_distance:
                                        score = 1.0 - d
                                        if best is None or score > best[0]:
                                            best = (score, bbox, part_text, predicted_name, conf)
                                except Exception as e:
                                    predicted_name = f"PredictErr: {e}"
                                    confidence_details = " [error]"
                            elif self.clf is not None and self.vectorizer is not None and self.label_encoder is not None:
                                # Legacy fallback
                                try:
                                    vec = self.vectorizer.transform([part_text])
                                    label_idx = self.clf.predict(vec)[0]
                                    predicted_name = self.label_encoder.inverse_transform([label_idx])[0]
                                    score = 0.5
                                    confidence_details = " [legacy_classifier]"
                                    if best is None or score > best[0]:
                                        best = (score, bbox, part_text, predicted_name, conf)
                                except Exception as e:
                                    predicted_name = f"PredictErr: {e}"
                                    confidence_details = " [error]"

                        # After loop: output only the best detection this frame (if any)
                        if best is not None:
                            _, bbox_b, part_text_b, predicted_name_b, conf_b = best
                            now_ts = time.time()
                            last_ts = self._recent_seen.get(part_text_b, 0)
                            if now_ts - last_ts >= self.duplicate_suppress_s:
                                self._recent_seen[part_text_b] = now_ts
                                if self.cb_draw_boxes and self.cb_draw_boxes.isChecked():
                                    pts = np.array(bbox_b).astype(int)
                                    cv2.polylines(display_frame, [pts.reshape((-1,1,2))], True, (0,255,0), 2)
                                    cv2.putText(display_frame, f"{part_text_b} -> {predicted_name_b}{confidence_details}", (pts[0][0], pts[0][1]-10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
                                self.comm.detection.emit(part_text_b, predicted_name_b, float(conf_b))

                    except Exception as e:
                        # OCR error but continue
                        self.append_log(f"OCR err: {e}")

                # Convert BGR to RGB for Qt
                try:
                    rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                    self.comm.frame_ready.emit(rgb)
                except Exception as e:
                    self.append_log(f"Frame convert error: {e}")

                # Sleep based on detection rate setting
                import time
                sleep_time = 1.0 / self.detection_rate_fps if self.detection_rate_fps > 0 else 0.02
                time.sleep(sleep_time)

            # Cleanup
            if self.capture:
                self.capture.release()
            self.append_log("Camera loop ended.")
        except Exception as e:
            self.append_log(f"Camera loop failed: {e}")

    def _view_spares_used_dialog(self):
        try:
            if not self._is_db_ready():
                return
            
            dlg = QDialog(self)
            dlg.setWindowTitle("Spares Used")
            dlg.setSizeGripEnabled(True)
            dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowMaximizeButtonHint)
            v = QVBoxLayout()

            # Search bar
            search_edit = QLineEdit()
            search_edit.setPlaceholderText("Search by part number or name...")
            v.addWidget(search_edit)

            # Manual Add Used row
            add_layout = QHBoxLayout()
            add_layout.addWidget(QLabel("Part Number:"))
            pn_edit = QLineEdit()
            add_layout.addWidget(pn_edit)
            add_layout.addWidget(QLabel("Name:"))
            nm_edit = QLineEdit()
            add_layout.addWidget(nm_edit)
            add_layout.addWidget(QLabel("Qty:"))
            qty_spin = QSpinBox()
            qty_spin.setRange(0, 999999)
            qty_spin.setValue(0)
            add_layout.addWidget(qty_spin)
            btn_add_used = QPushButton("Add Used")
            btn_add_used.setMinimumSize(110, 30)
            add_layout.addWidget(btn_add_used)
            v.addLayout(add_layout)

            # Table
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Timestamp", "Part Number", "Name", "Quantity"])
            table.setAlternatingRowColors(True)
            table.setSortingEnabled(True)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setSelectionMode(QTableWidget.MultiSelection)
            v.addWidget(table)

            # Actions row
            actions_h = QHBoxLayout()
            btn_delete_sel = QPushButton("Delete Selected")
            btn_delete_sel.setMinimumSize(120, 30)
            btn_delete_all = QPushButton("Delete All Records")
            btn_delete_all.setMinimumSize(160, 30)
            btn_export_used = QPushButton("Export Used")
            btn_export_used.setMinimumSize(140, 30)
            actions_h.addWidget(btn_delete_sel)
            actions_h.addWidget(btn_delete_all)
            actions_h.addWidget(btn_export_used)
            actions_h.addStretch(1)
            v.addLayout(actions_h)

            def reload_table(filter_text: str = ""):
                try:
                    cur = self.conn.cursor()
                    if filter_text:
                        like = f"%{filter_text}%"
                        cur.execute(
                            "SELECT ts, part_number, name, quantity FROM spares_used WHERE part_number LIKE ? OR name LIKE ? ORDER BY ts DESC",
                            (like, like),
                        )
                    else:
                        cur.execute("SELECT ts, part_number, name, quantity FROM spares_used ORDER BY ts DESC")
                    rows = cur.fetchall()
                    table.setRowCount(len(rows))
                    for i, (ts, pn, nm, qty) in enumerate(rows):
                        table.setItem(i, 0, QTableWidgetItem(str(ts)))
                        table.setItem(i, 1, QTableWidgetItem(str(pn)))
                        table.setItem(i, 2, QTableWidgetItem(str(nm)))
                        table.setItem(i, 3, QTableWidgetItem(str(qty)))
                    table.resizeColumnsToContents()
                except Exception as e:
                    self.append_log(f"Load spares_used failed: {e}")

            def on_add_used():
                try:
                    part_number = pn_edit.text().strip()
                    name = nm_edit.text().strip()
                    qty = int(qty_spin.value())
                    if not part_number or qty <= 0:
                        self.append_log("Provide part number and quantity > 0")
                        return
                    # Check current stock
                    cur = self.conn.cursor()
                    cur.execute("SELECT quantity, name FROM spares WHERE part_number = ?", (part_number,))
                    row = cur.fetchone()
                    current_qty = row[0] if row else None
                    existing_name = row[1] if row else ""
                    if current_qty is None:
                        QMessageBox.warning(dlg, "Part Not Found", f"Cannot mark used: {part_number} not in spares.")
                        return
                    if qty > current_qty:
                        QMessageBox.warning(dlg, "Insufficient Stock", f"Requested {qty}, available {current_qty} for {part_number}.")
                        return
                    final_name = name.strip() or existing_name or "Unknown"
                    # Insert used record
                    ts = datetime.now().isoformat()
                    cur.execute("INSERT INTO spares_used(ts, part_number, name, quantity) VALUES(?,?,?,?)", (ts, part_number, final_name, qty))
                    # Update spares quantity
                    new_qty = max(current_qty - qty, 0)
                    cur.execute("UPDATE spares SET quantity = ?, name = ? WHERE part_number = ?", (new_qty, final_name, part_number))
                    self.conn.commit()
                    self.append_log(f"USED (manual): {qty} from {part_number} - {final_name} (New Total: {new_qty})")
                    # Clear inputs and refresh
                    qty_spin.setValue(0)
                    pn_edit.clear()
                    nm_edit.clear()
                    reload_table(search_edit.text().strip())
                except Exception as e:
                    self.append_log(f"Add used failed: {e}")

            def on_delete_selected():
                if "backup_restore" in self.locked_areas:
                    QMessageBox.warning(self, "Access Denied", "Backup/restore operations are currently locked.")
                    return
                try:
                    selected = table.selectionModel().selectedRows()
                    if not selected:
                        self.append_log("No rows selected.")
                        return
                    # Confirm
                    resp = QMessageBox.question(dlg, "Confirm Delete", f"Delete {len(selected)} record(s)?", QMessageBox.Yes | QMessageBox.No)
                    if resp != QMessageBox.Yes:
                        return
                    timestamps = []
                    for idx in selected:
                        row = idx.row()
                        item = table.item(row, 0) # timestamp column
                        if item:
                            timestamps.append(item.text())
                    if timestamps:
                        cur = self.conn.cursor()
                        cur.executemany("DELETE FROM spares_used WHERE ts=?", [(ts,) for ts in timestamps])
                        self.conn.commit()
                        self.append_log(f"Deleted {len(timestamps)} used record(s)")
                        reload_table(search_edit.text().strip())
                except Exception as e:
                    self.append_log(f"Delete selected failed: {e}")

            def on_delete_all():
                try:
                    resp = QMessageBox.warning(dlg, "Delete ALL Used Records", "This will delete ALL spares used records. Continue?", QMessageBox.Yes | QMessageBox.No)
                    if resp != QMessageBox.Yes:
                        return
                    cur = self.conn.cursor()
                    cur.execute("DELETE FROM spares_used")
                    self.conn.commit()
                    self.append_log("Deleted all used records")
                    reload_table("")
                except Exception as e:
                    self.append_log(f"Delete all failed: {e}")

            def on_export_used():
                if "export" in self.locked_areas:
                    QMessageBox.warning(dlg, "Access Denied", "Export functions are currently locked.")
                    return
                try:
                    filename, _ = QFileDialog.getSaveFileName(dlg, "Export Used Parts", "used_parts.csv", "CSV Files (*.csv)")
                    if not filename:
                        return
                    cur = self.conn.cursor()
                    filter_text = search_edit.text().strip()
                    if filter_text:
                        like = f"%{filter_text}%"
                        cur.execute(
                            "SELECT ts, part_number, name, quantity FROM spares_used WHERE part_number LIKE ? OR name LIKE ? ORDER BY ts DESC",
                            (like, like),
                        )
                    else:
                        cur.execute("SELECT ts, part_number, name, quantity FROM spares_used ORDER BY ts DESC")
                    rows = cur.fetchall()
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        import csv
                        writer = csv.writer(f)
                        writer.writerow(["Timestamp", "Part Number", "Name", "Quantity"])
                        for ts, pn, nm, qty in rows:
                            writer.writerow([ts, pn, nm, qty])
                    self.append_log(f"Exported {len(rows)} used records to {filename}")
                except Exception as e:
                    self.append_log(f"Export used failed: {e}")

            search_edit.textChanged.connect(lambda _: reload_table(search_edit.text().strip()))
            btn_add_used.clicked.connect(on_add_used)
            btn_delete_sel.clicked.connect(on_delete_selected)
            btn_delete_all.clicked.connect(on_delete_all)
            btn_export_used.clicked.connect(on_export_used)

            reload_table("")

            btns = QDialogButtonBox(QDialogButtonBox.Close)
            btns.rejected.connect(dlg.reject)
            btns.accepted.connect(dlg.accept)
            v.addWidget(btns)
            dlg.setLayout(v)
            dlg.resize(900, 600)
            dlg.exec_()
        except Exception as e:
            self.append_log(f"View spares_used failed: {e}")

    def _view_spares_issued_dialog(self):
        """Show spares issued dialog"""
        try:
            if not self._is_db_ready():
                return

            dlg = QDialog(self)
            dlg.setWindowTitle("Spares Issued")
            dlg.setSizeGripEnabled(True)
            dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowMaximizeButtonHint)
            v = QVBoxLayout()

            # Search bar
            search_edit = QLineEdit()
            search_edit.setPlaceholderText("Search by part number or name...")
            v.addWidget(search_edit)

            # Manual Add Issued row
            add_layout = QHBoxLayout()
            add_layout.addWidget(QLabel("Part Number:"))
            pn_edit = QLineEdit()
            add_layout.addWidget(pn_edit)
            add_layout.addWidget(QLabel("Name:"))
            nm_edit = QLineEdit()
            add_layout.addWidget(nm_edit)
            add_layout.addWidget(QLabel("Qty:"))
            qty_spin = QSpinBox()
            qty_spin.setRange(0, 999999)
            qty_spin.setValue(0)
            add_layout.addWidget(qty_spin)
            btn_add_issued = QPushButton("Add Issued")
            btn_add_issued.setMinimumSize(110, 30)
            add_layout.addWidget(btn_add_issued)
            v.addLayout(add_layout)

            # Table
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Timestamp", "Part Number", "Name", "Quantity"])
            table.setAlternatingRowColors(True)
            table.setSortingEnabled(True)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setSelectionMode(QTableWidget.MultiSelection)
            v.addWidget(table)

            # Actions row
            actions_h = QHBoxLayout()
            btn_delete_sel = QPushButton("Delete Selected")
            btn_delete_sel.setMinimumSize(140, 30)
            btn_delete_all = QPushButton("Delete All Records")
            btn_delete_all.setMinimumSize(160, 30)
            btn_export_issued = QPushButton("Export Issued")
            btn_export_issued.setMinimumSize(140, 30)
            actions_h.addWidget(btn_delete_sel)
            actions_h.addWidget(btn_delete_all)
            actions_h.addWidget(btn_export_issued)
            actions_h.addStretch(1)
            v.addLayout(actions_h)

            def reload_table(filter_text: str = ""):
                try:
                    cur = self.conn.cursor()
                    if filter_text:
                        like = f"%{filter_text}%"
                        cur.execute(
                            "SELECT ts, part_number, name, quantity FROM spares_issued WHERE part_number LIKE ? OR name LIKE ? ORDER BY ts DESC",
                            (like, like),
                        )
                    else:
                        cur.execute("SELECT ts, part_number, name, quantity FROM spares_issued ORDER BY ts DESC")
                    rows = cur.fetchall()
                    table.setRowCount(len(rows))
                    for i, (ts, pn, nm, qty) in enumerate(rows):
                        table.setItem(i, 0, QTableWidgetItem(str(ts)))
                        table.setItem(i, 1, QTableWidgetItem(str(pn)))
                        table.setItem(i, 2, QTableWidgetItem(str(nm)))
                        table.setItem(i, 3, QTableWidgetItem(str(qty)))
                    table.resizeColumnsToContents()
                except Exception as e:
                    self.append_log(f"Load spares_issued failed: {e}")

            def on_add_issued():
                try:
                    part_number = pn_edit.text().strip()
                    name = nm_edit.text().strip()
                    qty = int(qty_spin.value())
                    if not part_number or qty <= 0:
                        self.append_log("Provide part number and quantity > 0")
                        return
                    cur = self.conn.cursor()
                    # Check if part exists to get existing name and qty
                    cur.execute("SELECT quantity, name FROM spares WHERE part_number = ?", (part_number,))
                    row = cur.fetchone()
                    current_qty = row[0] if row else 0
                    existing_name = row[1] if row else ""
                    final_name = name.strip() or existing_name or "Unknown"
                    # Insert issued record
                    ts = datetime.now().isoformat()
                    cur.execute("INSERT INTO spares_issued(ts, part_number, name, quantity) VALUES(?,?,?,?)", (ts, part_number, final_name, qty))
                    # Update spares quantity (increase)
                    new_qty = current_qty + qty
                    cur.execute("INSERT OR REPLACE INTO spares(part_number, name, quantity) VALUES(?,?,?)", (part_number, final_name, new_qty))
                    self.conn.commit()
                    self.append_log(f"ISSUED (manual): {qty} to {part_number} - {final_name} (New Total: {new_qty})")
                    # Clear inputs and refresh
                    qty_spin.setValue(0)
                    pn_edit.clear()
                    nm_edit.clear()
                    reload_table(search_edit.text().strip())
                except Exception as e:
                    self.append_log(f"Add issued failed: {e}")

            def on_delete_selected():
                if "backup_restore" in self.locked_areas:
                    QMessageBox.warning(self, "Access Denied", "Backup/restore operations are currently locked.")
                    return
                try:
                    selected = table.selectionModel().selectedRows()
                    if not selected:
                        self.append_log("No rows selected.")
                        return
                    # Confirm
                    resp = QMessageBox.question(dlg, "Confirm Delete", f"Delete {len(selected)} record(s)?", QMessageBox.Yes | QMessageBox.No)
                    if resp != QMessageBox.Yes:
                        return
                    timestamps = []
                    for idx in selected:
                        row = idx.row()
                        item = table.item(row, 0) # timestamp column
                        if item:
                            timestamps.append(item.text())
                    if timestamps:
                        cur = self.conn.cursor()
                        cur.executemany("DELETE FROM spares_issued WHERE ts=?", [(ts,) for ts in timestamps])
                        self.conn.commit()
                        self.append_log(f"Deleted {len(timestamps)} issued record(s)")
                        reload_table(search_edit.text().strip())
                except Exception as e:
                    self.append_log(f"Delete selected failed: {e}")

            def on_delete_all():
                try:
                    resp = QMessageBox.warning(dlg, "Delete ALL Issued Records", "This will delete ALL spares issued records. Continue?", QMessageBox.Yes | QMessageBox.No)
                    if resp != QMessageBox.Yes:
                        return
                    cur = self.conn.cursor()
                    cur.execute("DELETE FROM spares_issued")
                    self.conn.commit()
                    self.append_log("Deleted all issued records")
                    reload_table("")
                except Exception as e:
                    self.append_log(f"Delete all failed: {e}")

            def on_export_issued():
                if "export" in self.locked_areas:
                    QMessageBox.warning(dlg, "Access Denied", "Export functions are currently locked.")
                    return
                try:
                    filename, _ = QFileDialog.getSaveFileName(dlg, "Export Issued Parts", "issued_parts.csv", "CSV Files (*.csv)")
                    if not filename:
                        return
                    cur = self.conn.cursor()
                    filter_text = search_edit.text().strip()
                    if filter_text:
                        like = f"%{filter_text}%"
                        cur.execute(
                            "SELECT ts, part_number, name, quantity FROM spares_issued WHERE part_number LIKE ? OR name LIKE ? ORDER BY ts DESC",
                            (like, like),
                        )
                    else:
                        cur.execute("SELECT ts, part_number, name, quantity FROM spares_issued ORDER BY ts DESC")
                    rows = cur.fetchall()
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        import csv
                        writer = csv.writer(f)
                        writer.writerow(["Timestamp", "Part Number", "Name", "Quantity"])
                        for ts, pn, nm, qty in rows:
                            writer.writerow([ts, pn, nm, qty])
                    self.append_log(f"Exported {len(rows)} issued records to {filename}")
                except Exception as e:
                    self.append_log(f"Export issued failed: {e}")

            search_edit.textChanged.connect(lambda _: reload_table(search_edit.text().strip()))
            btn_add_issued.clicked.connect(on_add_issued)
            btn_delete_sel.clicked.connect(on_delete_selected)
            btn_delete_all.clicked.connect(on_delete_all)
            btn_export_issued.clicked.connect(on_export_issued)

            reload_table("")

            btns = QDialogButtonBox(QDialogButtonBox.Close)
            btns.rejected.connect(dlg.reject)
            btns.accepted.connect(dlg.accept)
            v.addWidget(btns)
            dlg.setLayout(v)
            dlg.resize(900, 600)
            dlg.exec_()
        except Exception as e:
            self.append_log(f"View spares_issued failed: {e}")

    def _stocktake_dialog(self):
        """Show stocktake management dialog"""
        try:
            if not self._is_db_ready():
                return
            
            if not self._check_area_access("stocktake"):
                return

            dlg = QDialog(self)
            dlg.setWindowTitle("Stocktake Management")
            dlg.setSizeGripEnabled(True)
            dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowMaximizeButtonHint)
            v = QVBoxLayout()

            # Info label
            info_label = QLabel("Stocktake Management - View and delete inventory records by date (standalone, does not change Spares totals)")
            info_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
            v.addWidget(info_label)

            # Calendar and date selection section
            date_group = QGroupBox("Date Selection")
            date_layout = QHBoxLayout()
            
            # Date range selection
            date_layout.addWidget(QLabel("From:"))
            from_date = QDateEdit()
            from_date.setDate(QDate.currentDate().addDays(-30))  # Default to 30 days ago
            from_date.setCalendarPopup(True)
            date_layout.addWidget(from_date)
            
            date_layout.addWidget(QLabel("To:"))
            to_date = QDateEdit()
            to_date.setDate(QDate.currentDate())  # Default to today
            to_date.setCalendarPopup(True)
            date_layout.addWidget(to_date)
            
            # Calendar widget - responsive sizing
            calendar = QCalendarWidget()
            calendar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            calendar.setMinimumSize(450, 320)  # Ensure dates are not cut off
            calendar.clicked.connect(lambda date: to_date.setDate(date))
            date_layout.addWidget(calendar)
            
            # Date filter dropdown menu
            date_filter_combo = QComboBox()
            date_filter_combo.addItems(["Custom Range", "Today", "This Week", "This Month", "All Time"])
            date_filter_combo.setCurrentText("Custom Range")
            
            def on_date_filter_changed(text):
                if text == "Today":
                    self._set_date_range(from_date, to_date, "today")
                elif text == "This Week":
                    self._set_date_range(from_date, to_date, "week")
                elif text == "This Month":
                    self._set_date_range(from_date, to_date, "month")
                elif text == "All Time":
                    self._set_date_range(from_date, to_date, "all")
                # Custom Range doesn't need action - user can manually set dates
                reload_table(search_edit.text().strip())
            
            date_filter_combo.currentTextChanged.connect(on_date_filter_changed)
            
            # Add label and combo to layout
            filter_layout = QHBoxLayout()
            filter_layout.addWidget(QLabel("Quick Filter:"))
            filter_layout.addWidget(date_filter_combo)
            filter_layout.addStretch(1)
            date_layout.addLayout(filter_layout)
            
            # Connect date changes to reload table
            from_date.dateChanged.connect(lambda: reload_table(search_edit.text().strip()))
            to_date.dateChanged.connect(lambda: reload_table(search_edit.text().strip()))
            
            date_group.setLayout(date_layout)
            v.addWidget(date_group)

            # Search bar
            search_edit = QLineEdit()
            search_edit.setPlaceholderText("Search by part number or name...")
            v.addWidget(search_edit)
            
            # Summary section
            summary_layout = QHBoxLayout()
            summary_label = QLabel("Date Range: ")
            summary_label.setStyleSheet("font-weight: bold; color: #333;")
            summary_layout.addWidget(summary_label)
            
            date_summary = QLabel("Loading...")
            date_summary.setStyleSheet("color: #666; font-style: italic;")
            summary_layout.addWidget(date_summary)
            
            summary_layout.addStretch(1)
            
            record_count = QLabel("Records: 0")
            record_count.setStyleSheet("color: #4CAF50; font-weight: bold;")
            summary_layout.addWidget(record_count)
            
            v.addLayout(summary_layout)

            # Table with stocktake data
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Part Number", "Name", "Current Qty", "Last Updated"])
            table.setAlternatingRowColors(True)
            table.setSortingEnabled(True)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setSelectionMode(QTableWidget.MultiSelection)
            v.addWidget(table)

            # Actions row - reorganized in logical order
            actions_h = QHBoxLayout()
            
            # Primary actions (left side)
            btn_add_new = QPushButton("➕ Add New Part")
            btn_add_new.setMinimumSize(140, 35)
            btn_add_new.setToolTip("Add a new part to the stocktake inventory")
            
            btn_refresh = QPushButton("🔄 Refresh")
            btn_refresh.setMinimumSize(100, 35)
            btn_refresh.setToolTip("Refresh the stocktake data table")
            
            # Secondary actions (middle)
            btn_export_stock = QPushButton("📊 Export Report")
            btn_export_stock.setMinimumSize(140, 35)
            btn_export_stock.setToolTip("Export stocktake data to CSV file")
            
            # Destructive actions (right side)
            btn_delete_selected = QPushButton("🗑️ Delete Selected")
            btn_delete_selected.setMinimumSize(150, 35)
            btn_delete_selected.setToolTip("Delete selected stocktake records (multi-selection)")
            btn_delete_selected.setStyleSheet("QPushButton { background-color: #dc3545; } QPushButton:hover { background-color: #c82333; }")
            
            # Add buttons in logical order
            actions_h.addWidget(btn_add_new)
            actions_h.addWidget(btn_refresh)
            actions_h.addStretch(1)  # Push export and delete to the right
            actions_h.addWidget(btn_export_stock)
            actions_h.addWidget(btn_delete_selected)
            
            v.addLayout(actions_h)


            def add_new_part():
                """Add a new part to inventory"""
                try:
                    # Simple input dialog
                    part_num, ok = QInputDialog.getText(dlg, "Add New Part", "Part Number:")
                    if not ok or not part_num.strip():
                        return
                    
                    name, ok = QInputDialog.getText(dlg, "Add New Part", "Part Name:")
                    if not ok or not name.strip():
                        return
                    
                    quantity, ok = QInputDialog.getInt(dlg, "Add New Part", "Initial Quantity:", 0, 0, 999999)
                    if not ok:
                        return
                    
                    # Add to stock_counts table
                    cur = self.conn.cursor()
                    ts = datetime.now().isoformat()
                    cur.execute(
                        "INSERT INTO stock_counts(ts, source, part_number, name, quantity) VALUES(?,?,?,?,?)",
                        (ts, "manual", part_num.strip(), name.strip(), quantity)
                    )
                    self.conn.commit()
                    
                    self.append_log(f"Added new part: {part_num} - {name} (qty: {quantity})")
                    reload_table(search_edit.text().strip())
                    
                except Exception as e:
                    self.append_log(f"Failed to add new part: {e}")

            def reload_table(filter_text: str = ""):
                try:
                    cur = self.conn.cursor()
                    
                    # Get date range
                    from_date_str = from_date.date().toString("yyyy-MM-dd")
                    to_date_str = to_date.date().toString("yyyy-MM-dd")
                    
                    if filter_text:
                        like = f"%{filter_text}%"
                        cur.execute(
                            """SELECT sc.part_number, sc.name, SUM(sc.quantity) as total_qty, MAX(sc.ts) as latest_ts, COUNT(*) as entry_count
                               FROM stock_counts sc 
                               WHERE (sc.part_number LIKE ? OR sc.name LIKE ?) 
                               AND DATE(sc.ts) BETWEEN ? AND ?
                               GROUP BY sc.part_number, sc.name
                               ORDER BY sc.part_number ASC""",
                            (like, like, from_date_str, to_date_str),
                        )
                    else:
                        cur.execute("""SELECT sc.part_number, sc.name, SUM(sc.quantity) as total_qty, MAX(sc.ts) as latest_ts, COUNT(*) as entry_count
                                      FROM stock_counts sc 
                                      WHERE DATE(sc.ts) BETWEEN ? AND ?
                                      GROUP BY sc.part_number, sc.name
                                      ORDER BY sc.part_number ASC""",
                                      (from_date_str, to_date_str))
                    rows = cur.fetchall()
                    table.setRowCount(len(rows))
                    for i, (pn, nm, total_qty, latest_ts, entry_count) in enumerate(rows):
                        table.setItem(i, 0, QTableWidgetItem(str(pn)))
                        
                        # Show name with entry count if multiple entries
                        display_name = str(nm)
                        if entry_count > 1:
                            display_name += f" ({entry_count} entries)"
                        table.setItem(i, 1, QTableWidgetItem(display_name))
                        
                        table.setItem(i, 2, QTableWidgetItem(str(total_qty)))
                        # Timestamp column (read-only)
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(latest_ts)
                            formatted_ts = dt.strftime("%Y-%m-%d %H:%M")
                        except:
                            formatted_ts = latest_ts
                        ts_item = QTableWidgetItem(formatted_ts)
                        ts_item.setFlags(ts_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                        table.setItem(i, 3, ts_item)
                    table.resizeColumnsToContents()
                    
                    # Note: No auto-update of spares here (stocktake is standalone)
                    
                    # Update summary labels
                    date_summary.setText(f"{from_date_str} to {to_date_str}")
                    record_count.setText(f"Records: {len(rows)}")
                    
                    if len(rows) == 0:
                        self.append_log("No stock counts found for selected date range. Start by detecting some parts to build inventory.")
                except Exception as e:
                    self.append_log(f"Load stocktake failed: {e}")


            def on_delete_selected():
                if "backup_restore" in self.locked_areas:
                    QMessageBox.warning(self, "Access Denied", "Backup/restore operations are currently locked.")
                    return
                try:
                    selected = table.selectionModel().selectedRows()
                    if not selected:
                        self.append_log("No rows selected.")
                        return

                    # Get selected part numbers
                    selected_parts = []
                    for idx in selected:
                        row = idx.row()
                        pn = table.item(row, 0).text()
                        name = table.item(row, 1).text()
                        selected_parts.append((pn, name))
                    
                    # Confirm deletion
                    part_list = "\n".join([f"• {pn} - {name}" for pn, name in selected_parts])
                    resp = QMessageBox.question(dlg, "Confirm Delete", 
                                              f"Delete stocktake records for {len(selected_parts)} part(s)?\n\n{part_list}", 
                                              QMessageBox.Yes | QMessageBox.No)
                    if resp != QMessageBox.Yes:
                        return

                    # Delete from stock_counts table (all rows for selected parts)
                    cur = self.conn.cursor()
                    deleted_count = 0
                    for pn, name in selected_parts:
                        # Delete all stock_counts records for this part
                        cur.execute("DELETE FROM stock_counts WHERE part_number = ?", (pn,))
                        deleted_count += cur.rowcount
                        
                        self.append_log(f"Deleted stocktake records for {pn} - {name}")
                    
                    if deleted_count > 0:
                        self.conn.commit()
                        self.append_log(f"Deleted {deleted_count} stocktake records for {len(selected_parts)} part(s)")
                        reload_table(search_edit.text().strip())
                    else:
                        self.append_log("No records found to delete")
                except Exception as e:
                    self.append_log(f"Delete selected failed: {e}")



            def on_export_stock():
                if "export" in self.locked_areas:
                    QMessageBox.warning(dlg, "Access Denied", "Export functions are currently locked.")
                    return
                try:
                    filename, _ = QFileDialog.getSaveFileName(dlg, "Export Stock Report", "stock_report.csv", "CSV Files (*.csv)")
                    if filename:
                        cur = self.conn.cursor()
                        
                        # Get date range for export
                        from_date_str = from_date.date().toString("yyyy-MM-dd")
                        to_date_str = to_date.date().toString("yyyy-MM-dd")
                        
                        # Export aggregated inventory counts for selected date range
                        cur.execute("""SELECT sc.part_number, sc.name, SUM(sc.quantity) as total_qty, MAX(sc.ts) as latest_ts, COUNT(*) as entry_count
                                      FROM stock_counts sc 
                                      WHERE DATE(sc.ts) BETWEEN ? AND ?
                                      GROUP BY sc.part_number, sc.name
                                      ORDER BY sc.part_number ASC""",
                                      (from_date_str, to_date_str))
                        rows = cur.fetchall()
                        
                        with open(filename, 'w', newline='', encoding='utf-8') as f:
                            import csv
                            writer = csv.writer(f)
                            writer.writerow(["Part Number", "Name", "Total Quantity", "Entry Count", "Last Updated", "Date Range"])
                            for row in rows:
                                pn, name, total_qty, latest_ts, entry_count = row
                                try:
                                    from datetime import datetime
                                    dt = datetime.fromisoformat(latest_ts)
                                    formatted_ts = dt.strftime("%Y-%m-%d %H:%M")
                                except:
                                    formatted_ts = latest_ts
                                writer.writerow([pn, name, total_qty, entry_count, formatted_ts, f"{from_date_str} to {to_date_str}"])
                        
                        self.append_log(f"Stock report exported to {filename} ({len(rows)} items for {from_date_str} to {to_date_str})")
                except Exception as e:
                    self.append_log(f"Export failed: {e}")

            # Connect signals
            search_edit.textChanged.connect(lambda _: reload_table(search_edit.text().strip()))
            btn_refresh.clicked.connect(lambda: reload_table(search_edit.text().strip()))
            btn_delete_selected.clicked.connect(on_delete_selected)
            btn_export_stock.clicked.connect(on_export_stock)
            btn_add_new.clicked.connect(add_new_part)

            reload_table("")

            btns = QDialogButtonBox(QDialogButtonBox.Close)
            btns.rejected.connect(dlg.reject)
            btns.accepted.connect(dlg.accept)
            v.addWidget(btns)
            dlg.setLayout(v)
            dlg.resize(1000, 700)
            dlg.exec_()
        except Exception as e:
            self.append_log(f"Stocktake dialog failed: {e}")

    # ----------------------------
    # Data Comparison Dialog
    # ----------------------------
    def _data_comparison_dialog(self):
        """Show data comparison dialog for Excel/PDF upload and stocktake comparison"""
        try:
            if not self._is_db_ready():
                self.append_log("Database not ready. Cannot perform data comparison.")
                return
            
            if not self._check_area_access("data_comparison"):
                return

            dlg = QDialog(self)
            dlg.setWindowTitle("Data Comparison Tool")
            dlg.setSizeGripEnabled(True)
            dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowMaximizeButtonHint)
            v = QVBoxLayout()

            # Info label
            info_label = QLabel("Data Comparison Tool - Upload Excel/PDF and compare with stocktake data")
            info_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
            v.addWidget(info_label)

            # File Upload Section (collapsible via tabs)
            tabs = QTabWidget()
            tabs.setTabPosition(QTabWidget.North)
            tabs.setDocumentMode(True)

            upload_tab = QWidget()
            upload_layout = QVBoxLayout(upload_tab)
            
            # File selection
            file_layout = QHBoxLayout()
            file_layout.addWidget(QLabel("Select File:"))
            file_path_edit = QLineEdit()
            file_path_edit.setPlaceholderText("Choose Excel (.xlsx/.xls) or PDF file...")
            file_path_edit.setReadOnly(True)
            file_layout.addWidget(file_path_edit)
            
            btn_browse = QPushButton("Browse")
            file_layout.addWidget(btn_browse)
            
            upload_layout.addLayout(file_layout)
            
            # File info
            file_info_label = QLabel("No file selected")
            file_info_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
            upload_layout.addWidget(file_info_label)

            # Optional column mapping for Excel files
            mapping_group = QGroupBox("Column Mapping (Excel)")
            mapping_group_layout = QHBoxLayout()
            mapping_group.setLayout(mapping_group_layout)
            mapping_group.setVisible(False)

            mapping_group_layout.addWidget(QLabel("Part Number:"))
            map_part_combo = QComboBox()
            mapping_group_layout.addWidget(map_part_combo)

            mapping_group_layout.addWidget(QLabel("Quantity:"))
            map_qty_combo = QComboBox()
            mapping_group_layout.addWidget(map_qty_combo)

            mapping_group_layout.addWidget(QLabel("Name (optional):"))
            map_name_combo = QComboBox()
            mapping_group_layout.addWidget(map_name_combo)

            upload_layout.addWidget(mapping_group)
            
            tabs.addTab(upload_tab, "Upload")

            # Date Selection Section (as tab)
            date_tab = QWidget()
            date_layout = QHBoxLayout(date_tab)
            
            date_layout.addWidget(QLabel("From:"))
            from_date = QDateEdit()
            from_date.setDate(QDate.currentDate().addDays(-30))
            from_date.setCalendarPopup(True)
            date_layout.addWidget(from_date)
            
            date_layout.addWidget(QLabel("To:"))
            to_date = QDateEdit()
            to_date.setDate(QDate.currentDate())
            to_date.setCalendarPopup(True)
            date_layout.addWidget(to_date)
            
            # Quick date buttons
            btn_today = QPushButton("Today")
            btn_today.clicked.connect(lambda: self._set_date_range(from_date, to_date, "today"))
            btn_week = QPushButton("This Week")
            btn_week.clicked.connect(lambda: self._set_date_range(from_date, to_date, "week"))
            btn_month = QPushButton("This Month")
            btn_month.clicked.connect(lambda: self._set_date_range(from_date, to_date, "month"))
            
            date_layout.addWidget(btn_today)
            date_layout.addWidget(btn_week)
            date_layout.addWidget(btn_month)
            tabs.addTab(date_tab, "Dates")

            # Comparison Options (as second tab)
            options_tab = QWidget()
            options_layout = QVBoxLayout(options_tab)
            
            cb_auto_fill = QCheckBox("Auto-fill stocktake quantities")
            cb_auto_fill.setChecked(False)
            cb_auto_fill.setEnabled(False)
            cb_auto_fill.setToolTip("Disabled: Data Comparison is read-only and will not modify Stocktake data")
            options_layout.addWidget(cb_auto_fill)
            
            cb_highlight_mismatches = QCheckBox("Highlight quantity mismatches")
            cb_highlight_mismatches.setChecked(True)
            cb_highlight_mismatches.setToolTip("Highlight rows where uploaded quantities differ from stocktake")
            options_layout.addWidget(cb_highlight_mismatches)
            
            cb_include_unmatched = QCheckBox("Include unmatched stocktake items")
            cb_include_unmatched.setToolTip("Include stocktake items that don't match uploaded file")
            options_layout.addWidget(cb_include_unmatched)

            cb_sync_uploaded = QCheckBox("Sync uploaded qty from captured stocktake")
            cb_sync_uploaded.setChecked(False)
            cb_sync_uploaded.setToolTip("If enabled, the uploaded quantity column will be auto-filled with captured stocktake quantities for matching part numbers")
            options_layout.addWidget(cb_sync_uploaded)

            cb_auto_compare = QCheckBox("Auto-compare on date/column change")
            cb_auto_compare.setChecked(True)
            cb_auto_compare.setToolTip("Automatically refresh comparison when date range or column mapping changes")
            options_layout.addWidget(cb_auto_compare)
            
            tabs.addTab(options_tab, "Options")
            v.addWidget(tabs)

            # Action Buttons
            action_layout = QHBoxLayout()
            
            btn_compare = QPushButton("🔍 Compare Data")
            btn_compare.setStyleSheet("""
                QPushButton {
                    background: #4CAF50;
                    color: white;
                    border: 1px solid #2E7D32;
                    border-radius: 6px;
                    font-weight: bold;
                    padding: 10px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: #66BB6A;
                    border-color: #388E3C;
                }
            """)
            def run_compare():
                self._perform_data_comparison(
                    file_path_edit.text(), from_date.date(), to_date.date(),
                    cb_auto_fill.isChecked(), cb_highlight_mismatches.isChecked(), cb_include_unmatched.isChecked(),
                    results_table, results_summary, match_count, mismatch_count, btn_export,
                    {
                        'part': map_part_combo.currentText() if mapping_group.isVisible() else None,
                        'qty': map_qty_combo.currentText() if mapping_group.isVisible() else None,
                        'name': map_name_combo.currentText() if mapping_group.isVisible() else None,
                    },
                    captured_table,
                    cb_sync_uploaded.isChecked()
                )

            btn_compare.clicked.connect(run_compare)
            action_layout.addWidget(btn_compare)
            
            btn_apply_sync = QPushButton("↔ Apply Captured → Uploaded")
            btn_apply_sync.setMinimumSize(240, 30)
            btn_apply_sync.setToolTip("Copy captured stocktake quantities into uploaded column for matching parts")
            btn_apply_sync.clicked.connect(lambda: (
                cb_sync_uploaded.setChecked(True),
                run_compare()
            ))
            action_layout.addWidget(btn_apply_sync)

            btn_export = QPushButton("📤 Export Results")
            btn_export.setStyleSheet("""
                QPushButton {
                    background: #2196F3;
                    color: white;
                    border: 1px solid #1976D2;
                    border-radius: 6px;
                    font-weight: bold;
                    padding: 10px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: #42A5F5;
                    border-color: #1565C0;
                }
            """)
            btn_export.setEnabled(False)  # Will be enabled after comparison
            action_layout.addWidget(btn_export)
            
            action_layout.addStretch(1)
            v.addLayout(action_layout)

            # Results Table
            results_group = QGroupBox("Comparison Results")
            results_layout = QVBoxLayout()
            
            # Results summary
            summary_layout = QHBoxLayout()
            summary_label = QLabel("Results: ")
            summary_label.setStyleSheet("font-weight: bold; color: #333;")
            summary_layout.addWidget(summary_label)
            
            results_summary = QLabel("No comparison performed yet")
            results_summary.setStyleSheet("color: #666; font-style: italic;")
            summary_layout.addWidget(results_summary)
            
            summary_layout.addStretch(1)
            
            match_count = QLabel("Matches: 0")
            match_count.setStyleSheet("color: #4CAF50; font-weight: bold;")
            summary_layout.addWidget(match_count)
            
            mismatch_count = QLabel("Mismatches: 0")
            mismatch_count.setStyleSheet("color: #FF9800; font-weight: bold;")
            summary_layout.addWidget(mismatch_count)
            
            results_layout.addLayout(summary_layout)
            
            # Filter buttons for status
            filter_layout = QHBoxLayout()
            filter_all_btn = QPushButton("Show All")
            filter_match_btn = QPushButton("Matches Only")
            filter_mismatch_btn = QPushButton("Mismatches Only")
            filter_nomatch_btn = QPushButton("No Matches Only")
            
            filter_all_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; }")
            filter_match_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
            filter_mismatch_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; }")
            filter_nomatch_btn.setStyleSheet("QPushButton { background-color: #F44336; color: white; }")
            
            filter_layout.addWidget(QLabel("Filter by Status:"))
            filter_layout.addWidget(filter_all_btn)
            filter_layout.addWidget(filter_match_btn)
            filter_layout.addWidget(filter_mismatch_btn)
            filter_layout.addWidget(filter_nomatch_btn)
            filter_layout.addStretch()
            
            results_layout.addLayout(filter_layout)
            
            # Results search
            results_search = QLineEdit()
            results_search.setPlaceholderText("Search results by part number, name, or status...")
            results_layout.addWidget(results_search)

            # Results table
            results_table = QTableWidget()
            results_table.setColumnCount(4)
            results_table.setHorizontalHeaderLabels([
                "Part Number", "Name", "Stocktake Qty", "Status"
            ])
            results_table.setAlternatingRowColors(True)
            results_table.setSortingEnabled(True)
            results_table.setSelectionBehavior(QTableWidget.SelectRows)
            results_table.setSelectionMode(QTableWidget.MultiSelection)
            results_table.setMinimumHeight(260)
            results_table.verticalHeader().setVisible(False)
            results_table.horizontalHeader().setStretchLastSection(True)
            
            results_layout.addWidget(results_table)
            results_group.setLayout(results_layout)
            v.addWidget(results_group)

            # Connect export button to results table
            btn_export.clicked.connect(lambda: self._export_comparison_results(results_table))

            # Hook results search to filter table rows
            current_status_filter = [None]  # Use list to allow modification in nested functions
            
            def _filter_results_table(text: str = None, status_filter: str = None):
                try:
                    if status_filter is not None:
                        current_status_filter[0] = status_filter
                    
                    search_text = (text or results_search.text() or "").strip().lower()
                    status_filter = current_status_filter[0]
                    
                    for r in range(results_table.rowCount()):
                        pn = results_table.item(r, 0).text().lower() if results_table.item(r, 0) else ""
                        nm = results_table.item(r, 1).text().lower() if results_table.item(r, 1) else ""
                        sq = results_table.item(r, 2).text().lower() if results_table.item(r, 2) else ""
                        st = results_table.item(r, 3).text().lower() if results_table.item(r, 3) else ""
                        
                        # Check search text match
                        text_match = search_text == "" or (search_text in pn) or (search_text in nm) or (search_text in sq) or (search_text in st)
                        
                        # Check status filter match
                        status_match = True
                        if status_filter == "match":
                            status_match = st == "match"
                        elif status_filter == "mismatch":
                            status_match = st == "mismatch"
                        elif status_filter == "nomatch":
                            status_match = st == "no match" or st == "stocktake only"
                        
                        # Show row only if both conditions are met
                        results_table.setRowHidden(r, not (text_match and status_match))
                        
                except Exception as e:
                    self.append_log(f"Filter results failed: {e}")
            
            results_search.textChanged.connect(_filter_results_table)
            
            # Connect filter buttons
            filter_all_btn.clicked.connect(lambda: _filter_results_table(status_filter=None))
            filter_match_btn.clicked.connect(lambda: _filter_results_table(status_filter="match"))
            filter_mismatch_btn.clicked.connect(lambda: _filter_results_table(status_filter="mismatch"))
            filter_nomatch_btn.clicked.connect(lambda: _filter_results_table(status_filter="no match"))

            # Captured stocktake data panel (scrollable table)
            captured_group = QGroupBox("Captured Stocktake Data (from selected dates)")
            captured_layout = QVBoxLayout()
            captured_table = QTableWidget()
            captured_table.setColumnCount(4)
            captured_table.setHorizontalHeaderLabels(["Part Number", "Name", "Quantity", "Last Updated"])
            captured_table.setAlternatingRowColors(True)
            captured_table.setSortingEnabled(True)
            captured_table.setSelectionBehavior(QTableWidget.SelectRows)
            captured_table.setSelectionMode(QTableWidget.MultiSelection)
            captured_table.setMinimumHeight(260)
            captured_table.verticalHeader().setVisible(False)
            captured_table.horizontalHeader().setStretchLastSection(True)
            captured_layout.addWidget(captured_table)
            captured_group.setLayout(captured_layout)

            # Splitter to show both tables side-by-side for compact layout
            splitter = QSplitter()
            left_container = QWidget()
            left_layout = QVBoxLayout(left_container)
            left_layout.setContentsMargins(0, 0, 0, 0)
            left_layout.setSpacing(6)
            left_layout.addWidget(captured_group)
            right_container = QWidget()
            right_layout = QVBoxLayout(right_container)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.setSpacing(6)
            right_layout.addWidget(results_group)
            splitter.addWidget(left_container)
            splitter.addWidget(right_container)
            splitter.setSizes([700, 500])
            v.addWidget(splitter)

            # Actions for captured stocktake (left panel): Delete Selected within date range
            def delete_selected_stocktake():
                try:
                    selected = captured_table.selectionModel().selectedRows()
                    if not selected:
                        self.append_log("No captured rows selected for deletion")
                        return
                    # Confirm
                    resp = QMessageBox.question(dlg, "Confirm Delete", f"Delete stocktake records for {len(selected)} part(s) in selected date range?", QMessageBox.Yes | QMessageBox.No)
                    if resp != QMessageBox.Yes:
                        return
                    parts = []
                    for idx in selected:
                        row = idx.row()
                        item = captured_table.item(row, 0)
                        if item:
                            parts.append(self._normalize_part_number_str(item.text()))
                    if not parts:
                        return
                    cur = self.conn.cursor()
                    from_date_str = from_date.date().toString("yyyy-MM-dd")
                    to_date_str = to_date.date().toString("yyyy-MM-dd")
                    # Delete stock_counts rows for these parts within date range
                    for pn in parts:
                        cur.execute(
                            "DELETE FROM stock_counts WHERE part_number = ? AND DATE(ts) BETWEEN ? AND ?",
                            (pn, from_date_str, to_date_str)
                        )
                    self.conn.commit()
                    self.append_log(f"Deleted stocktake records for {len(parts)} part(s) between {from_date_str} and {to_date_str}")
                    # Refresh captured and results
                    run_compare()
                except Exception as e:
                    self.append_log(f"Delete captured stocktake failed: {e}")

            captured_actions = QHBoxLayout()
            btn_delete_captured = QPushButton("🗑 Delete Selected")
            btn_delete_captured.setMinimumHeight(28)
            btn_delete_captured.setToolTip("Delete stocktake records for selected parts within the chosen date range")
            btn_delete_captured.clicked.connect(delete_selected_stocktake)
            captured_actions.addWidget(btn_delete_captured)
            captured_actions.addStretch(1)
            captured_layout.addLayout(captured_actions)

            # Connect browse to open dialog and populate mapping
            btn_browse.clicked.connect(lambda: self._on_select_comparison_file(
                file_path_edit, mapping_group, map_part_combo, map_qty_combo, map_name_combo, file_info_label,
                (lambda: run_compare()) if cb_auto_compare.isChecked() else None
            ))

            # Helper function to populate captured stocktake table when date range changes
            def populate_captured_stocktake():
                try:
                    stocktake_data = self._load_stocktake_data(from_date.date(), to_date.date())
                    if stocktake_data:
                        rows = []
                        for pn, data in stocktake_data.items():
                            rows.append((pn, data.get('name', ''), data.get('quantity', 0), data.get('timestamp', '')))
                        captured_table.setRowCount(len(rows))
                        for i, (pn, nm, qty, ts) in enumerate(rows):
                            captured_table.setItem(i, 0, QTableWidgetItem(str(pn)))
                            captured_table.setItem(i, 1, QTableWidgetItem(str(nm)))
                            captured_table.setItem(i, 2, QTableWidgetItem(str(qty)))
                            captured_table.setItem(i, 3, QTableWidgetItem(str(ts)))
                        captured_table.resizeColumnsToContents()
                        self.append_log(f"Loaded {len(rows)} stocktake items for selected date range")
                    else:
                        captured_table.setRowCount(0)
                        self.append_log("No stocktake data found for selected date range")
                except Exception as e:
                    self.append_log(f"Failed to populate captured stocktake: {e}")

            # Auto-run when dates change - always populate captured table, run comparison if file selected
            def on_date_changed():
                populate_captured_stocktake()
                if cb_auto_compare.isChecked() and file_path_edit.text().strip():
                    run_compare()
            
            from_date.dateChanged.connect(lambda _: on_date_changed())
            to_date.dateChanged.connect(lambda _: on_date_changed())
            
            # Initial population of captured stocktake table
            populate_captured_stocktake()

            # Auto-run when mapping changes
            map_part_combo.currentTextChanged.connect(lambda _:
                (run_compare() if (cb_auto_compare.isChecked() and file_path_edit.text().strip()) else None)
            )
            map_qty_combo.currentTextChanged.connect(lambda _:
                (run_compare() if (cb_auto_compare.isChecked() and file_path_edit.text().strip()) else None)
            )
            map_name_combo.currentTextChanged.connect(lambda _:
                (run_compare() if (cb_auto_compare.isChecked() and file_path_edit.text().strip()) else None)
            )

            # Close button
            btns = QDialogButtonBox(QDialogButtonBox.Close)
            btns.rejected.connect(dlg.reject)
            v.addWidget(btns)
            
            dlg.setLayout(v)
            dlg.resize(1200, 800)
            dlg.exec_()
            
        except Exception as e:
            self.append_log(f"Data comparison dialog failed: {e}")

    def _browse_comparison_file(self, file_path_edit):
        """Browse for Excel or PDF file for comparison"""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, 
                "Select File for Comparison", 
                "", 
                "Excel Files (*.xlsx *.xls);;PDF Files (*.pdf);;All Files (*)"
            )
            if filename:
                file_path_edit.setText(filename)
                self.append_log(f"Selected file for comparison: {filename}")
        except Exception as e:
            self.append_log(f"File browse failed: {e}")

    def _on_select_comparison_file(self, file_path_edit, mapping_group, map_part_combo, map_qty_combo, map_name_combo, info_label, on_selected_callback=None):
        """Open file dialog and populate column mapping for Excel files"""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, 
                "Select File for Comparison", 
                "", 
                "Excel Files (*.xlsx *.xls);;PDF Files (*.pdf);;All Files (*)"
            )
            if not filename:
                return
            file_path_edit.setText(filename)
            info_label.setText(os.path.basename(filename))
            ext = os.path.splitext(filename)[1].lower()
            if ext in [".xlsx", ".xls"]:
                # Load columns
                try:
                    df = pd.read_excel(filename, nrows=1)
                    columns = [str(c) for c in df.columns.tolist()]
                except Exception as e:
                    self.append_log(f"Failed to read Excel columns: {e}")
                    columns = []
                # Populate combos
                for combo in (map_part_combo, map_qty_combo, map_name_combo):
                    combo.clear()
                    combo.addItems(columns)
                    combo.setEditable(False)
                mapping_group.setVisible(True)
            else:
                # Hide mapping for PDFs or others
                mapping_group.setVisible(False)
            if callable(on_selected_callback):
                try:
                    on_selected_callback()
                except Exception as e:
                    self.append_log(f"Auto compare after select failed: {e}")
        except Exception as e:
            self.append_log(f"Select file failed: {e}")

    def _perform_data_comparison(self, file_path, from_date, to_date, auto_fill, highlight_mismatches, include_unmatched,
                                 results_table=None, results_summary=None, match_count_label=None, mismatch_count_label=None, export_button=None,
                                 column_mapping=None, captured_table=None, sync_uploaded_from_captured=False):
        """Perform the actual data comparison between uploaded file and stocktake data"""
        try:
            if not file_path or not os.path.exists(file_path):
                self.append_log("Please select a valid file for comparison")
                return
            
            # Load uploaded file data (using mapping if provided for Excel)
            uploaded_data = self._load_comparison_file(file_path, column_mapping=column_mapping)
            if not uploaded_data:
                self.append_log("Failed to load uploaded file data")
                return
            
            # Load stocktake data for the date range
            stocktake_data = self._load_stocktake_data(from_date, to_date)
            if not stocktake_data:
                self.append_log("No stocktake data found for the selected date range")
                return
            
            # Debug prints: sizes
            self.append_log(f"Compare: uploaded={len(uploaded_data)} items, stocktake={len(stocktake_data)} items")
            if len(uploaded_data) > 0:
                sample_up = uploaded_data[0]
                self.append_log(f"Sample uploaded -> PN='{sample_up.get('part_number')}', qty={sample_up.get('quantity')}")
            # Optionally sync uploaded qty from captured stocktake data
            if sync_uploaded_from_captured:
                try:
                    # Build quick lookup from captured data
                    for item in uploaded_data:
                        pn = self._normalize_part_number_str(item['part_number'])
                        if pn in stocktake_data:
                            item['quantity'] = int(stocktake_data[pn].get('quantity', item['quantity']))
                    self.append_log("Uploaded quantities synchronized from captured stocktake data")
                except Exception as e:
                    self.append_log(f"Sync uploaded from captured failed: {e}")

            # Perform comparison
            comparison_results = self._compare_data_sets(uploaded_data, stocktake_data, auto_fill, include_unmatched)
            
            # Update results table and summary
            self._update_comparison_results(
                comparison_results,
                highlight_mismatches,
                include_unmatched,
                results_table,
                results_summary,
                match_count_label,
                mismatch_count_label,
                export_button,
                from_date,
                to_date
            )
            
            self.append_log(f"Data comparison completed: {len(comparison_results)} items processed")

            # Populate captured stocktake table if provided
            if captured_table is not None:
                try:
                    # Build a list of rows from stocktake dictionary
                    rows = []
                    for pn, data in stocktake_data.items():
                        rows.append((pn, data.get('name', ''), data.get('quantity', 0), data.get('timestamp', '')))
                    captured_table.setRowCount(len(rows))
                    for i, (pn, nm, qty, ts) in enumerate(rows):
                        captured_table.setItem(i, 0, QTableWidgetItem(str(pn)))
                        captured_table.setItem(i, 1, QTableWidgetItem(str(nm)))
                        captured_table.setItem(i, 2, QTableWidgetItem(str(qty)))
                        captured_table.setItem(i, 3, QTableWidgetItem(str(ts)))
                    captured_table.resizeColumnsToContents()
                except Exception as e:
                    self.append_log(f"Populate captured table failed: {e}")
            
        except Exception as e:
            self.append_log(f"Data comparison failed: {e}")

    def _load_comparison_file(self, file_path, column_mapping=None):
        """Load data from Excel or PDF file"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.xlsx', '.xls']:
                # Load Excel file
                df = pd.read_excel(file_path)
                self.append_log(f"Loaded Excel file with {len(df)} rows")
                
                # Try to identify part number and quantity columns
                columns = df.columns.tolist()
                part_col = None
                qty_col = None
                name_col = None
                # If mapping provided and valid, use it
                if column_mapping:
                    pc = column_mapping.get('part')
                    qc = column_mapping.get('qty')
                    nc = column_mapping.get('name')
                    if pc in columns:
                        part_col = pc
                    if qc in columns:
                        qty_col = qc
                    if nc in columns:
                        name_col = nc
                
                # If still missing, look for common column names with expanded keywords
                # Use priority-based detection to avoid conflicts
                if not part_col or not qty_col or not name_col:
                    # First pass: detect specific columns with high priority keywords
                    for col in columns:
                        col_lower = col.lower().strip()
                        # High priority part number detection
                        if not part_col and any(keyword in col_lower for keyword in ['part number', 'part_number', 'partnumber', 'pn', 'sku', 'item code', 'item_code']):
                            part_col = col
                        # High priority quantity detection
                        if not qty_col and any(keyword in col_lower for keyword in ['quantity', 'qty', 'stock', 'on hand', 'onhand', 'available', 'balance']):
                            qty_col = col
                        # High priority name detection
                        if not name_col and any(keyword in col_lower for keyword in ['description', 'desc', 'name', 'title', 'product name', 'item name']):
                            name_col = col
                    
                    # Second pass: fallback detection for remaining columns
                    for col in columns:
                        col_lower = col.lower().strip()
                        # Fallback part number detection (avoid 'item' if description column exists)
                        if not part_col and any(keyword in col_lower for keyword in ['part', 'number', 'code', 'id']):
                            part_col = col
                        # Fallback quantity detection
                        if not qty_col and any(keyword in col_lower for keyword in ['amount', 'count']):
                            qty_col = col
                        # Fallback name detection (only use 'item' if no description-like column found)
                        if not name_col and 'item' in col_lower and not any('desc' in c.lower() for c in columns):
                            name_col = col
                
                if not part_col:
                    self.append_log("Could not identify part number column in Excel file")
                    return None
                
                # Continue processing even if quantity column is not found
                if not qty_col:
                    self.append_log("Warning: Could not identify quantity column in Excel file. Will import with default quantity of 0.")
                    qty_col = None  # Will handle this in data extraction
                
                # Extract data
                data = []
                for _, row in df.iterrows():
                    raw_pn = row[part_col]
                    part_number = self._normalize_part_number_str(raw_pn)
                    
                    # Handle quantity - use default if column not found
                    if qty_col is not None:
                        raw_qty = row[qty_col]
                        quantity = self._parse_quantity_value(raw_qty)
                    else:
                        quantity = 0  # Default quantity when column not found
                    
                    name_raw = str(row[name_col]).strip() if name_col else ""
                    name = self._sanitize_name(name_raw, part_number)
                    
                    if part_number and part_number.lower() != 'nan':
                        data.append({
                            'part_number': part_number,
                            'name': name,
                            'quantity': quantity
                        })
                
                return data
                
            elif file_ext == '.pdf':
                if not PDF_SUPPORT:
                    self.append_log("PDF support not available. Please install pdfplumber or use Excel files.")
                    return None
                
                # Load PDF file using pdfplumber
                try:
                    with pdfplumber.open(file_path) as pdf:
                        all_text = ""
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                all_text += text + "\n"
                    
                    self.append_log(f"Extracted text from PDF: {len(all_text)} characters")
                    
                    # Parse the extracted text to find part numbers and quantities
                    # This is a basic implementation - you may need to customize based on your PDF format
                    data = self._parse_pdf_text(all_text)
                    
                    if data:
                        self.append_log(f"Parsed {len(data)} items from PDF")
                        return data
                    else:
                        self.append_log("Could not parse part numbers and quantities from PDF text")
                        return None
                        
                except Exception as e:
                    self.append_log(f"PDF parsing failed: {e}")
                    return None
            else:
                self.append_log(f"Unsupported file type: {file_ext}")
                return None
                
        except Exception as e:
            self.append_log(f"Failed to load comparison file: {e}")
            return None

    def _parse_pdf_text(self, text):
        """Parse PDF text to extract part numbers and quantities"""
        try:
            data = []
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for part number patterns (5-12 digits + dash + 4 digits)
                part_match = PART_NUMBER_REGEX.search(line)
                if part_match:
                    part_number = f"{part_match.group(1)}-{part_match.group(2)}"
                    
                    # Look for quantity patterns in the same line
                    # Common patterns: numbers, "Qty:", "Quantity:", etc.
                    qty_patterns = [
                        r'(\d+)\s*$',  # Number at end of line
                        r'Qty[:\s]*(\d+)',  # Qty: number
                        r'Quantity[:\s]*(\d+)',  # Quantity: number
                        r'(\d+)\s*[Pp]cs?',  # Number pcs
                        r'(\d+)\s*[Uu]nits?',  # Number units
                    ]
                    
                    quantity = 0
                    for pattern in qty_patterns:
                        qty_match = re.search(pattern, line, re.IGNORECASE)
                        if qty_match:
                            try:
                                quantity = int(qty_match.group(1))
                                break
                            except (ValueError, IndexError):
                                continue
                    
                    # Extract name/description (text before part number)
                    name = line[:part_match.start()].strip()
                    if not name:
                        # Try to get name from next line if available
                        name = "Unknown"
                    
                    data.append({
                        'part_number': part_number,
                        'name': name,
                        'quantity': quantity
                    })
            
            return data
            
        except Exception as e:
            self.append_log(f"PDF text parsing failed: {e}")
            return []

    def _load_stocktake_data(self, from_date, to_date):
        """Load stocktake data for the specified date range"""
        try:
            if not self._is_db_ready():
                return None
            
            cur = self.conn.cursor()
            
            # Convert QDate to string format
            from_date_str = from_date.toString("yyyy-MM-dd")
            to_date_str = to_date.toString("yyyy-MM-dd")
            
            # Query inventory counts for the date range (inclusive on full days)
            # Include all sources so historical counts from camera/manual are considered
            cur.execute("""
                SELECT part_number, name, quantity, ts
                FROM stock_counts 
                WHERE DATE(ts) BETWEEN ? AND ?
                ORDER BY part_number, ts DESC
            """, (from_date_str, to_date_str))
            
            rows = cur.fetchall()
            
            # Group by part number and get the latest quantity for each
            stocktake_data = {}
            for row in rows:
                part_number, name, quantity, ts = row
                part_number = self._normalize_part_number_str(part_number)
                if part_number not in stocktake_data:
                    stocktake_data[part_number] = {
                        'name': name,
                        'quantity': quantity,
                        'timestamp': ts
                    }
            
            if len(stocktake_data) == 0:
                # No fallback to spares table - only show actual stocktake data
                # This ensures comparison only uses real stocktake entries from the Stocktake Management section
                self.append_log(f"No stocktake data found in date range {from_date_str} to {to_date_str}")
                self.append_log("Tip: Use the Stocktake Management section to capture inventory data first")
            self.append_log(f"Loaded {len(stocktake_data)} stocktake items from {from_date_str} to {to_date_str}")
            return stocktake_data
            
        except Exception as e:
            self.append_log(f"Failed to load stocktake data: {e}")
            return None

    def _compare_data_sets(self, uploaded_data, stocktake_data, auto_fill, include_unmatched):
        """Compare uploaded data with stocktake data"""
        try:
            comparison_results = []
            
            # Process uploaded data
            for item in uploaded_data:
                part_number = self._normalize_part_number_str(item['part_number'])
                uploaded_qty = item['quantity']
                uploaded_name = item['name']
                
                if part_number in stocktake_data:
                    self.append_log(f"MATCH: {part_number}")
                    # Match found
                    stocktake_qty = stocktake_data[part_number]['quantity']
                    stocktake_name = self._sanitize_name(stocktake_data[part_number]['name'], part_number)
                    
                    difference = uploaded_qty - stocktake_qty
                    status = "Match"  # Part number found = Match, regardless of quantity difference
                    
                    comparison_results.append({
                        'part_number': part_number,
                        'name': stocktake_name or uploaded_name,
                        'uploaded_qty': uploaded_qty,
                        'stocktake_qty': stocktake_qty,
                        'difference': difference,
                        'status': status,
                        'matched': True
                    })
                    
                    # Auto-fill disabled: Data comparison is read-only and does not modify stocktake
                        
                else:
                    self.append_log(f"NO MATCH: {part_number}")
                    # No match found
                    comparison_results.append({
                        'part_number': part_number,
                        'name': uploaded_name,
                        'uploaded_qty': uploaded_qty,
                        'stocktake_qty': 0,
                        'difference': uploaded_qty,
                        'status': "No Match",
                        'matched': False
                    })
            
            # Add unmatched stocktake items if requested
            if include_unmatched:
                uploaded_part_numbers = {self._normalize_part_number_str(item['part_number']) for item in uploaded_data}
                for part_number, data in stocktake_data.items():
                    if part_number not in uploaded_part_numbers:
                        self.append_log(f"STOCKTAKE ONLY: {part_number}")
                        comparison_results.append({
                            'part_number': part_number,
                            'name': data['name'],
                            'uploaded_qty': 0,
                            'stocktake_qty': data['quantity'],
                            'difference': -data['quantity'],
                            'status': "Stocktake Only",
                            'matched': False
                        })
            
            return comparison_results
            
        except Exception as e:
            self.append_log(f"Data comparison failed: {e}")
            return []

    def _update_stocktake_quantity(self, part_number, new_quantity):
        """Update stocktake quantity for a part number"""
        try:
            if not self._is_db_ready():
                return
            
            cur = self.conn.cursor()
            ts = datetime.now().isoformat()
            
            # Get the current name from spares table
            cur.execute("SELECT name FROM spares WHERE part_number = ?", (part_number,))
            result = cur.fetchone()
            name = result[0] if result else "Unknown"
            
            # Insert new stocktake record
            cur.execute("""
                INSERT INTO stock_counts(ts, source, part_number, name, quantity) 
                VALUES(?,?,?,?,?)
            """, (ts, "stocktake", part_number, name, new_quantity))
            
            self.conn.commit()
            self.append_log(f"Updated stocktake quantity for {part_number}: {new_quantity}")
            
        except Exception as e:
            self.append_log(f"Failed to update stocktake quantity: {e}")

    def _update_comparison_results(self, comparison_results, highlight_mismatches, include_unmatched,
                                   results_table=None, results_summary=None, match_count_label=None,
                                   mismatch_count_label=None, export_button=None, from_date=None, to_date=None):
        """Update the comparison results table and summary"""
        try:
            matches = sum(1 for r in comparison_results if r['status'] == "Match")
            mismatches = sum(1 for r in comparison_results if r['status'] == "Mismatch")

            # Update labels if provided
            if match_count_label is not None:
                match_count_label.setText(f"Matches: {matches}")
            if mismatch_count_label is not None:
                mismatch_count_label.setText(f"Mismatches: {mismatches}")
            if results_summary is not None and from_date is not None and to_date is not None:
                results_summary.setText(f"Compared {len(comparison_results)} items | Date range: {from_date.toString('yyyy-MM-dd')} → {to_date.toString('yyyy-MM-dd')}")
            if export_button is not None:
                export_button.setEnabled(True)

            # Populate table if provided
            if results_table is not None:
                results_table.setRowCount(len(comparison_results))
                for i, r in enumerate(comparison_results):
                    results_table.setItem(i, 0, QTableWidgetItem(str(r['part_number'])))
                    results_table.setItem(i, 1, QTableWidgetItem(str(r['name'])))
                    results_table.setItem(i, 2, QTableWidgetItem(str(r['stocktake_qty'])))
                    status_item = QTableWidgetItem(str(r['status']))
                    results_table.setItem(i, 3, status_item)

                    # Highlight mismatches if requested
                    if highlight_mismatches and r['status'] in ("Mismatch", "No Match", "Stocktake Only"):
                        for c in range(0, 4):
                            item = results_table.item(i, c)
                            if item:
                                item.setBackground(Qt.yellow)
                    elif r['status'] == "Match":
                        for c in range(0, 4):
                            item = results_table.item(i, c)
                            if item:
                                # Reset to default background; using transparent allows alternating row colors
                                item.setBackground(Qt.transparent)

                results_table.resizeColumnsToContents()

            # Always log a brief summary
            self.append_log(f"Comparison results: {matches} matches, {mismatches} mismatches, total {len(comparison_results)} rows")
        except Exception as e:
            self.append_log(f"Failed to update comparison results: {e}")

    def _export_comparison_results(self, results_table):
        """Export comparison results to Excel file with color formatting"""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import PatternFill
            
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Export Comparison Results", 
                f"comparison_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "Excel Files (*.xlsx)"
            )
            
            if not filename:
                return
            
            # Create workbook and worksheet
            wb = Workbook()
            ws = wb.active
            ws.title = "Comparison Results"
            
            # Add headers
            headers = ["Part Number", "Name", "Stocktake Qty", "Status"]
            for col, header in enumerate(headers, 1):
                ws.cell(row=1, column=col, value=header)
            
            # Define color fills
            green_fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")  # Light green for matches
            red_fill = PatternFill(start_color="FFB6C1", end_color="FFB6C1", fill_type="solid")    # Light red for no matches
            
            # Extract data from table and add to worksheet with colors
            for row in range(results_table.rowCount()):
                excel_row = row + 2  # Start from row 2 (after headers)
                status_text = ""
                
                for col in range(results_table.columnCount()):
                    item = results_table.item(row, col)
                    cell_value = item.text() if item else ""
                    ws.cell(row=excel_row, column=col + 1, value=cell_value)
                    
                    # Store status for color formatting
                    if col == 3:  # Status column
                        status_text = cell_value.lower()
                
                # Apply color formatting to status column only
                if status_text == "match":
                    ws.cell(row=excel_row, column=4).fill = green_fill  # Status column only
                elif status_text in ["no match", "stocktake only"]:
                    ws.cell(row=excel_row, column=4).fill = red_fill    # Status column only
            
            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            wb.save(filename)
            self.append_log(f"Comparison results exported to {filename} with color formatting")
            
        except Exception as e:
            self.append_log(f"Export failed: {e}")

    # ----------------------------
    # Save log
    # ----------------------------
    def save_log(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save log", "scan_log.txt", "Text files (*.txt)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_text.toPlainText())
            self.append_log(f"Saved log to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Save error", f"Failed to save log: {e}")

    def _record_spare_used(self, part_number: str, name: str, quantity: int):
        try:
            cur = self.conn.cursor()
            ts = datetime.now().isoformat()
            cur.execute("INSERT INTO spares_used(ts, part_number, name, quantity) VALUES(?,?,?,?)", (ts, part_number, name, quantity))
            self.conn.commit()
            self.append_log(f"Recorded {quantity} used for {part_number}")
        except Exception as e:
            self.append_log(f"Record used failed: {e}")

    def _record_spare_issued(self, part_number: str, name: str, quantity: int):
        try:
            cur = self.conn.cursor()
            ts = datetime.now().isoformat()
            cur.execute("INSERT INTO spares_issued(ts, part_number, name, quantity) VALUES(?,?,?,?)", (ts, part_number, name, quantity))
            self.conn.commit()
            self.append_log(f"Recorded {quantity} issued for {part_number}")
        except Exception as e:
            self.append_log(f"Record issued failed: {e}")

    def _save_log(self):
        """Save the current log to a file with advanced formatting"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Log File", 
                f"stocktake_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt);;All Files (*)"
            )
            if filename:
                # Get plain text content
                log_content = self.log_text.toPlainText()
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Stocktake Application Log\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"{'='*50}\n\n")
                    f.write(log_content)
                
                self.append_log(f"Log saved to: {filename}")
                
                # Update status
                if hasattr(self, 'log_status_label'):
                    self.log_status_label.setText("Saved")
                    self.log_status_label.setStyleSheet("color: #4CAF50; font-size: 10px;")
                    
        except Exception as e:
            self.append_log(f"Failed to save log: {e}")
            if hasattr(self, 'log_status_label'):
                self.log_status_label.setText("Save Failed")
                self.log_status_label.setStyleSheet("color: #ff4444; font-size: 10px;")

    def _admin_login_prompt(self):
        """Prompt for admin password before opening admin dialog"""
        if "admin_panel" in self.locked_areas:
            QMessageBox.warning(self, "Access Denied", "Admin panel access is currently locked.")
            return
        try:
            self.append_log("Admin button clicked")
            
            # Check if admin protection is enabled and user is not logged in
            if self.admin_enabled and not self.admin_session_active:
                self.append_log("Password required - showing login dialog")
                password, ok = QInputDialog.getText(self, "Admin Login", 
                                                  "Enter admin password:", 
                                                  QLineEdit.Password)
                if not ok:
                    self.append_log("Login cancelled")
                    return
                
                if hashlib.md5(password.encode()).hexdigest() != self.admin_password:
                    # Invalid password - invalidate any active session and log attempt
                    self.admin_session_active = False
                    self._save_admin_settings()  # Persist security state immediately
                    self.append_log("Invalid password attempt - admin access denied")
                    QMessageBox.warning(self, "Access Denied", "Invalid password. Admin access denied and session invalidated for security.")
                    return
                
                self.append_log("Login successful")
                self.admin_session_active = True
                self._start_session_timer()  # Start session timeout
            elif not self.admin_enabled:
                self.append_log("Admin protection disabled - direct access")
                self.admin_session_active = True
                self._start_session_timer()  # Start session timeout
            
            # Open admin dialog
            self._admin_dialog()
            
        except Exception as e:
            self.append_log(f"Admin error: {e}")
            QMessageBox.critical(self, "Error", f"Admin error: {e}")

    def _admin_dialog(self):
        """Show admin settings dialog"""
        try:
            dlg = QDialog(self)
            dlg.setWindowTitle("Admin Settings")
            dlg.setSizeGripEnabled(True)
            dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowMaximizeButtonHint)
            v = QVBoxLayout()

            # Info label
            info_label = QLabel("Admin Settings - Configure password protection and area locks")
            info_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
            v.addWidget(info_label)

            # Password section
            password_group = QGroupBox("Password Management")
            password_layout = QVBoxLayout()
            
            # Current password status
            status_layout = QHBoxLayout()
            status_label = QLabel("Status:")
            status_value = QLabel("Not Set" if not self.admin_password else "Set")
            status_value.setStyleSheet("color: #4CAF50; font-weight: bold;" if self.admin_password else "color: #FF5722; font-weight: bold;")
            status_layout.addWidget(status_label)
            status_layout.addWidget(status_value)
            status_layout.addStretch(1)
            password_layout.addLayout(status_layout)
            
            # Set/Change password
            password_input_layout = QHBoxLayout()
            password_input_layout.addWidget(QLabel("New Password:"))
            password_edit = QLineEdit()
            password_edit.setEchoMode(QLineEdit.Password)
            password_edit.setPlaceholderText("Enter new password")
            password_input_layout.addWidget(password_edit)
            
            confirm_edit = QLineEdit()
            confirm_edit.setEchoMode(QLineEdit.Password)
            confirm_edit.setPlaceholderText("Confirm password")
            password_input_layout.addWidget(confirm_edit)
            
            btn_set_password = QPushButton("Set Password")
            btn_set_password.setMinimumSize(120, 30)
            password_input_layout.addWidget(btn_set_password)
            password_layout.addLayout(password_input_layout)
            
            # Reset password
            reset_layout = QHBoxLayout()
            btn_reset_password = QPushButton("Reset Password")
            btn_reset_password.setMinimumSize(120, 30)
            btn_reset_password.setStyleSheet("background: #FF5722; color: white;")
            reset_layout.addWidget(btn_reset_password)
            reset_layout.addStretch(1)
            password_layout.addLayout(reset_layout)
            
            password_group.setLayout(password_layout)
            v.addWidget(password_group)

            # Area Locking section
            lock_group = QGroupBox("Area Locking")
            lock_layout = QVBoxLayout()
            
            # Checkboxes for different areas
            self.cb_lock_spares = QCheckBox("Lock Spares Management")
            self.cb_lock_spares_add = QCheckBox("Lock Add/Update Spares")
            self.cb_lock_spares_delete_selected = QCheckBox("Lock Delete Selected Spares")
            self.cb_lock_spares_delete_all = QCheckBox("Lock Delete All Spares")
            self.cb_lock_spares_reset_quantity = QCheckBox("Lock Reset Quantity")
            self.cb_lock_edit_amount = QCheckBox("Lock Edit Amount on View Spares")
            self.cb_lock_used = QCheckBox("Lock Used Parts View")
            self.cb_lock_issued = QCheckBox("Lock Issued Parts View")
            self.cb_lock_stocktake = QCheckBox("Lock Stocktake Management")
            self.cb_lock_import = QCheckBox("Lock Import Functions")
            self.cb_lock_data_comparison = QCheckBox("Lock Data Comparison")
            self.cb_lock_models = QCheckBox("Lock Model Training")

            self.cb_lock_export = QCheckBox("Lock Export Functions")
            self.cb_lock_admin_panel = QCheckBox("Lock Admin Panel Access")
            self.cb_lock_ocr_corrections = QCheckBox("Lock OCR Corrections")
            self.cb_lock_camera_controls = QCheckBox("Lock Camera Controls")
            self.cb_lock_data_sync = QCheckBox("Lock Data Synchronization")
            self.cb_lock_backup_restore = QCheckBox("Lock Backup/Restore Functions")
            
            lock_layout.addWidget(self.cb_lock_spares)
            lock_layout.addWidget(self.cb_lock_spares_add)
            lock_layout.addWidget(self.cb_lock_spares_delete_selected)
            lock_layout.addWidget(self.cb_lock_spares_delete_all)
            lock_layout.addWidget(self.cb_lock_spares_reset_quantity)
            lock_layout.addWidget(self.cb_lock_edit_amount)
            lock_layout.addWidget(self.cb_lock_used)
            lock_layout.addWidget(self.cb_lock_issued)
            lock_layout.addWidget(self.cb_lock_stocktake)
            lock_layout.addWidget(self.cb_lock_import)
            lock_layout.addWidget(self.cb_lock_data_comparison)
            lock_layout.addWidget(self.cb_lock_models)

            lock_layout.addWidget(self.cb_lock_export)
            lock_layout.addWidget(self.cb_lock_admin_panel)
            lock_layout.addWidget(self.cb_lock_ocr_corrections)
            lock_layout.addWidget(self.cb_lock_camera_controls)
            lock_layout.addWidget(self.cb_lock_data_sync)
            lock_layout.addWidget(self.cb_lock_backup_restore)
            
            lock_group.setLayout(lock_layout)
            v.addWidget(lock_group)



            # Session management
            session_group = QGroupBox("Session Management")
            session_layout = QHBoxLayout()
            
            btn_login = QPushButton("Login as Admin")
            btn_login.setMinimumSize(120, 30)
            btn_login.setEnabled(False)  # User is already logged in to reach this dialog
            btn_logout = QPushButton("Logout")
            btn_logout.setMinimumSize(120, 30)
            btn_logout.setEnabled(True)  # User is already logged in to reach this dialog
            
            session_layout.addWidget(btn_login)
            session_layout.addWidget(btn_logout)
            session_layout.addStretch(1)
            
            session_status = QLabel("Logged In")  # User is already logged in to reach this dialog
            session_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
            session_layout.addWidget(session_status)
            
            session_group.setLayout(session_layout)
            v.addWidget(session_group)

            def load_current_settings():
                """Load current admin settings"""
                # Load locked areas
                self.cb_lock_spares.setChecked("spares" in self.locked_areas)
                self.cb_lock_spares_add.setChecked("spares_add" in self.locked_areas)
                self.cb_lock_spares_delete_selected.setChecked("spares_delete_selected" in self.locked_areas)
                self.cb_lock_spares_delete_all.setChecked("spares_delete_all" in self.locked_areas)
                self.cb_lock_spares_reset_quantity.setChecked("spares_reset_quantity" in self.locked_areas)
                self.cb_lock_edit_amount.setChecked("edit_amount" in self.locked_areas)
                self.cb_lock_used.setChecked("used" in self.locked_areas)
                self.cb_lock_issued.setChecked("issued" in self.locked_areas)
                self.cb_lock_stocktake.setChecked("stocktake" in self.locked_areas)
                self.cb_lock_import.setChecked("import" in self.locked_areas)
                self.cb_lock_data_comparison.setChecked("data_comparison" in self.locked_areas)
                self.cb_lock_models.setChecked("models" in self.locked_areas)

                self.cb_lock_export.setChecked("export" in self.locked_areas)
                self.cb_lock_admin_panel.setChecked("admin_panel" in self.locked_areas)
                self.cb_lock_ocr_corrections.setChecked("ocr_corrections" in self.locked_areas)
                self.cb_lock_camera_controls.setChecked("camera_controls" in self.locked_areas)
                self.cb_lock_data_sync.setChecked("data_sync" in self.locked_areas)
                self.cb_lock_backup_restore.setChecked("backup_restore" in self.locked_areas)
                
                # Custom areas removed - no longer needed

            def on_set_password():
                """Set or change admin password"""
                try:
                    password = password_edit.text().strip()
                    confirm = confirm_edit.text().strip()
                    
                    if not password:
                        self.append_log("Password cannot be empty")
                        return
                    
                    if password != confirm:
                        self.append_log("Passwords do not match")
                        return
                    
                    if len(password) < 4:
                        self.append_log("Password must be at least 4 characters")
                        return
                    
                    # Hash the password using MD5 for consistency across sessions
                    self.admin_password = hashlib.md5(password.encode()).hexdigest()
                    self.admin_enabled = True
                    
                    # Save to file
                    self._save_admin_settings()
                    
                    self.append_log("Admin password set successfully")
                    status_value.setText("Set")
                    status_value.setStyleSheet("color: #4CAF50; font-weight: bold;")
                    password_edit.clear()
                    confirm_edit.clear()
                    
                except Exception as e:
                    self.append_log(f"Failed to set password: {e}")

            def on_reset_password():
                """Reset admin password"""
                try:
                    resp = QMessageBox.question(dlg, "Reset Password", 
                                              "This will disable admin protection. Continue?", 
                                              QMessageBox.Yes | QMessageBox.No)
                    if resp != QMessageBox.Yes:
                        return
                    
                    self.admin_password = None
                    self.admin_enabled = False
                    self.admin_session_active = False
                    self.locked_areas.clear()
                    
                    # Save to file
                    self._save_admin_settings()
                    
                    self.append_log("Admin password reset - protection disabled")
                    status_value.setText("Not Set")
                    status_value.setStyleSheet("color: #FF5722; font-weight: bold;")
                    session_status.setText("Not Logged In")
                    session_status.setStyleSheet("color: #FF5722; font-weight: bold;")
                    btn_logout.setEnabled(False)
                    
                    # Clear all checkboxes
                    for cb in [self.cb_lock_spares, self.cb_lock_used, self.cb_lock_issued, 
                              self.cb_lock_stocktake, self.cb_lock_import, self.cb_lock_data_comparison, self.cb_lock_models]:
                        cb.setChecked(False)
                    
                except Exception as e:
                    self.append_log(f"Failed to reset password: {e}")

            def on_login():
                """Login as admin"""
                try:
                    if not self.admin_enabled:
                        self.append_log("Admin protection not enabled")
                        return
                    
                    password, ok = QInputDialog.getText(dlg, "Admin Login", "Enter admin password:", QLineEdit.Password)
                    if not ok:
                        return
                    
                    if hashlib.md5(password.encode()).hexdigest() == self.admin_password:
                        self.admin_session_active = True
                        self._start_session_timer()  # Start session timeout
                        self.append_log("Admin login successful")
                        session_status.setText("Logged In")
                        session_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
                        btn_logout.setEnabled(True)
                    else:
                        # Invalid password - ensure session is invalidated and log attempt
                        self.admin_session_active = False
                        self._save_admin_settings()  # Persist security state immediately
                        self.append_log("Invalid admin password attempt - access denied")
                        QMessageBox.warning(dlg, "Access Denied", "Invalid password. Access to restricted areas is denied.")
                        session_status.setText("Not Logged In")
                        session_status.setStyleSheet("color: #FF5722; font-weight: bold;")
                        btn_logout.setEnabled(False)
                        
                except Exception as e:
                    self.append_log(f"Login failed: {e}")

            def on_logout():
                """Logout from admin session"""
                try:
                    self.admin_session_active = False
                    self.admin_last_activity = None
                    if self.session_timer:
                        self.session_timer.stop()
                        self.session_timer = None
                    self.append_log("Admin logout successful")
                    session_status.setText("Not Logged In")
                    session_status.setStyleSheet("color: #FF5722; font-weight: bold;")
                    btn_logout.setEnabled(False)
                except Exception as e:
                    self.append_log(f"Logout failed: {e}")



            def _apply_lock_checkboxes():
                """Apply checkbox states to locked_areas and persist immediately"""
                try:
                    self.locked_areas.clear()
                    if self.cb_lock_spares.isChecked():
                        self.locked_areas.add("spares")
                    if self.cb_lock_spares_add.isChecked():
                        self.locked_areas.add("spares_add")
                    if self.cb_lock_spares_delete_selected.isChecked():
                        self.locked_areas.add("spares_delete_selected")
                    if self.cb_lock_spares_delete_all.isChecked():
                        self.locked_areas.add("spares_delete_all")
                    if self.cb_lock_spares_reset_quantity.isChecked():
                        self.locked_areas.add("spares_reset_quantity")
                    if self.cb_lock_edit_amount.isChecked():
                        self.locked_areas.add("edit_amount")
                    if self.cb_lock_used.isChecked():
                        self.locked_areas.add("used")
                    if self.cb_lock_issued.isChecked():
                        self.locked_areas.add("issued")
                    if self.cb_lock_stocktake.isChecked():
                        self.locked_areas.add("stocktake")
                    if self.cb_lock_import.isChecked():
                        self.locked_areas.add("import")
                    if self.cb_lock_data_comparison.isChecked():
                        self.locked_areas.add("data_comparison")
                    if self.cb_lock_models.isChecked():
                        self.locked_areas.add("models")

                    if self.cb_lock_export.isChecked():
                        self.locked_areas.add("export")
                    if self.cb_lock_admin_panel.isChecked():
                        self.locked_areas.add("admin_panel")
                    if self.cb_lock_ocr_corrections.isChecked():
                        self.locked_areas.add("ocr_corrections")
                    if self.cb_lock_camera_controls.isChecked():
                        self.locked_areas.add("camera_controls")
                    if self.cb_lock_data_sync.isChecked():
                        self.locked_areas.add("data_sync")
                    if self.cb_lock_backup_restore.isChecked():
                        self.locked_areas.add("backup_restore")
                    # Persist
                    self._save_admin_settings()
                except Exception as e:
                    self.append_log(f"Failed to apply lock checkboxes: {e}")

            def on_save_settings():
                """Save area lock settings"""
                try:
                    # User is already logged in to reach this dialog
                    
                    _apply_lock_checkboxes()
                    
                    self.append_log("Area lock settings saved")
                    
                except Exception as e:
                    self.append_log(f"Failed to save settings: {e}")

            # Connect signals
            btn_set_password.clicked.connect(on_set_password)
            btn_reset_password.clicked.connect(on_reset_password)
            btn_login.clicked.connect(on_login)
            btn_logout.clicked.connect(on_logout)

            # Auto-apply lock changes immediately upon toggle
            for cb in [self.cb_lock_spares, self.cb_lock_edit_amount, self.cb_lock_used, self.cb_lock_issued,
                       self.cb_lock_stocktake, self.cb_lock_import, self.cb_lock_data_comparison, self.cb_lock_models]:
                cb.stateChanged.connect(lambda _state: _apply_lock_checkboxes())
            
            # Load current settings
            load_current_settings()

            # Buttons
            buttons_layout = QHBoxLayout()
            btn_save = QPushButton("Save Settings")
            btn_save.setMinimumSize(120, 30)
            btn_save.clicked.connect(on_save_settings)
            buttons_layout.addWidget(btn_save)
            buttons_layout.addStretch(1)
            
            btns = QDialogButtonBox(QDialogButtonBox.Close)
            btns.rejected.connect(dlg.reject)
            buttons_layout.addWidget(btns)
            v.addLayout(buttons_layout)
            
            dlg.setLayout(v)
            dlg.resize(500, 600)
            dlg.exec_()
            
        except Exception as e:
            self.append_log(f"Admin dialog failed: {e}")

    def _save_admin_settings(self):
        """Save admin settings to file"""
        try:
            if self.admin_session_active:
                self._update_session_activity()  # Track admin activity
            import json
            settings = {
                "admin_password": self.admin_password,
                "admin_enabled": self.admin_enabled,
                "locked_areas": list(self.locked_areas)
                # admin_session_active is not saved for security - sessions don't persist
            }
            
            with open("admin_settings.json", "w") as f:
                json.dump(settings, f, indent=2)
                
            self.append_log(f"Admin settings saved: enabled={self.admin_enabled}, password_set={bool(self.admin_password)}, locked_areas={len(self.locked_areas)}")
                
        except Exception as e:
            self.append_log(f"Failed to save admin settings: {e}")

    def _load_admin_settings(self):
        """Load admin settings from file"""
        try:
            import json
            import os
            
            if os.path.exists("admin_settings.json"):
                with open("admin_settings.json", "r") as f:
                    settings = json.load(f)
                    
                self.admin_password = str(settings.get("admin_password", ""))
                self.admin_enabled = settings.get("admin_enabled", False)
                self.locked_areas = set(settings.get("locked_areas", []))
                # Always start with session inactive for security
                self.admin_session_active = False
                
                self.append_log(f"Admin settings loaded: enabled={self.admin_enabled}, password_set={bool(self.admin_password)}, locked_areas={len(self.locked_areas)}")
            else:
                self.append_log("No admin_settings.json file found - using defaults")
                
        except Exception as e:
            self.append_log(f"Failed to load admin settings: {e}")

    def _start_session_timer(self):
        """Start or restart the session timeout timer"""
        try:
            import time
            self.admin_last_activity = time.time()
            
            # Stop existing timer if running
            if self.session_timer:
                self.session_timer.stop()
            
            # Create new timer that checks every 30 seconds
            self.session_timer = QTimer()
            self.session_timer.timeout.connect(self._check_session_timeout)
            self.session_timer.start(3000)  # Check every 30 seconds
            
        except Exception as e:
            self.append_log(f"Failed to start session timer: {e}")
    
    def _update_session_activity(self):
        """Update last activity timestamp"""
        try:
            import time
            if self.admin_session_active:
                self.admin_last_activity = time.time()
        except Exception as e:
            self.append_log(f"Failed to update session activity: {e}")
    
    def _check_session_timeout(self):
        """Check if admin session has timed out"""
        try:
            import time
            if not self.admin_session_active or not self.admin_last_activity:
                return
            
            current_time = time.time()
            elapsed = current_time - self.admin_last_activity
            
            if elapsed >= self.admin_session_timeout:
                self._force_logout("Session timed out after 15 minutes of inactivity")
                
        except Exception as e:
            self.append_log(f"Session timeout check failed: {e}")
    
    def _force_logout(self, reason="Session expired"):
        """Force logout and stop session timer"""
        try:
            self.admin_session_active = False
            self.admin_last_activity = None
            
            if self.session_timer:
                self.session_timer.stop()
                self.session_timer = None
            
            self.append_log(f"Admin auto-logout: {reason}")
            
            # Show warning to user
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Session Expired", 
                              f"Admin session has expired: {reason}\nPlease login again to access protected areas.")
                              
        except Exception as e:
            self.append_log(f"Force logout failed: {e}")

    def _check_area_access(self, area_name):
        """Check if user has access to a specific area"""
        try:
            if not self.admin_enabled:
                return True  # No admin protection enabled
            
            if area_name not in self.locked_areas:
                return True  # Area not locked
            
            if self.admin_session_active:
                self._update_session_activity()  # Track admin activity
                return True  # Admin is logged in
            
            # Area is locked and user is not admin
            QMessageBox.warning(self, "Access Denied", 
                              f"This area is locked. Please login as admin to access {area_name.replace('_', ' ').title()}.")
            return False
            
        except Exception as e:
            self.append_log(f"Access check failed: {e}")
            return False

    def _check_edit_amount_access(self):
        """Check if user has access to edit amounts in view spares"""
        try:
            if not self.admin_enabled:
                return True  # No admin protection enabled
            
            if "edit_amount" not in self.locked_areas:
                return True  # Edit amount not locked
            
            if self.admin_session_active:
                return True  # Admin is logged in
            
            # Edit amount is locked and user is not admin
            QMessageBox.warning(self, "Access Denied", 
                              "Editing amounts is locked. Please login as admin to edit quantities.")
            return False
            
        except Exception as e:
            self.append_log(f"Edit amount access check failed: {e}")
            return False

    # Custom area access check removed - functionality no longer needed


# ----------------------------
# Run app
# ----------------------------
def main():
    app = QApplication(sys.argv)
    
    # Apply stylesheet if available
    try:
        if os.path.exists('styles.css'):
            with open('styles.css', 'r') as f:
                stylesheet = f.read()
            app.setStyleSheet(stylesheet)
    except Exception as e:
        print(f"Could not load stylesheet: {e}")
    
    window = PartScannerApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
