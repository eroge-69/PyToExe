# Sample Python code
import pdfrw
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import json
import os


class PDFFormFillerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Заполнитель PDF-форм")
        self.root.geometry("800x600")

        # Переменные
        self.template_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.form_fields = []
        self.field_widgets = {}

        self.setup_ui()

    def setup_ui(self):
        # Создаем панель вкладок
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Вкладка 1: Выбор файла и просмотр полей
        tab_file = ttk.Frame(notebook)
        notebook.add(tab_file, text="Файл и поля")

        # Вкладка 2: Заполнение данных
        tab_data = ttk.Frame(notebook)
        notebook.add(tab_data, text="Заполнение данных")

        # Вкладка 3: Сохранение и результат
        tab_save = ttk.Frame(notebook)
        notebook.add(tab_save, text="Сохранение")

        # Настройка вкладки "Файл и поля"
        self.setup_file_tab(tab_file)

        # Настройка вкладки "Заполнение данных"
        self.setup_data_tab(tab_data)

        # Настройка вкладки "Сохранение"
        self.setup_save_tab(tab_save)

    def setup_file_tab(self, parent):
        # Выбор шаблона PDF
        frame_template = ttk.LabelFrame(parent, text="Шаблон PDF", padding=10)
        frame_template.pack(fill='x', padx=5, pady=5)

        ttk.Label(frame_template, text="Файл шаблона:").grid(
            row=0, column=0, sticky='w', pady=5)
        ttk.Entry(frame_template, textvariable=self.template_path,
                  width=50).grid(row=0, column=1, padx=5)
        ttk.Button(frame_template, text="Обзор...",
                   command=self.browse_template).grid(row=0, column=2, padx=5)

        ttk.Button(frame_template, text="Загрузить поля формы",
                   command=self.load_form_fields).grid(row=1, column=0, columnspan=3, pady=10)

        # Просмотр полей формы
        frame_fields = ttk.LabelFrame(parent, text="Поля формы", padding=10)
        frame_fields.pack(fill='both', expand=True, padx=5, pady=5)

        self.fields_text = scrolledtext.ScrolledText(
            frame_fields, height=15, width=70)
        self.fields_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.fields_text.config(state='disabled')

    def setup_data_tab(self, parent):
        # Область для динамического создания полей ввода
        self.data_frame = ttk.LabelFrame(
            parent, text="Данные для заполнения", padding=10)
        self.data_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Прокручиваемая область для полей
        self.canvas = tk.Canvas(self.data_frame)
        scrollbar = ttk.Scrollbar(
            self.data_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Подсказка
        ttk.Label(parent, text="Заполните поля ниже, затем перейдите на вкладку 'Сохранение'",
                  foreground="gray").pack(pady=5)

    def setup_save_tab(self, parent):
        # Выбор пути сохранения
        frame_save = ttk.LabelFrame(
            parent, text="Сохранение результата", padding=10)
        frame_save.pack(fill='x', padx=5, pady=5)

        ttk.Label(frame_save, text="Сохранить как:").grid(
            row=0, column=0, sticky='w', pady=5)
        ttk.Entry(frame_save, textvariable=self.output_path,
                  width=50).grid(row=0, column=1, padx=5)
        ttk.Button(frame_save, text="Обзор...", command=self.browse_output).grid(
            row=0, column=2, padx=5)

        # Кнопки действий
        frame_actions = ttk.Frame(parent)
        frame_actions.pack(pady=20)

        ttk.Button(frame_actions, text="Заполнить PDF",
                   command=self.fill_pdf, style='Accent.TButton').pack(pady=10)

        ttk.Button(frame_actions, text="Экспорт данных в JSON",
                   command=self.export_data).pack(pady=5)

        ttk.Button(frame_actions, text="Импорт данных из JSON",
                   command=self.import_data).pack(pady=5)

        # Статус
        self.status_label = ttk.Label(
            parent, text="Готов к работе", foreground="green")
        self.status_label.pack(pady=10)

    def browse_template(self):
        filename = filedialog.askopenfilename(
            title="Выберите PDF-шаблон",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.template_path.set(filename)
            self.output_path.set(
                str(Path(filename).with_name(f"filled_{Path(filename).name}")))

    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Сохранить заполненный PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if filename:
            self.output_path.set(filename)

    def load_form_fields(self):
        if not self.template_path.get():
            messagebox.showerror("Ошибка", "Сначала выберите PDF-файл")
            return

        try:
            self.form_fields = self.get_form_fields(self.template_path.get())
            self.display_form_fields()
            self.create_data_inputs()
            self.update_status(
                f"Загружено {len(self.form_fields)} полей", "green")
        except Exception as e:
            self.update_status(f"Ошибка: {e}", "red")
            messagebox.showerror("Ошибка", f"Не удалось загрузить поля: {e}")

    def get_form_fields(self, template_path):
        template_pdf = pdfrw.PdfReader(template_path)
        fields = []

        for page in template_pdf.pages:
            annotations = page.get('/Annots')
            if annotations:
                for annotation in annotations:
                    if annotation['/Subtype'] == '/Widget':
                        field_name = annotation.get('/T')
                        field_type = annotation.get('/FT')
                        if field_name:
                            fields.append({
                                'name': field_name,
                                'type': field_type,
                                'description': f"{field_name} ({field_type})"
                            })
        return fields

    def display_form_fields(self):
        self.fields_text.config(state='normal')
        self.fields_text.delete(1.0, tk.END)

        if not self.form_fields:
            self.fields_text.insert(
                tk.END, "Поля не найдены. Убедитесь, что это PDF-форма.")
        else:
            for field in self.form_fields:
                self.fields_text.insert(tk.END, f"• {field['description']}\n")

        self.fields_text.config(state='disabled')

    def create_data_inputs(self):
        # Очищаем предыдущие поля
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.field_widgets = {}

        if not self.form_fields:
            ttk.Label(self.scrollable_frame,
                      text="Сначала загрузите поля формы на вкладке 'Файл и поля'",
                      foreground="gray").pack(pady=20)
            return

        for i, field in enumerate(self.form_fields):
            frame = ttk.Frame(self.scrollable_frame)
            frame.pack(fill='x', padx=5, pady=2)

            ttk.Label(frame, text=f"{field['name']}:",
                      width=25, anchor='w').pack(side='left')

            if field['type'] == '/Btn':  # Чекбокс
                var = tk.BooleanVar()
                widget = ttk.Checkbutton(frame, variable=var)
                widget.pack(side='left')
            else:  # Текстовое поле
                var = tk.StringVar()
                widget = ttk.Entry(frame, textvariable=var, width=30)
                widget.pack(side='left', fill='x', expand=True)

            self.field_widgets[field['name']] = {
                'var': var, 'type': field['type']}

    def collect_form_data(self):
        data = {}
        for field_name, widget_info in self.field_widgets.items():
            value = widget_info['var'].get()
            if widget_info['type'] == '/Btn':
                # Для чекбоксов преобразуем в строку 'Yes' или 'Off'
                data[field_name] = 'Yes' if value else 'Off'
            else:
                data[field_name] = str(value)
        return data

    def fill_pdf(self):
        if not self.template_path.get() or not self.output_path.get():
            messagebox.showerror("Ошибка", "Укажите пути к файлам")
            return

        if not self.form_fields:
            messagebox.showerror("Ошибка", "Сначала загрузите поля формы")
            return

        try:
            data = self.collect_form_data()
            self.fill_pdf_template(
                self.template_path.get(), self.output_path.get(), data)
            self.update_status("PDF успешно заполнен!", "green")
            messagebox.showinfo(
                "Успех", f"Файл сохранен как:\n{self.output_path.get()}")

            # Предложение открыть файл
            if messagebox.askyesno("Успех", "Открыть заполненный PDF?"):
                os.startfile(self.output_path.get())

        except Exception as e:
            self.update_status(f"Ошибка: {e}", "red")
            messagebox.showerror("Ошибка", f"Не удалось заполнить PDF: {e}")

    def fill_pdf_template(self, template_path, output_path, data_dict):
        template_pdf = pdfrw.PdfReader(template_path)

        for page in template_pdf.pages:
            annotations = page.get('/Annots')
            if annotations:
                for annotation in annotations:
                    if annotation['/Subtype'] == '/Widget':
                        field_name = annotation.get('/T')
                        if field_name and field_name in data_dict:
                            value = data_dict[field_name]
                            field_type = annotation.get('/FT')

                            if field_type == '/Tx':  # Текстовое поле
                                annotation.update(pdfrw.PdfDict(
                                    V=pdfrw.PdfString(value)))
                            elif field_type == '/Btn':  # Чекбокс/радиокнопка
                                annotation.update(pdfrw.PdfDict(
                                    V=pdfrw.PdfName(value),
                                    AS=pdfrw.PdfName(value)
                                ))
                            # Блокируем поле
                            annotation.update(pdfrw.PdfDict(Ff=1))

        pdfrw.PdfWriter().write(output_path, template_pdf)

    def export_data(self):
        if not self.field_widgets:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
            return

        filename = filedialog.asksaveasfilename(
            title="Экспорт данных",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )

        if filename:
            try:
                data = self.collect_form_data()
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.update_status("Данные экспортированы", "green")
            except Exception as e:
                self.update_status(f"Ошибка экспорта: {e}", "red")

    def import_data(self):
        if not self.field_widgets:
            messagebox.showwarning(
                "Предупреждение", "Сначала загрузите поля формы")
            return

        filename = filedialog.askopenfilename(
            title="Импорт данных",
            filetypes=[("JSON files", "*.json")]
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for field_name, value in data.items():
                    if field_name in self.field_widgets:
                        if self.field_widgets[field_name]['type'] == '/Btn':
                            # Для чекбоксов
                            self.field_widgets[field_name]['var'].set(
                                value == 'Yes')
                        else:
                            # Для текстовых полей
                            self.field_widgets[field_name]['var'].set(value)

                self.update_status("Данные импортированы", "green")
            except Exception as e:
                self.update_status(f"Ошибка импорта: {e}", "red")

    def update_status(self, message, color="black"):
        self.status_label.config(text=message, foreground=color)


def main():
    root = tk.Tk()
    app = PDFFormFillerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()