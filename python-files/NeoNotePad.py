import tkinter as tk
from tkinter import filedialog, messagebox, Menu

class NotepadWithInfo:
    def __init__(self, root):
        self.root = root
        self.root.title("NeoNotePad")
        self.root.geometry("640x480")

        # Создаем меню
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Файл меню
        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Создать", command=self.new_file)
        file_menu.add_command(label="Открыть", command=self.open_file)
        file_menu.add_command(label="Сохранить как...", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        self.menu_bar.add_cascade(label="Файл", menu=file_menu)

        # О программе меню
        help_menu = Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        self.menu_bar.add_cascade(label="Помощь", menu=help_menu)

        # Текстовый редактор
        self.text_area = tk.Text(self.root, wrap='word')
        self.text_area.pack(fill=tk.BOTH, expand=1)

    def new_file(self):
        """Создать новый файл"""
        if messagebox.askyesno("Создать новый файл", "Очистить текущий документ?"):
            self.text_area.delete(1.0, tk.END)

    def open_file(self):
        """Открыть файл"""
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Neo-Текстовые файлы", "*.neotxt"), ("Все файлы", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("Ошибка открытия файла", str(e))

    def save_file(self):
        """Сохранить файл"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Neo-Текстовые файлы", "*.neotxt"), ("Все файлы", "*.*")]
        )
        if file_path:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Сохранено", "Файл успешно сохранен.")
            except Exception as e:
                messagebox.showerror("Ошибка сохранения файла", str(e))

    def show_about(self):
        """Показать информацию о программе"""
        about_text = (
            "Программа: NeoNotePad\n"
            "Версия: 1.1\n"
            "Разработчик: MiniSurka\n"
            "Описание: Простое приложение для редактирования текста."
        )
        messagebox.showinfo("О программе", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = NotepadWithInfo(root)
    root.mainloop()
