import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QPushButton, QLineEdit, QLabel,
    QDialog, QFormLayout, QDialogButtonBox, QPlainTextEdit, QMessageBox,
    QGroupBox, QComboBox
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont

# Data model for a command entry.
class Command:
    def __init__(self, title, command, description, group, tags, id=None, order_index=0):
        self.id = id
        self.title = title
        self.command = command
        self.description = description
        self.group = group
        self.tags = tags  # a list of strings (unused now)
        self.order_index = order_index

# Dialog for adding/editing a command.
class CommandDialog(QDialog):
    def __init__(self, command_obj=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Command")
        self.layout = QFormLayout(self)
        
        self.title_edit = QLineEdit()
        
        # QPlainTextEdit for multi-line command input.
        self.command_edit = QPlainTextEdit()
        self.command_edit.setFixedHeight(100)
        
        # QPlainTextEdit for multi-line description.
        self.description_edit = QPlainTextEdit()
        self.description_edit.setFixedHeight(80)
        
        self.group_edit = QLineEdit()
        self.tags_edit = QLineEdit()  # comma-separated (still stored but not filtered)
        
        self.layout.addRow("Title:", self.title_edit)
        self.layout.addRow("Command:", self.command_edit)
        self.layout.addRow("Description:", self.description_edit)
        self.layout.addRow("Group:", self.group_edit)
        self.layout.addRow("Tags (comma-separated):", self.tags_edit)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)
        
        if command_obj:
            self.title_edit.setText(command_obj.title)
            self.command_edit.setPlainText(command_obj.command)
            self.description_edit.setPlainText(command_obj.description)
            self.group_edit.setText(command_obj.group)
            self.tags_edit.setText(", ".join(command_obj.tags))
    
    def get_data(self):
        title = self.title_edit.text().strip()
        command_text = self.command_edit.toPlainText().strip()
        description = self.description_edit.toPlainText().strip()
        group = self.group_edit.text().strip()
        tags = [tag.strip() for tag in self.tags_edit.text().split(",") if tag.strip()]
        return Command(title, command_text, description, group, tags)

# Main application window.
class CommandManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linux Command Archive")
        self.resize(1000, 700)
        
        # Save search mode preference.
        self.settings = QSettings("MyCompany", "CommandArchive")
        
        # Connect to (or create) the SQLite database.
        self.conn = sqlite3.connect("commands.db")
        self.cursor = self.conn.cursor()
        self.init_db()
        
        self.commands = []  # List of Command objects.
        self.selected_groups = set()  # groups selected via toggle buttons
        
        # Main widget and layout.
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.v_layout = QVBoxLayout(self.main_widget)
        
        # --- Top Filter Bar: Search query and search mode ---
        filter_bar = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Enter search query...")
        self.search_edit.textChanged.connect(self.refresh_tree)
        
        mode_label = QLabel("Mode:")
        self.search_mode_combo = QComboBox()
        self.search_mode_combo.addItems([
            "Default (All except command)",
            "All",
            "Groups",
            "Command"
        ])
        # Restore saved search mode if available.
        saved_mode = self.settings.value("search_mode", "Default (All except command)")
        index = self.search_mode_combo.findText(saved_mode)
        if index != -1:
            self.search_mode_combo.setCurrentIndex(index)
        self.search_mode_combo.currentIndexChanged.connect(self.on_search_mode_changed)
        
        filter_bar.addWidget(search_label)
        filter_bar.addWidget(self.search_edit)
        filter_bar.addWidget(mode_label)
        filter_bar.addWidget(self.search_mode_combo)
        self.v_layout.addLayout(filter_bar)
        
        # --- Group Filter Buttons (stacked horizontally) ---
        self.group_filter_box = QGroupBox("Filter by Groups")
        self.group_filter_layout = QHBoxLayout()  # horizontal layout
        self.group_filter_box.setLayout(self.group_filter_layout)
        self.v_layout.addWidget(self.group_filter_box)
        
        # --- QTreeWidget for listing commands ---
        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(["Title", "Group", "Tags", "Actions"])
        self.tree.setColumnWidth(0, 250)
        self.tree.setColumnWidth(1, 150)
        self.tree.setColumnWidth(2, 200)
        self.tree.setColumnWidth(3, 150)
        self.v_layout.addWidget(self.tree)
        
        # --- Buttons for Add, Edit, Delete, and reordering ---
        btn_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Command")
        self.add_button.clicked.connect(self.add_command)
        self.edit_button = QPushButton("Edit Command")
        self.edit_button.clicked.connect(self.edit_command)
        self.delete_button = QPushButton("Delete Command")
        self.delete_button.clicked.connect(self.delete_command)
        self.move_up_button = QPushButton("Move Up")
        self.move_up_button.clicked.connect(self.move_up)
        self.move_down_button = QPushButton("Move Down")
        self.move_down_button.clicked.connect(self.move_down)
        
        btn_layout.addWidget(self.add_button)
        btn_layout.addWidget(self.edit_button)
        btn_layout.addWidget(self.delete_button)
        btn_layout.addWidget(self.move_up_button)
        btn_layout.addWidget(self.move_down_button)
        self.v_layout.addLayout(btn_layout)
        
        self.load_commands()
        self.update_filter_buttons()  # build group filter buttons
        self.refresh_tree()
    
    def init_db(self):
        # Create the commands table if it doesn't exist.
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                command TEXT,
                description TEXT,
                group_name TEXT,
                tags TEXT,
                order_index INTEGER
            )
        """)
        self.conn.commit()
    
    def load_commands(self):
        """Load commands from the database (ordered by order_index)."""
        self.commands = []
        self.cursor.execute("""
            SELECT id, title, command, description, group_name, tags, order_index
            FROM commands
            ORDER BY order_index ASC
        """)
        rows = self.cursor.fetchall()
        for row in rows:
            id, title, command_text, description, group_name, tags_str, order_index = row
            tags = [tag.strip() for tag in tags_str.split(",")] if tags_str else []
            cmd = Command(title, command_text, description, group_name, tags, id=id, order_index=order_index)
            self.commands.append(cmd)
    
    def update_filter_buttons(self):
        """Rebuild the group filter buttons based on current commands."""
        unique_groups = sorted({cmd.group for cmd in self.commands if cmd.group})
        # Clear current layout.
        for i in reversed(range(self.group_filter_layout.count())):
            widget = self.group_filter_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        # Create a toggle button for each group.
        for group in unique_groups:
            btn = QPushButton(group)
            btn.setCheckable(True)
            btn.setChecked(group in self.selected_groups)
            btn.toggled.connect(lambda checked, grp=group: self.on_group_button_toggled(grp, checked))
            self.group_filter_layout.addWidget(btn)
    
    def on_group_button_toggled(self, group, checked):
        if checked:
            self.selected_groups.add(group)
        else:
            self.selected_groups.discard(group)
        self.refresh_tree()
    
    def on_search_mode_changed(self):
        # Save the selected search mode.
        mode = self.search_mode_combo.currentText()
        self.settings.setValue("search_mode", mode)
        self.refresh_tree()
    
    def refresh_tree(self):
        """Refresh the QTreeWidget based on search query, mode, and group filter."""
        self.tree.clear()
        query = self.search_edit.text().strip().lower()
        mode = self.search_mode_combo.currentText()
        
        # Decide if a command matches the search query.
        def command_matches(cmd):
            if query:
                if mode == "Default (All except command)":
                    if (query not in cmd.title.lower() and
                        query not in cmd.group.lower() and
                        query not in ", ".join(cmd.tags).lower() and
                        query not in cmd.description.lower()):
                        return False
                elif mode == "All":
                    if (query not in cmd.title.lower() and
                        query not in cmd.group.lower() and
                        query not in ", ".join(cmd.tags).lower() and
                        query not in cmd.description.lower() and
                        query not in cmd.command.lower()):
                        return False
                elif mode == "Groups":
                    if query not in cmd.group.lower():
                        return False
                elif mode == "Command":
                    if query not in cmd.command.lower():
                        return False
            # Apply group filter: if any group is selected, the command's group must be one of them.
            if self.selected_groups and cmd.group not in self.selected_groups:
                return False
            return True
        
        # Populate the tree with commands that match.
        for cmd in self.commands:
            if not command_matches(cmd):
                continue
            
            # Top-level item.
            top_item = QTreeWidgetItem([cmd.title, cmd.group, ", ".join(cmd.tags), ""])
            top_item.setData(0, Qt.UserRole, cmd.id)
            self.tree.addTopLevelItem(top_item)
            
            # Create a Copy button.
            copy_btn = QPushButton("Copy")
            copy_btn.clicked.connect(lambda checked, c=cmd: self.copy_to_clipboard(c.command))
            self.tree.setItemWidget(top_item, 3, copy_btn)
            
            # Child item: Expanded details.
            child_item = QTreeWidgetItem()
            top_item.addChild(child_item)
            
            # Create a details widget with a code block for the command and a description area.
            details_widget = QWidget()
            details_layout = QVBoxLayout(details_widget)
            details_layout.setContentsMargins(5, 5, 5, 5)
            details_layout.setSpacing(5)
            
            # Code block style for the command.
            code_widget = QPlainTextEdit()
            code_widget.setReadOnly(True)
            code_widget.setPlainText(cmd.command)
            code_widget.setFont(QFont("Courier New"))
            code_widget.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ccc;")
            code_widget.setFixedHeight(100)  # Adjust as needed.
            details_layout.addWidget(code_widget)
            
            # Description label.
            desc_label = QLabel("Description:")
            desc_label.setStyleSheet("font-weight: bold;")
            details_layout.addWidget(desc_label)
            
            # Description text.
            desc_widget = QLabel(cmd.description)
            desc_widget.setWordWrap(True)
            details_layout.addWidget(desc_widget)
            
            # Set details widget to span all columns.
            self.tree.setItemWidget(child_item, 0, details_widget)
            child_item.setFirstColumnSpanned(True)
        
        self.tree.collapseAll()
    
    def copy_to_clipboard(self, text):
        QApplication.clipboard().setText(text)
    
    def add_command(self):
        dialog = CommandDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            new_cmd = dialog.get_data()
            next_order = max([cmd.order_index for cmd in self.commands], default=-1) + 1
            new_cmd.order_index = next_order
            self.cursor.execute(
                "INSERT INTO commands (title, command, description, group_name, tags, order_index) VALUES (?, ?, ?, ?, ?, ?)",
                (new_cmd.title, new_cmd.command, new_cmd.description, new_cmd.group, ", ".join(new_cmd.tags), new_cmd.order_index)
            )
            self.conn.commit()
            self.load_commands()
            self.update_filter_buttons()
            self.refresh_tree()
    
    def get_selected_command(self):
        selected = self.tree.selectedItems()
        if selected:
            item = selected[0]
            if item.parent():
                item = item.parent()
            cmd_id = item.data(0, Qt.UserRole)
            for cmd in self.commands:
                if cmd.id == cmd_id:
                    return cmd
        return None
    
    def edit_command(self):
        cmd = self.get_selected_command()
        if not cmd:
            QMessageBox.information(self, "Edit Command", "Please select a command to edit.")
            return
        dialog = CommandDialog(command_obj=cmd, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            updated_cmd = dialog.get_data()
            self.cursor.execute(
                "UPDATE commands SET title=?, command=?, description=?, group_name=?, tags=? WHERE id=?",
                (updated_cmd.title, updated_cmd.command, updated_cmd.description, updated_cmd.group, ", ".join(updated_cmd.tags), cmd.id)
            )
            self.conn.commit()
            self.load_commands()
            self.update_filter_buttons()
            self.refresh_tree()
    
    def delete_command(self):
        cmd = self.get_selected_command()
        if not cmd:
            QMessageBox.information(self, "Delete Command", "Please select a command to delete.")
            return
        confirm = QMessageBox.question(
            self, "Delete Command", f"Are you sure you want to delete '{cmd.title}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM commands WHERE id=?", (cmd.id,))
            self.conn.commit()
            self.load_commands()
            self.update_filter_buttons()
            self.refresh_tree()
    
    def move_up(self):
        cmd = self.get_selected_command()
        if not cmd:
            QMessageBox.information(self, "Move Up", "Please select a command to move.")
            return
        index = self.commands.index(cmd)
        if index > 0:
            other = self.commands[index - 1]
            self.cursor.execute("UPDATE commands SET order_index=? WHERE id=?", (other.order_index, cmd.id))
            self.cursor.execute("UPDATE commands SET order_index=? WHERE id=?", (cmd.order_index, other.id))
            self.conn.commit()
            self.load_commands()
            self.refresh_tree()
    
    def move_down(self):
        cmd = self.get_selected_command()
        if not cmd:
            QMessageBox.information(self, "Move Down", "Please select a command to move.")
            return
        index = self.commands.index(cmd)
        if index < len(self.commands) - 1:
            other = self.commands[index + 1]
            self.cursor.execute("UPDATE commands SET order_index=? WHERE id=?", (other.order_index, cmd.id))
            self.cursor.execute("UPDATE commands SET order_index=? WHERE id=?", (cmd.order_index, other.id))
            self.conn.commit()
            self.load_commands()
            self.refresh_tree()
    
    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = CommandManager()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("An error occurred. Press Enter to exit...")
