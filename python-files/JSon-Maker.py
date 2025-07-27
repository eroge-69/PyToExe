import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QComboBox, QFileDialog, QLabel,
    QLineEdit, QMessageBox, QGroupBox, QFormLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class JsonTreeEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📂 JSON Tree Editor by Roni (Auto Save Enabled)")
        self.setGeometry(200, 100, 850, 620)
        self.data = {}
        self.node_map = {}
        self.current_file_path = None  # 🆕 To remember loaded file

        # UI Elements
        self.load_btn = QPushButton("📁 Load JSON")
        self.save_btn = QPushButton("💾 Save JSON")
        self.save_btn.setEnabled(False)

        self.name_dropdown = QComboBox()
        self.name_dropdown.setEnabled(False)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter new child name")

        self.rename_input = QLineEdit()
        self.rename_input.setPlaceholderText("Rename selected node to...")

        self.add_btn = QPushButton("➕ Add Child")
        self.add_btn.setEnabled(False)

        self.rename_btn = QPushButton("✏️ Rename Node")
        self.rename_btn.setEnabled(False)

        self.delete_btn = QPushButton("🗑️ Delete Selected")
        self.delete_btn.setEnabled(False)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setFont(QFont("Courier", 10))

        self.set_button_styles()
        self.init_ui()

        # Connections
        self.load_btn.clicked.connect(self.load_json)
        self.save_btn.clicked.connect(self.save_json)
        self.add_btn.clicked.connect(self.add_child)
        self.rename_btn.clicked.connect(self.rename_node)
        self.delete_btn.clicked.connect(self.delete_name)
        self.name_dropdown.currentIndexChanged.connect(self.update_selection_preview)

    def set_button_styles(self):
        btn_style = """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border-radius: 6px;
            padding: 6px 12px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #388E3C;
        }
        QPushButton:pressed {
            background-color: #1B5E20;
        }
        """
        for btn in [self.load_btn, self.save_btn, self.add_btn, self.rename_btn, self.delete_btn]:
            btn.setStyleSheet(btn_style)

    def init_ui(self):
        layout = QVBoxLayout()

        file_group = QGroupBox("File Controls")
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.load_btn)
        file_layout.addWidget(self.save_btn)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        edit_group = QGroupBox("Edit Tree Nodes")
        edit_layout = QFormLayout()
        edit_layout.addRow(QLabel("Select a node:"), self.name_dropdown)
        edit_layout.addRow(QLabel("New child name:"), self.name_input)
        edit_layout.addRow(QLabel("Rename to:"), self.rename_input)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.rename_btn)
        btn_layout.addWidget(self.delete_btn)
        edit_layout.addRow(btn_layout)
        edit_group.setLayout(edit_layout)
        layout.addWidget(edit_group)

        preview_group = QGroupBox("Selected Node's Children Preview")
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(self.preview)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        self.setLayout(layout)

    def load_json(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                self.current_file_path = file_path  # 🆕 remember the file
                self.populate_dropdown()
                self.update_selection_preview()
                self.save_btn.setEnabled(True)
                self.add_btn.setEnabled(True)
                self.rename_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                self.name_dropdown.setEnabled(True)
                QMessageBox.information(self, "✅ Success", "JSON loaded successfully.")
            except Exception as e:
                QMessageBox.critical(self, "❌ Error", f"Failed to load JSON:\n{e}")

    def save_json(self):  # Manual save (still available)
        file_path, _ = QFileDialog.getSaveFileName(self, "Save JSON File", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "✅ Saved", "JSON saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "❌ Error", f"Failed to save JSON:\n{e}")

    def auto_save(self):  # 🆕 Auto Save to current file
        if self.current_file_path:
            try:
                with open(self.current_file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                QMessageBox.critical(self, "❌ Auto Save Failed", f"Could not auto save:\n{e}")

    def populate_dropdown(self):
        self.name_dropdown.clear()
        self.node_map = {}

        def recurse_names(node):
            if isinstance(node, dict):
                name = node.get("name")
                if name:
                    self.node_map[name] = node
                for child in node.get("children", []):
                    recurse_names(child)

        recurse_names(self.data)
        self.name_dropdown.addItems(self.node_map.keys())

    def find_node_by_name(self, name, node):
        if node.get("name") == name:
            return node
        for child in node.get("children", []):
            result = self.find_node_by_name(name, child)
            if result:
                return result
        return None

    def update_selection_preview(self):
        selected_name = self.name_dropdown.currentText()
        if not selected_name:
            self.preview.clear()
            return

        selected_node = self.find_node_by_name(selected_name, self.data)
        if not selected_node:
            self.preview.setPlainText("❌ Node not found.")
            return

        children = selected_node.get("children", [])

        if not children:
            self.preview.setPlainText("⚠️ No children found for this node.")
        else:
            flat_children = [{"name": child.get("name", "Unnamed")} for child in children]
            preview_json = json.dumps(flat_children, indent=2, ensure_ascii=False)
            self.preview.setPlainText(preview_json)

    def add_child(self):
        child_name = self.name_input.text().strip()
        if not child_name:
            QMessageBox.warning(self, "⚠️ Input Required", "Please enter a child name.")
            return

        parent_name = self.name_dropdown.currentText()
        parent_node = self.find_node_by_name(parent_name, self.data)

        if parent_node is not None:
            if "children" not in parent_node:
                parent_node["children"] = []
            parent_node["children"].append({"name": child_name})
            self.name_input.clear()
            self.populate_dropdown()
            self.name_dropdown.setCurrentText(parent_name)
            self.update_selection_preview()
            self.auto_save()  # 🆕
        else:
            QMessageBox.warning(self, "⚠️ Invalid Selection", "Parent node not found.")

    def rename_node(self):
        selected_name = self.name_dropdown.currentText()
        new_name = self.rename_input.text().strip()
        if not new_name:
            QMessageBox.warning(self, "⚠️ Input Required", "Please enter a new name.")
            return

        node = self.find_node_by_name(selected_name, self.data)
        if node:
            node["name"] = new_name
            self.rename_input.clear()
            self.populate_dropdown()
            self.name_dropdown.setCurrentText(new_name)
            self.update_selection_preview()
            self.auto_save()  # 🆕
        else:
            QMessageBox.warning(self, "❌ Error", "Node not found.")

    def delete_name(self):
        target_name = self.name_dropdown.currentText()
        if not target_name:
            return

        def recurse_delete(node, name):
            if "children" in node:
                node["children"] = [c for c in node["children"] if c.get("name") != name]
                for c in node["children"]:
                    recurse_delete(c, name)

        if self.data.get("name") == target_name:
            QMessageBox.warning(self, "⚠️ Protected", "Root node cannot be deleted.")
            return

        recurse_delete(self.data, target_name)
        self.populate_dropdown()
        self.update_selection_preview()
        self.auto_save()  # 🆕


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = JsonTreeEditor()
    window.show()
    sys.exit(app.exec_())
