#!/usr/bin/env python3
# lua_compiler_gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import os

# ----- API Settings -----
url_raw = 'luac.mtasa.com'
url = f'https://{url_raw}'
url_file = f'{url}/index.php'

HEADERS = {
    'Host': url_raw,
    'Origin': url,
    'Referer': url_file,
}

# ----- Request function -----
def compile_lua(file_path: str, obfuscate_level: int, do_compile: bool, debug: bool):
    filename = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        file_bytes = f.read()

    files = {
        'luasource': (filename, file_bytes, 'application/octet-stream')
    }
    data = {
        'compile': '1' if do_compile else '0',
        'obfuscate': str(obfuscate_level),
        'debug': '1' if debug else '0',
        'Submit': 'Submit'
    }

    resp = requests.post(url_file, headers=HEADERS, files=files, data=data, timeout=30)
    return resp

# ----- GUI -----
class LuaCompilerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lua Compiler GUI")
        self.resizable(False, False)
        padding = 10

        frm = ttk.Frame(self, padding=padding)
        frm.grid(row=0, column=0)

        # File selector
        ttk.Label(frm, text="Lua file:").grid(row=0, column=0, sticky='w')
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(frm, textvariable=self.file_var, width=50)
        self.file_entry.grid(row=1, column=0, columnspan=2, sticky='w')
        ttk.Button(frm, text="Browse...", command=self.browse_file).grid(row=1, column=2, padx=(6,0))

        # Obfuscate level
        ttk.Label(frm, text="Obfuscate level:").grid(row=2, column=0, sticky='w', pady=(8,0))
        self.obf_var = tk.IntVar(value=3)
        obf_menu = ttk.Combobox(frm, textvariable=self.obf_var, values=[0,1,2,3], width=4, state='readonly')
        obf_menu.grid(row=2, column=1, sticky='w', pady=(8,0))

        # Compile & Debug checkbuttons
        self.compile_var = tk.BooleanVar(value=True)
        self.debug_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm, text="Compile", variable=self.compile_var).grid(row=3, column=0, sticky='w', pady=(8,0))
        ttk.Checkbutton(frm, text="Debug", variable=self.debug_var).grid(row=3, column=1, sticky='w', pady=(8,0))

        # Overwrite or Save As option
        self.overwrite_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Overwrite original file after success", variable=self.overwrite_var).grid(row=4, column=0, columnspan=2, sticky='w', pady=(6,0))

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=(12,0))
        self.btn_compile = ttk.Button(btn_frame, text="Compile", command=self.on_compile)
        self.btn_compile.grid(row=0, column=0)
        ttk.Button(btn_frame, text="Quit", command=self.destroy).grid(row=0, column=1, padx=(8,0))

        # Status box
        ttk.Label(frm, text="Status:").grid(row=6, column=0, sticky='w', pady=(10,0))
        self.status = tk.Text(frm, width=65, height=8, state='disabled', wrap='word')
        self.status.grid(row=7, column=0, columnspan=3, pady=(4,0))

    def browse_file(self):
        p = filedialog.askopenfilename(title="Select Lua file", filetypes=[("Lua files","*.lua"),("All files","*.*")])
        if p:
            self.file_var.set(p)

    def log(self, *msgs):
        self.status.configure(state='normal')
        for m in msgs:
            self.status.insert('end', f"{m}\n")
        self.status.see('end')
        self.status.configure(state='disabled')

    def on_compile(self):
        file_path = self.file_var.get().strip()
        if not file_path or not os.path.isfile(file_path):
            messagebox.showerror("Error", "Please select a valid Lua file.")
            return

        obf = int(self.obf_var.get())
        do_compile = bool(self.compile_var.get())
        debug = bool(self.debug_var.get())

        self.btn_compile.configure(state='disabled')
        self.log("Sending file to server...")

        try:
            resp = compile_lua(file_path, obf, do_compile, debug)
        except Exception as e:
            self.log("Request error:", str(e))
            messagebox.showerror("Network Error", f"Request failed:\n{e}")
            self.btn_compile.configure(state='normal')
            return

        if resp.status_code != 200:
            self.log(f"Server response: HTTP {resp.status_code}")
            messagebox.showerror("Server Error", f"Server returned: HTTP {resp.status_code}")
            self.btn_compile.configure(state='normal')
            return

        content = resp.content

        if content == b'ERROR Could not compile file':
            self.log("Server: Could not compile file")
            messagebox.showerror("Compile Error", "Server could not compile the file.")
            self.btn_compile.configure(state='normal')
            return

        if self.overwrite_var.get():
            save_path = file_path
        else:
            suggested = os.path.splitext(os.path.basename(file_path))[0] + ".luac"
            save_path = filedialog.asksaveasfilename(
                title="Save compiled file as",
                initialfile=suggested,
                defaultextension=".luac",
                filetypes=[("Compiled Lua","*.luac"),("All files","*.*")]
            )
            if not save_path:
                self.log("Save canceled.")
                self.btn_compile.configure(state='normal')
                return

        try:
            with open(save_path, 'wb') as out_f:
                out_f.write(content)
            self.log(f"File successfully saved: {save_path} ({len(content)} bytes)")
            messagebox.showinfo("Done", f"File saved:\n{save_path}")
        except Exception as e:
            self.log("Save error:", str(e))
            messagebox.showerror("Save Error", f"Could not save file:\n{e}")
        finally:
            self.btn_compile.configure(state='normal')

if __name__ == '__main__':
    app = LuaCompilerGUI()
    app.mainloop()
