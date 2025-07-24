import tkinter as tk
from tkinter import messagebox

class CompositionCalculator:
    def __init__(self, master):
        self.master = master
        master.title("Combined Composition Calculator")
        master.geometry("400x400")
        master.config(bg="#e0f7fa")

        self.fibers = []

        self.title_label = tk.Label(master, text="Textile Composition Calculator", font=("Arial", 14, "bold"), bg="#e0f7fa")
        self.title_label.pack(pady=10)

        self.name_label = tk.Label(master, text="Fiber Name:", bg="#e0f7fa")
        self.name_label.pack()

        self.name_entry = tk.Entry(master)
        self.name_entry.pack()

        self.weight_label = tk.Label(master, text="Weight (grams):", bg="#e0f7fa")
        self.weight_label.pack()

        self.weight_entry = tk.Entry(master)
        self.weight_entry.pack()

        self.add_button = tk.Button(master, text="Add Fiber", command=self.add_fiber, bg="#4caf50", fg="white")
        self.add_button.pack(pady=10)

        self.calculate_button = tk.Button(master, text="Calculate Composition", command=self.calculate_composition, bg="#2196f3", fg="white")
        self.calculate_button.pack(pady=10)

        self.result_text = tk.Text(master, height=10, width=40)
        self.result_text.pack(pady=10)

    def add_fiber(self):
        name = self.name_entry.get()
        try:
            weight = float(self.weight_entry.get())
            if weight <= 0:
                raise ValueError
            self.fibers.append((name, weight))
            self.result_text.insert(tk.END, f"{name} - {weight}g added.\n")
            self.name_entry.delete(0, tk.END)
            self.weight_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid weight (positive number).")

    def calculate_composition(self):
        self.result_text.insert(tk.END, "\n--- Composition Result ---\n")
        total_weight = sum(weight for _, weight in self.fibers)
        if total_weight == 0:
            messagebox.showerror("Error", "No fibers added.")
            return
        for name, weight in self.fibers:
            percent = (weight / total_weight) * 100
            self.result_text.insert(tk.END, f"{name}: {percent:.2f}%\n")
        self.fibers.clear()

if __name__ == "__main__":
    root = tk.Tk()
    app = CompositionCalculator(root)
    root.mainloop()
