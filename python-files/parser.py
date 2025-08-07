import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QSlider, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt


class TripleSliderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.word0 = "Козодой"
        self.word1 = "Шидюк"
        self.words = ["Павловец", "Дерушев", "Лапусто"]

        self.setWindowTitle("Три ползунка")
        self.setGeometry(100, 100, 500, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # Создаем три слайдера с подписями
        self.sliders = []
        slider_config = [
            ("медленно", "быстро"),
            ("плохо", "качественно"),
            ("бесплатно", "дорого")
        ]

        for left, right in slider_config:
            h_layout = QHBoxLayout()

            # Левая подпись
            left_label = QLabel(left)
            h_layout.addWidget(left_label)

            # Слайдер
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(1)
            slider.setSingleStep(1)
            slider.setValue(0)
            slider.valueChanged.connect(self.slider_changed)
            h_layout.addWidget(slider)
            self.sliders.append(slider)

            # Правая подпись
            right_label = QLabel(right)
            h_layout.addWidget(right_label)

            main_layout.addLayout(h_layout)

        # Метка для текста
        self.text_label = QLabel(f"{self.word0}, {self.word1}")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet("font-size: 30px; font-weight: bold; margin-top: 30px;")
        main_layout.addWidget(self.text_label)

        central_widget.setLayout(main_layout)

    def slider_changed(self):
        # Получаем текущие значения слайдеров
        values = [s.value() for s in self.sliders]
        total = sum(values)

        # Если активных три, выключаем случайный из предыдущих
        if total == 3:
            # Находим только что включенный слайдер
            sender_slider = self.sender()
            try:
                sender_index = self.sliders.index(sender_slider)
            except:
                return

            # Выбираем случайный из других активных слайдеров
            other_active = [i for i, val in enumerate(values) if val == 1 and i != sender_index]
            if other_active:
                index_to_disable = random.choice(other_active)
                self.sliders[index_to_disable].blockSignals(True)
                self.sliders[index_to_disable].setValue(0)
                self.sliders[index_to_disable].blockSignals(False)

        # Обновляем текст
        self.update_text()

    def update_text(self):
        active_indices = [i for i, slider in enumerate(self.sliders) if slider.value() == 1]
        n = len(active_indices)

        if n == 0:
            text = f"{self.word0}, {self.word1}"
        elif n == 1:
            # Случайно выбираем какое слово заменить
            replacement = self.words[active_indices[0]]
            if random.randint(0, 1) == 0:
                text = f"{replacement}, {self.word1}"
            else:
                text = f"{self.word0}, {replacement}"
        else:  # n == 2
            replacements = [self.words[i] for i in active_indices]
            random.shuffle(replacements)
            text = f"{replacements[0]}, {replacements[1]}"

        self.text_label.setText(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TripleSliderApp()
    window.show()
    sys.exit(app.exec_())