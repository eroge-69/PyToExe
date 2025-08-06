import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import subprocess
import re
import os

HIGHLIGHT_WORDS = {
    "print": "#C586C0", "input": "#FFD700",
    "if": "#C586C0", "else": "#C586C0", "elif": "#C586C0",
    "True": "#569CD6", "False": "#569CD6", "None": "#569CD6"
}

class LeatherCodeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LEATHER CODE ORG")
        self.geometry("900x550")
        self.configure(bg="#1e1e1e")
        self.button_color = "#32CD32"  # Default green
        self.create_main_menu()

    def create_main_menu(self):
        self.clear_window()

        tk.Label(self, text="LEATHER CODE ORG V0.01", font=("Segoe UI", 20, "bold"),
                 bg="#1e1e1e", fg="white").pack(pady=30)

        style = self.button_style()

        tk.Button(self, text="Start Coding", command=self.open_editor, **style).pack(pady=10)
        tk.Button(self, text="Theme", command=self.open_theme_menu, **style).pack(pady=10)
        tk.Button(self, text="Exit", command=self.quit, **style).pack(pady=10)

    def open_theme_menu(self):
        self.clear_window()

        tk.Label(self, text="Choose Theme", font=("Segoe UI", 18, "bold"),
                 bg="#1e1e1e", fg="white").pack(pady=20)

        themes = {
            "Blue": "#1E90FF",
            "Green": "#32CD32",
            "Pink": "#FF69B4",
            "White": "#F0F0F0"
        }

        for name, color in themes.items():
            tk.Button(self, text=name, command=lambda c=color: self.set_theme(c),
                      font=("Segoe UI", 14, "bold"), bg=color, fg="black",
                      activebackground=color, activeforeground="white",
                      bd=0, relief="flat", width=20, height=2).pack(pady=5)

        tk.Button(self, text="Back", command=self.create_main_menu, **self.button_style()).pack(pady=20)

    def set_theme(self, color):
        self.button_color = color
        messagebox.showinfo("Theme", f"Theme set to {color}")
        self.create_main_menu()

    def button_style(self):
        return {
            "font": ("Segoe UI", 14, "bold"),
            "bg": self.button_color,
            "fg": "white",
            "activebackground": self.button_color,
            "activeforeground": "white",
            "bd": 0,
            "relief": "flat",
            "width": 20,
            "height": 2
        }

    def open_editor(self):
        self.clear_window()

        toolbar = tk.Frame(self, bg="#1e1e1e")
        toolbar.pack(side=tk.TOP, fill=tk.X)

        style = {
            "font": ("Segoe UI", 10, "bold"),
            "bg": self.button_color,
            "fg": "white",
            "activebackground": self.button_color,
            "activeforeground": "white",
            "bd": 0,
            "relief": "flat",
            "width": 12,
            "height": 1
        }

        buttons = [
            ("Copy", self.copy_text), ("Paste", self.paste_text),
            ("Select All", self.select_all_text), ("Undo", self.undo_action),
            ("Save", self.save_file), ("Run", self.run_code),
            ("Import .py File", self.import_py_file), ("Back", self.create_main_menu)
        ]

        for text, cmd in buttons[:-1]:
            tk.Button(toolbar, text=text, command=cmd, **style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="Back", command=buttons[-1][1], **style).pack(side=tk.RIGHT, padx=5, pady=5)

        self.editor = ScrolledText(self, font=("Consolas", 14), undo=True,
                                   bg="#1e1e1e", fg="white", insertbackground="white")
        self.editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.editor.bind("<KeyRelease>", lambda e: self.highlight_syntax())
        self.highlight_syntax()

    def run_code(self):
        code = self.editor.get("1.0", "end-1c")
        temp_file = "temp_run.py"

        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            if os.name == "nt":
                subprocess.Popen(f'start cmd /k python {temp_file}', shell=True)
            else:
                subprocess.Popen(["x-terminal-emulator", "-e", f"python3 {temp_file}"])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def import_py_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", content)
            self.highlight_syntax()

    def copy_text(self):
        try:
            selected = self.editor.get("sel.first", "sel.last")
            self.clipboard_clear()
            self.clipboard_append(selected)
        except tk.TclError:
            pass

    def paste_text(self):
        try:
            self.editor.insert("insert", self.clipboard_get())
        except tk.TclError:
            pass

    def select_all_text(self):
        self.editor.tag_add("sel", "1.0", "end")

    def undo_action(self):
        try:
            self.editor.edit_undo()
        except:
            pass

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py",
                                                 filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.editor.get("1.0", "end-1c"))

    def highlight_syntax(self):
        content = self.editor.get("1.0", tk.END)
        for tag in self.editor.tag_names():
            self.editor.tag_remove(tag, "1.0", tk.END)

        for word, color in HIGHLIGHT_WORDS.items():
            self.editor.tag_config(word, foreground=color)
            pattern = r'(?<!\w)' + re.escape(word) + r'(?!\w)'
            for match in re.finditer(pattern, content):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.editor.tag_add(word, start, end)

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = LeatherCodeApp()
    app.mainloop()
