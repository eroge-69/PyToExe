import json

class CriminalDatabase:
    def __init__(self, filename="criminal_database.json"):
        self.filename = filename
        self.load_database()
    
    def load_database(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.people = json.load(f)
        except FileNotFoundError:
            self.people = []
    
    def save_database(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.people, f, ensure_ascii=False, indent=2)
    
    def add_person(self):
        print("\n--- Добавление нового человека ---")
        name = input("ФИО: ")
        age = input("Возраст: ")
        description = input("Описание: ")
        crime = input("Преступление: ")
        
        person = {
            "name": name,
            "age": age,
            "description": description,
            "crime": crime,
            "status": "В розыске"
        }
        
        self.people.append(person)
        self.save_database()
        print(f"\n{name} добавлен в базу данных!")
    
    def show_all_people(self):
        print("\n--- База данных преступников ---")
        if not self.people:
            print("База данных пуста")
            return
        
        for i, person in enumerate(self.people, 1):
            print(f"{i}. {person['name']} - {person['status']}")
    
    def generate_dossier(self, index):
        if 0 <= index < len(self.people):
            person = self.people[index]
            print("\n" + "="*50)
            print("ДОСЬЕ НА РОЗЫСК")
            print("="*50)
            print(f"ФИО: {person['name']}")
            print(f"Возраст: {person['age']}")
            print(f"Приметы: {person['description']}")
            print(f"Преступление: {person['crime']}")
            print(f"Статус: {person['status']}")
            print("="*50)
        else:
            print("Неверный номер!")
    
    def run(self):
        while True:
            print("\n--- Криминальная база данных ---")
            print("1. Показать всех людей")
            print("2. Добавить человека")
            print("3. Сформировать досье")
            print("4. Выход")
            
            choice = input("\nВыберите действие: ")
            
            if choice == "1":
                self.show_all_people()
            
            elif choice == "2":
                self.add_person()
            
            elif choice == "3":
                self.show_all_people()
                if self.people:
                    try:
                        num = int(input("\nВведите номер человека для досье: ")) - 1
                        self.generate_dossier(num)
                    except ValueError:
                        print("Введите число!")
            
            elif choice == "4":
                print("Выход из программы")
                break
            
            else:
                print("Неверный выбор!")

# Запуск программы
if __name__ == "__main__":
    db = CriminalDatabase()
    db.run()