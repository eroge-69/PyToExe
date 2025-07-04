import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import tempfile
import webbrowser
import os
import sys
import requests
import json

DARK_BG = "#222222"
DARK_FG = "#eeeeee"
DARK_ENTRY_BG = "#2a2a2a"
DARK_BTN_BG = "#333333"
DARK_BTN_FG = "#ffffff"
DARK_TAB_BG = "#242424"
GREEN_BTN_BG = "#37b24d"  # Green color for save button

FIREBASE_URL = "https://trackingclients-default-rtdb.firebaseio.com/"  # Ensure ending slash

def save_html_to_firebase(html_content):
    try:
        url = f"{FIREBASE_URL}html_snippets.json"
        data = {
            "html_content": html_content,
            "timestamp": int(__import__('time').time())
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)

class HTMLTab:
    def __init__(self, parent, tab_control, title):
        self.parent = parent
        self.frame = ttk.Frame(tab_control)
        tab_control.add(self.frame, text=title)

        btn_frame = tk.Frame(self.frame, bg=DARK_TAB_BG)
        btn_frame.pack(fill=tk.X, padx=8, pady=8)

        self.paste_btn = tk.Button(btn_frame, text="Paste", font=("Arial", 12), command=self.paste_clipboard, bg=DARK_BTN_BG, fg=DARK_BTN_FG, activebackground="#444")
        self.paste_btn.pack(side=tk.LEFT, padx=(0, 4))
        self.select_all_btn = tk.Button(btn_frame, text="Select All", font=("Arial", 12), command=self.select_all, bg=DARK_BTN_BG, fg=DARK_BTN_FG, activebackground="#444")
        self.select_all_btn.pack(side=tk.LEFT, padx=(0, 4))
        self.copy_btn = tk.Button(btn_frame, text="Copy", font=("Arial", 12), command=self.copy_to_clipboard, bg=DARK_BTN_BG, fg=DARK_BTN_FG, activebackground="#444")
        self.copy_btn.pack(side=tk.LEFT, padx=(0, 4))
        self.undo_btn = tk.Button(btn_frame, text="Undo", font=("Arial", 12), command=self.undo, bg=DARK_BTN_BG, fg=DARK_BTN_FG, activebackground="#444")
        self.undo_btn.pack(side=tk.LEFT, padx=(0, 4))
        self.redo_btn = tk.Button(btn_frame, text="Redo", font=("Arial", 12), command=self.redo, bg=DARK_BTN_BG, fg=DARK_BTN_FG, activebackground="#444")
        self.redo_btn.pack(side=tk.LEFT, padx=(0, 4))
        self.preview_btn = tk.Button(btn_frame, text="Preview in Chrome", font=("Arial", 12), command=self.preview_html, bg=DARK_BTN_BG, fg=DARK_BTN_FG, activebackground="#444")
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 4))

        self.textbox = scrolledtext.ScrolledText(
            self.frame, font=("Consolas", 13), wrap=tk.NONE,
            bg=DARK_ENTRY_BG, fg=DARK_FG, insertbackground=DARK_FG, 
            undo=True, maxundo=-1, autoseparators=True
        )
        self.textbox.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0,8))

        self.textbox.bind("<Control-z>", self.undo)
        self.textbox.bind("<Control-y>", self.redo)
        self.textbox.bind("<Control-Shift-Z>", self.redo)
        self.textbox.bind("<Command-z>", self.undo)  # macOS
        self.textbox.bind("<Command-Shift-Z>", self.redo)  # macOS

    def paste_clipboard(self):
        try:
            self.textbox.event_generate('<<Paste>>')
        except Exception as e:
            messagebox.showerror("Error", f"Could not paste from clipboard:\n{e}")

    def select_all(self):
        self.textbox.tag_add('sel', '1.0', 'end')
        self.textbox.focus_set()

    def copy_to_clipboard(self):
        try:
            text = self.textbox.get("1.0", tk.END)
            self.textbox.clipboard_clear()
            self.textbox.clipboard_append(text)
        except Exception as e:
            messagebox.showerror("Error", f"Could not copy to clipboard:\n{e}")

    def undo(self, event=None):
        try:
            self.textbox.edit_undo()
        except Exception:
            pass
        return "break"

    def redo(self, event=None):
        try:
            self.textbox.edit_redo()
        except Exception:
            pass
        return "break"

    def preview_html(self):
        html_code = self.textbox.get("1.0", tk.END).strip()
        if not html_code:
            messagebox.showwarning("Empty HTML", "Please paste some HTML code to preview.")
            return
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as tmp:
            tmp.write(html_code)
            tmp_path = tmp.name
        try:
            chrome_path = get_chrome_path()
            webbrowser.get(chrome_path).open(f"file://{tmp_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open in Chrome.\nError: {e}\nTrying default browser.")
            webbrowser.open(f"file://{tmp_path}")

    def get_content(self):
        return self.textbox.get("1.0", tk.END)

def get_chrome_path():
    if sys.platform.startswith('win'):
        chrome_paths = [
            "C://Program Files//Google//Chrome//Application//chrome.exe",
            "C://Program Files (x86)//Google//Chrome//Application//chrome.exe"
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                return f'"{path}" %s'
        return "chrome"
    elif sys.platform.startswith('darwin'):
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            return f'"{chrome_path}" %s'
        return "chrome"
    else:
        for path in ["google-chrome", "chrome", "chromium-browser", "chromium"]:
            if is_executable_in_path(path):
                return f"{path} %s"
        return "google-chrome"

def is_executable_in_path(exe):
    from shutil import which
    return which(exe) is not None

class HTMLPreviewTabsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HTML Previewer - Dark Tabs + Firebase Save")
        self.make_maximized()
        self.root.configure(bg=DARK_BG)

        style = ttk.Style(self.root)
        style.theme_use('default')
        style.configure('TNotebook', background=DARK_TAB_BG, borderwidth=0)
        style.configure('TNotebook.Tab', background=DARK_TAB_BG, foreground=DARK_FG, lightcolor=DARK_TAB_BG, borderwidth=0)
        style.map('TNotebook.Tab', background=[('selected', '#111')], foreground=[('selected', '#fff')])

        # Tab control
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.tabs = []
        self.tab_count = 0

        # Top menu frame with a green "Save to Firebase" button and an "Add Tab" button
        menu_frame = tk.Frame(self.root, bg=DARK_BG)
        menu_frame.pack(fill=tk.X, padx=0, pady=(0,4))
        self.save_firebase_btn = tk.Button(
            menu_frame, text="Save to Firebase", font=("Arial", 12, "bold"),
            command=self.save_current_tab_to_firebase,
            bg=GREEN_BTN_BG, fg="#fff", activebackground="#28a745", activeforeground="#fff"
        )
        self.save_firebase_btn.pack(side=tk.LEFT, padx=12, pady=6)

        self.add_tab_btn = tk.Button(
            menu_frame, text="Add Tab", font=("Arial", 12),
            command=self.add_tab,
            bg="#555", fg="#fff", activebackground="#444", activeforeground="#fff"
        )
        self.add_tab_btn.pack(side=tk.LEFT, padx=4, pady=6)

        # Start with one tab
        self.add_tab()

        # F11 to toggle maximized
        self.root.bind("<F11>", self.toggle_maximize)
        self.is_maximized = True

        # Ctrl+T to add tab
        self.root.bind("<Control-t>", lambda event: self.add_tab())

    def add_tab(self, event=None):
        self.tab_count += 1
        tab = HTMLTab(self.root, self.tab_control, f"Tab {self.tab_count}")
        self.tabs.append(tab)
        self.tab_control.select(len(self.tabs) - 1)

    def save_current_tab_to_firebase(self):
        current_tab_index = self.tab_control.index(self.tab_control.select())
        if 0 <= current_tab_index < len(self.tabs):
            tab = self.tabs[current_tab_index]
            html_content = tab.get_content().strip()
            if not html_content:
                messagebox.showwarning("Empty HTML", "Please paste some HTML code before saving.")
                return
            ok, resp = save_html_to_firebase(html_content)
            if ok:
                messagebox.showinfo("Saved to Firebase", "Tab's HTML saved to Firebase successfully!")
            else:
                messagebox.showerror("Error", f"Could not save to Firebase:\n{resp}")

    def make_maximized(self):
        self.root.attributes("-fullscreen", False)
        if sys.platform.startswith('win'):
            self.root.state('zoomed')
        else:
            self.root.attributes('-zoomed', True)

    def toggle_maximize(self, event=None):
        if self.is_maximized:
            self.root.state('normal')
            self.root.attributes('-zoomed', False)
        else:
            if sys.platform.startswith('win'):
                self.root.state('zoomed')
            else:
                self.root.attributes('-zoomed', True)
        self.is_maximized = not self.is_maximized

if __name__ == "__main__":
    try:
        import requests  # Ensure requests is available
    except ImportError:
        import sys
        messagebox.showerror("Missing Dependency", "Please install the 'requests' package:\npip install requests")
        sys.exit(1)
    root = tk.Tk()
    app = HTMLPreviewTabsApp(root)
    root.mainloop()
