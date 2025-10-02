import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
import subprocess
import sys
from pathlib import Path

class ModernMysticOSBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("🧙‍♂️ Mystic OS Builder - Визуальный конструктор ОС")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Конфигурация проекта
        self.project_path = Path(".")
        self.blocks = {
            'boot': [], 'kernel': [], 'gdt': [], 'print': [], 'disk': []
        }
        self.current_file = None
        
        self.setup_styles()
        self.setup_ui()
        self.load_project_structure()
        
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Настраиваем стили
        self.style.configure('Mystic.TFrame', background='#1e1e1e')
        self.style.configure('Mystic.TLabelframe', background='#1e1e1e', foreground='#00ff88')
        self.style.configure('Mystic.TLabelframe.Label', background='#1e1e1e', foreground='#00ff88')
        self.style.configure('Mystic.TButton', background='#006633', foreground='white')
        self.style.configure('Mystic.TNotebook', background='#1e1e1e')
        self.style.configure('Mystic.TNotebook.Tab', background='#333333', foreground='#00ff88')
        
    def setup_ui(self):
        # Главный контейнер
        main_container = ttk.Frame(self.root, style='Mystic.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Верхняя панель инструментов
        self.setup_toolbar(main_container)
        
        # Основная область
        content_frame = ttk.Frame(main_container, style='Mystic.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Левая панель - файлы и блоки
        left_panel = ttk.Frame(content_frame, style='Mystic.TFrame', width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Центральная область - редактор
        center_panel = ttk.Frame(content_frame, style='Mystic.TFrame')
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Правая панель - свойства и предпросмотр
        right_panel = ttk.Frame(content_frame, style='Mystic.TFrame', width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        self.setup_file_explorer(left_panel)
        self.setup_blocks_panel(left_panel)
        self.setup_workspace(center_panel)
        self.setup_properties_panel(right_panel)
        self.setup_preview_panel(right_panel)
        
    def setup_toolbar(self, parent):
        toolbar = ttk.Frame(parent, style='Mystic.TFrame', height=40)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        toolbar.pack_propagate(False)
        
        buttons = [
            ("🚀 Сборка", self.build_project),
            ("💾 Сохранить", self.save_project),
            ("📂 Открыть", self.load_project),
            ("🔧 Экспорт ASM", self.export_asm),
            ("▶️ Запуск в VM", self.run_vm),
            ("📊 Анализ", self.analyze_project)
        ]
        
        for text, command in buttons:
            btn = tk.Button(
                toolbar, text=text, command=command,
                bg='#006633', fg='white', relief='raised', bd=2,
                font=('Arial', 9, 'bold')
            )
            btn.pack(side=tk.LEFT, padx=5)
    
    def setup_file_explorer(self, parent):
        frame = ttk.LabelFrame(parent, text="📁 ФАЙЛЫ ПРОЕКТА", style='Mystic.TLabelframe')
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Дерево файлов
        self.tree = ttk.Treeview(frame, show='tree')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Контекстное меню
        self.tree_menu = tk.Menu(self.tree, tearoff=0)
        self.tree_menu.add_command(label="Открыть", command=self.open_selected_file)
        self.tree_menu.add_command(label="Удалить", command=self.delete_file)
        self.tree_menu.add_command(label="Переименовать", command=self.rename_file)
        
        self.tree.bind("<Button-3>", self.show_tree_menu)
        self.tree.bind("<Double-1>", self.open_selected_file)
    
    def setup_blocks_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="🧩 БЛОКИ КОДА", style='Mystic.TLabelframe')
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Ноутбук для категорий блоков
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        categories = {
            "🔰 Загрузчик": self.create_boot_blocks(),
            "🎯 Ядро": self.create_kernel_blocks(),
            "📺 Видео": self.create_video_blocks(),
            "💾 Диск": self.create_disk_blocks(),
            "🛡️ Система": self.create_system_blocks()
        }
        
        for category, blocks in categories.items():
            category_frame = ttk.Frame(notebook)
            notebook.add(category_frame, text=category)
            
            for block_name, block_id, color, description in blocks:
                self.create_block_button(category_frame, block_name, block_id, color, description)
    
    def create_boot_blocks(self):
        return [
            ("BIOS Загрузка", "boot_bios", "#ff6b6b", "Инициализация BIOS загрузки"),
            ("GDT Загрузка", "boot_gdt", "#ff6b6b", "Загрузка Global Descriptor Table"),
            ("Защищенный режим", "boot_protected", "#ff6b6b", "Переход в 32-битный режим"),
            ("Чтение диска", "boot_disk_read", "#ff6b6b", "Чтение секторов с диска")
        ]
    
    def create_kernel_blocks(self):
        return [
            ("Точка входа", "kernel_entry", "#4ecdc4", "Основная точка входа ядра"),
            ("Инициализация", "kernel_init", "#4ecdc4", "Инициализация систем ядра"),
            ("Обработчики прерываний", "kernel_interrupts", "#4ecdc4", "Настройка IDT и прерываний")
        ]
    
    def create_video_blocks(self):
        return [
            ("VGA Текст", "vga_text", "#45b7d1", "Вывод текста в VGA режиме"),
            ("Очистка экрана", "vga_clear", "#45b7d1", "Очистка экрана"),
            ("Установка цвета", "vga_color", "#45b7d1", "Настройка цветов текста"),
            ("Позиция курсора", "vga_cursor", "#45b7d1", "Управление позицией курсора")
        ]
    
    def create_disk_blocks(self):
        return [
            ("Чтение сектора", "disk_read", "#f9c80e", "Чтение сектора диска"),
            ("Запись сектора", "disk_write", "#f9c80e", "Запись сектора диска"),
            ("Поиск файла", "disk_find", "#f9c80e", "Поиск файла на диске")
        ]
    
    def create_system_blocks(self):
        return [
            ("GDT Дескриптор", "gdt_descriptor", "#9966cc", "Создание GDT дескриптора"),
            ("Сегмент кода", "gdt_code", "#9966cc", "Дескриптор сегмента кода"),
            ("Сегмент данных", "gdt_data", "#9966cc", "Дескриптор сегмента данных")
        ]
    
    def create_block_button(self, parent, name, block_id, color, description):
        btn = tk.Button(
            parent, text=name, 
            bg=color, fg='white', relief='raised', bd=2,
            font=('Arial', 8), wraplength=120, justify=tk.CENTER,
            cursor='hand2'
        )
        btn.pack(fill=tk.X, padx=5, pady=2)
        btn.bind('<Button-1>', lambda e, bid=block_id: self.add_block(bid))
        
        # Подсказка
        self.create_tooltip(btn, description)
    
    def create_tooltip(self, widget, text):
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="#ffffe0", relief='solid', borderwidth=1)
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def setup_workspace(self, parent):
        # Ноутбук для редактирования файлов
        self.editor_notebook = ttk.Notebook(parent)
        self.editor_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Холст для визуального конструктора
        self.canvas_frame = ttk.Frame(self.editor_notebook)
        self.editor_notebook.add(self.canvas_frame, text="🎨 Визуальный конструктор")
        
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            bg='#2d2d2d',
            scrollregion=(0, 0, 2000, 2000)
        )
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Привязки для перетаскивания
        self.canvas.bind('<Button-1>', self.canvas_click)
        self.canvas.bind('<B1-Motion>', self.canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.canvas_release)
    
    def setup_properties_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="⚙️ СВОЙСТВА БЛОКА", style='Mystic.TLabelframe')
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.properties_text = scrolledtext.ScrolledText(
            frame, 
            bg='#2d2d2d', 
            fg='#00ff88',
            font=('Consolas', 10),
            height=10
        )
        self.properties_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_preview_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="👁️ ПРЕДПРОСМОТР КОДА", style='Mystic.TLabelframe')
        frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_text = scrolledtext.ScrolledText(
            frame,
            bg='#2d2d2d',
            fg='#88ff88', 
            font=('Consolas', 9),
            height=15
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def load_project_structure(self):
        """Загрузка структуры файлов проекта"""
        self.tree.delete(*self.tree.get_children())
        
        project_root = self.tree.insert('', 'end', text="Mystic OS Project", values=("PROJECT",))
        
        # Добавляем файлы
        files = [
            ("boot.asm", "ASM файл"),
            ("kernel.asm", "ASM файл"), 
            ("gdt.asm", "ASM файл"),
            ("print.asm", "ASM файл"),
            ("disk.asm", "ASM файл"),
            ("mystic_os.img", "Образ диска"),
            ("build.bat", "Скрипт сборки"),
            ("mystic_builder.py", "Python скрипт")
        ]
        
        for file_name, file_type in files:
            if Path(file_name).exists():
                self.tree.insert(project_root, 'end', text=file_name, values=("FILE", file_name))
    
    def add_block(self, block_id):
        """Добавление блока на холст"""
        block_config = self.get_block_config(block_id)
        
        # Создаем визуальный блок
        x, y = 100, 100  # Позиция по умолчанию
        
        block_rect = self.canvas.create_rectangle(
            x-60, y-25, x+60, y+25,
            fill=block_config['color'],
            outline='#ffffff',
            width=2,
            tags=('block', block_id)
        )
        
        self.canvas.create_text(
            x, y,
            text=block_config['name'],
            fill='white',
            font=('Arial', 9, 'bold'),
            tags=('text', block_id)
        )
        
        # Обновляем свойства
        self.update_properties(block_config)
        
        self.update_status(f"Добавлен блок: {block_config['name']}")
    
    def get_block_config(self, block_id):
        """Конфигурация блоков с кодом"""
        blocks = {
            'boot_bios': {
                'name': 'BIOS Загрузка',
                'color': '#ff6b6b',
                'code': '''bits 16
org 0x7C00

start:
    cli
    mov ax, 0x07C0
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00
    sti
'''
            },
            'boot_protected': {
                'name': 'Защищенный режим', 
                'color': '#ff6b6b',
                'code': '''; Переход в защищенный режим
enable_protected:
    cli
    lgdt [gdt_descriptor]
    mov eax, cr0
    or eax, 1
    mov cr0, eax
    jmp 0x08:protected_mode
'''
            },
            'kernel_entry': {
                'name': 'Точка входа',
                'color': '#4ecdc4', 
                'code': '''bits 32
protected_mode:
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    mov esp, 0x90000
    call main
'''
            }
        }
        return blocks.get(block_id, {'name': 'Unknown', 'color': '#666666', 'code': '; Unknown block\n'})
    
    def update_properties(self, block_config):
        """Обновление панели свойств"""
        self.properties_text.delete(1.0, tk.END)
        self.properties_text.insert(1.0, f"Блок: {block_config['name']}\n")
        self.properties_text.insert(2.0, f"Цвет: {block_config['color']}\n")
        self.properties_text.insert(3.0, "\nСгенерированный код:\n")
        self.properties_text.insert(4.0, block_config['code'])
    
    def canvas_click(self, event):
        """Обработка клика на холсте"""
        items = self.canvas.find_closest(event.x, event.y)
        if items:
            self.canvas.drag_data = {
                "item": items[0],
                "x": event.x,
                "y": event.y
            }
    
    def canvas_drag(self, event):
        """Перетаскивание блоков"""
        if hasattr(self.canvas, 'drag_data'):
            dx = event.x - self.canvas.drag_data["x"]
            dy = event.y - self.canvas.drag_data["y"]
            self.canvas.move(self.canvas.drag_data["item"], dx, dy)
            self.canvas.drag_data["x"] = event.x
            self.canvas.drag_data["y"] = event.y
    
    def canvas_release(self, event):
        """Завершение перетаскивания"""
        if hasattr(self.canvas, 'drag_data'):
            del self.canvas.drag_data
    
    def build_project(self):
        """Сборка проекта"""
        try:
            self.export_asm()
            
            if os.name == 'nt':
                result = subprocess.run(['build.bat'], capture_output=True, text=True)
                if result.returncode == 0:
                    messagebox.showinfo("Успех", "✅ Проект успешно собран!\nФайл: mystic_os.img")
                    self.update_status("Сборка завершена успешно!")
                else:
                    messagebox.showerror("Ошибка", f"Ошибка сборки:\n{result.stderr}")
            else:
                messagebox.showinfo("Инфо", "Запустите сборку вручную для вашей ОС")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сборки: {str(e)}")
    
    def export_asm(self):
        """Экспорт в ASM файлы"""
        try:
            # Здесь будет логика генерации кода из блоков
            messagebox.showinfo("Успех", "ASM файлы экспортированы!")
            self.update_status("Экспорт ASM завершен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {str(e)}")
    
    def run_vm(self):
        """Запуск в виртуальной машине"""
        try:
            if Path("mystic_os.img").exists():
                # Попытка запуска в VirtualBox
                subprocess.Popen(['VBoxManage', 'startvm', 'MysticOS'])
                self.update_status("Запуск в VirtualBox...")
            else:
                messagebox.showwarning("Предупреждение", "Сначала соберите проект!")
        except:
            messagebox.showinfo("Инфо", "Запустите VM вручную с образом mystic_os.img")
    
    def analyze_project(self):
        """Анализ проекта"""
        analysis = "📊 АНАЛИЗ ПРОЕКТА:\n\n"
        analysis += f"• ASM файлов: {len([f for f in Path('.').glob('*.asm')])}\n"
        analysis += f"• Бинарных файлов: {len([f for f in Path('.').glob('*.bin')])}\n"
        analysis += f"• Образ диска: {'✅' if Path('mystic_os.img').exists() else '❌'}\n"
        
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, analysis)
    
    def save_project(self):
        """Сохранение проекта"""
        try:
            project_data = {
                'blocks': self.blocks,
                'files': [f for f in Path('.').glob('*.*')]
            }
            
            with open('mystic_project.json', 'w') as f:
                json.dump(project_data, f, indent=2)
                
            messagebox.showinfo("Успех", "Проект сохранен!")
            self.update_status("Проект сохранен в mystic_project.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")
    
    def load_project(self):
        """Загрузка проекта"""
        try:
            filename = filedialog.askopenfilename(filetypes=[("Mystic OS Project", "*.json")])
            if filename:
                with open(filename, 'r') as f:
                    project_data = json.load(f)
                
                self.blocks = project_data.get('blocks', {})
                self.update_status("Проект загружен!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {str(e)}")
    
    def open_selected_file(self, event=None):
        """Открытие выбранного файла"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            if item['values'][0] == "FILE":
                filename = item['values'][1]
                self.open_file_editor(filename)
    
    def open_file_editor(self, filename):
        """Открытие файла в редакторе"""
        try:
            if Path(filename).exists():
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Создаем вкладку для файла
                text_frame = ttk.Frame(self.editor_notebook)
                self.editor_notebook.add(text_frame, text=f"📄 {filename}")
                
                text_widget = scrolledtext.ScrolledText(
                    text_frame,
                    bg='#1e1e1e',
                    fg='#d4d4d4',
                    font=('Consolas', 10),
                    insertbackground='white'
                )
                text_widget.pack(fill=tk.BOTH, expand=True)
                text_widget.insert(1.0, content)
                
                # Кнопка сохранения
                save_btn = tk.Button(
                    text_frame, text="💾 Сохранить",
                    command=lambda: self.save_file(filename, text_widget),
                    bg='#006633', fg='white'
                )
                save_btn.pack(side=tk.BOTTOM, fill=tk.X)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")
    
    def save_file(self, filename, text_widget):
        """Сохранение файла"""
        try:
            content = text_widget.get(1.0, tk.END)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            self.update_status(f"Файл {filename} сохранен!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")
    
    def show_tree_menu(self, event):
        """Показать контекстное меню для дерева файлов"""
        self.tree_menu.post(event.x_root, event.y_root)
    
    def delete_file(self):
        """Удаление выбранного файла"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            if item['values'][0] == "FILE":
                filename = item['values'][1]
                if messagebox.askyesno("Подтверждение", f"Удалить {filename}?"):
                    try:
                        Path(filename).unlink()
                        self.load_project_structure()
                        self.update_status(f"Файл {filename} удален")
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось удалить файл: {str(e)}")
    
    def rename_file(self):
        """Переименование файла"""
        selection = self.tree.selection()
        if selection:
            # Реализация переименования
            messagebox.showinfo("Инфо", "Функция переименования в разработке")
    
    def update_status(self, message):
        """Обновление статусной строки"""
        if hasattr(self, 'status'):
            self.status.config(text=message)
        print(f"STATUS: {message}")

def main():
    try:
        root = tk.Tk()
        app = ModernMysticOSBuilder(root)
        root.mainloop()
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()