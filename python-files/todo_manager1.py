import json
import os
from datetime import datetime, timedelta

TASK_FILE = "tasks.json"

# ---------------- File Handling ----------------
def load_tasks():
    if not os.path.exists(TASK_FILE):
        return []
    with open(TASK_FILE, "r") as file:
        return json.load(file)

def save_tasks(tasks):
    with open(TASK_FILE, "w") as file:
        json.dump(tasks, file, indent=4)

# ---------------- Task Functions ----------------
def add_task(tasks):
    description = input("Enter task description: ")
    due_date = input("Enter due date (YYYY-MM-DD) or leave blank: ")
    task = {
        "description": description,
        "due_date": due_date,
        "completed": False
    }
    tasks.append(task)
    save_tasks(tasks)
    print("✅ Task added successfully!")

def view_tasks(tasks, filter_type="all"):
    print("\n--- Tasks ---")
    for i, task in enumerate(tasks):
        due_info = f", Due: {task['due_date']}" if task['due_date'] else ""
        status = "✔ Done" if task["completed"] else "⏳ Pending"
        
        if filter_type == "completed" and not task["completed"]:
            continue
        elif filter_type == "pending" and task["completed"]:
            continue
        elif filter_type == "due_soon":
            if not task["due_date"]:
                continue
            due_date = datetime.strptime(task["due_date"], "%Y-%m-%d")
            if due_date > datetime.today() + timedelta(days=3):
                continue

        print(f"{i+1}. {task['description']} [{status}{due_info}]")
    print()

def mark_task_complete(tasks):
    view_tasks(tasks, filter_type="pending")
    try:
        idx = int(input("Enter task number to mark as complete: ")) - 1
        tasks[idx]["completed"] = True
        save_tasks(tasks)
        print("✅ Task marked as complete!")
    except:
        print("❌ Invalid input.")

def edit_task(tasks):
    view_tasks(tasks)
    try:
        idx = int(input("Enter task number to edit: ")) - 1
        new_desc = input("Enter new description: ")
        new_due = input("Enter new due date (YYYY-MM-DD) or leave blank: ")
        tasks[idx]["description"] = new_desc
        tasks[idx]["due_date"] = new_due
        save_tasks(tasks)
        print("✅ Task edited successfully!")
    except:
        print("❌ Invalid input.")

def delete_task(tasks):
    view_tasks(tasks)
    try:
        idx = int(input("Enter task number to delete: ")) - 1
        removed = tasks.pop(idx)
        save_tasks(tasks)
        print(f"✅ Task '{removed['description']}' deleted.")
    except:
        print("❌ Invalid input.")

# ---------------- Menu ----------------
def menu():
    tasks = load_tasks()

    while True:
        print("\n==== To-Do List Manager ====")
        print("1. Add Task")
        print("2. View All Tasks")
        print("3. View Completed Tasks")
        print("4. View Pending Tasks")
        print("5. View Tasks Due Soon")
        print("6. Mark Task as Complete")
        print("7. Edit Task")
        print("8. Delete Task")
        print("9. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            view_tasks(tasks, "all")
        elif choice == "3":
            view_tasks(tasks, "completed")
        elif choice == "4":
            view_tasks(tasks, "pending")
        elif choice == "5":
            view_tasks(tasks, "due_soon")
        elif choice == "6":
            mark_task_complete(tasks)
        elif choice == "7":
            edit_task(tasks)
        elif choice == "8":
            delete_task(tasks)
        elif choice == "9":
            print("👋 Exiting To-Do List Manager. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 9.")

# Run the program
if __name__ == "__main__":
    menu()