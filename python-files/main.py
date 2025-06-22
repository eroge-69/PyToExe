import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, StringVar, Radiobutton, IntVar, colorchooser
from string import ascii_uppercase
from openpyxl import load_workbook, Workbook
from openpyxl.styles import PatternFill
from copy import copy
import chardet
import traceback
from datetime import datetime
import re
import sys


class DebtMarkerApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.initialize_attributes()
        self.create_widgets()
        self.setup_validation()
        self.setup_event_handlers()

    def setup_window(self):
        """Configure main window settings"""
        self.root.title("Поиск должников v2.2")
        self.root.geometry("1200x900")
        self.root.minsize(1000, 700)

        try:
            self.root.iconbitmap("debt_marker.ico")
        except:
            pass

    def initialize_attributes(self):
        """Initialize all class attributes"""
        # Data storage
        self.residents_df = None
        self.debtors_df = None
        self.result_df = None
        self.original_wb = None
        self.original_residents_path = None
        self.original_debtors_path = None

        # UI settings
        self.new_column_name = "Статус"
        self.column_mode = StringVar(value="new")
        self.update_method = StringVar(value="replace")
        self.resident_sheets = []
        self.debtor_sheets = []
        self.selected_resident_sheet = StringVar()
        self.selected_debtor_sheet = StringVar()
        self.header_row = IntVar(value=1)

        # Column references
        self.mark_column = None
        self.resident_id_column = None
        self.debtor_id_column = None

        # Colors
        self.debtor_color = "FFFF00"  # Yellow
        self.non_debtor_color = "FFFFFF"  # White
        self.header_color = "D3D3D3"  # Light gray
        self.highlight_color = "#347083"  # Blue for selection

    def create_widgets(self):
        """Create all UI elements"""
        self.setup_styles()
        self.create_main_frames()
        self.create_load_section()
        self.create_header_section()
        self.create_compare_section()
        self.create_settings_section()
        self.create_color_section()
        self.create_result_section()
        self.create_export_section()
        self.toggle_column_mode()

    def setup_styles(self):
        """Configure UI styles"""
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('TRadiobutton', font=('Arial', 10))
        style.configure('TCombobox', font=('Arial', 10))
        style.configure('Treeview', rowheight=25)
        style.configure('Treeview.Heading', background=self.header_color)
        style.map('Treeview', background=[('selected', self.highlight_color)])

    def create_main_frames(self):
        """Create main container frames"""
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(fill="x", padx=10, pady=5)

        self.middle_frame = ttk.Frame(self.root)
        self.middle_frame.pack(fill="x", padx=10, pady=5)

        self.bottom_frame = ttk.Frame(self.root)
        self.bottom_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def create_load_section(self):
        """Create file loading section"""
        load_frame = ttk.LabelFrame(self.top_frame, text="1. Загрузка файлов", padding=10)
        load_frame.pack(fill="x", pady=5)

        # Residents frame
        resident_frame = ttk.Frame(load_frame)
        resident_frame.pack(side="left", expand=True, fill="x", padx=5)

        ttk.Button(resident_frame, text="Загрузить таблицу Жильцы",
                   command=self.load_residents).pack(fill="x")

        self.resident_sheet_label = ttk.Label(resident_frame, text="Выберите лист:")
        self.resident_sheet_label.pack(pady=(5, 0))

        self.resident_sheet_combo = ttk.Combobox(resident_frame,
                                                 textvariable=self.selected_resident_sheet,
                                                 state="readonly")
        self.resident_sheet_combo.pack(fill="x")

        # Debtors frame
        debtor_frame = ttk.Frame(load_frame)
        debtor_frame.pack(side="left", expand=True, fill="x", padx=5)

        ttk.Button(debtor_frame, text="Загрузить таблицу Должники",
                   command=self.load_debtors).pack(fill="x")

        self.debtor_sheet_label = ttk.Label(debtor_frame, text="Выберите лист:")
        self.debtor_sheet_label.pack(pady=(5, 0))

        self.debtor_sheet_combo = ttk.Combobox(debtor_frame,
                                               textvariable=self.selected_debtor_sheet,
                                               state="readonly")
        self.debtor_sheet_combo.pack(fill="x")

    def create_header_section(self):
        """Create header row selection section"""
        header_frame = ttk.LabelFrame(self.top_frame, text="2. Строка с заголовками", padding=10)
        header_frame.pack(fill="x", pady=5)

        ttk.Radiobutton(header_frame, text="Строка 1", variable=self.header_row, value=1).pack(side="left", padx=5)
        ttk.Radiobutton(header_frame, text="Строка 2", variable=self.header_row, value=2).pack(side="left", padx=5)
        ttk.Radiobutton(header_frame, text="Строка 3", variable=self.header_row, value=3).pack(side="left", padx=5)
        ttk.Radiobutton(header_frame, text="Строка 4", variable=self.header_row, value=4).pack(side="left", padx=5)

    def create_compare_section(self):
        """Create column comparison section"""
        self.compare_frame = ttk.LabelFrame(self.middle_frame, text="3. Столбцы для сравнения", padding=10)
        self.compare_frame.pack(fill="x", pady=5)

        ttk.Label(self.compare_frame, text="Столбец в таблице Жильцов:").grid(row=0, column=0, sticky="w", padx=5,
                                                                              pady=2)
        self.resident_id_combo = ttk.Combobox(self.compare_frame, state="readonly")
        self.resident_id_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(self.compare_frame, text="Столбец в таблице Должников:").grid(row=0, column=2, sticky="w", padx=5,
                                                                                pady=2)
        self.debtor_id_combo = ttk.Combobox(self.compare_frame, state="readonly")
        self.debtor_id_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=2)

        self.compare_frame.grid_columnconfigure(1, weight=1)
        self.compare_frame.grid_columnconfigure(3, weight=1)

    def create_settings_section(self):
        """Create marking settings section"""
        self.settings_frame = ttk.LabelFrame(self.middle_frame, text="4. Настройки маркировки", padding=10)
        self.settings_frame.pack(fill="x", pady=5)

        ttk.Radiobutton(self.settings_frame, text="Создать новый столбец",
                        variable=self.column_mode, value="new",
                        command=self.toggle_column_mode).grid(row=0, column=0, sticky="w", padx=5, pady=2)

        ttk.Radiobutton(self.settings_frame, text="Использовать существующий(временно не работает)",
                        variable=self.column_mode, value="existing",
                        command=self.toggle_column_mode).grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ttk.Radiobutton(self.settings_frame, text="Обновить существующий(временно не работает)",
                        variable=self.column_mode, value="update",
                        command=self.toggle_column_mode).grid(row=0, column=2, sticky="w", padx=5, pady=2)

        self.new_col_label = ttk.Label(self.settings_frame, text="Название нового столбца:")
        self.new_col_entry = ttk.Entry(self.settings_frame, validate="key",
                                       validatecommand=(self.root.register(self.validate_text_input), '%P'))
        self.new_col_entry.insert(0, self.new_column_name)

        self.existing_col_label = ttk.Label(self.settings_frame, text="Выберите столбец для отметки:")
        self.existing_col_combo = ttk.Combobox(self.settings_frame, state="readonly")

        self.update_method_label = ttk.Label(self.settings_frame, text="Метод обновления:")
        self.replace_radio = ttk.Radiobutton(self.settings_frame, text="Заменить значения",
                                             variable=self.update_method, value="replace")
        self.append_radio = ttk.Radiobutton(self.settings_frame, text="Дописать к значениям",
                                            variable=self.update_method, value="append")

        ttk.Label(self.settings_frame, text="Значение для должников:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.mark_entry = ttk.Entry(self.settings_frame)
        self.mark_entry.insert(0, "Должник")
        self.mark_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(self.settings_frame, text="Значение для НЕ должников:").grid(row=3, column=2, sticky="w", padx=5,
                                                                               pady=2)
        self.non_debtor_entry = ttk.Entry(self.settings_frame)
        self.non_debtor_entry.grid(row=3, column=3, sticky="ew", padx=5, pady=2)

        ttk.Button(self.settings_frame, text="Выполнить маркировку",
                   command=self.mark_debtors).grid(row=4, column=0, columnspan=4, pady=10)

        for i in range(4):
            self.settings_frame.grid_columnconfigure(i, weight=1)

    def create_color_section(self):
        """Create color selection section"""
        color_frame = ttk.LabelFrame(self.middle_frame, text="5. Настройка цветов", padding=10)
        color_frame.pack(fill="x", pady=5)

        ttk.Label(color_frame, text="Цвет должников:").grid(row=0, column=0, padx=5, pady=5)
        self.debtor_color_btn = tk.Button(color_frame, text="Выбрать", bg="#FFFF00",
                                          command=lambda: self.choose_color("debtor"))
        self.debtor_color_btn.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(color_frame, text="Цвет НЕ должников:").grid(row=0, column=2, padx=5, pady=5)
        self.non_debtor_color_btn = tk.Button(color_frame, text="Выбрать", bg="#FFFFFF",
                                              command=lambda: self.choose_color("non_debtor"))
        self.non_debtor_color_btn.grid(row=0, column=3, padx=5, pady=5)

        for i in range(4):
            color_frame.grid_columnconfigure(i, weight=1)

    def create_result_section(self):
        """Create results display section"""
        result_frame = ttk.LabelFrame(self.bottom_frame, text="6. Результат", padding=10)
        result_frame.pack(fill="both", expand=True, pady=5)

        self.tree = ttk.Treeview(result_frame)
        self.tree.pack(side="left", fill="both", expand=True)

        y_scroll = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        y_scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=y_scroll.set)

        x_scroll = ttk.Scrollbar(result_frame, orient="horizontal", command=self.tree.xview)
        x_scroll.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=x_scroll.set)

    def create_export_section(self):
        """Create export buttons section"""
        export_frame = ttk.Frame(self.bottom_frame)
        export_frame.pack(fill="x", pady=5)

        ttk.Button(export_frame, text="Сохранить с форматированием",
                   command=self.save_with_formatting).pack(side="left", padx=5)

        ttk.Button(export_frame, text="Экспорт в Excel",
                   command=lambda: self.save_result("xlsx")).pack(side="left", padx=5)

        ttk.Button(export_frame, text="Экспорт в CSV",
                   command=lambda: self.save_result("csv")).pack(side="left", padx=5)

    def setup_validation(self):
        """Setup validation for entry fields"""
        self.root.register(self.validate_text_input, '%P')

    def validate_text_input(self, text):
        """Basic text validation"""
        return len(text) <= 50

    def setup_event_handlers(self):
        """Setup event handlers for UI elements"""
        self.selected_resident_sheet.trace_add('write', self.on_resident_sheet_changed)
        self.selected_debtor_sheet.trace_add('write', self.on_debtor_sheet_changed)
        self.header_row.trace_add('write', self.on_header_row_changed)
        self.resident_id_combo.bind("<<ComboboxSelected>>", self.on_resident_id_changed)
        self.debtor_id_combo.bind("<<ComboboxSelected>>", self.on_debtor_id_changed)

    def on_resident_sheet_changed(self, *args):
        """Handle resident sheet selection change"""
        if self.original_residents_path and self.selected_resident_sheet.get():
            try:
                sheet_name = self.selected_resident_sheet.get()
                self.residents_df = self.load_data_file(self.original_residents_path, sheet_name)
                self.update_column_comboboxes()
                self.display_result(self.residents_df)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить лист:\n{str(e)}")

    def on_debtor_sheet_changed(self, *args):
        """Handle debtor sheet selection change"""
        if self.original_debtors_path and self.selected_debtor_sheet.get():
            try:
                sheet_name = self.selected_debtor_sheet.get()
                self.debtors_df = self.load_data_file(self.original_debtors_path, sheet_name)

                if self.debtors_df is not None and not self.debtors_df.empty:
                    columns = [str(col) for col in self.debtors_df.columns.tolist()]
                    self.debtor_id_combo['values'] = columns
                    if columns:
                        self.debtor_id_combo.set(columns[0])
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить лист:\n{str(e)}")

    def on_header_row_changed(self, *args):
        """Handle header row change"""
        if self.original_residents_path:
            try:
                sheet_name = self.selected_resident_sheet.get() if self.selected_resident_sheet.get() else None
                self.residents_df = self.load_data_file(self.original_residents_path, sheet_name)
                self.update_column_comboboxes()
                self.display_result(self.residents_df)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить данные:\n{str(e)}")

    def on_resident_id_changed(self, event):
        """Handle resident ID column selection change"""
        self.resident_id_column = self.resident_id_combo.get()
        self.display_result(self.residents_df if self.result_df is None else self.result_df)

    def on_debtor_id_changed(self, event):
        """Handle debtor ID column selection change"""
        self.debtor_id_column = self.debtor_id_combo.get()

    def toggle_column_mode(self):
        """Toggle between column modes"""
        mode = self.column_mode.get()

        self.new_col_label.grid_remove()
        self.new_col_entry.grid_remove()
        self.existing_col_label.grid_remove()
        self.existing_col_combo.grid_remove()
        self.update_method_label.grid_remove()
        self.replace_radio.grid_remove()
        self.append_radio.grid_remove()

        if mode == "new":
            self.new_col_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
            self.new_col_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        elif mode == "existing":
            self.existing_col_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
            self.existing_col_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        elif mode == "update":
            self.existing_col_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
            self.existing_col_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
            self.update_method_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)
            self.replace_radio.grid(row=2, column=1, sticky="w", padx=5, pady=2)
            self.append_radio.grid(row=2, column=2, sticky="w", padx=5, pady=2)

    def choose_color(self, color_type):
        """Choose color for debtors/non-debtors"""
        color_code = colorchooser.askcolor(title=f"Выберите цвет для {color_type}")[1]
        if color_code:
            if color_type == "debtor":
                self.debtor_color = color_code.replace("#", "")
                self.debtor_color_btn.config(bg=color_code)
            elif color_type == "non_debtor":
                self.non_debtor_color = color_code.replace("#", "")
                self.non_debtor_color_btn.config(bg=color_code)

    def detect_file_encoding(self, file_path):
        """Detect file encoding"""
        with open(file_path, 'rb') as f:
            rawdata = f.read(10000)
            result = chardet.detect(rawdata)
            return result['encoding']

    def get_excel_sheets(self, file_path):
        """Get sheet names from Excel file"""
        try:
            if file_path.endswith('.xlsx'):
                with pd.ExcelFile(file_path, engine='openpyxl') as xls:
                    return xls.sheet_names
            elif file_path.endswith('.xls'):
                with pd.ExcelFile(file_path, engine='xlrd') as xls:
                    return xls.sheet_names
            return []
        except Exception as e:
            print(f"Error getting sheets: {str(e)}")
            return []

    def load_residents(self):
        """Load residents data"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл с таблицей Жильцы",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            self.original_residents_path = file_path

            if file_path.endswith(('.xlsx', '.xls')):
                try:
                    self.original_wb = load_workbook(file_path)
                except Exception as e:
                    print(f"Failed to load formatting: {str(e)}")
                    self.original_wb = None

            self.resident_sheets = self.get_excel_sheets(file_path)
            if self.resident_sheets:
                self.resident_sheet_combo['values'] = self.resident_sheets
                self.resident_sheet_combo.set(self.resident_sheets[0])
                self.selected_resident_sheet.set(self.resident_sheets[0])

            sheet_name = self.selected_resident_sheet.get() if self.resident_sheets else None
            self.residents_df = self.load_data_file(file_path, sheet_name)

            if self.residents_df is None or self.residents_df.empty:
                raise ValueError("Файл не содержит данных или не может быть прочитан")

            self.update_column_comboboxes()
            self.display_result(self.residents_df)

            messagebox.showinfo("Успех", f"Таблица Жильцы загружена!\nЗаписей: {len(self.residents_df)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def load_debtors(self):
        """Load debtors data"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл с таблицей Должники",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            self.original_debtors_path = file_path

            self.debtor_sheets = self.get_excel_sheets(file_path)
            if self.debtor_sheets:
                self.debtor_sheet_combo['values'] = self.debtor_sheets
                self.debtor_sheet_combo.set(self.debtor_sheets[0])
                self.selected_debtor_sheet.set(self.debtor_sheets[0])

            sheet_name = self.selected_debtor_sheet.get() if self.debtor_sheets else None
            self.debtors_df = self.load_data_file(file_path, sheet_name)

            if self.debtors_df is None or self.debtors_df.empty:
                raise ValueError("Файл не содержит данных или не может быть прочитан")

            columns = [str(col) for col in self.debtors_df.columns.tolist()]
            self.debtor_id_combo['values'] = columns
            if columns:
                self.debtor_id_combo.set(columns[0])

            messagebox.showinfo("Успех", f"Таблица Должники загружена!\nЗаписей: {len(self.debtors_df)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def load_data_file(self, file_path, sheet_name=None):
        """Load data from file with error handling"""
        try:
            if file_path.endswith('.csv'):
                return self.load_csv_file(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                return self.load_excel_file(file_path, sheet_name)
            else:
                return self.try_unknown_format(file_path)
        except Exception as e:
            print(f"Error loading file: {str(e)}")
            return None

    def load_csv_file(self, file_path):
        """Load CSV file with automatic settings detection"""
        encoding = self.detect_file_encoding(file_path)

        for delimiter in [',', ';', '\t', '|']:
            try:
                df = pd.read_csv(
                    file_path,
                    encoding=encoding,
                    header=self.header_row.get() - 1,
                    delimiter=delimiter,
                    dtype=str,
                    on_bad_lines='warn'
                )
                df = self.clean_dataframe(df)
                if not df.empty:
                    return df
            except:
                continue

        try:
            df = pd.read_csv(file_path, header=self.header_row.get() - 1, dtype=str)
            return self.clean_dataframe(df)
        except Exception as e:
            raise ValueError(f"Не удалось загрузить CSV файл: {str(e)}")

    def load_excel_file(self, file_path, sheet_name=None):
        """Load Excel file"""
        engine = 'openpyxl' if file_path.endswith('.xlsx') else 'xlrd'
        try:
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                header=self.header_row.get() - 1,
                engine=engine,
                dtype=str
            )
            return self.clean_dataframe(df)
        except Exception as e:
            raise ValueError(f"Не удалось загрузить Excel файл: {str(e)}")

    def clean_dataframe(self, df):
        """Clean and prepare dataframe"""
        if df is None:
            return None

        df = df.dropna(axis=1, how='all')
        df = df.dropna(how='all')
        self.rename_unnamed_columns(df)

        return df

    def rename_unnamed_columns(self, df):
        """Rename unnamed columns to A, B, C,..."""
        if df is not None:
            new_columns = []
            for i, col in enumerate(df.columns):
                if pd.isna(col) or str(col).strip() == '' or str(col).startswith('Unnamed'):
                    col_name = ''
                    n = i
                    while n >= 0:
                        col_name = ascii_uppercase[n % 26] + col_name
                        n = n // 26 - 1
                    new_columns.append(col_name)
                else:
                    new_columns.append(str(col).strip())
            df.columns = new_columns

    def update_column_comboboxes(self):
        """Update column selection comboboxes"""
        if self.residents_df is not None:
            columns = [str(col) for col in self.residents_df.columns.tolist()]
            self.resident_id_combo['values'] = columns
            self.existing_col_combo['values'] = columns

            if columns:
                id_cols = self.find_id_columns(self.residents_df)
                self.resident_id_combo.set(id_cols[0] if id_cols else columns[0])
                self.existing_col_combo.set(columns[-1])

    def find_id_columns(self, df):
        """Find columns that might contain IDs"""
        possible_names = ['id', 'номер', 'код', 'account', 'uid', 'уникальный', 'unique']
        result = []
        for col in df.columns:
            col_lower = str(col).lower()
            for name in possible_names:
                if name in col_lower:
                    result.append(col)
                    break
        return result

    def mark_debtors(self):
        """Main marking function with improved error handling"""
        try:
            self.validate_before_marking()

            params = self.get_marking_parameters()

            self.mark_column = params['mark_col']
            self.resident_id_column = params['resident_col']
            self.debtor_id_column = params['debtor_col']

            self.result_df = self.perform_marking(params)

            self.display_result(self.result_df)

            self.show_marking_stats(params)

        except Exception as e:
            messagebox.showerror("Ошибка маркировки",
                                 f"Не удалось выполнить маркировку:\n{str(e)}\n\n"
                                 f"Подробности:\n{traceback.format_exc()}")

    def validate_before_marking(self):
        """Improved validation before marking"""
        errors = []

        if self.residents_df is None:
            errors.append("Не загружена таблица жильцов")
        if self.debtors_df is None:
            errors.append("Не загружена таблица должников")

        resident_col = self.resident_id_combo.get()
        debtor_col = self.debtor_id_combo.get()

        if not resident_col:
            errors.append("Не выбран столбец ID жильцов")
        elif resident_col not in self.residents_df.columns:
            errors.append(f"Столбец '{resident_col}' не найден в таблице жильцов")

        if not debtor_col:
            errors.append("Не выбран столбец ID должников")
        elif debtor_col not in self.debtors_df.columns:
            errors.append(f"Столбец '{debtor_col}' не найден в таблице должников")

        if not self.mark_entry.get().strip():
            errors.append("Не указано значение для отметки должников")

        if errors:
            raise ValueError("\n".join(errors))

    def get_marking_parameters(self):
        """Get marking parameters with additional validation"""
        params = {
            'resident_col': self.resident_id_combo.get(),
            'debtor_col': self.debtor_id_combo.get(),
            'mark_value': self.mark_entry.get().strip(),
            'non_debtor_value': self.non_debtor_entry.get().strip(),
            'mode': self.column_mode.get(),
            'update_method': self.update_method.get()
        }

        if params['mode'] == "new":
            params['mark_col'] = self.new_col_entry.get().strip()
            if not params['mark_col']:
                raise ValueError("Введите название нового столбца")
            if params['mark_col'] in self.residents_df.columns:
                raise ValueError(f"Столбец '{params['mark_col']}' уже существует")
        else:
            params['mark_col'] = self.existing_col_combo.get()
            if not params['mark_col']:
                raise ValueError("Выберите существующий столбец")

        return params

    def perform_marking(self, params):
        """Perform the actual marking"""
        result_df = self.residents_df.copy()

        debtor_ids = self.get_debtor_ids(params['debtor_col'])

        mask = result_df[params['resident_col']].astype(str).str.strip().isin(debtor_ids)

        if params['mode'] == "new":
            result_df[params['mark_col']] = params['non_debtor_value'] if params['non_debtor_value'] else ""
            result_df.loc[mask, params['mark_col']] = params['mark_value']
        elif params['mode'] == "existing":
            result_df.loc[mask, params['mark_col']] = params['mark_value']
            if params['non_debtor_value']:
                result_df.loc[~mask, params['mark_col']] = params['non_debtor_value']
        elif params['mode'] == "update":
            if params['update_method'] == "replace":
                result_df.loc[mask, params['mark_col']] = params['mark_value']
                if params['non_debtor_value']:
                    result_df.loc[~mask, params['mark_col']] = params['non_debtor_value']
            else:
                result_df.loc[mask, params['mark_col']] = (
                        result_df.loc[mask, params['mark_col']].astype(str) + " " + params['mark_value']
                )
                if params['non_debtor_value']:
                    result_df.loc[~mask, params['mark_col']] = (
                            result_df.loc[~mask, params['mark_col']].astype(str) + " " + params['non_debtor_value']
                    )

        return result_df.fillna('')

    def get_debtor_ids(self, debtor_col):
        """Get unique debtor IDs with cleaning"""
        debtor_ids = self.debtors_df[debtor_col].dropna()
        debtor_ids = debtor_ids[debtor_ids.astype(str).str.strip() != '']
        return debtor_ids.astype(str).str.strip().unique()

    def display_result(self, df):
        """Display results in treeview with improved formatting"""
        try:
            if df is None:
                return

            self.tree.delete(*self.tree.get_children())

            columns_to_show = []

            if hasattr(self, 'mark_column') and self.mark_column in df.columns:
                columns_to_show.append(self.mark_column)

            if hasattr(self, 'resident_id_column') and self.resident_id_column in df.columns:
                if self.resident_id_column not in columns_to_show:
                    columns_to_show.insert(0, self.resident_id_column)

            other_columns = [col for col in df.columns
                             if col not in columns_to_show and not str(col).startswith('Unnamed')]
            columns_to_show.extend(other_columns[:3])

            self.tree["columns"] = columns_to_show
            for col in columns_to_show:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=150, anchor="w", stretch=tk.YES)

                if col == self.mark_column:
                    self.tree.heading(col, text=f"★ {col} ★")
                elif col == self.resident_id_column:
                    self.tree.heading(col, text=f"→ {col}")

            sample_size = min(500, len(df))
            for _, row in df.iloc[:sample_size].iterrows():
                values = [row[col] if col in df.columns else "" for col in columns_to_show]
                self.tree.insert("", "end", values=values)

        except Exception as e:
            print(f"Error displaying results: {str(e)}")

    def show_marking_stats(self, params):
        """Show marking statistics with more details"""
        try:
            mask = self.result_df[params['resident_col']].astype(str).str.strip().isin(
                self.get_debtor_ids(params['debtor_col'])
            )
            num_debtors = mask.sum()
            num_non_debtors = len(self.result_df) - num_debtors

            stats_message = (
                f"Должники успешно отмечены!\n\n"
                f"Всего жильцов: {len(self.result_df)}\n"
                f"Найдено должников: {num_debtors}\n"
                f"Не должников: {num_non_debtors}\n\n"
                f"Сравнивались столбцы:\n"
                f"Жильцы: '{params['resident_col']}'\n"
                f"Должники: '{params['debtor_col']}'\n\n"
                f"Столбец для отметки: '{params['mark_col']}'\n"
                f"Режим: {'новый столбец' if params['mode'] == 'new' else 'существующий столбец' if params['mode'] == 'existing' else 'обновление столбца (' + params['update_method'] + ')'}"
            )

            messagebox.showinfo("Результаты маркировки", stats_message)

        except Exception as e:
            messagebox.showerror("Ошибка статистики", f"Не удалось показать статистику:\n{str(e)}")

    def save_with_formatting(self):
        """Save with original formatting with comprehensive validation"""
        try:
            if not self.validate_before_saving():
                return

            file_path = filedialog.asksaveasfilename(
                title="Сохранить с форматированием",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=f"marked_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )

            if not file_path:
                return

            try:
                wb, ws = self.prepare_workbook()
            except Exception as e:
                raise ValueError(f"Не удалось подготовить файл для сохранения: {str(e)}")

            try:
                # Проверяем, что столбцы существуют в result_df
                if self.mark_column not in self.result_df.columns:
                    raise ValueError(f"Столбец '{self.mark_column}' не найден в данных")
                if self.resident_id_column not in self.result_df.columns:
                    raise ValueError(f"Столбец '{self.resident_id_column}' не найден в данных")

                mark_col_idx = self.find_column_index(ws, self.mark_column, is_critical=False)
                resident_col_idx = self.find_column_index(ws, self.resident_id_column)

                if mark_col_idx is None and self.column_mode.get() == "new":
                    mark_col_idx = ws.max_column + 1
                    ws.cell(row=self.header_row.get(), column=mark_col_idx, value=self.mark_column)

                if resident_col_idx is None:
                    raise ValueError(f"Не удалось найти столбец '{self.resident_id_column}' в файле")

            except Exception as e:
                raise ValueError(f"Ошибка поиска столбцов: {str(e)}")

            try:
                self.apply_formatting(ws, mark_col_idx, resident_col_idx)
            except Exception as e:
                raise ValueError(f"Ошибка применения форматирования: {str(e)}")

            try:
                wb.save(file_path)
                messagebox.showinfo("Успех", "Файл успешно сохранён с форматированием!")
            except Exception as e:
                raise ValueError(f"Ошибка сохранения файла: {str(e)}")

        except Exception as e:
            error_msg = f"Не удалось сохранить файл:\n{str(e)}"
            if hasattr(e, '__traceback__'):
                error_msg += f"\n\nПодробности:\n{traceback.format_exc()}"
            messagebox.showerror("Ошибка сохранения", error_msg)

    def validate_before_saving(self):
        """Validate data before saving"""
        errors = []

        if self.result_df is None:
            errors.append("Нет данных для сохранения")
        if not self.original_residents_path:
            errors.append("Исходный файл жильцов не загружен")
        if not hasattr(self, 'mark_column') or not self.mark_column:
            errors.append("Не выбран столбец для отметки")
        if not hasattr(self, 'resident_id_column') or not self.resident_id_column:
            errors.append("Не выбран столбец с ID жильцов")

        # Дополнительная проверка, что столбцы существуют в результате
        if self.result_df is not None:
            if hasattr(self, 'mark_column') and self.mark_column not in self.result_df.columns:
                errors.append(f"Столбец для отметки '{self.mark_column}' не найден в данных")
            if hasattr(self, 'resident_id_column') and self.resident_id_column not in self.result_df.columns:
                errors.append(f"Столбец ID жильцов '{self.resident_id_column}' не найден в данных")

        if errors:
            messagebox.showerror("Ошибка сохранения", "\n".join(errors))
            return False
        return True

    def prepare_workbook(self):
        """Prepare workbook for saving with error handling"""
        if self.original_wb is None:
            try:
                self.original_wb = load_workbook(self.original_residents_path)
            except Exception as e:
                print(f"Failed to load original file: {str(e)}")
                self.original_wb = Workbook()
                ws = self.original_wb.active
                for col_num, column in enumerate(self.residents_df.columns, 1):
                    ws.cell(row=1, column=col_num, value=column)
                for row_num, row in enumerate(self.residents_df.values, 2):
                    for col_num, value in enumerate(row, 1):
                        ws.cell(row=row_num, column=col_num, value=value)

        wb = copy(self.original_wb)
        sheet_name = self.selected_resident_sheet.get() if self.selected_resident_sheet.get() else wb.sheetnames[0]

        try:
            ws = wb[sheet_name]
        except KeyError:
            ws = wb.active
            print(f"Sheet '{sheet_name}' not found, using active sheet")

        return wb, ws

    def find_column_index(self, ws, column_name, is_critical=True):
        """
        Find column index by name with flexible matching
        Args:
            ws: Worksheet object
            column_name: Name of column to find
            is_critical: If True, raises error when column not found
        Returns:
            Column index (1-based) or None if not found and not critical
        """
        if not column_name:
            if is_critical:
                raise ValueError("Не указано имя столбца для поиска")
            return None

        header_row = self.header_row.get()

        # Проверка, что header_row не превышает количество строк в файле
        if header_row > ws.max_row:
            if is_critical:
                raise ValueError(
                    f"Строка заголовков {header_row} не существует в файле (максимальная строка: {ws.max_row})")
            return None

        column_name = str(column_name).strip().lower()
        found_cols = []

        for col in range(1, ws.max_column + 1):
            cell_value = str(ws.cell(row=header_row, column=col).value or "").strip().lower()
            if cell_value == column_name:
                return col
            if column_name in cell_value:
                found_cols.append(col)

        # Если точного совпадения нет, попробуем найти похожие
        if found_cols:
            return found_cols[0]

        # Попробуем очистить от специальных символов
        clean_search = re.sub(r'[^a-zа-я0-9]', '', column_name)
        for col in range(1, ws.max_column + 1):
            cell_value = str(ws.cell(row=header_row, column=col).value or "")
            clean_cell = re.sub(r'[^a-zа-я0-9]', '', cell_value.strip().lower())
            if clean_search == clean_cell:
                return col

        if is_critical:
            available_columns = [str(ws.cell(row=header_row, column=col).value or "") for col in
                                 range(1, min(ws.max_column + 1, 10))]
            raise ValueError(
                f"Столбец '{column_name}' не найден в файле. Доступные столбцы: {', '.join(available_columns)}..."
            )
        return None

    def apply_formatting(self, ws, mark_col_idx, resident_col_idx):
        """Apply formatting to worksheet with robust error handling"""
        try:
            if mark_col_idx is None or resident_col_idx is None:
                raise ValueError("Не найдены индексы столбцов для форматирования")

            if not isinstance(mark_col_idx, int) or not isinstance(resident_col_idx, int):
                raise ValueError("Некорректные индексы столбцов")

            if resident_col_idx > ws.max_column or mark_col_idx > ws.max_column:
                raise ValueError(f"Столбцы выходят за пределы таблицы (макс: {ws.max_column})")

            debtor_ids = self.get_debtor_ids(self.debtor_id_column)

            debtor_fill = PatternFill(
                start_color=self.debtor_color,
                end_color=self.debtor_color,
                fill_type="solid"
            )
            non_debtor_fill = PatternFill(
                start_color=self.non_debtor_color,
                end_color=self.non_debtor_color,
                fill_type="solid"
            )

            header_row = self.header_row.get()

            for row in range(header_row + 1, ws.max_row + 1):
                try:
                    resident_id = str(ws.cell(row=row, column=resident_col_idx).value or "").strip()
                    cell = ws.cell(row=row, column=mark_col_idx)

                    if resident_id in debtor_ids:
                        cell.value = self.mark_entry.get()
                        cell.fill = debtor_fill
                    else:
                        cell.value = self.non_debtor_entry.get() if self.non_debtor_entry.get() else ""
                        cell.fill = non_debtor_fill
                except Exception as e:
                    print(f"Ошибка форматирования строки {row}: {str(e)}")
                    continue

        except Exception as e:
            raise ValueError(f"Ошибка при применении форматирования: {str(e)}")

    def save_result(self, file_type):
        """Save result without formatting"""
        try:
            if self.result_df is None:
                messagebox.showerror("Ошибка", "Нет данных для сохранения!")
                return

            if file_type == "csv":
                filetypes = [("CSV files", "*.csv")]
                defaultext = ".csv"
            else:
                filetypes = [("Excel files", "*.xlsx")]
                defaultext = ".xlsx"

            file_path = filedialog.asksaveasfilename(
                title=f"Экспорт в {file_type.upper()}",
                defaultextension=defaultext,
                filetypes=filetypes,
                initialfile=f"marked_{datetime.now().strftime('%Y%m%d_%H%M%S')}{defaultext}"
            )

            if not file_path:
                return

            if file_type == "csv":
                self.result_df.to_csv(file_path, index=False, encoding='utf-8-sig')
            else:
                self.result_df.to_excel(file_path, index=False, engine='openpyxl')

            messagebox.showinfo("Успех", f"Файл успешно экспортирован в {file_type.upper()}!")

        except Exception as e:
            messagebox.showerror("Ошибка экспорта",
                                 f"Не удалось экспортировать файл:\n{str(e)}\n\n"
                                 f"Подробности:\n{traceback.format_exc()}")

    def try_unknown_format(self, file_path):
        """Try to load file of unknown format"""
        try:
            return pd.read_excel(file_path, header=self.header_row.get() - 1, dtype=str)
        except:
            try:
                return pd.read_csv(file_path, header=self.header_row.get() - 1, dtype=str)
            except Exception as e:
                raise ValueError(f"Неизвестный формат файла: {str(e)}")


def check_dependencies():
    """Check for required dependencies"""
    try:
        import xlrd
        import openpyxl
        import pandas as pd
        import chardet
        return True
    except ImportError as e:
        error_msg = (
            f"Отсутствуют необходимые зависимости:\n{str(e)}\n\n"
            "Установите их командой:\n"
            "pip install pandas numpy openpyxl xlrd chardet"
        )

        try:
            tk.Tk().withdraw()
            messagebox.showerror("Ошибка зависимостей", error_msg)
        except:
            print(error_msg)

        input("Нажмите Enter для выхода...")
        return False


if __name__ == "__main__":
    if check_dependencies():
        root = tk.Tk()
        app = DebtMarkerApp(root)
        root.mainloop()