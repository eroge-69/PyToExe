import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

class AhkLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("AHK LAUNCHER")
        self.ahk_files = {}  # словарь для хранения путей к файлам

        # Общий стиль
        self.root.geometry("500x600")
        self.root.configure(bg="#f0f0f0")

        # Заголовок
        title_label = tk.Label(
            self.root, text="AHK LAUNCHER",
            font=("Helvetica", 24, "bold"),
            bg="#f0f0f0",
            fg="#333"
        )
        title_label.pack(pady=20)

        # Область для списка файлов
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill=tk.BOTH, expand=True, padx=20)

        self.listbox = tk.Listbox(
            frame, height=12,
            font=("Arial", 14),
            selectbackground="#3399ff",
            activestyle='none'
        )
        self.listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Кнопки
        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=20)

        add_btn = tk.Button(
            btn_frame, text="Добавить файл",
            font=("Arial", 12),
            command=self.add_ahk_file,
            bg="#4CAF50", fg="white",
            width=15, height=2,
            relief=tk.RAISED
        )
        add_btn.pack(side=tk.LEFT, padx=10)

        run_btn = tk.Button(
            btn_frame, text="Запустить выбранное",
            font=("Arial", 12),
            command=self.run_selected,
            bg="#2196F3", fg="white",
            width=15, height=2,
            relief=tk.RAISED
        )
        run_btn.pack(side=tk.LEFT, padx=10)

        delete_btn = tk.Button(
            btn_frame, text="Удалить выбранное",
            font=("Arial", 12),
            command=self.delete_selected,
            bg="#f44336", fg="white",
            width=15, height=2,
            relief=tk.RAISED
        )
        delete_btn.pack(side=tk.LEFT, padx=10)

    def add_ahk_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите .ahk файл",
            filetypes=[("AutoHotkey files", "*.ahk")]
        )
        if file_path:
            filename = file_path.split("/")[-1]
            if filename in self.ahk_files:
                messagebox.showwarning("Предупреждение", "Этот файл уже добавлен.")
                return
            self.ahk_files[filename] = file_path
            self.listbox.insert(tk.END, filename)

    def run_selected(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("Информация", "Пожалуйста, выберите файл для запуска.")
            return
        filename = self.listbox.get(selected_indices[0])
        file_path = self.ahk_files[filename]
        try:
            subprocess.Popen(["AutoHotkey.exe", file_path])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить файл: {e}")

    def delete_selected(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("Информация", "Пожалуйста, выберите файл для удаления.")
            return
        index = selected_indices[0]
        filename = self.listbox.get(index)
        del self.ahk_files[filename]
        self.listbox.delete(index)

if __name__ == "__main__":
    root = tk.Tk()
    app = AhkLauncher(root)
    root.mainloop()
