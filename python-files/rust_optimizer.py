import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil

class RustOptimizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Rust FPS Booster 1.0")
        self.root.geometry("650x550")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)
        
        # Путь к конфигу (ваш вариант)
        self.config_path = "C:\\SteamLibrary\\steamapps\\common\\Rust\\cfg\\client.cfg"
        self.backup_path = "C:\\SteamLibrary\\steamapps\\common\\Rust\\cfg\\client_backup.cfg"
        
        # Создаём резервную копию конфига
        self.create_backup()
        
        # Настройка интерфейса
        self.setup_ui()

    def create_backup(self):
        """Создаёт резервную копию конфига"""
        if os.path.exists(self.config_path) and not os.path.exists(self.backup_path):
            try:
                shutil.copy2(self.config_path, self.backup_path)
            except Exception as e:
                messagebox.showwarning("Ошибка", f"Не удалось создать резервную копию:\n{e}")

    def setup_ui(self):
        # Стиль
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="#00ffaa", font=("Arial", 12))
        style.configure("TButton", background="#2a2a2a", foreground="#ffffff", font=("Arial", 12))
        style.map("TButton", background=[("active", "#3a3a3a")])
        
        # Заголовок
        header = ttk.Label(
            self.root,
            text="RUST FPS OPTIMIZER 1.0",
            font=("Arial", 20, "bold"),
            foreground="#00ffaa"
        )
        header.pack(pady=10)

        # Информация
        info_frame = ttk.Frame(self.root)
        info_frame.pack(pady=5)
        
        ttk.Label(
            info_frame,
            text="Создано 17.08.25 | 1 человек",
            font=("Arial", 10),
            foreground="#7f7f7f"
        ).pack()

        # Проверка конфига
        self.config_status = ttk.Label(
            self.root,
            text=f"Конфиг: {'Найден' if os.path.exists(self.config_path) else 'Не найден!'}",
            foreground="#00ffaa" if os.path.exists(self.config_path) else "#ff5555"
        )
        self.config_status.pack(pady=5)

        # Ползунок оптимизации
        ttk.Label(
            self.root,
            text="Уровень оптимизации:",
            font=("Arial", 12)
        ).pack(pady=5)
        
        self.optimization_level = tk.IntVar(value=50)
        scale = tk.Scale(
            self.root,
            from_=0,
            to=100,
            variable=self.optimization_level,
            orient="horizontal",
            length=400,
            bg="#1e1e1e",
            fg="#ffffff",
            troughcolor="#2a2a2a",
            activebackground="#00ffaa",
            highlightthickness=0
        )
        scale.pack(pady=10)

        # Чекбоксы
        options_frame = ttk.Frame(self.root)
        options_frame.pack(pady=15)
        
        self.grass_var = tk.IntVar()
        grass_cb = tk.Checkbutton(
            options_frame,
            text="Отключить траву",
            variable=self.grass_var,
            bg="#1e1e1e",
            fg="#ffffff",
            selectcolor="#1e1e1e",
            activebackground="#1e1e1e",
            activeforeground="#ffffff",
            font=("Arial", 12)
        )
        grass_cb.pack(anchor="w", padx=20, pady=5)

        self.fog_var = tk.IntVar()
        fog_cb = tk.Checkbutton(
            options_frame,
            text="Уменьшить туман",
            variable=self.fog_var,
            bg="#1e1e1e",
            fg="#ffffff",
            selectcolor="#1e1e1e",
            activebackground="#1e1e1e",
            activeforeground="#ffffff",
            font=("Arial", 12)
        )
        fog_cb.pack(anchor="w", padx=20, pady=5)

        # Кнопки
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        apply_btn = ttk.Button(
            btn_frame,
            text="Применить настройки",
            command=self.apply_settings,
            style="TButton"
        )
        apply_btn.pack(side="left", padx=10)

        restore_btn = ttk.Button(
            btn_frame,
            text="Сбросить настройки",
            command=self.restore_settings,
            style="TButton"
        )
        restore_btn.pack(side="left", padx=10)

        exit_btn = ttk.Button(
            btn_frame,
            text="Выход",
            command=self.root.destroy,
            style="TButton"
        )
        exit_btn.pack(side="left", padx=10)

    def apply_settings(self):
        """Применяет выбранные настройки"""
        if not os.path.exists(self.config_path):
            messagebox.showerror("Ошибка", "Файл конфига не найден!")
            return

        try:
            with open(self.config_path, "r") as f:
                config_lines = f.readlines()

            # Оптимизация графики
            opt_level = self.optimization_level.get()
            config_lines = self.set_config_value(config_lines, "graphics.shadowdistance", str(200 - opt_level * 1.5))
            config_lines = self.set_config_value(config_lines, "graphics.drawdistance", str(opt_level * 2))

            # Отключение травы
            if self.grass_var.get():
                config_lines = self.set_config_value(config_lines, "grass.displace", "false")
                config_lines = self.set_config_value(config_lines, "grass.shadow", "false")
                config_lines = self.set_config_value(config_lines, "grass.detail", "0")

            # Уменьшение тумана
            if self.fog_var.get():
                config_lines = self.set_config_value(config_lines, "weather.fog", "0.2")
                config_lines = self.set_config_value(config_lines, "weather.clouds", "0.5")

            # Сохраняем изменения
            with open(self.config_path, "w") as f:
                f.writelines(config_lines)

            messagebox.showinfo("Готово!", "Настройки успешно применены!\nПерезапустите Rust для эффекта.")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось изменить конфиг:\n{e}")

    def restore_settings(self):
        """Восстанавливает настройки из резервной копии"""
        if not os.path.exists(self.backup_path):
            messagebox.showerror("Ошибка", "Резервная копия не найдена!")
            return

        try:
            shutil.copy2(self.backup_path, self.config_path)
            messagebox.showinfo("Готово!", "Настройки сброшены до стандартных!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось восстановить конфиг:\n{e}")

    @staticmethod
    def set_config_value(config_lines, key, value):
        """Изменяет значение параметра в конфиге"""
        for i, line in enumerate(config_lines):
            if line.startswith(key):
                config_lines[i] = f"{key} {value}\n"
                break
        else:
            config_lines.append(f"{key} {value}\n")
        return config_lines

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = RustOptimizer()
    app.run()