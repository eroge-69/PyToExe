import tkinter as tk

def evaluate_expression():
    try:
        result = eval(entry.get())
        result_label.config(text=f"Ergebnis: {result}")
    except Exception:
        result_label.config(text="Fehler im Ausdruck")

root = tk.Tk()
root.title("Einfacher Taschenrechner")

entry = tk.Entry(root, width=30, font=("Arial", 14))
entry.pack(pady=10)

calculate_button = tk.Button(root, text="Berechnen", command=evaluate_expression, font=("Arial", 12))
calculate_button.pack(pady=5)

result_label = tk.Label(root, text="Ergebnis: ", font=("Arial", 14))
result_label.pack(pady=10)

root.mainloop()
