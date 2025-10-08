import sys
import json
import os
from datetime import datetime, date, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                             QLineEdit, QTextEdit, QComboBox, QListWidget, 
                             QListWidgetItem, QTabWidget, QMessageBox, 
                             QFrame, QSplitter, QDialog, QDialogButtonBox,
                             QDateEdit, QCheckBox, QScrollArea, QGroupBox,
                             QProgressBar, QListWidget, QMenu, QAction,
                             QInputDialog, QColorDialog, QSystemTrayIcon)
from PyQt5.QtCore import Qt, QDate, QTimer, QMimeData, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QDrag

class TaskDialog(QDialog):
    def __init__(self, parent=None, task=None):
        super().__init__(parent)
        self.task = task
        self.parent_app = parent
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Add/Edit Task")
        self.setModal(True)
        self.resize(500, 500)
        
        layout = QVBoxLayout()
        
        # Task title
        layout.addWidget(QLabel("Task Title:*"))
        self.title_edit = QLineEdit()
        if self.task:
            self.title_edit.setText(self.task['title'])
        layout.addWidget(self.title_edit)
        
        # Task description
        layout.addWidget(QLabel("Description:"))
        self.desc_edit = QTextEdit()
        if self.task:
            self.desc_edit.setText(self.task.get('description', ''))
        self.desc_edit.setMaximumHeight(100)
        layout.addWidget(self.desc_edit)
        
        # Priority
        layout.addWidget(QLabel("Priority:*"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High", "Critical"])
        if self.task:
            self.priority_combo.setCurrentText(self.task.get('priority', 'Medium'))
        else:
            self.priority_combo.setCurrentText('Medium')
        layout.addWidget(self.priority_combo)
        
        # Urgency/Importance (Eisenhower Matrix)
        layout.addWidget(QLabel("Eisenhower Category:*"))
        self.urgency_combo = QComboBox()
        self.urgency_combo.addItems(["Urgent & Important", "Important & Not Urgent", 
                                    "Urgent & Not Important", "Not Urgent & Not Important"])
        if self.task:
            self.urgency_combo.setCurrentText(self.task['urgency'])
        layout.addWidget(self.urgency_combo)
        
        # Categories/Tags
        layout.addWidget(QLabel("Category:"))
        category_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.refresh_categories()
        if self.task:
            self.category_combo.setCurrentText(self.task.get('category', ''))
        category_layout.addWidget(self.category_combo)
        
        manage_categories_btn = QPushButton("Manage")
        manage_categories_btn.clicked.connect(self.manage_categories)
        category_layout.addWidget(manage_categories_btn)
        layout.addLayout(category_layout)
        
        # Due date with time
        layout.addWidget(QLabel("Due Date & Time:"))
        datetime_layout = QHBoxLayout()
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        if self.task and 'due_date' in self.task:
            self.date_edit.setDate(QDate.fromString(self.task['due_date'], 'yyyy-MM-dd'))
        datetime_layout.addWidget(self.date_edit)
        
        self.time_combo = QComboBox()
        self.time_combo.addItems([f"{h:02d}:{m:02d}" for h in range(24) for m in [0, 30]])
        if self.task and 'due_time' in self.task:
            self.time_combo.setCurrentText(self.task['due_time'])
        datetime_layout.addWidget(self.time_combo)
        layout.addLayout(datetime_layout)
        
        # Reminder
        reminder_layout = QHBoxLayout()
        self.reminder_check = QCheckBox("Set Reminder")
        if self.task and self.task.get('reminder'):
            self.reminder_check.setChecked(True)
        reminder_layout.addWidget(self.reminder_check)
        
        self.reminder_combo = QComboBox()
        self.reminder_combo.addItems(["5 minutes", "15 minutes", "30 minutes", "1 hour", "2 hours", "1 day"])
        if self.task and 'reminder_offset' in self.task:
            self.reminder_combo.setCurrentText(self.task['reminder_offset'])
        reminder_layout.addWidget(self.reminder_combo)
        layout.addLayout(reminder_layout)
        
        # Status (for Kanban)
        layout.addWidget(QLabel("Status:*"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["To Do", "In Progress", "Done"])
        if self.task:
            self.status_combo.setCurrentText(self.task['status'])
        layout.addWidget(self.status_combo)
        
        # Dependencies
        layout.addWidget(QLabel("Depends On:"))
        self.dependencies_list = QListWidget()
        self.dependencies_list.setSelectionMode(QListWidget.MultiSelection)
        self.refresh_dependencies()
        layout.addWidget(self.dependencies_list)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def refresh_categories(self):
        self.category_combo.clear()
        if self.parent_app:
            self.category_combo.addItems(self.parent_app.categories)
    
    def refresh_dependencies(self):
        self.dependencies_list.clear()
        if self.parent_app:
            current_task_id = self.task.get('id') if self.task else None
            for task in self.parent_app.tasks:
                if task.get('id') != current_task_id:
                    item = QListWidgetItem(task['title'])
                    item.setData(Qt.UserRole, task.get('id'))
                    if self.task and task.get('id') in self.task.get('dependencies', []):
                        item.setSelected(True)
                    self.dependencies_list.addItem(item)
    
    def manage_categories(self):
        text, ok = QInputDialog.getText(self, "Manage Categories", 
                                       "Add new category (comma-separated for multiple):")
        if ok and text:
            new_categories = [cat.strip() for cat in text.split(',')]
            for category in new_categories:
                if category and category not in self.parent_app.categories:
                    self.parent_app.categories.append(category)
            self.parent_app.save_categories()
            self.refresh_categories()
    
    def validate_and_accept(self):
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Task title is required!")
            return
        
        if not self.priority_combo.currentText():
            QMessageBox.warning(self, "Validation Error", "Priority is required!")
            return
            
        self.accept()
    
    def get_task_data(self):
        selected_dependencies = []
        for i in range(self.dependencies_list.count()):
            item = self.dependencies_list.item(i)
            if item.isSelected():
                selected_dependencies.append(item.data(Qt.UserRole))
        
        task_id = self.task['id'] if self.task else self.parent_app.generate_task_id()
        
        return {
            'id': task_id,
            'title': self.title_edit.text(),
            'description': self.desc_edit.toPlainText(),
            'priority': self.priority_combo.currentText(),
            'urgency': self.urgency_combo.currentText(),
            'category': self.category_combo.currentText(),
            'due_date': self.date_edit.date().toString('yyyy-MM-dd'),
            'due_time': self.time_combo.currentText(),
            'status': self.status_combo.currentText(),
            'dependencies': selected_dependencies,
            'reminder': self.reminder_check.isChecked(),
            'reminder_offset': self.reminder_combo.currentText() if self.reminder_check.isChecked() else '',
            'created': self.task['created'] if self.task else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
    
    def startDrag(self, supportedActions):
        items = self.selectedItems()
        if items:
            mimeData = QMimeData()
            task_data = items[0].data(Qt.UserRole)
            mimeData.setText(json.dumps(task_data))
            
            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.exec_(Qt.MoveAction)

class TaskListWidget(QWidget):
    def __init__(self, title, color, main_app):
        super().__init__()
        self.main_app = main_app
        self.title = title
        self.color = color
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title with task count
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(f"background-color: {self.color.name()}; padding: 5px;")
        layout.addWidget(self.title_label)
        
        # Task list
        self.task_list = DraggableListWidget()
        self.task_list.itemDoubleClicked.connect(self.on_task_double_click)
        self.task_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.task_list)
        
        self.setLayout(layout)
    
    def update_title_count(self):
        count = self.task_list.count()
        self.title_label.setText(f"{self.title} ({count})")
    
    def add_task(self, task):
        item = QListWidgetItem(self.format_task_text(task))
        item.setData(Qt.UserRole, task)
        self.apply_task_styling(item, task)
        self.task_list.addItem(item)
        self.update_title_count()
    
    def format_task_text(self, task):
        text = task['title']
        
        # Add priority indicator
        priority_icons = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
        text = f"{priority_icons.get(task['priority'], '⚪')} {text}"
        
        # Add due date if available
        due_date = task.get('due_date', '')
        if due_date:
            text += f" 📅{due_date}"
        
        # Add category if available
        category = task.get('category', '')
        if category:
            text += f" #{category}"
            
        return text
    
    def apply_task_styling(self, item, task):
        # Priority-based background color
        priority_colors = {
            "Critical": QColor(255, 200, 200),
            "High": QColor(255, 220, 200),
            "Medium": QColor(255, 255, 200),
            "Low": QColor(200, 255, 200)
        }
        
        item.setBackground(priority_colors.get(task['priority'], QColor(240, 240, 240)))
        
        # Strike-through for completed tasks
        if task['status'] == 'Done':
            font = item.font()
            font.setStrikeOut(True)
            item.setFont(font)
    
    def clear(self):
        self.task_list.clear()
        self.update_title_count()
    
    def on_task_double_click(self, item):
        task = item.data(Qt.UserRole)
        self.main_app.edit_task(task)
    
    def show_context_menu(self, position):
        item = self.task_list.itemAt(position)
        if item:
            task = item.data(Qt.UserRole)
            menu = QMenu(self)
            
            edit_action = menu.addAction("Edit Task")
            delete_action = menu.addAction("Delete Task")
            complete_action = menu.addAction("Mark Complete")
            
            action = menu.exec_(self.task_list.mapToGlobal(position))
            
            if action == edit_action:
                self.main_app.edit_task(task)
            elif action == delete_action:
                self.main_app.delete_task(task)
            elif action == complete_action:
                self.main_app.mark_task_complete(task)

class EisenhowerMatrixWidget(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.init_ui()
        
    def init_ui(self):
        layout = QGridLayout()
        layout.setSpacing(10)
        
        # Create quadrants
        self.quadrant1 = TaskListWidget("Urgent & Important", QColor(255, 150, 150), self.main_app)
        self.quadrant2 = TaskListWidget("Important & Not Urgent", QColor(150, 255, 150), self.main_app)
        self.quadrant3 = TaskListWidget("Urgent & Not Important", QColor(255, 255, 150), self.main_app)
        self.quadrant4 = TaskListWidget("Not Urgent & Not Important", QColor(150, 150, 255), self.main_app)
        
        # Add to grid
        layout.addWidget(self.quadrant1, 0, 0)  # Top-left
        layout.addWidget(self.quadrant2, 0, 1)  # Top-right
        layout.addWidget(self.quadrant3, 1, 0)  # Bottom-left
        layout.addWidget(self.quadrant4, 1, 1)  # Bottom-right
        
        self.setLayout(layout)
    
    def refresh_tasks(self):
        tasks = self.main_app.tasks
        self.quadrant1.clear()
        self.quadrant2.clear()
        self.quadrant3.clear()
        self.quadrant4.clear()
        
        for task in tasks:
            if task['urgency'] == "Urgent & Important":
                self.quadrant1.add_task(task)
            elif task['urgency'] == "Important & Not Urgent":
                self.quadrant2.add_task(task)
            elif task['urgency'] == "Urgent & Not Important":
                self.quadrant3.add_task(task)
            elif task['urgency'] == "Not Urgent & Not Important":
                self.quadrant4.add_task(task)

class KanbanColumn(QWidget):
    def __init__(self, status, color, main_app):
        super().__init__()
        self.main_app = main_app
        self.status = status
        self.color = color
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title with progress
        self.title_label = QLabel(self.status)
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(f"background-color: {self.color.name()}; padding: 5px;")
        layout.addWidget(self.title_label)
        
        # Task list
        self.task_list = DraggableListWidget()
        self.task_list.setAcceptDrops(True)
        self.task_list.setDropIndicatorShown(True)
        self.task_list.itemDoubleClicked.connect(self.on_task_double_click)
        self.task_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.task_list)
        
        self.setLayout(layout)
    
    def update_title_count(self):
        count = self.task_list.count()
        self.title_label.setText(f"{self.status} ({count})")
    
    def add_task(self, task):
        item = QListWidgetItem(self.format_task_text(task))
        item.setData(Qt.UserRole, task)
        self.apply_task_styling(item, task)
        self.task_list.addItem(item)
        self.update_title_count()
    
    def format_task_text(self, task):
        text = task['title']
        
        # Add priority indicator
        priority_icons = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
        text = f"{priority_icons.get(task['priority'], '⚪')} {text}"
        
        # Add due date if available
        due_date = task.get('due_date', '')
        if due_date:
            text += f" 📅{due_date}"
        
        # Add category if available
        category = task.get('category', '')
        if category:
            text += f" #{category}"
            
        return text
    
    def apply_task_styling(self, item, task):
        # Priority-based background color
        priority_colors = {
            "Critical": QColor(255, 200, 200),
            "High": QColor(255, 220, 200),
            "Medium": QColor(255, 255, 200),
            "Low": QColor(200, 255, 200)
        }
        
        item.setBackground(priority_colors.get(task['priority'], QColor(240, 240, 240)))
        
        # Strike-through for completed tasks
        if task['status'] == 'Done':
            font = item.font()
            font.setStrikeOut(True)
            item.setFont(font)
    
    def clear(self):
        self.task_list.clear()
        self.update_title_count()
    
    def on_task_double_click(self, item):
        task = item.data(Qt.UserRole)
        self.main_app.edit_task(task)
    
    def show_context_menu(self, position):
        item = self.task_list.itemAt(position)
        if item:
            task = item.data(Qt.UserRole)
            menu = QMenu(self)
            
            edit_action = menu.addAction("Edit Task")
            delete_action = menu.addAction("Delete Task")
            complete_action = menu.addAction("Mark Complete")
            
            action = menu.exec_(self.task_list.mapToGlobal(position))
            
            if action == edit_action:
                self.main_app.edit_task(task)
            elif action == delete_action:
                self.main_app.delete_task(task)
            elif action == complete_action:
                self.main_app.mark_task_complete(task)

class KanbanWidget(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        # Create columns
        self.todo_column = KanbanColumn("To Do", QColor(255, 200, 200), self.main_app)
        self.inprogress_column = KanbanColumn("In Progress", QColor(255, 255, 200), self.main_app)
        self.done_column = KanbanColumn("Done", QColor(200, 255, 200), self.main_app)
        
        # Enable drag and drop
        self.setup_drag_drop()
        
        layout.addWidget(self.todo_column)
        layout.addWidget(self.inprogress_column)
        layout.addWidget(self.done_column)
        
        self.setLayout(layout)
    
    def setup_drag_drop(self):
        # Connect drop events
        self.todo_column.task_list.dropEvent = lambda e: self.handle_drop(e, "To Do")
        self.inprogress_column.task_list.dropEvent = lambda e: self.handle_drop(e, "In Progress")
        self.done_column.task_list.dropEvent = lambda e: self.handle_drop(e, "Done")
    
    def handle_drop(self, event, new_status):
        source = event.source()
        if source:
            items = source.selectedItems()
            if items:
                task = items[0].data(Qt.UserRole)
                old_status = task['status']
                
                # Check dependencies if moving to Done
                if new_status == "Done" and not self.main_app.check_dependencies_complete(task):
                    QMessageBox.warning(self, "Dependency Check", 
                                      "Cannot complete task. Dependent tasks are not finished!")
                    return
                
                # Update task status
                task['status'] = new_status
                task['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # If marking as done, set completion date
                if new_status == "Done" and 'completed_date' not in task:
                    task['completed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                self.main_app.save_tasks()
                self.main_app.refresh_all()
                
                # Show notification
                self.main_app.show_notification(f"Task '{task['title']}' moved from {old_status} to {new_status}")
    
    def refresh_tasks(self):
        tasks = self.main_app.tasks
        self.todo_column.clear()
        self.inprogress_column.clear()
        self.done_column.clear()
        
        for task in tasks:
            if task['status'] == "To Do":
                self.todo_column.add_task(task)
            elif task['status'] == "In Progress":
                self.inprogress_column.add_task(task)
            elif task['status'] == "Done":
                self.done_column.add_task(task)

class StatisticsWidget(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Overall Progress
        progress_group = QGroupBox("Overall Progress")
        progress_layout = QVBoxLayout()
        
        self.overall_progress = QProgressBar()
        self.overall_progress.setMaximumHeight(25)
        progress_layout.addWidget(QLabel("Completion Progress:"))
        progress_layout.addWidget(self.overall_progress)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Statistics Grid
        stats_group = QGroupBox("Task Statistics")
        stats_layout = QGridLayout()
        
        # Eisenhower Matrix Stats
        stats_layout.addWidget(QLabel("Eisenhower Matrix:"), 0, 0)
        self.eisenhower_stats = QLabel("Loading...")
        stats_layout.addWidget(self.eisenhower_stats, 0, 1)
        
        # Priority Stats
        stats_layout.addWidget(QLabel("Priority Distribution:"), 1, 0)
        self.priority_stats = QLabel("Loading...")
        stats_layout.addWidget(self.priority_stats, 1, 1)
        
        # Status Stats
        stats_layout.addWidget(QLabel("Status Distribution:"), 2, 0)
        self.status_stats = QLabel("Loading...")
        stats_layout.addWidget(self.status_stats, 2, 1)
        
        # Category Stats
        stats_layout.addWidget(QLabel("Category Distribution:"), 3, 0)
        self.category_stats = QLabel("Loading...")
        stats_layout.addWidget(self.category_stats, 3, 1)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Recent Activity
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout()
        self.activity_list = QListWidget()
        activity_layout.addWidget(self.activity_list)
        activity_group.setLayout(activity_layout)
        layout.addWidget(activity_group)
        
        self.setLayout(layout)
    
    def refresh_stats(self):
        tasks = self.main_app.tasks
        
        if not tasks:
            self.overall_progress.setValue(0)
            self.eisenhower_stats.setText("No tasks")
            self.priority_stats.setText("No tasks")
            self.status_stats.setText("No tasks")
            self.category_stats.setText("No tasks")
            return
        
        # Overall progress
        completed = len([t for t in tasks if t['status'] == 'Done'])
        total = len(tasks)
        progress = int((completed / total) * 100) if total > 0 else 0
        self.overall_progress.setValue(progress)
        
        # Eisenhower Matrix stats
        quadrants = {
            "Urgent & Important": 0,
            "Important & Not Urgent": 0,
            "Urgent & Not Important": 0,
            "Not Urgent & Not Important": 0
        }
        for task in tasks:
            quadrants[task['urgency']] += 1
        
        eisenhower_text = "\n".join([f"{k}: {v}" for k, v in quadrants.items()])
        self.eisenhower_stats.setText(eisenhower_text)
        
        # Priority stats
        priorities = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for task in tasks:
            priorities[task['priority']] += 1
        
        priority_text = "\n".join([f"{k}: {v}" for k, v in priorities.items()])
        self.priority_stats.setText(priority_text)
        
        # Status stats
        statuses = {"To Do": 0, "In Progress": 0, "Done": 0}
        for task in tasks:
            statuses[task['status']] += 1
        
        status_text = "\n".join([f"{k}: {v}" for k, v in statuses.items()])
        self.status_stats.setText(status_text)
        
        # Category stats
        categories = {}
        for task in tasks:
            cat = task.get('category', 'Uncategorized')
            categories[cat] = categories.get(cat, 0) + 1
        
        category_text = "\n".join([f"{k}: {v}" for k, v in categories.items()])
        self.category_stats.setText(category_text)
        
        # Recent activity
        self.activity_list.clear()
        sorted_tasks = sorted(tasks, key=lambda x: x['last_updated'], reverse=True)[:10]
        for task in sorted_tasks:
            item = QListWidgetItem(f"{task['title']} - {task['last_updated']}")
            self.activity_list.addItem(item)

class DailyRoutineManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tasks = []
        self.categories = ["Work", "Personal", "Health", "Learning", "Finance"]
        self.data_file = "daily_routine.json"
        self.categories_file = "categories.json"
        self.load_data()
        self.init_ui()
        self.setup_reminders()
        
    def init_ui(self):
        self.setWindowTitle("Daily Routine Manager - Eisenhower Matrix & Kanban")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Daily Routine Manager")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title_label)
        
        # Add task button
        add_task_btn = QPushButton("Add New Task")
        add_task_btn.clicked.connect(self.add_new_task)
        header_layout.addWidget(add_task_btn)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_all)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Eisenhower Matrix Tab
        self.eisenhower_tab = EisenhowerMatrixWidget(self)
        self.tab_widget.addTab(self.eisenhower_tab, "Eisenhower Matrix")
        
        # Kanban Tab
        self.kanban_tab = KanbanWidget(self)
        self.tab_widget.addTab(self.kanban_tab, "Kanban Board")
        
        # Statistics Tab
        self.stats_tab = StatisticsWidget(self)
        self.tab_widget.addTab(self.stats_tab, "Statistics & Analytics")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.statusBar().showMessage(f"Total Tasks: {len(self.tasks)}")
        
        central_widget.setLayout(main_layout)
        
        # Initial refresh
        self.refresh_all()
    
    def setup_reminders(self):
        self.reminder_timer = QTimer()
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(60000)  # Check every minute
    
    def check_reminders(self):
        now = datetime.now()
        for task in self.tasks:
            if task.get('reminder') and not task.get('reminder_shown', False):
                due_datetime = datetime.strptime(f"{task['due_date']} {task['due_time']}", "%Y-%m-%d %H:%M")
                reminder_offset = self.parse_reminder_offset(task['reminder_offset'])
                reminder_time = due_datetime - reminder_offset
                
                if now >= reminder_time:
                    self.show_reminder(task)
                    task['reminder_shown'] = True
                    self.save_tasks()
    
    def parse_reminder_offset(self, offset_str):
        offsets = {
            "5 minutes": timedelta(minutes=5),
            "15 minutes": timedelta(minutes=15),
            "30 minutes": timedelta(minutes=30),
            "1 hour": timedelta(hours=1),
            "2 hours": timedelta(hours=2),
            "1 day": timedelta(days=1)
        }
        return offsets.get(offset_str, timedelta(minutes=15))
    
    def show_reminder(self, task):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Task Reminder")
        msg.setText(f"Reminder: {task['title']}")
        msg.setInformativeText(f"Due: {task['due_date']} at {task['due_time']}\n"
                              f"Priority: {task['priority']}\n"
                              f"Category: {task.get('category', 'None')}")
        msg.exec_()
    
    def show_notification(self, message):
        self.statusBar().showMessage(message, 3000)
    
    def generate_task_id(self):
        return str(int(datetime.now().timestamp()))
    
    def check_dependencies_complete(self, task):
        dependencies = task.get('dependencies', [])
        if not dependencies:
            return True
        
        dependency_tasks = [t for t in self.tasks if t['id'] in dependencies]
        return all(t['status'] == 'Done' for t in dependency_tasks)
    
    def add_new_task(self):
        dialog = TaskDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            task_data = dialog.get_task_data()
            self.tasks.append(task_data)
            self.save_tasks()
            self.refresh_all()
            self.show_notification("Task added successfully!")
    
    def edit_task(self, task):
        dialog = TaskDialog(self, task)
        if dialog.exec_() == QDialog.Accepted:
            updated_task = dialog.get_task_data()
            # Find and update the task
            for i, t in enumerate(self.tasks):
                if t['id'] == task['id']:
                    self.tasks[i] = updated_task
                    break
            self.save_tasks()
            self.refresh_all()
            self.show_notification("Task updated successfully!")
    
    def delete_task(self, task):
        reply = QMessageBox.question(self, "Delete Task", 
                                   f"Are you sure you want to delete '{task['title']}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.tasks = [t for t in self.tasks if t['id'] != task['id']]
            self.save_tasks()
            self.refresh_all()
            self.show_notification("Task deleted successfully!")
    
    def mark_task_complete(self, task):
        if not self.check_dependencies_complete(task):
            QMessageBox.warning(self, "Dependency Check", 
                              "Cannot complete task. Dependent tasks are not finished!")
            return
        
        task['status'] = 'Done'
        task['completed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save_tasks()
        self.refresh_all()
        self.show_notification("Task marked as complete!")
    
    def refresh_all(self):
        self.eisenhower_tab.refresh_tasks()
        self.kanban_tab.refresh_tasks()
        self.stats_tab.refresh_stats()
        self.statusBar().showMessage(f"Total Tasks: {len(self.tasks)} | "
                                   f"Completed: {len([t for t in self.tasks if t['status'] == 'Done'])}")
    
    def load_data(self):
        # Load tasks
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.tasks = json.load(f)
            except:
                self.tasks = []
        
        # Load categories
        if os.path.exists(self.categories_file):
            try:
                with open(self.categories_file, 'r') as f:
                    self.categories = json.load(f)
            except:
                self.categories = ["Work", "Personal", "Health", "Learning", "Finance"]
    
    def save_tasks(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def save_categories(self):
        with open(self.categories_file, 'w') as f:
            json.dump(self.categories, f, indent=2)

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = DailyRoutineManager()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()