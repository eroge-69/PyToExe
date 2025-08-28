import sys
import os
import shutil
import zipfile
import tarfile
import hashlib
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QSplitter, QTreeView, QListView, 
                             QFileSystemModel, QToolBar, QAction, QLineEdit, 
                             QStatusBar, QMessageBox, QMenu, QInputDialog,
                             QDialog, QLabel, QPushButton, QComboBox, QTabWidget,
                             QTextEdit, QToolButton, QStyle, QFileDialog, QDialogButtonBox,
                             QProgressBar, QGridLayout, QGroupBox, QHeaderView, QTableWidget,
                             QTableWidgetItem, QListWidget, QListWidgetItem, QCheckBox)
from PyQt5.QtCore import Qt, QDir, QModelIndex, QThread, pyqtSignal, QSettings, QSize
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QColor, QPalette

class FileOperationThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, operation, source, destination):
        super().__init__()
        self.operation = operation
        self.source = source
        self.destination = destination
        self.canceled = False

    def run(self):
        try:
            if self.operation == "copy":
                self.copy_files()
            elif self.operation == "move":
                self.move_files()
            elif self.operation == "delete":
                self.delete_files()
            elif self.operation == "zip":
                self.create_zip()
        except Exception as e:
            self.error.emit(str(e))

    def copy_files(self):
        total_files = sum(len(files) for _, _, files in os.walk(self.source))
        processed = 0
        
        if os.path.isdir(self.source):
            for root, dirs, files in os.walk(self.source):
                if self.canceled:
                    return
                    
                rel_path = os.path.relpath(root, self.source)
                dest_path = os.path.join(self.destination, rel_path)
                
                if not os.path.exists(dest_path):
                    os.makedirs(dest_path)
                
                for file in files:
                    if self.canceled:
                        return
                        
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dest_path, file)
                    
                    shutil.copy2(src_file, dst_file)
                    processed += 1
                    self.progress.emit(int(processed / total_files * 100))
        else:
            shutil.copy2(self.source, self.destination)
            self.progress.emit(100)
        
        self.finished.emit("Copy completed")

    def move_files(self):
        shutil.move(self.source, self.destination)
        self.progress.emit(100)
        self.finished.emit("Move completed")

    def delete_files(self):
        if os.path.isdir(self.source):
            shutil.rmtree(self.source)
        else:
            os.remove(self.source)
        self.progress.emit(100)
        self.finished.emit("Delete completed")

    def create_zip(self):
        with zipfile.ZipFile(self.destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.isdir(self.source):
                for root, dirs, files in os.walk(self.source):
                    for file in files:
                        if self.canceled:
                            return
                            
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.source)
                        zipf.write(file_path, arcname)
            else:
                zipf.write(self.source, os.path.basename(self.source))
        
        self.progress.emit(100)
        self.finished.emit("Zip creation completed")

    def cancel(self):
        self.canceled = True


class FilePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(2)
        
        # Хранилище данных для вкладок
        self.tab_data = {}
        
        # Path navigation
        self.path_layout = QHBoxLayout()
        self.parent_button = QToolButton()
        self.parent_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogToParent))
        self.parent_button.clicked.connect(self.navigate_to_parent)
        self.path_layout.addWidget(self.parent_button)
        
        self.home_button = QToolButton()
        self.home_button.setIcon(self.style().standardIcon(QStyle.SP_DirHomeIcon))
        self.home_button.clicked.connect(self.navigate_to_home)
        self.path_layout.addWidget(self.home_button)
        
        self.drive_combo = QComboBox()
        self.drive_combo.setMaximumWidth(100)
        self.drive_combo.currentTextChanged.connect(self.drive_changed)
        self.path_layout.addWidget(self.drive_combo)
        
        self.path_edit = QLineEdit()
        self.path_edit.returnPressed.connect(self.navigate_to_path)
        self.path_layout.addWidget(self.path_edit)
        
        self.refresh_button = QToolButton()
        self.refresh_button.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.refresh_button.clicked.connect(self.refresh)
        self.path_layout.addWidget(self.refresh_button)
        
        self.layout.addLayout(self.path_layout)
        
        # File view with tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        self.layout.addWidget(self.tabs)
        
        # Create initial tab
        self.create_new_tab()
        
        # Set initial directory to home
        home_path = os.path.expanduser("~")
        self.set_current_path(home_path)
        
        # Populate drive combo
        self.populate_drives()
    
    def create_new_tab(self):
        tab_widget = QWidget()
        tab_layout = QHBoxLayout(tab_widget)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Tree view for directory structure
        tree_view = QTreeView()
        tree_model = QFileSystemModel()
        tree_model.setRootPath("")
        tree_view.setModel(tree_model)
        tree_view.setRootIndex(tree_model.index(""))
        tree_view.hideColumn(1)  # Hide size column
        tree_view.hideColumn(2)  # Hide type column
        tree_view.hideColumn(3)  # Hide date modified column
        tree_view.clicked.connect(self.tree_view_clicked)
        tree_view.setHeaderHidden(True)
        tree_view.setAnimated(True)
        tree_view.setIndentation(15)
        
        # List view for files
        list_view = QListView()
        list_model = QFileSystemModel()
        list_model.setRootPath("")
        list_view.setModel(list_model)
        list_view.doubleClicked.connect(self.list_view_double_clicked)
        list_view.setViewMode(QListView.IconMode)
        list_view.setResizeMode(QListView.Adjust)
        list_view.setGridSize(QSize(100, 80))
        list_view.setUniformItemSizes(True)
        list_view.setSelectionMode(QListView.ExtendedSelection)
        list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        list_view.customContextMenuRequested.connect(self.show_context_menu)
        
        splitter.addWidget(tree_view)
        splitter.addWidget(list_view)
        splitter.setSizes([200, 600])
        
        tab_layout.addWidget(splitter)
        
        tab_index = self.tabs.addTab(tab_widget, "Home")
        
        # Store references to the views and models
        self.tab_data[tab_index] = {
            'tree_view': tree_view,
            'tree_model': tree_model,
            'list_view': list_view,
            'list_model': list_model,
            'splitter': splitter,
            'current_path': ""
        }
        
        self.tabs.setCurrentIndex(tab_index)
    
    def tab_changed(self, index):
        if index >= 0 and index in self.tab_data:
            current_path = self.tab_data[index]['current_path']
            self.path_edit.setText(current_path)
    
    def close_tab(self, index):
        if self.tabs.count() > 1:
            if index in self.tab_data:
                del self.tab_data[index]
            
            # Обновляем индексы оставшихся вкладок
            new_tab_data = {}
            for i in range(self.tabs.count()):
                if i != index:
                    if i > index:
                        new_tab_data[i-1] = self.tab_data[i]
                    else:
                        new_tab_data[i] = self.tab_data[i]
            
            self.tab_data = new_tab_data
            self.tabs.removeTab(index)
    
    def get_current_tab_data(self):
        current_index = self.tabs.currentIndex()
        if current_index in self.tab_data:
            return self.tab_data[current_index]
        return None
    
    def get_current_list_view(self):
        data = self.get_current_tab_data()
        return data['list_view'] if data else None
    
    def get_current_list_model(self):
        data = self.get_current_tab_data()
        return data['list_model'] if data else None
    
    def get_current_tree_view(self):
        data = self.get_current_tab_data()
        return data['tree_view'] if data else None
    
    def get_current_tree_model(self):
        data = self.get_current_tab_data()
        return data['tree_model'] if data else None
    
    def set_current_path(self, path):
        self.path_edit.setText(path)
        
        data = self.get_current_tab_data()
        if data:
            data['current_path'] = path
            
            data['list_view'].setRootIndex(data['list_model'].index(path))
            data['tree_view'].setExpanded(data['tree_model'].index(path), True)
            data['tree_view'].setCurrentIndex(data['tree_model'].index(path))
            
            # Update tab text
            tab_text = os.path.basename(path) if path != "/" else "Root"
            if len(tab_text) > 15:
                tab_text = tab_text[:12] + "..."
            self.tabs.setTabText(self.tabs.currentIndex(), tab_text)
    
    def get_current_path(self):
        return self.path_edit.text()
    
    def navigate_to_path(self):
        path = self.path_edit.text()
        if os.path.exists(path):
            self.set_current_path(path)
        else:
            QMessageBox.warning(self, "Error", "Path does not exist")
    
    def navigate_to_parent(self):
        current_path = self.get_current_path()
        parent_path = os.path.dirname(current_path)
        if os.path.exists(parent_path):
            self.set_current_path(parent_path)
    
    def navigate_to_home(self):
        home_path = os.path.expanduser("~")
        self.set_current_path(home_path)
    
    def tree_view_clicked(self, index):
        data = self.get_current_tab_data()
        if data:
            path = data['tree_model'].filePath(index)
            if os.path.isdir(path):
                self.set_current_path(path)
    
    def list_view_double_clicked(self, index):
        data = self.get_current_tab_data()
        if data:
            path = data['list_model'].filePath(index)
            if os.path.isdir(path):
                self.set_current_path(path)
            else:
                # Open file with default application
                try:
                    if os.name == 'nt':
                        os.startfile(path)
                    else:
                        os.system(f'xdg-open "{path}"')
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
    
    def get_selected_files(self):
        data = self.get_current_tab_data()
        if data:
            selected = data['list_view'].selectedIndexes()
            return [data['list_model'].filePath(index) for index in selected]
        return []
    
    def refresh(self):
        current_path = self.get_current_path()
        data = self.get_current_tab_data()
        if data:
            data['list_model'].setRootPath("")  # Reset model
            self.set_current_path(current_path)  # Refresh view
    
    def populate_drives(self):
        self.drive_combo.clear()
        if os.name == 'nt':  # Windows
            import string
            from ctypes import windll
            drives = []
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drives.append(f"{letter}:\\")
                bitmask >>= 1
            self.drive_combo.addItems(drives)
        else:  # Linux/Mac
            self.drive_combo.addItem("/")
            home = os.path.expanduser("~")
            self.drive_combo.addItem(home)
    
    def drive_changed(self, drive):
        if os.path.exists(drive):
            self.set_current_path(drive)
    
    def show_context_menu(self, pos):
        menu = QMenu()
        
        open_action = menu.addAction("Open")
        open_action.triggered.connect(self.open_selected)
        
        menu.addSeparator()
        
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(lambda: self.parent.copy_files())
        
        move_action = menu.addAction("Move")
        move_action.triggered.connect(lambda: self.parent.move_files())
        
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self.parent.delete_files())
        
        menu.addSeparator()
        
        rename_action = menu.addAction("Rename")
        rename_action.triggered.connect(self.rename_file)
        
        properties_action = menu.addAction("Properties")
        properties_action.triggered.connect(self.show_properties)
        
        data = self.get_current_tab_data()
        if data:
            menu.exec_(data['list_view'].mapToGlobal(pos))
    
    def open_selected(self):
        selected_files = self.get_selected_files()
        if selected_files:
            for file_path in selected_files:
                if os.path.isdir(file_path):
                    self.set_current_path(file_path)
                else:
                    try:
                        if os.name == 'nt':
                            os.startfile(file_path)
                        else:
                            os.system(f'xdg-open "{file_path}"')
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
    
    def rename_file(self):
        selected_files = self.get_selected_files()
        if len(selected_files) != 1:
            QMessageBox.warning(self, "Warning", "Please select exactly one file to rename")
            return
        
        old_path = selected_files[0]
        new_name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", text=os.path.basename(old_path))
        
        if ok and new_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            try:
                os.rename(old_path, new_path)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to rename: {str(e)}")
    
    def show_properties(self):
        selected_files = self.get_selected_files()
        if not selected_files:
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Properties")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        
        if len(selected_files) == 1:
            file_path = selected_files[0]
            info = self.get_file_info(file_path)
            
            text_edit = QTextEdit()
            text_edit.setPlainText(info)
            text_edit.setReadOnly(True)
            layout.addWidget(text_edit)
        else:
            label = QLabel(f"Selected {len(selected_files)} items")
            layout.addWidget(label)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        dialog.exec_()
    
    def get_file_info(self, file_path):
        try:
            stat = os.stat(file_path)
            info = f"Name: {os.path.basename(file_path)}\n"
            info += f"Path: {file_path}\n"
            info += f"Size: {self.format_size(stat.st_size)}\n"
            info += f"Created: {datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}\n"
            info += f"Modified: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n"
            info += f"Accessed: {datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if os.path.isdir(file_path):
                info += "Type: Directory\n"
                try:
                    num_files = sum(len(files) for _, _, files in os.walk(file_path))
                    info += f"Contains: {num_files} files\n"
                except:
                    info += "Contains: Unable to calculate\n"
            else:
                info += f"Type: {os.path.splitext(file_path)[1]} file\n"
            
            return info
        except Exception as e:
            return f"Error getting file info: {str(e)}"
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"


class ProgressDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 150)
        
        layout = QVBoxLayout(self)
        
        self.label = QLabel("Processing...")
        layout.addWidget(self.label)
        
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel)
        layout.addWidget(self.cancel_button)
        
        self.thread = None
    
    def set_thread(self, thread):
        self.thread = thread
        thread.progress.connect(self.progress_bar.setValue)
        thread.finished.connect(self.accept)
        thread.error.connect(self.show_error)
    
    def cancel(self):
        if self.thread:
            self.thread.cancel()
        self.reject()
    
    def show_error(self, error_msg):
        QMessageBox.critical(self, "Error", error_msg)
        self.reject()


class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search Files")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Search criteria
        criteria_group = QGroupBox("Search Criteria")
        criteria_layout = QGridLayout(criteria_group)
        
        criteria_layout.addWidget(QLabel("Name:"), 0, 0)
        self.name_edit = QLineEdit()
        criteria_layout.addWidget(self.name_edit, 0, 1)
        
        criteria_layout.addWidget(QLabel("Containing text:"), 1, 0)
        self.text_edit = QLineEdit()
        criteria_layout.addWidget(self.text_edit, 1, 1)
        
        criteria_layout.addWidget(QLabel("Search in:"), 2, 0)
        self.path_edit = QLineEdit()
        self.path_edit.setText(os.path.expanduser("~"))
        criteria_layout.addWidget(self.path_edit, 2, 1)
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_path)
        criteria_layout.addWidget(self.browse_button, 2, 2)
        
        self.case_sensitive = QCheckBox("Case sensitive")
        criteria_layout.addWidget(self.case_sensitive, 3, 0, 1, 2)
        
        layout.addWidget(criteria_group)
        
        # Results
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_list = QListWidget()
        results_layout.addWidget(self.results_list)
        
        layout.addWidget(results_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.start_search)
        button_layout.addWidget(self.search_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        self.search_thread = None
        self.stop_search = False
    
    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory", self.path_edit.text())
        if path:
            self.path_edit.setText(path)
    
    def start_search(self):
        self.results_list.clear()
        self.search_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.stop_search = False
        
        name = self.name_edit.text()
        text = self.text_edit.text()
        path = self.path_edit.text()
        case_sensitive = self.case_sensitive.isChecked()
        
        if not name and not text:
            QMessageBox.warning(self, "Warning", "Please specify at least one search criteria")
            self.search_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            return
        
        self.search_thread = SearchThread(name, text, path, case_sensitive)
        self.search_thread.result_found.connect(self.add_result)
        self.search_thread.finished.connect(self.search_finished)
        self.stop_button.clicked.connect(self.search_thread.stop)
        self.search_thread.start()
    
    def add_result(self, file_path):
        item = QListWidgetItem(file_path)
        self.results_list.addItem(item)
    
    def search_finished(self):
        self.search_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if self.results_list.count() == 0:
            QMessageBox.information(self, "Search Complete", "No files found matching your criteria")
        else:
            QMessageBox.information(self, "Search Complete", f"Found {self.results_list.count()} files")


class SearchThread(QThread):
    result_found = pyqtSignal(str)
    
    def __init__(self, name, text, path, case_sensitive):
        super().__init__()
        self.name = name
        self.text = text
        self.path = path
        self.case_sensitive = case_sensitive
        self.stop_flag = False
    
    def run(self):
        if not os.path.exists(self.path):
            return
        
        for root, dirs, files in os.walk(self.path):
            if self.stop_flag:
                return
                
            for file in files:
                if self.stop_flag:
                    return
                
                file_path = os.path.join(root, file)
                
                # Check name pattern
                name_match = True
                if self.name:
                    if self.case_sensitive:
                        name_match = self.name in file
                    else:
                        name_match = self.name.lower() in file.lower()
                
                # Check text content
                text_match = True
                if self.text and name_match:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        if self.case_sensitive:
                            text_match = self.text in content
                        else:
                            text_match = self.text.lower() in content.lower()
                    except:
                        text_match = False
                
                if name_match and text_match:
                    self.result_found.emit(file_path)
    
    def stop(self):
        self.stop_flag = True


class Mexplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("Mexplorer", "Mexplorer")
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Mexplorer - Advanced File Manager')
        self.setGeometry(100, 100, 1400, 800)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        
        # Create two file panels
        self.left_panel = FilePanel(self)
        self.right_panel = FilePanel(self)
        
        # Add panels to main layout with splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.right_panel)
        splitter.setSizes([700, 700])
        main_layout.addWidget(splitter)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Set initial directories
        home_path = os.path.expanduser("~")
        self.left_panel.set_current_path(home_path)
        self.right_panel.set_current_path(home_path)
        
        # Load saved settings
        self.load_settings()
        
    def create_toolbar(self):
        # Main toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        
        # Navigation toolbar
        self.nav_toolbar = QToolBar("Navigation Toolbar")
        self.addToolBar(self.nav_toolbar)
        
        # Add actions to toolbars
        self.create_actions()
        
    def create_actions(self):
        # New tab action
        new_tab_action = QAction(QIcon.fromTheme('tab-new'), 'New Tab', self)
        new_tab_action.setShortcut('Ctrl+T')
        new_tab_action.triggered.connect(self.new_tab)
        self.toolbar.addAction(new_tab_action)
        
        # Refresh action
        refresh_action = QAction(QIcon.fromTheme('view-refresh'), 'Refresh', self)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.triggered.connect(self.refresh_all)
        self.toolbar.addAction(refresh_action)
        
        self.toolbar.addSeparator()
        
        # Copy action
        copy_action = QAction(QIcon.fromTheme('edit-copy'), 'Copy', self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy_files)
        self.toolbar.addAction(copy_action)
        
        # Move action
        move_action = QAction(QIcon.fromTheme('go-jump'), 'Move', self)
        move_action.setShortcut('F6')
        move_action.triggered.connect(self.move_files)
        self.toolbar.addAction(move_action)
        
        # Delete action
        delete_action = QAction(QIcon.fromTheme('edit-delete'), 'Delete', self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.delete_files)
        self.toolbar.addAction(delete_action)
        
        self.toolbar.addSeparator()
        
        # New directory action
        new_dir_action = QAction(QIcon.fromTheme('folder-new'), 'New Directory', self)
        new_dir_action.setShortcut('F7')
        new_dir_action.triggered.connect(self.create_new_directory)
        self.toolbar.addAction(new_dir_action)
        
        # View action
        view_action = QAction(QIcon.fromTheme('document-open'), 'View', self)
        view_action.setShortcut('F3')
        view_action.triggered.connect(self.view_file)
        self.toolbar.addAction(view_action)
        
        # Edit action
        edit_action = QAction(QIcon.fromTheme('accessories-text-editor'), 'Edit', self)
        edit_action.setShortcut('F4')
        edit_action.triggered.connect(self.edit_file)
        self.toolbar.addAction(edit_action)
        
        self.toolbar.addSeparator()
        
        # Zip action
        zip_action = QAction(QIcon.fromTheme('package-x-generic'), 'Zip', self)
        zip_action.setShortcut('Ctrl+Z')
        zip_action.triggered.connect(self.zip_files)
        self.toolbar.addAction(zip_action)
        
        # Unzip action
        unzip_action = QAction(QIcon.fromTheme('package-open'), 'Unzip', self)
        unzip_action.setShortcut('Ctrl+Shift+Z')
        unzip_action.triggered.connect(self.unzip_files)
        self.toolbar.addAction(unzip_action)
        
        self.toolbar.addSeparator()
        
        # Search action
        search_action = QAction(QIcon.fromTheme('edit-find'), 'Search', self)
        search_action.setShortcut('Ctrl+F')
        search_action.triggered.connect(self.search_files)
        self.toolbar.addAction(search_action)
        
        # Properties action
        properties_action = QAction(QIcon.fromTheme('document-properties'), 'Properties', self)
        properties_action.setShortcut('Alt+Enter')
        properties_action.triggered.connect(self.show_properties)
        self.toolbar.addAction(properties_action)
        
        self.toolbar.addSeparator()
        
        # Exit action
        exit_action = QAction(QIcon.fromTheme('application-exit'), 'Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        self.toolbar.addAction(exit_action)
        
    def apply_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        self.setPalette(dark_palette)
        self.setStyleSheet("""
            QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }
            QMenuBar::item:selected { background-color: #2a82da; }
            QTabWidget::pane { border: 1px solid #444; }
            QTabBar::tab { background: #353535; color: white; padding: 5px; }
            QTabBar::tab:selected { background: #2a82da; }
            QTreeView, QListView { 
                background-color: #252525; 
                alternate-background-color: #353535;
                color: white;
                outline: 0;
            }
            QTreeView::item:selected, QListView::item:selected {
                background-color: #2a82da;
                color: black;
            }
            QHeaderView::section {
                background-color: #353535;
                color: white;
                border: 1px solid #444;
                padding: 5px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #444;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
    
    def get_active_panel(self):
        # Determine which panel is active based on focus
        left_list_view = self.left_panel.get_current_list_view()
        right_list_view = self.right_panel.get_current_list_view()
        
        if left_list_view and (left_list_view.hasFocus() or 
            self.left_panel.path_edit.hasFocus()):
            return self.left_panel
        elif right_list_view and (right_list_view.hasFocus() or 
              self.right_panel.path_edit.hasFocus()):
            return self.right_panel
        else:
            return self.left_panel  # Default to left panel
    
    def get_inactive_panel(self):
        # Get the panel that is not active
        active = self.get_active_panel()
        return self.right_panel if active == self.left_panel else self.left_panel
    
    def new_tab(self):
        active_panel = self.get_active_panel()
        active_panel.create_new_tab()
        active_panel.set_current_path(active_panel.get_current_path())
    
    def refresh_all(self):
        self.left_panel.refresh()
        self.right_panel.refresh()
        self.status_bar.showMessage("Refreshed", 2000)
    
    def copy_files(self):
        active_panel = self.get_active_panel()
        inactive_panel = self.get_inactive_panel()
        
        selected_files = active_panel.get_selected_files()
        if not selected_files:
            QMessageBox.information(self, "Info", "No files selected")
            return
        
        dest_dir = inactive_panel.get_current_path()
        
        # Show progress dialog
        progress_dialog = ProgressDialog("Copying Files", self)
        thread = FileOperationThread("copy", selected_files[0] if len(selected_files) == 1 else selected_files, dest_dir)
        progress_dialog.set_thread(thread)
        
        thread.start()
        if progress_dialog.exec_() == QDialog.Accepted:
            self.status_bar.showMessage(f"Copied {len(selected_files)} item(s) to {dest_dir}", 3000)
            inactive_panel.refresh()
    
    def move_files(self):
        active_panel = self.get_active_panel()
        inactive_panel = self.get_inactive_panel()
        
        selected_files = active_panel.get_selected_files()
        if not selected_files:
            QMessageBox.information(self, "Info", "No files selected")
            return
        
        dest_dir = inactive_panel.get_current_path()
        
        # Show progress dialog
        progress_dialog = ProgressDialog("Moving Files", self)
        thread = FileOperationThread("move", selected_files[0] if len(selected_files) == 1 else selected_files, dest_dir)
        progress_dialog.set_thread(thread)
        
        thread.start()
        if progress_dialog.exec_() == QDialog.Accepted:
            self.status_bar.showMessage(f"Moved {len(selected_files)} item(s) to {dest_dir}", 3000)
            active_panel.refresh()
            inactive_panel.refresh()
    
    def delete_files(self):
        active_panel = self.get_active_panel()
        
        selected_files = active_panel.get_selected_files()
        if not selected_files:
            QMessageBox.information(self, "Info", "No files selected")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                    f"Are you sure you want to delete {len(selected_files)} item(s)?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Show progress dialog
            progress_dialog = ProgressDialog("Deleting Files", self)
            thread = FileOperationThread("delete", selected_files[0] if len(selected_files) == 1 else selected_files, "")
            progress_dialog.set_thread(thread)
            
            thread.start()
            if progress_dialog.exec_() == QDialog.Accepted:
                self.status_bar.showMessage(f"Deleted {len(selected_files)} item(s)", 3000)
                active_panel.refresh()
    
    def create_new_directory(self):
        active_panel = self.get_active_panel()
        current_path = active_panel.get_current_path()
        
        name, ok = QInputDialog.getText(self, "New Directory", "Enter directory name:")
        if ok and name:
            new_dir_path = os.path.join(current_path, name)
            try:
                os.makedirs(new_dir_path, exist_ok=True)
                self.status_bar.showMessage(f"Created directory: {name}", 2000)
                active_panel.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create directory: {str(e)}")
    
    def view_file(self):
        active_panel = self.get_active_panel()
        selected_files = active_panel.get_selected_files()
        
        if not selected_files:
            QMessageBox.information(self, "Info", "No file selected")
            return
        
        if len(selected_files) > 1:
            QMessageBox.information(self, "Info", "Please select only one file to view")
            return
        
        file_path = selected_files[0]
        if os.path.isdir(file_path):
            QMessageBox.information(self, "Info", "Please select a file, not a directory")
            return
        
        # Enhanced text file viewer dialog
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Viewer - {os.path.basename(file_path)}")
            dialog.setGeometry(200, 200, 800, 600)
            
            layout = QVBoxLayout(dialog)
            
            # Add file info
            info_label = QLabel(f"File: {file_path} | Size: {active_panel.format_size(os.path.getsize(file_path))}")
            layout.addWidget(info_label)
            
            # Text editor for viewing
            text_edit = QTextEdit()
            text_edit.setPlainText(content)
            text_edit.setReadOnly(True)
            text_edit.setFont(QFont("Courier New", 10))
            layout.addWidget(text_edit)
            
            button_box = QDialogButtonBox(QDialogButtonBox.Close)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
    
    def edit_file(self):
        active_panel = self.get_active_panel()
        selected_files = active_panel.get_selected_files()
        
        if not selected_files:
            QMessageBox.information(self, "Info", "No file selected")
            return
        
        if len(selected_files) > 1:
            QMessageBox.information(self, "Info", "Please select only one file to edit")
            return
        
        file_path = selected_files[0]
        if os.path.isdir(file_path):
            QMessageBox.information(self, "Info", "Please select a file, not a directory")
            return
        
        # Open file with default text editor
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            else:  # Linux/Mac
                os.system(f'xdg-open "{file_path}"')
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
    
    def zip_files(self):
        active_panel = self.get_active_panel()
        
        selected_files = active_panel.get_selected_files()
        if not selected_files:
            QMessageBox.information(self, "Info", "No files selected")
            return
        
        zip_path, _ = QFileDialog.getSaveFileName(self, "Save ZIP Archive", 
                                                 os.path.join(active_panel.get_current_path(), "archive.zip"), 
                                                 "ZIP Files (*.zip)")
        if not zip_path:
            return
        
        # Show progress dialog
        progress_dialog = ProgressDialog("Creating ZIP Archive", self)
        thread = FileOperationThread("zip", selected_files[0] if len(selected_files) == 1 else selected_files, zip_path)
        progress_dialog.set_thread(thread)
        
        thread.start()
        if progress_dialog.exec_() == QDialog.Accepted:
            self.status_bar.showMessage(f"Created ZIP archive: {os.path.basename(zip_path)}", 3000)
    
    def unzip_files(self):
        active_panel = self.get_active_panel()
        
        selected_files = active_panel.get_selected_files()
        if not selected_files:
            QMessageBox.information(self, "Info", "No archive selected")
            return
        
        if len(selected_files) > 1:
            QMessageBox.information(self, "Info", "Please select only one archive to extract")
            return
        
        archive_path = selected_files[0]
        if not (archive_path.endswith('.zip') or archive_path.endswith('.tar') or 
                archive_path.endswith('.gz') or archive_path.endswith('.bz2')):
            QMessageBox.warning(self, "Warning", "Selected file is not a supported archive format")
            return
        
        extract_path = QFileDialog.getExistingDirectory(self, "Select Extraction Directory", 
                                                       active_panel.get_current_path())
        if not extract_path:
            return
        
        try:
            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
            else:
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_path)
            
            self.status_bar.showMessage(f"Extracted archive to: {extract_path}", 3000)
            active_panel.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to extract archive: {str(e)}")
    
    def search_files(self):
        dialog = SearchDialog(self)
        dialog.exec_()
    
    def show_properties(self):
        active_panel = self.get_active_panel()
        active_panel.show_properties()
    
    def load_settings(self):
        # Load window geometry
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Load panel paths
        left_path = self.settings.value("left_panel_path")
        right_path = self.settings.value("right_panel_path")
        
        if left_path and os.path.exists(left_path):
            self.left_panel.set_current_path(left_path)
        
        if right_path and os.path.exists(right_path):
            self.right_panel.set_current_path(right_path)
    
    def save_settings(self):
        # Save window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        
        # Save panel paths
        self.settings.setValue("left_panel_path", self.left_panel.get_current_path())
        self.settings.setValue("right_panel_path", self.right_panel.get_current_path())
    
    def closeEvent(self, event):
        self.save_settings()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Mexplorer")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Mexplorer")
    
    window = Mexplorer()
    window.show()
    sys.exit(app.exec_())