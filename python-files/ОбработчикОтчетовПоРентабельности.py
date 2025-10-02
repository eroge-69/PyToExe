import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
import re
import csv

class ExcelProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Обработчик Excel файлов")
        self.root.geometry("1200x800")
        
        self.files = []
        self.data = defaultdict(dict)
        self.settings = {
            'warehouse_col': 1,
            'warehouse_start_row': 9,
            'revenue_col': 17,
            'gross_profit_col': 19,
            'salary_col': 20,
            'inventory_delta_col': 21,
            'net_profit_col': 23,
            'comment_col': 24,
            'period_row': 2,
            'period_col': 3
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Загрузка файлов
        file_frame = ttk.LabelFrame(main_frame, text="Загрузка файлов", padding="5")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(file_frame, text="Загрузить файлы", command=self.load_files).grid(row=0, column=0, padx=5)
        ttk.Button(file_frame, text="Обработать", command=self.process_files).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Очистить", command=self.clear_files).grid(row=0, column=2, padx=5)
        
        self.file_list = tk.Listbox(file_frame, width=80, height=6)
        self.file_list.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Настройки
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки столбцов", padding="5")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Создание полей для настройки
        settings_labels = [
            ("Столбец СКЛАД:", "warehouse_col"),
            ("Начальная строка СКЛАД:", "warehouse_start_row"),
            ("Столбец СРЕДНЯЯ ВЫРУЧКА:", "revenue_col"),
            ("Столбец ВАЛОВАЯ ПРИБЫЛЬ:", "gross_profit_col"),
            ("Столбец ЗП К НАЧИСЛЕНИЮ:", "salary_col"),
            ("Столбец ДЕЛЬТА ПО ИНВ:", "inventory_delta_col"),
            ("Столбец ЧИСТАЯ ПРИБЫЛЬ:", "net_profit_col"),
            ("Столбец КОММЕНТАРИЙ:", "comment_col"),
            ("Строка ПЕРИОДА:", "period_row"),
            ("Столбец ПЕРИОДА:", "period_col")
        ]
        
        self.entry_vars = {}
        for i, (label, key) in enumerate(settings_labels):
            ttk.Label(settings_frame, text=label).grid(row=i//2, column=(i%2)*2, sticky=tk.W, padx=5)
            var = tk.StringVar(value=str(self.settings[key]))
            entry = ttk.Entry(settings_frame, textvariable=var, width=8)
            entry.grid(row=i//2, column=(i%2)*2+1, padx=5)
            self.entry_vars[key] = var
        
        ttk.Button(settings_frame, text="Применить настройки", 
                  command=self.apply_settings).grid(row=5, column=0, columnspan=4, pady=5)
        
        # Таблица результатов
        result_frame = ttk.LabelFrame(main_frame, text="Результаты", padding="5")
        result_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Создание фрейма для таблицы с прокрутками
        table_container = ttk.Frame(result_frame)
        table_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Создание treeview для отображения результатов
        columns = ('warehouse')
        self.tree = ttk.Treeview(table_container, columns=columns, show='headings', height=15)
        
        # Вертикальная прокрутка
        v_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Горизонтальная прокрутка
        h_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Размещение элементов в grid
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Кнопки экспорта - размещаем в отдельном фрейме под таблицей
        export_frame = ttk.Frame(result_frame)
        export_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(export_frame, text="Экспорт в CSV", command=self.export_to_csv).grid(row=0, column=0, padx=5)
        ttk.Button(export_frame, text="Экспорт в XLS", command=self.export_to_xls).grid(row=0, column=1, padx=5)
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        table_container.columnconfigure(0, weight=1)
        table_container.rowconfigure(0, weight=1)
        export_frame.columnconfigure(0, weight=0)  # Кнопки не растягиваем
    
    def apply_settings(self):
        try:
            for key, var in self.entry_vars.items():
                self.settings[key] = int(var.get())
            messagebox.showinfo("Успех", "Настройки применены успешно")
        except ValueError:
            messagebox.showerror("Ошибка", "Все значения должны быть целыми числами")
    
    def load_files(self):
        files = filedialog.askopenfilenames(
            title="Выберите Excel файлы",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        
        for file in files:
            if file not in self.files:
                self.files.append(file)
                self.file_list.insert(tk.END, os.path.basename(file))
    
    def clear_files(self):
        self.files.clear()
        self.file_list.delete(0, tk.END)
        self.data.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def read_excel_file(self, file_path):
        """Чтение данных из Excel файла (xlsx)"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Получаем shared strings
                shared_strings = []
                if 'xl/sharedStrings.xml' in zip_file.namelist():
                    with zip_file.open('xl/sharedStrings.xml') as f:
                        content = f.read().decode('utf-8')
                        root = ET.fromstring(content)
                        for si in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'):
                            if si.text:
                                shared_strings.append(si.text)
                
                # Читаем данные из первого листа
                sheet_files = [f for f in zip_file.namelist() if f.startswith('xl/worksheets/sheet')]
                if not sheet_files:
                    return None, None
                
                with zip_file.open(sheet_files[0]) as f:
                    content = f.read().decode('utf-8')
                    root = ET.fromstring(content)
                    
                    data = []
                    namespace = {'ss': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                    
                    # Читаем все ячейки
                    rows = root.findall('.//ss:row', namespace)
                    for row in rows:
                        row_data = []
                        cells = row.findall('ss:c', namespace)
                        for cell in cells:
                            cell_value = ""
                            v = cell.find('ss:v', namespace)
                            if v is not None and v.text:
                                if cell.get('t') == 's':  # shared string
                                    try:
                                        idx = int(v.text)
                                        if idx < len(shared_strings):
                                            cell_value = shared_strings[idx]
                                    except ValueError:
                                        cell_value = v.text
                                else:
                                    cell_value = v.text
                            row_data.append(cell_value)
                        data.append(row_data)
                    
                    return data, self.get_period(data)
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка чтения файла {file_path}: {str(e)}")
            return None, None
    
    def clean_period_name(self, period):
        """Очистка названия периода - удаляем 'Период отчета:' и оставляем только даты"""
        if not period:
            return "Неизвестный период"
        
        # Удаляем фразу "Период отчета:" и лишние пробелы
        period = str(period).replace('Период отчета:', '').strip()
        
        # Удаляем возможные дополнительные фразы
        period = period.replace('Отчетный период:', '').strip()
        period = period.replace('Период:', '').strip()
        
        # Оставляем только дату/диапазон дат
        # Если после очистки осталась пустая строка, возвращаем исходное значение
        if not period:
            return "Неизвестный период"
        
        return period
    
    def get_period(self, data):
        """Получение периода из данных"""
        try:
            row_idx = self.settings['period_row'] - 1
            col_idx = self.settings['period_col'] - 1
            
            if row_idx < len(data) and col_idx < len(data[row_idx]):
                raw_period = data[row_idx][col_idx]
                return self.clean_period_name(raw_period)
        except:
            pass
        return "Неизвестный период"
    
    def extract_warehouse_data(self, data, period):
        """Извлечение данных по складам"""
        warehouse_data = {}
        
        try:
            start_row = self.settings['warehouse_start_row'] - 1
            warehouse_col = self.settings['warehouse_col'] - 1
            
            for i in range(start_row, len(data)):
                if warehouse_col < len(data[i]) and data[i][warehouse_col]:
                    warehouse_name = str(data[i][warehouse_col]).strip()
                    
                    if warehouse_name.lower() == 'итого':
                        break
                    
                    if warehouse_name and warehouse_name not in warehouse_data:
                        # Извлекаем данные по всем показателям
                        metrics = {}
                        col_mappings = {
                            'revenue': self.settings['revenue_col'] - 1,
                            'gross_profit': self.settings['gross_profit_col'] - 1,
                            'salary': self.settings['salary_col'] - 1,
                            'inventory_delta': self.settings['inventory_delta_col'] - 1,
                            'net_profit': self.settings['net_profit_col'] - 1,
                            'comment': self.settings['comment_col'] - 1
                        }
                        
                        for metric, col_idx in col_mappings.items():
                            if col_idx < len(data[i]) and data[i][col_idx]:
                                try:
                                    if metric == 'comment':  # Комментарии - текстовые данные
                                        metrics[metric] = str(data[i][col_idx]).strip()
                                    else:  # Остальные показатели - числовые
                                        # Очищаем значение от лишних символов
                                        value = str(data[i][col_idx]).replace(' ', '').replace(',', '.')
                                        metrics[metric] = float(value) if self.is_numeric(value) else 0.0
                                except:
                                    if metric == 'comment':
                                        metrics[metric] = ""
                                    else:
                                        metrics[metric] = 0.0
                            else:
                                if metric == 'comment':
                                    metrics[metric] = ""
                                else:
                                    metrics[metric] = 0.0
                        
                        warehouse_data[warehouse_name] = metrics
                        
        except Exception as e:
            print(f"Ошибка при извлечении данных склада: {str(e)}")
        
        return warehouse_data
    
    def is_numeric(self, value):
        """Проверка, является ли значение числовым"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def process_files(self):
        if not self.files:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файлы")
            return
        
        self.data.clear()
        
        for file_path in self.files:
            data, period = self.read_excel_file(file_path)
            if data and period:
                warehouse_data = self.extract_warehouse_data(data, period)
                
                for warehouse, metrics in warehouse_data.items():
                    if warehouse not in self.data:
                        self.data[warehouse] = {}
                    self.data[warehouse][period] = metrics
        
        self.display_results()
    
    def display_results(self):
        """Отображение результатов в таблице - каждый склад один раз, данные по периодам горизонтально"""
        # Очищаем предыдущие результаты
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Очищаем предыдущие колонки
        for col in self.tree['columns']:
            self.tree.heading(col, text='')
        
        # Собираем все уникальные периоды
        all_periods = set()
        for warehouse_data in self.data.values():
            all_periods.update(warehouse_data.keys())
        
        all_periods = sorted(all_periods)
        
        # Создаем колонки
        columns = ['СКЛАД']
        
        # Для каждого периода создаем 6 колонок с показателями (5 числовых + комментарий)
        for period in all_periods:
            columns.extend([
                f'{period}_СРЕДНЯЯ_ВЫРУЧКА',
                f'{period}_ВАЛОВАЯ_ПРИБЫЛЬ', 
                f'{period}_ЗП_К_НАЧИСЛЕНИЮ',
                f'{period}_ДЕЛЬТА_ПО_ИНВ',
                f'{period}_ЧИСТАЯ_ПРИБЫЛЬ',
                f'{period}_КОММЕНТАРИЙ'
            ])
        
        # Настраиваем treeview
        self.tree['columns'] = columns
        
        # Настраиваем заголовки
        self.tree.heading('СКЛАД', text='СКЛАД')
        self.tree.column('СКЛАД', width=150, minwidth=100, anchor='w')
        
        # Настраиваем заголовки для показателей по периодам
        for col in columns[1:]:
            # Разделяем на период и показатель
            parts = col.split('_', 1)
            if len(parts) == 2:
                period_part = parts[0]
                metric_part = parts[1]
                
                # Форматируем отображение
                if len(period_part) > 15:
                    # Если период длинный, разбиваем на несколько строк
                    display_text = f"{period_part}\n{metric_part}"
                else:
                    display_text = f"{period_part} {metric_part}"
            else:
                display_text = col
            
            self.tree.heading(col, text=display_text)
            
            # Устанавливаем разную ширину для комментариев и числовых колонок
            if col.endswith('_КОММЕНТАРИЙ'):
                self.tree.column(col, width=150, minwidth=100, anchor='w')
            else:
                self.tree.column(col, width=100, minwidth=80, anchor='e')
        
        # Заполняем данные - каждый склад один раз
        for warehouse in sorted(self.data.keys()):
            row_data = [warehouse]
            
            # Для каждого периода добавляем все 6 показателей
            for period in all_periods:
                if period in self.data[warehouse]:
                    metrics = self.data[warehouse][period]
                    row_data.extend([
                        f"{metrics.get('revenue', 0):.2f}",
                        f"{metrics.get('gross_profit', 0):.2f}",
                        f"{metrics.get('salary', 0):.2f}",
                        f"{metrics.get('inventory_delta', 0):.2f}",
                        f"{metrics.get('net_profit', 0):.2f}",
                        metrics.get('comment', '')
                    ])
                else:
                    row_data.extend(['0.00', '0.00', '0.00', '0.00', '0.00', ''])
            
            self.tree.insert('', tk.END, values=row_data)
    
    def prepare_export_data(self):
        """Подготовка данных для экспорта в правильном формате - каждый склад один раз"""
        export_data = []
        
        # Собираем все уникальные периоды
        all_periods = set()
        for warehouse_data in self.data.values():
            all_periods.update(warehouse_data.keys())
        
        all_periods = sorted(all_periods)
        
        # Создаем заголовки для экспорта
        headers = ['СКЛАД']
        for period in all_periods:
            headers.extend([
                f'{period}_СРЕДНЯЯ_ВЫРУЧКА',
                f'{period}_ВАЛОВАЯ_ПРИБЫЛЬ',
                f'{period}_ЗП_К_НАЧИСЛЕНИЮ',
                f'{period}_ДЕЛЬТА_ПО_ИНВ', 
                f'{period}_ЧИСТАЯ_ПРИБЫЛЬ',
                f'{period}_КОММЕНТАРИЙ'
            ])
        
        # Заполняем данные
        for warehouse in sorted(self.data.keys()):
            row = [warehouse]
            for period in all_periods:
                if period in self.data[warehouse]:
                    metrics = self.data[warehouse][period]
                    row.extend([
                        metrics.get('revenue', 0),
                        metrics.get('gross_profit', 0),
                        metrics.get('salary', 0),
                        metrics.get('inventory_delta', 0),
                        metrics.get('net_profit', 0),
                        metrics.get('comment', '')
                    ])
                else:
                    row.extend([0, 0, 0, 0, 0, ''])
            export_data.append(row)
        
        return headers, export_data
    
    def export_to_csv(self):
        """Экспорт результатов в CSV с правильными заголовками"""
        if not self.data:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Сохранить как CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if not file_path:
            return
        
        try:
            headers, export_data = self.prepare_export_data()
            
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(headers)
                writer.writerows(export_data)
            
            messagebox.showinfo("Успех", f"Данные экспортированы в {file_path}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")
    
    def export_to_xls(self):
        """Экспорт результатов в XLS формат (с использованием XML)"""
        if not self.data:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Сохранить как XLS",
            defaultextension=".xls",
            filetypes=[("Excel files", "*.xls")]
        )
        
        if not file_path:
            return
        
        try:
            headers, export_data = self.prepare_export_data()
            
            # Создаем простой XLS файл в формате XML
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0"?>\n')
                f.write('<?mso-application progid="Excel.Sheet"?>\n')
                f.write('<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"\n')
                f.write(' xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">\n')
                f.write(' <Styles>\n')
                f.write('  <Style ss:ID="Default" ss:Name="Normal">\n')
                f.write('   <Alignment ss:Vertical="Bottom"/>\n')
                f.write('  </Style>\n')
                f.write('  <Style ss:ID="Header">\n')
                f.write('   <Font ss:Bold="1"/>\n')
                f.write('  </Style>\n')
                f.write(' </Styles>\n')
                f.write(' <Worksheet ss:Name="Sheet1">\n')
                f.write('  <Table>\n')
                
                # Заголовки
                f.write('   <Row>\n')
                for header in headers:
                    f.write(f'    <Cell ss:StyleID="Header"><Data ss:Type="String">{header}</Data></Cell>\n')
                f.write('   </Row>\n')
                
                # Данные
                for row in export_data:
                    f.write('   <Row>\n')
                    for i, cell in enumerate(row):
                        if i == 0 or (i - 1) % 6 == 5:  # Текстовые колонки (СКЛАД и КОММЕНТАРИЙ)
                            f.write(f'    <Cell><Data ss:Type="String">{cell}</Data></Cell>\n')
                        else:  # Числовые колонки
                            f.write(f'    <Cell><Data ss:Type="Number">{cell}</Data></Cell>\n')
                    f.write('   </Row>\n')
                
                f.write('  </Table>\n')
                f.write(' </Worksheet>\n')
                f.write('</Workbook>\n')
            
            messagebox.showinfo("Успех", f"Данные экспортированы в {file_path}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")

def main():
    root = tk.Tk()
    app = ExcelProcessor(root)
    root.mainloop()

if __name__ == "__main__":
    main()