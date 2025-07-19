import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

def load_excel_data():
    try:
        holders_df = pd.read_excel("База токарных резцов.xlsx", sheet_name="Державки")
        inserts_df = pd.read_excel("База токарных резцов.xlsx", sheet_name="Пластины")
        operations = holders_df["Обработка"].unique().tolist()
        tool_types = holders_df["Назначение резца"].unique().tolist()
        
        print("Уникальные формы в 'Державки' (2. Форма пластины):", holders_df["2. Форма пластины"].unique())
        print("Уникальные формы в 'Пластины' (1.Форма пластины):", inserts_df["1.Форма пластины"].unique())
        
        if "Обозначение " not in inserts_df.columns:
            print("Ошибка: В листе 'Пластины' отсутствует столбец 'Обозначение '")
            return holders_df, inserts_df, operations, tool_types
        if "Обозначение" not in holders_df.columns:
            print("Ошибка: В листе 'Державки' отсутствует столбец 'Обозначение'")
            return holders_df, inserts_df, operations, tool_types
        
        return holders_df, inserts_df, operations, tool_types
    except FileNotFoundError:
        messagebox.showerror("Ошибка", "Файл 'База токарных резцов.xlsx' не найден.")
        return None, None, None, None
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при чтении файла: {str(e)}")
        return None, None, None, None

def find_compatible_inserts(holder_designation, holders_df, inserts_df):
    holder_row = holders_df[holders_df["Обозначение"] == holder_designation]
    if holder_row.empty:
        print(f"Державка {holder_designation} не найдена.")
        return []

    holder_shape = holder_row.iloc[0]["2. Форма пластины"]
    if pd.isna(holder_shape):
        print(f"Форма пластины для {holder_designation} отсутствует.")
        return []

    compatible_inserts = inserts_df[inserts_df["1.Форма пластины"] == holder_shape]["Обозначение "].tolist()
    if not compatible_inserts:
        print(f"Нет совместимых пластин для формы {holder_shape} в {holder_designation}.")
    
    return compatible_inserts

def show_inserts(designation):
    compatible_inserts = find_compatible_inserts(designation, holders_df, inserts_df)
    insert_list_text.delete(1.0, tk.END)
    if compatible_inserts:
        insert_list_text.insert(tk.END, "Список совместимых пластин (съемные режущие элементы):\n" + "\n".join(compatible_inserts))
    else:
        insert_list_text.insert(tk.END, "Совместимые пластины не найдены. Проверьте совпадение форм.")

def update_tool_buttons(*args):
    selected_operation = operation_var.get()
    selected_tool_type = tool_type_var.get()
    if not selected_operation and not selected_tool_type:
        for widget in canvas_frame.winfo_children():
            widget.destroy()
        return

    if holders_df is None or inserts_df is None:
        return

    filtered_holders = holders_df
    if selected_operation:
        filtered_holders = filtered_holders[filtered_holders["Обработка"] == selected_operation]
    if selected_tool_type:
        filtered_holders = filtered_holders[filtered_holders["Назначение резца"] == selected_tool_type]

    for widget in canvas_frame.winfo_children():
        widget.destroy()

    if not filtered_holders.empty:
        holder_designations = filtered_holders["Обозначение"].tolist()
        for designation in holder_designations:
            btn = ttk.Button(canvas_frame, text=designation, command=lambda d=designation: show_inserts(d), style="Holder.TButton")
            btn.pack(fill="x", pady=2)
    else:
        label = ttk.Label(canvas_frame, text="Державки для выбранных параметров не найдены.", style="Holder.TLabel")
        label.pack(pady=5)

# Создание главного окна
root = tk.Tk()
root.title("Выбор державок и пластин")
root.geometry("700x600")
root.configure(bg="#f0f0f0")

# Стилизация
style = ttk.Style()
style.theme_use("clam")  # Используем тему "clam" для современного вида
style.configure("Holder.TButton", padding=6, background="#4CAF50", foreground="white")
style.map("Holder.TButton", background=[("active", "#45a049")])
style.configure("Holder.TLabel", background="#f0f0f0", foreground="#333")
style.configure("TCombobox", fieldbackground="#fff", background="#fff")
style.configure("TLabelFrame.Label", font=("Arial", 12))  # Шрифт для текста в LabelFrame

# Загрузка данных
holders_df, inserts_df, operations, tool_types = load_excel_data()

if holders_df is not None and inserts_df is not None and operations and tool_types:
    # Фрейм для фильтров
    filter_frame = ttk.Frame(root, padding="10")
    filter_frame.pack(fill="x", pady=5)

    # Метка и выпадающее меню для "Обработка"
    operation_label = ttk.Label(filter_frame, text="Выберите тип обработки:", font=("Arial", 12))
    operation_label.pack(side=tk.LEFT, padx=5)
    operation_var = tk.StringVar()
    operation_var.trace("w", update_tool_buttons)
    operation_menu = ttk.Combobox(filter_frame, textvariable=operation_var, values=[""] + operations, state="readonly", width=30)
    operation_menu.pack(side=tk.LEFT, padx=5)

    # Метка и выпадающее меню для "Назначение резца"
    tool_type_label = ttk.Label(filter_frame, text="Выберите назначение резца:", font=("Arial", 12))
    tool_type_label.pack(side=tk.LEFT, padx=5)
    tool_type_var = tk.StringVar()
    tool_type_var.trace("w", update_tool_buttons)
    tool_type_menu = ttk.Combobox(filter_frame, textvariable=tool_type_var, values=[""] + tool_types, state="readonly", width=30)
    tool_type_menu.pack(side=tk.LEFT, padx=5)

    # Фрейм для вывода
    output_frame = ttk.Frame(root, padding="10")
    output_frame.pack(fill="both", expand=True)

    # Панель с кнопками державок с прокруткой
    holder_frame = ttk.LabelFrame(output_frame, text="Державки (нажмите для выбора)", padding="10")
    holder_frame.pack(side=tk.LEFT, padx=10, pady=5, fill="both", expand=True)

    canvas = tk.Canvas(holder_frame, bg="#f0f0f0")
    scrollbar = ttk.Scrollbar(holder_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=canvas_frame, anchor="nw")

    scrollbar.pack(side=tk.RIGHT, fill="y")
    canvas.pack(side=tk.LEFT, fill="both", expand=True)

    def configure_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    canvas_frame.bind("<Configure>", configure_scroll_region)

    # Текстовое поле для пластин
    insert_frame = ttk.LabelFrame(output_frame, text="Пластины", padding="10")
    insert_frame.pack(side=tk.RIGHT, padx=10, pady=5, fill="both", expand=True)
    insert_list_text = tk.Text(insert_frame, height=15, width=30, font=("Arial", 10), bg="#fff", bd=2, relief="solid")
    insert_list_text.pack(pady=5)
    insert_info = ttk.Label(insert_frame, text="Пластина — съемный режущий элемент для державки.", font=("Arial", 8))
    insert_info.pack()

    # Изначальная загрузка кнопок
    update_tool_buttons()
else:
    root.destroy()

# Запуск главного цикла
root.mainloop()