import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os

class SimpleTextEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Papind")
        self.root.geometry("800x600")
        self.current_file = None
        
        self.setup_ui()
        self.setup_menu()
        
    def setup_ui(self):
        # Главный фрейм
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Текстовое поле с прокруткой
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_area = tk.Text(
            text_frame, 
            wrap=tk.WORD, 
            font=("Arial", 12),
            undo=True,
            maxundo=-1
        )
        
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scrollbar.set)
        
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Статус бар
        self.status_bar = tk.Label(
            self.root, 
            text="Готов к работе", 
            anchor=tk.W,
            relief=tk.SUNKEN
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        
        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Новый", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Открыть", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить как", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.exit_app)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        # Меню Правка
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Отменить", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Повторить", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Копировать", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Вставить", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_command(label="Удалить", command=self.delete, accelerator="Del")
        edit_menu.add_separator()
        edit_menu.add_command(label="Выделить все", command=self.select_all, accelerator="Ctrl+A")
        menubar.add_cascade(label="Правка", menu=edit_menu)
        
        # Меню Вид
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Увеличить шрифт", command=self.increase_font)
        view_menu.add_command(label="Уменьшить шрифт", command=self.decrease_font)
        view_menu.add_separator()
        view_menu.add_command(label="Сбросить шрифт", command=self.reset_font)
        menubar.add_cascade(label="Вид", menu=view_menu)
        
        # Меню Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.about)
        menubar.add_cascade(label="Справка", menu=help_menu)
        
        self.root.config(menu=menubar)
        
        # Горячие клавиши
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-x>', lambda e: self.cut())
        self.root.bind('<Control-c>', lambda e: self.copy())
        self.root.bind('<Control-v>', lambda e: self.paste())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        
    def new_file(self):
        if self.check_save():
            self.text_area.delete(1.0, tk.END)
            self.current_file = None
            self.update_status("Новый файл")
            
    def open_file(self):
        if self.check_save():
            file_path = filedialog.askopenfilename(
                defaultextension=".txt",
                filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, content)
                    self.current_file = file_path
                    self.update_status(f"Открыт: {os.path.basename(file_path)}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")
                    
    def save_file(self):
        if self.current_file:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.update_status(f"Сохранено: {os.path.basename(self.current_file)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
        else:
            self.save_as_file()
            
    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if file_path:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.current_file = file_path
                self.update_status(f"Сохранено как: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
                
    def check_save(self):
        content = self.text_area.get(1.0, tk.END).strip()
        if content:
            result = messagebox.askyesnocancel(
                "Сохранить файл",
                "Сохранить изменения перед продолжением?"
            )
            if result is None:  # Cancel
                return False
            elif result:  # Yes
                self.save_file()
        return True
        
    def undo(self):
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass
            
    def redo(self):
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            pass
            
    def cut(self):
        self.text_area.event_generate("<<Cut>>")
        
    def copy(self):
        self.text_area.event_generate("<<Copy>>")
        
    def paste(self):
        self.text_area.event_generate("<<Paste>>")
        
    def delete(self):
        self.text_area.event_generate("<<Clear>>")
        
    def select_all(self):
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
        
    def increase_font(self):
        current_font = self.text_area.cget("font")
        font_name, font_size = current_font.split()
        new_size = int(font_size) + 2
        self.text_area.config(font=(font_name, new_size))
        
    def decrease_font(self):
        current_font = self.text_area.cget("font")
        font_name, font_size = current_font.split()
        new_size = max(8, int(font_size) - 2)
        self.text_area.config(font=(font_name, new_size))
        
    def reset_font(self):
        self.text_area.config(font=("Arial", 12))
        
    def about(self):
        about_text = """Papind
Версия 1.0

Простой текстовый редактор
Создан на Python Артемом)

Функции:
- Создание и редактирование текста
- Сохранение и открытие файлов
- Поддержка русского языка
- Горячие клавиши
- Изменение размера шрифта"""
        messagebox.showinfo("О программе", about_text)
        
    def update_status(self, message):
        self.status_bar.config(text=message)
        
    def exit_app(self):
        if self.check_save():
            self.root.quit()
            
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.root.mainloop()

# Упрощенная версия редактора
class UltraSimpleEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Простой редактор")
        self.root.geometry("600x400")
        self.current_file = None
        
        # Текстовое поле
        self.text = tk.Text(self.root, wrap=tk.WORD, font=("Arial", 12))
        self.text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Кнопки
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(button_frame, text="Новый", command=self.new_file).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Открыть", command=self.open_file).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Сохранить", command=self.save_file).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Сохранить как", command=self.save_as).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Выход", command=self.root.quit).pack(side=tk.RIGHT, padx=2)
    
    def new_file(self):
        self.text.delete(1.0, tk.END)
        self.current_file = None
    
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Текстовые файлы", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text.delete(1.0, tk.END)
                self.text.insert(1.0, content)
                self.current_file = file_path
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")
    
    def save_file(self):
        if self.current_file:
            try:
                content = self.text.get(1.0, tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Успех", "Файл сохранен")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
        else:
            self.save_as()
    
    def save_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt")]
        )
        if file_path:
            try:
                content = self.text.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.current_file = file_path
                messagebox.showinfo("Успех", "Файл сохранен")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Запуск полной версии
    editor = SimpleTextEditor()
    editor.run()
    
    # Или запуск упрощенной версии
    # editor = UltraSimpleEditor()
    # editor.run()