import json
import os

# Класс для работы с экспонатами
class МузейныйЭкспонат:
    def __init__(self, id, название, автор, год, местоположение, описание):
        self.id = id
        self.название = название
        self.автор = автор
        self.год = год
        self.местоположение = местоположение
        self.описание = описание
    
    def to_dict(self):
        return {
            'id': self.id,
            'название': self.название,
            'автор': self.автор,
            'год': self.год,
            'местоположение': self.местоположение,
            'описание': self.описание
        }

# Класс для работы с базой данных музея
class МузейнаяБазаДанных:
    def __init__(self, файл_базы='музейная_база.json'):
        self.файл_базы = файл_базы
        self.экспонаты = []
        self.загрузить_базу()
    
    def загрузить_базу(self):
        if os.path.exists(self.файл_базы):
            with open(self.файл_базы, 'r', encoding='utf-8') as файл:
                данные = json.load(файл)
                self.экспонаты = [МузейныйЭкспонат(**item) for item in данные]
        else:
            self.экспонаты = []
    
    def сохранить_базу(self):
        with open(self.файл_базы, 'w', encoding='utf-8') as файл:
            json.dump([экспонат.to_dict() for экспонат in self.экспонаты], файл, ensure_ascii=False, indent=2)
    
    def добавить_экспонат(self, экспонат):
        self.экспонаты.append(экспонат)
        self.сохранить_базу()
    
    def найти_экспонат_по_id(self, id):
        for экспонат in self.экспонаты:
            if экспонат.id == id:
                return экспонат
        return None
    
    def найти_экспонаты_по_названию(self, название):
        return [экспонат for экспонат in self.экспонаты if название.lower() in экспонат.название.lower()]
    
    def удалить_экспонат(self, id):
        экспонат = self.найти_экспонат_по_id(id)
        if экспонат:
            self.экспонаты.remove(экспонат)
            self.сохранить_базу()
            return True
        return False
    
    def получить_все_экспонаты(self):
        return self.экспонаты

# Функции для взаимодействия с пользователем
def показать_меню():
    print("\n=== Система учета экспонатов музея ===")
    print("1. Добавить новый экспонат")
    print("2. Просмотреть все экспонаты")
    print("3. Найти экспонат по ID")
    print("4. Найти экспонаты по названию")
    print("5. Редактировать экспонат")
    print("6. Удалить экспонат")
    print("0. Выход")

def ввести_экспонат(база_данных):
    print("\nДобавление нового экспоната:")
    id = input("Введите ID экспоната: ")
    
    # Проверка на уникальность ID
    if база_данных.найти_экспонат_по_id(id):
        print("Ошибка: экспонат с таким ID уже существует!")
        return
    
    название = input("Введите название: ")
    автор = input("Введите автора: ")
    год = input("Введите год создания: ")
    местоположение = input("Введите местоположение в музее: ")
    описание = input("Введите описание: ")
    
    новый_экспонат = МузейныйЭкспонат(id, название, автор, год, местоположение, описание)
    база_данных.добавить_экспонат(новый_экспонат)
    print("Экспонат успешно добавлен!")

def показать_экспонат(экспонат):
    if экспонат:
        print("\nИнформация об экспонате:")
        print(f"ID: {экспонат.id}")
        print(f"Название: {экспонат.название}")
        print(f"Автор: {экспонат.автор}")
        print(f"Год создания: {экспонат.год}")
        print(f"Местоположение: {экспонат.местоположение}")
        print(f"Описание: {экспонат.описание}")
    else:
        print("Экспонат не найден!")

def показать_все_экспонаты(база_данных):
    экспонаты = база_данных.получить_все_экспонаты()
    if экспонаты:
        print("\nСписок всех экспонатов:")
        for экспонат in экспонаты:
            print(f"{экспонат.id}: {экспонат.название} ({экспонат.автор}, {экспонат.год})")
    else:
        print("В базе данных нет экспонатов!")

def найти_экспонат_по_id(база_данных):
    id = input("Введите ID экспоната: ")
    экспонат = база_данных.найти_экспонат_по_id(id)
    показать_экспонат(экспонат)

def найти_экспонаты_по_названию(база_данных):
    название = input("Введите название или часть названия: ")
    экспонаты = база_данных.найти_экспонаты_по_названию(название)
    if экспонаты:
        print("\nНайденные экспонаты:")
        for экспонат in экспонаты:
            print(f"{экспонат.id}: {экспонат.название} ({экспонат.автор}, {экспонат.год})")
    else:
        print("Экспонаты не найдены!")

def редактировать_экспонат(база_данных):
    id = input("Введите ID экспоната для редактирования: ")
    экспонат = база_данных.найти_экспонат_по_id(id)
    
    if not экспонат:
        print("Экспонат не найден!")
        return
    
    показать_экспонат(экспонат)
    print("\nВведите новые данные (оставьте пустым, чтобы не изменять):")
    
    новое_название = input(f"Название [{экспонат.название}]: ")
    новый_автор = input(f"Автор [{экспонат.автор}]: ")
    новый_год = input(f"Год [{экспонат.год}]: ")
    новое_местоположение = input(f"Местоположение [{экспонат.местоположение}]: ")
    новое_описание = input(f"Описание [{экспонат.описание}]: ")
    
    if новое_название:
        экспонат.название = новое_название
    if новый_автор:
        экспонат.автор = новый_автор
    if новый_год:
        экспонат.год = новый_год
    if новое_местоположение:
        экспонат.местоположение = новое_местоположение
    if новое_описание:
        экспонат.описание = новое_описание
    
    база_данных.сохранить_базу()
    print("Изменения сохранены!")

def удалить_экспонат(база_данных):
    id = input("Введите ID экспоната для удаления: ")
    if база_данных.удалить_экспонат(id):
        print("Экспонат успешно удален!")
    else:
        print("Экспонат не найден!")

# Основная функция
def main():
    база_данных = МузейнаяБазаДанных()
    
    while True:
        показать_меню()
        выбор = input("Выберите действие: ")
        
        if выбор == '1':
            ввести_экспонат(база_данных)
        elif выбор == '2':
            показать_все_экспонаты(база_данных)
        elif выбор == '3':
            найти_экспонат_по_id(база_данных)
        elif выбор == '4':
            найти_экспонаты_по_названию(база_данных)
        elif выбор == '5':
            редактировать_экспонат(база_данных)
        elif выбор == '6':
            удалить_экспонат(база_данных)
        elif выбор == '0':
            print("Выход из программы...")
            break
        else:
            print("Неверный ввод! Попробуйте еще раз.")

if __name__ == "__main__":
    main()