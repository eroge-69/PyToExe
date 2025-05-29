
tasks = []

def show_tasks():
    if not tasks:
        print("Brak zadań na liście.")
    else:
        print("Twoje zadania:")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task}")

def add_task():
    task = input("Wpisz nowe zadanie: ")
    tasks.append(task)
    print(f"Zadanie '{task}' dodane.")

def remove_task():
    show_tasks()
    if tasks:
        try:
            index = int(input("Podaj numer zadania do usunięcia: "))
            if 1 <= index <= len(tasks):
                removed = tasks.pop(index - 1)
                print(f"Zadanie '{removed}' usunięte.")
            else:
                print("Niepoprawny numer.")
        except ValueError:
            print("Proszę wpisać poprawny numer.")

def main():
    while True:
        print("\nMenu:")
        print("1. Wyświetl listę zadań")
        print("2. Dodaj zadanie")
        print("3. Usuń zadanie")
        print("4. Zakończ")
        choice = input("Wybierz opcję: ")

        if choice == '1':
            show_tasks()
        elif choice == '2':
            add_task()
        elif choice == '3':
            remove_task()
        elif choice == '4':
            print("Do widzenia!")
            break
        else:
            print("Nieprawidłowa opcja, spróbuj ponownie.")

if __name__ == "__main__":
    main()
