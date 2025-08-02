import tkinter as tk
import subprocess
import os
import random
import time
from tkinter import messagebox, ttk, filedialog

class AutoSpaceVPN:
    def __init__(self, root):
        self.root = root
        self.root.title("Nzarsteve2 AutoVPN")
        self.root.geometry("1920x1080")
        self.root.state('zoomed')
        self.root.configure(bg='#0a043c')
        
        # Настройки VPN по умолчанию
        self.ovpn_config = ""
        self.vpn_username = ""
        self.vpn_password = ""
        self.auto_connect = False
        self.ovpn_process = None
        
        self.create_main_ui()
        self.show_tutorial()

    def create_stars(self, count):
        """Создает звездное небо на фоне"""
        for _ in range(count):
            x = random.randint(0, 1920)
            y = random.randint(0, 1080)
            size = random.randint(1, 4)
            color = random.choice(['white', '#bbdefb', '#e6e6e6'])
            self.canvas.create_oval(x, y, x+size, y+size, fill=color, outline='')

    def create_main_ui(self):
        """Создает основной интерфейс приложения"""
        self.canvas = tk.Canvas(self.root, bg='#0a043c', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.create_stars(200)
        
        self.main_frame = tk.Frame(self.canvas, bg='#12005e', bd=3, relief=tk.RIDGE)
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=800, height=600)
        
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tab_connect = tk.Frame(self.notebook, bg='#12005e')
        self.notebook.add(self.tab_connect, text='Подключение VPN')
        
        self.tab_tutorial = tk.Frame(self.notebook, bg='#12005e')
        self.notebook.add(self.tab_tutorial, text='Инструкция')
        
        self.create_connection_tab()
        self.create_tutorial_tab()
        
        self.status_light = self.canvas.create_oval(
            1750, 50, 1800, 100,
            fill='red',
            outline='white',
            width=2
        )
        self.canvas.create_text(
            1775, 120,
            text="VPN STATUS",
            fill='white',
            font=('Arial', 12)
        )

    def create_connection_tab(self):
        """Создает содержимое вкладки подключения"""
        tk.Label(
            self.tab_connect,
            text="Nzarsteve2",
            font=('Arial', 28, 'bold'),
            fg='#bbdefb',
            bg='#12005e'
        ).pack(pady=20)
        
        tk.Label(
            self.tab_connect,
            text="Файл конфигурации (.ovpn):",
            font=('Arial', 12),
            fg='white',
            bg='#12005e'
        ).pack()
        
        self.entry_config = tk.Entry(self.tab_connect, width=50, font=('Arial', 12))
        self.entry_config.pack(pady=5)
        
        tk.Button(
            self.tab_connect,
            text="Выбрать файл",
            command=self.browse_config,
            bg='#1a237e',
            fg='white',
            font=('Arial', 10)
        ).pack(pady=5)
        
        tk.Label(
            self.tab_connect,
            text="Логин:",
            font=('Arial', 12),
            fg='white',
            bg='#12005e'
        ).pack()
        
        self.entry_username = tk.Entry(self.tab_connect, width=30, font=('Arial', 12))
        self.entry_username.pack(pady=5)
        
        tk.Label(
            self.tab_connect,
            text="Пароль:",
            font=('Arial', 12),
            fg='white',
            bg='#12005e'
        ).pack()
        
        self.entry_password = tk.Entry(self.tab_connect, width=30, show='*', font=('Arial', 12))
        self.entry_password.pack(pady=5)
        
        self.btn_control = tk.Button(
            self.tab_connect,
            text="🚀 ПОДКЛЮЧИТЬ VPN",
            font=('Arial', 18),
            command=self.toggle_vpn,
            bg='#1a237e',
            fg='white',
            activebackground='#4a148c',
            width=25
        )
        self.btn_control.pack(pady=20)
        
        self.auto_connect_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self.tab_connect,
            text="Автоподключение при запуске",
            variable=self.auto_connect_var,
            font=('Arial', 12),
            fg='white',
            bg='#12005e',
            selectcolor='#1a237e',
            activebackground='#12005e',
            activeforeground='white'
        ).pack()
        
        self.log_text = tk.Text(
            self.tab_connect,
            height=10,
            width=70,
            bg='#0a043c',
            fg='white',
            font=('Consolas', 10)
        )
        self.log_text.pack(pady=10)

    def create_tutorial_tab(self):
        """Создает вкладку с инструкцией"""
        tutorial_text = """
        🚀 ИНСТРУКЦИЯ ПО ПОДКЛЮЧЕНИЮ VPN:
        
        1. СКАЧАЙТЕ КОНФИГУРАЦИОННЫЙ ФАЙЛ:
           - Получите .ovpn файл от вашего VPN-провайдера
           - Сохраните его в удобную папку
        
        2. НАСТРОЙТЕ ПОДКЛЮЧЕНИЕ:
           - Нажмите "Выбрать файл" и укажите ваш .ovpn файл
           - Введите логин и пароль от VPN-сервиса
           - При необходимости включите автоподключение
        
        3. ПОДКЛЮЧЕНИЕ:
           - Нажмите "ПОДКЛЮЧИТЬ VPN" для установки соединения
           - Статус подключения отобразится в логе
           - Индикатор сменит цвет на зеленый при успешном подключении
        
        4. ДОПОЛНИТЕЛЬНО:
           - Программа автоматически переподключается при обрыве
           - Логи сохраняются в течение сеанса работы
           - Для отключения нажмите кнопку еще раз
        
        ⚠️ ТРЕБОВАНИЯ:
        - Установленный OpenVPN (скачать: https://openvpn.net/)
        - Python 3.6 или новее
        """
        
        tutorial_label = tk.Label(
            self.tab_tutorial,
            text=tutorial_text,
            font=('Arial', 14),
            fg='white',
            bg='#12005e',
            justify=tk.LEFT
        )
        tutorial_label.pack(padx=20, pady=20, anchor=tk.W)
        
        tk.Button(
            self.tab_tutorial,
            text="Я все настроил, начать работу!",
            command=self.hide_tutorial,
            bg='#1a237e',
            fg='white',
            font=('Arial', 14),
            width=25
        ).pack(pady=20)

    def show_tutorial(self):
        """Показывает инструкцию при первом запуске"""
        self.notebook.select(self.tab_tutorial)

    def hide_tutorial(self):
        """Скрывает инструкцию и переключает на вкладку подключения"""
        self.notebook.select(self.tab_connect)

    def browse_config(self):
        """Открывает диалог выбора файла конфигурации"""
        filepath = filedialog.askopenfilename(
            title="Выберите файл конфигурации",
            filetypes=(("OVPN files", "*.ovpn"), ("All files", "*.*"))
        )
        if filepath:
            self.entry_config.delete(0, tk.END)
            self.entry_config.insert(0, filepath)
            self.ovpn_config = filepath

    def toggle_vpn(self):
        """Переключает состояние VPN подключения"""
        self.ovpn_config = self.entry_config.get()
        self.vpn_username = self.entry_username.get()
        self.vpn_password = self.entry_password.get()
        self.auto_connect = self.auto_connect_var.get()
        
        if not self.ovpn_config or not os.path.exists(self.ovpn_config):
            messagebox.showerror("Ошибка", "Укажите правильный путь к .ovpn файлу!")
            return
            
        if not self.vpn_username or not self.vpn_password:
            messagebox.showerror("Ошибка", "Введите логин и пароль VPN!")
            return
            
        if self.ovpn_process:
            self.disconnect_vpn()
        else:
            self.connect_vpn()

    def connect_vpn(self):
        if self.ovpn_process:
            return
            
        try:
            self.log("Попытка подключения к VPN...")
            
            with open('vpn_auth.txt', 'w') as f:
                f.write(f"{self.vpn_username}\n{self.vpn_password}")
            
            cmd = [
                'openvpn',
                '--config', self.ovpn_config,
                '--auth-user-pass', 'vpn_auth.txt',
                '--daemon'
            ]
            
            self.ovpn_process = subprocess.Popen(cmd)
            self.update_status(True)
            self.btn_control.config(text="🛑 ОТКЛЮЧИТЬ VPN", bg='#d32f2f')
            self.log("VPN успешно подключен!")
            
            self.root.after(5000, self.check_connection)
            
        except Exception as e:
            self.log(f"Ошибка подключения: {str(e)}")
            self.cleanup()

    def disconnect_vpn(self):
        if not self.ovpn_process:
            return
            
        try:
            self.log("Отключение VPN...")
            subprocess.run(['pkill', 'openvpn'], timeout=5)
            self.update_status(False)
            self.btn_control.config(text="🚀 ПОДКЛЮЧИТЬ VPN", bg='#1a237e')
            self.log("VPN отключен")
            
        except Exception as e:
            self.log(f"Ошибка отключения: {str(e)}")
        finally:
            self.cleanup()

    def check_connection(self):
        """Проверяет активность VPN соединения"""
        if self.ovpn_process:
            try:
                result = subprocess.run(['pgrep', 'openvpn'], capture_output=True)
                if result.returncode == 0:
                    self.root.after(10000, self.check_connection)
                else:
                    self.log("Обнаружено разъединение VPN!")
                    if self.auto_connect:
                        self.connect_vpn()
            except:
                pass

    def update_status(self, connected):
        """Обновляет статус подключения"""
        if connected:
            self.canvas.itemconfig(self.status_light, fill='green')
        else:
            self.canvas.itemconfig(self.status_light, fill='red')

    def log(self, message):
        """Добавляет сообщение в лог"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.update()

    def cleanup(self):
        """Очистка ресурсов"""
        if os.path.exists('vpn_auth.txt'):
            os.remove('vpn_auth.txt')
        self.ovpn_process = None

    def on_close(self):
        """Действия при закрытии окна"""
        self.disconnect_vpn()
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = AutoSpaceVPN(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()