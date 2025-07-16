import tkinter as tk
from tkinter import messagebox

def calculate_required_mdcat():
    try:
        matric = float(entry_matric.get())
        fsc = float(entry_fsc.get())
        target = float(entry_target.get())

        if not (0 <= matric <= 1100):
            raise ValueError("Matric marks must be between 0 and 1100.")
        if not (0 <= fsc <= 1200):
            raise ValueError("FSc marks must be between 0 and 1200.")
        if not (0 <= target <= 100):
            raise ValueError("Target aggregate must be between 0 and 100.")

        matric_part = (matric / 1100) * 10
        fsc_part = (fsc / 1200) * 40
        mdcat_required_percentage = target - matric_part - fsc_part

        if mdcat_required_percentage < 0:
            result_label.config(
                text="Target already achieved! 🟢", fg="green"
            )
            return
        elif mdcat_required_percentage > 50:
            result_label.config(
                text="Target is impossible with given scores. 🔴", fg="red"
            )
            return

        mdcat_required_marks = round((mdcat_required_percentage / 50) * 180, 2)
        result_label.config(
            text=f"Required MDCAT Marks: {mdcat_required_marks} / 180", fg="blue"
        )

    except ValueError as ve:
        messagebox.showerror("Invalid Input", str(ve))
    except Exception as e:
        messagebox.showerror("Error", "Something went wrong!")

def reset_fields():
    entry_matric.delete(0, tk.END)
    entry_fsc.delete(0, tk.END)
    entry_target.delete(0, tk.END)
    result_label.config(text="")

# GUI Setup
root = tk.Tk()
root.title("MDCAT Required Marks Calculator")
root.geometry("400x350")
root.resizable(False, False)

tk.Label(root, text="Matric Marks (out of 1100):").pack(pady=5)
entry_matric = tk.Entry(root)
entry_matric.pack()

tk.Label(root, text="FSc Marks (out of 1200):").pack(pady=5)
entry_fsc = tk.Entry(root)
entry_fsc.pack()

tk.Label(root, text="Target Aggregate (e.g., 91.00):").pack(pady=5)
entry_target = tk.Entry(root)
entry_target.pack()

tk.Button(root, text="Calculate", command=calculate_required_mdcat, bg="#4CAF50", fg="white").pack(pady=10)
tk.Button(root, text="Reset", command=reset_fields, bg="#f0ad4e").pack(pady=2)
tk.Button(root, text="Exit", command=root.quit, bg="#d9534f", fg="white").pack(pady=2)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=10)

root.mainloop()
