import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QLineEdit, QMessageBox

class GlassBridgeGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Стеклянный мост из Игры в кальмара")
        self.setGeometry(100, 100, 400, 300)
        
        self.words = ["Apple", "Banana", "Cat", "Dog", "Elephant", "Fish", "Giraffe"]  # Можно редактировать
        self.current_level = 0
        self.max_levels = 7
        
        self.initUI()
    
    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        
        self.word_label = QLabel("Нажми на плиту, чтобы начать!")
        self.layout.addWidget(self.word_label)
        
        self.tile_button = QPushButton("Наступить на плиту")
        self.tile_button.clicked.connect(self.step_on_tile)
        self.layout.addWidget(self.tile_button)
        
        self.next_button = QPushButton("Следующий уровень")
        self.next_button.clicked.connect(self.next_level)
        self.next_button.setEnabled(False)
        self.layout.addWidget(self.next_button)
        
        self.edit_label = QLabel("Редактировать слова (через запятую):")
        self.layout.addWidget(self.edit_label)
        
        self.word_edit = QLineEdit(", ".join(self.words))
        self.layout.addWidget(self.word_edit)
        
        self.save_button = QPushButton("Сохранить слова")
        self.save_button.clicked.connect(self.save_words)
        self.layout.addWidget(self.save_button)
        
        self.central_widget.setLayout(self.layout)
    
    def step_on_tile(self):
        if self.current_level >= self.max_levels:
            QMessageBox.information(self, "Конец игры", "Вы прошли все уровни!")
            return
        
        word = self.words[self.current_level]
        self.word_label.setText(f"Слово: {word}")
        
        # Случайное определение - упал или нет (50/50)
        if random.choice([True, False]):
            self.result = "Прошел дальше!"
            self.next_button.setEnabled(True)
        else:
            self.result = "Упал! Игра окончена."
            self.next_button.setEnabled(False)
            QMessageBox.critical(self, "Результат", self.result)
            self.reset_game()
    
    def next_level(self):
        self.current_level += 1
        if self.current_level >= self.max_levels:
            QMessageBox.information(self, "Победа!", "Вы прошли все уровни!")
            self.reset_game()
        else:
            self.word_label.setText(f"Уровень {self.current_level + 1}. Нажми на плиту.")
            self.next_button.setEnabled(False)
    
    def reset_game(self):
        self.current_level = 0
        self.word_label.setText("Нажми на плиту, чтобы начать заново!")
    
    def save_words(self):
        new_words = self.word_edit.text().split(", ")
        if len(new_words) >= self.max_levels:
            self.words = new_words[:self.max_levels]
            QMessageBox.information(self, "Сохранено", "Слова обновлены!")
        else:
            QMessageBox.warning(self, "Ошибка", f"Нужно минимум {self.max_levels} слов!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = GlassBridgeGame()
    game.show()
    sys.exit(app.exec_())