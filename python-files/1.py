import tkinter as tk
from tkinter import ttk
import math

def calculate():
    try:
        # Get yesterday and today values
        yesterday_values = [float(entries[col][0].get()) for col in columns]
        today_values = [float(entries[col][1].get()) for col in columns]
        
        # Calculate sums
        sum_yesterday = sum(yesterday_values)
        sum_today = sum(today_values)
        total_diff = sum_today - sum_yesterday
        
        # Calculate specific differences
        gai_diff = (today_values[0] - yesterday_values[0]) / 1000
        derzhiv_diff = (today_values[1] - yesterday_values[1]) / 1000
        pukenychi_diff = ((today_values[2] + today_values[7]) - (yesterday_values[2] + yesterday_values[7])) / 1000
        lubeshiv_diff = (today_values[3] - yesterday_values[3]) / 1000
        letnya_diff = ((today_values[4] + today_values[5]) - (yesterday_values[4] + yesterday_values[5])) / 1000
        dashava_diff = (today_values[6] - yesterday_values[6]) / 1000
        
        # Prepare results
        results = [
            f"Suma sogodni: {round(sum_today/1000, 1)}",
            f"Suma vchora: {round(sum_yesterday/1000, 1)}",
            f"Riznytsya: {round((sum_today - sum_yesterday)/1000, 3)}",
            "",
            "Riznytsi:"
        ]
        
        # Add negative differences
        if gai_diff < 0:
            results.append(f"Гаї різниця: {round(gai_diff, 3)}")
        if derzhiv_diff < 0:
            results.append(f"Держів різниця: {round(derzhiv_diff, 3)}")
        if pukenychi_diff < 0:
            results.append(f"Пукеничі різниця: {round(pukenychi_diff, 3)}")
        if lubeshiv_diff < 0:
            results.append(f"Любешів різниця: {round(lubeshiv_diff, 3)}")
        if letnya_diff < 0:
            results.append(f"Летня різниця: {round(letnya_diff, 3)}")
        if dashava_diff < 0:
            results.append(f"Дашава різниця: {round(dashava_diff, 3)}")
        
        # Show results
        result_text = "\n".join(results)
        result_label.config(text=result_text)
        
        # Create copyable text
        copyable_text = "\n".join([line for line in results if line and not line.startswith("Riznytsi")])
        copy_button.config(command=lambda: root.clipboard_clear() or root.clipboard_append(copyable_text))
        
    except ValueError:
        result_label.config(text="Будь ласка, введіть коректні числові значення у всі поля")

# Create main window
root = tk.Tk()
root.title("Розрахунок різниць")
root.geometry("1000x600")

# Columns
columns = ["Гаї", "Держів", "Луги", "Любешів", "1000", "500", "Дашава", "Миколаїв"]
rows = ["Вчора", "Сьогодні"]

# Create entries
entries = {}
for i, col in enumerate(columns):
    frame = ttk.Frame(root)
    frame.grid(row=0, column=i, padx=5, pady=5)
    
    label = ttk.Label(frame, text=col)
    label.pack()
    
    col_entries = []
    for row in rows:
        entry_frame = ttk.Frame(frame)
        entry_frame.pack(pady=2)
        
        row_label = ttk.Label(entry_frame, text=row)
        row_label.pack(side=tk.LEFT)
        
        entry = ttk.Entry(entry_frame, width=8)
        entry.pack(side=tk.LEFT)
        col_entries.append(entry)
    
    entries[col] = col_entries

# Calculate button
calculate_button = ttk.Button(root, text="Розрахувати", command=calculate)
calculate_button.grid(row=1, column=0, columnspan=len(columns), pady=10)

# Result label
result_label = ttk.Label(root, text="", justify=tk.LEFT)
result_label.grid(row=2, column=0, columnspan=len(columns), pady=10)

# Copy button
copy_button = ttk.Button(root, text="Копіювати результати")
copy_button.grid(row=3, column=0, columnspan=len(columns), pady=5)

root.mainloop()