import tkinter as tk
from tkinter import messagebox
import winreg
import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def block_task_manager(block=True):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                           0, winreg.KEY_SET_VALUE)
        
        if block:
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            messagebox.showinfo("Успех", "Диспетчер задач заблокирован!")
        else:
            try:
                winreg.DeleteValue(key, "DisableTaskMgr")
                messagebox.showinfo("Успех", "Диспетчер задач разблокирован!")
            except FileNotFoundError:
                messagebox.showinfo("Инфо", "Диспетчер задач уже разблокирован")
        
        winreg.CloseKey(key)
        return True
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось изменить параметры реестра: {e}")
        return False

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Блокировщик Диспетчера задач")
        self.root.geometry("400x200")
        
        if not is_admin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
        
        self.create_widgets()
    
    def create_widgets(self):
        tk.Label(self.root, text="Управление Диспетчером задач", 
                font=("Arial", 14)).pack(pady=20)
        
        self.block_btn = tk.Button(self.root, text="Заблокировать Диспетчер задач", 
                                 command=lambda: self.toggle_task_manager(True),
                                 bg="red", fg="white")
        self.block_btn.pack(pady=10)
        
        self.unblock_btn = tk.Button(self.root, text="Разблокировать Диспетчер задач", 
                                   command=lambda: self.toggle_task_manager(False),
                                   bg="green", fg="white")
        self.unblock_btn.pack(pady=10)
        
        tk.Label(self.root, text="Требуются права администратора", 
                fg="gray").pack(pady=10)
    
    def toggle_task_manager(self, block):
        if block:
            if messagebox.askyesno("Подтверждение", 
                                 "Вы уверены, что хотите заблокировать Диспетчер задач?"):
                block_task_manager(True)
        else:
            if messagebox.askyesno("Подтверждение",
                                 "Вы уверены, что хотите разблокировать Диспетчер задач?"):
                block_task_manager(False)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()