
import tkinter as tk
from tkinter import messagebox

def calculate():
    try:
        from_val = entry_from.get()
        is_val = entry_is.get()
        diff_val = entry_diff.get()
        percent_val = entry_percent.get()

        values = {
            'from': float(from_val) if from_val else None,
            'is': float(is_val) if is_val else None,
            'diff': float(diff_val) if diff_val else None,
            'percent': float(percent_val) if percent_val else None
        }

        filled = [k for k, v in values.items() if v is not None]

        if len(filled) != 2:
            messagebox.showerror("Fel", "Ange exakt två värden för att beräkna de andra.")
            return

        if values['from'] is not None and values['is'] is not None:
            values['diff'] = values['is'] - values['from']
            values['percent'] = (values['diff'] / values['from']) * 100
        elif values['from'] is not None and values['diff'] is not None:
            values['is'] = values['from'] + values['diff']
            values['percent'] = (values['diff'] / values['from']) * 100
        elif values['from'] is not None and values['percent'] is not None:
            values['diff'] = values['from'] * (values['percent'] / 100)
            values['is'] = values['from'] + values['diff']
        elif values['is'] is not None and values['diff'] is not None:
            values['from'] = values['is'] - values['diff']
            values['percent'] = (values['diff'] / values['from']) * 100
        elif values['is'] is not None and values['percent'] is not None:
            values['from'] = values['is'] / (1 + values['percent'] / 100)
            values['diff'] = values['is'] - values['from']
        elif values['diff'] is not None and values['percent'] is not None:
            values['from'] = values['diff'] / (values['percent'] / 100)
            values['is'] = values['from'] + values['diff']

        entry_from.delete(0, tk.END)
        entry_from.insert(0, f"{values['from']:.2f}")
        entry_is.delete(0, tk.END)
        entry_is.insert(0, f"{values['is']:.2f}")
        entry_diff.delete(0, tk.END)
        entry_diff.insert(0, f"{values['diff']:.2f}")
        entry_percent.delete(0, tk.END)
        entry_percent.insert(0, f"{values['percent']:.2f}")

    except Exception as e:
        messagebox.showerror("Fel", f"Ett fel uppstod: {e}")

root = tk.Tk()
root.title("Procentberäkning")

tk.Label(root, text="From:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_from = tk.Entry(root)
entry_from.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Is:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_is = tk.Entry(root)
entry_is.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Skillnad:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_diff = tk.Entry(root)
entry_diff.grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="Procentuell ökning:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
entry_percent = tk.Entry(root)
entry_percent.grid(row=3, column=1, padx=5, pady=5)

tk.Button(root, text="Beräkna", command=calculate).grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
