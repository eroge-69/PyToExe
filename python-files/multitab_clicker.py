import sys
import threading
import time
import pyautogui
import keyboard
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QSpinBox, QComboBox, QLabel, QTabWidget, QLineEdit, 
    QMessageBox, QFileDialog, QStatusBar, QAction, QMenuBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

pyautogui.FAILSAFE = False

class ClickTask:
    def __init__(self, x, y, delay_ms, click_type):
        self.x = x
        self.y = y
        self.delay_ms = delay_ms
        self.click_type = click_type

class ClickTab(QWidget):
    def __init__(self, tab_id, name="Task"):
        super().__init__()
        self.tab_id = tab_id
        self.name = name
        self.click_tasks = []
        self.is_running = False
        self.hotkey = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Table for click tasks
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["X", "Y", "Delay (ms)", "Click Type"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # Input fields
        input_layout = QHBoxLayout()
        self.x_input = QSpinBox(); self.x_input.setMaximum(10000)
        self.y_input = QSpinBox(); self.y_input.setMaximum(10000)
        self.delay_input = QSpinBox(); self.delay_input.setMaximum(100000); self.delay_input.setValue(1000)
        self.click_type_input = QComboBox()
        self.click_type_input.addItems(["left", "right", "middle", "double"])
        input_layout.addWidget(QLabel("X:")); input_layout.addWidget(self.x_input)
        input_layout.addWidget(QLabel("Y:")); input_layout.addWidget(self.y_input)
        input_layout.addWidget(QLabel("Delay (ms):")); input_layout.addWidget(self.delay_input)
        input_layout.addWidget(QLabel("Click Type:")); input_layout.addWidget(self.click_type_input)

        # Position button
        self.get_pos_button = QPushButton("📍 Get Position")
        self.get_pos_button.clicked.connect(self.get_mouse_position)
        input_layout.addWidget(self.get_pos_button)

        # Add button
        add_button = QPushButton("➕ Add")
        add_button.clicked.connect(self.add_click)
        input_layout.addWidget(add_button)

        layout.addLayout(input_layout)

        # Repeat and hotkey settings
        repeat_layout = QHBoxLayout()
        repeat_layout.addWidget(QLabel("Repeat (0 = ∞):"))
        self.repeat_input = QSpinBox(); self.repeat_input.setMaximum(100000)
        self.repeat_input.setValue(1)
        repeat_layout.addWidget(self.repeat_input)

        repeat_layout.addWidget(QLabel("Hotkey:"))
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setPlaceholderText("e.g., ctrl+shift+1")
        repeat_layout.addWidget(self.hotkey_input)

        set_hotkey_btn = QPushButton("Set Hotkey")
        set_hotkey_btn.clicked.connect(self.set_hotkey)
        repeat_layout.addWidget(set_hotkey_btn)

        layout.addLayout(repeat_layout)

        # Action buttons
        action_layout = QHBoxLayout()
        self.remove_button = QPushButton("🗑️ Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected)
        action_layout.addWidget(self.remove_button)

        self.clear_button = QPushButton("🧹 Clear All")
        self.clear_button.clicked.connect(self.clear_all)
        action_layout.addWidget(self.clear_button)

        self.save_button = QPushButton("💾 Save Tasks")
        self.save_button.clicked.connect(self.save_tasks)
        action_layout.addWidget(self.save_button)

        self.load_button = QPushButton("📂 Load Tasks")
        self.load_button.clicked.connect(self.load_tasks)
        action_layout.addWidget(self.load_button)

        layout.addLayout(action_layout)

        self.setLayout(layout)

    def add_click(self):
        x = self.x_input.value()
        y = self.y_input.value()
        delay = self.delay_input.value()
        click_type = self.click_type_input.currentText()
        task = ClickTask(x, y, delay, click_type)
        self.click_tasks.append(task)
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(x)))
        self.table.setItem(row, 1, QTableWidgetItem(str(y)))
        self.table.setItem(row, 2, QTableWidgetItem(str(delay)))
        self.table.setItem(row, 3, QTableWidgetItem(click_type))

    def get_mouse_position(self):
        self.hide()
        QMessageBox.information(self, "Get Position", "Move your mouse to the target location in the next 3 seconds...")
        time.sleep(3)
        x, y = pyautogui.position()
        self.x_input.setValue(x)
        self.y_input.setValue(y)
        self.show()

    def set_hotkey(self):
        new_hotkey = self.hotkey_input.text().strip()
        if not new_hotkey:
            QMessageBox.warning(self, "Error", "Hotkey cannot be empty")
            return
        try:
            if self.hotkey:
                keyboard.remove_hotkey(self.hotkey)
            self.hotkey = keyboard.add_hotkey(new_hotkey, self.start_clicking)
            QMessageBox.information(self, "Hotkey Set", f"Hotkey '{new_hotkey}' assigned to Tab {self.tab_id + 1}")
        except Exception as e:
            QMessageBox.critical(self, "Hotkey Error", str(e))

    def start_clicking(self):
        if self.is_running:
            return
        if not self.click_tasks:
            QMessageBox.warning(self, "No Tasks", "Please add click tasks first")
            return
            
        self.is_running = True
        threading.Thread(target=self.run_clicks, args=(self.repeat_input.value(),), daemon=True).start()

    def run_clicks(self, repeat_count):
        count = 0
        while self.is_running:
            for task in self.click_tasks:
                if not self.is_running:
                    break
                pyautogui.click(task.x, task.y, button=task.click_type)
                time.sleep(task.delay_ms / 1000.0)
            count += 1
            if repeat_count > 0 and count >= repeat_count:
                break
        self.is_running = False

    def remove_selected(self):
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()), reverse=True)
        for row in selected_rows:
            self.table.removeRow(row)
            if row < len(self.click_tasks):
                self.click_tasks.pop(row)

    def clear_all(self):
        self.table.setRowCount(0)
        self.click_tasks = []

    def save_tasks(self):
        if not self.click_tasks:
            QMessageBox.warning(self, "No Tasks", "No tasks to save")
            return
            
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Tasks", "", "JSON Files (*.json);;All Files (*)", options=options)
            
        if not filename:
            return
            
        if not filename.endswith('.json'):
            filename += '.json'
            
        data = {
            "repeat": self.repeat_input.value(),
            "hotkey": self.hotkey_input.text(),
            "tasks": [
                {
                    "x": task.x,
                    "y": task.y,
                    "delay_ms": task.delay_ms,
                    "click_type": task.click_type
                } for task in self.click_tasks
            ]
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            QMessageBox.information(self, "Success", f"Tasks saved to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save tasks: {str(e)}")

    def load_tasks(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Tasks", "", "JSON Files (*.json);;All Files (*)", options=options)
            
        if not filename:
            return
            
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            # Clear current tasks
            self.clear_all()
            
            # Load new tasks
            self.repeat_input.setValue(data.get("repeat", 1))
            self.hotkey_input.setText(data.get("hotkey", ""))
            
            for task_data in data.get("tasks", []):
                task = ClickTask(
                    task_data["x"],
                    task_data["y"],
                    task_data["delay_ms"],
                    task_data["click_type"]
                )
                self.click_tasks.append(task)
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(task.x)))
                self.table.setItem(row, 1, QTableWidgetItem(str(task.y)))
                self.table.setItem(row, 2, QTableWidgetItem(str(task.delay_ms)))
                self.table.setItem(row, 3, QTableWidgetItem(task.click_type))
                
            QMessageBox.information(self, "Success", f"Tasks loaded from {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load tasks: {str(e)}")

    # --- Added for project-wide load/save ---
    def to_dict(self):
        return {
            "name": self.name,
            "repeat": self.repeat_input.value(),
            "hotkey": self.hotkey_input.text(),
            "tasks": [
                {
                    "x": t.x, "y": t.y, "delay_ms": t.delay_ms, "click_type": t.click_type
                } for t in self.click_tasks
            ]
        }

    def from_dict(self, data):
        self.clear_all()
        self.name = data.get("name", "Task")
        self.repeat_input.setValue(data.get("repeat", 1))
        self.hotkey_input.setText(data.get("hotkey", ""))
        for task_data in data.get("tasks", []):
            task = ClickTask(
                task_data["x"],
                task_data["y"],
                task_data["delay_ms"],
                task_data["click_type"]
            )
            self.click_tasks.append(task)
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(task.x)))
            self.table.setItem(row, 1, QTableWidgetItem(str(task.y)))
            self.table.setItem(row, 2, QTableWidgetItem(str(task.delay_ms)))
            self.table.setItem(row, 3, QTableWidgetItem(task.click_type))

class MultiTabClicker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multitasking Auto Clicker with Tabs")
        self.setGeometry(300, 200, 900, 600)
        
        # Create menu bar
        menubar = QMenuBar()
        file_menu = menubar.addMenu("&File")

        save_proj_action = QAction("Save Project", self)
        save_proj_action.setShortcut(QKeySequence("Ctrl+S"))
        save_proj_action.triggered.connect(self.save_project)
        file_menu.addAction(save_proj_action)

        load_proj_action = QAction("Load Project", self)
        load_proj_action.setShortcut(QKeySequence("Ctrl+O"))
        load_proj_action.triggered.connect(self.load_project)
        file_menu.addAction(load_proj_action)

        # Global stop action
        stop_action = QAction("Stop All", self)
        stop_action.setShortcut(QKeySequence("Esc"))
        stop_action.triggered.connect(self.stop_all_tasks)
        file_menu.addAction(stop_action)

        main_layout = QVBoxLayout()
        main_layout.setMenuBar(menubar)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.add_tab_button = QPushButton("➕ Add New Tab")
        self.add_tab_button.clicked.connect(self.add_new_tab)
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.add_tab_button)
        main_layout.addWidget(self.status_bar)
        self.setLayout(main_layout)
        keyboard.add_hotkey('esc', self.stop_all_tasks)

        # For project load/save
        self.project_file = None

        # Add initial tabs
        for i in range(3):
            self.add_tab(f"Task {i + 1}")

    def add_tab(self, name):
        tab = ClickTab(self.tabs.count(), name)
        self.tabs.addTab(tab, name)
        return tab

    def add_new_tab(self):
        tab_count = self.tabs.count() + 1
        self.add_tab(f"Task {tab_count}")

    def close_tab(self, index):
        if self.tabs.count() > 1:
            widget = self.tabs.widget(index)
            if widget.is_running:
                widget.is_running = False
                time.sleep(0.1)
            self.tabs.removeTab(index)
        else:
            QMessageBox.warning(self, "Cannot Close", "At least one tab must remain open")

    def stop_all_tasks(self):
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            tab.is_running = False
        self.status_bar.showMessage("All tasks stopped", 3000)

    # --- Project-wide Save/Load ---
    def save_project(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "", "MultiTabClicker Project (*.mtcproj);;All Files (*)", options=options)
        if not filename:
            return
        if not filename.endswith('.mtcproj'):
            filename += '.mtcproj'

        project_data = {
            "tabs": [self.tabs.tabText(i) for i in range(self.tabs.count())],
            "tab_data": [self.tabs.widget(i).to_dict() for i in range(self.tabs.count())]
        }

        try:
            with open(filename, 'w') as f:
                json.dump(project_data, f, indent=4)
            self.status_bar.showMessage(f"Project saved: {filename}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save project: {str(e)}")

    def load_project(self, filename=None):
        if not filename:
            options = QFileDialog.Options()
            filename, _ = QFileDialog.getOpenFileName(
                self, "Load Project", "", "MultiTabClicker Project (*.mtcproj);;All Files (*)", options=options)
            if not filename:
                return

        try:
            with open(filename, 'r') as f:
                project_data = json.load(f)

            # Remove all tabs
            while self.tabs.count() > 0:
                self.tabs.removeTab(0)

            for i, tab_name in enumerate(project_data.get("tabs", [])):
                tab = self.add_tab(tab_name)
                tab.from_dict(project_data["tab_data"][i])

            self.status_bar.showMessage(f"Project loaded: {filename}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load project: {str(e)}")

# --- Support for opening file by argument ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MultiTabClicker()
    # If project file provided as argument, auto-load it
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        window.load_project(sys.argv[1])
    window.show()
    sys.exit(app.exec_())
