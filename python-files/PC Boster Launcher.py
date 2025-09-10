import customtkinter as ctk
import os
import time
import win32com.client
import math
from PIL import Image, ImageDraw
import sys
import shutil
import tempfile
from ctypes import windll, create_unicode_buffer

# Настройки
APP_NAME = "PCBooster"
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))

# Правильное определение пути к рабочему столу
def get_desktop_path():
    try:
        # Стандартный путь
        desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
        if os.path.exists(desktop):
            return desktop
        
        # Альтернативный метод через Windows API
        try:
            from ctypes import windll, create_unicode_buffer
            buf = create_unicode_buffer(260)
            windll.shell32.SHGetFolderPathW(None, 0x0010, None, 0, buf)
            if os.path.exists(buf.value):
                return buf.value
        except:
            pass
            
        # Если ничего не работает, используем домашнюю директорию
        return os.path.expanduser("~")
        
    except:
        return os.path.expanduser("~")

DESKTOP_PATH = get_desktop_path()
LAUNCHER_EXE = os.path.join(WORKING_DIR, "PCBooster.exe")
SHORTCUT_NAME = "PC Booster.lnk"

class LoadingWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PC Booster - Установка")
        self.geometry("500x400")
        self.configure(fg_color="#1a1a1a")
        self.center_window()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        print("[DEBUG] Запущено первое окно")
        print(f"[DEBUG] Путь к рабочему столу: {DESKTOP_PATH}")

        # Флаг для остановки анимаций
        self.is_running = True

        # Заголовок с эффектом неона
        self.title_label = ctk.CTkLabel(
            self, 
            text="PC BOOSTER", 
            font=("Arial", 32, "bold"),
            text_color="#00ff00"
        )
        self.title_label.pack(pady=60)

        # Подзаголовок
        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Оптимизация системы",
            font=("Arial", 14),
            text_color="#88ffaa"
        )
        self.subtitle_label.pack(pady=5)

        # Контейнер для кружков
        self.circles_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.circles_frame.pack(pady=40)

        # Кружки с плавной анимацией
        self.circles = []
        for i in range(3):
            circle = ctk.CTkLabel(
                self.circles_frame, 
                text="", 
                width=20, 
                height=20, 
                fg_color="#00ff00", 
                corner_radius=10
            )
            circle.pack(side="left", padx=15)
            self.circles.append({
                'widget': circle,
                'size': 20,
                'target_size': 20,
                'color': "#00ff00",
                'alpha': 1.0
            })
        
        # Прогресс бар
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=300,
            height=4,
            progress_color="#00ff00",
            fg_color="#333333"
        )
        self.progress_bar.pack(pady=20)
        self.progress_bar.set(0)

        # Текст статуса
        self.status_label = ctk.CTkLabel(
            self,
            text="Подготовка к установке...",
            font=("Arial", 12),
            text_color="#88ffaa"
        )
        self.status_label.pack(pady=10)

        # Счётчики для анимации
        self.animation_time = 0
        self.progress_value = 0
        self.current_status = 0
        self.status_messages = [
            "Подготовка к установке...",
            "Загрузка компонентов...",
            "Оптимизация настроек...",
            "Создание ярлыков...",
            "Завершение установки..."
        ]

        # Запуск анимаций
        self.animate_circles()
        self.animate_progress()
        self.animate_status()

        # Переключение на следующее окно через 5 секунд (уменьшил время для теста)
        self.after(5000, self.open_success_window)

    def center_window(self):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 400) // 2
        self.geometry(f"500x400+{x}+{y}")

    def animate_circles(self):
        """Плавная анимация кружков"""
        if not self.is_running:
            return
            
        self.animation_time += 0.1
        
        for i, circle_data in enumerate(self.circles):
            # Плавное пульсирование с разными фазами
            phase = i * (2 * math.pi / 3)
            pulse = math.sin(self.animation_time + phase) * 0.5 + 0.5
            
            # Плавное изменение размера
            target_size = 20 + int(pulse * 15)
            circle_data['size'] += (target_size - circle_data['size']) * 0.2
            
            # Плавное изменение цвета
            intensity = int(255 * pulse)
            color = f"#{intensity:02x}ff{intensity:02x}"
            
            # Обновляем виджет
            circle_data['widget'].configure(
                width=int(circle_data['size']),
                height=int(circle_data['size']),
                fg_color=color
            )
        
        if self.is_running:
            self.after(16, self.animate_circles)

    def animate_progress(self):
        """Плавная анимация прогресс бара"""
        if not self.is_running:
            return
            
        self.progress_value += 0.01  # Увеличил скорость для теста
        if self.progress_value > 1:
            self.progress_value = 1
        
        current_progress = self.progress_bar.get()
        new_progress = current_progress + (self.progress_value - current_progress) * 0.1
        self.progress_bar.set(new_progress)
        
        if new_progress < 1 and self.is_running:
            self.after(50, self.animate_progress)

    def animate_status(self):
        """Анимация смены статусов"""
        if not self.is_running:
            return
            
        self.current_status = (self.current_status + 1) % len(self.status_messages)
        self.status_label.configure(text=self.status_messages[self.current_status])
        
        if self.progress_value < 1 and self.is_running:
            self.after(1500, self.animate_status)  # Увеличил интервал

    def open_success_window(self):
        """Открывает окно успеха"""
        print("[DEBUG] Открываю второе окно")
        self.is_running = False  # Останавливаем все анимации
        self.fade_out()

    def fade_out(self):
        """Плавное исчезновение окна"""
        if not self.winfo_exists():  # Проверяем, существует ли ещё окно
            return
            
        current_alpha = self.attributes('-alpha')
        new_alpha = max(0, current_alpha - 0.05)
        self.attributes('-alpha', new_alpha)
        
        if new_alpha > 0:
            self.after(20, self.fade_out)
        else:
            self.destroy()
            try:
                success_window = SuccessWindow()
                success_window.mainloop()
            except Exception as e:
                print(f"[ERROR] Не удалось открыть второе окно: {e}")
                exit(1)

    def destroy(self):
        """Переопределяем destroy для остановки анимаций"""
        self.is_running = False
        super().destroy()

class SuccessWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PC Booster - Успешная установка")
        self.geometry("500x450")
        self.configure(fg_color="#1a1a1a")
        self.center_window()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Устанавливаем прозрачность для плавного появления
        self.attributes('-alpha', 0)
        self.is_running = True

        print("[DEBUG] Запущено второе окно")
        print(f"[DEBUG] Путь к рабочему столу: {DESKTOP_PATH}")

        # Получаем имя пользователя
        username = os.getlogin()

        # Иконка успеха
        self.create_success_icon()

        # Текст с эффектами
        self.success_label = ctk.CTkLabel(
            self, 
            text="✅ УСПЕШНАЯ УСТАНОВКА", 
            font=("Arial", 24, "bold"),
            text_color="#00ff00"
        )
        self.success_label.pack(pady=20)

        self.welcome_label = ctk.CTkLabel(
            self, 
            text=f"Добро пожаловать, {username}!",
            font=("Arial", 16),
            text_color="#88ffaa"
        )
        self.welcome_label.pack(pady=10)

        # Дополнительная информация
        self.info_label = ctk.CTkLabel(
            self,
            text="PC Booster готов к работе!\nЯрлык будет создан на вашем рабочем столе.",
            font=("Arial", 12),
            text_color="#cccccc",
            justify="center"
        )
        self.info_label.pack(pady=20)

        # Кнопка с анимацией
        self.start_button = ctk.CTkButton(
            self,
            text="🚀 НАЧАТЬ ОПТИМИЗАЦИЮ",
            command=self.create_shortcut,
            width=200,
            height=50,
            fg_color="#00aa44",
            hover_color="#00ff88",
            font=("Arial", 14, "bold"),
            corner_radius=25,
            border_width=2,
            border_color="#00ff00",
            text_color="#222222"
        )
        self.start_button.pack(pady=30)

        # Текст внизу
        self.footer_label = ctk.CTkLabel(
            self,
            text="© 2024 PC Booster. Все права защищены.",
            font=("Arial", 10),
            text_color="#666666"
        )
        self.footer_label.pack(side="bottom", pady=10)

        # Запускаем плавное появление после создания всех виджетов
        self.after(100, self.fade_in)

    def create_success_icon(self):
        """Создаёт иконку успеха"""
        try:
            # Создаём круглую иконку с галочкой
            img = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Рисуем круг
            draw.ellipse([5, 5, 75, 75], fill='#00ff00', outline='#00ff88', width=3)
            
            # Рисуем галочку
            draw.line([25, 40, 40, 55], fill='#1a1a1a', width=4)
            draw.line([40, 55, 65, 30], fill='#1a1a1a', width=4)
            
            # Конвертируем в CTkImage
            success_image = ctk.CTkImage(light_image=img, dark_image=img, size=(80, 80))
            
            # Создаём лейбл с иконкой
            icon_label = ctk.CTkLabel(self, image=success_image, text="")
            icon_label.pack(pady=20)
            
        except Exception as e:
            print(f"[WARNING] Не удалось создать иконку: {e}")
            # Запасной вариант - эмодзи
            icon_label = ctk.CTkLabel(
                self, 
                text="✅", 
                font=("Arial", 48),
                text_color="#00ff00"
            )
            icon_label.pack(pady=20)

    def center_window(self):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 450) // 2
        self.geometry(f"500x450+{x}+{y}")

    def fade_in(self):
        """Плавное появление окна"""
        if not self.is_running or not self.winfo_exists():
            return
            
        current_alpha = self.attributes('-alpha')
        new_alpha = min(1.0, current_alpha + 0.05)
        self.attributes('-alpha', new_alpha)
        
        if new_alpha < 1.0:
            self.after(20, self.fade_in)
        else:
            # Запускаем анимацию кнопки после появления
            self.animate_button()

    def animate_button(self):
        """Анимация кнопки"""
        if not self.is_running or not self.winfo_exists():
            return
            
        current_size = self.start_button.cget("width")
        if current_size < 220:
            self.start_button.configure(width=current_size + 2)
            self.after(10, self.animate_button)

    def create_shortcut(self):
        """Создаёт ярлык на рабочем столе"""
        shortcut_path = os.path.join(DESKTOP_PATH, SHORTCUT_NAME)
        
        try:
            print(f"[INFO] Пытаюсь создать ярлык: {shortcut_path}")
            
            # Проверяем существование целевого файла
            if not os.path.exists(LAUNCHER_EXE):
                error_msg = f"Файл PCBooster.exe не найден по пути:\n{LAUNCHER_EXE}"
                print(f"[ERROR] {error_msg}")
                self.show_error(error_msg)
                return

            # Проверяем доступность рабочего стола
            if not os.path.exists(DESKTOP_PATH):
                error_msg = f"Не удается найти папку рабочего стола:\n{DESKTOP_PATH}"
                print(f"[ERROR] {error_msg}")
                self.show_error(error_msg)
                return

            # Создаём ярлык
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = LAUNCHER_EXE
            shortcut.WorkingDirectory = WORKING_DIR
            shortcut.IconLocation = LAUNCHER_EXE
            shortcut.Description = "PC Booster - Оптимизация системы"
            shortcut.save()
            
            print("[SUCCESS] Ярлык успешно создан")
            self.show_success("Ярлык успешно создан на рабочем столе!")
            
        except Exception as e:
            error_msg = f"Ошибка создания ярлыка:\n{str(e)}"
            print(f"[ERROR] {error_msg}")
            self.show_error(error_msg)

    def show_success(self, message):
        """Показывает сообщение об успехе"""
        self.info_label.configure(text=message, text_color="#00ff00")
        self.start_button.configure(text="✅ ГОТОВО!", state="disabled", fg_color="#00ff00")

    def show_error(self, message):
        """Показывает сообщение об ошибке"""
        self.info_label.configure(text=message, text_color="#ff4444")
        self.start_button.configure(text="⚠️ ПОВТОРИТЬ", fg_color="#ff4444", command=self.retry_create_shortcut)

    def retry_create_shortcut(self):
        """Повторная попытка создания ярлыка"""
        self.info_label.configure(text="Повторная попытка создания...", text_color="#ffcc00")
        self.start_button.configure(text="⏳ ОЖИДАЙТЕ...", state="disabled")
        self.after(1000, self.create_shortcut)

    def destroy(self):
        """Переопределяем destroy для остановки анимаций"""
        self.is_running = False
        super().destroy()

if __name__ == "__main__":
    try:
        print(f"[INFO] Рабочая директория: {WORKING_DIR}")
        print(f"[INFO] Путь к EXE: {LAUNCHER_EXE}")
        print(f"[INFO] EXE существует: {os.path.exists(LAUNCHER_EXE)}")
        
        # Инициализация приложения
        app = LoadingWindow()
        app.mainloop()
    except Exception as e:
        print(f"[FATAL ERROR] Основная программа завершена с ошибкой: {e}")
        # Создаём простое окно с ошибкой
        error_root = ctk.CTk()
        error_root.title("Ошибка")
        error_root.geometry("400x200")
        ctk.CTkLabel(
            error_root, 
            text=f"Произошла ошибка:\n{e}", 
            font=("Arial", 12),
            text_color="#ff4444",
            justify="center"
        ).pack(expand=True)
        error_root.mainloop()