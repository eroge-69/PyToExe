# Poultry Management System (Basic Desktop App)
# Modules: Flock, Feed, Egg Production

import tkinter as tk
from tkinter import ttk, messagebox
import csv

class PoultryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Poultry Management System")
        self.root.geometry("700x500")

        self.tabControl = ttk.Notebook(root)

        self.flock_tab = ttk.Frame(self.tabControl)
        self.feed_tab = ttk.Frame(self.tabControl)
        self.egg_tab = ttk.Frame(self.tabControl)

        self.tabControl.add(self.flock_tab, text='Flock Management')
        self.tabControl.add(self.feed_tab, text='Feed Tracking')
        self.tabControl.add(self.egg_tab, text='Egg Production')
        self.tabControl.pack(expand=1, fill="both")

        self.setup_flock_tab()
        self.setup_feed_tab()
        self.setup_egg_tab()

    def setup_flock_tab(self):
        ttk.Label(self.flock_tab, text="Flock Name").grid(column=0, row=0, padx=10, pady=10)
        ttk.Label(self.flock_tab, text="Breed").grid(column=0, row=1, padx=10)
        ttk.Label(self.flock_tab, text="Arrival Date").grid(column=0, row=2, padx=10)

        self.flock_name = tk.StringVar()
        self.breed = tk.StringVar()
        self.arrival_date = tk.StringVar()

        tk.Entry(self.flock_tab, textvariable=self.flock_name).grid(column=1, row=0)
        tk.Entry(self.flock_tab, textvariable=self.breed).grid(column=1, row=1)
        tk.Entry(self.flock_tab, textvariable=self.arrival_date).grid(column=1, row=2)

        tk.Button(self.flock_tab, text="Save Flock", command=self.save_flock).grid(column=1, row=3, pady=10)

    def save_flock(self):
        data = [self.flock_name.get(), self.breed.get(), self.arrival_date.get()]
        with open("flocks.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(data)
        messagebox.showinfo("Saved", "Flock saved successfully")

    def setup_feed_tab(self):
        ttk.Label(self.feed_tab, text="Date").grid(column=0, row=0, padx=10, pady=10)
        ttk.Label(self.feed_tab, text="Feed Quantity (kg)").grid(column=0, row=1, padx=10)

        self.feed_date = tk.StringVar()
        self.feed_qty = tk.StringVar()

        tk.Entry(self.feed_tab, textvariable=self.feed_date).grid(column=1, row=0)
        tk.Entry(self.feed_tab, textvariable=self.feed_qty).grid(column=1, row=1)

        tk.Button(self.feed_tab, text="Save Feed Entry", command=self.save_feed).grid(column=1, row=2, pady=10)

    def save_feed(self):
        data = [self.feed_date.get(), self.feed_qty.get()]
        with open("feed.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(data)
        messagebox.showinfo("Saved", "Feed record saved successfully")

    def setup_egg_tab(self):
        ttk.Label(self.egg_tab, text="Date").grid(column=0, row=0, padx=10, pady=10)
        ttk.Label(self.egg_tab, text="Eggs Collected").grid(column=0, row=1, padx=10)

        self.egg_date = tk.StringVar()
        self.egg_count = tk.StringVar()

        tk.Entry(self.egg_tab, textvariable=self.egg_date).grid(column=1, row=0)
        tk.Entry(self.egg_tab, textvariable=self.egg_count).grid(column=1, row=1)

        tk.Button(self.egg_tab, text="Save Egg Entry", command=self.save_eggs).grid(column=1, row=2, pady=10)

    def save_eggs(self):
        data = [self.egg_date.get(), self.egg_count.get()]
        with open("eggs.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(data)
        messagebox.showinfo("Saved", "Egg record saved successfully")

if __name__ == '__main__':
    root = tk.Tk()
    app = PoultryApp(root)
    root.mainloop()
