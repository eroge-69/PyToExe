import
import os
import json
from datetime import datetime

TASKS_FILE = "tasks.json"


def load_tasks():
    """Загружает задачи из файла"""
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}


def save_tasks(tasks):
    """Сохраняет задачи в файл"""
    with open(TASKS_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, ensure_ascii=False, indent=4)


def print_tasks(tasks):
    """Выводит список задач с нумерацией"""
    if not tasks:
        print("\nСписок задач пуст.\n")1
        return

    print("\n--- Ваши задачи ---")
    for i, (task, details) in enumerate(tasks.items(), 1):
        print(f"{i}. {task}")
        print(f"   Описание: {details['description']}")
        print(f"   Дата создания: {details['created_at']}\n")
    print("------------------")


def add_task(tasks):
    """Добавляет новую задачу"""
    task = input("Введите название задачи: ")
    description = input("Введите описание задачи: ")

    tasks[task] = {
        "description": description,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "completed": False
    }
    save_tasks(tasks)
    print(f"\nЗадача '{task}' успешно добавлена!\n")


def delete_task(tasks):
    """Удаляет задачу"""
    print_tasks(tasks)
    if not tasks:
        return

    try:
        task_num = int(input("\nВведите номер задачи для удаления: "))
        task_name = list(tasks.keys())[task_num - 1]
        del tasks[task_name]
        save_tasks(tasks)
        print(f"\nЗадача '{task_name}' удалена!\n")
    except (ValueError, IndexError):
        print("\nОшибка: неверный номер задачи!\n")


def mark_completed(tasks):
    """Отмечает задачу как выполненную"""
    print_tasks(tasks)
    if not tasks:
        return

    try:
        task_num = int(input("\nВведите номер выполненной задачи: "))
        task_name = list(tasks.keys())[task_num - 1]
        tasks[task_name]["completed"] = True
        tasks[task_name]["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_tasks(tasks)
        print(f"\nЗадача '{task_name}' отмечена как выполненная!\n")
    except (ValueError, IndexError):
        print("\nОшибка: неверный номер задачи!\n")


def main():
    tasks = load_tasks()

    while True:
        print("\n=== Менеджер задач ===")
        print("1. Показать все задачи")
        print("2. Добавить задачу")
        print("3. Удалить задачу")
        print("4. Отметить как выполненную")
        print("5. Выйти")

        choice = input("\nВыберите действие (1-5): ")

        if choice == "1":
            print_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
        elif choice == "3":
            delete_task(tasks)
        elif choice == "4":
            mark_completed(tasks)
        elif choice == "5":
            print("\nРабота программы завершена. До свидания!")
            break
        else:
            print("\nОшибка: введите число от 1 до 5\n")


if __name__ == "__main__":
    main()
