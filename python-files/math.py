import tkinter as tk
from tkinter import messagebox
import numpy as np


class MatrixApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Матрица 8x8")
        self.root.geometry("800x600")

        self.matrix = np.zeros((8, 8), dtype=int)
        self.current_row = 0
        self.current_col = 0
        self.found_blocks = []

        self.create_widgets()
        self.focus_first_cell()

    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(self.root, text="Матрица 8x8", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Фрейм для матрицы
        matrix_frame = tk.Frame(self.root)
        matrix_frame.pack(pady=20)

        # Создание ячеек матрицы
        self.cells = []
        for i in range(8):
            row_cells = []
            for j in range(8):
                cell = tk.Entry(matrix_frame, width=5, font=("Arial", 12), justify="center")
                cell.grid(row=i, column=j, padx=2, pady=2)
                cell.bind("<KeyRelease>", lambda event, row=i, col=j: self.on_key_release(event, row, col))
                cell.bind("<FocusIn>", lambda event, row=i, col=j: self.on_focus(row, col))
                row_cells.append(cell)
            self.cells.append(row_cells)

        # Фрейм для управления
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=20)

        # Поле для целевой суммы
        tk.Label(control_frame, text="Целевая сумма:", font=("Arial", 12)).grid(row=0, column=0, padx=5)
        self.target_entry = tk.Entry(control_frame, width=10, font=("Arial", 12))
        self.target_entry.grid(row=0, column=1, padx=5)
        self.target_entry.bind("<Return>", lambda e: self.find_blocks())

        # Кнопка поиска
        find_button = tk.Button(control_frame, text="Найти", command=self.find_blocks,
                                font=("Arial", 12), bg="#4CAF50", fg="white")
        find_button.grid(row=0, column=2, padx=10)

        # Кнопка сброса
        reset_button = tk.Button(control_frame, text="Сброс", command=self.reset_colors,
                                 font=("Arial", 12), bg="#f44336", fg="white")
        reset_button.grid(row=0, column=3, padx=5)

        # Кнопка очистки
        clear_button = tk.Button(control_frame, text="Очистить все", command=self.clear_all,
                                 font=("Arial", 12), bg="#FF9800", fg="white")
        clear_button.grid(row=0, column=4, padx=5)

        # Область результатов
        self.result_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.result_label.pack(pady=10)

        # Подсказки
        hint_label = tk.Label(self.root,
                              text="Автоматический переход между ячейками | Стрелки для ручного перемещения",
                              font=("Arial", 10), fg="gray")
        hint_label.pack(pady=5)

    def focus_first_cell(self):
        self.cells[0][0].focus_set()
        self.current_row = 0
        self.current_col = 0

    def on_focus(self, row, col):
        self.current_row = row
        self.current_col = col

    def on_key_release(self, event, row, col):
        key = event.keysym

        # Обрабатываем только цифровые клавиши и Backspace
        if (key in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"] or
                key == "BackSpace" or key == "Delete"):

            # Сохраняем значение
            try:
                value = self.cells[row][col].get()
                if value:  # Если поле не пустое
                    self.matrix[row, col] = int(value)
                else:
                    self.matrix[row, col] = 0
            except ValueError:
                self.matrix[row, col] = 0

            # Автоматически переходим к следующей ячейке после ввода цифры
            if key in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                self.move_to_next_cell_auto()

        # Обработка стрелок для ручного перемещения
        elif key == "Right" and col < 7:
            self.cells[row][col + 1].focus_set()
            self.current_col = col + 1

        elif key == "Left" and col > 0:
            self.cells[row][col - 1].focus_set()
            self.current_col = col - 1

        elif key == "Down" and row < 7:
            self.cells[row + 1][col].focus_set()
            self.current_row = row + 1

        elif key == "Up" and row > 0:
            self.cells[row - 1][col].focus_set()
            self.current_row = row - 1

    def move_to_next_cell_auto(self):
        # Переходим к следующей ячейке
        if self.current_col < 7:
            self.current_col += 1
        else:
            # Если это последняя ячейка в строке, переходим на следующую строку
            if self.current_row < 7:
                self.current_row += 1
                self.current_col = 0
            else:
                # Если это последняя ячейка матрицы, остаемся на ней
                return

        # Устанавливаем фокус на следующую ячейку
        self.cells[self.current_row][self.current_col].focus_set()
        # Выделяем текст в следующей ячейке для удобства замены
        self.cells[self.current_row][self.current_col].select_range(0, tk.END)

    def find_blocks(self):
        # Сначала обновляем все значения матрицы
        self.get_matrix_values()

        # Сбрасываем цвета
        self.reset_colors()

        # Получаем целевую сумму
        try:
            target = int(self.target_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную целевую сумму")
            return

        # Ищем блоки
        self.found_blocks = []
        for i in range(7):
            for j in range(7):
                block_sum = (self.matrix[i, j] + self.matrix[i, j + 1] +
                             self.matrix[i + 1, j] + self.matrix[i + 1, j + 1])
                if block_sum == target:
                    self.found_blocks.append((i, j))

        # Подсвечиваем найденные блоки
        for i, j in self.found_blocks:
            self.cells[i][j].config(bg="#90EE90")  # верхний левый
            self.cells[i][j + 1].config(bg="#90EE90")  # верхний правый
            self.cells[i + 1][j].config(bg="#90EE90")  # нижний левый
            self.cells[i + 1][j + 1].config(bg="#90EE90")  # нижний правый

        # Показываем результаты
        if self.found_blocks:
            self.result_label.config(
                text=f"Найдено блоков 2x2 с суммой {target}: {len(self.found_blocks)}",
                fg="green"
            )

    def reset_colors(self):
        # Сбрасываем цвета всех ячеек
        for i in range(8):
            for j in range(8):
                self.cells[i][j].config(bg="white")

        self.result_label.config(text="")

    def clear_all(self):
        # Очищаем все ячейки и целевую сумму
        for i in range(8):
            for j in range(8):
                self.cells[i][j].delete(0, tk.END)
                self.matrix[i, j] = 0

        self.target_entry.delete(0, tk.END)
        self.reset_colors()
        self.focus_first_cell()

    def get_matrix_values(self):
        # Получаем значения из всех ячеек
        for i in range(8):
            for j in range(8):
                try:
                    value = self.cells[i][j].get()
                    if value:  # Если поле не пустое
                        self.matrix[i, j] = int(value)
                    else:
                        self.matrix[i, j] = 0
                except ValueError:
                    self.matrix[i, j] = 0


def main():
    root = tk.Tk()
    app = MatrixApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()