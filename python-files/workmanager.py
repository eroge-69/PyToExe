import sys
import json
import os
import subprocess
import webbrowser
from pathlib import Path
import platform
import time
from datetime import datetime, timedelta
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTreeWidget, QTreeWidgetItem, QListWidget, QPushButton, 
                            QLabel, QTabWidget, QFileDialog, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class ModernJobManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Job Manager Pro")
        self.setGeometry(100, 100, 1400, 900)
        
        # Data storage
        self.data_file = "job_manager_data.json"
        self.jobs_data = self.load_data()
        
        # Time tracking
        self.active_job = None
        self.start_time = None
        self.timer_thread = None
        self.is_timing = False
        self.current_session_time = 0
        
        # Setup UI
        self.setup_ui()
        
        # Load existing data into tree
        self.populate_tree()
        
        # Update statistics initially
        self.update_time_statistics()
        
        # Start timer for UI updates
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update_ui)
        self.ui_timer.start(1000)  # Update every second

    def setup_ui(self):
        """Setup the PyQt6 UI with modern styling and larger text"""
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)
        
        # Apply dark theme stylesheet with increased font sizes
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117;
            }
            QTabWidget::pane {
                border: 1px solid #30363d;
                background: #161b22;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #21262d;
                color: #8b949e;
                padding: 14px 28px;
                border: 2px solid #30363d;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 140px;
                max-width: 140px;
                font: bold 13px "Segoe UI";
            }
            QTabBar::tab:selected {
                background: #2a2e37;
                color: #f0f6fc;
                border-bottom: 2px solid #58a6ff;
            }
            QTabBar::tab:hover:!selected {
                background: #79c0ff;
                color: #f0f6fc;
            }
            QPushButton {
                background-color: #21262d;
                color: #f0f6fc;
                border: 1px solid #30363d;
                padding: 10px 18px;
                border-radius: 6px;
                font: 11px "Segoe UI";
            }
            QPushButton:hover {
                background-color: #58a6ff;
                border-color: #79c0ff;
            }
            QPushButton:pressed {
                background-color: #79c0ff;
            }
            QTreeWidget, QListWidget {
                background-color: #21262d;
                color: #f0f6fc;
                border: 1px solid #30363d;
                border-radius: 6px;
                font: 12px "Segoe UI";
            }
            QTreeWidget::item:selected, QListWidget::item:selected {
                background-color: #58a6ff;
                color: #f0f6fc;
            }
            QLabel {
                color: #f0f6fc;
                font: 11px "Segoe UI";
            }
            QLabel#heading {
                font: bold 16px "Segoe UI";
            }
            QLabel#subheading {
                color: #8b949e;
                font: 12px "Segoe UI";
            }
        """)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Job Manager Pro")
        title_label.setObjectName("heading")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        export_button = QPushButton("📤 Export Config")
        export_button.clicked.connect(self.export_config)
        header_layout.addWidget(export_button)
        
        import_button = QPushButton("📥 Import Config")
        import_button.clicked.connect(self.import_config)
        header_layout.addWidget(import_button)
        
        main_layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Main tab
        main_tab = QWidget()
        main_layout_tab = QHBoxLayout(main_tab)
        main_layout_tab.setContentsMargins(15, 15, 15, 15)
        
        # Left panel - Jobs tree
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        left_header = QLabel("Jobs & Branches")
        left_header.setObjectName("subheading")
        left_layout.addWidget(left_header)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Jobs & Branches", "Status", "Session Time"])
        self.tree.setColumnWidth(0, 300)  # Increased to accommodate larger text
        self.tree.setColumnWidth(1, 120)
        self.tree.setColumnWidth(2, 120)
        self.tree.itemSelectionChanged.connect(self.on_tree_select)
        left_layout.addWidget(self.tree)
        
        tree_actions = QHBoxLayout()
        add_job_btn = QPushButton("➕ Add Job")
        add_job_btn.clicked.connect(self.add_job)
        tree_actions.addWidget(add_job_btn)
        
        add_branch_btn = QPushButton("🌿 Add Branch")
        add_branch_btn.clicked.connect(self.add_branch)
        tree_actions.addWidget(add_branch_btn)
        
        self.play_button = QPushButton("▶️ Start")
        self.play_button.clicked.connect(self.toggle_timer)
        tree_actions.addWidget(self.play_button)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.clicked.connect(self.delete_item)
        tree_actions.addWidget(delete_btn)
        
        left_layout.addLayout(tree_actions)
        main_layout_tab.addWidget(left_panel)
        
        # Right panel - Tools
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        right_header = QLabel("Tools")
        right_header.setObjectName("subheading")
        right_layout.addWidget(right_header)
        
        self.tools_listbox = QListWidget()
        self.tools_listbox.itemDoubleClicked.connect(self.open_tool)
        right_layout.addWidget(self.tools_listbox)
        
        tools_actions = QHBoxLayout()
        add_file_btn = QPushButton("📁 Add File")
        add_file_btn.clicked.connect(self.add_file_tool)
        tools_actions.addWidget(add_file_btn)
        
        add_url_btn = QPushButton("🌐 Add URL")
        add_url_btn.clicked.connect(self.add_url_tool)
        tools_actions.addWidget(add_url_btn)
        
        remove_tool_btn = QPushButton("❌ Remove")
        remove_tool_btn.clicked.connect(self.remove_tool)
        tools_actions.addWidget(remove_tool_btn)
        
        right_layout.addLayout(tools_actions)
        
        drop_info = QLabel("💡 Tip: Drag & drop files here or use the buttons above")
        drop_info.setObjectName("subheading")
        right_layout.addWidget(drop_info)
        
        main_layout_tab.addWidget(right_panel)
        self.tabs.addTab(main_tab, "Job Manager")
        
        # Time tracking tab
        time_tab = QWidget()
        time_layout = QVBoxLayout(time_tab)
        time_layout.setContentsMargins(15, 15, 15, 15)
        
        time_header = QLabel("Time Tracking Statistics")
        time_header.setObjectName("heading")
        time_layout.addWidget(time_header)
        
        # Current session info
        session_frame = QWidget()
        session_layout = QVBoxLayout(session_frame)
        session_layout.setContentsMargins(10, 10, 10, 10)
        
        session_header = QLabel("Current Session")
        session_header.setObjectName("subheading")
        session_layout.addWidget(session_header)
        
        self.current_job_label = QLabel("No active job")
        session_layout.addWidget(self.current_job_label)
        
        self.session_time_label = QLabel("Session time: 00:00:00")
        session_layout.addWidget(self.session_time_label)
        
        time_layout.addWidget(session_frame)
        
        # Statistics
        stats_frame = QWidget()
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(10, 10, 10, 10)
        
        stats_header = QLabel("Weekly Statistics")
        stats_header.setObjectName("subheading")
        stats_layout.addWidget(stats_header)
        
        self.stats_tree = QTreeWidget()
        self.stats_tree.setHeaderLabels(["Job", "Today", "This Week", "Total Time"])
        self.stats_tree.setColumnWidth(0, 250)  # Increased to accommodate larger text
        self.stats_tree.setColumnWidth(1, 120)
        self.stats_tree.setColumnWidth(2, 120)
        self.stats_tree.setColumnWidth(3, 120)
        stats_layout.addWidget(self.stats_tree)
        
        time_layout.addWidget(stats_frame)
        self.tabs.addTab(time_tab, "Time Spent")

    def load_data(self):
        """Load job data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for job_name, job_data in data.items():
                        if "time_tracking" not in job_data:
                            job_data["time_tracking"] = {
                                "total_seconds": 0,
                                "sessions": [],
                                "daily_stats": {},
                                "weekly_stats": {}
                            }
                    return data
            except (json.JSONDecodeError, IOError) as e:
                QMessageBox.warning(self, "Warning", f"Could not load existing data: {e}\nStarting fresh.")
        return {}

    def save_data(self):
        """Save job data to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.jobs_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            QMessageBox.critical(self, "Error", f"Could not save data: {e}")

    def populate_tree(self):
        """Populate tree view with existing job data"""
        self.tree.clear()
        for job_name, job_data in self.jobs_data.items():
            status = "⏹️" if self.active_job != job_name else "▶️"
            session_time = "00:00:00"
            if self.active_job == job_name and self.is_timing:
                session_time = self.format_time(self.current_session_time)
            
            job_item = QTreeWidgetItem(self.tree, [f"📋 {job_name}", status, session_time])
            job_item.setData(0, Qt.ItemDataRole.UserRole, ("job", job_name))
            job_item.setExpanded(True)
            
            if "branches" in job_data:
                self.populate_branches(job_item, job_data["branches"], job_name)

    def populate_branches(self, parent_item, branches_data, job_name, parent_path=""):
        """Recursively populate branches with unlimited nesting"""
        for branch_name, branch_data in branches_data.items():
            current_path = f"{parent_path}/{branch_name}" if parent_path else branch_name
            branch_item = QTreeWidgetItem(parent_item, [f"🌿 {branch_name}", "", ""])
            branch_item.setData(0, Qt.ItemDataRole.UserRole, ("branch", job_name, current_path))
            branch_item.setExpanded(True)
            
            if isinstance(branch_data, dict) and "branches" in branch_data:
                self.populate_branches(branch_item, branch_data["branches"], job_name, current_path)

    def toggle_timer(self):
        """Toggle timer for selected job"""
        if self.is_timing:
            self.stop_timer()
            return
            
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a job to track time!")
            return
        
        item = selected_items[0]
        values = item.data(0, Qt.ItemDataRole.UserRole)
        
        if not values or values[0] != "job":
            QMessageBox.warning(self, "Warning", "Please select a job (not a branch) to track time!")
            return
        
        job_name = values[1]
        self.start_timer(job_name)

    def start_timer(self, job_name):
        """Start timer for a job"""
        self.active_job = job_name
        self.start_time = time.time()
        self.is_timing = True
        self.current_session_time = 0
        
        self.play_button.setText("⏸️ Stop")
        self.current_job_label.setText(f"Active job: {job_name}")
        
        self.timer_thread = threading.Thread(target=self.update_timer, daemon=True)
        self.timer_thread.start()
        
        self.refresh_tree_display()
        QMessageBox.information(self, "Timer Started", f"Started tracking time for '{job_name}'")

    def stop_timer(self):
        """Stop the current timer"""
        if not self.is_timing:
            return
        
        current_job = self.active_job
        session_duration = int(time.time() - self.start_time) if self.start_time else 0
        
        self.is_timing = False
        if self.timer_thread:
            threading.Event().wait(0.1)
        
        if current_job and session_duration > 0:
            self.save_time_session(current_job, session_duration)
        
        self.active_job = None
        self.start_time = None
        self.current_session_time = 0
        self.timer_thread = None
        
        self.play_button.setText("▶️ Start")
        self.current_job_label.setText("No active job")
        self.session_time_label.setText("Session time: 00:00:00")
        
        self.refresh_tree_display()
        self.update_time_statistics()
        
        if session_duration > 0:
            QMessageBox.information(self, "Timer Stopped", f"Session saved: {self.format_time(session_duration)}")
        else:
            QMessageBox.information(self, "Timer Stopped", "Timer stopped")

    def update_timer(self):
        """Update timer in a separate thread"""
        try:
            while self.is_timing and self.start_time:
                self.current_session_time = int(time.time() - self.start_time)
                if self.current_session_time % 5 == 0:
                    self.refresh_tree_display()
                time.sleep(1)
        except:
            pass

    def update_ui(self):
        """Update UI elements safely from main thread"""
        if self.is_timing:
            time_str = self.format_time(self.current_session_time)
            self.session_time_label.setText(f"Session time: {time_str}")

    def save_time_session(self, job_name, duration_seconds):
        """Save a time tracking session"""
        if job_name not in self.jobs_data:
            return
        
        if "time_tracking" not in self.jobs_data[job_name]:
            self.jobs_data[job_name]["time_tracking"] = {
                "total_seconds": 0,
                "sessions": [],
                "daily_stats": {},
                "weekly_stats": {}
            }
        
        time_data = self.jobs_data[job_name]["time_tracking"]
        
        time_data["total_seconds"] += duration_seconds
        
        session_record = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "start_time": datetime.now().strftime("%H:%M:%S"),
            "duration_seconds": duration_seconds
        }
        time_data["sessions"].append(session_record)
        
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in time_data["daily_stats"]:
            time_data["daily_stats"][today] = 0
        time_data["daily_stats"][today] += duration_seconds
        
        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
        if week_start not in time_data["weekly_stats"]:
            time_data["weekly_stats"][week_start] = 0
        time_data["weekly_stats"][week_start] += duration_seconds
        
        self.save_data()

    def format_time(self, seconds):
        """Format seconds to HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def refresh_tree_display(self):
        """Refresh the tree display with current timer info"""
        self.tree.clear()
        self.populate_tree()

    def update_time_statistics(self):
        """Update the time statistics display"""
        self.stats_tree.clear()
        
        today = datetime.now().strftime("%Y-%m-%d")
        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
        
        for job_name, job_data in self.jobs_data.items():
            if "time_tracking" not in job_data:
                continue
            
            time_data = job_data["time_tracking"]
            
            today_seconds = time_data["daily_stats"].get(today, 0)
            
            week_seconds = 0
            for date_str, daily_seconds in time_data["daily_stats"].items():
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                week_start_obj = datetime.strptime(week_start, "%Y-%m-%d")
                if date_obj >= week_start_obj:
                    week_seconds += daily_seconds
            
            total_seconds = time_data["total_seconds"]
            
            item = QTreeWidgetItem(self.stats_tree, [
                f"📋 {job_name}",
                self.format_time(today_seconds),
                self.format_time(week_seconds),
                self.format_time(total_seconds)
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, ("job", job_name))

    def add_job(self):
        """Add a new job"""
        job_name, ok = QInputDialog.getText(self, "New Job", "Enter job name:")
        if ok and job_name.strip():
            job_name = job_name.strip()
            if job_name not in self.jobs_data:
                self.jobs_data[job_name] = {
                    "tools": [], 
                    "branches": {},
                    "time_tracking": {
                        "total_seconds": 0,
                        "sessions": [],
                        "daily_stats": {},
                        "weekly_stats": {}
                    }
                }
                item = QTreeWidgetItem(self.tree, [f"📋 {job_name}", "⏹️", "00:00:00"])
                item.setData(0, Qt.ItemDataRole.UserRole, ("job", job_name))
                item.setExpanded(True)
                self.save_data()
                self.update_time_statistics()
                QMessageBox.information(self, "Success", f"Job '{job_name}' created successfully!")
            else:
                QMessageBox.warning(self, "Warning", "Job already exists!")

    def add_branch(self):
        """Add a new branch to selected job or branch"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a job or branch first!")
            return
        
        item = selected_items[0]
        values = item.data(0, Qt.ItemDataRole.UserRole)
        
        if not values or len(values) < 2:
            QMessageBox.warning(self, "Warning", "Invalid selection!")
            return
        
        branch_name, ok = QInputDialog.getText(self, "New Branch", "Enter branch name:")
        if not ok or not branch_name.strip():
            return
        
        branch_name = branch_name.strip()
        job_name = values[1]
        
        if values[0] == "job":
            if branch_name not in self.jobs_data[job_name]["branches"]:
                self.jobs_data[job_name]["branches"][branch_name] = {"tools": [], "branches": {}}
                branch_item = QTreeWidgetItem(item, [f"🌿 {branch_name}", "", ""])
                branch_item.setData(0, Qt.ItemDataRole.UserRole, ("branch", job_name, branch_name))
                branch_item.setExpanded(True)
                self.save_data()
                QMessageBox.information(self, "Success", f"Branch '{branch_name}' created successfully!")
            else:
                QMessageBox.warning(self, "Warning", "Branch already exists!")
                
        elif values[0] == "branch":
            parent_path = values[2]
            path_parts = parent_path.split("/")
            
            current_data = self.jobs_data[job_name]["branches"]
            for part in path_parts:
                if "branches" not in current_data[part]:
                    current_data[part]["branches"] = {}
                current_data = current_data[part]["branches"]
            
            if branch_name not in current_data:
                current_data[branch_name] = {"tools": [], "branches": {}}
                new_path = f"{parent_path}/{branch_name}"
                branch_item = QTreeWidgetItem(item, [f"🌿 {branch_name}", "", ""])
                branch_item.setData(0, Qt.ItemDataRole.UserRole, ("branch", job_name, new_path))
                branch_item.setExpanded(True)
                self.save_data()
                QMessageBox.information(self, "Success", f"Sub-branch '{branch_name}' created successfully!")
            else:
                QMessageBox.warning(self, "Warning", "Branch already exists at this level!")

    def delete_item(self):
        """Delete selected job or branch"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select an item to delete!")
            return
        
        item = selected_items[0]
        values = item.data(0, Qt.ItemDataRole.UserRole)
        item_text = item.text(0)
        
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete '{item_text}'?\n\nThis action cannot be undone.",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if values[0] == "job":
                job_name = values[1]
                del self.jobs_data[job_name]
                QMessageBox.information(self, "Success", f"Job '{job_name}' deleted successfully!")
                
            elif values[0] == "branch":
                job_name = values[1]
                branch_path = values[2]
                path_parts = branch_path.split("/")
                
                current_data = self.jobs_data[job_name]["branches"]
                for part in path_parts[:-1]:
                    if "branches" not in current_data[part]:
                        current_data[part]["branches"] = {}
                    current_data = current_data[part]["branches"]
                
                if path_parts[-1] in current_data:
                    del current_data[path_parts[-1]]
                    QMessageBox.information(self, "Success", f"Branch '{path_parts[-1]}' deleted successfully!")
                else:
                    QMessageBox.warning(self, "Warning", "Branch not found!")
            
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(item))
            self.tools_listbox.clear()
            self.save_data()

    def on_tree_select(self):
        """Handle tree view selection"""
        selected_items = self.tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            values = item.data(0, Qt.ItemDataRole.UserRole)
            self.update_tools_list(values)

    def update_tools_list(self, values):
        """Update tools list based on selection"""
        self.tools_listbox.clear()
        
        if not values or len(values) < 2:
            return
        
        job_name = values[1]
        
        if values[0] == "job":
            tools = self.jobs_data[job_name]["tools"]
        elif values[0] == "branch":
            branch_path = values[2]
            path_parts = branch_path.split("/")
            
            current_data = self.jobs_data[job_name]["branches"]
            for part in path_parts:
                if part in current_data:
                    current_data = current_data[part]
                else:
                    current_data = {"tools": []}
                    break
            
            tools = current_data.get("tools", [])
        else:
            return
        
        for tool in tools:
            display_name = tool.get("name", "Unknown Tool")
            tool_type = tool.get("type", "unknown")
            icon = "📁" if tool_type == "file" else "🌐" if tool_type == "url" else "🔧"
            self.tools_listbox.addItem(f"{icon} {display_name}")

    def add_file_tool(self):
        """Add a file tool via file dialog"""
        if not self._validate_selection():
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Tool File", "",
            "All Files (*.*);;Python Files (*.py);;Shortcuts (*.lnk);;Executables (*.exe);;Batch Files (*.bat);;PowerShell Scripts (*.ps1)"
        )
        if file_path:
            self.add_tool_to_selection(file_path, "file")

    def add_url_tool(self):
        """Add a URL tool"""
        if not self._validate_selection():
            return
            
        url, ok = QInputDialog.getText(self, "Add URL", "Enter URL (e.g., https://example.com):")
        if ok and url.strip():
            url = url.strip()
            if not url.startswith(('http://', 'https://', 'ftp://')):
                url = 'https://' + url
            self.add_tool_to_selection(url, "url")

    def _validate_selection(self):
        """Validate that a job or branch is selected"""
        if not self.tree.selectedItems():
            QMessageBox.warning(self, "Warning", "Please select a job or branch first!")
            return False
        return True

    def add_tool_to_selection(self, path_or_url, tool_type):
        """Add tool to currently selected job or branch"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        values = item.data(0, Qt.ItemDataRole.UserRole)
        
        if not values or len(values) < 2:
            return
        
        tool_name = os.path.basename(path_or_url) if tool_type == "file" else path_or_url
        tool_data = {
            "type": tool_type,
            "name": tool_name,
            "path" if tool_type == "file" else "url": path_or_url
        }
        
        job_name = values[1]
        
        if values[0] == "job":
            self.jobs_data[job_name]["tools"].append(tool_data)
        elif values[0] == "branch":
            branch_path = values[2]
            path_parts = branch_path.split("/")
            
            current_data = self.jobs_data[job_name]["branches"]
            for part in path_parts:
                if part in current_data:
                    current_data = current_data[part]
                else:
                    current_data[part] = {"tools": [], "branches": {}}
                    current_data = current_data[part]
            
            if "tools" not in current_data:
                current_data["tools"] = []
            current_data["tools"].append(tool_data)
        
        self.update_tools_list(values)
        self.save_data()
        QMessageBox.information(self, "Success", f"Tool '{tool_name}' added successfully!")

    def remove_tool(self):
        """Remove selected tool"""
        selected_items = self.tree.selectedItems()
        selected_tools = self.tools_listbox.selectedItems()
        
        if not selected_items or not selected_tools:
            QMessageBox.warning(self, "Warning", "Please select a job/branch and a tool!")
            return
        
        item = selected_items[0]
        values = item.data(0, Qt.ItemDataRole.UserRole)
        tool_index = self.tools_listbox.row(selected_tools[0])
        
        if not values or len(values) < 2:
            return
        
        job_name = values[1]
        tool_name = "Tool"
        
        if values[0] == "job":
            tool_name = self.jobs_data[job_name]["tools"][tool_index]["name"]
            del self.jobs_data[job_name]["tools"][tool_index]
        elif values[0] == "branch":
            branch_path = values[2]
            path_parts = branch_path.split("/")
            
            current_data = self.jobs_data[job_name]["branches"]
            for part in path_parts:
                if part in current_data:
                    current_data = current_data[part]
                else:
                    return
            
            if "tools" in current_data and tool_index < len(current_data["tools"]):
                tool_name = current_data["tools"][tool_index]["name"]
                del current_data["tools"][tool_index]
            else:
                return
        
        self.update_tools_list(values)
        self.save_data()
        QMessageBox.information(self, "Success", f"Tool '{tool_name}' removed successfully!")

    def open_tool(self, item):
        """Open selected tool by double-clicking"""
        selected_items = self.tree.selectedItems()
        selected_tools = self.tools_listbox.selectedItems()
        
        if not selected_items or not selected_tools:
            return
        
        tree_item = selected_items[0]
        values = tree_item.data(0, Qt.ItemDataRole.UserRole)
        tool_index = self.tools_listbox.row(item)
        
        if not values or len(values) < 2:
            return
        
        job_name = values[1]
        
        if values[0] == "job":
            tool_data = self.jobs_data[job_name]["tools"][tool_index]
        elif values[0] == "branch":
            branch_path = values[2]
            path_parts = branch_path.split("/")
            
            current_data = self.jobs_data[job_name]["branches"]
            for part in path_parts:
                if part in current_data:
                    current_data = current_data[part]
                else:
                    return
            
            if "tools" not in current_data or tool_index >= len(current_data["tools"]):
                return
            tool_data = current_data["tools"][tool_index]
        else:
            return
        
        try:
            if tool_data["type"] == "file":
                file_path = tool_data["path"]
                if os.path.exists(file_path):
                    if platform.system() == "Windows":
                        subprocess.run(["cmd", "/c", "start", "", file_path], shell=True)
                    elif platform.system() == "Darwin":
                        subprocess.run(["open", file_path])
                    else:
                        subprocess.run(["xdg-open", file_path])
                else:
                    QMessageBox.critical(self, "Error", f"File not found: {file_path}")
            
            elif tool_data["type"] == "url":
                webbrowser.open(tool_data["url"])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open tool: {e}")

    def export_config(self):
        """Export configuration to a file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Configuration", "",
            "JSON files (*.json);;All files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.jobs_data, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "Success", f"Configuration exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export configuration: {e}")

    def import_config(self):
        """Import configuration from a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Configuration", "",
            "JSON files (*.json);;All files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_data = json.load(f)
                
                reply = QMessageBox.question(
                    self, "Import Mode",
                    "Yes: Merge with existing data\nNo: Replace all data\nCancel: Cancel import",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    for job_name, job_data in imported_data.items():
                        if job_name in self.jobs_data:
                            self.jobs_data[job_name]["tools"].extend(job_data.get("tools", []))
                            self._merge_branches(self.jobs_data[job_name]["branches"], 
                                               job_data.get("branches", {}))
                        else:
                            self.jobs_data[job_name] = job_data
                    
                elif reply == QMessageBox.StandardButton.No:
                    self.jobs_data = imported_data
                
                else:
                    return
                
                self.tree.clear()
                self.tools_listbox.clear()
                self.populate_tree()
                self.save_data()
                
                QMessageBox.information(self, "Success", "Configuration imported successfully!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import configuration: {e}")

    def _merge_branches(self, existing_branches, new_branches):
        """Recursively merge branch data"""
        for branch_name, branch_data in new_branches.items():
            if branch_name in existing_branches:
                existing_branches[branch_name]["tools"].extend(branch_data.get("tools", []))
                self._merge_branches(existing_branches[branch_name]["branches"],
                                   branch_data.get("branches", {}))
            else:
                existing_branches[branch_name] = branch_data

    def closeEvent(self, event):
        """Handle application close"""
        if self.is_timing:
            self.stop_timer()
        self.save_data()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernJobManager()
    window.show()
    sys.exit(app.exec())