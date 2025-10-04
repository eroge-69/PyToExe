import webbrowser
import os
import shutil
#import pywin32
def copy_file_to_all_folders(source_file_path, root_directory):
    """
    Копирует файл во все подпапки указанной корневой директории.

    :param source_file_path: Путь к исходному файлу, который нужно скопировать.
    :param root_directory: Корневая директория, в подпапках которой нужно разместить файл.
    """
    # Проверяем, существует ли исходный файл
    if not os.path.isfile(source_file_path):
        print(f"Ошибка: Исходный файл '{source_file_path}' не найден.")
        return

    # Используем os.walk для рекурсивного обхода всех папок
    for current_dir, subdirs, files in os.walk(root_directory):
        # Формируем полный путь для копии файла в текущей папке
        destination_path = os.path.join(current_dir, os.path.basename(source_file_path))

        try:
            # Копируем файл с сохранением метаданных
            shutil.copy2(source_file_path, destination_path)
            print(f"Файл скопирован в: {destination_path}")
        except Exception as e:
            print(f"Не удалось скопировать в {destination_path}: {e}")


# Пример использования
source_file = "C:\С++ and python projects\Python_P/xsmlWEB/smalexe.exe"  # Замените на путь к вашему EXE-файлу
target_directory = "C:\С++ and python projects/addd"  # Замените на целевую директорию

#copy_file_to_all_folders(source_file, target_directory)
op='Xasmol'
qst1 = input('Открыть сайт?(Y or N): ')
if qst1 == 'Y': webbrowser.open('https://sxml.tilda.ws/projectssxml', new=2)
else:
    qst2 = input('Enter name: ')
    if qst2 == op:
        print('Welcome back!')
        while True:
            gd = input('command: ')
            if gd == 'help':
                print('commands:\n1.start web\n2.change op\n3.quit')
            elif gd == 'start web':
                source_file = input("Exe file path: ")
                target_directory = input('Target directory:')
                copy_file_to_all_folders(source_file, target_directory)
    else:
        print('Wrong')