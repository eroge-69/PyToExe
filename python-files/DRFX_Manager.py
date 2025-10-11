import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import zipfile
import tempfile

# Путь к темплейтам Resolve
TEMPLATES_DIR = os.path.join(
    os.getenv("APPDATA"),
    "Blackmagic Design",
    "DaVinci Resolve",
    "Support",
    "Fusion",
    "Templates"
)

class DRFXManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DaVinci Resolve DRFX Manager")
        self.geometry("600x400")
        self.resizable(False, False)

        ttk.Label(self, text="DaVinci Resolve DRFX Manager", font=("Segoe UI", 14, "bold")).pack(pady=10)
        ttk.Label(self, text=f"Templates folder:\n{TEMPLATES_DIR}", font=("Segoe UI", 9)).pack()

        # Кнопки управления
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Установить DRFX", command=self.install_drfx).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Удалить выбранное", command=self.delete_selected).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Обновить список", command=self.refresh_list).grid(row=0, column=2, padx=5)

        # Список установленных паков
        self.tree = ttk.Treeview(self, columns=("size"), show="headings", selectmode="extended")
        self.tree.heading("size", text="Папка / Размер")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        self.refresh_list()

    def get_folder_size(self, folder):
        total = 0
        for root, _, files in os.walk(folder):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except:
                    pass
        return total

    def refresh_list(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        if not os.path.exists(TEMPLATES_DIR):
            os.makedirs(TEMPLATES_DIR)

        folders = [f for f in os.listdir(TEMPLATES_DIR) if os.path.isdir(os.path.join(TEMPLATES_DIR, f))]
        for f in folders:
            size = self.get_folder_size(os.path.join(TEMPLATES_DIR, f)) // 1024
            self.tree.insert("", "end", values=(f"{f}  ({size} KB)"))

    def install_drfx(self):
        file_paths = filedialog.askopenfilenames(title="Выбери DRFX файлы", filetypes=[("DaVinci Templates", "*.drfx")])
        if not file_paths:
            return

        for path in file_paths:
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    with zipfile.ZipFile(path, "r") as z:
                        z.extractall(tmpdir)
                    for root, dirs, files in os.walk(tmpdir):
                        rel_path = os.path.relpath(root, tmpdir)
                        dest_dir = os.path.join(TEMPLATES_DIR, rel_path)
                        os.makedirs(dest_dir, exist_ok=True)
                        for file in files:
                            shutil.copy2(os.path.join(root, file), os.path.join(dest_dir, file))
                print(f"Установлено: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось установить {path}\n\n{e}")
        messagebox.showinfo("Готово", "Установка завершена!")
        self.refresh_list()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Удаление", "Выбери хотя бы один пакет для удаления.")
            return

        if not messagebox.askyesno("Подтверждение", "Удалить выбранные пакеты?"):
            return

        for item in selected:
            folder_text = self.tree.item(item, "values")[0]
            folder_name = folder_text.split("  (")[0].strip()
            folder_path = os.path.join(TEMPLATES_DIR, folder_name)
            try:
                shutil.rmtree(folder_path)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить {folder_name}\n\n{e}")

        messagebox.showinfo("Готово", "Удаление завершено!")
        self.refresh_list()


if __name__ == "__main__":
    app = DRFXManager()
    app.mainloop()
