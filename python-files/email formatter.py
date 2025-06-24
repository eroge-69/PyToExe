import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class EmailFormatterTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Formatter Tool")
        self.root.geometry("500x400")
        self.root.configure(bg="#1c1b2f")

        # Select file
        tk.Label(root, text="📂 Select Email List File:", fg="white", bg="#1c1b2f").pack(pady=5)
        self.file_entry = tk.Entry(root, width=50)
        self.file_entry.pack()
        tk.Button(root, text="Browse", bg="green", fg="white", command=self.browse_file).pack(pady=5)

        # Emails per line
        tk.Label(root, text="📋 Emails per line:", fg="white", bg="#1c1b2f").pack(pady=5)
        self.per_line_entry = tk.Entry(root, width=10)
        self.per_line_entry.pack()

        # Format button
        tk.Button(root, text="🛠 Format Emails", bg="green", fg="white", command=self.format_emails).pack(pady=10)

        # Logs
        tk.Label(root, text="📄 Logs:", fg="white", bg="#1c1b2f").pack()
        self.log_box = scrolledtext.ScrolledText(root, width=60, height=10)
        self.log_box.pack()

    def browse_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, filepath)

    def format_emails(self):
        filepath = self.file_entry.get()
        try:
            emails_per_line = int(self.per_line_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for emails per line.")
            return

        if not filepath:
            messagebox.showwarning("No File", "Please select an email list file.")
            return

        try:
            with open(filepath, "r") as f:
                emails = [line.strip() for line in f if line.strip()]

            formatted_lines = []
            for i in range(0, len(emails), emails_per_line):
                formatted_lines.append(", ".join(emails[i:i + emails_per_line]))

            output_path = filepath.replace(".txt", "_formatted.txt")
            with open(output_path, "w") as f:
                f.write("\n".join(formatted_lines))

            self.log_box.insert(tk.END, f"✔ Success! Output saved to:\n{output_path}\n\n")
        except Exception as e:
            self.log_box.insert(tk.END, f"❌ Error: {str(e)}\n")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = EmailFormatterTool(root)
    root.mainloop()
