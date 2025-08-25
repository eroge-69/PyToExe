import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dragon Timer")

        self.timers = []
        for i in range(19):
            self.create_timer(i)

        # Calculate All button
        calc_all_btn = ttk.Button(self.root, text="Calculate All", command=self.calculate_all)
        calc_all_btn.grid(row=20, column=0, pady=10, sticky="w")

    def create_timer(self, index):
        frame = ttk.Frame(self.root, padding=5)
        frame.grid(row=index, column=0, sticky="w")

        # Timer name (editable)
        name_var = tk.StringVar(value=f"Timer {index+1}")
        name_entry = ttk.Entry(frame, textvariable=name_var, width=15)
        name_entry.grid(row=0, column=0)

        # Input time
        input_var = tk.StringVar()
        input_entry = ttk.Entry(frame, textvariable=input_var, width=10)
        input_entry.grid(row=0, column=1)
        input_entry.insert(0, "1:00 PM")

        # Hours to add
        add_var = tk.IntVar(value=1)
        add_entry = ttk.Entry(frame, textvariable=add_var, width=5)
        add_entry.grid(row=0, column=2)

        # Result label
        result_var = tk.StringVar(value="Result: --")
        result_label = ttk.Label(frame, textvariable=result_var, width=15)
        result_label.grid(row=0, column=3)

        # Calculate button
        def calculate():
            self.calculate_single(input_var, add_var, result_var)

        calc_button = ttk.Button(frame, text="=", command=calculate, width=3)
        calc_button.grid(row=0, column=4, padx=(4, 2))

        # Reset button
        def reset():
            name_var.set(f"Timer {index+1}")
            input_var.set("1:00 PM")
            add_var.set(1)
            result_var.set("Result: --")

        reset_button = ttk.Button(frame, text="Reset", command=reset)
        reset_button.grid(row=0, column=5, padx=(2, 0))

        self.timers.append({
            "name": name_var,
            "input": input_var,
            "add": add_var,
            "result": result_var
        })

    def calculate_single(self, input_var, add_var, result_var):
        try:
            input_time = datetime.strptime(input_var.get(), "%I:%M %p")
            added_time = input_time + timedelta(hours=add_var.get())
            result_var.set(added_time.strftime("%I:%M %p"))
        except ValueError:
            result_var.set("Invalid Time")

    def calculate_all(self):
        for t in self.timers:
            self.calculate_single(t["input"], t["add"], t["result"])

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
