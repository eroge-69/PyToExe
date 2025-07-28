import pandas as pd

# Загрузка файла Excel
file_path = input("Введите путь к файлу Excel: ")
try:
    df = pd.read_excel(file_path, dtype={'номер': str, 'id': str})
except Exception as e:
    print(f"Ошибка при загрузке файла: {e}")
    exit()

print("Программа запущена. Введите номер для поиска или 'exit' для выхода.")

while True:
    # Запрос номера у пользователя
    user_input = input("\nВведите номер: ").strip()
    
    if user_input.lower() == 'exit':
        break
    
    # Поиск совпадений (с учетом возможных пробелов и регистра)
    results = df[df['номер'].astype(str).str.strip().str.lower() == user_input.lower()]
    
    if results.empty:
        print(f"ID для номера '{user_input}' не найден")
    else:
        # Вывод всех найденных ID (если дубликатов нет - будет один)
        for _, row in results.iterrows():
            print(f"ID: {row['id']}")

print("Работа программы завершена.")