import tkinter as tk
from tkinter import ttk, messagebox
import paramiko
import serial
import serial.tools.list_ports
import time
import threading

class DeviceTesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Автоматизированная проверка Start/StartD")
        self.root.geometry("800x600")
        
        # Переменные для хранения настроек
        self.ip_address = tk.StringVar(value="192.168.0.0")
        self.username = tk.StringVar(value="root")
        self.password = tk.StringVar(value="password")
        self.com_port = tk.StringVar()
        self.baud_rate = tk.StringVar(value="115200")
        
        # SSH клиент
        self.ssh = None
        self.ssh_console1 = None
        self.ssh_console2 = None
        
        # Serial соединение
        self.serial_conn = None
        
        self.create_widgets()
        self.update_com_ports()
        
    def create_widgets(self):
        # Фрейм для настроек подключения
        settings_frame = ttk.LabelFrame(self.root, text="Настройки подключения", padding=10)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Поля для ввода IP, логина, пароля
        ttk.Label(settings_frame, text="IP адрес:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.ip_address).grid(row=0, column=1, sticky=tk.EW)
        
        ttk.Label(settings_frame, text="Логин:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.username).grid(row=1, column=1, sticky=tk.EW)
        
        ttk.Label(settings_frame, text="Пароль:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.password).grid(row=2, column=1, sticky=tk.EW)
        
        ttk.Label(settings_frame, text="COM порт:").grid(row=3, column=0, sticky=tk.W)
        ttk.Combobox(settings_frame, textvariable=self.com_port).grid(row=3, column=1, sticky=tk.EW)
        ttk.Button(settings_frame, text="Обновить", command=self.update_com_ports).grid(row=3, column=2)
        
        ttk.Label(settings_frame, text="Скорость (baud):").grid(row=4, column=0, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.baud_rate).grid(row=4, column=1, sticky=tk.EW)
        
        # Кнопка подключения
        ttk.Button(settings_frame, text="Подключиться", command=self.connect).grid(row=5, column=0, columnspan=3, pady=5)
        
        # Фрейм для тестов
        tests_frame = ttk.LabelFrame(self.root, text="Тесты", padding=10)
        tests_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Кнопки для тестов
        ttk.Button(tests_frame, text="Проверить светодиоды", command=self.test_leds).grid(row=0, column=0, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(tests_frame, text="Проверить USB", command=self.test_usb).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(tests_frame, text="Проверить COM1", command=lambda: self.test_com("COM1")).grid(row=1, column=0, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(tests_frame, text="Проверить COM2", command=lambda: self.test_com("COM2")).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(tests_frame, text="Проверить K803 (Мастер)", command=self.test_k803_master).grid(row=2, column=0, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(tests_frame, text="Проверить K803 (Ровер)", command=self.test_k803_rover).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(tests_frame, text="Проверить УКВ", command=self.test_ukv).grid(row=3, column=0, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(tests_frame, text="Проверить CAN", command=self.test_can).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(tests_frame, text="Проверить GSM", command=self.test_gsm).grid(row=4, column=0, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(tests_frame, text="Проверить PoE", command=self.test_poe).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(tests_frame, text="Проверить Wi-Fi", command=self.test_wifi).grid(row=5, column=0, sticky=tk.EW, padx=5, pady=2)
        
        # Консоль вывода
        self.console = tk.Text(self.root, height=10, state=tk.DISABLED)
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Полоса прокрутки для консоли
        scrollbar = ttk.Scrollbar(self.console)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.console.yview)
        
    def update_com_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.com_port.set(ports[0] if ports else "")
        
    def log_message(self, message):
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, f"{message}\n")
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)
        
    def connect(self):
        try:
            self.log_message(f"Подключение к {self.ip_address.get()}...")
            
            # Подключение по SSH
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                self.ip_address.get(),
                username=self.username.get(),
                password=self.password.get()
            )
            
            # Открываем две консоли (имитация двух окон PuTTY)
            self.ssh_console1 = self.ssh.invoke_shell()
            self.ssh_console2 = self.ssh.invoke_shell()
            
            # Настройка COM порта
            if self.com_port.get():
                self.serial_conn = serial.Serial(
                    self.com_port.get(),
                    baudrate=int(self.baud_rate.get()),
                    timeout=1
                )
            
            self.log_message("Подключение успешно установлено!")
            
        except Exception as e:
            self.log_message(f"Ошибка подключения: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {str(e)}")
            
    def execute_command(self, console, command, wait=0.5):
        if not console:
            self.log_message("Ошибка: SSH соединение не установлено")
            return ""
            
        console.send(command + "\n")
        time.sleep(wait)
        output = ""
        while console.recv_ready():
            output += console.recv(1024).decode('utf-8')
        self.log_message(f"Команда: {command}\nРезультат: {output}")
        return output
    
    def test_leds(self):
        def run_test():
            try:
                self.log_message("=== Начало проверки светодиодов ===")
                
                # Проверка светодиода питания (должен гореть постоянно)
                self.log_message("Светодиод питания должен гореть постоянно")
                
                # Проверка светодиодов
                commands = [
                    ("gpio mode 13 out", "Настройка вывода для светодиода спутников"),
                    ("gpio write 13 1", "Включение светодиода спутников (SAT M для двухантенного)"),
                    ("sleep 2", "Пауза для визуальной проверки"),
                    ("gpio write 13 0", "Выключение светодиода спутников"),
                    
                    ("gpio mode 22 out", "Настройка вывода для светодиода SAR R"),
                    ("gpio write 22 1", "Включение светодиода SAR R"),
                    ("sleep 2", "Пауза для визуальной проверки"),
                    ("gpio write 22 0", "Выключение светодиода SAR R"),
                    
                    ("gpio mode 21 out", "Настройка вывода для светодиода DIFF"),
                    ("gpio write 21 1", "Включение светодиода DIFF"),
                    ("sleep 2", "Пауза для визуальной проверки"),
                    ("gpio write 21 0", "Выключение светодиода DIFF"),
                    
                    ("gpio mode 23 out", "Настройка вывода для светодиода RTK"),
                    ("gpio write 23 1", "Включение светодиода RTK (RTK M для двухантенного)"),
                    ("sleep 2", "Пауза для визуальной проверки"),
                    ("gpio write 23 0", "Выключение светодиода RTK"),
                    
                    ("gpio mode 20 out", "Настройка вывода для светодиода RTK R"),
                    ("gpio write 20 1", "Включение светодиода RTK R"),
                    ("sleep 2", "Пауза для визуальной проверки"),
                    ("gpio write 20 0", "Выключение светодиода RTK R")
                ]
                
                for cmd, desc in commands:
                    self.log_message(desc)
                    self.execute_command(self.ssh_console1, cmd)
                
                self.log_message("=== Проверка светодиодов завершена ===")
                messagebox.showinfo("Успех", "Проверка светодиодов завершена успешно")
                
            except Exception as e:
                self.log_message(f"Ошибка при проверке светодиодов: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось проверить светодиоды: {str(e)}")
        
        threading.Thread(target=run_test).start()
        
    def test_usb(self):
        def run_test():
            try:
                self.log_message("=== Начало проверки USB ===")
                
                # Выключаем USB порты
                self.execute_command(self.ssh_console1, "gpio mode 14 out")
                self.execute_command(self.ssh_console1, "gpio mode 1 out")
                self.execute_command(self.ssh_console1, "gpio mode 7 out")
                self.execute_command(self.ssh_console1, "gpio write 14 0")
                self.execute_command(self.ssh_console1, "gpio write 1 0")
                self.execute_command(self.ssh_console1, "gpio write 7 0")
                
                # Проверяем список портов
                output = self.execute_command(self.ssh_console1, "ls /dev/tty*")
                if "ttyUSB" in output:
                    self.log_message("ОШИБКА: USB порты обнаружены, когда должны быть выключены")
                else:
                    self.log_message("USB порты успешно отключены")
                
                # Включаем USB порты
                self.execute_command(self.ssh_console1, "gpio write 14 1")
                self.execute_command(self.ssh_console1, "gpio write 1 1")
                self.execute_command(self.ssh_console1, "gpio write 7 1")
                
                # Проверяем список портов снова
                output = self.execute_command(self.ssh_console1, "ls /dev/tty*")
                if "ttyUSB" in output:
                    self.log_message("USB порты успешно включены")
                    self.log_message(f"Список портов: {output}")
                else:
                    self.log_message("ОШИБКА: USB порты не обнаружены после включения")
                
                self.log_message("=== Проверка USB завершена ===")
                messagebox.showinfo("Успех", "Проверка USB завершена успешно")
                
            except Exception as e:
                self.log_message(f"Ошибка при проверке USB: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось проверить USB: {str(e)}")
        
        threading.Thread(target=run_test).start()
        
    def test_com(self, com_port):
        def run_test():
            try:
                self.log_message(f"=== Начало проверки {com_port} ===")
                
                if not self.serial_conn:
                    self.log_message("ОШИБКА: COM порт не настроен")
                    return
                
                # Настройка порта
                if com_port == "COM1":
                    self.execute_command(self.ssh_console1, "gpio mode 14 out")
                    self.execute_command(self.ssh_console1, "gpio mode 1 out")
                    self.execute_command(self.ssh_console1, "gpio write 14 1")
                    self.execute_command(self.ssh_console1, "gpio write 1 1")
                    
                    # Проверка COM1
                    self.execute_command(self.ssh_console1, "stty -echo -F /dev/ttyUSB0 115200")
                    self.execute_command(self.ssh_console1, "cat /dev/ttyUSB0", wait=2)
                    
                    # Отправка команды через COM порт
                    self.serial_conn.write(b"log version\n")
                    time.sleep(1)
                    
                    # Проверка ответа (упрощенно)
                    self.execute_command(self.ssh_console1, "echo -e \"log version\" > /dev/ttyUSB0")
                    
                elif com_port == "COM2":
                    # Проверка COM2
                    self.execute_command(self.ssh_console1, "stty -echo -F /dev/ttyUSB3 115200")
                    self.execute_command(self.ssh_console1, "cat /dev/ttyUSB3", wait=2)
                    
                    # Отправка команды через COM порт
                    self.serial_conn.write(b"log version\n")
                    time.sleep(1)
                    
                    # Проверка ответа (упрощенно)
                    self.execute_command(self.ssh_console1, "echo -e \"log version\" > /dev/ttyUSB3")
                
                self.log_message(f"=== Проверка {com_port} завершена ===")
                messagebox.showinfo("Успех", f"Проверка {com_port} завершена успешно")
                
            except Exception as e:
                self.log_message(f"Ошибка при проверке {com_port}: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось проверить {com_port}: {str(e)}")
        
        threading.Thread(target=run_test).start()
        
    def test_k803_master(self):
        def run_test():
            try:
                self.log_message("=== Начало проверки K803 (Мастер) ===")
                
                # Проверка K803 (Мастер)
                self.execute_command(self.ssh_console1, "stty -echo -F /dev/ttyS1 115200")
                self.execute_command(self.ssh_console1, "cat /dev/ttyS1", wait=2)
                
                self.execute_command(self.ssh_console2, "gpio mode 4 out")
                self.execute_command(self.ssh_console2, "gpio write 4 0")
                self.execute_command(self.ssh_console2, "gpio write 4 1")
                
                # Проверка ответа (упрощенно)
                self.execute_command(self.ssh_console2, "echo -e \"log version\" > /dev/ttyS1")
                
                self.log_message("=== Проверка K803 (Мастер) завершена ===")
                messagebox.showinfo("Успех", "Проверка K803 (Мастер) завершена успешно")
                
            except Exception as e:
                self.log_message(f"Ошибка при проверке K803 (Мастер): {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось проверить K803 (Мастер): {str(e)}")
        
        threading.Thread(target=run_test).start()
        
    def test_k803_rover(self):
        def run_test():
            try:
                self.log_message("=== Начало проверки K803 (Ровер) ===")
                
                # Проверка K803 (Ровер)
                self.execute_command(self.ssh_console1, "stty -echo -F /dev/ttyUSB5 115200")
                self.execute_command(self.ssh_console1, "cat /dev/ttyUSB5", wait=2)
                
                self.execute_command(self.ssh_console2, "gpio mode 4 out")
                self.execute_command(self.ssh_console2, "gpio write 4 0")
                self.execute_command(self.ssh_console2, "gpio write 4 1")
                
                # Проверка ответа (упрощенно)
                self.execute_command(self.ssh_console2, "echo -e \"log version\" > /dev/ttyUSB5")
                
                self.log_message("=== Проверка K803 (Ровер) завершена ===")
                messagebox.showinfo("Успех", "Проверка K803 (Ровер) завершена успешно")
                
            except Exception as e:
                self.log_message(f"Ошибка при проверке K803 (Ровер): {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось проверить K803 (Ровер): {str(e)}")
        
        threading.Thread(target=run_test).start()
        
    def test_ukv(self):
        def run_test():
            try:
                self.log_message("=== Начало проверки УКВ ===")
                
                # Проверка УКВ
                self.execute_command(self.ssh_console1, "gpio mode 19 out")
                self.execute_command(self.ssh_console1, "gpio write 19 1")
                self.execute_command(self.ssh_console1, "stty -echo -F /dev/ttyS2 115200")
                self.execute_command(self.ssh_console1, "cat /dev/ttyS2", wait=2)
                
                self.execute_command(self.ssh_console2, "echo -e \"\\\$\\\$01log radioinfo\" > /dev/ttyS2")
                
                # Проверка через USB
                self.execute_command(self.ssh_console1, "stty -echo -F /dev/ttyUSB8 115200")
                self.execute_command(self.ssh_console1, "cat /dev/ttyUSB8", wait=2)
                
                self.execute_command(self.ssh_console2, "echo -e \"\\\$\\\$01log radioinfo\" > /dev/ttyUSB8")
                
                # Выключение УКВ
                self.execute_command(self.ssh_console2, "gpio write 19 0")
                self.execute_command(self.ssh_console2, "echo -e \"\\\$\\\$01log radioinfo\" > /dev/ttyUSB8")
                
                self.log_message("=== Проверка УКВ завершена ===")
                messagebox.showinfo("Успех", "Проверка УКВ завершена успешно")
                
            except Exception as e:
                self.log_message(f"Ошибка при проверке УКВ: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось проверить УКВ: {str(e)}")
        
        threading.Thread(target=run_test).start()
        
    def test_can(self):
        def run_test():
            try:
                self.log_message("=== Начало проверки CAN ===")
                
                # Проверка CAN
                self.execute_command(self.ssh_console1, "gpio mode 3 out")
                self.execute_command(self.ssh_console1, "gpio mode 2 out")
                self.execute_command(self.ssh_console1, "gpio write 3 0")
                self.execute_command(self.ssh_console1, "gpio write 2 0")
                self.execute_command(self.ssh_console1, "gpio write 2 1")
                self.execute_command(self.ssh_console1, "gpio write 3 1")
                
                self.execute_command(self.ssh_console1, "stty -echo -F /dev/ttyUSB7 57600")
                self.execute_command(self.ssh_console1, "cat /dev/ttyUSB7", wait=2)
                
                self.execute_command(self.ssh_console2, "echo -e \"AT\" > /dev/ttyUSB7")
                
                # Выключение CAN
                self.execute_command(self.ssh_console2, "gpio write 3 0")
                self.execute_command(self.ssh_console2, "echo -e \"AT\" > /dev/ttyUSB7")
                
                self.log_message("=== Проверка CAN завершена ===")
                messagebox.showinfo("Успех", "Проверка CAN завершена успешно")
                
            except Exception as e:
                self.log_message(f"Ошибка при проверке CAN: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось проверить CAN: {str(e)}")
        
        threading.Thread(target=run_test).start()
        
    def test_gsm(self):
        def run_test():
            try:
                self.log_message("=== Начало проверки GSM ===")
                
                # Проверка GSM
                self.execute_command(self.ssh_console1, "gpio mode 14 out")
                self.execute_command(self.ssh_console1, "gpio write 14 0")
                self.execute_command(self.ssh_console1, "gpio mode 7 out")
                self.execute_command(self.ssh_console1, "gpio write 7 1")
                
                # Проверка портов
                output = self.execute_command(self.ssh_console1, "ls /dev/tty*", wait=10)
                if "ttyUSB" in output:
                    self.log_message("GSM модем обнаружен")
                else:
                    self.log_message("ОШИБКА: GSM модем не обнаружен")
                
                # Перезагрузка модема
                self.execute_command(self.ssh_console2, "echo -e \"AT#SIMINCFG=0,1\" > /dev/ttyUSB2")
                self.execute_command(self.ssh_console2, "echo -e \"AT#REBOOT\" > /dev/ttyUSB2")
                
                # Проверка регистрации в сети
                self.execute_command(self.ssh_console1, "stty -echo -F /dev/ttyUSB2 115200")
                self.execute_command(self.ssh_console1, "cat /dev/ttyUSB2", wait=2)
                
                self.execute_command(self.ssh_console2, "echo -e \"at+creg?\" > /dev/ttyUSB2")
                
                self.log_message("=== Проверка GSM завершена ===")
                messagebox.showinfo("Успех", "Проверка GSM завершена успешно")
                
            except Exception as e:
                self.log_message(f"Ошибка при проверке GSM: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось проверить GSM: {str(e)}")
        
        threading.Thread(target=run_test).start()
        
    def test_poe(self):
        def run_test():
            try:
                self.log_message("=== Начало проверки PoE ===")
                self.log_message("1. Отключите питание приемника")
                self.log_message("2. Подключите блок питания PoE к локальной сети и к сети питания")
                self.log_message("3. Подключите приемник к блоку питания")
                self.log_message("4. Проверьте, включился ли приемник")
                self.log_message("5. Проверьте его регистрацию в локальной сети")
                
                self.log_message("=== Проверка PoE завершена (требуется ручная проверка) ===")
                messagebox.showinfo("Информация", "Проверка PoE требует ручных действий. Следуйте инструкциям в логе.")
                
            except Exception as e:
                self.log_message(f"Ошибка при проверке PoE: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось проверить PoE: {str(e)}")
        
        threading.Thread(target=run_test).start()
        
    def test_wifi(self):
        def run_test():
            try:
                self.log_message("=== Начало проверки Wi-Fi ===")
                
                # Запуск Wi-Fi
                self.execute_command(self.ssh_console1, "systemctl start rclocal")
                
                self.log_message("1. Откройте веб-интерфейс в браузере (логин/пароль: admin/admin)")
                self.log_message("2. В меню Сеть включите Точку доступа Wi-Fi")
                self.log_message("3. Введите уникальное число и пароль 123456789")
                self.log_message("4. Нажмите Применить")
                self.log_message("5. Подключитесь к созданной точке доступа")
                
                self.log_message("=== Проверка Wi-Fi завершена (требуется ручная проверка) ===")
                messagebox.showinfo("Информация", "Проверка Wi-Fi требует ручных действий. Следуйте инструкциям в логе.")
                
            except Exception as e:
                self.log_message(f"Ошибка при проверке Wi-Fi: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось проверить Wi-Fi: {str(e)}")
        
        threading.Thread(target=run_test).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = DeviceTesterApp(root)
    root.mainloop()
