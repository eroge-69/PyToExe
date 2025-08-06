import json
import os
from datetime import datetime
import sys
from enum import Enum

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Status(Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class Task:
    def __init__(self, description, due_date=None, priority=Priority.MEDIUM, category="General"):
        self.id = None
        self.description = description
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.due_date = due_date
        self.priority = priority
        self.category = category
        self.status = Status.PENDING
        self.completed_at = None

    def mark_completed(self):
        self.status = Status.COMPLETED
        self.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def mark_in_progress(self):
        self.status = Status.IN_PROGRESS

    def mark_pending(self):
        self.status = Status.PENDING

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "created_at": self.created_at,
            "due_date": self.due_date,
            "priority": self.priority.value,
            "category": self.category,
            "status": self.status.value,
            "completed_at": self.completed_at
        }

    @classmethod
    def from_dict(cls, data):
        task = cls(
            description=data["description"],
            due_date=data["due_date"],
            priority=Priority(data["priority"]),
            category=data["category"]
        )
        task.id = data["id"]
        task.created_at = data["created_at"]
        task.status = Status(data["status"])
        task.completed_at = data["completed_at"]
        return task

class TodoApp:
    def __init__(self):
        self.tasks = []
        self.task_id_counter = 1
        self.data_file = "todo_data.json"
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as file:
                    data = json.load(file)
                    self.task_id_counter = data.get("task_id_counter", 1)
                    for task_data in data.get("tasks", []):
                        task = Task.from_dict(task_data)
                        self.tasks.append(task)
            except (json.JSONDecodeError, KeyError):
                print("Warning: Could not load data. Starting with empty task list.")
                self.tasks = []
                self.task_id_counter = 1

    def save_data(self):
        data = {
            "task_id_counter": self.task_id_counter,
            "tasks": [task.to_dict() for task in self.tasks]
        }
        with open(self.data_file, 'w') as file:
            json.dump(data, file, indent=2)

    def add_task(self):
        print("\n--- Add New Task ---")
        description = input("Enter task description: ")
        
        # Due date
        due_date = None
        due_date_input = input("Enter due date (YYYY-MM-DD) or leave blank: ")
        if due_date_input:
            try:
                datetime.strptime(due_date_input, "%Y-%m-%d")
                due_date = due_date_input
            except ValueError:
                print("Invalid date format. Task will be created without due date.")
        
        # Priority
        print("\nPriority options:")
        print("1. Low")
        print("2. Medium")
        print("3. High")
        priority_choice = input("Select priority (1-3, default=2): ")
        try:
            priority = Priority(int(priority_choice))
        except (ValueError, IndexError):
            priority = Priority.MEDIUM
        
        # Category
        category = input("Enter category (default=General): ") or "General"
        
        # Create and add task
        task = Task(description, due_date, priority, category)
        task.id = self.task_id_counter
        self.tasks.append(task)
        self.task_id_counter += 1
        self.save_data()
        
        print(f"\n✅ Task added successfully (ID: {task.id})")
        self.print_task_details(task)

    def print_task_details(self, task):
        status_color = {
            Status.PENDING: "\033[93m",    # Yellow
            Status.IN_PROGRESS: "\033[94m", # Blue
            Status.COMPLETED: "\033[92m"    # Green
        }
        
        priority_color = {
            Priority.LOW: "\033[97m",     # White
            Priority.MEDIUM: "\033[93m",  # Yellow
            Priority.HIGH: "\033[91m"     # Red
        }
        
        reset_color = "\033[0m"
        
        print(f"\nID: {task.id}")
        print(f"Description: {task.description}")
        print(f"Created: {task.created_at}")
        if task.due_date:
            print(f"Due Date: {task.due_date}")
        print(f"Priority: {priority_color[task.priority]}{task.priority.name}{reset_color}")
        print(f"Category: {task.category}")
        print(f"Status: {status_color[task.status]}{task.status.value}{reset_color}")
        if task.completed_at:
            print(f"Completed: {task.completed_at}")

    def view_tasks(self, filter_func=None):
        if not self.tasks:
            print("\nNo tasks yet!")
            return
        
        tasks_to_show = filter_func(self.tasks) if filter_func else self.tasks
        
        if not tasks_to_show:
            print("\nNo tasks match your filter!")
            return
        
        print("\n--- YOUR TO-DO LIST ---")
        for task in tasks_to_show:
            status_indicator = {
                Status.PENDING: "○",
                Status.IN_PROGRESS: "◐",
                Status.COMPLETED: "✓"
            }
            
            priority_indicator = {
                Priority.LOW: "!",
                Priority.MEDIUM: "!!",
                Priority.HIGH: "!!!"
            }
            
            due_str = f" (Due: {task.due_date})" if task.due_date else ""
            print(f"[{status_indicator[task.status]}] ID:{task.id} - {task.description}{due_str} [{priority_indicator[task.priority]}] [{task.category}]")
        print("-----------------------\n")

    def filter_by_status(self, status):
        return lambda tasks: [task for task in tasks if task.status == status]

    def filter_by_priority(self, priority):
        return lambda tasks: [task for task in tasks if task.priority == priority]

    def filter_by_category(self, category):
        return lambda tasks: [task for task in tasks if task.category.lower() == category.lower()]

    def search_tasks(self):
        if not self.tasks:
            print("\nNo tasks to search!")
            return
        
        search_term = input("\nEnter search term: ").lower()
        matching_tasks = [task for task in self.tasks if search_term in task.description.lower()]
        
        if not matching_tasks:
            print(f"\nNo tasks found containing '{search_term}'!")
            return
        
        print(f"\n--- TASKS CONTAINING '{search_term}' ---")
        for task in matching_tasks:
            status_indicator = {
                Status.PENDING: "○",
                Status.IN_PROGRESS: "◐",
                Status.COMPLETED: "✓"
            }
            print(f"[{status_indicator[task.status]}] ID:{task.id} - {task.description}")
        print("--------------------------------\n")

    def update_task_status(self):
        if not self.tasks:
            print("\nNo tasks yet!")
            return
        
        task_id = int(input("\nEnter task ID to update: "))
        for task in self.tasks:
            if task.id == task_id:
                print("\nCurrent status:", task.status.value)
                print("Status options:")
                print("1. Pending")
                print("2. In Progress")
                print("3. Completed")
                
                status_choice = input("Select new status (1-3): ")
                if status_choice == "1":
                    task.mark_pending()
                elif status_choice == "2":
                    task.mark_in_progress()
                elif status_choice == "3":
                    task.mark_completed()
                else:
                    print("Invalid choice. Status not updated.")
                    return
                
                self.save_data()
                print(f"\n✅ Task status updated to: {task.status.value}")
                self.print_task_details(task)
                return
        
        print("\n❌ Task not found!")

    def edit_task(self):
        if not self.tasks:
            print("\nNo tasks yet!")
            return
        
        task_id = int(input("\nEnter task ID to edit: "))
        for task in self.tasks:
            if task.id == task_id:
                print("\nCurrent task details:")
                self.print_task_details(task)
                
                print("\n--- Edit Task ---")
                task.description = input(f"Enter new description [{task.description}]: ") or task.description
                
                due_date_input = input(f"Enter due date (YYYY-MM-DD) [{task.due_date or 'None'}]: ")
                if due_date_input:
                    try:
                        datetime.strptime(due_date_input, "%Y-%m-%d")
                        task.due_date = due_date_input
                    except ValueError:
                        print("Invalid date format. Due date not updated.")
                
                print("\nPriority options:")
                print("1. Low")
                print("2. Medium")
                print("3. High")
                priority_choice = input(f"Select priority [{task.priority.name}] (1-3): ")
                if priority_choice:
                    try:
                        task.priority = Priority(int(priority_choice))
                    except (ValueError, IndexError):
                        print("Invalid priority. Priority not updated.")
                
                task.category = input(f"Enter category [{task.category}]: ") or task.category
                
                self.save_data()
                print("\n✅ Task updated successfully!")
                self.print_task_details(task)
                return
        
        print("\n❌ Task not found!")

    def delete_task(self):
        if not self.tasks:
            print("\nNo tasks yet!")
            return
        
        task_id = int(input("\nEnter task ID to delete: "))
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                removed = self.tasks.pop(i)
                self.save_data()
                print(f"\n🗑️ Deleted task: '{removed.description}'")
                return
        
        print("\n❌ Task not found!")

    def show_statistics(self):
        if not self.tasks:
            print("\nNo tasks to show statistics for!")
            return
        
        total = len(self.tasks)
        pending = len([t for t in self.tasks if t.status == Status.PENDING])
        in_progress = len([t for t in self.tasks if t.status == Status.IN_PROGRESS])
        completed = len([t for t in self.tasks if t.status == Status.COMPLETED])
        
        high_priority = len([t for t in self.tasks if t.priority == Priority.HIGH])
        medium_priority = len([t for t in self.tasks if t.priority == Priority.MEDIUM])
        low_priority = len([t for t in self.tasks if t.priority == Priority.LOW])
        
        overdue = 0
        today = datetime.now().strftime("%Y-%m-%d")
        for task in self.tasks:
            if task.due_date and task.status != Status.COMPLETED and task.due_date < today:
                overdue += 1
        
        categories = {}
        for task in self.tasks:
            if task.category in categories:
                categories[task.category] += 1
            else:
                categories[task.category] = 1
        
        print("\n--- TASK STATISTICS ---")
        print(f"Total tasks: {total}")
        print(f"Pending: {pending} ({pending/total*100:.1f}%)")
        print(f"In Progress: {in_progress} ({in_progress/total*100:.1f}%)")
        print(f"Completed: {completed} ({completed/total*100:.1f}%)")
        print("\nPriority Distribution:")
        print(f"High: {high_priority} ({high_priority/total*100:.1f}%)")
        print(f"Medium: {medium_priority} ({medium_priority/total*100:.1f}%)")
        print(f"Low: {low_priority} ({low_priority/total*100:.1f}%)")
        print(f"\nOverdue tasks: {overdue}")
        print("\nCategories:")
        for category, count in sorted(categories.items()):
            print(f"{category}: {count} ({count/total*100:.1f}%)")
        print("------------------------\n")

    def run(self):
        print("\033[95m" + "\n=== ENHANCED TO-DO LIST APP ===" + "\033[0m")
        
        while True:
            print("\nMain Menu:")
            print("1. Add Task")
            print("2. View All Tasks")
            print("3. View Pending Tasks")
            print("4. View In Progress Tasks")
            print("5. View Completed Tasks")
            print("6. View Tasks by Priority")
            print("7. View Tasks by Category")
            print("8. Search Tasks")
            print("9. Update Task Status")
            print("10. Edit Task")
            print("11. Delete Task")
            print("12. Show Statistics")
            print("13. Exit")
            
            choice = input("\nSelect an option (1-13): ")
            
            if choice == "1":
                self.add_task()
            elif choice == "2":
                self.view_tasks()
            elif choice == "3":
                self.view_tasks(self.filter_by_status(Status.PENDING))
            elif choice == "4":
                self.view_tasks(self.filter_by_status(Status.IN_PROGRESS))
            elif choice == "5":
                self.view_tasks(self.filter_by_status(Status.COMPLETED))
            elif choice == "6":
                print("\nPriority options:")
                print("1. Low")
                print("2. Medium")
                print("3. High")
                priority_choice = input("Select priority (1-3): ")
                try:
                    priority = Priority(int(priority_choice))
                    self.view_tasks(self.filter_by_priority(priority))
                except (ValueError, IndexError):
                    print("Invalid priority choice.")
            elif choice == "7":
                category = input("\nEnter category to filter by: ")
                self.view_tasks(self.filter_by_category(category))
            elif choice == "8":
                self.search_tasks()
            elif choice == "9":
                self.update_task_status()
            elif choice == "10":
                self.edit_task()
            elif choice == "11":
                self.delete_task()
            elif choice == "12":
                self.show_statistics()
            elif choice == "13":
                print("\n👋 Goodbye! Your tasks have been saved.")
                break
            else:
                print("\n❌ Invalid choice. Try again!")

if __name__ == "__main__":
    app = TodoApp()
    app.run()