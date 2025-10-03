import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp
from itertools import combinations

def about():  
    messagebox.showinfo("О программе", "Здесь должны быть сведения о программе и авторах.")

def commutator(A, B):
    return A * B - B * A

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f'{width}x{height}+{x}+{y}')

def display_matrix(frame, matrix):
    for widget in frame.winfo_children():
        widget.destroy()

    for i in range(matrix.rows):
        for j in range(matrix.cols):
            el = sp.simplify(matrix[i, j])
            text = tk.Text(frame, width=15, height=1, font=('Arial', 12))
            text.insert(tk.END, el)
            text.config(state=tk.DISABLED)
            text.grid(row=i, column=j, padx=5, pady=5)

def show_ideals(index, results, original_matrix):
    def on_show_commutators():
        comm_window = tk.Toplevel(ideal_window)
        comm_window.title("Коммутаторы")
        comm_window.geometry("800x400")
        center_window(comm_window, 800, 400)

        tk.Label(comm_window, text="Первый коммутатор ([B, L])", font=('Arial', 14)).pack()
        first_matrix_frame = tk.Frame(comm_window)
        first_matrix_frame.pack()

        tk.Label(comm_window, text="Второй коммутатор ([B, [B, L]])", font=('Arial', 14)).pack()
        second_matrix_frame = tk.Frame(comm_window)
        second_matrix_frame.pack()

        B = results[index]
        first_commutator = commutator(B, original_matrix)
        second_commutator = commutator(B, first_commutator)

        display_matrix(first_matrix_frame, first_commutator)
        display_matrix(second_matrix_frame, second_commutator)

    def on_next():
        nonlocal index
        index += 1
        if index < len(results):
            show_ideal()
        else:
            index -= 1

    def show_ideal():
        display_matrix(ideal_matrix_frame, results[index])
        ideal_label.config(text=f"Идеал {index + 1} из {len(results)}")

    ideal_window = tk.Toplevel(root)
    ideal_window.title("Внутренние идеалы")
    ideal_window.geometry("800x600")
    center_window(ideal_window, 800, 600)

    ideal_label = ttk.Label(ideal_window, text="", font=('Arial', 12))
    ideal_label.pack(pady=10)

    ideal_matrix_frame = tk.Frame(ideal_window)
    ideal_matrix_frame.pack()

    show_ideal()

    ttk.Button(ideal_window, text="Показать коммутаторы", command=on_show_commutators).pack(pady=10)
    ttk.Button(ideal_window, text="Далее", command=on_next).pack(pady=10)

def compute_result():
    try:
        n = len(entries)
        elements = []

        for i in range(n):
            for j in range(n):
                value = entries[i][j].get()
                elements.append(sp.sympify(value))

        original_matrix = sp.Matrix(n, n, elements)

        if original_matrix.trace() != 0:
            messagebox.showerror("Ошибка", "Введенная матрица не принадлежит sln(F)")
            return

        submatrices = get_submatrices_with_zero_trace(original_matrix)
        results = []

        for B in submatrices:
            f = commutator(B, original_matrix)
            s = commutator(B, f)
            flag = True
            rows, cols = B.shape
            for i in range(rows):
                 for j in range(cols):
                      if B[i,j]==0:
                          if s[i,j]!=0:
                                 flag = False 
                                 break
            if s.trace() == 0 and flag:
                results.append(B)

        if results:
            show_ideals(0, results, original_matrix)
        else:
            messagebox.showinfo("Результаты", "Внутренние идеалы не найдены.")
    except Exception as e:
        messagebox.showerror("Ошибка", "Необходимо ввести элементы матрицы!")
   

def get_submatrices_with_zero_trace(matrix):
    rows, cols = matrix.shape
    submatrices = []
    seen = set()

    for row_indices in range(1, rows + 1):
        for chosen_rows in combinations(range(rows), row_indices):
            for col_indices in range(1, cols + 1):
                for chosen_cols in combinations(range(cols), col_indices):
                    submatrix = matrix.extract(chosen_rows, chosen_cols)
                    augmented_matrix = sp.Matrix.zeros(rows, cols)
                    for i, row in enumerate(chosen_rows):
                        for j, col in enumerate(chosen_cols):
                            augmented_matrix[row, col] = submatrix[i, j]

                    if augmented_matrix.trace() == 0:
                        matrix_tuple = tuple(map(tuple, augmented_matrix.tolist()))
                        if matrix_tuple not in seen:
                            seen.add(matrix_tuple)
                            submatrices.append(augmented_matrix)

    zero_matrix = sp.Matrix.zeros(rows, cols)
    submatrices.append(zero_matrix)

    # Удаление повторяющихся элементов
    unique_submatrices = list({tuple(map(tuple, mat.tolist())): mat for mat in submatrices}.values())

    return unique_submatrices

def create_matrix_input():
    try:
        n = int(size_entry.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Введите натуральное число n - порядок матрицы.")
        return

    for widget in matrix_frame.winfo_children():
        widget.destroy()

    global entries
    entries = []

    for i in range(n):
        row_entries = []
        for j in range(n):
            entry = ttk.Entry(matrix_frame, width=5)
            entry.grid(row=i, column=j)
            row_entries.append(entry)
        entries.append(row_entries)

    compute_button.pack()

root = tk.Tk()
root.title("Поиск внутренних идеалов специальной линейной алгебры Ли")
center_window(root, 500, 400)

menu_bar = tk.Menu(root)

help_menu = tk.Menu(menu_bar, tearoff=0) 
help_menu.add_command(label="О программе", command=about)  
menu_bar.add_cascade(label="Справка", menu=help_menu) 

ttk.Label(root, text="Введите порядок квадратной матрицы:").pack()
size_entry = ttk.Entry(root)
size_entry.pack()

size_button = ttk.Button(root, text="Создать ячейки для ввода матрицы", command=create_matrix_input)
size_button.pack()

matrix_frame = tk.Frame(root)
matrix_frame.pack()

compute_button = ttk.Button(root, text="Найти все внутренние идеалы", command=compute_result)
root.config(menu=menu_bar)  
root.mainloop()
