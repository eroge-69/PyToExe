import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QComboBox, QLineEdit, QLabel, QHeaderView, QSizePolicy, 
    QDialog, QSlider, QSpinBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QBrush, QKeySequence


class InitiativeViewer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Просмотр инициативы")
        self.setGeometry(200, 200, 300, 600)
        self.scale_factor = 1.0
        self.parent = parent
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Round info
        round_layout = QHBoxLayout()
        round_label = QLabel("Раунд:")
        round_label.setFont(QFont("Arial", 16, QFont.Bold))
        round_layout.addWidget(round_label)
        
        self.round_label = QLabel("1")
        self.round_label.setFont(QFont("Arial", 16, QFont.Bold))
        round_layout.addWidget(self.round_label)
        round_layout.addStretch()
        
        main_layout.addLayout(round_layout)
        
        # Initiative table
        self.initiative_table = QTableWidget()
        self.initiative_table.setColumnCount(1)
        self.initiative_table.setHorizontalHeaderLabels(["Имя персонажа"])
        self.initiative_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.initiative_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        main_layout.addWidget(self.initiative_table)
        self.setLayout(main_layout)
    
    def apply_zoom(self, scale_percent):
        self.scale_factor = scale_percent / 100.0
        
        # Update font sizes
        base_font_size = 10
        self.round_label.setFont(QFont("Arial", int(base_font_size * self.scale_factor * 1.6), QFont.Bold))
        
        # Update table font
        table_font = QFont("Arial", int(base_font_size * self.scale_factor))
        self.initiative_table.setFont(table_font)
        self.initiative_table.horizontalHeader().setFont(QFont("Arial", int(base_font_size * self.scale_factor), QFont.Bold))
        
        # Update row heights
        self.initiative_table.verticalHeader().setDefaultSectionSize(int(24 * self.scale_factor))
        self.initiative_table.resizeRowsToContents()


class DnDInitiativeTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DnD Initiative Tracker")
        self.setGeometry(100, 100, 1200, 800)

        self.current_round = 1
        self.current_active_row = 0
        self.teams = {}
        self.current_team = ""
        self.data_file = "dnd_teams.json"
        self.viewer_window = None
        self.viewer_zoom = 100  # Default zoom 100%

        self.load_teams()
        self.init_ui()
        self.setup_shortcuts()

    def load_teams(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.teams = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.teams = {}
        else:
            self.teams = {}

    def save_teams_to_file(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.teams, f, ensure_ascii=False, indent=4)

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Left side: Initiative and Creatures
        left_layout = QVBoxLayout()

        # Initiative Table
        self.initiative_label = QLabel("Таблица Инициативы")
        self.initiative_label.setFont(QFont("Arial", 14, QFont.Bold))
        left_layout.addWidget(self.initiative_label)

        # Team selection
        team_layout = QHBoxLayout()
        self.team_combo = QComboBox()
        self.team_combo.setEditable(True)
        self.team_combo.setPlaceholderText("Название команды")
        self.team_combo.currentTextChanged.connect(self.change_team)
        
        for team_name in self.teams.keys():
            self.team_combo.addItem(team_name)
            
        team_layout.addWidget(self.team_combo, 4)

        self.save_team_btn = QPushButton("Сохранить команду")
        self.save_team_btn.clicked.connect(self.save_team)
        team_layout.addWidget(self.save_team_btn, 2)

        self.delete_team_btn = QPushButton("Удалить команду")
        self.delete_team_btn.clicked.connect(self.delete_team)
        team_layout.addWidget(self.delete_team_btn, 2)

        self.sort_btn = QPushButton("Порядок!")
        self.sort_btn.clicked.connect(self.sort_initiative)
        team_layout.addWidget(self.sort_btn, 2)

        self.viewer_btn = QPushButton("Открыть просмотр")
        self.viewer_btn.clicked.connect(self.open_viewer)
        team_layout.addWidget(self.viewer_btn, 2)

        left_layout.addLayout(team_layout)

        self.initiative_table = QTableWidget()
        self.initiative_table.setColumnCount(2)
        self.initiative_table.setHorizontalHeaderLabels(["Результат броска кубика", "Имя персонажа"])
        self.initiative_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.initiative_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        left_layout.addWidget(self.initiative_table)

        # Add/Remove buttons for initiative
        initiative_btn_layout = QHBoxLayout()
        self.add_initiative_btn = QPushButton("Добавить")
        self.add_initiative_btn.clicked.connect(self.add_initiative_row)
        initiative_btn_layout.addWidget(self.add_initiative_btn)
        
        self.delete_initiative_btn = QPushButton("Удалить выбранное")
        self.delete_initiative_btn.clicked.connect(self.delete_selected_initiative_row)
        initiative_btn_layout.addWidget(self.delete_initiative_btn)
        
        left_layout.addLayout(initiative_btn_layout)

        # Creatures Table
        self.creatures_label = QLabel("Существа")
        self.creatures_label.setFont(QFont("Arial", 14, QFont.Bold))
        left_layout.addWidget(self.creatures_label)

        self.creatures_table = QTableWidget()
        self.creatures_table.setColumnCount(10)
        self.creatures_table.setHorizontalHeaderLabels([
            "Название", "Описание", "Жизни", "Броня", "Оставшиеся жизни", 
            "Нанесенный урон", "Урон", "Ударить", "Лечение", "Лечить"
        ])
        self.creatures_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        left_layout.addWidget(self.creatures_table)

        # Add/Duplicate/Remove buttons for creatures
        creatures_btn_layout = QHBoxLayout()
        self.add_creature_btn = QPushButton("Добавить")
        self.add_creature_btn.clicked.connect(self.add_creature_row)
        creatures_btn_layout.addWidget(self.add_creature_btn)

        self.duplicate_creature_btn = QPushButton("Дублировать выбранное")
        self.duplicate_creature_btn.clicked.connect(self.duplicate_selected_creature_row)
        creatures_btn_layout.addWidget(self.duplicate_creature_btn)
        
        self.delete_creature_btn = QPushButton("Удалить выбранное")
        self.delete_creature_btn.clicked.connect(self.delete_selected_creature_row)
        creatures_btn_layout.addWidget(self.delete_creature_btn)
        
        left_layout.addLayout(creatures_btn_layout)

        # Viewer zoom control
        zoom_layout = QHBoxLayout()
        zoom_label = QLabel("Масштаб просмотра:")
        zoom_layout.addWidget(zoom_label)
        
        self.zoom_spin = QSpinBox()
        self.zoom_spin.setRange(50, 300)
        self.zoom_spin.setValue(100)
        self.zoom_spin.setSuffix("%")
        self.zoom_spin.valueChanged.connect(self.update_viewer_zoom)
        zoom_layout.addWidget(self.zoom_spin)
        
        left_layout.addLayout(zoom_layout)

        # Right side: Next Turn and Reset buttons
        right_layout = QVBoxLayout()
        
        # Round label
        self.round_label = QLabel(f"Раунд: {self.current_round}")
        self.round_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.round_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.round_label)
        
        # Big Next Turn button
        self.next_turn_btn = QPushButton("Следующий ход (Enter)")
        self.next_turn_btn.setFont(QFont("Arial", 14, QFont.Bold))
        self.next_turn_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.next_turn_btn.clicked.connect(self.next_turn)
        right_layout.addWidget(self.next_turn_btn, 1)
        
        # Reset button
        self.reset_btn = QPushButton("Сброс")
        self.reset_btn.clicked.connect(self.reset_tracker)
        right_layout.addWidget(self.reset_btn)

        main_layout.addLayout(left_layout, 4)
        main_layout.addLayout(right_layout, 1)

        self.setCentralWidget(main_widget)

        # Add initial rows
        self.add_initiative_row()
        self.add_creature_row()

        # Connect signals
        self.creatures_table.cellChanged.connect(self.update_creature_stats)

    def update_viewer_zoom(self, value):
        self.viewer_zoom = value
        if self.viewer_window:
            self.viewer_window.apply_zoom(value)

    def open_viewer(self):
        if not self.viewer_window:
            self.viewer_window = InitiativeViewer(self)
            self.viewer_window.apply_zoom(self.viewer_zoom)
            self.viewer_window.show()
        else:
            self.viewer_window.show()
        
        self.update_viewer()

    def update_viewer(self):
        if not self.viewer_window:
            return
            
        self.viewer_window.initiative_table.setRowCount(self.initiative_table.rowCount())
        self.viewer_window.round_label.setText(str(self.current_round))
        
        for row in range(self.initiative_table.rowCount()):
            name_item = self.initiative_table.item(row, 1)
            if name_item:
                new_item = QTableWidgetItem(name_item.text())
                new_item.setFlags(new_item.flags() ^ Qt.ItemIsEditable)
                
                # Копируем оформление
                new_item.setBackground(name_item.background())
                new_item.setForeground(name_item.foreground())
                
                self.viewer_window.initiative_table.setItem(row, 0, new_item)
        
        # Выделяем текущий ход
        if 0 <= self.current_active_row < self.viewer_window.initiative_table.rowCount():
            for row in range(self.viewer_window.initiative_table.rowCount()):
                item = self.viewer_window.initiative_table.item(row, 0)
                if item:
                    if row == self.current_active_row:
                        item.setBackground(QColor(255, 255, 0))
                    else:
                        if item.text() == "Враги":
                            item.setBackground(QColor(255, 200, 200))
                        else:
                            item.setBackground(QColor(255, 255, 255))
        
        # Применяем текущий масштаб
        self.viewer_window.apply_zoom(self.viewer_zoom)

    def setup_shortcuts(self):
        self.next_turn_shortcut = QKeySequence(Qt.Key_Return)
        self.next_turn_btn.setShortcut(self.next_turn_shortcut)

    def save_team(self):
        team_name = self.team_combo.currentText()
        if not team_name:
            return

        initiative_data = []
        for row in range(self.initiative_table.rowCount()):
            roll_item = self.initiative_table.item(row, 0)
            name_item = self.initiative_table.item(row, 1)
            if roll_item and name_item:
                initiative_data.append({
                    "roll": roll_item.text(),
                    "name": name_item.text()
                })

        self.teams[team_name] = initiative_data
        self.save_teams_to_file()

        if self.team_combo.findText(team_name) == -1:
            self.team_combo.addItem(team_name)

    def delete_team(self):
        team_name = self.team_combo.currentText()
        if not team_name or team_name not in self.teams:
            return
            
        del self.teams[team_name]
        self.save_teams_to_file()
        
        index = self.team_combo.findText(team_name)
        if index >= 0:
            self.team_combo.removeItem(index)

    def change_team(self, team_name):
        if not team_name or team_name not in self.teams:
            return

        self.current_team = team_name
        self.initiative_table.setRowCount(0)

        for member in self.teams[team_name]:
            row = self.initiative_table.rowCount()
            self.initiative_table.insertRow(row)
            self.initiative_table.setItem(row, 0, QTableWidgetItem(member["roll"]))
            self.initiative_table.setItem(row, 1, QTableWidgetItem(member["name"]))

        # Add "Enemies" row with red background
        row = self.initiative_table.rowCount()
        self.initiative_table.insertRow(row)
        self.initiative_table.setItem(row, 0, QTableWidgetItem("0"))
        self.initiative_table.setItem(row, 1, QTableWidgetItem("Враги"))
        
        for col in range(2):
            item = self.initiative_table.item(row, col)
            if item:
                item.setBackground(QColor(255, 200, 200))
                item.setForeground(QBrush(QColor(0, 0, 0)))

    def add_initiative_row(self):
        row = self.initiative_table.rowCount()
        self.initiative_table.insertRow(row)
        self.initiative_table.setItem(row, 0, QTableWidgetItem(""))
        self.initiative_table.setItem(row, 1, QTableWidgetItem(""))

    def delete_initiative_row(self, row):
        self.initiative_table.removeRow(row)
        if self.current_active_row >= row:
            self.current_active_row = max(0, self.current_active_row - 1)
            self.highlight_active_row(self.current_active_row)
        
        self.update_viewer()

    def delete_selected_initiative_row(self):
        selected = self.initiative_table.selectedItems()
        if not selected:
            return
            
        rows = set(item.row() for item in selected)
        for row in sorted(rows, reverse=True):
            self.delete_initiative_row(row)

    def sort_initiative(self):
        # Clear current highlight
        self.clear_row_highlight(self.current_active_row)
        self.current_active_row = 0

        # Collect all rows data including enemies
        rows_data = []
        for row in range(self.initiative_table.rowCount()):
            roll_item = self.initiative_table.item(row, 0)
            name_item = self.initiative_table.item(row, 1)
            if roll_item and name_item:
                try:
                    roll = int(roll_item.text()) if roll_item.text() else 0
                except ValueError:
                    roll = 0
                rows_data.append((roll, name_item.text(), row, name_item.text() == "Враги"))

        # Sort by roll in descending order (enemies will sort with others)
        rows_data.sort(reverse=True, key=lambda x: x[0])

        # Clear table and repopulate with sorted data
        self.initiative_table.setRowCount(0)
        
        # Add sorted rows
        for roll, name, _, is_enemy in rows_data:
            row = self.initiative_table.rowCount()
            self.initiative_table.insertRow(row)
            self.initiative_table.setItem(row, 0, QTableWidgetItem(str(roll)))
            self.initiative_table.setItem(row, 1, QTableWidgetItem(name))
            
            # Apply red background for enemies
            if is_enemy:
                for col in range(2):
                    item = self.initiative_table.item(row, col)
                    if item:
                        item.setBackground(QColor(255, 200, 200))
                        item.setForeground(QBrush(QColor(0, 0, 0)))

        # Highlight first row
        self.highlight_active_row(0)
        self.update_viewer()

    def next_turn(self):
        if self.initiative_table.rowCount() == 0:
            return

        self.clear_row_highlight(self.current_active_row)

        self.current_active_row += 1
        if self.current_active_row >= self.initiative_table.rowCount():
            self.current_active_row = 0
            self.current_round += 1
            self.round_label.setText(f"Раунд: {self.current_round}")

        self.highlight_active_row(self.current_active_row)
        self.update_viewer()

    def highlight_active_row(self, row):
        for col in range(self.initiative_table.columnCount()):
            item = self.initiative_table.item(row, col)
            if item:
                item.setBackground(QColor(255, 255, 0))
        
        self.update_viewer()

    def clear_row_highlight(self, row):
        for col in range(self.initiative_table.columnCount()):
            item = self.initiative_table.item(row, col)
            if item:
                if item.text() == "Враги":
                    item.setBackground(QColor(255, 200, 200))
                else:
                    item.setBackground(QColor(255, 255, 255))
        
        self.update_viewer()

    def add_creature_row(self):
        row = self.creatures_table.rowCount()
        self.creatures_table.insertRow(row)
        
        # Name
        name_item = QTableWidgetItem("")
        self.creatures_table.setItem(row, 0, name_item)
        
        # Description
        desc_item = QTableWidgetItem("")
        self.creatures_table.setItem(row, 1, desc_item)
        
        # HP
        hp_item = QTableWidgetItem("0")
        self.creatures_table.setItem(row, 2, hp_item)
        
        # Armor
        armor_item = QTableWidgetItem("0")
        self.creatures_table.setItem(row, 3, armor_item)
        
        # Current HP (readonly)
        current_hp_item = QTableWidgetItem("0")
        current_hp_item.setFlags(current_hp_item.flags() ^ Qt.ItemIsEditable)
        self.creatures_table.setItem(row, 4, current_hp_item)
        
        # Damage taken
        damage_item = QTableWidgetItem("0")
        damage_item.setFlags(damage_item.flags() ^ Qt.ItemIsEditable)
        self.creatures_table.setItem(row, 5, damage_item)
        
        # Damage input
        damage_input = QTableWidgetItem("")
        self.creatures_table.setItem(row, 6, damage_input)
        
        # Attack button
        attack_btn = QPushButton("Ударить")
        attack_btn.clicked.connect(lambda _, r=row: self.apply_damage(r))
        self.creatures_table.setCellWidget(row, 7, attack_btn)
        
        # Heal input
        heal_input = QTableWidgetItem("")
        self.creatures_table.setItem(row, 8, heal_input)
        
        # Heal button
        heal_btn = QPushButton("Лечить")
        heal_btn.clicked.connect(lambda _, r=row: self.apply_heal(r))
        self.creatures_table.setCellWidget(row, 9, heal_btn)

    def duplicate_selected_creature_row(self):
        selected_row = self.creatures_table.currentRow()
        if selected_row == -1:
            return
            
        row = self.creatures_table.rowCount()
        self.creatures_table.insertRow(row)
        
        for col in range(6):
            source_item = self.creatures_table.item(selected_row, col)
            if source_item:
                new_item = QTableWidgetItem(source_item.text())
                if col in [4, 5]:
                    new_item.setFlags(new_item.flags() ^ Qt.ItemIsEditable)
                self.creatures_table.setItem(row, col, new_item)
        
        damage_input = QTableWidgetItem("")
        self.creatures_table.setItem(row, 6, damage_input)
        
        attack_btn = QPushButton("Ударить")
        attack_btn.clicked.connect(lambda _, r=row: self.apply_damage(r))
        self.creatures_table.setCellWidget(row, 7, attack_btn)
        
        heal_input = QTableWidgetItem("")
        self.creatures_table.setItem(row, 8, heal_input)
        
        heal_btn = QPushButton("Лечить")
        heal_btn.clicked.connect(lambda _, r=row: self.apply_heal(r))
        self.creatures_table.setCellWidget(row, 9, heal_btn)

    def delete_selected_creature_row(self):
        selected_row = self.creatures_table.currentRow()
        if selected_row != -1:
            self.creatures_table.removeRow(selected_row)

    def update_creature_stats(self, row, column):
        if column in (2, 5):
            hp_item = self.creatures_table.item(row, 2)
            damage_item = self.creatures_table.item(row, 5)
            
            try:
                hp = int(hp_item.text()) if hp_item and hp_item.text() else 0
                damage = int(damage_item.text()) if damage_item and damage_item.text() else 0
                current_hp = max(0, hp - damage)
                
                current_hp_item = self.creatures_table.item(row, 4)
                if current_hp_item:
                    current_hp_item.setText(str(current_hp))
                    
                    if current_hp <= 0:
                        for col in range(self.creatures_table.columnCount()):
                            item = self.creatures_table.item(row, col)
                            if item:
                                item.setBackground(QColor(255, 200, 200))
                                item.setForeground(QBrush(QColor(0, 0, 0)))
                    else:
                        for col in range(self.creatures_table.columnCount()):
                            item = self.creatures_table.item(row, col)
                            if item:
                                item.setBackground(QColor(255, 255, 255))
                                item.setForeground(QBrush(QColor(0, 0, 0)))
            except ValueError:
                pass

    def apply_damage(self, row):
        damage_item = self.creatures_table.item(row, 6)
        damage_taken_item = self.creatures_table.item(row, 5)
        
        if damage_item and damage_taken_item:
            try:
                damage = int(damage_item.text()) if damage_item.text() else 0
                current_damage = int(damage_taken_item.text()) if damage_taken_item.text() else 0
                damage_taken_item.setText(str(current_damage + damage))
                damage_item.setText("")
                self.update_creature_stats(row, 5)
            except ValueError:
                pass

    def apply_heal(self, row):
        heal_item = self.creatures_table.item(row, 8)
        damage_taken_item = self.creatures_table.item(row, 5)
        
        if heal_item and damage_taken_item:
            try:
                heal = int(heal_item.text()) if heal_item.text() else 0
                current_damage = int(damage_taken_item.text()) if damage_taken_item.text() else 0
                new_damage = max(0, current_damage - heal)
                damage_taken_item.setText(str(new_damage))
                heal_item.setText("")
                self.update_creature_stats(row, 5)
            except ValueError:
                pass

    def reset_tracker(self):
        self.current_round = 1
        self.round_label.setText(f"Раунд: {self.current_round}")
        self.current_active_row = 0
        self.highlight_active_row(0)

        for row in range(self.creatures_table.rowCount()):
            damage_taken_item = self.creatures_table.item(row, 5)
            if damage_taken_item:
                damage_taken_item.setText("0")
                self.update_creature_stats(row, 5)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DnDInitiativeTracker()
    window.show()
    sys.exit(app.exec_())