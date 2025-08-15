import os

def create_project_structure(base_path, project_name):
    # Создаём основную папку проекта
    project_path = os.path.join(base_path, project_name)
    os.makedirs(project_path, exist_ok=True)

    # Папка 2: modeling с подпапками high и mid
    modeling_path = os.path.join(project_path, "modeling")
    os.makedirs(modeling_path, exist_ok=True)
    os.makedirs(os.path.join(modeling_path, "high"), exist_ok=True)
    os.makedirs(os.path.join(modeling_path, "mid"), exist_ok=True)

    # Папка 3: baking с подпапкой baking maps
    baking_path = os.path.join(project_path, "baking")
    os.makedirs(baking_path, exist_ok=True)
    os.makedirs(os.path.join(baking_path, "baking maps"), exist_ok=True)

    # Папка 4: UV
    os.makedirs(os.path.join(project_path, "UV"), exist_ok=True)

    # Папка 5: references
    os.makedirs(os.path.join(project_path, "references"), exist_ok=True)

    print(f"Структура папок для проекта '{project_name}' успешно создана в '{project_path}'")

if __name__ == "__main__":
    # Укажите путь, где будет создана структура (например, рабочий стол)
    base_directory = input("Введите путь к папке, где создать проект (например, C:\\Users\\YourName\\Desktop): ").strip()
    
    # Укажите название проекта
    project_name = input("Введите название проекта: ").strip()

    # Проверка, что введены оба значения
    if not base_directory or not project_name:
        print("Ошибка: необходимо указать путь и название проекта.")
    else:
        create_project_structure(base_directory, project_name)