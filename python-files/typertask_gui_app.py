
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

def convert_to_typertask(text, trigger="F6::"):
    lines = text.strip().splitlines()
    output_lines = [trigger]
    for line in lines:
        escaped = line.replace("{", "{{}").replace("}", "{}}")
        output_lines.append(f"SendInput {escaped}{{Enter}}")
    output_lines.append("Return")
    return "\n".join(output_lines)

def convert():
    text = input_text.get("1.0", tk.END)
    if not text.strip():
        messagebox.showwarning("Empty Input", "Please enter some text.")
        return
    result = convert_to_typertask(text)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, result)

def copy_to_clipboard():
    result = output_text.get("1.0", tk.END)
    root.clipboard_clear()
    root.clipboard_append(result)
    messagebox.showinfo("Copied", "Converted text copied to clipboard.")

def save_to_file():
    result = output_text.get("1.0", tk.END)
    if not result.strip():
        messagebox.showwarning("No Output", "Nothing to save.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result)
        messagebox.showinfo("Saved", f"File saved to {file_path}")

root = tk.Tk()
root.title("TyperTask Code Converter")

tk.Label(root, text="Paste your code or paragraph:").pack(anchor='w', padx=10, pady=(10, 0))
input_text = scrolledtext.ScrolledText(root, height=12, width=80)
input_text.pack(padx=10, pady=5)

tk.Button(root, text="Convert to TyperTask", command=convert).pack(pady=5)

tk.Label(root, text="TyperTask Output:").pack(anchor='w', padx=10, pady=(10, 0))
output_text = scrolledtext.ScrolledText(root, height=12, width=80)
output_text.pack(padx=10, pady=5)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)
tk.Button(button_frame, text="Copy to Clipboard", command=copy_to_clipboard).pack(side=tk.LEFT, padx=10)
tk.Button(button_frame, text="Save as .txt", command=save_to_file).pack(side=tk.LEFT, padx=10)

root.mainloop()
