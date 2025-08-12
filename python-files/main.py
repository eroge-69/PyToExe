import tkinter as tk
from tkinter import messagebox, font
import random


class GlassBridgeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Стеклянный мост: Игра в кальмара")
        self.root.geometry("700x600")
        self.root.resizable(False, False)

        # Настройка цветов
        self.bg_color = "#1a1a2e"
        self.tile_color = "#16213e"
        self.active_color = "#0f3460"
        self.correct_color = "#4CAF50"
        self.incorrect_color = "#F44336"
        self.neutral_color = "#1f4068"
        self.text_color = "#e6e6e6"
        self.highlight_color = "#FFEB3B"

        self.root.configure(bg=self.bg_color)

        self.vocabulary = []
        self.current_level = 0
        self.max_levels = 7
        self.bridge_tiles = []  # Для хранения плит моста

        # Создаем два фрейма: настройка и игра
        self.setup_frame = tk.Frame(self.root, bg=self.bg_color)
        self.game_frame = tk.Frame(self.root, bg=self.bg_color)

        self.create_setup_ui()
        self.create_game_ui()

        # Показываем только экран настройки
        self.show_setup()

    def create_setup_ui(self):
        """Создаем интерфейс для настройки игры"""
        setup_frame = self.setup_frame
        setup_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Заголовок
        title_label = tk.Label(
            setup_frame,
            text="НАСТРОЙКА СТЕКЛЯННОГО МОСТА",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        title_label.pack(pady=(0, 20))

        # Инструкция
        instruction = tk.Label(
            setup_frame,
            text="Введите 7 пар слов для стеклянного моста.\n"
                 "Формат: русское слово, английский перевод\n"
                 "Пример:",
            font=("Arial", 10),
            wraplength=500,
            justify="center",
            bg=self.bg_color,
            fg=self.text_color
        )
        instruction.pack(pady=(0, 10))

        # Пример
        example_frame = tk.Frame(setup_frame, bg=self.tile_color, bd=1, relief=tk.SOLID)
        example_frame.pack(pady=5, padx=50, fill=tk.X)
        example_label = tk.Label(
            example_frame,
            text="яблоко, apple\nсобака, dog\nкошка, cat\nдом, house\nмашина, car\nкнига, book\nсолнце, sun",
            font=("Courier", 11),
            bg=self.tile_color,
            fg=self.text_color,
            justify=tk.LEFT,
            padx=10,
            pady=10
        )
        example_label.pack()

        # Поле для ввода слов
        words_frame = tk.Frame(setup_frame, bg=self.bg_color)
        words_frame.pack(fill=tk.BOTH, expand=True, pady=15)

        self.words_entry = tk.Text(
            words_frame,
            font=("Arial", 11),
            width=50,
            height=10,
            bg=self.tile_color,
            fg=self.text_color,
            insertbackground='white'
        )
        self.words_entry.pack(fill=tk.BOTH, expand=True)
        self.words_entry.insert("1.0",
                                "яблоко, apple\nсобака, dog\nкошка, cat\nдом, house\nмашина, car\nкнига, book\nсолнце, sun")

        # Кнопка начала игры
        button_frame = tk.Frame(setup_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=15)

        self.start_button = tk.Button(
            button_frame,
            text="ЗАПУСТИТЬ ИГРУ",
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            width=20,
            height=2,
            command=self.start_game,
            relief=tk.RAISED,
            bd=3
        )
        self.start_button.pack(pady=10)

        # Предупреждение
        warning = tk.Label(
            setup_frame,
            text="В игре нужно выбирать между двумя плитами активной пары!",
            font=("Arial", 9, "italic"),
            fg="#ff5252",
            wraplength=500,
            justify="center",
            bg=self.bg_color
        )
        warning.pack(pady=5)

    def create_game_ui(self):
        """Создаем интерфейс для игрового процесса"""
        game_frame = self.game_frame
        game_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Заголовок уровня
        self.level_label = tk.Label(
            game_frame,
            text="УРОВЕНЬ: 1/7",
            font=("Arial", 16, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        self.level_label.pack(pady=(0, 15))

        # Русское слово текущего уровня
        self.russian_label = tk.Label(
            game_frame,
            text="",
            font=("Arial", 24, "bold"),
            bg=self.bg_color,
            fg="#64b5f6",
            height=2
        )
        self.russian_label.pack(pady=5, fill=tk.X)

        # Результат выбора
        self.result_label = tk.Label(
            game_frame,
            text="",
            font=("Arial", 12),
            bg=self.bg_color,
            fg=self.text_color,
            height=2
        )
        self.result_label.pack(pady=5, fill=tk.X)

        # Мост - 7 пар плит
        self.bridge_frame = tk.Frame(game_frame, bg=self.bg_color)
        self.bridge_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Кнопка следующего уровня
        self.next_button = tk.Button(
            game_frame,
            text="СЛЕДУЮЩИЙ УРОВЕНЬ →",
            font=("Arial", 12, "bold"),
            state=tk.DISABLED,
            bg="#FF9800",
            fg="white",
            command=self.next_level,
            relief=tk.RAISED,
            bd=3
        )
        self.next_button.pack(pady=15, fill=tk.X)

        # Кнопка возврата к настройкам
        edit_button = tk.Button(
            game_frame,
            text="Новая игра",
            font=("Arial", 10),
            bg="#9C27B0",
            fg="white",
            command=self.show_setup
        )
        edit_button.pack(pady=10, fill=tk.X)

    def create_bridge(self):
        """Создаем стеклянный мост из 7 пар плит"""
        # Очищаем предыдущие плиты
        for widget in self.bridge_frame.winfo_children():
            widget.destroy()

        self.bridge_tiles = []

        # Создаем 7 рядов (уровней)
        for row in range(self.max_levels):
            row_frame = tk.Frame(self.bridge_frame, bg=self.bg_color)
            row_frame.pack(fill=tk.X, pady=3)

            # Создаем 2 плиты для каждого ряда
            for col in range(2):
                tile = tk.Label(
                    row_frame,
                    text="",  # Текст будет установлен позже
                    font=("Arial", 11 if row == self.current_level else 1),
                    width=15,
                    height=2,
                    bg=self.neutral_color,
                    fg=self.text_color,
                    relief=tk.RAISED,
                    bd=2
                )

                # Только для активного уровня делаем плиты интерактивными
                if row == self.current_level:
                    tile.config(
                        bg=self.active_color,
                        cursor="hand2",
                        font=("Arial", 11, "bold")
                    )
                    tile.bind("<Button-1>", lambda e, idx=col: self.step_on_tile(idx))

                tile.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
                self.bridge_tiles.append((row, col, tile))

    def update_bridge_text(self):
        """Обновляем текст на плитах моста"""
        for row, col, tile in self.bridge_tiles:
            # Для активного уровня показываем текст
            if row == self.current_level:
                if col == 0:
                    tile.config(text=self.tile_left_text)
                else:
                    tile.config(text=self.tile_right_text)
            # Для неактивных уровней показываем номер уровня
            else:
                tile.config(text=f"Уровень {row + 1}")

    def show_setup(self):
        """Показываем экран настройки"""
        self.game_frame.pack_forget()
        self.setup_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def show_game(self):
        """Показываем игровой экран"""
        self.setup_frame.pack_forget()
        self.game_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.create_bridge()
        self.setup_level()

    def start_game(self):
        """Начинаем игру с введенными словами"""
        # Получаем слова из поля ввода
        words_input = self.words_entry.get("1.0", tk.END).strip()

        # Парсим введенные данные
        self.vocabulary = []
        try:
            # Разделяем на строки
            lines = [line.strip() for line in words_input.split('\n') if line.strip()]

            for line in lines:
                # Разделяем на пары
                if ',' in line:
                    parts = line.split(',')
                    if len(parts) >= 2:
                        russian = parts[0].strip()
                        english = parts[1].strip()
                        if russian and english:
                            self.vocabulary.append((russian, english))

            # Проверяем количество слов
            if len(self.vocabulary) < self.max_levels:
                messagebox.showerror("Ошибка", f"Нужно ровно {self.max_levels} пар слов!")
                return

            # Ограничиваем количество уровней
            self.vocabulary = self.vocabulary[:self.max_levels]
            self.current_level = 0
            self.show_game()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неправильный формат ввода: {str(e)}")

    def setup_level(self):
        """Настраиваем текущий уровень"""
        # Получаем текущую пару слов
        russian_word, correct_translation = self.vocabulary[self.current_level]

        # Сбрасываем результат
        self.result_label.config(text="")
        self.next_button.config(state=tk.DISABLED)

        # Выбираем случайную плиту для правильного ответа (0 - левая, 1 - правая)
        self.correct_tile = random.randint(0, 1)

        # Формируем неправильный вариант
        all_translations = [pair[1] for pair in self.vocabulary]
        wrong_translations = [t for t in all_translations if t != correct_translation]
        wrong_translation = random.choice(wrong_translations)

        # Сохраняем тексты для плит
        if self.correct_tile == 0:
            self.tile_left_text = correct_translation
            self.tile_right_text = wrong_translation
        else:
            self.tile_left_text = wrong_translation
            self.tile_right_text = correct_translation

        # Обновляем мост
        self.create_bridge()
        self.update_bridge_text()

        # Обновляем статус
        self.level_label.config(text=f"УРОВЕНЬ: {self.current_level + 1}/7")
        self.russian_label.config(text=russian_word)

    def step_on_tile(self, tile_index):
        """Обработчик выбора плиты"""
        # Получаем текущую пару слов
        russian_word, correct_translation = self.vocabulary[self.current_level]

        # Определяем, правильный ли выбор
        if tile_index == self.correct_tile:
            # Правильный выбор
            self.result_label.config(
                text=f"✅ Правильно! {russian_word} = {correct_translation}",
                fg="#4CAF50"
            )

            # Активируем кнопку следующего уровня
            self.next_button.config(state=tk.NORMAL)
        else:
            # Неправильный выбор
            selected_text = self.tile_left_text if tile_index == 0 else self.tile_right_text
            self.result_label.config(
                text=f"❌ Неправильно! {russian_word} ≠ {selected_text}",
                fg="#F44336"
            )

            # Показываем сообщение об окончании игры
            self.root.after(1500, self.show_game_over)

    def show_game_over(self):
        messagebox.showerror("Игра окончена", "Вы упали! Попробуйте снова.")
        self.show_setup()

    def next_level(self):
        """Переход на следующий уровень"""
        self.current_level += 1

        if self.current_level >= self.max_levels:
            messagebox.showinfo("Победа!", "Поздравляем! Вы успешно прошли стеклянный мост!")
            self.show_setup()
        else:
            self.setup_level()


if __name__ == "__main__":
    root = tk.Tk()
    game = GlassBridgeGame(root)
    root.mainloop()