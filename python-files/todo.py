import argparse
from pathlib import Path

TODO_FILE = Path.home() / '.todo.txt'

def add_task(description):
    with open(TODO_FILE, 'a') as f:
        f.write(f"[ ] {description}\n")
    print(f"Added task: {description}")

def list_tasks():
    if not TODO_FILE.exists():
        print("No tasks found!")
        return

    with open(TODO_FILE, 'r') as f:
        tasks = f.readlines()

    if not tasks:
        print("No tasks found!")
        return

    for idx, task in enumerate(tasks, 1):
        print(f"{idx}. {task.strip()}")

def complete_task(index):
    tasks = get_all_tasks()
    
    try:
        index = int(index) - 1
        if 0 <= index < len(tasks):
            if not tasks[index].startswith('[x]'):
                tasks[index] = tasks[index].replace('[ ]', '[x]', 1)
                save_tasks(tasks)
                print(f"Marked task {index + 1} as complete")
            else:
                print(f"Task {index + 1} is already complete")
        else:
            print("Invalid task number")
    except ValueError:
        print("Please enter a valid number")

def delete_task(index):
    tasks = get_all_tasks()
    
    try:
        index = int(index) - 1
        if 0 <= index < len(tasks):
            deleted_task = tasks.pop(index)
            save_tasks(tasks)
            print(f"Deleted task: {deleted_task.strip()}")
        else:
            print("Invalid task number")
    except ValueError:
        print("Please enter a valid number")

def get_all_tasks():
    if not TODO_FILE.exists():
        return []
    
    with open(TODO_FILE, 'r') as f:
        return f.readlines()

def save_tasks(tasks):
    with open(TODO_FILE, 'w') as f:
        f.writelines(tasks)

def main():
    parser = argparse.ArgumentParser(description="Command-line Todo List")
    subparsers = parser.add_subparsers(dest='command')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('description', type=str, help='Task description')

    # List command
    subparsers.add_parser('list', help='List all tasks')

    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Mark task as complete')
    complete_parser.add_argument('index', type=str, help='Task number to mark complete')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('index', type=str, help='Task number to delete')

    args = parser.parse_args()

    if args.command == 'add':
        add_task(args.description)
    elif args.command == 'list':
        list_tasks()
    elif args.command == 'complete':
        complete_task(args.index)
    elif args.command == 'delete':
        delete_task(args.index)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()