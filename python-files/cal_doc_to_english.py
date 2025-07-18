
import tkinter as tk
from tkinter import filedialog, messagebox
import re

class CalDocToEnglishApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CAL DOC to Plain English Converter")
        self.root.geometry("900x600")

        tk.Button(root, text="Load CAL DOC File", command=self.load_file).pack(pady=10)
        tk.Button(root, text="Save Output", command=self.save_output).pack(pady=5)

        self.text_box = tk.Text(root, wrap="word", font=("Courier", 10))
        self.text_box.pack(expand=True, fill="both", padx=10, pady=10)

        self.output_text = ""

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        english_lines = []
        for line in lines:
            if not line.strip() or line.startswith("#") or "Parameter Name" in line or "-" * 5 in line:
                continue

            match = re.match(r"\s*(\S+)\s+(\S+)\s+(\S+)?\s+0x[0-9A-Fa-f]+.*?([A-Za-z].*)", line)
            if match:
                name, value, unit, comment = match.groups()
                name_clean = name.strip("_").replace("_", " ").title()
                unit_str = f" {unit}" if unit and unit not in ["None", ""] else ""
                english_line = f"{name_clean}: {value}{unit_str} — {comment.strip()}"
                english_lines.append(english_line)

        self.output_text = "\n".join(english_lines)
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, self.output_text)

    def save_output(self):
        if not self.output_text:
            messagebox.showwarning("No Output", "Please load a CAL DOC file first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if path:
            with open(path, "w") as f:
                f.write(self.output_text)
            messagebox.showinfo("Saved", "Plain English output saved successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalDocToEnglishApp(root)
    root.mainloop()
