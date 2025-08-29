import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re
import json

def extract_and_filter_product_numbers(file_path, target_count):
    filtered_blocks_info = []
    current_box_data = {}
    in_product_numbers_block = False
    product_numbers_list = []
    collecting_metadata = False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()

                # Начинаем собирать метаданные при встрече "Number":
                if '"Number":' in stripped_line and not in_product_numbers_block:
                    collecting_metadata = True
                    current_box_data = {}
                    product_numbers_list = []

                if collecting_metadata:
                    # Ищем Number
                    number_match = re.search(r'"Number": (\d+),?', stripped_line)
                    if number_match:
                        current_box_data['Number'] = int(number_match.group(1))

                    # Ищем boxNumber
                    box_number_match = re.search(r'"boxNumber": "([^"]+)",?', stripped_line)
                    if box_number_match:
                        current_box_data['boxNumber'] = box_number_match.group(1)

                    # Ищем boxAgregate
                    box_agregate_match = re.search(r'"boxAgregate": (true|false),?', stripped_line)
                    if box_agregate_match:
                        current_box_data['boxAgregate'] = json.loads(box_agregate_match.group(1).lower())

                    # Ищем boxTime
                    box_time_match = re.search(r'"boxTime": "([^"]+)",?', stripped_line)
                    if box_time_match:
                        current_box_data['boxTime'] = box_time_match.group(1)

                    # Если встретили начало productNumbers, заканчиваем сбор метаданных
                    if '"productNumbers": [' in stripped_line:
                        collecting_metadata = False
                        in_product_numbers_block = True
                        continue

                elif in_product_numbers_block:
                    if stripped_line == ']':
                        in_product_numbers_block = False
                        product_numbers_count = len(product_numbers_list)
                        if product_numbers_count != target_count:
                            filtered_blocks_info.append({
                                'Number': current_box_data.get('Number', 'N/A'),
                                'boxNumber': current_box_data.get('boxNumber', 'N/A'),
                                'productNumbers_count': product_numbers_count,
                                'productNumbers_sample': product_numbers_list[:5]
                            })
                        current_box_data = {}
                        product_numbers_list = []
                        continue

                    # Добавляем productNumber
                    pn = stripped_line.replace('"', '').replace(',', '').strip()
                    if pn:
                        product_numbers_list.append(pn)

    except FileNotFoundError:
        raise FileNotFoundError(f"Файл '{file_path}' не найден.")
    except Exception as e:
        raise Exception(f"Произошла непредвиденная ошибка при чтении файла: {e}")

    return filtered_blocks_info

class ProductFilterApp:
    def __init__(self, master):
        self.master = master
        master.title("Поиск пачки")

        self.file_path = tk.StringVar()
        self.target_count = tk.StringVar(value="100")

        self.create_widgets()

    def create_widgets(self):
        file_frame = tk.LabelFrame(self.master, text="Выбор файла")
        file_frame.pack(padx=10, pady=10, fill="x")

        self.file_entry = tk.Entry(file_frame, textvariable=self.file_path, width=50)
        self.file_entry.pack(side="left", padx=5, pady=5, expand=True, fill="x")

        self.browse_button = tk.Button(file_frame, text="Обзор...", command=self.browse_file)
        self.browse_button.pack(side="right", padx=5, pady=5)

        count_frame = tk.LabelFrame(self.master, text="Заданное количество Product Numbers")
        count_frame.pack(padx=10, pady=5, fill="x")

        self.count_entry = tk.Entry(count_frame, textvariable=self.target_count, width=10)
        self.count_entry.pack(padx=5, pady=5)

        self.run_button = tk.Button(self.master, text="Запустить фильтрацию", command=self.run_filter)
        self.run_button.pack(padx=10, pady=10)

        self.result_text = scrolledtext.ScrolledText(self.master, width=80, height=20, wrap=tk.WORD)
        self.result_text.pack(padx=10, pady=10, expand=True, fill="both")

    def browse_file(self):
        f_path = filedialog.askopenfilename(
            title="Выберите текстовый файл",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if f_path:
            self.file_path.set(f_path)

    def run_filter(self):
        self.result_text.delete(1.0, tk.END)

        file_path = self.file_path.get()
        if not file_path:
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите файл.")
            return

        try:
            target_count = int(self.target_count.get())
            if target_count < 0:
                messagebox.showwarning("Ошибка", "Количество должно быть неотрицательным числом.")
                return
        except ValueError:
            messagebox.showwarning("Ошибка", "Пожалуйста, введите корректное целое число для количества.")
            return

        try:
            results = extract_and_filter_product_numbers(file_path, target_count)

            if results:
                self.result_text.insert(tk.END, f"Найдены блоки с количеством productNumbers НЕ равным {target_count}:\n\n")
                for block in results:
                    self.result_text.insert(tk.END, f"  Number: {block['Number']}\n")
                    self.result_text.insert(tk.END, f"  Box Number: {block['boxNumber']}\n")
                    self.result_text.insert(tk.END, f"  Product Numbers Count: {block['productNumbers_count']}\n")
                    self.result_text.insert(tk.END, f"  Product Numbers Sample: {block['productNumbers_sample']}\n")
                    self.result_text.insert(tk.END, "-" * 40 + "\n\n")
            else:
                self.result_text.insert(tk.END, f"Не найдено блоков с количеством productNumbers, отличным от {target_count}.\n")

        except FileNotFoundError as e:
            messagebox.showerror("Ошибка файл не найден", str(e))
        except Exception as e:
            messagebox.showerror("Неизвестная ошибка", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductFilterApp(root)
    root.mainloop()