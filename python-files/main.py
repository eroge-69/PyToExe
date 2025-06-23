
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
from datetime import datetime

SAVE_FILE = "rappels.json"

class RappelsApp:
    def __init__(self, master):
        self.master = master
        master.title("Rappels PC+")
        master.geometry("500x500")
        master.configure(bg="#f8f8f5")

        self.tasks = []
        self.load_tasks()

        self.entry = tk.Entry(master, width=40)
        self.entry.pack(pady=10)

        self.add_button = tk.Button(master, text="Ajouter un rappel", command=self.add_task)
        self.add_button.pack()

        self.listbox = tk.Listbox(master, width=70, height=15)
        self.listbox.pack(pady=10)

        self.date_button = tk.Button(master, text="Ajouter une date", command=self.add_date_to_task)
        self.date_button.pack(pady=5)

        self.delete_button = tk.Button(master, text="Supprimer", command=self.delete_task)
        self.delete_button.pack(pady=5)

        self.save_button = tk.Button(master, text="Sauvegarder", command=self.save_tasks)
        self.save_button.pack(pady=5)

        self.refresh_listbox()

    def add_task(self):
        task = self.entry.get()
        if task:
            self.tasks.append({"task": task, "date": ""})
            self.entry.delete(0, tk.END)
            self.refresh_listbox()
        else:
            messagebox.showwarning("Champ vide", "Veuillez entrer une tâche.")

    def add_date_to_task(self):
        selected = self.listbox.curselection()
        if selected:
            date_str = simpledialog.askstring("Date", "Entrez une date (ex: 2025-06-22 14:00):")
            try:
                datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                self.tasks[selected[0]]["date"] = date_str
                self.refresh_listbox()
            except:
                messagebox.showerror("Erreur", "Format invalide. Utilisez AAAA-MM-JJ HH:MM.")

    def delete_task(self):
        selected = self.listbox.curselection()
        if selected:
            del self.tasks[selected[0]]
            self.refresh_listbox()

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for t in self.tasks:
            display = t["task"]
            if t["date"]:
                display += f"  ⏰ {t['date']}"
            self.listbox.insert(tk.END, display)

    def save_tasks(self):
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Sauvegarde", "Les rappels ont été sauvegardés.")

    def load_tasks(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                self.tasks = json.load(f)

if __name__ == "__main__":
    root = tk.Tk()
    app = RappelsApp(root)
    root.mainloop()
