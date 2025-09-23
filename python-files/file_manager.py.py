import os

def list_files(directory):
    #Выводит список файлов в указанной директории.
    try:
        files = os.listdir(directory)
        print("Список файлов и папок в директории:", directory)
        for file in files:
            print(file)
    except FileNotFoundError:
        print("Директория не найдена.")
    except PermissionError:
        print("Нет доступа к директории.")

def open_file(file_path):
    #Открывает файл и выводит его содержимое.
    try:
        with open(file_path, 'r') as file:
            print(file.read())
    except FileNotFoundError:
        print("Файл не найден.")
    except IsADirectoryError:
        print("Указанный путь является директорией, а не файлом.")
    except Exception as e:
        print(f"Ошибка при открытии файла: {e}")

def delete_file(file_path):
    #Удаляет указанный файл.
    try:
        os.remove(file_path)
        print(f"Файл {file_path} успешно удален.")
    except FileNotFoundError:
        print("Файл не найден.")
    except PermissionError:
        print("Нет доступа для удаления файла.")
    except Exception as e:
        print(f"Ошибка при удалении файла: {e}")

def main():
    while True:
        print("\nДиспетчер файлов")
        print("1. Просмотреть файлы")
        print("2. Открыть файл")
        print("3. Удалить файл")
        print("4. Выход")
        
        choice = input("Выберите действие (1-4): ")
        
        if choice == '1':
            directory = input("Введите путь к директории: ")
            list_files(directory)
        elif choice == '2':
            file_path = input("Введите путь к файлу: ")
            open_file(file_path)
        elif choice == '3':
            file_path = input("Введите путь к файлу для удаления: ")
            delete_file(file_path)
        elif choice == '4':
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор. Пожалуйста, попробуйте снова.")

main()