
import tkinter as tk
from tkinter import messagebox
import datetime

tasks = []

def add_task():
    task = entry.get()
    if task:
        tasks.append(task)
        listbox.insert(tk.END, task)
        entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Champ vide", "Veuillez entrer une tâche.")

def delete_task():
    selected = listbox.curselection()
    if selected:
        listbox.delete(selected[0])
        del tasks[selected[0]]

app = tk.Tk()
app.title("Rappels PC+")
app.geometry("400x400")
app.configure(bg="#f7f7f5")

entry = tk.Entry(app, width=30)
entry.pack(pady=10)

add_btn = tk.Button(app, text="Ajouter un rappel", command=add_task)
add_btn.pack()

listbox = tk.Listbox(app, width=50, height=10)
listbox.pack(pady=10)

del_btn = tk.Button(app, text="Supprimer", command=delete_task)
del_btn.pack()

app.mainloop()
