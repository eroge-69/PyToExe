import tkinter as tk
from tkinter import messagebox

def add_task():
    task = task_entry.get()  # Get the text entered in the task entry box
    if task != "":
        task_listbox.insert(tk.END, task)  # Add the task to the listbox
        task_entry.delete(0, tk.END)  # Clear the entry box
    else:
        messagebox.showwarning("Input Error", "Please enter a task.")

def delete_task():
    try:
        selected_task_index = task_listbox.curselection()[0]
        task_listbox.delete(selected_task_index)
    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to delete.")

def mark_done():
    try:
        selected_task_index = task_listbox.curselection()[0]
        task = task_listbox.get(selected_task_index)
        task_listbox.delete(selected_task_index)
        task_listbox.insert(tk.END, task + " (Done)")
    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to mark as done.")

root = tk.Tk()
root.title("To-Do List App")

task_entry = tk.Entry(root, width=40)
task_entry.pack(pady=10)

add_button = tk.Button(root, text="Add Task", width=20, command=add_task)
add_button.pack(pady=5)

task_listbox = tk.Listbox(root, width=50, height=10)
task_listbox.pack(pady=10)

delete_button = tk.Button(root, text="Delete Task", width=20, command=delete_task)
delete_button.pack(pady=5)

mark_done_button = tk.Button(root, text="Mark as Done", width=20, command=mark_done)
mark_done_button.pack(pady=5)

root.mainloop()