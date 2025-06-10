import sys
import random
from enum import Enum

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QDialog, QLabel,
    QComboBox, QGridLayout, QMessageBox, QHBoxLayout, QGroupBox, QRadioButton
)
from PyQt5.QtCore import Qt, QTimer

# Константы для игры
BOARD_SIZE = 7               # Размер игрового поля
WIN_LENGTH = 4               # Количество значков подряд для победы

# Перечисление для уровней сложности
class Difficulty(Enum):
    EASY = "Лёгкая"
    MEDIUM = "Средняя"
    HARD = "Сложная"

# Диалог настроек, включая правила и выбор сложности
class SettingsDialog(QDialog):
    def __init__(self, parent=None, selected_difficulty=Difficulty.EASY):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        layout = QVBoxLayout()

        # Заголовок
        header = QLabel("Правила игры")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            background: #ff5b63;
            color: #23262f;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            font-size: 28px;
            font-weight: bold;
            padding: 12px 0 8px 0;
        """)

        # Описание правил игры
        rules = QLabel(
            f"1. Игровое поле: Игра проходит на квадратном поле размером {BOARD_SIZE}x{BOARD_SIZE} клеток.\n"
            "2. Игроки: Играют два игрока, один из которых использует символ 'X', а другой — символ 'O'.\n"
            f"3. Если один из игроков выстраивает линию из {WIN_LENGTH} своих символов, он объявляется победителем.\n"
            f"4. Если все {BOARD_SIZE * BOARD_SIZE} клеток заполнены, а ни один из игроков не выстроил линию из {WIN_LENGTH} символов, игра заканчивается вничью.\n"
            f"5. После каждого хода проверяется, есть ли у текущего игрока линия из {WIN_LENGTH} символов подряд (горизонтально, вертикально или диагонально)."
        )
        rules.setWordWrap(True)
        rules.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        rules.setStyleSheet("""
            background: #59dd95;
            color: #23262f;
            border-bottom-left-radius: 12px;
            border-bottom-right-radius: 12px;
            font-size: 18px;
            font-weight: bold;
            padding: 18px 12px 18px 12px;
        """)

        layout.addWidget(header)
        layout.addWidget(rules)

        # Выбор сложности бота
        difficulty_layout = QHBoxLayout()
        difficulty_layout.addWidget(QLabel("Сложность бота:"))

        self.difficulty = QComboBox()
        for d in Difficulty:
            self.difficulty.addItem(d.value)
        # Установить выбранную сложность
        self.difficulty.setCurrentText(selected_difficulty.value)
        difficulty_layout.addWidget(self.difficulty)

        # Метка для отображения выбранной сложности
        self.selected_difficulty_label = QLabel(f"Выбранная сложность: {selected_difficulty.value}")
        difficulty_layout.addWidget(self.selected_difficulty_label)

        self.difficulty.currentIndexChanged.connect(self.update_selected_difficulty)

        # Кнопка для применения выбранной сложности
        self.select_button = QPushButton("Выбрать сложность")
        self.select_button.clicked.connect(self.accept)
        difficulty_layout.addWidget(self.select_button)

        layout.addLayout(difficulty_layout)
        self.setLayout(layout)

    def update_selected_difficulty(self):
        # Обновить текст метки при изменении сложности
        self.selected_difficulty_label.setText(f"Выбранная сложность: {self.difficulty.currentText()}")

# Класс с логикой игры "Крестики-нолики 7x7"
class TicTacToe7x7:
    def __init__(self):
        self.board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = 'X'
        self.game_over = False
        self.bot_mode = False
        self.bot_difficulty = Difficulty.MEDIUM
        self.reset()

    def reset(self):
        # Сброс игрового поля и параметров игры
        self.board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = 'X'
        self.game_over = False

    def make_move(self, row, col):
        # Сделать ход, если возможно
        if self.game_over or self.board[row][col] != '':
            return False, None

        self.board[row][col] = self.current_player
        winner = self.check_winner()

        if winner:
            self.game_over = True
            return True, f"Игрок {winner} победил!"
        elif self.is_board_full():
            self.game_over = True
            return True, "Ничья!"
        else:
            self.current_player = 'O' if self.current_player == 'X' else 'X'
            return True, None

    def check_winner(self):
        # Проверка строк
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE - WIN_LENGTH + 1):
                if self.board[row][col] != '' and all(self.board[row][col + k] == self.board[row][col] for k in range(WIN_LENGTH)):
                    return self.board[row][col]
        # Проверка столбцов
        for col in range(BOARD_SIZE):
            for row in range(BOARD_SIZE - WIN_LENGTH + 1):
                if self.board[row][col] != '' and all(self.board[row + k][col] == self.board[row][col] for k in range(WIN_LENGTH)):
                    return self.board[row][col]
        # Проверка диагоналей (слева направо)
        for row in range(BOARD_SIZE - WIN_LENGTH + 1):
            for col in range(BOARD_SIZE - WIN_LENGTH + 1):
                if self.board[row][col] != '' and all(self.board[row + k][col + k] == self.board[row][col] for k in range(WIN_LENGTH)):
                    return self.board[row][col]
        # Проверка диагоналей (справа налево)
        for row in range(BOARD_SIZE - WIN_LENGTH + 1):
            for col in range(WIN_LENGTH - 1, BOARD_SIZE):
                if self.board[row][col] != '' and all(self.board[row + k][col - k] == self.board[row][col] for k in range(WIN_LENGTH)):
                    return self.board[row][col]
        return None

    def is_board_full(self):
        # Проверить, заполнено ли всё поле
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == '':
                    return False
        return True

    def get_bot_move(self):
        # Получить ход бота в зависимости от сложности
        if self.bot_difficulty == Difficulty.EASY:
            return self.get_random_move()
        elif self.bot_difficulty == Difficulty.MEDIUM:
            # 50% на случайный ход, 50% на умный ход
            if random.random() < 0.5:
                return self.get_random_move()
            else:
                return self.get_smart_move()
        else:  # Сложная
            # 20% на случайный ход, 80% на умный ход
            if random.random() < 0.2:
                return self.get_random_move()
            else:
                return self.get_smart_move()

    def get_random_move(self):
        # Случайный свободный ход
        empty_cells = [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if self.board[i][j] == '']
        return random.choice(empty_cells) if empty_cells else (0, 0)

    def get_smart_move(self):
        # 1. Проверяем, может ли бот выиграть следующим ходом
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j] == '':
                    self.board[i][j] = 'O'
                    if self.check_winner() == 'O':
                        self.board[i][j] = ''
                        return i, j
                    self.board[i][j] = ''
        # 2. Проверяем, может ли игрок выиграть следующим ходом, блокируем
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j] == '':
                    self.board[i][j] = 'X'
                    if self.check_winner() == 'X':
                        self.board[i][j] = ''
                        return i, j
                    self.board[i][j] = ''
        # 3. Пытаемся занять центр
        center = BOARD_SIZE // 2
        if self.board[center][center] == '':
            return center, center
        # 4. Пытаемся занять углы
        corners = [(0, 0), (0, BOARD_SIZE-1), (BOARD_SIZE-1, 0), (BOARD_SIZE-1, BOARD_SIZE-1)]
        random.shuffle(corners)
        for i, j in corners:
            if self.board[i][j] == '':
                return i, j
        # 5. Случайный ход
        return self.get_random_move()

# Виджет с игровым полем
class GameGrid(QWidget):
    def __init__(self, game_logic, main_window):
        super().__init__()

        grid_size = 600
        btn_size = 60 # grid_size // BOARD_SIZE
        self.setFixedSize(grid_size, grid_size)

        # Фоновая сетка
        self.background = QLabel(self)
        pixmap = QPixmap("grid.PNG")
        self.background.setPixmap(pixmap.scaled(grid_size, grid_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.background.setGeometry(0, 0, grid_size, grid_size)
        self.background.lower()

        self.game_logic = game_logic
        self.main_window = main_window

        self.buttons = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 20, 0, 15)

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                btn = QPushButton("")
                btn.setFixedSize(btn_size, btn_size)
                btn.clicked.connect(lambda _, x=i, y=j: self.handle_click(x, y))
                btn.setStyleSheet(
                    "background: transparent; border: none; font-size: 28px; color: white;"
                )
                self.buttons[i][j] = btn
                layout.addWidget(btn, i, j)
        self.setLayout(layout)

    def handle_click(self, row, col):
        # Обработка клика по клетке поля
        if self.game_logic.game_over or (self.game_logic.bot_mode and self.game_logic.current_player == 'O'):
            return

        success, message = self.game_logic.make_move(row, col)
        if success:
            self.buttons[row][col].setText(self.game_logic.board[row][col])
            self.buttons[row][col].setEnabled(False)

            if message:
                QMessageBox.information(self, "Конец игры", message)
                self.disable_all()
            elif self.game_logic.bot_mode and self.game_logic.current_player == 'O' and not self.game_logic.game_over:
                QTimer.singleShot(500, self.make_bot_move)  # Задержка для видимости хода

    def make_bot_move(self):
        # Ход бота
        if self.game_logic.game_over:
            return

        row, col = self.game_logic.get_bot_move()
        success, message = self.game_logic.make_move(row, col)
        if success:
            self.buttons[row][col].setText(self.game_logic.board[row][col])
            self.buttons[row][col].setEnabled(False)

            if message:
                QMessageBox.information(self, "Конец игры", message)
                self.disable_all()

    def reset_board(self):
        # Сброс поля в начальное состояние
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.buttons[i][j].setText("")
                self.buttons[i][j].setEnabled(True)

    def disable_all(self):
        # Заблокировать все кнопки поля
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.buttons[i][j].setEnabled(False)

# Фабрика для создания стилизованных кнопок управления
def create_styled_button(text, gradient, text_color="#23262f"):
    btn = QPushButton(text)
    btn.setStyleSheet(f"""
        QPushButton {{
            font-size: 28px;
            font-weight: bold;
            background: {gradient};
            color: {text_color};
            border: none;
            border-radius: 12px;
            min-height: 54px;
            margin: 0 8px;
        }}
        QPushButton:hover {{
            background: {gradient};
        }}
    """)
    return btn

# Главное окно приложения
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        title = f"Крестики нолики {BOARD_SIZE}x{BOARD_SIZE}"
        self.setWindowTitle(title)
        self.setFixedSize(1000, 650)

        self.game_logic = TicTacToe7x7()
        self.selected_difficulty = Difficulty.MEDIUM
        main_layout = QGridLayout()
        main_layout.setRowStretch(1, 1)
        main_layout.setColumnStretch(1, 1)

        # Заголовок приложения
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            background-color: rgba(33, 36, 54, 0.8);
            color: #f8faff;
            border-radius: 10px;
            padding: 10px 20px;
        """)
        self.title_label.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(self.title_label, 0, 0, 1, 2)

        # Блок управления игрой
        control_panel = QGroupBox("Управление игрой")
        control_layout = QVBoxLayout()

        # Группа для выбора режима игры
        self.mode_group = QGroupBox("Режим игры")
        mode_layout = QVBoxLayout()
        self.pvp_radio = QRadioButton("Игрок vs Игрок")
        self.pvp_radio.setChecked(True)
        self.pve_radio = QRadioButton("Игрок vs Бот")
        mode_layout.addWidget(self.pvp_radio)
        mode_layout.addWidget(self.pve_radio)
        self.mode_group.setLayout(mode_layout)

        # Кнопки управления игрой
        self.start_button = create_styled_button(
            "Начать игру",
            "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff7a4f, stop:1 #fd885f)"
        )
        self.settings_button = create_styled_button(
            "Настройки",
            "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ffe27c, stop:1 #ffd257)"
        )

        self.language_button = create_styled_button(
            "Язык игры",
            "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c6afb, stop:1 #4a5fff)",
            text_color="#fff"
        )

        self.start_button.clicked.connect(self.start_game)
        self.settings_button.clicked.connect(self.open_settings)
        self.language_button.clicked.connect(self.change_language)

        control_layout.addWidget(self.mode_group)
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.settings_button)
        control_layout.addWidget(self.language_button)
        control_layout.addStretch()
        control_panel.setLayout(control_layout)

        # Игровое поле
        self.game_grid = GameGrid(self.game_logic, self)

        main_layout.addWidget(control_panel, 1, 0)
        main_layout.addWidget(self.game_grid, 1, 1)

        self.setLayout(main_layout)

    def start_game(self):
        # Запуск новой игры
        self.game_logic.reset()
        self.game_logic.bot_mode = self.pve_radio.isChecked()
        self.game_logic.bot_difficulty = self.selected_difficulty
        self.game_grid.reset_board()

        if self.game_logic.bot_mode and self.game_logic.current_player == 'O':
            QTimer.singleShot(500, self.game_grid.make_bot_move)

    def open_settings(self):
        # Открытие диалога настроек
        dialog = SettingsDialog(self, selected_difficulty=self.selected_difficulty)
        if dialog.exec_():
            # Обновить сложность, если игра не в режиме против бота
            if not self.game_logic.bot_mode:
                selected_text = dialog.difficulty.currentText()
                for d in Difficulty:
                    if d.value == selected_text:
                        self.selected_difficulty = d
                        break
                self.game_logic.bot_difficulty = self.selected_difficulty
                QMessageBox.information(self, "Сложность бота",
                                        f"Выбрана сложность: {self.game_logic.bot_difficulty.value}")
            else:
                QMessageBox.information(self, "Предупреждение",
                                        "Сложность бота не может быть изменена во время игры с ботом.")

    def change_language(self):
        # Пока поддерживается только русский язык
        QMessageBox.information(self, "Язык", "Игра доступна только на русском языке")

# Точка входа в приложение
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget {
            background-color: #212436;
            color: #ffffff;
            font-family: 'Arial', sans-serif;
            font-size: 16pt;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
