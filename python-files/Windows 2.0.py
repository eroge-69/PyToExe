import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, colorchooser
import os
import webbrowser
from functools import partial  # Добавляем импорт partial

class Win(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Windows")
        self.geometry("800x600")
        self.configure(bg="#008080")
        
        self.fullscreen = False
        self.bind("<F11>", self.toggle_fullscreen)
        
        self.create_taskbar()
        self.create_start_menu()
        self.create_desktop_icons()

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)

    def create_taskbar(self):
        self.taskbar = tk.Frame(self, bg="#C0C0C0", height=30)
        self.taskbar.pack(side="bottom", fill="x")
        tk.Button(self.taskbar, text="Start", command=self.toggle_menu).pack(side="left", padx=5)

    def create_start_menu(self):
        self.menu = tk.Frame(self, bg="#E0E0E0", width=160)
        apps = [
            ("Command Prompt", self.cmd_prompt),
            ("Notepad", self.notepad),
            ("Paint", self.paint),
            ("Browser", self.open_browser),
            ("Explorer", self.explorer),
            ("Exit", self.quit)
        ]
        
        # Используем partial для правильной передачи команд
        for name, cmd in apps:
            tk.Button(self.menu, text=name, anchor="w", command=partial(cmd)).pack(fill="x")
            
        # Изначально меню скрыто
        self.menu.place_forget()

    def toggle_menu(self):
        if self.menu.winfo_ismapped():
            self.menu.place_forget()
        else:
            # Получаем текущую высоту окна
            height = self.winfo_height()
            # Высота меню (запрошенная)
            menu_height = self.menu.winfo_reqheight()
            # Высота панели задач
            taskbar_height = self.taskbar.winfo_height()
            # Размещаем меню снизу слева, над панелью задач
            self.menu.place(x=0, y=height - menu_height - taskbar_height)

    def create_desktop_icons(self):
        icons = [
            ("Командная строка", self.cmd_prompt, "🖥️"),
            ("Проводник", self.explorer, "🖥️"),
            ("Блокнот", self.notepad, "📄"),
            ("Paint", self.paint, "🎨"),
            ("Браузер", self.open_browser, "🌐")
        ]
        for i, (name, cmd, icon) in enumerate(icons):
            f = tk.Frame(self, bg="#008080")
            f.place(x=50, y=50 + i*90)
            tk.Label(f, text=icon, font=("Arial", 30), bg="#008080", fg="white").pack()
            tk.Button(f, text=name, bg="#008080", fg="white", bd=0, command=cmd).pack()

    def cmd_prompt(self):
        win = tk.Toplevel(self)
        win.title("Command Prompt")
        win.geometry("600x400")
        text = tk.Text(win, bg="black", fg="white", insertbackground="white")
        text.pack(fill="both", expand=True)
        prompt = "C:\\WINDOWS> "
        text.insert("end", prompt)
        text.focus_set()

        def on_enter(event):
            line_start = text.index("insert linestart + %dc" % len(prompt))
            line_end = text.index("insert lineend")
            cmd = text.get(line_start, line_end).strip()
            text.insert("end", "\n")
            if cmd.lower() == "exit":
                win.destroy()
            elif cmd.lower() == "cls":
                text.delete("1.0", "end")
            elif cmd.lower() == "dir":
                for f in os.listdir('.'):
                    text.insert("end", f + "\n")
            else:
                text.insert("end", f"'{cmd}' is not recognized\n")
            text.insert("end", prompt)
            text.see("end")
            return "break"

        text.bind("<Return>", on_enter)

    def notepad(self):
        win = tk.Toplevel(self)
        win.title("Notepad")
        win.geometry("400x300")
        text = tk.Text(win)
        text.pack(fill="both", expand=True)

        def save_file():
            f = filedialog.asksaveasfilename(defaultextension=".txt")
            if f:
                with open(f, "w", encoding="utf-8") as file:
                    file.write(text.get("1.0", "end-1c"))
                messagebox.showinfo("Notepad", "File saved")

        menubar = tk.Menu(win)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save", command=save_file)
        filemenu.add_command(label="Close", command=win.destroy)
        menubar.add_cascade(label="File", menu=filemenu)
        win.config(menu=menubar)

    def paint(self):
        win = tk.Toplevel(self)
        win.title("Paint")
        win.geometry("500x400")
        canvas = tk.Canvas(win, bg="white")
        canvas.pack(fill="both", expand=True)

        color = "black"
        last_x, last_y = None, None

        def set_color():
            nonlocal color
            c = colorchooser.askcolor()[1]
            if c:
                color = c

        def paint_start(event):
            nonlocal last_x, last_y
            last_x, last_y = event.x, event.y

        def paint_move(event):
            nonlocal last_x, last_y
            if last_x is not None and last_y is not None:
                canvas.create_line(last_x, last_y, event.x, event.y, fill=color, width=3)
            last_x, last_y = event.x, event.y

        def paint_end(event):
            nonlocal last_x, last_y
            last_x, last_y = None, None

        toolbar = tk.Frame(win)
        toolbar.pack()
        tk.Button(toolbar, text="Color", command=set_color).pack(side="left")
        canvas.bind("<ButtonPress-1>", paint_start)
        canvas.bind("<B1-Motion>", paint_move)
        canvas.bind("<ButtonRelease-1>", paint_end)

    def explorer(self):
        win = tk.Toplevel(self)
        win.title("Explorer")
        win.geometry("500x400")
        listbox = tk.Listbox(win)
        listbox.pack(fill="both", expand=True)

        files = os.listdir(".")
        for f in files:
            listbox.insert("end", f)

        def open_selected():
            try:
                selected = listbox.get(listbox.curselection())
                if os.path.isfile(selected) and selected.endswith(".txt"):
                    with open(selected, encoding="utf-8") as file:
                        content = file.read()
                    txt_win = tk.Toplevel(win)
                    txt_win.title(selected)
                    txt = tk.Text(txt_win)
                    txt.insert("1.0", content)
                    txt.pack(fill="both", expand=True)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")

        listbox.bind("<Double-1>", lambda e: open_selected())

    def open_browser(self):
        url = simpledialog.askstring("Browser", "Enter URL", initialvalue="https://www.google.com")
        if url:
            if not url.startswith(("http://", "https://")):
                url = "http://" + url
            webbrowser.open(url)

if __name__ == "__main__":
    app = Win()
    app.mainloop()
