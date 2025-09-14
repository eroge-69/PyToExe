import tkinter as tk
from tkinter import messagebox

# --- Functions ---
def add_task():
    task = task_entry.get()
    if task != "":
        task_listbox.insert(tk.END, task)
        task_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Warning", "You must enter a task!")

def delete_task():
    try:
        selected_task = task_listbox.curselection()[0]
        task_listbox.delete(selected_task)
    except:
        messagebox.showwarning("Warning", "Select a task to delete")

def clear_all():
    task_listbox.delete(0, tk.END)

# --- GUI ---
app = tk.Tk()
app.title("To-Do List App")
app.geometry("300x400")

task_entry = tk.Entry(app, width=25)
task_entry.pack(pady=10)

add_button = tk.Button(app, text="Add Task", width=15, command=add_task)
add_button.pack(pady=5)

delete_button = tk.Button(app, text="Delete Task", width=15, command=delete_task)
delete_button.pack(pady=5)

clear_button = tk.Button(app, text="Clear All", width=15, command=clear_all)
clear_button.pack(pady=5)

task_listbox = tk.Listbox(app, width=40, height=15)
task_listbox.pack(pady=10)

app.mainloop()
