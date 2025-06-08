import os
import sys
import time
import serial
import serial.tools.list_ports
import shutil
from tkinter import *
from tkinter import messagebox
import threading

# Проверка версии Python
if sys.version_info < (3, 6):
    input("Требуется Python 3.6 или новее. Нажмите Enter для выхода...")
    sys.exit(1)

# Настройки программы
PLAYER_LIMIT = 10
BANK_NAME = "БАНК"

class PlayerSystem:
    def __init__(self):
        self.players = []
        self.bank_registered = False
        self.serial_conn = None
        self.serial_thread = None
        self.serial_running = False
        
        # Удаляем и создаем заново папку для данных
        self.data_dir = os.path.join(os.path.dirname(__file__), "BD")
        self.clean_data_directory()
        
        # Автопоиск COM-порта
        self.com_port = self.find_arduino_port()
        if not self.com_port:
            messagebox.showerror("Ошибка", "Arduino не найдена! Проверьте подключение.")
            sys.exit(1)
        
        self.setup_gui()
        self.create_bank_player()
    
    def clean_data_directory(self):
        """Очищает папку с данными"""
        try:
            if os.path.exists(self.data_dir):
                shutil.rmtree(self.data_dir)
            os.makedirs(self.data_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось очистить папку данных: {str(e)}")
            sys.exit(1)
    
    def find_arduino_port(self):
        """Автоматически находит порт Arduino"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Arduino" in port.description or "CH340" in port.description:
                return port.device
        return ports[0].device if ports else None
    
    def setup_gui(self):
        """Создает графический интерфейс"""
        self.root = Tk()
        self.root.title("Игровая система")
        self.root.geometry("350x250")
        
        Label(self.root, text="Управление игроками", font=("Arial", 12, "bold")).place(x=20, y=20)
        
        self.lbl_player_count = Label(self.root, text=f"Добавлено игроков: 0\nПорт: {self.com_port}")
        self.lbl_player_count.place(x=20, y=60)
        
        Button(self.root, text="Добавить игрока", command=self.add_player_window, 
              font=("Arial", 10, "bold")).place(x=20, y=100, width=310, height=40)
        
        self.btn_start = Button(self.root, text="Начать игру", state=DISABLED,
                              font=("Arial", 10, "bold"), command=self.start_game)
        self.btn_start.place(x=20, y=150, width=310, height=40)
        
        Button(self.root, text="Выход", command=self.root.quit).place(x=20, y=200, width=310, height=30)
    
    def create_bank_player(self):
        """Добавляет системного игрока БАНК"""
        if not any(p[0] == BANK_NAME for p in self.players):
            if len(self.players) < PLAYER_LIMIT:
                self.players.append([BANK_NAME, ""])
                self.update_display()
    
    def update_display(self):
        """Обновляет интерфейс"""
        self.lbl_player_count.config(text=f"Добавлено игроков: {len(self.players)}\nПорт: {self.com_port}")
        self.btn_start.config(state=NORMAL if (len(self.players) > 1 and self.bank_registered) else DISABLED)
    
    def add_player_window(self):
        """Окно добавления нового игрока"""
        if len(self.players) >= PLAYER_LIMIT:
            messagebox.showwarning("Ошибка", "Достигнут лимит игроков!")
            return
            
        window = Toplevel(self.root)
        window.title("Добавить игрока")
        window.geometry("350x250")
        window.grab_set()  # Делаем окно модальным
        
        # Определяем, регистрируем ли мы БАНК
        is_bank = not self.bank_registered and self.players[0][0] == BANK_NAME and not self.players[0][1]
        
        Label(window, text="Регистрация БАНКа" if is_bank else "Добавить игрока", 
             font=("Arial", 12, "bold")).place(x=20, y=10)
        
        Label(window, text="Имя игрока:").place(x=20, y=50)
        name_entry = Entry(window)
        name_entry.place(x=20, y=70, width=310, height=25)
        
        if is_bank:
            name_entry.insert(0, BANK_NAME)
            name_entry.config(state=DISABLED)
        
        Label(window, text="Статус RFID:").place(x=20, y=110)
        self.rfid_label = Label(window, text="Приложите карту к считывателю...")
        self.rfid_label.place(x=20, y=130)
        
        btn_save = Button(window, text="Сохранить", state=DISABLED if not is_bank else NORMAL)
        btn_save.place(x=20, y=170, width=310, height=30)
        
        # Переменные для RFID
        self.rfid_data = ""
        self.card_read = False
        self.serial_error = False
        
        def check_inputs():
            """Проверяет условия для активации кнопки Сохранить"""
            name = name_entry.get().strip()
            if is_bank:
                btn_save.config(state=NORMAL)
            else:
                btn_save.config(state=NORMAL if (name and self.card_read) else DISABLED)
        
        def on_name_change(*args):
            """Обработчик изменения имени"""
            check_inputs()
        
        # Отслеживаем изменения в поле имени
        name_var = StringVar()
        name_var.trace("w", on_name_change)
        name_entry.config(textvariable=name_var)
        
        def read_serial():
            """Чтение данных с COM-порта"""
            try:
                self.serial_conn = serial.Serial(self.com_port, 9600, timeout=1)
                while self.serial_running and not self.serial_error:
                    if self.serial_conn.in_waiting:
                        line = self.serial_conn.readline().decode('utf-8').strip()
                        if line.startswith("RFID:"):
                            self.rfid_data = line[5:]
                            self.rfid_label.config(text=f"Считана карта: {self.rfid_data}")
                            self.card_read = True
                            window.after(0, check_inputs)
            except Exception as e:
                self.serial_error = True
                if self.serial_running:  # Только если окно еще не закрыто
                    window.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка чтения порта: {str(e)}"))
                    window.after(0, window.destroy)
            finally:
                if hasattr(self, 'serial_conn') and self.serial_conn:
                    self.serial_conn.close()
        
        def save_player():
            """Сохранение игрока"""
            name = name_entry.get().strip()
            if not name and not is_bank:
                messagebox.showwarning("Ошибка", "Введите имя игрока!")
                window.focus_force()
                return
                
            if not self.card_read and not is_bank:
                messagebox.showwarning("Ошибка", "Не считана RFID-карта!")
                window.focus_force()
                return
                
            # Проверка уникальности
            if name != BANK_NAME and any(p[0] == name for p in self.players):
                messagebox.showwarning("Ошибка", "Игрок с таким именем уже есть!")
                window.focus_force()
                return
                
            if any(p[1] == self.rfid_data for p in self.players if p[1]):
                messagebox.showwarning("Ошибка", "Эта карта уже зарегистрирована!")
                window.focus_force()
                return
                
            # Обновляем данные
            if is_bank:
                self.players[0][1] = self.rfid_data
                self.bank_registered = True
                messagebox.showinfo("Успех", "Карта БАНКа зарегистрирована!")
            else:
                self.players.append([name, self.rfid_data])
                
            self.update_display()
            close_window()
        
        def close_window():
            """Корректное закрытие окна"""
            self.serial_running = False
            if hasattr(self, 'serial_conn') and self.serial_conn:
                self.serial_conn.close()
            window.destroy()
        
        btn_save.config(command=save_player)
        
        # Запускаем чтение порта в отдельном потоке
        self.serial_running = True
        self.serial_thread = threading.Thread(target=read_serial, daemon=True)
        self.serial_thread.start()
        
        # Обработчик закрытия окна
        window.protocol("WM_DELETE_WINDOW", close_window)
    
    def start_game(self):
        """Сохранение данных и запуск игры"""
        try:
            # Сохраняем данные в файлы
            with open(os.path.join(self.data_dir, "players.txt"), "w", encoding='utf-8') as f:
                f.write("\n".join(p[0] for p in self.players))
                
            with open(os.path.join(self.data_dir, "card.txt"), "w", encoding='utf-8') as f:
                f.write("\n".join(p[1] for p in self.players))
                
            with open(os.path.join(self.data_dir, "money.txt"), "w", encoding='utf-8') as f:
                f.write("\n".join(str(25000 if p[0] == BANK_NAME else 1500) for p in self.players))
            
            messagebox.showinfo("Успех", "Данные сохранены!\nЗапускаем игру...")
            self.root.quit()
            # os.system("start game.exe")  # Раскомментируйте для запуска игры
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")

if __name__ == "__main__":
    try:
        app = PlayerSystem()
        app.root.mainloop()
    except Exception as e:
        messagebox.showerror("Критическая ошибка", f"Программа завершена с ошибкой:\n{str(e)}")
        sys.exit(1)