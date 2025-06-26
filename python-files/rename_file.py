import os
import tkinter as tk
from tkinter import filedialog, messagebox

class FileRenamer:
    def __init__(self):
        # Инициализация словаря
        self.crimea_ecor_current_account = {
                    "40602810100030020018":"40602810640130000024",
                    "40602810200030030018":"40602810940130000038",
                    "40602810300030040018":"40602810540130000030",
                    "40602810400030050018":"40602810940130000025",
                    "40602810500030060018":"40602810540130000027",
                    "40602810600030070018":"40602810040130000022",
                    "40602810700030080018":"40602810340130000036",
                    "40602810800030090018":"40602810840130000031",
                    "40602810800030100018":"40602810240130000026",
                    "40602810900030110018":"40602810240130000026",
                    "40602810900030110018":"40602810240130000026",
                    "40602810000030120018":"40602810640130000037",
                    "40602810100030130018":"40602810140130000032",
                    "40602810200030140018":"40602810640130000040",
                    "40602810300030150018":"40602810040130000019",
                    "40602810400030160018":"40602810340130000023",
                    "40602810500030170018":"40602810440130000020",
                    "40602810600030180018":"40602810240130000039",
                    "40602810700030190018":"40602810940130000041",
                    "40602810700030200018":"40602810440130000033",
                    "40602810800030210018":"40602810740130000034",
                    "40602810900030220018":"40602810040130000035",
                    "40602810000030230018":"40602810740130000021",
                    "40602810100030240018":"40602810840130000028",
        }
        # Здесь добавьте нужные значения в словарь
        self.renamed_count = 0  # Счетчик успешно переименованных файлов

    def get_account_name(self, key):
        # Удаляем расширение файла, если оно есть
        clean_key = key.split('.')[0]
        
        # Проверяем наличие ключа в словаре
        return self.crimea_ecor_current_account.get(clean_key, clean_key)

    def rename_files(self, files):
        self.renamed_count = 0  # Сбрасываем счетчик
        total_files = len(files)
        
        for file_path in files:
            try:
                # Проверяем существование исходного файла
                if not os.path.exists(file_path):
                    messagebox.showerror(
                        "Ошибка",
                        f"Файл не найден: {file_path}"
                    )
                    continue

                # Получаем директорию и имя файла
                directory = os.path.dirname(file_path)
                filename = os.path.splitext(os.path.basename(file_path))[0]

                # Разбиваем имя файла на части
                parts = filename.split('_')
                
                # Проверяем корректность формата имени файла
                if len(parts) < 5:
                    messagebox.showerror(
                        "Ошибка",
                        f"Неверный формат имени файла: {file_path}"
                    )
                    continue

                # Формируем новое имя файла изменить на Т БАНК
                new_filename = f"{"043510607"}_{parts[1]}_{parts[2]}_{parts[3]}_{parts[4]}.txt"
                #new_filename = f"{parts[0]}_{parts[1]}_{parts[2]}_{self.get_account_name(parts[3])}.txt"
                new_file_path = os.path.join(directory, new_filename).strip()

                # Проверяем, не существует ли файл с таким именем
                if os.path.exists(new_file_path):
                    messagebox.showwarning(
                        "Предупреждение",
                        f"Файл уже существует: {new_file_path}"
                    )
                    continue

                # Выполняем переименование
                os.rename(file_path, new_file_path)
                self.renamed_count += 1

            except PermissionError as e:
                messagebox.showerror(
                    "Ошибка",
                    f"Отказано в доступе: {str(e)}"
                )
            except OSError as e:
                messagebox.showerror(
                    "Ошибка",
                    f"Ошибка операционной системы: {str(e)}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Ошибка",
                    f"Непредвиденная ошибка: {str(e)}"
                )

        # Показываем сообщение об успешном завершении
        if self.renamed_count > 0:
            messagebox.showinfo(
                "Успешно",
                f"Переименовано файлов: {self.renamed_count} из {total_files}"
            )
        else:
            messagebox.showinfo(
                "Информация",
                "Файлы не были переименованы"
            )

    

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Переименование файлов Почта Крыма")
        self.geometry("400x75")
        
        self.renamer = FileRenamer()
        
        # Создаем и размещаем кнопку
        btn = tk.Button(
            self,
            text="Выбрать файлы (Почта Крыма)",
            command=self.select_files
        )
        btn.pack(expand=True)

    def select_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*")
            ]
        )
        if files:
            self.renamer.rename_files(files)


if __name__ == "__main__":
    app = Application()
    app.mainloop()