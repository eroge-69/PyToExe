import tkinter as tk
import random
import threading
import time
import sys


class AggressiveBlinkingWindows:
    def __init__(self):
        self.windows = []
        self.is_running = True
        self.root = None

    def init_root(self):
        """Инициализация главного окна"""
        self.root = tk.Tk()
        self.root.withdraw()  # Скрываем главное окно

    def create_window(self):
        """Создает мигающее окно"""
        try:
            # Получаем размеры экрана
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            # Случайные размеры и позиция
            width = random.randint(200, 350)
            height = random.randint(80, 120)
            x = random.randint(0, max(0, screen_width - width))
            y = random.randint(0, max(0, screen_height - height))

            # Создаем окно
            window = tk.Toplevel(self.root)
            window.geometry(f"{width}x{height}+{x}+{y}")
            window.overrideredirect(True)  # Убираем рамку окна
            window.attributes('-topmost', True)
            window.attributes('-alpha', 0.9)  # Небольшая прозрачность

            # Выбираем случайный эффект мигания
            effect_type = random.choice(['red_blink', 'color_switch', 'pulse', 'rainbow'])

            # Создаем надпись
            label = tk.Label(
                window,
                text="ПОШЛИ В ДОТУ",
                font=("Arial", random.randint(16, 24), "bold"),
                fg="white",
                bg="red",
                justify='center'
            )
            label.pack(expand=True, fill='both')

            # Добавляем в список
            self.windows.append((window, label, effect_type))

            # Запускаем мигание
            self.start_effect(window, label, effect_type)

            # ESC для остановки
            window.bind('<Escape>', lambda e: self.stop())
            window.focus_force()

        except Exception as e:
            print(f"Ошибка создания окна: {e}")

    def start_effect(self, window, label, effect_type):
        """Запускает эффект мигания"""

        def effect_loop():
            if not self.is_running or not window.winfo_exists():
                return

            try:
                if effect_type == 'red_blink':
                    self.red_blink_effect(window, label)
                elif effect_type == 'color_switch':
                    self.color_switch_effect(window, label)
                elif effect_type == 'pulse':
                    self.pulse_effect(window, label)
                elif effect_type == 'rainbow':
                    self.rainbow_effect(window, label)

                # Очень быстрое обновление
                window.after(30, effect_loop)
            except:
                pass

        effect_loop()

    def red_blink_effect(self, window, label):
        """Мигание красными цветами"""
        colors = ['red', 'darkred', 'maroon', 'firebrick', 'crimson', 'brown']
        color = random.choice(colors)
        window.configure(bg=color)
        label.configure(bg=color, fg='white')

    def color_switch_effect(self, window, label):
        """Быстрое переключение цветов"""
        color_pairs = [
            ('red', 'white'), ('black', 'red'),
            ('yellow', 'red'), ('white', 'red'),
            ('red', 'yellow'), ('darkblue', 'white')
        ]
        bg, fg = random.choice(color_pairs)
        window.configure(bg=bg)
        label.configure(bg=bg, fg=fg)

    def pulse_effect(self, window, label):
        """Пульсирующий эффект"""
        sizes = [14, 16, 18, 20, 22, 24, 26, 24, 22, 20, 18, 16]
        size = random.choice(sizes)
        colors = ['red', 'darkred', 'maroon']
        color = random.choice(colors)

        label.configure(font=("Arial", size, "bold"))
        window.configure(bg=color)
        label.configure(bg=color, fg='white')

    def rainbow_effect(self, window, label):
        """Радужный эффект"""
        colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink']
        bg_color = random.choice(colors)
        fg_color = random.choice([c for c in colors if c != bg_color])

        window.configure(bg=bg_color)
        label.configure(bg=bg_color, fg=fg_color)

    def ultra_fast_spawn(self):
        """Ультра-быстрый спавн окон"""
        spawn_count = 0
        while self.is_running:
            try:
                self.create_window()
                spawn_count += 1

                # Очистка старых окон (если их слишком много)
                if len(self.windows) > 100:
                    for _ in range(20):
                        if self.windows:
                            window, label, _ = self.windows.pop(0)
                            try:
                                window.destroy()
                            except:
                                pass

                if spawn_count % 50 == 0:
                    print(f"Создано окон: {spawn_count}, Активно: {len(self.windows)}")

                time.sleep(0.01)  # 0.01 секунды между созданием окон

            except Exception as e:
                print(f"Ошибка в спавне: {e}")
                time.sleep(0.001)

    def stop(self):
        """Остановка программы"""
        self.is_running = False
        print("\n!!! ОСТАНОВКА ПРОГРАММЫ !!!")

        # Закрываем все окна
        for window, label, _ in self.windows:
            try:
                window.destroy()
            except:
                pass

        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass

        print("Все окна закрыты. Выход.")
        sys.exit()


def main():
    print("=" * 60)
    print("АГРЕССИВНЫЙ РЕЖИМ ЗАПУЩЕН!")
    print("Окна создаются каждые 0.01 секунды")
    print("Разные эффекты мигания")
    print("ESC для экстренной остановки")
    print("=" * 60)

    app = AggressiveBlinkingWindows()
    app.init_root()

    # Запускаем спавн окон
    spawn_thread = threading.Thread(target=app.ultra_fast_spawn, daemon=True)
    spawn_thread.start()

    # Обработка ESC в главном окне
    app.root.bind('<Escape>', lambda e: app.stop())

    try:
        app.root.mainloop()
    except KeyboardInterrupt:
        app.stop()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        app.stop()


if __name__ == "__main__":
    main()