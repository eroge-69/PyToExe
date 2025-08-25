import base64
import os
import threading
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

# ---------------------------
# Base64 helpers
# ---------------------------

def file_to_b64_string(path: str) -> str:
    with open(path, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode('utf-8')


def b64_string_to_file(b64: str, out_path: str):
    # remove common whitespace/newlines
    cleaned = ''.join(b64.split())
    with open(out_path, 'wb') as f:
        f.write(base64.b64decode(cleaned))


# ---------------------------
# GUI
# ---------------------------
class Base64App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("system")  # "light", "dark", or "system"
        ctk.set_default_color_theme("blue")

        self.title("Base64 Converter • CustomTkinter")
        self.geometry("980x640")
        self.minsize(820, 540)

        # state
        self.selected_file_path: str | None = None

        # layout: two columns, left actions, right text area
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, corner_radius=16)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)
        self.sidebar.grid_rowconfigure(10, weight=1)

        self.main = ctk.CTkFrame(self, corner_radius=16)
        self.main.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        # --- sidebar widgets ---
        self.lbl_title = ctk.CTkLabel(self.sidebar, text="Base64 Converter", font=("Segoe UI", 20, "bold"))
        self.lbl_title.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        self.btn_pick = ctk.CTkButton(self.sidebar, text="📁 Choose File…", command=self.pick_file)
        self.btn_pick.grid(row=1, column=0, padx=16, pady=(8, 8), sticky="ew")

        self.lbl_file = ctk.CTkLabel(self.sidebar, text="No file selected", wraplength=220, fg_color="transparent")
        self.lbl_file.grid(row=2, column=0, padx=16, pady=(0, 8), sticky="w")

        self.btn_encode = ctk.CTkButton(self.sidebar, text="Encode → Base64", command=self.encode_selected, state="disabled")
        self.btn_encode.grid(row=3, column=0, padx=16, pady=8, sticky="ew")

        self.btn_save_b64 = ctk.CTkButton(self.sidebar, text="💾 Save Base64 to .txt", command=self.save_b64)
        self.btn_save_b64.grid(row=4, column=0, padx=16, pady=(8, 8), sticky="ew")

        self.separator = ctk.CTkLabel(self.sidebar, text="", height=1)
        self.separator.grid(row=5, column=0, padx=16, pady=(12, 12), sticky="ew")

        self.btn_load_b64 = ctk.CTkButton(self.sidebar, text="📜 Load Base64 .txt…", command=self.load_b64_from_file)
        self.btn_load_b64.grid(row=6, column=0, padx=16, pady=(8, 8), sticky="ew")

        self.btn_decode = ctk.CTkButton(self.sidebar, text="Decode → File", command=self.decode_to_file)
        self.btn_decode.grid(row=7, column=0, padx=16, pady=8, sticky="ew")

        self.btn_copy = ctk.CTkButton(self.sidebar, text="📋 Copy Base64", command=self.copy_b64)
        self.btn_copy.grid(row=8, column=0, padx=16, pady=8, sticky="ew")

        self.progress = ctk.CTkProgressBar(self.sidebar)
        self.progress.set(0)
        self.progress.grid(row=9, column=0, padx=16, pady=(8, 16), sticky="ew")

        self.theme_switch = ctk.CTkSwitch(self.sidebar, text="Dark mode", command=self.toggle_theme)
        self.theme_switch.grid(row=11, column=0, padx=16, pady=(8, 16), sticky="w")
        # initialize switch state to current
        self.theme_switch.select() if ctk.get_appearance_mode() == "Dark" else self.theme_switch.deselect()

        # --- main panel ---
        self.search_frame = ctk.CTkFrame(self.main)
        self.search_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        self.search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.search_frame, text="Find:").grid(row=0, column=0, padx=(8, 6), pady=8)
        self.entry_search = ctk.CTkEntry(self.search_frame, placeholder_text="Search in Base64 text…")
        self.entry_search.grid(row=0, column=1, padx=(0, 6), pady=8, sticky="ew")
        ctk.CTkButton(self.search_frame, text="Find", width=60, command=self.find_in_text).grid(row=0, column=2, padx=(0, 8), pady=8)

        self.txt = ctk.CTkTextbox(self.main, wrap="none")
        self.txt.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        # scrollbars
        self.scroll_x = ctk.CTkScrollbar(self.main, orientation="horizontal", command=self.txt.xview)
        self.scroll_x.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        self.txt.configure(xscrollcommand=self.scroll_x.set)

    # --- actions ---
    def toggle_theme(self):
        mode = ctk.get_appearance_mode()
        new_mode = "Light" if mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)

    def set_progress(self, value: float):
        try:
            self.progress.set(value)
            self.update_idletasks()
        except Exception:
            pass

    def pick_file(self):
        path = filedialog.askopenfilename(title="Choose a file to encode")
        if not path:
            return
        self.selected_file_path = path
        base = os.path.basename(path)
        size = os.path.getsize(path)
        self.lbl_file.configure(text=f"Selected: {base} (\u2248 {size:,} bytes)")
        self.btn_encode.configure(state="normal")

    def encode_selected(self):
        if not self.selected_file_path:
            messagebox.showinfo("No file", "Please choose a file first.")
            return
        self.run_bg(self._encode_worker)

    def _encode_worker(self):
        try:
            self.set_progress(0.1)
            b64 = file_to_b64_string(self.selected_file_path)
            self.set_progress(0.6)
            # insert to text box
            self.txt.delete("1.0", tk.END)
            self.txt.insert("1.0", b64)
            self.set_progress(1.0)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Encode error", str(e))
        finally:
            self.after(400, lambda: self.set_progress(0))

    def save_b64(self):
        content = self.txt.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo("Nothing to save", "There is no Base64 text to save.")
            return
        out = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt"), ("All", "*.*")], title="Save Base64 text")
        if not out:
            return
        try:
            with open(out, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("Saved", f"Saved Base64 to:\n{out}")
        except Exception as e:
            messagebox.showerror("Save error", str(e))

    def load_b64_from_file(self):
        path = filedialog.askopenfilename(title="Open Base64 text file", filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.txt.delete("1.0", tk.END)
            self.txt.insert("1.0", content)
            messagebox.showinfo("Loaded", f"Loaded Base64 from:\n{path}")
        except Exception as e:
            messagebox.showerror("Load error", str(e))

    def decode_to_file(self):
        b64 = self.txt.get("1.0", tk.END).strip()
        if not b64:
            messagebox.showinfo("No Base64", "Paste or load Base64 text first.")
            return
        out = filedialog.asksaveasfilename(title="Save decoded file as…", defaultextension="", filetypes=[("All", "*.*")])
        if not out:
            return
        # run in bg to keep UI responsive
        self.run_bg(self._decode_worker, args=(b64, out))

    def _decode_worker(self, b64: str, out: str):
        try:
            self.set_progress(0.1)
            b64_string_to_file(b64, out)
            self.set_progress(1.0)
            messagebox.showinfo("Done", f"Decoded file saved to:\n{out}")
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Decode error", str(e))
        finally:
            self.after(400, lambda: self.set_progress(0))

    def copy_b64(self):
        content = self.txt.get("1.0", tk.END)
        if not content.strip():
            messagebox.showinfo("Nothing to copy", "No Base64 text to copy.")
            return
        self.clipboard_clear()
        self.clipboard_append(content)
        messagebox.showinfo("Copied", "Base64 text copied to clipboard.")

    def find_in_text(self):
        term = self.entry_search.get()
        if not term:
            return
        self.txt.tag_remove('search', '1.0', tk.END)
        start = '1.0'
        while True:
            pos = self.txt.search(term, start, stopindex=tk.END)
            if not pos:
                break
            end = f"{pos}+{len(term)}c"
            self.txt.tag_add('search', pos, end)
            start = end
        self.txt.tag_config('search', background='#444444', foreground='#ffffff')

    # util to run function in background thread
    def run_bg(self, target, args: tuple = ()):  
        t = threading.Thread(target=target, args=args, daemon=True)
        t.start()


if __name__ == "__main__":
    try:
        app = Base64App()
        app.mainloop()
    except Exception as e:
        print("Fatal error:", e)
