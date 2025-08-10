import os
import winreg
from tkinter import *
from tkinter import ttk, messagebox

class StartupManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер автозагрузки")
        self.root.geometry("800x600")
        
        # Создаем основную рамку
        self.mainframe = ttk.Frame(root, padding="10")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        
        # Создаем дерево для отображения элементов автозагрузки
        self.tree = ttk.Treeview(self.mainframe, columns=('Name', 'Path', 'Location'), show='headings')
        self.tree.heading('Name', text='Имя программы')
        self.tree.heading('Path', text='Путь')
        self.tree.heading('Location', text='Расположение')
        self.tree.column('Name', width=200)
        self.tree.column('Path', width=400)
        self.tree.column('Location', width=150)
        self.tree.grid(column=0, row=0, columnspan=2, sticky=(N, W, E, S))
        
        # Кнопка удаления
        self.delete_button = ttk.Button(self.mainframe, text="Удалить выбранное", command=self.delete_selected)
        self.delete_button.grid(column=0, row=1, pady=10, sticky=W)
        
        # Кнопка обновления
        self.refresh_button = ttk.Button(self.mainframe, text="Обновить список", command=self.load_startup_items)
        self.refresh_button.grid(column=1, row=1, pady=10, sticky=E)
        
        # Загружаем элементы автозагрузки
        self.load_startup_items()
        
        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
    
    def load_startup_items(self):
        # Очищаем дерево
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Загружаем элементы из реестра
        self.load_registry_startup_items()
        
        # Загружаем элементы из папки автозагрузки
        self.load_folder_startup_items()
    
    def load_registry_startup_items(self):
        # Ключи реестра для автозагрузки
        registry_locations = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce")
        ]
        
        for hive, subkey in registry_locations:
            try:
                with winreg.OpenKey(hive, subkey) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            location = "Реестр: " + ("HKCU" if hive == winreg.HKEY_CURRENT_USER else "HKLM") + "\\" + subkey
                            self.tree.insert('', 'end', values=(name, value, location))
                            i += 1
                        except OSError:
                            break
            except WindowsError:
                continue
    
    def load_folder_startup_items(self):
        # Папки автозагрузки
        folders = [
            os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'),
            os.path.join(os.getenv('PROGRAMDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        ]
        
        for folder in folders:
            if os.path.exists(folder):
                for item in os.listdir(folder):
                    full_path = os.path.join(folder, item)
                    location = "Папка: " + folder
                    self.tree.insert('', 'end', values=(item, full_path, location))
    
    def delete_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите элемент для удаления")
            return
        
        item_data = self.tree.item(selected_item)
        name, path, location = item_data['values']
        
        if "Реестр:" in location:
            # Удаляем из реестра
            if messagebox.askyesno("Подтверждение", f"Удалить '{name}' из автозагрузки?\n\nПуть: {path}"):
                try:
                    hive_part = location.split(":")[1].strip().split("\\")[0].strip()
                    subkey = "\\".join(location.split(":")[1].strip().split("\\")[1:])
                    
                    hive = winreg.HKEY_CURRENT_USER if hive_part == "HKCU" else winreg.HKEY_LOCAL_MACHINE
                    
                    with winreg.OpenKey(hive, subkey, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.DeleteValue(key, name)
                    
                    self.tree.delete(selected_item)
                    messagebox.showinfo("Успех", "Элемент успешно удален из реестра")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить из реестра: {e}")
        else:
            # Удаляем файл из папки автозагрузки
            if messagebox.askyesno("Подтверждение", f"Удалить файл '{name}'?\n\nПуть: {path}"):
                try:
                    os.remove(path)
                    self.tree.delete(selected_item)
                    messagebox.showinfo("Успех", "Файл успешно удален")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить файл: {e}")

if __name__ == "__main__":
    root = Tk()
    app = StartupManager(root)
    root.mainloop()