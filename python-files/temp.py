import tkinter as tk
from tkinter import ttk, font, messagebox, filedialog
import pandas as pd
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import json
import os
import shutil

class ConfigManager:
    """Керує завантаженням та збереженням конфігурацій, наприклад, ширини стовпців."""
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def get_table_settings(self, table_id):
        return self.config.get(table_id, {})

    def save_table_settings(self, table_id, settings):
        self.config[table_id] = settings
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Помилка збереження", f"Не вдалося зберегти налаштування: {e}")

class DatabaseManager:
    """Керує всіма операціями з базою даних в Excel-файлі."""
    def __init__(self):
        desktop_path = Path.home() / "Desktop"
        self.db_folder = desktop_path / "MilPro"
        self.db_path = self.db_folder / "database.xlsx"
        self.initialize_database()

    def initialize_database(self):
        try:
            if not self.db_folder.exists(): self.db_folder.mkdir(parents=True, exist_ok=True)
            
            sheets_to_create = {
                "Підрозділи": pd.DataFrame(columns=["№", "Назва", "МВО"]),
                "Майнові позиції": pd.DataFrame(columns=["№", "Назва", "Номен. код", "Ціна", "Зав. №"]),
                "Журнал операцій": pd.DataFrame(columns=["№ запису", "Дата запису", "Тип документа", "Номер документа", "Підрозділ-відправник", "Підрозділ-отримувач"]),
                "Описові документи": pd.DataFrame(columns=["№ Запису", "Дата запису", "Назва документа", "Номер документа", "Примітки"])
            }

            if not self.db_path.exists():
                with pd.ExcelWriter(self.db_path, engine='openpyxl') as writer:
                    for sheet_name, df in sheets_to_create.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                with pd.ExcelWriter(self.db_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                    xls = pd.ExcelFile(self.db_path)
                    for sheet_name, df_template in sheets_to_create.items():
                        if sheet_name not in xls.sheet_names:
                            df_template.to_excel(writer, sheet_name=sheet_name, index=False)
        except Exception as e: messagebox.showerror("Помилка ініціалізації", f"Не вдалося створити/оновити файл бази даних: {e}")
    
    def get_sheet_names(self):
        try:
            return pd.ExcelFile(self.db_path).sheet_names
        except FileNotFoundError:
            return []
        except Exception as e:
            messagebox.showerror("Помилка читання", f"Не вдалося отримати список аркушів: {e}")
            return []

    def read_data(self, sheet_name):
        try: return pd.read_excel(self.db_path, sheet_name=sheet_name, dtype=str).fillna('')
        except ValueError: return pd.DataFrame()
        except Exception as e: messagebox.showerror("Помилка читання", f"Не вдалося прочитати дані з '{sheet_name}': {e}"); return pd.DataFrame()

    def write_data(self, sheet_name, data_df):
        try:
            with pd.ExcelWriter(self.db_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                data_df.to_excel(writer, sheet_name=sheet_name, index=False)
        except Exception as e: messagebox.showerror("Помилка запису", f"Не вдалося записати дані в '{sheet_name}': {e}")

    def get_column_values(self, sheet_name, column_name):
        df = self.read_data(sheet_name)
        if not df.empty and column_name in df.columns: return df[column_name].dropna().unique().tolist()
        return []

class AttachmentsWindow(tk.Toplevel):
    """Вікно для керування прикріпленими PDF-документами."""
    def __init__(self, parent_widget, app_instance, milpro_folder_path, record_id, prefix):
        super().__init__(parent_widget)
        self.app = app_instance
        self.record_id = record_id
        self.prefix = prefix
        self.attachments_path = milpro_folder_path / "attached"
        self.attachments_path.mkdir(exist_ok=True)

        self.title(f"Прикріплені документи до запису №{self.record_id}")
        self.state('zoomed')
        self.transient(parent_widget)
        self.grab_set()
        self.create_widgets()
        self.populate_files()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10"); main_frame.pack(fill="both", expand=True)
        button_frame = ttk.Frame(main_frame); button_frame.pack(fill="x", pady=(0, 10))
        ttk.Button(button_frame, text="Додати", command=self.add_files).pack(side="left")
        ttk.Button(button_frame, text="Видалити", command=self.delete_file).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Відкрити", command=self.open_file).pack(side="left")

        self.tree = ttk.Treeview(main_frame, columns=("filename",), show="headings")
        self.tree.heading("filename", text="Назва файлу")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.open_file)

    def populate_files(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        try:
            file_prefix = f"{self.prefix}_{self.record_id}_"
            for system_filename in os.listdir(self.attachments_path):
                if system_filename.startswith(file_prefix):
                    original_filename = system_filename.replace(file_prefix, "", 1)
                    self.tree.insert("", "end", iid=system_filename, values=(original_filename,))
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося прочитати список файлів: {e}")

    def add_files(self):
        filepaths = filedialog.askopenfilenames(title="Оберіть PDF файли для додавання", filetypes=[("PDF Documents", "*.pdf"), ("All files", "*.*")])
        if not filepaths: return

        for src_path in filepaths:
            try:
                original_filename = os.path.basename(src_path)
                dest_filename = f"{self.prefix}_{self.record_id}_{original_filename}"
                dest_path = self.attachments_path / dest_filename
                shutil.copy(src_path, dest_path)
            except Exception as e:
                messagebox.showwarning("Помилка копіювання", f"Не вдалося скопіювати файл {original_filename}:\n{e}")
        
        self.populate_files()
        self.app.refresh_application_data()


    def delete_file(self):
        selected_item_iid = self.tree.selection()
        if not selected_item_iid:
            messagebox.showwarning("Увага", "Будь ласка, оберіть файл для видалення."); return

        system_filename = selected_item_iid[0]
        original_filename = self.tree.item(system_filename, "values")[0]
        if messagebox.askyesno("Підтвердження", f"Ви впевнені, що хочете видалити файл '{original_filename}'?"):
            try:
                os.remove(self.attachments_path / system_filename)
                self.populate_files()
                self.app.refresh_application_data()
            except Exception as e: messagebox.showerror("Помилка видалення", f"Не вдалося видалити файл: {e}")

    def open_file(self, event=None):
        selected_item_iid = self.tree.selection()
        if not selected_item_iid:
            messagebox.showwarning("Увага", "Будь ласка, оберіть файл для відкриття."); return
        system_filename = selected_item_iid[0]
        filepath = self.attachments_path / system_filename
        try: os.startfile(filepath)
        except Exception as e: messagebox.showerror("Помилка відкриття", f"Не вдалося відкрити файл: {e}")

class AssetAnalytics:
    def __init__(self, db_manager):
        self.db_manager, self.asset_info = db_manager, pd.DataFrame()
        self.excluded_subdivisions = {"Постачальник", "Списання"}
    def refresh_asset_info(self):
        asset_data = self.db_manager.read_data("Майнові позиції")
        if not asset_data.empty and "Назва" in asset_data.columns:
            asset_data.drop_duplicates(subset=['Назва'], keep='last', inplace=True); self.asset_info = asset_data.set_index("Назва")
        else: self.asset_info = pd.DataFrame()
    def calculate_balances(self):
        self.refresh_asset_info(); balances = defaultdict(lambda: defaultdict(lambda: {'quantity': 0, 'serials': set()})); operations_df = self.db_manager.read_data("Журнал операцій")
        for _, op in operations_df.iterrows():
            details_df = self.db_manager.read_data(f"details_{op['№ запису']}")
            if details_df.empty: continue
            sender, receiver = op.get('Підрозділ-відправник'), op.get('Підрозділ-отримувач')
            for _, item in details_df.iterrows():
                try:
                    asset_name, quantity, serial = item['Назва'], int(float(item['Кількість'])), item.get('Зав. №') or 'б/н'
                    if sender: balances[sender][asset_name]['quantity'] -= quantity; balances[sender][asset_name]['serials'].discard(serial)
                    if receiver: balances[receiver][asset_name]['quantity'] += quantity; balances[receiver][asset_name]['serials'].add(serial)
                except (ValueError, TypeError, KeyError) as e: print(f"Помилка обробки запису {op['№ запису']}, майно '{item.get('Назва')}': {e}")
        for sub_name in self.excluded_subdivisions: balances.pop(sub_name, None)
        return balances

class AssetsTab(ttk.Frame):
    def __init__(self, parent, db_manager, config_manager):
        super().__init__(parent); self.db_manager, self.config_manager, self.analytics = db_manager, config_manager, AssetAnalytics(db_manager); self.create_widgets(); self.toggle_view()
    
    def refresh_data(self):
        self.toggle_view()

    def create_widgets(self):
        control_frame = ttk.Frame(self); control_frame.pack(fill="x", padx=10, pady=10); ttk.Label(control_frame, text="Режим звіту:").pack(side="left", padx=(0, 10))
        self.view_mode = tk.StringVar(value="subdivision"); ttk.Radiobutton(control_frame, text="По підрозділах", variable=self.view_mode, value="subdivision", command=self.toggle_view).pack(side="left", padx=5); ttk.Radiobutton(control_frame, text="По майну", variable=self.view_mode, value="asset", command=self.toggle_view).pack(side="left", padx=5)
        self.filter_var = tk.StringVar(); self.filter_combo = ttk.Combobox(control_frame, textvariable=self.filter_var, width=40, state="readonly"); self.filter_combo.bind("<<ComboboxSelected>>", self.run_report); self.filter_combo.pack(side="left", padx=20)
        self.export_button = ttk.Button(control_frame, text="Експортувати звіт", command=self.export_report, state="disabled"); self.export_button.pack(side="left", padx=5)
        table_frame = ttk.Frame(self); table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5)); self.tree = ttk.Treeview(table_frame)
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview); self.tree.configure(yscrollcommand=vsb.set); vsb.pack(side="right", fill="y"); self.tree.pack(fill="both", expand=True)
        summary_frame = ttk.Frame(self); summary_frame.pack(fill="x", padx=10, pady=(0, 10)); self.total_quantity_var, self.total_value_var = tk.StringVar(value="Загальна кількість: 0"), tk.StringVar(value="Загальна вартість: 0.00")
        summary_font = font.Font(family="Arial", size=10, weight="bold"); ttk.Label(summary_frame, textvariable=self.total_quantity_var, font=summary_font).pack(side="left", padx=5); ttk.Label(summary_frame, textvariable=self.total_value_var, font=summary_font).pack(side="left", padx=20)
        self.context_menu = tk.Menu(self, tearoff=0); self.context_menu.add_command(label="Копіювати", command=self.copy_cell_value); self.context_menu.add_separator(); self.context_menu.add_command(label="Зберегти налаштування таблиці", command=self.save_column_widths); self.tree.bind("<Button-3>", self.show_context_menu)
    def show_context_menu(self, event): self.tree.identify_row(event.y); self.context_menu.tk_popup(event.x_root, event.y_root)
    def copy_cell_value(self):
        if not self.tree.focus(): return
        cur_item = self.tree.focus(); col_id = self.tree.identify_column(self.winfo_pointerx() - self.tree.winfo_rootx())
        if col_id: col_index = int(col_id.replace('#', '')) - 1; value = self.tree.item(cur_item, 'values')[col_index]; self.clipboard_clear(); self.clipboard_append(value)
    def get_current_table_id(self): return f"assets_{self.view_mode.get()}"
    def save_column_widths(self): widths = {col: self.tree.column(col, "width") for col in self.tree['columns']}; self.config_manager.save_table_settings(self.get_current_table_id(), widths); messagebox.showinfo("Збережено", "Налаштування ширини стовпців збережено.")
    def apply_column_widths(self):
        settings = self.config_manager.get_table_settings(self.get_current_table_id())
        for col, width in settings.items():
            if col in self.tree['columns']: self.tree.column(col, width=width)
    def toggle_view(self):
        self.filter_var.set(''); [self.tree.delete(i) for i in self.tree.get_children()]; self.total_quantity_var.set("Загальна кількість: 0"); self.total_value_var.set("Загальна вартість: 0.00"); self.export_button.config(state="disabled")
        mode = self.view_mode.get()
        if mode == "subdivision":
            subdivisions = sorted([s for s in self.db_manager.get_column_values("Підрозділи", "Назва") if s not in self.analytics.excluded_subdivisions]); subdivisions.insert(0, "Загальний звіт"); self.filter_combo['values'] = subdivisions
            self.tree['columns'] = ("asset_name", "nomen_code", "quantity", "total_price", "serials"); self.tree.heading("asset_name", text="Назва майна"); self.tree.heading("nomen_code", text="Номен. код"); self.tree.heading("quantity", text="Кількість"); self.tree.heading("total_price", text="Загальна вартість");
            self.tree.heading("serials", text="Зав. №")
        else:
            self.filter_combo['values'] = sorted(self.db_manager.get_column_values("Майнові позиції", "Назва"))
            self.tree['columns'] = ("subdivision", "quantity", "total_price", "serials"); self.tree.heading("subdivision", text="Підрозділ"); self.tree.heading("quantity", text="Кількість"); self.tree.heading("total_price", text="Загальна вартість"); self.tree.heading("serials", text="Зав. №")
        self.tree.heading("#0", text="", anchor="w"); self.tree.column("#0", width=0, stretch=tk.NO); self.apply_column_widths()
    def run_report(self, event=None):
        if not self.filter_var.get(): return
        main_window = self.winfo_toplevel(); main_window.config(cursor="watch"); self.update()
        try: balances = self.analytics.calculate_balances()
        finally: main_window.config(cursor="")
        [self.tree.delete(i) for i in self.tree.get_children()]; total_quantity, total_value = 0, 0.0
        mode, filter_value = self.view_mode.get(), self.filter_var.get()
        if mode == "subdivision" and filter_value == "Загальний звіт":
            general_report = defaultdict(lambda: {'quantity': 0, 'serials': set()})
            for sub_data in balances.values():
                for asset_name, data in sub_data.items(): general_report[asset_name]['quantity'] += data['quantity']; general_report[asset_name]['serials'].update(data['serials'])
            for asset_name, data in sorted(general_report.items()):
                if data['quantity'] != 0:
                    try: info = self.analytics.asset_info.loc[asset_name]; price = float(info.get("Ціна", "0") or "0"); current_total_price, nomen_code = price * data['quantity'], info.get("Номен. код", "н/д")
                    except (KeyError, ValueError): current_total_price, nomen_code = 0.0, "Не знайдено в довіднику"
                    serials = ", ".join(sorted(list(data['serials']))); self.tree.insert("", "end", values=(asset_name, nomen_code, data['quantity'], f"{current_total_price:.2f}", serials)); total_quantity += data['quantity']; total_value += current_total_price
        elif mode == "subdivision":
            if filter_value in balances:
                for asset_name, data in sorted(balances[filter_value].items()):
                    if data['quantity'] != 0:
                        try: info = self.analytics.asset_info.loc[asset_name]; price = float(info.get("Ціна", "0") or "0"); current_total_price, nomen_code = price * data['quantity'], info.get("Номен. код", "н/д")
                        except (KeyError, ValueError): current_total_price, nomen_code = 0.0, "Не знайдено в довіднику"
                        serials = ", ".join(sorted(list(data['serials']))); self.tree.insert("", "end", values=(asset_name, nomen_code, data['quantity'], f"{current_total_price:.2f}", serials)); total_quantity += data['quantity']; total_value += current_total_price
        else:
            for sub_name, assets in sorted(balances.items()):
                if filter_value in assets and assets[filter_value]['quantity'] != 0:
                    data = assets[filter_value]
                    try: info = self.analytics.asset_info.loc[filter_value]; price = float(info.get("Ціна", "0") or "0"); current_total_price = price * data['quantity']
                    except (KeyError, ValueError): current_total_price = 0.0
                    serials = ", ".join(sorted(list(data['serials']))); self.tree.insert("", "end", values=(sub_name, data['quantity'], f"{current_total_price:.2f}", serials)); total_quantity += data['quantity']; total_value += current_total_price
        self.total_quantity_var.set(f"Загальна кількість: {total_quantity}"); self.total_value_var.set(f"Загальна вартість: {total_value:.2f}"); self.export_button.config(state="normal" if self.tree.get_children() else "disabled")
    def export_report(self):
        if not self.tree.get_children(): messagebox.showwarning("Експорт неможливий", "У звіті немає даних для експорту."); return
        default_filename = f"Звіт_{self.filter_var.get()}_{datetime.now().strftime('%Y-%m-%d')}.txt"
        filepath = filedialog.asksaveasfilename(initialfile=default_filename, defaultextension=".txt", filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"ЗВІТ ПО МАЙНУ\nДата формування: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"); mode_text = "По підрозділах" if self.view_mode.get() == "subdivision" else "По майну"; f.write(f"Режим: {mode_text}\nФільтр: {self.filter_var.get()}\n\n")
                cols = self.tree['columns']; headers = [self.tree.heading(col)['text'] for col in cols]; col_widths = {col: len(header) for col, header in zip(cols, headers)}
                for item in self.tree.get_children():
                    values = self.tree.item(item)['values']
                    for i, val in enumerate(values): col_widths[cols[i]] = max(col_widths[cols[i]], len(str(val)))
                header_line = " | ".join([header.ljust(col_widths[col]) for col, header in zip(cols, headers)]); f.write(header_line + "\n"); f.write("-" * len(header_line) + "\n")
                for item in self.tree.get_children():
                    values = self.tree.item(item)['values']; row_line = " | ".join([str(val).ljust(col_widths[cols[i]]) for i, val in enumerate(values)]); f.write(row_line + "\n")
                f.write("\n" + "=" * len(header_line) + "\n"); f.write(f"{self.total_quantity_var.get()}\n"); f.write(f"{self.total_value_var.get()}\n")
            messagebox.showinfo("Експорт успішний", f"Звіт було успішно збережено у файл:\n{filepath}")
        except Exception as e: messagebox.showerror("Помилка експорту", f"Не вдалося зберегти файл: {e}")

class DetailsWindow(tk.Toplevel):
    def __init__(self, parent_widget, app_instance, db_manager, config_manager, record_id):
        super().__init__(parent_widget)
        self.app = app_instance
        self.db_manager, self.config_manager, self.record_id = db_manager, config_manager, record_id
        self.table_id = "details_window"
        self.sheet_name = f"details_{self.record_id}"
        self.asset_positions = self.db_manager.read_data("Майнові позиції")
        self.title(f"Деталізація запису №{self.record_id}"); self.state('zoomed'); self.transient(parent_widget); self.grab_set(); self.create_widgets(); self.load_data()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self); main_frame.pack(fill="both", expand=True); control_frame = ttk.Frame(main_frame); control_frame.pack(side="left", fill="y", padx=10, pady=10)
        form_frame = ttk.LabelFrame(control_frame, text="Форма заповнення"); form_frame.pack(fill="x", padx=5, pady=5); self.entries = {}
        fields = {"№": "Label", "Назва": "Combobox", "Номен. код": "Readonly", "Ціна": "Readonly", "Кількість": "Entry", "Загальна вартість": "Readonly", "Зав. №": "Entry"}
        for i, (field, widget_type) in enumerate(fields.items()):
            ttk.Label(form_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            if widget_type == "Combobox": entry = ttk.Combobox(form_frame, values=sorted(self.asset_positions['Назва'].tolist()), width=28); entry.bind("<<ComboboxSelected>>", self.on_asset_select)
            elif widget_type in ["Readonly", "Label"]: entry = ttk.Entry(form_frame, width=30, state="readonly")
            else: entry = ttk.Entry(form_frame, width=30); entry.bind("<KeyRelease>", self.calculate_total) if field == "Кількість" else None
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew"); self.entries[field] = entry; make_context_menu(entry)
        button_frame = ttk.Frame(control_frame); button_frame.pack(fill="x", padx=5, pady=10); ttk.Button(button_frame, text="Додати", command=self.add_data).pack(fill="x", pady=2); ttk.Button(button_frame, text="Змінити", command=self.update_data).pack(fill="x", pady=2); ttk.Button(button_frame, text="Видалити", command=self.delete_data).pack(fill="x", pady=2);
        ttk.Button(button_frame, text="Очистити форму", command=self.clear_form).pack(fill="x", pady=5)
        table_frame = ttk.Frame(main_frame); table_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(table_frame, columns=list(fields.keys()), show="headings")
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview); self.tree.configure(yscrollcommand=vsb.set); vsb.pack(side="right", fill="y"); self.tree.pack(fill="both", expand=True)
        for col in self.tree['columns']: self.tree.heading(col, text=col)
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        self.context_menu = tk.Menu(self, tearoff=0); self.context_menu.add_command(label="Копіювати", command=self.copy_cell_value); self.context_menu.add_separator(); self.context_menu.add_command(label="Зберегти налаштування таблиці", command=self.save_column_widths); self.tree.bind("<Button-3>", self.show_context_menu)
    def show_context_menu(self, event): self.tree.identify_row(event.y); self.context_menu.tk_popup(event.x_root, event.y_root)
    def copy_cell_value(self):
        if not self.tree.focus(): return
        cur_item = self.tree.focus(); col_id = self.tree.identify_column(self.winfo_pointerx() - self.tree.winfo_rootx())
        if col_id: col_index = int(col_id.replace('#', '')) - 1; value = self.tree.item(cur_item, 'values')[col_index]; self.clipboard_clear(); self.clipboard_append(value)
    
    # **ВИПРАВЛЕНО: Використання self.tree['columns'] для надійності**
    def save_column_widths(self): 
        widths = {col: self.tree.column(col, "width") for col in self.tree['columns']}
        self.config_manager.save_table_settings(self.table_id, widths)
        messagebox.showinfo("Збережено", "Налаштування ширини стовпців збережено.")

    def apply_column_widths(self):
        settings = self.config_manager.get_table_settings(self.table_id)
        if not settings: self.bind('<Configure>', self.auto_resize_columns, add='+')
        else:
            for col, width in settings.items():
                if col in self.tree['columns']: self.tree.column(col, width=width, anchor='w')

    def auto_resize_columns(self, event=None):
        width = self.tree.winfo_width() - 20;
        if width <= 1: return
        weights = {'№': 0.5, 'Назва': 3, 'Номен. код': 1.5, 'Ціна': 1, 'Кількість': 1, 'Загальна вартість': 1.5, 'Зав. №': 2};
        total_weight = sum(weights.values())
        for col in self.tree['columns']: self.tree.column(col, width=int((width * weights[col]) / total_weight), anchor='w')
    def on_asset_select(self, event=None):
        asset_details = self.asset_positions[self.asset_positions['Назва'] == self.entries["Назва"].get()]
        if not asset_details.empty:
            for field in ["Номен. код", "Ціна"]: self.entries[field].config(state="normal"); self.entries[field].delete(0, tk.END); self.entries[field].insert(0, asset_details[field].iloc[0]); self.entries[field].config(state="readonly")
        self.calculate_total()
    def calculate_total(self, event=None):
        try: total_str = f"{float(self.entries['Ціна'].get()) * float(self.entries['Кількість'].get()):.2f}"
        except (ValueError, tk.TclError): total_str = ""
        self.entries["Загальна вартість"].config(state="normal"); self.entries["Загальна вартість"].delete(0, tk.END); self.entries["Загальна вартість"].insert(0, total_str); self.entries["Загальна вартість"].config(state="readonly")
    def load_data(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        self.data_df = self.db_manager.read_data(self.sheet_name)
        if self.data_df.empty: self.data_df = pd.DataFrame(columns=self.entries.keys())
        for _, row in self.data_df.iterrows(): self.tree.insert("", "end", values=list(row))
        self.apply_column_widths()
    def add_data(self):
        df = self.db_manager.read_data(self.sheet_name); next_id = pd.to_numeric(df['№'], errors='coerce').max() + 1 if not df.empty and pd.to_numeric(df['№'], errors='coerce').notna().any() else 1
        self.entries['№'].config(state="normal"); self.entries['№'].delete(0, tk.END); self.entries['№'].insert(0, str(int(next_id))); self.entries['№'].config(state="readonly")
        df = pd.concat([df, pd.DataFrame([[e.get() for e in self.entries.values()]], columns=self.entries.keys())], ignore_index=True)
        self.db_manager.write_data(self.sheet_name, df); self.load_data(); self.clear_form()
        self.app.refresh_application_data()
    def update_data(self):
        if not self.tree.selection(): return
        df = self.db_manager.read_data(self.sheet_name); row_index = df.index[df['№'].astype(str) == str(self.tree.item(self.tree.selection()[0])['values'][0])].tolist()
        if not row_index: return
        df.loc[row_index[0]] = [e.get() for e in self.entries.values()]; self.db_manager.write_data(self.sheet_name, df); self.load_data(); self.clear_form()
    def delete_data(self):
        if not self.tree.selection() or not messagebox.askyesno("Підтвердження", "Видалити цей запис?"): return
        df = self.db_manager.read_data(self.sheet_name); df = df[df['№'].astype(str) != str(self.tree.item(self.tree.selection()[0])['values'][0])]
        self.db_manager.write_data(self.sheet_name, df); self.load_data(); self.clear_form()
        self.app.refresh_application_data()
    def on_item_select(self, event):
        if not self.tree.selection(): return
        self.clear_form()
        for (field, entry), value in zip(self.entries.items(), self.tree.item(self.tree.selection()[0])['values']):
            entry.config(state="normal")
            if isinstance(entry, ttk.Combobox): entry.set(value)
            else: entry.delete(0, tk.END); entry.insert(0, value)
            if field in ["Номен. код", "Ціна", "Загальна вартість", "№"]: entry.config(state="readonly")
        self.on_asset_select(); self.calculate_total()
    def clear_form(self):
        for field, entry in self.entries.items():
            entry.config(state="normal"); entry.delete(0, tk.END)
            if field == "Назва": entry.set('')
            if field in ["Номен. код", "Ціна", "Загальна вартість", "№"]: entry.config(state="readonly")

class CrudTab(ttk.Frame):
    def __init__(self, parent, db_manager, config_manager, sheet_name, columns_config, select_callback=None, table_id=None, has_status_column=False):
        super().__init__(parent)
        self.db_manager = db_manager
        self.config_manager = config_manager
        self.sheet_name = sheet_name
        self.columns_config = columns_config
        self.select_callback = select_callback
        self.table_id = table_id if table_id else self.sheet_name
        self.has_status_column = has_status_column
        
        tree_cols = list(self.columns_config.keys())
        if self.has_status_column:
            tree_cols.insert(0, "Статус")
            self.attachments_path = self.db_manager.db_folder / "attached"
            self.attachments_path.mkdir(exist_ok=True)

        self.entries = {}
        self.create_widgets(tree_cols)
        self.load_data()

    def refresh_data(self):
        self.load_data(self.search_var.get())

    def update_combobox_values(self, field_name, new_values):
        if field_name in self.entries and isinstance(self.entries[field_name], ttk.Combobox):
            self.entries[field_name]['values'] = new_values

    def create_widgets(self, tree_columns):
        control_frame = ttk.Frame(self); control_frame.pack(side="left", fill="y", padx=10, pady=10)
        form_frame = ttk.LabelFrame(control_frame, text="Форма заповнення"); form_frame.pack(fill="x", padx=5, pady=5)
        
        for i, (field, config) in enumerate(self.columns_config.items()):
            ttk.Label(form_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Combobox(form_frame, values=config.get("values", []), width=28) if config.get("widget") == "combobox" else ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew"); self.entries[field] = entry; make_context_menu(entry)

        self.button_frame = ttk.Frame(control_frame); self.button_frame.pack(fill="x", padx=5, pady=10)
        ttk.Button(self.button_frame, text="Додати", command=self.add_data).pack(fill="x", pady=2)
        ttk.Button(self.button_frame, text="Змінити", command=self.update_data).pack(fill="x", pady=2)
        ttk.Button(self.button_frame, text="Видалити", command=self.delete_data).pack(fill="x", pady=2)
        ttk.Button(self.button_frame, text="Очистити форму", command=self.clear_form).pack(fill="x", pady=5)

        table_frame = ttk.Frame(self); table_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        search_frame = ttk.Frame(table_frame); search_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(search_frame, text="Пошук:").pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar(); self.search_var.trace_add("write", lambda *args: self.search_data())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var); search_entry.pack(fill="x", expand=True); make_context_menu(search_entry)
        
        self.tree = ttk.Treeview(table_frame, columns=tree_columns, show="headings")
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview); self.tree.configure(yscrollcommand=vsb.set); vsb.pack(side="right", fill="y"); self.tree.pack(fill="both", expand=True)

        for col in self.tree['columns']:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_column(_col, False))
            self.tree.column(col, width=120, anchor='w')
        
        if self.has_status_column:
            self.tree.column("Статус", width=60, stretch=tk.NO, anchor='center')
            self.tree.heading("Статус", text="Статус", command=lambda: self.sort_column("Статус", False))

        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        self.context_menu = tk.Menu(self, tearoff=0); self.context_menu.add_command(label="Копіювати", command=self.copy_cell_value); self.context_menu.add_separator(); self.context_menu.add_command(label="Зберегти налаштування таблиці", command=self.save_column_widths); self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event): self.tree.identify_row(event.y); self.context_menu.tk_popup(event.x_root, event.y_root)
    def copy_cell_value(self):
        if not self.tree.focus(): return
        cur_item = self.tree.focus(); col_id = self.tree.identify_column(self.winfo_pointerx() - self.tree.winfo_rootx())
        if col_id: col_index = int(col_id.replace('#', '')) - 1; value = self.tree.item(cur_item, 'values')[col_index]; self.clipboard_clear(); self.clipboard_append(value)
    
    # **ВИПРАВЛЕНО: Метод тепер надійно отримує список колонок з самого віджету**
    def save_column_widths(self):
        widths = {col: self.tree.column(col, "width") for col in self.tree['columns']}
        self.config_manager.save_table_settings(self.table_id, widths)
        messagebox.showinfo("Збережено", "Налаштування ширини стовпців збережено.")

    def apply_column_widths(self):
        settings = self.config_manager.get_table_settings(self.table_id)
        for col, width in settings.items():
            if col in self.tree['columns']:
                self.tree.column(col, width=width)

    def load_data(self, search_term=""):
        for item in self.tree.get_children(): self.tree.delete(item)
        self.data_df = self.db_manager.read_data(self.sheet_name)
        if self.data_df.empty: return
        
        all_sheets = self.db_manager.get_sheet_names()
        all_attachments = []
        if self.has_status_column:
            all_attachments = os.listdir(self.attachments_path)

        df_filtered = self.data_df[self.data_df.apply(lambda r: r.astype(str).str.contains(search_term, case=False).any(), axis=1)] if search_term else self.data_df
        
        for _, row in df_filtered.iterrows():
            values = list(row)
            if self.has_status_column:
                status_icons = ""
                pk_col_name = list(self.columns_config.keys())[0]
                record_id = row[pk_col_name]
                
                if self.sheet_name == "Журнал операцій":
                    if f"details_{record_id}" in all_sheets:
                        status_icons += '📄 '
                    if any(f.startswith(f"journal_{record_id}_") for f in all_attachments):
                        status_icons += '📎'
                elif self.sheet_name == "Описові документи":
                    if any(f.startswith(f"docs_{record_id}_") for f in all_attachments):
                        status_icons += '📎'
                
                values.insert(0, status_icons.strip())

            self.tree.insert("", "end", values=values)
            
        self.apply_column_widths()

    def add_data(self):
        values = [e.get() for e in self.entries.values()]
        if not all(v for i, v in enumerate(values) if self.columns_config[list(self.columns_config.keys())[i]].get("required", True)): messagebox.showwarning("Попередження", "Будь ласка, заповніть всі обов'язкові поля."); return
        
        df, pk_col = self.db_manager.read_data(self.sheet_name), list(self.columns_config.keys())[0]
        if pd.DataFrame([values], columns=self.columns_config.keys())[pk_col].iloc[0] in df[pk_col].astype(str).values: messagebox.showerror("Помилка", f"Запис з таким '{pk_col}' вже існує!"); return
        
        df = pd.concat([df, pd.DataFrame([values], columns=self.columns_config.keys())], ignore_index=True); self.db_manager.write_data(self.sheet_name, df); self.load_data(); self.clear_form()

    def update_data(self):
        if not self.tree.selection(): return
        df, pk_col = self.db_manager.read_data(self.sheet_name), list(self.columns_config.keys())[0]
        
        pk_col_index = self.tree['columns'].index(pk_col)
        selected_id = self.tree.item(self.tree.selection()[0])['values'][pk_col_index]

        row_index = df.index[df[pk_col].astype(str) == str(selected_id)].tolist()
        if not row_index: return
        df.loc[row_index[0]] = [e.get() for e in self.entries.values()]; self.db_manager.write_data(self.sheet_name, df); self.load_data(); self.clear_form()

    def delete_data(self):
        if not self.tree.selection() or not messagebox.askyesno("Підтвердження", "Видалити цей запис?"): return
        df, pk_col = self.db_manager.read_data(self.sheet_name), list(self.columns_config.keys())[0]
        
        pk_col_index = self.tree['columns'].index(pk_col)
        selected_id = self.tree.item(self.tree.selection()[0])['values'][pk_col_index]

        df = df[df[pk_col].astype(str) != str(selected_id)]; self.db_manager.write_data(self.sheet_name, df)
        
        if self.sheet_name == "Журнал операцій":
            try:
                sheets = self.db_manager.get_sheet_names()
                detail_sheet_name = f"details_{selected_id}"
                if detail_sheet_name in sheets:
                    with pd.ExcelWriter(self.db_manager.db_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                         if detail_sheet_name in writer.book.sheetnames:
                            del writer.book[detail_sheet_name]
            except Exception as e:
                print(f"Помилка під час видалення аркуша деталізації: {e}")

        self.load_data(); self.clear_form()
    
    def search_data(self): self.load_data(self.search_var.get())
    def sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')];
        try: l.sort(key=lambda t: float(str(t[0]).replace(',','.')), reverse=reverse)
        except (ValueError, IndexError): l.sort(key=lambda t: t[0], reverse=reverse)
        for i, (v, k) in enumerate(l): self.tree.move(k, '', i)
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def on_item_select(self, event):
        selected_item = self.tree.selection()
        if self.select_callback: self.select_callback(bool(selected_item))
        if not selected_item: self.clear_form(clear_selection=False); return
        self.clear_form(clear_selection=False)
        
        item_values = self.tree.item(selected_item)['values']
        data_values = item_values[1:] if self.has_status_column else item_values

        for entry, value in zip(self.entries.values(), data_values):
            if isinstance(entry, ttk.Combobox): entry.set(value)
            else: entry.delete(0, tk.END); entry.insert(0, value)

    def clear_form(self, clear_selection=True):
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox): entry.set('')
            else: entry.delete(0, tk.END)
        if clear_selection and self.tree.selection(): self.tree.selection_remove(self.tree.selection()[0])

class MilProApp:
    def __init__(self, root):
        self.root = root
        self.db_manager = DatabaseManager()
        self.config_manager = ConfigManager(self.db_manager.db_folder / "config.json")
        self.reference_tabs = []
        self.setup_window()
        self.create_header()
        self.create_tabs()
    def setup_window(self):
        self.root.title("MilPro"); self.root.state('zoomed'); self.root.minsize(1280, 720)
        self.style = ttk.Style(); self.style.theme_use('clam'); self.style.map('Treeview', background=[('selected', '#3498db')], foreground=[('selected', 'white')])
    def create_header(self):
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80); header_frame.pack(fill='x'); header_frame.pack_propagate(False)
        ttk.Label(header_frame, text='  📊  ', font=('Arial', 30), background='#2c3e50', foreground='white').pack(side='left', padx=(20, 15), pady=10)
        title_frame = tk.Frame(header_frame, bg=header_frame['bg']); title_frame.pack(side='left', pady=10, anchor='w')
        ttk.Label(title_frame, text='MilPro', font=('Arial', 24, 'bold'), background='#2c3e50', foreground='white').pack(anchor='w')
        ttk.Label(title_frame, text='Система обліку майна', font=('Arial', 12), background='#2c3e50', foreground='#bdc3c7').pack(anchor='w')
    
    def create_tabs(self):
        tab_container = ttk.Frame(self.root)
        tab_container.pack(fill='both', expand=True, padx=10, pady=10)

        self.notebook = ttk.Notebook(tab_container)
        self.notebook.pack(fill='both', expand=True)

        refresh_button = ttk.Button(tab_container, text="Оновити дані 🔄", command=self.refresh_application_data)
        refresh_button.place(relx=1.0, rely=0, x=-5, y=2, anchor='ne')

        self.operations_frame = ttk.Frame(self.notebook); self.notebook.add(self.operations_frame, text='Журнал операцій'); self.setup_operations_tab()
        self.assets_frame = ttk.Frame(self.notebook); self.notebook.add(self.assets_frame, text='Дані по майну'); self.setup_assets_tab()
        self.docs_frame = ttk.Frame(self.notebook); self.notebook.add(self.docs_frame, text='Описові документи'); self.setup_docs_tab()
        self.calc_frame = ttk.Frame(self.notebook); self.notebook.add(self.calc_frame, text='Калькулятори'); self.setup_calc_tab()
        self.references_frame = ttk.Frame(self.notebook); self.notebook.add(self.references_frame, text='Довідники'); self.setup_references_tab()

    def refresh_application_data(self):
        self.root.config(cursor="watch")
        self.root.update()
        
        subdivisions = sorted(self.db_manager.get_column_values("Підрозділи", "Назва"))
        self.operations_tab.update_combobox_values("Підрозділ-відправник", subdivisions)
        self.operations_tab.update_combobox_values("Підрозділ-отримувач", subdivisions)
        
        self.operations_tab.refresh_data()
        self.assets_tab.refresh_data()
        self.docs_tab.refresh_data()
        for ref_tab in self.reference_tabs:
            ref_tab.refresh_data()

        self.root.config(cursor="")
        messagebox.showinfo("Оновлення", "Дані було успішно оновлено.")

    def setup_operations_tab(self):
        doc_types = ["Акт приймання-передачі", "Акт списання", "Накладна (видавальна)", "Накладна (приймальна)"]; subdivisions = sorted(self.db_manager.get_column_values("Підрозділи", "Назва"))
        columns_config = { "№ запису": {"required": True}, "Дата запису": {"required": True}, "Тип документа": {"widget": "combobox", "values": doc_types, "required": True}, "Номер документа": {"required": False}, "Підрозділ-відправник": {"widget": "combobox", "values": subdivisions, "required": False}, "Підрозділ-отримувач": {"widget": "combobox", "values": subdivisions, "required": False} }
        
        def toggle_action_buttons(is_selected): 
            state = "normal" if is_selected else "disabled"
            self.details_button.config(state=state)
            self.attachments_button.config(state=state)
            self.export_op_button.config(state=state)
        
        self.operations_tab = CrudTab(self.operations_frame, self.db_manager, self.config_manager, 
                         "Журнал операцій", columns_config, 
                         select_callback=toggle_action_buttons,
                         table_id="operations_journal",
                         has_status_column=True)
        self.operations_tab.pack(fill="both", expand=True)
        
        self.details_button = ttk.Button(self.operations_tab.button_frame, text="Деталізація запису", command=lambda: self.open_details(self.operations_tab), state="disabled"); self.details_button.pack(fill="x", pady=(10,2))
        self.attachments_button = ttk.Button(self.operations_tab.button_frame, text="Прикріплені документи", command=lambda: self.open_attachments(self.operations_tab, prefix="journal"), state="disabled"); self.attachments_button.pack(fill="x", pady=2)
        
        self.export_op_button = ttk.Button(self.operations_tab.button_frame, text="Експортувати звіт", command=lambda: self.export_operation_report(self.operations_tab), state="disabled")
        self.export_op_button.pack(fill="x", pady=2)

    def export_operation_report(self, tab):
        if not tab.tree.selection():
            messagebox.showwarning("Експорт неможливий", "Будь ласка, оберіть запис для експорту.")
            return

        selected_item = tab.tree.selection()[0]
        item_values = tab.tree.item(selected_item)['values']
        headers = tab.tree['columns']
        
        pk_col_name = list(tab.columns_config.keys())[0]
        pk_col_index = headers.index(pk_col_name)
        record_id = item_values[pk_col_index]

        default_filename = f"Звіт_по_операції_№{record_id}_{datetime.now().strftime('%Y-%m-%d')}.txt"
        filepath = filedialog.asksaveasfilename(initialfile=default_filename, defaultextension=".txt", filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if not filepath:
            return

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"ЗВІТ ПО ОПЕРАЦІЇ №{record_id}\n")
                f.write(f"Дата формування: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("ОСНОВНІ ДАНІ:\n")
                for header, value in zip(headers, item_values):
                    if header != "Статус":
                        f.write(f"  {header}: {value}\n")
                
                details_df = self.db_manager.read_data(f"details_{record_id}")
                if not details_df.empty:
                    f.write("\n" + "="*50 + "\n\n")
                    f.write("ДЕТАЛІЗАЦІЯ ЗАПИСУ:\n")
                    
                    cols = details_df.columns.tolist()
                    col_widths = {col: len(col) for col in cols}
                    for _, row in details_df.iterrows():
                        for col in cols:
                            col_widths[col] = max(col_widths[col], len(str(row[col])))
                    
                    header_line = " | ".join([col.ljust(col_widths[col]) for col in cols])
                    f.write(header_line + "\n")
                    f.write("-" * len(header_line) + "\n")

                    for _, row in details_df.iterrows():
                        row_line = " | ".join([str(row[col]).ljust(col_widths[col]) for col in cols])
                        f.write(row_line + "\n")
                else:
                    f.write("\nДеталізація для цього запису відсутня.\n")
            
            messagebox.showinfo("Експорт успішний", f"Звіт було успішно збережено у файл:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Помилка експорту", f"Не вдалося зберегти файл: {e}")

    def open_details(self, tab):
        if not tab.tree.selection(): messagebox.showwarning("Увага", "Будь ласка, оберіть запис для деталізації."); return
        pk_col_name = list(tab.columns_config.keys())[0]
        pk_col_index = tab.tree['columns'].index(pk_col_name)
        record_id = tab.tree.item(tab.tree.selection()[0])['values'][pk_col_index]
        DetailsWindow(self.root, self, self.db_manager, self.config_manager, record_id)

    def open_attachments(self, tab, prefix):
        if not tab.tree.selection(): messagebox.showwarning("Увага", "Будь ласка, оберіть запис для керування документами."); return
        pk_col_name = list(tab.columns_config.keys())[0]
        pk_col_index = tab.tree['columns'].index(pk_col_name)
        record_id = tab.tree.item(tab.tree.selection()[0])['values'][pk_col_index]
        AttachmentsWindow(self.root, self, self.db_manager.db_folder, record_id, prefix)
    
    def setup_assets_tab(self): 
        self.assets_tab = AssetsTab(self.assets_frame, self.db_manager, self.config_manager)
        self.assets_tab.pack(fill='both', expand=True)

    def setup_docs_tab(self):
        columns_config = { "№ Запису": {"required": True}, "Дата запису": {"required": True}, "Назва документа": {"required": True}, "Номер документа": {"required": False}, "Примітки": {"required": False} }
        
        def toggle_docs_attachments_button(is_selected): 
            self.docs_attachments_button.config(state="normal" if is_selected else "disabled")
        
        self.docs_tab = CrudTab(self.docs_frame, self.db_manager, self.config_manager, 
                           "Описові документи", columns_config, 
                           select_callback=toggle_docs_attachments_button,
                           table_id="descriptive_docs",
                           has_status_column=True)
        self.docs_tab.pack(fill="both", expand=True)
        
        self.docs_attachments_button = ttk.Button(self.docs_tab.button_frame, text="Прикріплені документи", command=lambda: self.open_attachments(self.docs_tab, prefix="docs"), state="disabled")
        self.docs_attachments_button.pack(fill="x", pady=(10, 2))

    def setup_calc_tab(self): ttk.Label(self.calc_frame, text="Тут будуть різноманітні калькулятори.", font=("Arial", 12)).pack(expand=True)
    def setup_references_tab(self):
        ref_notebook = ttk.Notebook(self.references_frame); ref_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        subdivisions_tab = CrudTab(ref_notebook, self.db_manager, self.config_manager, "Підрозділи", 
                                   {"№": {}, "Назва": {}, "МВО": {}}, table_id="ref_subdivisions")
        ref_notebook.add(subdivisions_tab, text='Підрозділи')
        
        assets_tab = CrudTab(ref_notebook, self.db_manager, self.config_manager, "Майнові позиції", 
                             {"№": {}, "Назва": {}, "Номен. код": {}, "Ціна": {}, "Зав. №": {}}, table_id="ref_assets")
        ref_notebook.add(assets_tab, text='Майнові позиції')

        self.reference_tabs.append(subdivisions_tab)
        self.reference_tabs.append(assets_tab)

def make_context_menu(widget):
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Вирізати", command=lambda: widget.event_generate('<<Cut>>'))
    menu.add_command(label="Копіювати", command=lambda: widget.event_generate('<<Copy>>'))
    menu.add_command(label="Вставити", command=lambda: widget.event_generate('<<Paste>>'))
    widget.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))
def main():
    root = tk.Tk()
    app = MilProApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()