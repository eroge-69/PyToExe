import tkinter as tk
from tkinter import filedialog, messagebox

class TextEditor:
    def __init__(self, root):
        self.root = root
        root.title("Enhanced Text Editor")
        root.geometry("800x600")

        self.default_font_size = 12
        self.font_size = self.default_font_size
        self.word_wrap = False
        self.dark_mode = False
        self.show_row_numbers = True

        self.setup_widgets()
        self.create_menu()
        self.bind_events()

        self.file_path = None
        self.update_status_bar()
        self.apply_theme()
        self.update_file_label()

    def setup_widgets(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Canvas for visual row indicators
        self.row_canvas = tk.Canvas(self.main_frame, width=40)
        self.row_canvas.grid(row=0, column=0, sticky="ns")

        self.text_area = tk.Text(
            self.main_frame,
            wrap="none",
            font=("Courier New", self.font_size),
            undo=True,
            maxundo=50
        )
        self.text_area.grid(row=0, column=1, sticky="nsew")

        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.on_scroll)
        self.scrollbar.grid(row=0, column=2, sticky="ns")
        self.text_area.config(yscrollcommand=self.scrollbar.set)

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        self.file_label = tk.Label(self.root, text="", anchor="w")
        self.file_label.grid(row=2, column=0, sticky="ew")

        self.status_bar = tk.Label(self.root, text="", anchor="w")
        self.status_bar.grid(row=1, column=0, sticky="ew")

    def create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        self.edit_menu = edit_menu
        edit_menu.add_command(label="Undo", command=self.text_area.edit_undo, accelerator="Ctrl+Z", state="disabled")
        self.undo_index = edit_menu.index("end")

        edit_menu.add_command(label="Redo", command=self.text_area.edit_redo, accelerator="Ctrl+Y", state="disabled")
        self.redo_index = edit_menu.index("end")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut")
        edit_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        menubar.add_cascade(label="Edit", menu=edit_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle Word Wrap", command=self.toggle_word_wrap)
        view_menu.add_command(label="Toggle Light/Dark Mode", command=self.toggle_theme)
        view_menu.add_command(label="Toggle Row Numbers", command=self.toggle_row_numbers)
        view_menu.add_separator()
        view_menu.add_command(label="Zoom In", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        view_menu.add_command(label="Reset Zoom", command=self.reset_zoom)
        menubar.add_cascade(label="View", menu=view_menu)

        about_menu = tk.Menu(menubar, tearoff=0)
        about_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="About", menu=about_menu)

        self.root.config(menu=menubar)

    def bind_events(self):
        self.text_area.bind("<Control-z>", lambda e: self.text_area.edit_undo())
        self.text_area.bind("<Control-y>", lambda e: self.text_area.edit_redo())
        self.text_area.bind("<<Modified>>", self.on_text_change)
        self.text_area.bind("<KeyRelease>", lambda e: (self.update_row_canvas(), self.update_edit_menu_state(), self.update_file_label(), self.update_status_bar()))
        self.text_area.bind("<MouseWheel>", lambda e: self.update_row_canvas())
        self.text_area.bind("<ButtonRelease>", lambda e: (self.update_row_canvas(), self.update_status_bar(), self.update_edit_menu_state()))
        self.text_area.bind("<Configure>", lambda e: self.update_row_canvas())
        self.root.bind("<Control-0>", lambda e: self.reset_zoom())

    def update_file_label(self):
        if self.file_path:
            self.file_label.config(text=f"File: {self.file_path}")
        else:
            self.file_label.config(text="File: (unsaved)")

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
                self.file_path = file_path
                self.update_row_canvas()

    def save_file(self):
        if not self.file_path:
            self.file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if self.file_path:
            with open(self.file_path, "w") as file:
                content = self.text_area.get("1.0", tk.END)
                file.write(content)
                self.update_file_label()

    def toggle_word_wrap(self):
        self.word_wrap = not self.word_wrap
        wrap_mode = "word" if self.word_wrap else "none"
        self.text_area.config(wrap=wrap_mode)
        self.update_row_canvas()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def toggle_row_numbers(self):
        self.show_row_numbers = not self.show_row_numbers
        if self.show_row_numbers:
            self.row_canvas.grid()
        else:
            self.row_canvas.grid_remove()
        self.update_row_canvas()

    def zoom_in(self):
        self.font_size += 1
        self.text_area.config(font=("Courier New", self.font_size))
        self.update_row_canvas()

    def zoom_out(self):
        if self.font_size > 6:
            self.font_size -= 1
            self.text_area.config(font=("Courier New", self.font_size))
            self.update_row_canvas()

    def reset_zoom(self):
        self.font_size = self.default_font_size
        self.text_area.config(font=("Courier New", self.font_size))
        self.update_row_canvas()

    def get_row_number_color(self):
        return "#aaaaaa" if self.dark_mode else "#000000"

    def apply_theme(self):
        if self.dark_mode:
            bg = "#2e2e2e"
            fg = "#ffffff"
            gutter_bg = "#3b3b3b"
            status_bg = "#1e1e1e"
            status_fg = "#cccccc"
        else:
            bg = "#ffffff"
            fg = "#000000"
            gutter_bg = "#f0f0f0"
            status_bg = "#f0f0f0"
            status_fg = "#000000"

        self.text_area.config(bg=bg, fg=fg, insertbackground=fg)
        self.row_canvas.config(bg=gutter_bg)
        self.status_bar.config(bg=status_bg, fg=status_fg)
        self.update_row_canvas()

    def on_scroll(self, *args):
        self.text_area.yview(*args)
        self.update_row_canvas()

    def update_edit_menu_state(self):
        try:
            self.edit_menu.entryconfig(self.undo_index, state="normal")
            self.edit_menu.entryconfig(self.redo_index, state="normal")
        except:
            pass

    def on_text_change(self, event=None):
        self.text_area.edit_modified(False)
        self.update_status_bar()
        self.update_row_canvas()

    def update_status_bar(self):
        text = self.text_area.get("1.0", tk.END)
        char_count = len(text) - 1
        word_count = len(text.split())
        line, col = self.text_area.index(tk.INSERT).split(".")
        status = f"Ln {line}, Col {int(col)+1} | Characters: {char_count} | Words: {word_count}"
        self.status_bar.config(text=status)

    def update_row_canvas(self):
        if not self.show_row_numbers:
            return

        self.row_canvas.delete("all")
        i = self.text_area.index("@0,0")
        while True:
            dline = self.text_area.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            row_num = i.split(".")[0]
            self.row_canvas.create_text(35, y, anchor="ne", text=row_num, font=("Courier New", 10), fill=self.get_row_number_color())
            i = self.text_area.index(f"{i}+1line")

    def show_about(self):
        messagebox.showinfo("About", "Enhanced Text Editor\nVersion 9.0\nCreated using Python and Tkinter\n\nProgrammer: Jason Knell")

if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()
