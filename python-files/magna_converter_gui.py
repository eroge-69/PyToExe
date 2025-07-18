
import tkinter as tk
from tkinter import scrolledtext

def convert_text():
    raw_input = input_text.get("1.0", tk.END).strip()
    model_mapping = {
        "F000": "Magna",
        "B800": "Lear"
    }

    result = []
    for line in raw_input.split('\n'):
        parts = line.strip().split()
        if len(parts) == 2:
            code, number = parts
            model = model_mapping.get(code, "Unknown")
            result.append(f"{number}\t{model}")

    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, "\n".join(result))

# GUI
root = tk.Tk()
root.title("Magna/Lear Converter")
root.geometry("600x500")

tk.Label(root, text="Paste Input Below:").pack()

input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=12)
input_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

tk.Button(root, text="Convert", command=convert_text).pack(pady=10)

tk.Label(root, text="Converted Output:").pack()

output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=12)
output_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

root.mainloop()
