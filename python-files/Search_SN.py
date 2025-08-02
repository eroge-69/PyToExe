import tkinter as tk
from tkinter import ttk, messagebox
import pickle
from pathlib import Path
LOOKUP_FILE = "POS_data.pkl"

class LookupApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Search Serial / Terminal")
        self.geometry("500x300")
        self.resizable(False, False)
        self.data = self.load_lookup_data()
        self.create_widgets()

    def load_lookup_data(self):
        if not Path(LOOKUP_FILE).exists():
            messagebox.showerror("خطأ", f"ملف البحث مش موجود: {POS_data}")
            self.destroy()
            return {}
        try:
            with open(LOOKUP_FILE, "rb") as f:
                data = pickle.load(f)
            return data
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في قراءة {POS_data}:\n{e}")
            self.destroy()
            return {}

    def create_widgets(self):
        frame = ttk.Frame(self, padding=15)
        frame.pack(fill="both", expand=True)

        self.mode_var = tk.StringVar(value="serial")
        ttk.Radiobutton(frame, text="Serial", value="serial", variable=self.mode_var).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Radiobutton(frame, text="Terminal", value="terminal", variable=self.mode_var).grid(row=0, column=2, sticky="w", padx=5)

        ttk.Label(frame, text="Input Serial / Terminal:").grid(row=1, column=0, sticky="w", pady=(10,0))
        self.entry = ttk.Entry(frame, width=30)
        self.entry.grid(row=1, column=1, columnspan=2, sticky="w", pady=(10,0))

        self.btn = ttk.Button(frame, text="Search ", command=self.lookup)
        self.btn.grid(row=2, column=1, pady=15)

        sep = ttk.Separator(frame, orient="horizontal")
        sep.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)

        self.result_text = tk.Text(frame, height=6, width=55, state="disabled", wrap="word")
        self.result_text.grid(row=4, column=0, columnspan=3, pady=(0,5))

        self.clip_btn = ttk.Button(frame, text="Copy", command=self.copy_result)
        self.clip_btn.grid(row=5, column=1, pady=(0,5))

    def lookup(self):
        val = self.entry.get().strip()
        if not val:
            messagebox.showwarning("نقص", "اكتب Serial أو Terminal.")
            return

        mode = self.mode_var.get()
        out = ""
        if mode == "serial":
            info = self.data.get("serial_to_info", {}).get(str(val))
            if not info:
                out = f"No data for this Serial = {val}"
            else:
                terminal, date = info
                out = (
                    f"Serial: {val}\n"
                    f"(Ordered Date): {date}\n"
                    f"Terminal : {terminal}"
                )
        else:
            info = self.data.get("terminal_to_info", {}).get(str(val))
            if not info:
                out = f"No data for this Terminal = {val}"
            else:
                serial, date = info
                out = (
                    f"Terminal: {val}\n"
                    f"(Ordered Date): {date}\n"
                    f"Serial: {serial}"
                )
        self.show_result(out)

    def show_result(self, text):
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.result_text.config(state="disabled")
        self.last_result = text

    def copy_result(self):
        if hasattr(self, "last_result") and self.last_result:
            self.clipboard_clear()
            self.clipboard_append(self.last_result)


if __name__ == "__main__":
    app = LookupApp()
    app.mainloop()
