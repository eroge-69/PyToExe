import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, scrolledtext
import os
import shutil
import subprocess
import sys
import random

FILESDIR = "DominikOS_files"

class SnakeGame:
    def __init__(self, master):
        self.win = tk.Toplevel(master)
        self.win.title("Snake")
        self.win.resizable(False, False)

        self.width = 400
        self.height = 400
        self.cell_size = 20
        self.cols = self.width // self.cell_size
        self.rows = self.height // self.cell_size

        self.canvas = tk.Canvas(self.win, width=self.width, height=self.height, bg="black")
        self.canvas.pack()

        self.direction = "Right"
        self.snake = [(self.cols//2, self.rows//2)]
        self.food = None
        self.game_over = False

        self.score = 0

        self.win.bind("<Key>", self.change_direction)
        self.win.focus_set()

        self.place_food()
        self.draw()
        self.move_snake()

    def place_food(self):
        while True:
            x = random.randint(0, self.cols - 1)
            y = random.randint(0, self.rows - 1)
            if (x, y) not in self.snake:
                self.food = (x, y)
                break

    def draw(self):
        self.canvas.delete("all")
        # Snake
        for x, y in self.snake:
            x1 = x * self.cell_size
            y1 = y * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="lime", outline="")

        # Food
        if self.food:
            x, y = self.food
            x1 = x * self.cell_size
            y1 = y * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_oval(x1, y1, x2, y2, fill="red", outline="")

        # Score
        self.canvas.create_text(50, 10, fill="white", text=f"Score: {self.score}", anchor="nw", font=("Arial", 14))

    def move_snake(self):
        if self.game_over:
            return

        head_x, head_y = self.snake[0]

        if self.direction == "Left":
            new_head = (head_x - 1, head_y)
        elif self.direction == "Right":
            new_head = (head_x + 1, head_y)
        elif self.direction == "Up":
            new_head = (head_x, head_y - 1)
        else:  # Down
            new_head = (head_x, head_y + 1)

        # Check collisions
        if (new_head in self.snake or
            new_head[0] < 0 or new_head[0] >= self.cols or
            new_head[1] < 0 or new_head[1] >= self.rows):
            self.game_over = True
            self.canvas.create_text(self.width//2, self.height//2, fill="red", font=("Arial", 30), text="GAME OVER")
            # Zamknij okno po 2 sekundach
            self.win.after(2000, self.win.destroy)
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.place_food()
        else:
            self.snake.pop()

        self.draw()
        self.win.after(150, self.move_snake)

    def change_direction(self, event):
        key = event.keysym
        opposites = {"Left": "Right", "Right": "Left", "Up": "Down", "Down": "Up"}
        if key in ["Left", "Right", "Up", "Down"]:
            if opposites[key] != self.direction:  # nie można zawrócić o 180 stopni
                self.direction = key


class DominikOS:
    def __init__(self, root):
        self.root = root
        self.root.title("DominikOS")
        self.root.geometry("900x600")
        self.root.configure(bg="black")

        if not os.path.exists(FILESDIR):
            os.makedirs(FILESDIR)

        self.current_dir = FILESDIR
        self.files = []
        self.load_files()

        self.desktop_frame = tk.Frame(root, bg="black")
        self.desktop_frame.pack(fill=tk.BOTH, expand=True)

        self.system_label = tk.Label(self.desktop_frame, text="DominikOS", fg="white", bg="black", font=("Arial", 48))
        self.system_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        self.files_frame = tk.Frame(self.desktop_frame, bg="black")
        self.files_frame.pack(pady=10)

        self.taskbar = tk.Frame(root, bg="gray20", height=40)
        self.taskbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.build_taskbar()
        self.update_file_view()

    def load_files(self):
        self.files = []
        for f in os.listdir(self.current_dir):
            path = os.path.join(self.current_dir, f)
            if os.path.isfile(path):
                self.files.append(f)

    def build_taskbar(self):
        apps = [
            ("Notepad", self.open_notepad),
            ("Terminal", self.open_terminal),
            ("Import File", self.import_file),
            ("Create File", self.create_file),
            ("Snake", self.open_snake),
            ("Refresh", self.refresh_files)
        ]
        for (text, cmd) in apps:
            btn = tk.Button(self.taskbar, text=text, bg="gray30", fg="white", command=cmd)
            btn.pack(side=tk.LEFT, padx=4, pady=4)

    def refresh_files(self):
        self.load_files()
        self.update_file_view()

    def update_file_view(self):
        for widget in self.files_frame.winfo_children():
            widget.destroy()

        for filename in self.files:
            file_frame = tk.Frame(self.files_frame, bg="black")
            file_frame.pack(anchor='w', fill=tk.X)

            lbl = tk.Label(file_frame, text=filename, fg="white", bg="black", font=("Arial", 12))
            lbl.pack(side=tk.LEFT, padx=5)

            btn_open = tk.Button(file_frame, text="Open", command=lambda f=filename: self.open_file(f))
            btn_open.pack(side=tk.LEFT, padx=5)

            btn_rename = tk.Button(file_frame, text="Rename", command=lambda f=filename: self.rename_file(f))
            btn_rename.pack(side=tk.LEFT, padx=5)

            btn_delete = tk.Button(file_frame, text="Delete", command=lambda f=filename: self.delete_file(f))
            btn_delete.pack(side=tk.LEFT, padx=5)

    def open_file(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        fullpath = os.path.join(self.current_dir, filename)
        if ext == ".txt" or ext == ".py" or ext == ".exe":
            self.open_text_file(fullpath, filename)
        else:
            messagebox.showinfo("Open File", f"Cannot open file type {ext}")

    def open_text_file(self, filepath, filename):
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("")

        editor = tk.Toplevel(self.root)
        editor.title(f"Editor - {filename}")
        editor.geometry("600x400")

        text = scrolledtext.ScrolledText(editor, undo=True)
        text.pack(fill=tk.BOTH, expand=True)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                text.insert("1.0", content)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot read file: {e}")

        def save():
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(text.get("1.0", tk.END))
                messagebox.showinfo("Saved", f"File '{filename}' saved.")
                editor.destroy()
                self.refresh_files()
            except Exception as e:
                messagebox.showerror("Error", f"Cannot save file: {e}")

        btn_save = tk.Button(editor, text="Save", command=save, bg="#333333", fg="white")
        btn_save.pack(side=tk.BOTTOM, fill=tk.X)

    def import_file(self):
        path = filedialog.askopenfilename()
        if path:
            try:
                dest = os.path.join(self.current_dir, os.path.basename(path))
                if os.path.exists(dest):
                    if not messagebox.askyesno("Overwrite?", f"File '{os.path.basename(path)}' exists. Overwrite?"):
                        return
                shutil.copy2(path, dest)
                self.refresh_files()
            except Exception as e:
                messagebox.showerror("Error", f"Cannot import file: {e}")

    def create_file(self):
        name = simpledialog.askstring("Create File", "Enter file name (with extension):")
        if not name:
            return
        path = os.path.join(self.current_dir, name)
        if os.path.exists(path):
            messagebox.showerror("Error", "File already exists.")
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
            self.refresh_files()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot create file: {e}")

    def rename_file(self, filename):
        newname = simpledialog.askstring("Rename File", "Enter new name:", initialvalue=filename)
        if not newname or newname == filename:
            return
        oldpath = os.path.join(self.current_dir, filename)
        newpath = os.path.join(self.current_dir, newname)
        if os.path.exists(newpath):
            messagebox.showerror("Error", "File with that name already exists.")
            return
        try:
            os.rename(oldpath, newpath)
            self.refresh_files()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot rename file: {e}")

    def delete_file(self, filename):
        if messagebox.askyesno("Delete File", f"Delete '{filename}'?"):
            try:
                os.remove(os.path.join(self.current_dir, filename))
                self.refresh_files()
            except Exception as e:
                messagebox.showerror("Error", f"Cannot delete file: {e}")

    def open_terminal(self):
        term = tk.Toplevel(self.root)
        term.title("Terminal")
        term.geometry("700x400")

        output = scrolledtext.ScrolledText(term, bg="black", fg="white", insertbackground="white")
        output.pack(fill=tk.BOTH, expand=True)

        input_box = tk.Entry(term, bg="black", fg="white", insertbackground="white")
        input_box.pack(fill=tk.X)

        def run_command():
            cmd = input_box.get().strip()
            output.insert(tk.END, f"> {cmd}\n")
            if cmd == "help":
                output.insert(tk.END, "Commands:\n - help\n - list\n - run file.py\n - off\n")
            elif cmd == "list":
                self.load_files()
                output.insert(tk.END, "\n".join(self.files) + "\n")
            elif cmd.startswith("run "):
                filename = cmd[4:].strip()
                filepath = os.path.join(self.current_dir, filename)
                if not os.path.exists(filepath):
                    output.insert(tk.END, f"File '{filename}' not found.\n")
                else:
                    if not filename.endswith(".py"):
                        output.insert(tk.END, "Only Python scripts (*.py) can be run.\n")
                    else:
                        try:
                            # Run python file and capture output/errors
                            proc = subprocess.Popen([sys.executable, filepath],
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                      text=True)
                           
                            out, err = proc.communicate(timeout=5)
                            if out:
                                output.insert(tk.END, out)
                            if err:
                                output.insert(tk.END, f"ERROR:\n{err}\n")
                        except Exception as e:
                            output.insert(tk.END, f"Exception: {e}\n")
            elif cmd.lower() == "off":
                output.insert(tk.END, "Shutting down DominikOS...\n")
                term.after(1000, self.root.destroy)
            else:
                output.insert(tk.END, f"Unknown command: {cmd}\n")

            output.see(tk.END)
            input_box.delete(0, tk.END)

        input_box.bind("<Return>", lambda e: run_command())

    def open_notepad(self):
        # Simplified notepad: just create a blank text file and open editor
        self.create_file()

    def open_snake(self):
        SnakeGame(self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = DominikOS(root)
    root.mainloop()
