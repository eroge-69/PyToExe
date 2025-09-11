import tkinter as tk
from tkinter import filedialog, messagebox, font, colorchooser
import os
import json
from collections import defaultdict

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Текстовый редактор")
        self.root.geometry("1000x600")
        
        self.current_file = None
        self.default_font_family = "Ubuntu Mono"
        self.default_font_size = 12
        self.default_bg_color = "#300a24"
        self.default_fg_color = "#ffffff"
        
        self.set_dark_theme()
        
        self.load_settings()
        self.setup_tags()
        self.create_menu()
        self.create_toolbar()
        self.create_text_area()
        self.create_status_bar()
        
        self.bind_events()
        
    def load_settings(self):
        self.settings_file = "text_editor_settings.json"
        default_settings = {
            "font_family": "Ubuntu Mono",
            "font_size": 12,
            "bg_color": "#300a24",
            "fg_color": "#ffffff",
            "recent_files": []
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.default_font_family = settings.get('font_family', self.default_font_family)
                    self.default_font_size = settings.get('font_size', self.default_font_size)
                    self.default_bg_color = settings.get('bg_color', self.default_bg_color)
                    self.default_fg_color = settings.get('fg_color', self.default_fg_color)
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
    
    def save_settings(self):
        settings = {
            "font_family": self.default_font_family,
            "font_size": self.default_font_size,
            "bg_color": self.default_bg_color,
            "fg_color": self.default_fg_color,
            "recent_files": []
        }
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def setup_tags(self):
        self.tag_counter = 0
        self.tag_styles = {}
        
    def set_dark_theme(self):
        self.bg_color = self.default_bg_color
        self.fg_color = self.default_fg_color
        self.menu_bg = "#2d0c22"
        self.menu_fg = "#ffffff"
        self.highlight_color = "#4a1e3d"
        self.accent_color = "#e95420"
        self.button_bg = "#4a1e3d"
        
        self.root.configure(bg=self.bg_color)
        
    def create_menu(self):
        menubar = tk.Menu(self.root, bg=self.menu_bg, fg=self.menu_fg, bd=0, relief=tk.FLAT)
        
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.menu_bg, fg=self.menu_fg, bd=0)
        file_menu.add_command(label="Новый", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Открыть", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить как...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.exit_app)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.menu_bg, fg=self.menu_fg, bd=0)
        edit_menu.add_command(label="Выделить все", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Отменить", command=self.undo_text, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Повторить", command=self.redo_text, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Копировать", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Вставить", command=self.paste_text, accelerator="Ctrl+V")
        menubar.add_cascade(label="Правка", menu=edit_menu)
        
        format_menu = tk.Menu(menubar, tearoff=0, bg=self.menu_bg, fg=self.menu_fg, bd=0)
        format_menu.add_command(label="Шрифт...", command=self.change_font_dialog)
        format_menu.add_separator()
        format_menu.add_command(label="Полужирный", command=lambda: self.apply_formatting('bold'), accelerator="Ctrl+B")
        format_menu.add_command(label="Курсив", command=lambda: self.apply_formatting('italic'), accelerator="Ctrl+I")
        format_menu.add_command(label="Подчеркнутый", command=lambda: self.apply_formatting('underline'), accelerator="Ctrl+U")
        format_menu.add_separator()
        format_menu.add_command(label="Цвет текста...", command=self.change_text_color_dialog)
        format_menu.add_command(label="Цвет фона...", command=self.change_bg_color_dialog)
        format_menu.add_separator()
        format_menu.add_command(label="Очистить форматирование", command=self.clear_formatting)
        menubar.add_cascade(label="Формат", menu=format_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.menu_bg, fg=self.menu_fg, bd=0)
        help_menu.add_command(label="О программе", command=self.about_program)
        help_menu.add_command(label="От разработчика", command=self.about_developer)
        menubar.add_cascade(label="Справка", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def bind_events(self):
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Control-z>', lambda e: self.undo_text())
        self.root.bind('<Control-y>', lambda e: self.redo_text())
        self.root.bind('<Control-x>', lambda e: self.cut_text())
        self.root.bind('<Control-c>', lambda e: self.copy_text())
        self.root.bind('<Control-v>', lambda e: self.paste_text())
        self.root.bind('<Control-b>', lambda e: self.apply_formatting('bold'))
        self.root.bind('<Control-i>', lambda e: self.apply_formatting('italic'))
        self.root.bind('<Control-u>', lambda e: self.apply_formatting('underline'))
        
        self.text_area.bind('<ButtonRelease-1>', self.on_selection_change)
        self.text_area.bind('<KeyRelease>', self.on_selection_change)
        self.text_area.bind('<Configure>', self.on_selection_change)
    
    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bg=self.bg_color, bd=0, relief=tk.FLAT, height=35)
        
        button_style = {
            'bg': self.button_bg,
            'fg': self.fg_color,
            'relief': tk.FLAT,
            'bd': 0,
            'font': ('Ubuntu', 10),
            'highlightthickness': 0,
            'activebackground': self.accent_color,
            'activeforeground': self.fg_color,
            'padx': 8,
            'pady': 3
        }
        
        new_btn = tk.Button(toolbar, text="Новый", command=self.new_file, **button_style)
        new_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        open_btn = tk.Button(toolbar, text="Открыть", command=self.open_file, **button_style)
        open_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        save_btn = tk.Button(toolbar, text="Сохранить", command=self.save_file, **button_style)
        save_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        sep1 = tk.Frame(toolbar, width=1, height=20, bg=self.highlight_color)
        sep1.pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        bold_btn = tk.Button(toolbar, text="Ж", command=lambda: self.apply_formatting('bold'), **button_style)
        bold_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        italic_btn = tk.Button(toolbar, text="К", command=lambda: self.apply_formatting('italic'), **button_style)
        italic_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        underline_btn = tk.Button(toolbar, text="Ч", command=lambda: self.apply_formatting('underline'), **button_style)
        underline_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        sep2 = tk.Frame(toolbar, width=1, height=20, bg=self.highlight_color)
        sep2.pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        cut_btn = tk.Button(toolbar, text="Вырезать", command=self.cut_text, **button_style)
        cut_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        copy_btn = tk.Button(toolbar, text="Копировать", command=self.copy_text, **button_style)
        copy_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        paste_btn = tk.Button(toolbar, text="Вставить", command=self.paste_text, **button_style)
        paste_btn.pack(side=tk.LEFT, padx=2, pady=2)

        sep3 = tk.Frame(toolbar, width=1, height=20, bg=self.highlight_color)
        sep3.pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        select_all_btn = tk.Button(toolbar, text="Выделить всё", command=self.select_all, **button_style)
        select_all_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        toolbar.pack(side=tk.TOP, fill=tk.X)
        toolbar.pack_propagate(False)
    
    def create_text_area(self):
        self.text_area = tk.Text(self.root, 
                                wrap=tk.WORD,
                                font=(self.default_font_family, self.default_font_size),
                                bg=self.default_bg_color,
                                fg=self.default_fg_color,
                                insertbackground=self.default_fg_color,
                                selectbackground=self.accent_color,
                                undo=True,
                                relief=tk.FLAT,
                                bd=0,
                                padx=15,
                                pady=15,
                                highlightthickness=0)
        
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.create_context_menu()
    
    def create_context_menu(self):
        self.context_menu = tk.Menu(self.text_area, tearoff=0, bg=self.menu_bg, fg=self.menu_fg, bd=0)
        
        self.context_menu.add_command(label="Отменить", command=self.undo_text)
        self.context_menu.add_separator()
        
        self.context_menu.add_command(label="Вырезать", command=self.cut_text)
        self.context_menu.add_command(label="Копировать", command=self.copy_text)
        self.context_menu.add_command(label="Вставить", command=self.paste_text)
        self.context_menu.add_command(label="Удалить", command=self.delete_text)
        
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Выделить все", command=self.select_all)
        
        self.context_menu.add_separator()
        font_menu = tk.Menu(self.context_menu, tearoff=0, bg=self.menu_bg, fg=self.menu_fg)
        font_menu.add_command(label="Шрифт...", command=self.change_font_dialog)
        font_menu.add_separator()
        font_menu.add_command(label="Полужирный", command=lambda: self.apply_formatting('bold'))
        font_menu.add_command(label="Курсив", command=lambda: self.apply_formatting('italic'))
        font_menu.add_command(label="Подчеркнутый", command=lambda: self.apply_formatting('underline'))
        font_menu.add_separator()
        font_menu.add_command(label="Цвет текста...", command=self.change_text_color_dialog)
        font_menu.add_command(label="Цвет фона текста...", command=self.change_bg_color_dialog)
        font_menu.add_separator()
        font_menu.add_command(label="Очистить форматирование", command=self.clear_formatting)
        self.context_menu.add_cascade(label="Формат", menu=font_menu)
        
        self.text_area.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def delete_text(self):
        try:
            if self.text_area.tag_ranges(tk.SEL):
                self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
    
    def create_status_bar(self):
        self.status_bar = tk.Label(self.root, 
                                  text="Готово", 
                                  relief=tk.FLAT,
                                  anchor=tk.W,
                                  bg=self.menu_bg,
                                  fg=self.menu_fg,
                                  font=("Ubuntu", 9),
                                  padx=10,
                                  pady=3,
                                  highlightthickness=0)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def on_selection_change(self, event=None):
        self.update_status()
    
    def update_status(self):
        cursor_pos = self.text_area.index(tk.INSERT)
        line, column = map(int, cursor_pos.split('.'))
        
        content = self.text_area.get(1.0, tk.END)
        char_count = len(content) - 1
        
        try:
            if self.text_area.tag_ranges(tk.SEL):
                selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                selected_count = len(selected_text)
                selection_info = f" | Выделено: {selected_count}"
            else:
                selection_info = ""
        except tk.TclError:
            selection_info = ""
        
        self.status_bar.config(text=f"Строка: {line}, Колонка: {column} | Символов: {char_count}{selection_info}")
    
    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.root.title("Текстовый редактор - Новый файл")
        self.status_bar.config(text="Создан новый файл")
        self.tag_styles.clear()
        self.tag_counter = 0
    
    def open_file(self):
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
                self.root.title(f"Текстовый редактор - {os.path.basename(file_path)}")
                self.status_bar.config(text=f"Открыт файл: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")
    
    def save_file(self):
        if self.current_file:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.status_bar.config(text=f"Файл сохранен: {self.current_file}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
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
                self.root.title(f"Текстовый редактор - {os.path.basename(file_path)}")
                self.status_bar.config(text=f"Файл сохранен как: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
    
    def exit_app(self):
        self.save_settings()
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.root.quit()
    
    def select_all(self, event=None):
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
        self.update_status()
        return "break"
    
    def cut_text(self, event=None):
        try:
            if self.text_area.tag_ranges(tk.SEL):
                # Сохраняем выделенный текст в буфер обмена
                selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                
                # Удаляем выделенный текст
                self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
                self.update_status()
            return "break"
        except:
            return "break"
    
    def copy_text(self, event=None):
        try:
            if self.text_area.tag_ranges(tk.SEL):
                selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
            return "break"
        except:
            return "break"
    
    def paste_text(self, event=None):
        try:
            # Получаем текст из буфера обмена
            clipboard_text = self.root.clipboard_get()
            
            # Если есть выделение, заменяем его
            if self.text_area.tag_ranges(tk.SEL):
                self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            
            # Вставляем текст на текущую позицию курсора
            self.text_area.insert(tk.INSERT, clipboard_text)
            self.update_status()
            return "break"
        except:
            return "break"
    
    def undo_text(self):
        try:
            self.text_area.edit_undo()
            self.update_status()
        except tk.TclError:
            pass
    
    def redo_text(self):
        try:
            self.text_area.edit_redo()
            self.update_status()
        except tk.TclError:
            pass
    
    def create_tag(self, style_properties):
        tag_name = f"tag_{self.tag_counter}"
        self.tag_counter += 1
        self.tag_styles[tag_name] = style_properties
        self.text_area.tag_configure(tag_name, **style_properties)
        return tag_name
    
    def apply_formatting(self, format_type):
        try:
            if self.text_area.tag_ranges(tk.SEL):
                start = self.text_area.index(tk.SEL_FIRST)
                end = self.text_area.index(tk.SEL_LAST)
                
                current_tags = self.text_area.tag_names(start)
                
                new_style = {}
                for tag in current_tags:
                    if tag in self.tag_styles:
                        new_style.update(self.tag_styles[tag])
                
                current_font = self.text_area.cget("font")
                if 'font' in new_style:
                    current_font = new_style['font']
                
                font_family = self.default_font_family
                font_size = self.default_font_size
                font_weight = "normal"
                font_slant = "roman"
                font_underline = False
                
                if isinstance(current_font, (list, tuple)):
                    font_family = current_font[0] if len(current_font) > 0 else self.default_font_family
                    font_size = current_font[1] if len(current_font) > 1 else self.default_font_size
                    if len(current_font) > 2:
                        for style in current_font[2:]:
                            if "bold" in str(style).lower():
                                font_weight = "bold"
                            elif "italic" in str(style).lower():
                                font_slant = "italic"
                            elif "underline" in str(style).lower():
                                font_underline = True
                elif isinstance(current_font, str):
                    parts = current_font.split()
                    if parts:
                        font_family = parts[0]
                        for part in parts[1:]:
                            if part.isdigit():
                                font_size = int(part)
                            elif "bold" in part.lower():
                                font_weight = "bold"
                            elif "italic" in part.lower():
                                font_slant = "italic"
                            elif "underline" in part.lower():
                                font_underline = True
                
                if format_type == 'bold':
                    font_weight = "bold" if font_weight != "bold" else "normal"
                elif format_type == 'italic':
                    font_slant = "italic" if font_slant != "italic" else "roman"
                elif format_type == 'underline':
                    font_underline = not font_underline
                
                new_font = [font_family, font_size]
                if font_weight == "bold":
                    new_font.append("bold")
                if font_slant == "italic":
                    new_font.append("italic")
                if font_underline:
                    new_font.append("underline")
                
                new_style['font'] = new_font
                new_tag = self.create_tag(new_style)
                self.text_area.tag_add(new_tag, start, end)
                
        except tk.TclError:
            pass
    
    def change_text_color_dialog(self):
        color = colorchooser.askcolor(title="Выберите цвет текста", initialcolor=self.default_fg_color)
        if color and color[1]:
            self.apply_text_color(color[1])
    
    def apply_text_color(self, color):
        try:
            if self.text_area.tag_ranges(tk.SEL):
                start = self.text_area.index(tk.SEL_FIRST)
                end = self.text_area.index(tk.SEL_LAST)
                
                current_tags = self.text_area.tag_names(start)
                
                new_style = {}
                for tag in current_tags:
                    if tag in self.tag_styles:
                        new_style.update(self.tag_styles[tag])
                
                new_style['foreground'] = color
                new_tag = self.create_tag(new_style)
                self.text_area.tag_add(new_tag, start, end)
                
        except tk.TclError:
            pass
    
    def change_bg_color_dialog(self):
        color = colorchooser.askcolor(title="Выберите цвет фона текста", initialcolor=self.default_bg_color)
        if color and color[1]:
            self.apply_bg_color(color[1])
    
    def apply_bg_color(self, color):
        try:
            if self.text_area.tag_ranges(tk.SEL):
                start = self.text_area.index(tk.SEL_FIRST)
                end = self.text_area.index(tk.SEL_LAST)
                
                current_tags = self.text_area.tag_names(start)
                
                new_style = {}
                for tag in current_tags:
                    if tag in self.tag_styles:
                        new_style.update(self.tag_styles[tag])
                
                new_style['background'] = color
                new_tag = self.create_tag(new_style)
                self.text_area.tag_add(new_tag, start, end)
                
        except tk.TclError:
            pass
    
    def clear_formatting(self):
        try:
            if self.text_area.tag_ranges(tk.SEL):
                start = self.text_area.index(tk.SEL_FIRST)
                end = self.text_area.index(tk.SEL_LAST)
                
                tags = self.text_area.tag_names(start)
                for tag in tags:
                    if tag != 'sel':
                        self.text_area.tag_remove(tag, start, end)
                
        except tk.TclError:
            pass
    
    def change_font_dialog(self):
        font_window = tk.Toplevel(self.root)
        font_window.title("Шрифт")
        font_window.geometry("400x300")
        font_window.configure(bg=self.bg_color, highlightthickness=0)
        font_window.resizable(False, False)
        font_window.transient(self.root)
        font_window.grab_set()
        
        main_frame = tk.Frame(font_window, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Шрифт:", bg=self.bg_color, fg=self.fg_color, 
                font=("Ubuntu", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        font_listbox = tk.Listbox(main_frame, bg=self.menu_bg, fg=self.fg_color, 
                                 selectbackground=self.accent_color, bd=0,
                                 font=("Ubuntu", 10), highlightthickness=0,
                                 exportselection=False)
        font_listbox.grid(row=1, column=0, sticky=tk.NSEW, padx=(0, 10))
        
        fonts = ["Ubuntu Mono", "Consolas", "Courier New", "Arial", "Times New Roman", 
                "Verdana", "Tahoma", "Georgia", "Comic Sans MS", "Impact"]
        
        for f in fonts:
            font_listbox.insert(tk.END, f)
        
        try:
            index = fonts.index(self.default_font_family)
            font_listbox.select_set(index)
            font_listbox.see(index)
        except ValueError:
            pass
        
        tk.Label(main_frame, text="Размер:", bg=self.bg_color, fg=self.fg_color,
                font=("Ubuntu", 10)).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        size_listbox = tk.Listbox(main_frame, bg=self.menu_bg, fg=self.fg_color,
                                 selectbackground=self.accent_color, bd=0,
                                 font=("Ubuntu", 10), highlightthickness=0,
                                 exportselection=False)
        size_listbox.grid(row=1, column=1, sticky=tk.NSEW)
        
        sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]
        for s in sizes:
            size_listbox.insert(tk.END, str(s))
        
        try:
            index = sizes.index(self.default_font_size)
            size_listbox.select_set(index)
            size_listbox.see(index)
        except ValueError:
            size_listbox.select_set(4)
        
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ok_btn = tk.Button(button_frame, text="OK", command=lambda: self.apply_font_selection(
            font_listbox, size_listbox, font_window), bg=self.accent_color, fg=self.fg_color,
            bd=0, font=("Ubuntu", 10), padx=20, pady=2, highlightthickness=0)
        ok_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Отмена", command=font_window.destroy,
                              bg=self.button_bg, fg=self.fg_color, bd=0,
                              font=("Ubuntu", 10), padx=20, pady=2, highlightthickness=0)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        font_window.protocol("WM_DELETE_WINDOW", font_window.destroy)
    
    def apply_font_selection(self, font_listbox, size_listbox, window):
        try:
            font_family = font_listbox.get(font_listbox.curselection()[0])
            font_size = int(size_listbox.get(size_listbox.curselection()[0]))
            
            self.default_font_family = font_family
            self.default_font_size = font_size
            
            self.text_area.configure(font=(font_family, font_size))
            
            self.save_settings()
            
            window.destroy()
        except IndexError:
            messagebox.showerror("Ошибка", "Выберите шрифт и размер")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить шрифт: {str(e)}")
    
    def about_program(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("О программе")
        about_window.geometry("500x450")
        about_window.configure(bg=self.bg_color, highlightthickness=0)
        about_window.resizable(False, False)
        about_window.transient(self.root)
        
        about_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - about_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - about_window.winfo_height()) // 2
        about_window.geometry(f"+{x}+{y}")
        
        main_frame = tk.Frame(about_window, bg=self.bg_color, padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(pady=(0, 20))
        
        tk.Label(title_frame, text="Текстовый редактор", 
                font=("Ubuntu", 20, "bold"), bg=self.bg_color, fg=self.accent_color).pack()
        
        tk.Label(title_frame, text="Версия 1.0", 
                font=("Ubuntu", 14), bg=self.bg_color, fg=self.fg_color).pack(pady=5)
        
        desc_frame = tk.Frame(main_frame, bg=self.bg_color)
        desc_frame.pack(pady=(0, 20))
        
        tk.Label(desc_frame, text="Современный текстовый редактор с темной темой", 
                font=("Ubuntu", 12), bg=self.bg_color, fg=self.fg_color).pack(pady=5)
        
        tk.Label(desc_frame, text="в стиле Ubuntu с расширенными возможностями форматирования", 
                font=("Ubuntu", 12), bg=self.bg_color, fg=self.fg_color, justify=tk.CENTER).pack()
        
        features_frame = tk.Frame(main_frame, bg=self.bg_color)
        features_frame.pack(pady=(0, 25))
        
        tk.Label(features_frame, text="Основные возможности:", 
                font=("Ubuntu", 12, "bold"), bg=self.bg_color, fg=self.accent_color).pack(anchor=tk.W, pady=(0, 10))
        
        features = [
            "• Индивидуальное форматирование символов",
            "• Поддержка Rich Text formatting",
            "• Темная тема в стиле Ubuntu",
            "• Сохранение и загрузка настроек",
            "• Контекстное меню с быстрым доступом",
            "• Подсчет символов и статистика",
            "• Горячие клавиши для всех операций"
        ]
        
        for feature in features:
            tk.Label(features_frame, text=feature, font=("Ubuntu", 10), 
                    bg=self.bg_color, fg=self.fg_color, justify=tk.LEFT).pack(anchor=tk.W, pady=2)
        
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack()
        
        ok_btn = tk.Button(button_frame, text="OK", command=about_window.destroy,
                          bg=self.accent_color, fg=self.fg_color, bd=0,
                          font=("Ubuntu", 12, "bold"), padx=40, pady=8, 
                          highlightthickness=0, cursor="hand2")
        ok_btn.pack(pady=10)
        
        about_window.protocol("WM_DELETE_WINDOW", about_window.destroy)
    
    def about_developer(self):
        dev_window = tk.Toplevel(self.root)
        dev_window.title("От разработчика")
        dev_window.geometry("500x400")
        dev_window.configure(bg=self.bg_color, highlightthickness=0)
        dev_window.resizable(False, False)
        dev_window.transient(self.root)
        
        dev_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dev_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dev_window.winfo_height()) // 2
        dev_window.geometry(f"+{x}+{y}")
        
        main_frame = tk.Frame(dev_window, bg=self.bg_color, padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(pady=(0, 20))
        
        tk.Label(title_frame, text="Разработчик", 
                font=("Ubuntu", 20, "bold"), bg=self.bg_color, fg=self.accent_color).pack()
        
        avatar_frame = tk.Frame(main_frame, bg=self.bg_color, height=80, width=80)
        avatar_frame.pack_propagate(False)
        avatar_frame.pack(pady=10)
        
        avatar_label = tk.Label(avatar_frame, text="👨‍💻", font=("Ubuntu", 40), 
                               bg=self.menu_bg, fg=self.fg_color)
        avatar_label.pack(fill=tk.BOTH, expand=True)
        
        info_frame = tk.Frame(main_frame, bg=self.bg_color)
        info_frame.pack(pady=(0, 20))
        
        developer_info = [
            {"label": "Имя:", "value": "Артём Ядров", "font": ("Ubuntu", 11, "bold")},
            {"label": "Discord:", "value": "toiletxyz", "font": ("Ubuntu", 10)},
            {"label": "Email:", "value": "terminal.mail.xd@gmail.com", "font": ("Ubuntu", 10)},
            {"label": "GitHub:", "value": "github.com/terminal-ux", "font": ("Ubuntu", 10)},
            {"label": "Telegram:", "value": "@wekeqq", "font": ("Ubuntu", 10)},
            {"label": "Репортните баг:", "value": "https://github.com/terminal-ux/madeinpython/issues", "font": ("Ubuntu", 10)}
        ]
        
        for info in developer_info:
            row_frame = tk.Frame(info_frame, bg=self.bg_color)
            row_frame.pack(pady=3)
            
            tk.Label(row_frame, text=info["label"], font=("Ubuntu", 10, "bold"), 
                    bg=self.bg_color, fg=self.accent_color, width=10, anchor=tk.W).pack(side=tk.LEFT)
            
            tk.Label(row_frame, text=info["value"], font=info["font"], 
                    bg=self.bg_color, fg=self.fg_color, anchor=tk.W).pack(side=tk.LEFT, padx=(5, 0))
        
        extra_frame = tk.Frame(main_frame, bg=self.bg_color)
        extra_frame.pack(pady=(15, 20))
        
        tk.Label(extra_frame, text="Текстовый редактор создан с использованием Python 3 и Tkinter", 
                font=("Ubuntu", 9), bg=self.bg_color, fg=self.fg_color, justify=tk.CENTER).pack()
        
        tk.Label(extra_frame, text="Дизайн вдохновлен Ubuntu и современными темными темами", 
                font=("Ubuntu", 9), bg=self.bg_color, fg=self.fg_color, justify=tk.CENTER).pack(pady=2)
        
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack()
        
        ok_btn = tk.Button(button_frame, text="OK", command=dev_window.destroy,
                          bg=self.accent_color, fg=self.fg_color, bd=0,
                          font=("Ubuntu", 12, "bold"), padx=40, pady=8, 
                          highlightthickness=0, cursor="hand2")
        ok_btn.pack(pady=10)
        
        dev_window.protocol("WM_DELETE_WINDOW", dev_window.destroy)

if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditor(root)
    root.mainloop()
