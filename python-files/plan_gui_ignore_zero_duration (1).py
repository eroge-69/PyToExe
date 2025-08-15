# Modifying the script so that it ignores plans with 0 minutes duration in the strategy combination generation

file_path = "/mnt/data/plan_gui_ignore_zero_duration.py"

code = '''\
import tkinter as tk
from tkinter import messagebox
import csv

def main():
    def parse_pace(text):
        if ':' in text:
            m, s = map(float, text.split(':'))
            return m * 60 + s
        return float(text)

    def calculate_plan(i):
        try:
            pace = parse_pace(pace_entries[i].get())
            fuel = float(fuel_entries[i].get())
            mode = plan_modes[i].get()
            if mode == "Fuel-based":
                tank = float(tank_entries[i].get())
                duration = (tank / fuel) * pace / 60
                duration_vars[i].set(f"{duration:.2f}")
                param_labels[i].config(text=f"{duration:.2f} min from tank")
            elif mode == "Time-based":
                dur = float(duration_entries[i].get())
                laps = (dur * 60) / pace
                fuel_needed = laps * fuel
                param_labels[i].config(text=f"{fuel_needed:.2f} L for {dur} min")
        except Exception as e:
            messagebox.showerror("Error", f"Plan {chr(65+i)} error: {e}")

    def toggle_fields(i):
        mode = plan_modes[i].get()
        if mode == "Fuel-based":
            tank_entries[i].grid()
            tank_labels[i].grid()
            duration_entries[i].grid_remove()
            duration_labels[i].grid_remove()
        elif mode == "Time-based":
            duration_entries[i].grid()
            duration_labels[i].grid()
            tank_entries[i].grid_remove()
            tank_labels[i].grid_remove()

    def bind_toggle(index):
        return lambda *args: toggle_fields(index)

    def calculate():
        try:
            max_reps = int(entry_max_reps.get())
            base_total = float(entry_base_total.get())
            allowance_percent = float(entry_allowance_percent.get())
            long_pit_duration = float(entry_long_pit.get())
            normal_pit_duration = float(entry_normal_pit.get())
            long_pit_count = int(entry_long_pit_count.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid global input")
            return

        min_total = base_total * (1 - allowance_percent / 100)
        max_total = base_total * (1 + allowance_percent / 100)

        plan_durations = []
        valid_indices = []

        for i in range(6):
            try:
                mode = plan_modes[i].get()
                pace = parse_pace(pace_entries[i].get())
                fuel = float(fuel_entries[i].get())
                if mode == "Fuel-based":
                    tank = float(tank_entries[i].get())
                    dur = (tank / fuel) * pace / 60
                else:
                    dur = float(duration_entries[i].get())
                if dur > 0:
                    plan_durations.append(dur)
                    valid_indices.append(i)
                    param_labels[i].config(text=f"{mode} | Dur: {dur:.2f}m")
                else:
                    param_labels[i].config(text=f"IGNORED (0 min)")
            except Exception as e:
                messagebox.showerror("Error", f"Error in Plan {chr(65+i)}: {e}")
                return

        combinations = []

        def generate(depth, current):
            if depth == len(plan_durations):
                total_plans = sum(current)
                if total_plans >= long_pit_count + 1:
                    normal_pits = total_plans - long_pit_count - 1
                    plan_time = sum([current[i] * plan_durations[i] for i in range(len(plan_durations))])
                    total_time = plan_time + normal_pits * normal_pit_duration + long_pit_count * long_pit_duration
                    if min_total <= total_time <= max_total:
                        row = [0] * 6
                        for idx, val in zip(valid_indices, current):
                            row[idx] = val
                        combinations.append(row + [normal_pits, long_pit_count, normal_pits + long_pit_count, total_time])
                return
            for i in range(max_reps + 1):
                generate(depth + 1, current + [i])

        generate(0, [])

        with open("plan_output.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Plan A", "Plan B", "Plan C", "Plan D", "Plan E", "Plan F", "Normal Pits", "Long Pits", "Total Pits", "Total Time"])
            for row in combinations:
                writer.writerow(row)

        messagebox.showinfo("Done", f"{len(combinations)} combinations written to plan_output.csv")

    root = tk.Tk()
    root.title("Strategy Planner - Ignore Zero Duration")
    root.geometry("500x800")

    plan_labels = ['A', 'B', 'C', 'D', 'E', 'F']
    plan_modes, pace_entries, fuel_entries = [], [], []
    tank_entries, duration_entries = [], []
    tank_labels, duration_labels, param_labels = [], [], []
    duration_vars = []

    for col, label in enumerate(plan_labels):
        tk.Label(root, text=f"Plan {label}", font=('Arial', 10, 'bold')).grid(row=10, column=col+1, pady=(10, 0))

        mode = tk.StringVar(value="Fuel-based")
        dropdown = tk.OptionMenu(root, mode, "Fuel-based", "Time-based")
        dropdown.grid(row=11, column=col+1)
        plan_modes.append(mode)

        tk.Label(root, text="Pace").grid(row=12, column=0)
        pace = tk.Entry(root, width=8); pace.insert(0, "90"); pace.grid(row=12, column=col+1)
        pace_entries.append(pace)

        tk.Label(root, text="Fuel/Lap").grid(row=13, column=0)
        fuel = tk.Entry(root, width=8); fuel.insert(0, "2.5"); fuel.grid(row=13, column=col+1)
        fuel_entries.append(fuel)

        tank_lbl = tk.Label(root, text="Tank")
        tank_lbl.grid(row=14, column=0)
        tank = tk.Entry(root, width=8); tank.insert(0, "100"); tank.grid(row=14, column=col+1)
        tank_labels.append(tank_lbl)
        tank_entries.append(tank)

        dur_lbl = tk.Label(root, text="Duration")
        dur_lbl.grid(row=15, column=0)
        duration_labels.append(dur_lbl)
        dur = tk.Entry(root, width=8); dur.insert(0, "80"); dur.grid(row=15, column=col+1)
        duration_entries.append(dur)
        duration_vars.append(tk.StringVar())

        btn = tk.Button(root, text="Calc", command=lambda i=col: calculate_plan(i))
        btn.grid(row=16, column=col+1)

        info = tk.Label(root, text="Info: N/A", anchor='w')
        info.grid(row=17, column=col+1, sticky='w')
        param_labels.append(info)

        mode.trace_add("write", bind_toggle(col))
        toggle_fields(col)

    row = 0
    tk.Label(root, text="Global Strategy Settings", font=('Arial', 11, 'bold')).grid(row=row, column=0, columnspan=2, pady=10)
    row += 1

    def add_input(label, default):
        nonlocal row
        tk.Label(root, text=label).grid(row=row, column=0)
        entry = tk.Entry(root)
        entry.insert(0, str(default))
        entry.grid(row=row, column=1)
        row += 1
        return entry

    entry_max_reps = add_input("Max Repetitions", 8)
    entry_base_total = add_input("Target Total Time", 480)
    entry_allowance_percent = add_input("Allowance ± (%)", 5)
    entry_long_pit = add_input("Long Pit Duration", 3.5)
    entry_normal_pit = add_input("Normal Pit Duration", 0.86)
    entry_long_pit_count = add_input("Long Pit Count", 3)

    tk.Button(root, text="Generate Strategy CSV", command=calculate).grid(row=row, column=0, columnspan=2, pady=10)
    row += 1
    tk.Button(root, text="Close", command=root.quit).grid(row=row, column=0, columnspan=2)

    root.mainloop()

if __name__ == "__main__":
    main()
'''

with open(file_path, 'w') as f:
    f.write(code)

file_path
