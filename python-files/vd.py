import sys, os, json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

CONFIG_DIR = "configs"
AUTOSAVE_FILE = os.path.join(CONFIG_DIR, "autosave.json")

os.makedirs(CONFIG_DIR, exist_ok=True)


class ToggleSwitch(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.search_name = text.lower()
        self.checkbox = QCheckBox()
        self.checkbox.setFixedSize(40, 20)
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 40px;
                height: 20px;
            }
            QCheckBox::indicator:unchecked {
                image: url();
                background-color: #333;
                border-radius: 10px;
            }
            QCheckBox::indicator:checked {
                image: url();
                background-color: #7a3cff;
                border-radius: 10px;
            }
        """)
        self.label = QLabel(text)
        self.label.setStyleSheet("color: #ddd;")
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.checkbox)
        layout.setContentsMargins(5, 2, 5, 2)
        self.setLayout(layout)

    def matches(self, query):
        return query in self.search_name

    def get_state(self):
        return self.checkbox.isChecked()

    def set_state(self, val):
        self.checkbox.setChecked(val)


class SliderWithValue(QWidget):
    def __init__(self, text, min_val, max_val, init_val):
        super().__init__()
        self.search_name = text.lower()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)
        self.label = QLabel(text)
        self.label.setStyleSheet("color: #ddd;")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(min_val, max_val)
        self.slider.setValue(init_val)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #444;
                height: 8px;
                background: #222;
                margin: 0px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #bb66ff;
                border: none;
                width: 14px;
                height: 14px;
                margin: -3px 0;
                border-radius: 7px;
            }
        """)
        self.value_label = QLabel(str(init_val))
        self.value_label.setStyleSheet("color: #bb66ff; font-weight: bold;")
        self.slider.valueChanged.connect(lambda v: self.value_label.setText(str(v)))
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.value_label)
        self.setLayout(layout)

    def matches(self, query):
        return query in self.search_name

    def get_state(self):
        return self.slider.value()

    def set_state(self, val):
        self.slider.setValue(val)


class CheatMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Violence District v5.7 - Fake GUI")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #1e1e1e; font: 13px Arial; color: #ddd;")

        self.all_widgets = {}

        central = QWidget()
        main_layout = QVBoxLayout(central)

        top_bar = QWidget()
        top_bar.setStyleSheet("background-color: #151515; border-bottom: 1px solid #333;")
        top_layout = QHBoxLayout(top_bar)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search functions...")
        self.search.setStyleSheet("""
            QLineEdit {
                background-color: #222;
                border: 1px solid #444;
                padding: 5px;
                color: white;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #7a3cff;
            }
        """)
        self.search.textChanged.connect(self.apply_search)
        top_layout.addWidget(self.search)
        main_layout.addWidget(top_bar, 0)

        main_split = QHBoxLayout()
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        for item in ["Combat", "Player", "Visuals", "Misc", "Configs"]:
            self.sidebar.addItem(item)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #151515;
                border-right: 1px solid #444;
            }
            QListWidget::item {
                padding: 10px;
                color: #aaa;
            }
            QListWidget::item:selected {
                background-color: #333;
                color: white;
            }
        """)
        self.sidebar.currentRowChanged.connect(self.change_tab)
        main_split.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        main_split.addWidget(self.stack, 1)

        self.combat = self.combat_tab()
        self.player = self.player_tab()
        self.visuals = self.visuals_tab()
        self.misc = self.misc_tab()
        self.configs = self.configs_tab()
        self.search_results = QWidget()

        self.stack.addWidget(self.combat)
        self.stack.addWidget(self.player)
        self.stack.addWidget(self.visuals)
        self.stack.addWidget(self.misc)
        self.stack.addWidget(self.configs)
        self.stack.addWidget(self.search_results)

        main_layout.addLayout(main_split, 1)
        self.setCentralWidget(central)

        self.load_config(AUTOSAVE_FILE, silent=True)

    def wrap_group(self, title, widgets):
        group = QGroupBox(title)
        layout = QVBoxLayout()
        layout.setSpacing(5)
        for w in widgets:
            layout.addWidget(w)
            self.all_widgets[w.search_name] = w
        group.setLayout(layout)
        return group

    def combat_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(self.wrap_group("Combat Settings", [
            ToggleSwitch("Flight"),
            ToggleSwitch("Noclip"),
            ToggleSwitch("Auto Weapons")
        ]))
        layout.addWidget(self.wrap_group("Select Weapons", [
            ToggleSwitch("Gun"),
            ToggleSwitch("Flashlight"),
            ToggleSwitch("Sword")
        ]))
        return tab

    def player_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.addWidget(self.wrap_group("Killer", [
            SliderWithValue("Speed Multiplier", 1, 10, 5),
            ToggleSwitch("Disable slider"),
            ToggleSwitch("Anti-Stun"),
            ToggleSwitch("AimBot"),
            ToggleSwitch("Kill all"),
            SliderWithValue("Hitbox Size", 1, 10, 3)
        ]))
        layout.addWidget(self.wrap_group("Survivor", [
            SliderWithValue("Field of View", 20, 120, 75),
            ToggleSwitch("Perfect Generator Repair"),
            ToggleSwitch("Disable mini-games"),
            ToggleSwitch("Invisible"),
            ToggleSwitch("Dash (Q)"),
            SliderWithValue("Speed", 1, 10, 5)
        ]))
        return tab

    def visuals_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(self.wrap_group("Visuals", [
            ToggleSwitch("FullBright"),
            ToggleSwitch("ESP")
        ]))
        layout.addWidget(self.wrap_group("ESP Settings", [
            ToggleSwitch("Generators"),
            ToggleSwitch("Hooks"),
            ToggleSwitch("Players"),
            ToggleSwitch("Gates"),
            ToggleSwitch("Pallet"),
            ToggleSwitch("Vault"),
            ToggleSwitch("Name")
        ]))
        return tab

    def misc_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(self.wrap_group("Keybinds", [
            ToggleSwitch("Teleport to gate"),
            ToggleSwitch("Teleport to nearest pallet"),
            ToggleSwitch("Use shadow clone NO CD"),
            ToggleSwitch("Use parrying Dagger NO CD")
        ]))
        return tab

    def configs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        form = QHBoxLayout()
        self.config_name = QLineEdit()
        self.config_name.setPlaceholderText("Config name")
        form.addWidget(self.config_name)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_config)
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_selected)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_configs)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_selected)

        for b in [save_btn, load_btn, refresh_btn, remove_btn]:
            form.addWidget(b)

        layout.addLayout(form)

        self.config_list = QListWidget()
        layout.addWidget(self.config_list)
        self.refresh_configs()

        tab.setLayout(layout)
        return tab

    def change_tab(self, index):
        if self.search.text().strip():
            return
        self.stack.setCurrentIndex(index)

    def apply_search(self, text):
        query = text.strip().lower()
        if query == "":
            self.stack.setCurrentIndex(self.sidebar.currentRow())
            return
        layout = QVBoxLayout()
        layout.setSpacing(5)
        found = False
        for name, w in self.all_widgets.items():
            if query in name:
                layout.addWidget(w)
                found = True
        if not found:
            lbl = QLabel("No results found")
            lbl.setStyleSheet("color: #888; font-style: italic;")
            layout.addWidget(lbl)
        container = QWidget()
        container.setLayout(layout)
        self.stack.removeWidget(self.search_results)
        self.search_results = container
        self.stack.addWidget(self.search_results)
        self.stack.setCurrentWidget(self.search_results)

    def get_all_states(self):
        data = {}
        for name, w in self.all_widgets.items():
            if isinstance(w, ToggleSwitch):
                data[name] = w.get_state()
            elif isinstance(w, SliderWithValue):
                data[name] = w.get_state()
        return data

    def apply_states(self, data):
        for name, val in data.items():
            if name in self.all_widgets:
                w = self.all_widgets[name]
                if isinstance(w, ToggleSwitch):
                    w.set_state(val)
                elif isinstance(w, SliderWithValue):
                    w.set_state(val)

    def config_path(self, name):
        return os.path.join(CONFIG_DIR, f"{name}.json")

    def save_config(self):
        name = self.config_name.text().strip()
        if not name:
            return
        with open(self.config_path(name), "w") as f:
            json.dump(self.get_all_states(), f, indent=2)
        self.refresh_configs()

    def load_config(self, path, silent=False):
        if not os.path.exists(path):
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
            self.apply_states(data)
            if not silent:
                QMessageBox.information(self, "Success", "Config loaded")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed: {e}")

    def load_selected(self):
        item = self.config_list.currentItem()
        if not item:
            return
        self.load_config(self.config_path(item.text()))

    def refresh_configs(self):
        self.config_list.clear()
        for f in os.listdir(CONFIG_DIR):
            if f.endswith(".json"):
                self.config_list.addItem(f[:-5])

    def remove_selected(self):
        item = self.config_list.currentItem()
        if not item:
            return
        os.remove(self.config_path(item.text()))
        self.refresh_configs()

    def closeEvent(self, event):
        with open(AUTOSAVE_FILE, "w") as f:
            json.dump(self.get_all_states(), f, indent=2)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CheatMenu()
    window.show()
    sys.exit(app.exec_())