import os
import subprocess
import sys

def simple_menu():
    while True:
        print("\n" + "="*40)
        print("1. Открыть файлы из C:/Nerest")
        print("2. Открыть NerestPc.exe")
        print("3. Выход")
        print("="*40)
        
        choice = input("Выберите цифру: ").strip()
        
        if choice == "1":
            if os.path.exists("C:/Nerest"):
                files = os.listdir("C:/Nerest")
                if files:
                    print("\nФайлы в папке:")
                    for i, file in enumerate(files, 1):
                        print(f"{i}. {file}")
                    file_choice = input("Выберите файл: ")
                    if file_choice.isdigit() and 1 <= int(file_choice) <= len(files):
                        file_path = f"C:/Nerest/{files[int(file_choice)-1]}"
                        os.system(f'start "" "{file_path}"')
                else:
                    print("Папка пуста!")
            else:
                print("Папка C:/Nerest не найдена! переместите скачанную папку Nerest на C диск")
                
        elif choice == "2":
            exe_path = "C:/Nerest/Nerest.exe"
            if os.path.exists(exe_path):
                print("Запуск Nerest.exe...")
                subprocess.Popen([exe_path])
            else:
                print("Файл Nerest.exe не найден! возможно его удалил Брандмауэр Windows")
                
        elif choice == "3":
            print("Выход...")
            sys.exit()
        else:
            print("Неверный выбор!")

if __name__ == "__main__":
    simple_menu()
