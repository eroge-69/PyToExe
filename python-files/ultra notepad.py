#!/usr/bin/env python3
"""
Ultra Notepad - merged full version
Features:
- Tabs with '+' tab to create new named tabs
- Close button inside each tab (top-right)
- Line count per tab + status bar
- Font color chooser in Settings (applies to current and new tabs)
- Dark mode and accent color selection
- File operations: New, Open, Save, Save As
- Keyboard shortcuts: Ctrl+N, Ctrl+S, Ctrl+Shift+S, Ctrl+W
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser, font

# Optional: nicer themed window; pip install ttkthemes
try:
    from ttkthemes import ThemedTk
    USE_THEMEDTK = True
except Exception:
    USE_THEMEDTK = False

class UltraNotepadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultra Notepad")
        self.root.geometry("950x650")
        self.root.minsize(640, 400)

        # state
        self.default_font_family = "Consolas" if "Consolas" in font.families() else "Courier"
        self.default_font_size = 12
        self.font_color = "#000000"  # default font color
        self.dark_mode = False
        self.accent = "#3b82f6"  # blue by default

        # UI
        self._create_menu()
        self._create_notebook()
        self._create_statusbar()

        # create initial tab
        self.create_new_tab()

        # shortcuts
        self.root.bind("<Control-n>", lambda e: self.create_new_tab())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-Shift-S>", lambda e: self.save_as_file())
        self.root.bind("<Control-w>", lambda e: self.close_current_tab())

    # ---------------- UI: Menu ----------------
    def _create_menu(self):
        menubar = tk.Menu(self.root)
        # File
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Tab", accelerator="Ctrl+N", command=self.create_new_tab)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Close Tab", accelerator="Ctrl+W", command=self.close_current_tab)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=lambda: self._event_on_current("<<Undo>>"))
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=lambda: self._event_on_current("<<Redo>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: self._event_on_current("<<Cut>>"))
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: self._event_on_current("<<Copy>>"))
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: self._event_on_current("<<Paste>>"))
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # Settings
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)
        settings_menu.add_command(label="Choose Font Color...", command=self.choose_font_color)

        # Accent color submenu
        accent_menu = tk.Menu(settings_menu, tearoff=0)
        accent_menu.add_command(label="Blue", command=lambda: self.set_accent("#3b82f6"))
        accent_menu.add_command(label="Green", command=lambda: self.set_accent("#16a34a"))
        accent_menu.add_command(label="Orange", command=lambda: self.set_accent("#f97316"))
        accent_menu.add_command(label="Purple", command=lambda: self.set_accent("#7c3aed"))
        settings_menu.add_cascade(label="Accent Color", menu=accent_menu)

        menubar.add_cascade(label="Settings", menu=settings_menu)

        self.root.config(menu=menubar)

    # ---------------- UI: Notebook (tabs) ----------------
    def _create_notebook(self):
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(fill="both", expand=True)

        # create a plus tab at the end
        self.plus_frame = ttk.Frame(self.tab_control)
        self.tab_control.add(self.plus_frame, text="+")
        self.tab_control.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event=None):
        # If user switched to the plus tab, create a new tab (and keep plus at end)
        idx = self.tab_control.index("current")
        if idx == self.tab_control.index(self.plus_frame):
            self.create_new_tab()

        # update status to reflect current tab
        self._update_status_from_active_tab()

    def create_new_tab(self, content="", title=None, file_path=None):
        # ask for custom tab name unless provided
        if title is None:
            title = simpledialog.askstring("Tab Name", "Enter tab name:", parent=self.root)
            if not title:
                title = "Untitled"

        frame = ttk.Frame(self.tab_control)
        # top bar inside tab (title label left, close button right, line count label)
        top_bar = tk.Frame(frame)
        top_bar.pack(fill="x", padx=4, pady=(6, 2))

        lbl_title = tk.Label(top_bar, text=title, anchor="w")
        lbl_title.pack(side="left", padx=(4, 0))

        line_lbl = tk.Label(top_bar, text="Lines: 0")
        line_lbl.pack(side="right", padx=4)

        close_btn = tk.Button(top_bar, text="Close Tab", command=lambda f=frame: self._close_tab_frame(f))
        close_btn.pack(side="right", padx=4)

        # text widget
        text = tk.Text(frame, wrap="word", undo=True,
                       font=(self.default_font_family, self.default_font_size),
                       fg=self.font_color, bd=0, relief="flat", padx=8, pady=8)
        text.pack(fill="both", expand=True, padx=6, pady=(0,6))

        # attach metadata
        text.file_path = file_path
        text.tab_title_widget = lbl_title
        text.line_label_widget = line_lbl

        # insert content
        if content:
            text.insert("1.0", content)

        # events
        text.bind("<KeyRelease>", lambda e, t=text: self._on_text_change(t))
        text.bind("<Button-3>", self._text_right_click)

        # insert tab before plus tab
        insert_index = max(0, self.tab_control.index("end") - 1)
        self.tab_control.insert(insert_index, frame, text=title)
        self.tab_control.select(frame)

        # apply theming
        self._apply_theme_to_text(text)

        # update line counts
        self._on_text_change(text)

    def _close_tab_frame(self, frame):
        # do not allow closing all tabs: if only plus and one tab exist, allow closing but create new
        self.tab_control.forget(frame)
        # ensure at least one tab exists
        if len(self.tab_control.tabs()) <= 1:
            self.create_new_tab()

        self._update_status_from_active_tab()

    def close_current_tab(self):
        cur = self.tab_control.select()
        if not cur:
            return
        widget = self.tab_control.nametowidget(cur)
        # don't close plus tab
        if widget == self.plus_frame:
            return
        self.tab_control.forget(cur)
        # ensure at least one tab remains
        if len(self.tab_control.tabs()) <= 1:
            self.create_new_tab()
        self._update_status_from_active_tab()

    def get_current_text(self):
        cur = self.tab_control.select()
        if not cur:
            return None
        frame = self.tab_control.nametowidget(cur)
        # find the Text child
        for child in frame.winfo_children():
            if isinstance(child, tk.Text):
                return child
        return None

    # ---------------- File operations ----------------
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt *.md *.py *.log"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Open Error", str(e))
            return

        filename = os.path.basename(path)
        self.create_new_tab(content=content, title=filename, file_path=path)

    def save_file(self):
        t = self.get_current_text()
        if not t:
            return
        if getattr(t, "file_path", None):
            path = t.file_path
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(t.get("1.0", "end-1c"))
                messagebox.showinfo("Saved", f"Saved: {path}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))
        else:
            self.save_as_file()

    def save_as_file(self):
        t = self.get_current_text()
        if not t:
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text files", "*.txt *.md"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(t.get("1.0", "end-1c"))
            t.file_path = path
            # update tab label
            cur = self.tab_control.select()
            self.tab_control.tab(cur, text=os.path.basename(path))
            # also update the small label inside top_bar
            t.tab_title_widget.config(text=os.path.basename(path))
            messagebox.showinfo("Saved", f"Saved: {path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    # ---------------- Edit helpers ----------------
    def _event_on_current(self, event_name):
        t = self.get_current_text()
        if t:
            t.event_generate(event_name)

    # ---------------- Text events, line counts, right-click ----------------
    def _on_text_change(self, text_widget):
        # update line label inside tab and status bar
        try:
            lines = int(text_widget.index("end-1c").split(".")[0])
        except Exception:
            lines = 0
        text_widget.line_label_widget.config(text=f"Lines: {lines}")
        # update global status if this is the active tab
        active_text = self.get_current_text()
        if active_text == text_widget:
            self.status_var.set(f"Lines: {lines}")

    def _update_status_from_active_tab(self):
        t = self.get_current_text()
        if t:
            try:
                lines = int(t.index("end-1c").split(".")[0])
            except Exception:
                lines = 0
            self.status_var.set(f"Lines: {lines}")
        else:
            self.status_var.set("Lines: 0")

    def _text_right_click(self, event):
        # simple context menu for text widget
        text_widget = event.widget
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Undo", command=lambda: text_widget.event_generate("<<Undo>>"))
        menu.add_command(label="Redo", command=lambda: text_widget.event_generate("<<Redo>>"))
        menu.add_separator()
        menu.add_command(label="Cut", command=lambda: text_widget.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: text_widget.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: text_widget.event_generate("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: self._select_all(text_widget))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _select_all(self, widget):
        widget.tag_add("sel", "1.0", "end-1c")
        widget.mark_set("insert", "1.0")
        widget.see("insert")

    # ---------------- Theme & font color ----------------
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self._apply_theme_all_texts()

    def choose_font_color(self):
        color = colorchooser.askcolor(title="Choose font color", initialcolor=self.font_color)[1]
        if color:
            self.font_color = color
            # apply to current text and set default for new tabs
            t = self.get_current_text()
            if t:
                t.config(fg=self.font_color)

    def set_accent(self, hexcolor):
        self.accent = hexcolor
        # for now accent used for selection tint; reapply
        self._apply_theme_all_texts()

    def _apply_theme_all_texts(self):
        for tab_id in self.tab_control.tabs():
            w = self.tab_control.nametowidget(tab_id)
            if w == self.plus_frame:
                continue
            for child in w.winfo_children():
                if isinstance(child, tk.Text):
                    self._apply_theme_to_text(child)
        # update status widget style if needed
        # (can extend to recolor other UI parts)

    def _apply_theme_to_text(self, text_widget):
        if self.dark_mode:
            bg = "#0b1220"
            fg = self.font_color if self.font_color else "#e6eef8"
            insert = "white"
        else:
            bg = "white"
            fg = self.font_color if self.font_color else "#0b1220"
            insert = "black"

        # apply selection tint using a subtle tinted version of accent
        sel_bg = self._tint_color(self.accent, 0.2)
        text_widget.config(bg=bg, fg=fg, insertbackground=insert,
                           selectbackground=sel_bg, selectforeground=fg)

    def _tint_color(self, hex_color, amount=0.12):
        try:
            hex_color = hex_color.lstrip("#")
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            r = int(r + (255 - r) * amount)
            g = int(g + (255 - g) * amount)
            b = int(b + (255 - b) * amount)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color

    # ---------------- Status bar ----------------
    def _create_statusbar(self):
        self.status_var = tk.StringVar(value="Lines: 0")
        status = ttk.Label(self.root, textvariable=self.status_var, anchor="w")
        status.pack(side="bottom", fill="x", padx=4, pady=2)

    # run
    def run(self):
        self.root.mainloop()

def main():
    if USE_THEMEDTK:
        root = ThemedTk(theme="arc")
    else:
        root = tk.Tk()
    app = UltraNotepadApp(root)
    app.run()

if __name__ == "__main__":
    main()