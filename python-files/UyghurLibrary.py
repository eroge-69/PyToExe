#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Uyghur Digital Library Application - Fixed Version
ئۇيغۇرچە رەقەملىك كۈتۈپخانا دېتالى - تۈزىتىلگەن نۇسخا
"""

import sys
import os

# First, check if all required modules are available
missing_modules = []
required_modules = {
    'PyQt5': 'PyQt5',
    'PyPDF2': 'PyPDF2',
    'docx': 'python-docx',
    'chardet': 'chardet',
    'arabic_reshaper': 'arabic-reshaper',
    'bidi': 'python-bidi'
}

print("Checking required modules...")
for module, package in required_modules.items():
    try:
        __import__(module)
        print(f"✓ {module} - OK")
    except ImportError:
        print(f"✗ {module} - MISSING")
        missing_modules.append(package)

if missing_modules:
    print("\n⚠ Missing modules detected!")
    print("Please install them using:")
    print(f"pip install {' '.join(missing_modules)}")
    print("\nPress Enter to exit...")
    input()
    sys.exit(1)

# Now import all modules
import sqlite3
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re

# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog,
    QListWidget, QListWidgetItem, QSplitter, QComboBox,
    QMessageBox, QProgressBar, QTabWidget, QTreeWidget,
    QTreeWidgetItem, QMenu, QAction, QToolBar, QStatusBar,
    QDialog, QDialogButtonBox, QFormLayout, QSpinBox,
    QTextBrowser, QGroupBox, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt5.QtGui import QFont, QIcon, QTextCursor, QTextCharFormat, QColor

# Text processing imports - with error handling
try:
    import PyPDF2
except ImportError:
    print("Warning: PyPDF2 not installed - PDF support disabled")
    PyPDF2 = None

try:
    import docx
except ImportError:
    print("Warning: python-docx not installed - DOCX support disabled")
    docx = None

try:
    import chardet
except ImportError:
    print("Warning: chardet not installed - encoding detection disabled")
    chardet = None

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError:
    print("Warning: RTL text support disabled")
    arabic_reshaper = None
    get_display = None


class DatabaseManager:
    """Database management class"""

    def __init__(self, db_path: str = "library.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Books table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS books
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           title
                           TEXT
                           NOT
                           NULL,
                           author
                           TEXT,
                           language
                           TEXT,
                           category
                           TEXT,
                           file_path
                           TEXT,
                           content
                           TEXT,
                           add_date
                           TIMESTAMP,
                           last_read
                           TIMESTAMP,
                           file_hash
                           TEXT
                           UNIQUE,
                           metadata
                           TEXT
                       )
                       ''')

        # Search history
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS search_history
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           query
                           TEXT,
                           search_date
                           TIMESTAMP
                       )
                       ''')

        # Bookmarks
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS bookmarks
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           book_id
                           INTEGER,
                           page_number
                           INTEGER,
                           note
                           TEXT,
                           add_date
                           TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           book_id
                       ) REFERENCES books
                       (
                           id
                       )
                           )
                       ''')

        # Full-text search table
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS books_fts 
            USING fts5(title, author, content, content=books)
        ''')

        conn.commit()
        conn.close()

    def add_book(self, title: str, content: str, **kwargs) -> int:
        """Add a book"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Generate file hash to prevent duplicates
        file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

        try:
            cursor.execute('''
                           INSERT INTO books (title, author, language, category,
                                              file_path, content, add_date, file_hash, metadata)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                           ''', (
                               title,
                               kwargs.get('author', 'Unknown'),
                               kwargs.get('language', 'ug'),
                               kwargs.get('category', 'General'),
                               kwargs.get('file_path', ''),
                               content,
                               datetime.now(),
                               file_hash,
                               json.dumps(kwargs.get('metadata', {}))
                           ))

            book_id = cursor.lastrowid

            # Add to FTS table
            cursor.execute('''
                           INSERT INTO books_fts (rowid, title, author, content)
                           VALUES (?, ?, ?, ?)
                           ''', (book_id, title, kwargs.get('author', ''), content))

            conn.commit()
            return book_id

        except sqlite3.IntegrityError:
            conn.close()
            raise ValueError("This book already exists!")
        finally:
            conn.close()

    def search_books(self, query: str, search_type: str = 'all') -> List[Dict]:
        """Search books"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        results = []

        if search_type == 'title':
            cursor.execute('''
                           SELECT id, title, author, language, category
                           FROM books
                           WHERE title LIKE ?
                           ''', (f'%{query}%',))
        elif search_type == 'author':
            cursor.execute('''
                           SELECT id, title, author, language, category
                           FROM books
                           WHERE author LIKE ?
                           ''', (f'%{query}%',))
        elif search_type == 'content':
            cursor.execute('''
                           SELECT b.id,
                                  b.title,
                                  b.author,
                                  b.language,
                                  b.category,
                                  snippet(books_fts, 2, '<b>', '</b>', '...', 30) as snippet
                           FROM books b
                                    JOIN books_fts ON b.id = books_fts.rowid
                           WHERE books_fts MATCH ?
                           ''', (query,))
        else:  # all
            cursor.execute('''
                           SELECT b.id,
                                  b.title,
                                  b.author,
                                  b.language,
                                  b.category,
                                  snippet(books_fts, 2, '<b>', '</b>', '...', 30) as snippet
                           FROM books b
                                    JOIN books_fts ON b.id = books_fts.rowid
                           WHERE books_fts MATCH ?
                           ''', (query,))

        for row in cursor.fetchall():
            result = {
                'id': row[0],
                'title': row[1],
                'author': row[2],
                'language': row[3],
                'category': row[4]
            }
            if len(row) > 5:
                result['snippet'] = row[5]
            results.append(result)

        # Save search history
        cursor.execute('''
                       INSERT INTO search_history (query, search_date)
                       VALUES (?, ?)
                       ''', (query, datetime.now()))

        conn.commit()
        conn.close()

        return results

    def get_book_content(self, book_id: int) -> Optional[str]:
        """Get book content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT content FROM books WHERE id = ?', (book_id,))
        result = cursor.fetchone()

        # Update last read time
        cursor.execute('''
                       UPDATE books
                       SET last_read = ?
                       WHERE id = ?
                       ''', (datetime.now(), book_id))

        conn.commit()
        conn.close()

        return result[0] if result else None

    def get_all_books(self) -> List[Dict]:
        """Get all books"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT id, title, author, language, category, add_date
                       FROM books
                       ORDER BY add_date DESC
                       ''')

        books = []
        for row in cursor.fetchall():
            books.append({
                'id': row[0],
                'title': row[1],
                'author': row[2],
                'language': row[3],
                'category': row[4],
                'add_date': row[5]
            })

        conn.close()
        return books


class TextExtractor:
    """Document text extraction class"""

    @staticmethod
    def extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF"""
        if not PyPDF2:
            raise Exception("PyPDF2 not installed")

        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"PDF reading error: {str(e)}")
        return text

    @staticmethod
    def extract_from_docx(file_path: str) -> str:
        """Extract text from DOCX"""
        if not docx:
            raise Exception("python-docx not installed")

        try:
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            raise Exception(f"DOCX reading error: {str(e)}")
        return text

    @staticmethod
    def extract_from_txt(file_path: str) -> str:
        """Extract text from TXT"""
        try:
            # Detect encoding
            if chardet:
                with open(file_path, 'rb') as file:
                    raw_data = file.read()
                    result = chardet.detect(raw_data)
                    encoding = result['encoding'] or 'utf-8'
            else:
                encoding = 'utf-8'

            with open(file_path, 'r', encoding=encoding) as file:
                text = file.read()
        except Exception as e:
            raise Exception(f"TXT reading error: {str(e)}")
        return text

    @classmethod
    def extract_text(cls, file_path: str) -> str:
        """Extract text based on file type"""
        ext = Path(file_path).suffix.lower()

        if ext == '.pdf':
            return cls.extract_from_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return cls.extract_from_docx(file_path)
        elif ext in ['.txt', '.text']:
            return cls.extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")


class BookReaderWidget(QTextBrowser):
    """Book reading widget"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.current_book_id = None
        self.search_highlights = []

    def setup_ui(self):
        """Setup UI"""
        # RTL languages support
        self.setLayoutDirection(Qt.RightToLeft)

        # Font settings for multi-language support
        font = QFont()
        font.setFamily("Arial, Tahoma, 'Microsoft Uighur', 'UKIJ Tuz', 'Noto Sans Arabic'")
        font.setPointSize(12)
        self.setFont(font)

        # Enable text selection and copying
        self.setTextInteractionFlags(
            Qt.TextSelectableByMouse |
            Qt.TextSelectableByKeyboard |
            Qt.LinksAccessibleByMouse
        )

    def display_book(self, content: str, book_id: int):
        """Display book"""
        self.current_book_id = book_id
        self.clear()

        # Process RTL text if needed
        if self.is_rtl_text(content):
            content = self.process_rtl_text(content)

        self.setHtml(f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Arial', 'Tahoma', 'Microsoft Uighur', 
                                   'UKIJ Tuz', 'Noto Sans Arabic';
                        font-size: 14pt;
                        line-height: 1.8;
                        padding: 20px;
                    }}
                    p {{ margin: 10px 0; }}
                    .highlight {{ background-color: yellow; font-weight: bold; }}
                </style>
            </head>
            <body>
                {content}
            </body>
            </html>
        """)

    def is_rtl_text(self, text: str) -> bool:
        """Check for RTL text"""
        # Check for Arabic, Uyghur, Hebrew characters
        rtl_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u0590-\u05FF]')
        return bool(rtl_pattern.search(text[:100]))  # Check first 100 chars

    def process_rtl_text(self, text: str) -> str:
        """Process RTL text"""
        if arabic_reshaper and get_display:
            try:
                reshaped = arabic_reshaper.reshape(text)
                return get_display(reshaped)
            except:
                return text
        return text

    def highlight_search_results(self, query: str):
        """Highlight search results"""
        cursor = self.textCursor()
        format = QTextCharFormat()
        format.setBackground(QColor("yellow"))

        # Clear previous highlights
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())

        # Find and highlight all occurrences
        cursor.movePosition(QTextCursor.Start)
        while self.find(query):
            cursor = self.textCursor()
            cursor.mergeCharFormat(format)


class MainWindow(QMainWindow):
    """Main window"""

    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.text_extractor = TextExtractor()
        self.settings = QSettings("UyghurLibrary", "Settings")
        self.init_ui()
        self.load_books()

    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Uyghur Digital Library - ئۇيغۇرچە رەقەملىك كۈتۈپخانا")
        self.setGeometry(100, 100, 1400, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel (reader)
        self.book_reader = BookReaderWidget()
        splitter.addWidget(self.book_reader)

        # Set splitter sizes
        splitter.setSizes([400, 1000])

        # Menu bar
        self.create_menu_bar()

        # Tool bar
        self.create_tool_bar()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def create_left_panel(self) -> QWidget:
        """Create left panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Language selector
        lang_group = QGroupBox("Language / تىل تاللاش")
        lang_layout = QHBoxLayout()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["All", "Uyghur", "Arabic", "Turkish", "English"])
        self.lang_combo.currentTextChanged.connect(self.filter_books_by_language)
        lang_layout.addWidget(self.lang_combo)
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)

        # Search section
        search_group = QGroupBox("Search / ئىزدەش")
        search_layout = QVBoxLayout()

        # Search input
        search_input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search content...")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_books)
        search_input_layout.addWidget(self.search_input)
        search_input_layout.addWidget(self.search_button)
        search_layout.addLayout(search_input_layout)

        # Search options
        self.search_type = QComboBox()
        self.search_type.addItems([
            "All",
            "Title",
            "Author",
            "Content"
        ])
        search_layout.addWidget(self.search_type)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Category tree
        category_group = QGroupBox("Categories / تۈرلەر")
        category_layout = QVBoxLayout()

        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderLabel("Book Categories")
        self.init_categories()
        category_layout.addWidget(self.category_tree)

        category_group.setLayout(category_layout)
        layout.addWidget(category_group)

        # Book list
        books_group = QGroupBox("Books / كىتابلار")
        books_layout = QVBoxLayout()

        self.book_list = QListWidget()
        self.book_list.itemDoubleClicked.connect(self.open_book)
        books_layout.addWidget(self.book_list)

        # Book count label
        self.book_count_label = QLabel("Total books: 0")
        books_layout.addWidget(self.book_count_label)

        books_group.setLayout(books_layout)
        layout.addWidget(books_group)

        # Upload button
        self.upload_button = QPushButton("Add New Book")
        self.upload_button.clicked.connect(self.upload_book)
        layout.addWidget(self.upload_button)

        return widget

    def init_categories(self):
        """Initialize category tree"""
        categories = {
            "Religious": ["Quran", "Hadith", "Fiqh", "Aqidah"],
            "Literature": ["Poetry", "Novel", "Story", "Drama"],
            "History": ["Islamic History", "Uyghur History", "World History"],
            "Science": ["Mathematics", "Physics", "Chemistry", "Computer"],
            "Language": ["Uyghur", "Arabic", "Turkish", "English"]
        }

        for main_cat, sub_cats in categories.items():
            main_item = QTreeWidgetItem(self.category_tree, [main_cat])
            for sub_cat in sub_cats:
                QTreeWidgetItem(main_item, [sub_cat])

    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        upload_action = QAction("Add Book", self)
        upload_action.triggered.connect(self.upload_book)
        file_menu.addAction(upload_action)

        export_action = QAction("Export Book", self)
        export_action.triggered.connect(self.export_book)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        find_action = QAction("Find", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)

        # View menu
        view_menu = menubar.addMenu("View")

        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_tool_bar(self):
        """Create tool bar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Add book action
        add_book_action = QAction("Add Book", self)
        add_book_action.triggered.connect(self.upload_book)
        toolbar.addAction(add_book_action)

        toolbar.addSeparator()

        # Search action
        search_action = QAction("Search", self)
        search_action.triggered.connect(self.search_books)
        toolbar.addAction(search_action)

        toolbar.addSeparator()

        # Bookmark action
        bookmark_action = QAction("Bookmark", self)
        bookmark_action.triggered.connect(self.add_bookmark)
        toolbar.addAction(bookmark_action)

        toolbar.addSeparator()

        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(settings_action)

    def upload_book(self):
        """Upload book"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Book",
            "",
            "Book Files (*.pdf *.docx *.doc *.txt);;All Files (*.*)"
        )

        if file_path:
            try:
                # Extract text
                content = self.text_extractor.extract_text(file_path)

                # Get book info dialog
                dialog = BookInfoDialog(self)
                if dialog.exec_():
                    info = dialog.get_info()
                    info['file_path'] = file_path

                    # Add to database
                    book_id = self.db_manager.add_book(
                        info['title'],
                        content,
                        **info
                    )

                    # Refresh book list
                    self.load_books()

                    QMessageBox.information(
                        self,
                        "Success",
                        f"Book '{info['title']}' added successfully!"
                    )

            except ValueError as e:
                QMessageBox.warning(self, "Warning", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error uploading book: {str(e)}")

    def load_books(self):
        """Load books"""
        self.book_list.clear()
        books = self.db_manager.get_all_books()

        for book in books:
            item_text = f"{book['title']} - {book['author']} ({book['language']})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, book['id'])
            self.book_list.addItem(item)

        self.book_count_label.setText(f"Total books: {len(books)}")

    def open_book(self, item: QListWidgetItem):
        """Open book"""
        book_id = item.data(Qt.UserRole)
        content = self.db_manager.get_book_content(book_id)

        if content:
            self.book_reader.display_book(content, book_id)
            self.status_bar.showMessage(f"Book opened: {item.text()}")

    def search_books(self):
        """Search books"""
        query = self.search_input.text()
        if not query:
            return

        search_types = {
            "All": "all",
            "Title": "title",
            "Author": "author",
            "Content": "content"
        }

        search_type = search_types.get(self.search_type.currentText(), "all")
        results = self.db_manager.search_books(query, search_type)

        # Display results
        self.book_list.clear()
        for result in results:
            item_text = f"{result['title']} - {result['author']}"
            if 'snippet' in result:
                item_text += f"\n   ...{result['snippet']}..."

            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, result['id'])
            self.book_list.addItem(item)

        self.status_bar.showMessage(f"Found {len(results)} results for '{query}'")

        # Highlight in reader if book is open
        if self.book_reader.current_book_id:
            self.book_reader.highlight_search_results(query)

    def filter_books_by_language(self, language: str):
        """Filter books by language"""
        lang_map = {
            "Uyghur": "ug",
            "Arabic": "ar",
            "Turkish": "tr",
            "English": "en",
            "All": None
        }

        selected_lang = lang_map.get(language)

        self.book_list.clear()
        books = self.db_manager.get_all_books()

        for book in books:
            if selected_lang is None or book['language'] == selected_lang:
                item_text = f"{book['title']} - {book['author']} ({book['language']})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, book['id'])
                self.book_list.addItem(item)

    def export_book(self):
        """Export book"""
        if not self.book_reader.current_book_id:
            QMessageBox.warning(self, "Warning", "Please open a book first!")
            return

        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self,
            "Save Book",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )

        if file_path:
            content = self.book_reader.toPlainText()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            QMessageBox.information(self, "Success", "Book saved!")

    def show_find_dialog(self):
        """Show find dialog"""
        dialog = FindDialog(self)
        if dialog.exec_():
            text = dialog.get_search_text()
            if text and self.book_reader.current_book_id:
                self.book_reader.highlight_search_results(text)

    def zoom_in(self):
        """Zoom in"""
        font = self.book_reader.font()
        font.setPointSize(font.pointSize() + 2)
        self.book_reader.setFont(font)

    def zoom_out(self):
        """Zoom out"""
        font = self.book_reader.font()
        if font.pointSize() > 8:
            font.setPointSize(font.pointSize() - 2)
            self.book_reader.setFont(font)

    def add_bookmark(self):
        """Add bookmark"""
        if not self.book_reader.current_book_id:
            QMessageBox.warning(self, "Warning", "Please open a book first!")
            return

        # Implementation for bookmark
        QMessageBox.information(self, "Bookmark", "Bookmark added!")

    def show_settings(self):
        """Show settings"""
        dialog = SettingsDialog(self)
        dialog.exec_()

    def show_about(self):
        """Show about"""
        QMessageBox.about(
            self,
            "About",
            """<h2>Uyghur Digital Library</h2>
            <p>Version: 1.0.0</p>
            <p>A multi-language digital library system similar to Al-Maktaba al-Shamila.</p>
            <p>Supported Languages:</p>
            <ul>
                <li>Uyghur</li>
                <li>Arabic</li>
                <li>Turkish</li>
                <li>English</li>
            </ul>
            <p>© 2024 - All rights reserved</p>"""
        )


class BookInfoDialog(QDialog):
    """Book info dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Book Information")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        self.title_input = QLineEdit()
        layout.addRow("Title:", self.title_input)

        self.author_input = QLineEdit()
        layout.addRow("Author:", self.author_input)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["ug", "ar", "tr", "en"])
        layout.addRow("Language:", self.language_combo)

        self.category_input = QLineEdit()
        layout.addRow("Category:", self.category_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def get_info(self) -> Dict:
        return {
            'title': self.title_input.text() or "Untitled",
            'author': self.author_input.text() or "Unknown",
            'language': self.language_combo.currentText(),
            'category': self.category_input.text() or "General"
        }


class FindDialog(QDialog):
    """Find dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search text...")
        layout.addWidget(self.search_input)

        self.case_sensitive = QCheckBox("Case sensitive")
        layout.addWidget(self.case_sensitive)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_search_text(self) -> str:
        return self.search_input.text()


class SettingsDialog(QDialog):
    """Settings dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        # Font size
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(12)
        layout.addRow("Font Size:", self.font_size)

        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        layout.addRow("Theme:", self.theme_combo)

        # Default language
        self.default_lang = QComboBox()
        self.default_lang.addItems(["Uyghur", "Arabic", "Turkish", "English"])
        layout.addRow("Default Language:", self.default_lang)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)


def main():
    """Main function"""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # RTL support for Uyghur and Arabic
    app.setLayoutDirection(Qt.RightToLeft)

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()