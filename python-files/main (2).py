tasks = []

def show_tasks():
    if not tasks:
        print("Твоя хуйня пуста, добав щось!")
    else:
        print("Твої справи:")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task}")
show_tasks()
def add_task():
    task = input("Введи нову хуйню: ")
    tasks.append(task)
    print(f"добавіло хуйло: {task}")
def main():
    while True:
        print("\nшо їбашимо?")
        print("1 — додати хуйню")
        print("2 — показати хуйню")
        print("3 — лівнуть")
        
        choice = input("Вибір: ")

        if choice == '1':
            add_task()
        elif choice == '2':
            show_tasks()
        elif choice == '3':
            print("па па")
            break
        else:
            print("ти даун по новій давай")
import tkinter as tk

tasks = []

def add_task():
    task = entry.get()
    if task:
        tasks.append(task)
        update_list()
        entry_delete(0, tk.END)
        
def update_list():
    listbox.delete(0, tk.END)
    for task in tasks:
        listbox.insert(tk.END, task)

root = tk.TK()
root.title("Мій to-do лістік")

entry = tk.Entry(root, width=40)
entry.pack(pady=10)

add_button = tk.Button(root, text="Піти нахуй", command=add_task)
add_button.pack()

listbox = tk.Listbox(root, width=50)
listbox.pack(pady=10)

root.mainloop()

main()