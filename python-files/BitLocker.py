import ctypes
import subprocess
import sys
from tkinter import *
from tkinter import ttk, messagebox

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class BitLockerManager:
    def __init__(self, root):
        self.root = root
        self.root.title("BitLocker Manager")
        self.root.geometry("500x300")
        
        if not is_admin():
            messagebox.showwarning("Ошибка", "Программа требует прав администратора!")
            self.root.destroy()
            return
        
        # Проверка доступности BitLocker
        if not self.check_bitlocker_available():
            messagebox.showerror("Ошибка", "BitLocker не поддерживается в этой системе или отключён")
            self.root.destroy()
            return
        
        self.create_widgets()
        self.list_volumes()
    
    def check_bitlocker_available(self):
        """Проверяет доступность BitLocker в системе"""
        try:
            subprocess.run(['manage-bde'], check=True, 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=BOTH, expand=True)
        
        # Список томов
        ttk.Label(main_frame, text="Выберите том:").pack()
        self.volume_list = ttk.Treeview(main_frame, columns=('status'), show='headings')
        self.volume_list.heading('#0', text='Том')
        self.volume_list.heading('status', text='Статус BitLocker')
        self.volume_list.column('#0', width=200)
        self.volume_list.column('status', width=200)
        self.volume_list.pack(fill=BOTH, expand=True)
        
        # Кнопки управления
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=X, pady=10)
        
        ttk.Button(btn_frame, text="Отключить BitLocker", command=self.disable_bitlocker).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Полностью расшифровать", command=self.decrypt_volume).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить список", command=self.list_volumes).pack(side=LEFT, padx=5)
    
    def run_command(self, cmd):
        """Универсальный метод для выполнения команд с обработкой кодировок"""
        try:
            return subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='cp866')
        except UnicodeDecodeError:
            try:
                return subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='cp1251')
            except UnicodeDecodeError:
                return subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
    
    def list_volumes(self):
        """Получает список томов и их статус BitLocker"""
        self.volume_list.delete(*self.volume_list.get_children())
        
        try:
            result = self.run_command(['manage-bde', '-status'])
            volumes = []
            current_volume = ""
            
            for line in result.stdout.split('\n'):
                # Поддержка русского и английского языков
                if 'Том' in line or 'Volume' in line:
                    current_volume = line.split(':')[1].strip()
                elif 'Шифрование BitLocker' in line or 'BitLocker Encryption' in line:
                    status = line.split(':')[1].strip()
                    volumes.append((current_volume, status))
            
            if not volumes:
                messagebox.showinfo("Информация", "Не найдено томов с BitLocker")
                return
            
            for vol, status in volumes:
                self.volume_list.insert('', 'end', text=vol, values=(status))
        
        except subprocess.CalledProcessError as e:
            error_msg = f"Не удалось получить список томов.\n\nКоманда: {' '.join(e.cmd)}\nОшибка: {e.stderr}"
            messagebox.showerror("Ошибка", error_msg)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неожиданная ошибка: {str(e)}")
    
    def disable_bitlocker(self):
        """Временно отключает BitLocker (шифрование остаётся)"""
        selected = self.volume_list.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите том!")
            return
        
        volume = self.volume_list.item(selected[0], 'text')
        
        if not messagebox.askyesno(
            "Подтверждение", 
            f"Вы уверены, что хотите отключить BitLocker для тома {volume}?\n\n"
            "Данные останутся зашифрованными, но не будут требовать пароль при загрузке."
        ):
            return
        
        try:
            result = self.run_command(['manage-bde', '-off', volume])
            messagebox.showinfo("Успех", f"BitLocker отключен для тома {volume}")
            self.list_volumes()
        except subprocess.CalledProcessError as e:
            error_msg = f"Не удалось отключить BitLocker.\n\nКоманда: {' '.join(e.cmd)}\nОшибка: {e.stderr}"
            messagebox.showerror("Ошибка", error_msg)
    
    def decrypt_volume(self):
        """Полностью расшифровывает том"""
        selected = self.volume_list.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите том!")
            return
        
        volume = self.volume_list.item(selected[0], 'text')
        
        if not messagebox.askyesno(
            "Подтверждение", 
            f"Вы уверены, что хотите полностью расшифровать том {volume}?\n\n"
            "Это может занять много времени в зависимости от размера диска."
        ):
            return
        
        try:
            result = self.run_command(['manage-bde', '-off', volume, '-decrypt'])
            messagebox.showinfo("Успех", f"Начат процесс расшифровки тома {volume}")
            self.list_volumes()
        except subprocess.CalledProcessError as e:
            error_msg = f"Не удалось начать расшифровку.\n\nКоманда: {' '.join(e.cmd)}\nОшибка: {e.stderr}"
            messagebox.showerror("Ошибка", error_msg)

if __name__ == "__main__":
    if not is_admin():
        # Попытка перезапуска с правами администратора
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    
    root = Tk()
    app = BitLockerManager(root)
    root.mainloop()