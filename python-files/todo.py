# todo.py

tasks = []

def show_menu():
    print("\n--- TO-DO LIST ---")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Remove Task")
    print("4. Exit")

while True:
    show_menu()
    choice = input("Choose an option (1-4): ")

    if choice == "1":
        task = input("Enter task: ")
        tasks.append(task)
        print(f"✅ Task added: {task}")

    elif choice == "2":
        if not tasks:
            print("⚠️ No tasks found.")
        else:
            print("\nYour Tasks:")
            for i, t in enumerate(tasks, start=1):
                print(f"{i}. {t}")

    elif choice == "3":
        if not tasks:
            print("⚠️ No tasks to remove.")
        else:
            num = int(input("Enter task number to remove: "))
            if 1 <= num <= len(tasks):
                removed = tasks.pop(num - 1)
                print(f"🗑️ Removed: {removed}")
            else:
                print("❌ Invalid task number.")

    elif choice == "4":
        print("👋 Goodbye!")
        break

    else:
        print("❌ Invalid option. Try again.")
