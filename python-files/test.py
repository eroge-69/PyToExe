import os

def create_files():
    # Получаем путь к рабочему столу
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    
    # Создаем 5 файлов
    for i in range(1, 6):
        filename = f"привет_{i}.txt"
        filepath = os.path.join(desktop, filename)
        
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(f"Привет, это файл номер {i}!")
    
    print(f"Создано 5 файлов на рабочем столе!")

if __name__ == "__main__":
    print("Привет!")
    create_files()
