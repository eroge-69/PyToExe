import json
import os

DATA_FILE = 'tasks.json'

PROFILES = ['R1', 'R2', 'R3X', 'EDV']
STATUSES = ['Input', 'In Progress', 'Completed']

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def add_task(tasks):
    print("\\nSelect a profile:")
    for i, p in enumerate(PROFILES):
        print(f"[{i+1}] {p}")
    profile = PROFILES[int(input("Enter choice: ")) - 1]

    subcategory = input("Enter subcategory: ")
    task_name = input("Enter task name or ID: ")
    status = STATUSES[0] # default to 'Input'
    notes = input("Enter any notes (optional): ")

    tasks.append({
        'profile': profile,
        'subcategory': subcategory,
        'name': task_name,
        'status': status,
        'notes': notes
    })
    print("Task added successfully.")

def view_tasks(tasks):
    if not tasks:
        print("\\nNo tasks available.")
        return
    for i, t in enumerate(tasks):
        print(f"\\nTask #{i+1}")
        print(f"Profile: {t['profile']}")
        print(f"Subcategory: {t['subcategory']}")
        print(f"Name: {t['name']}")
        print(f"Status: {t['status']}")
        print(f"Notes: {t['notes']}")

def update_task(tasks):
    view_tasks(tasks)
    if not tasks:
        return
    index = int(input("\\nEnter task number to update: ")) - 1
    if index < 0 or index >= len(tasks):
        print("Invalid task number.")
        return

    print("\\nUpdate status:")
    for i, s in enumerate(STATUSES):
        print(f"[{i+1}] {s}")
    tasks[index]['status'] = STATUSES[int(input("Enter choice: ")) - 1]
    print("Status updated.")

    edit_notes = input("Edit notes? (y/n): ").lower()
    if edit_notes == 'y':
        tasks[index]['notes'] = input("Enter new notes: ")

def filter_tasks(tasks):
    print("\\nFilter by:")
    print("[1] Profile")
    print("[2] Status")
    choice = input("Enter choice: ")

    if choice == '1':
        print("\\nSelect profile:")
        for i, p in enumerate(PROFILES):
            print(f"[{i+1}] {p}")
        profile = PROFILES[int(input("Enter choice: ")) - 1]
        filtered = [t for t in tasks if t['profile'] == profile]
    elif choice == '2':
        print("\\nSelect status:")
        for i, s in enumerate(STATUSES):
            print(f"[{i+1}] {s}")
        status = STATUSES[int(input("Enter choice: ")) - 1]
        filtered = [t for t in tasks if t['status'] == status]
    else:
        print("Invalid choice.")
        return

    if not filtered:
        print("\\nNo matching tasks.")
    else:
        view_tasks(filtered)

def main():
    tasks = load_tasks()

    while True:
        print("\\nWork Manager CLI")
        print("[1] Add a new task")
        print("[2] View all tasks")
        print("[3] Update a task")
        print("[4] Filter tasks by profile/status")
        print("[5] Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            add_task(tasks)
        elif choice == '2':
            view_tasks(tasks)
        elif choice == '3':
            update_task(tasks)
        elif choice == '4':
            filter_tasks(tasks)
        elif choice == '5':
            save_tasks(tasks)
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()