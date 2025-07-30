import tkinter as tk

def title_case(sentence):
    exceptions = {"a", "an", "and", "as", "at", "but", "by", "for", "in",
                  "nor", "of", "on", "or", "so", "the", "to", "up", "yet"}
    words = sentence.lower().split()
    if not words:
        return ""
    titled = [words[0].capitalize()]
    for word in words[1:]:
        titled.append(word if word in exceptions else word.capitalize())
    return " ".join(titled)

class TitleCaseApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.overrideredirect(True)  # Remove OS window frame
        self.geometry("620x520")  # taller to fit footer
        self.configure(bg="#1e1e1e")

        self._offsetx = 0
        self._offsety = 0
        self.is_minimized = False  # Track minimized state

        # Colors
        self.TITLE_BAR_BG = "#d35400"       # Dark orange
        self.TITLE_BAR_HOVER_BG = "#a24300" # Darker orange for hover

        # Custom Title Bar
        self.title_bar = tk.Frame(self, bg=self.TITLE_BAR_BG, relief='raised', bd=0, height=40)
        self.title_bar.pack(fill=tk.X)

        # Top label - BIG BOLD UPPERCASE
        self.title_label = tk.Label(
            self.title_bar,
            text="BROKKEN MEDIA | TITLE CONVERTER",
            bg=self.TITLE_BAR_BG,
            fg="white",
            font=("Segoe UI", 16, "bold")
        )
        self.title_label.pack(side=tk.LEFT, padx=15, pady=5)

        # Window control buttons
        self.create_title_bar_buttons()

        # Bind move window events to title bar and label
        self.title_bar.bind("<Button-1>", self.click_title_bar)
        self.title_bar.bind("<B1-Motion>", self.drag_title_bar)
        self.title_label.bind("<Button-1>", self.click_title_bar)
        self.title_label.bind("<B1-Motion>", self.drag_title_bar)

        self.is_maximized = False
        self.normal_geometry = self.geometry()

        # Build main UI
        self.build_ui()

        # Bind to window restore event to fix overrideredirect after minimize
        self.bind("<Map>", self.on_map)

    def create_title_bar_buttons(self):
        # Close button
        self.btn_close = tk.Button(self.title_bar, text="✕", bg=self.TITLE_BAR_BG, fg="white", borderwidth=0,
                                   command=self.close_app, font=("Segoe UI", 12, "bold"),
                                   activebackground="#e74c3c", activeforeground="white", cursor="hand2")
        self.btn_close.pack(side=tk.RIGHT, padx=5, pady=5)
        self.btn_close.bind("<Enter>", lambda e: self.btn_close.config(bg=self.TITLE_BAR_HOVER_BG))
        self.btn_close.bind("<Leave>", lambda e: self.btn_close.config(bg=self.TITLE_BAR_BG))

        # Maximize button
        self.btn_maximize = tk.Button(self.title_bar, text="⬜", bg=self.TITLE_BAR_BG, fg="white", borderwidth=0,
                                      command=self.maximize_restore, font=("Segoe UI", 10, "bold"),
                                      activebackground="#e67e22", activeforeground="white", cursor="hand2")
        self.btn_maximize.pack(side=tk.RIGHT, padx=5, pady=5)
        self.btn_maximize.bind("<Enter>", lambda e: self.btn_maximize.config(bg=self.TITLE_BAR_HOVER_BG))
        self.btn_maximize.bind("<Leave>", lambda e: self.btn_maximize.config(bg=self.TITLE_BAR_BG))

        # Minimize button
        self.btn_minimize = tk.Button(self.title_bar, text="━", bg=self.TITLE_BAR_BG, fg="white", borderwidth=0,
                                      command=self.minimize_app, font=("Segoe UI", 12, "bold"),
                                      activebackground="#e67e22", activeforeground="white", cursor="hand2")
        self.btn_minimize.pack(side=tk.RIGHT, padx=5, pady=5)
        self.btn_minimize.bind("<Enter>", lambda e: self.btn_minimize.config(bg=self.TITLE_BAR_HOVER_BG))
        self.btn_minimize.bind("<Leave>", lambda e: self.btn_minimize.config(bg=self.TITLE_BAR_BG))

    def click_title_bar(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def drag_title_bar(self, event):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.geometry(f"+{x}+{y}")

    def close_app(self):
        self.destroy()

    def minimize_app(self):
        self.is_minimized = True
        self.overrideredirect(False)  # Allow native window controls to work
        self.iconify()

    def on_map(self, event=None):
        # Called when window is restored
        if self.is_minimized:
            self.overrideredirect(True)
            self.is_minimized = False

    def maximize_restore(self):
        if not self.is_maximized:
            self.normal_geometry = self.geometry()
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
            self.is_maximized = True
        else:
            self.geometry(self.normal_geometry)
            self.is_maximized = False

    def build_ui(self):
        FONT_MAIN = ("Segoe UI", 14)
        FONT_BUTTON = ("Segoe UI", 12, "bold")
        COLOR_BG = "#1e1e1e"
        COLOR_TEXT = "#e0e0e0"

        self.title_label_text = tk.Label(self, text="Paste or Type Your Text Below:", font=FONT_MAIN, bg=COLOR_BG, fg=COLOR_TEXT)
        self.title_label_text.pack(pady=(20, 8))

        self.input_box = tk.Text(self, height=6, width=72, font=FONT_MAIN, bg="#2b2b2b", fg=COLOR_TEXT, insertbackground=COLOR_TEXT,
                                relief="flat", bd=0, highlightthickness=2, highlightbackground="#444444", highlightcolor="#666666",
                                undo=True)
        self.input_box.pack(padx=20, pady=(0, 15))

        self.input_box.bind("<<Modified>>", self.on_modified)
        self.input_box.bind("<Control-v>", self.on_paste)
        self.input_box.bind("<<Paste>>", self.on_paste)
        self.input_box.bind("<Control-z>", self.undo)
        self.input_box.bind("<Control-y>", self.redo)

        button_frame = tk.Frame(self, bg=COLOR_BG)
        button_frame.pack(pady=(0, 15))

        self.reset_button = tk.Button(button_frame, text="Reset", command=self.reset_all,
                                     font=FONT_BUTTON, bg=self.TITLE_BAR_BG, fg="white",
                                     activebackground=self.TITLE_BAR_HOVER_BG, activeforeground="white",
                                     relief="flat", bd=0, padx=14, pady=8, cursor="hand2")
        self.reset_button.pack()

        separator = tk.Frame(self, height=2, bg="#444444", bd=0)
        separator.pack(fill="x", padx=20, pady=(0,15))

        self.output_box = tk.Text(self, height=8, width=72, font=FONT_MAIN, bg="#2b2b2b", fg=self.TITLE_BAR_BG, insertbackground=self.TITLE_BAR_BG,
                                 relief="flat", bd=0, highlightthickness=2, highlightbackground="#444444", highlightcolor="#666666",
                                 state="disabled")
        self.output_box.pack(padx=20, pady=(0,20))
        self.output_box.tag_configure("yellow_text", foreground=self.TITLE_BAR_BG)

        # Footer copyright label
        self.footer_label = tk.Label(self,
                                     text="© 2025 Brokken Media Video Productions LLC, all rights reserved.",
                                     bg=COLOR_BG, fg="white", font=("Segoe UI", 9))
        self.footer_label.pack(side=tk.BOTTOM, pady=8)

    def process_text(self):
        input_text = self.input_box.get("1.0", tk.END).rstrip('\n')
        if not input_text:
            self.clear_output()
            return
        if input_text.lower() == "exit":
            self.destroy()
            return
        result = title_case(input_text)
        self.output_box.config(state="normal")
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, result)
        self.output_box.tag_add("yellow_text", "1.0", "end")
        self.output_box.config(state="disabled")

    def on_modified(self, event=None):
        self.input_box.edit_modified(False)
        self.process_text()

    def on_paste(self, event=None):
        self.after(50, lambda: (
            self.process_text(),
            self.copy_to_clipboard()
        ))
        return None

    def copy_to_clipboard(self):
        output_text = self.output_box.get("1.0", tk.END).strip()
        if output_text:
            self.clipboard_clear()
            self.clipboard_append(output_text)

    def undo(self, event=None):
        try:
            self.input_box.edit_undo()
        except tk.TclError:
            pass
        self.process_text()
        return "break"

    def redo(self, event=None):
        try:
            self.input_box.edit_redo()
        except tk.TclError:
            pass
        self.process_text()
        return "break"

    def reset_all(self):
        self.input_box.delete("1.0", tk.END)
        self.clear_output()

    def clear_output(self):
        self.output_box.config(state="normal")
        self.output_box.delete("1.0", tk.END)
        self.output_box.config(state="disabled")

if __name__ == "__main__":
    app = TitleCaseApp()
    app.mainloop()
