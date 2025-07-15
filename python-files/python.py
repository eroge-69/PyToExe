import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from PIL import Image, ImageTk  # Pillow required for logo
import threading

class ExcelToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Multi-Sheet Comparator & VLOOKUP Tool")
        self.root.geometry("1200x800")
        self.root.configure(bg="#232946")
        self.files = []
        self.dfs = []
        self.sheet_names = []
        self.selected_columns = []
        self.result_df = None

        # App icon/logo
        try:
            logo_img = Image.open("logo.png").resize((48, 48))
            self.logo = ImageTk.PhotoImage(logo_img)
            self.root.iconphoto(False, self.logo)
        except Exception:
            self.logo = None

        # Style
        self.set_style()

        # Menu bar
        self.create_menu()

        # UI Elements
        self.create_widgets()

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor="w", style="Status.TLabel")
        self.status_bar.pack(side=tk.BOTTOM, fill="x")

    def set_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#232946", foreground="#fffffe", font=("Segoe UI", 12))
        style.configure("TButton",
                        background="#eebbc3",
                        foreground="#232946",
                        font=("Segoe UI", 12, "bold"),
                        padding=10,
                        borderwidth=0,
                        relief="flat")
        style.map("TButton",
                  background=[("active", "#b8c1ec"), ("pressed", "#b8c1ec")],
                  relief=[("pressed", "flat"), ("!pressed", "flat")])
        style.configure("TFrame", background="#232946")
        style.configure("TLabelframe", background="#232946", foreground="#eebbc3", font=("Segoe UI", 13, "bold"))
        style.configure("TLabelframe.Label", background="#232946", foreground="#eebbc3", font=("Segoe UI", 13, "bold"))
        style.configure("Treeview", background="#121629", foreground="#fffffe", fieldbackground="#121629", font=("Segoe UI", 11), borderwidth=0)
        style.configure("Treeview.Heading", background="#eebbc3", foreground="#232946", font=("Segoe UI", 12, "bold"))
        style.map("Treeview", background=[("selected", "#eebbc3")], foreground=[("selected", "#232946")])
        style.configure("Status.TLabel", background="#121629", foreground="#eebbc3", font=("Segoe UI", 10, "italic"))

    def create_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Excel Files...", command=self.load_files)
        file_menu.add_command(label="Export Result...", command=self.export_result)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def show_about(self):
        messagebox.showinfo("About", "Excel Multi-Sheet Comparator & VLOOKUP Tool\nVersion 1.0\n© 2025 Your Company\n\nMade with ♥ for Data Comparison.")

    def create_widgets(self):
        # --- SCROLLABLE MAIN AREA ---
        main_canvas = tk.Canvas(self.root, borderwidth=0, background="#232946", highlightthickness=0)
        main_canvas.pack(side="left", fill="both", expand=True)
        vscroll = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        vscroll.pack(side="right", fill="y")
        main_canvas.configure(yscrollcommand=vscroll.set)

        # Frame inside the canvas
        self.main_frame = ttk.Frame(main_canvas)
        self.main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # --- ALL YOUR WIDGETS GO INTO self.main_frame BELOW ---
        # Logo and title
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill="x", padx=24, pady=(18, 0))
        if self.logo:
            logo_label = ttk.Label(top_frame, image=self.logo, background="#232946")
            logo_label.pack(side=tk.LEFT, padx=(0, 16))
        title_label = ttk.Label(top_frame, text="Excel Multi-Sheet Comparator & VLOOKUP Tool", font=("Segoe UI", 20, "bold"), background="#232946", foreground="#eebbc3")
        title_label.pack(side=tk.LEFT, pady=8)

        # File selection
        file_frame = ttk.Labelframe(self.main_frame, text="Step 1: Select Excel Files", padding=18)
        file_frame.pack(fill="x", padx=32, pady=16)
        ttk.Button(file_frame, text="Add Excel Files", command=self.load_files, style="TButton").pack(side=tk.LEFT, padx=10, pady=6)
        ttk.Button(file_frame, text="Clear Files", command=self.clear_files, style="TButton").pack(side=tk.LEFT, padx=10, pady=6)
        file_list_frame = ttk.Frame(file_frame)
        file_list_frame.pack(side=tk.LEFT, padx=16, pady=6, fill="both", expand=True)
        self.file_listbox = tk.Listbox(file_list_frame, width=90, height=4, bg="#232946", fg="#eebbc3", font=("Segoe UI", 11), highlightthickness=0, bd=0, relief="flat", selectbackground="#b8c1ec", selectforeground="#232946")
        self.file_listbox.pack(side=tk.LEFT, fill="both", expand=True)
        file_scrollbar = ttk.Scrollbar(file_list_frame, orient="vertical", command=self.file_listbox.yview)
        file_scrollbar.pack(side=tk.RIGHT, fill="y")
        self.file_listbox.config(yscrollcommand=file_scrollbar.set)

        # Sheet selection
        sheet_frame = ttk.Labelframe(self.main_frame, text="Step 2: Select Sheet", padding=18)
        sheet_frame.pack(fill="x", padx=32, pady=16)
        ttk.Label(sheet_frame, text="Sheet:").pack(side=tk.LEFT)
        self.sheet_combo = ttk.Combobox(sheet_frame, state="readonly", width=32, font=("Segoe UI", 11))
        self.sheet_combo.pack(side=tk.LEFT, padx=10)
        ttk.Button(sheet_frame, text="Load Sheet", command=self.load_sheet, style="TButton").pack(side=tk.LEFT, padx=10, pady=6)

        # Column selection
        col_frame = ttk.Labelframe(self.main_frame, text="Step 3: Select Columns and Operation", padding=18)
        col_frame.pack(fill="x", padx=32, pady=16)
        ttk.Label(col_frame, text="Columns:").pack(side=tk.LEFT)
        col_list_frame = ttk.Frame(col_frame)
        col_list_frame.pack(side=tk.LEFT, padx=10, pady=6)
        self.col_listbox = tk.Listbox(col_list_frame, selectmode=tk.MULTIPLE, width=48, height=7, bg="#232946", fg="#eebbc3", font=("Segoe UI", 11), highlightthickness=0, bd=0, relief="flat", selectbackground="#b8c1ec", selectforeground="#232946")
        self.col_listbox.pack(side=tk.LEFT, fill="both", expand=True)
        col_scrollbar = ttk.Scrollbar(col_list_frame, orient="vertical", command=self.col_listbox.yview)
        col_scrollbar.pack(side=tk.RIGHT, fill="y")
        self.col_listbox.config(yscrollcommand=col_scrollbar.set)
        btn_frame = ttk.Frame(col_frame)
        btn_frame.pack(side=tk.LEFT, padx=24)
        ttk.Button(btn_frame, text="Concat Columns", width=20, command=self.concat_columns, style="TButton").pack(pady=8)
        ttk.Button(btn_frame, text="Find Unique", width=20, command=self.find_unique, style="TButton").pack(pady=8)
        ttk.Button(btn_frame, text="VLOOKUP", width=20, command=self.vlookup, style="TButton").pack(pady=8)

        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, orient="horizontal", mode="indeterminate", length=300)
        self.progress.pack(pady=(0, 8))
        self.progress.pack_forget()  # Hide initially

        # Preview area
        preview_frame = ttk.Labelframe(self.main_frame, text="Step 4: Preview Results", padding=18)
        preview_frame.pack(fill="both", expand=True, padx=32, pady=16)
        tree_frame = ttk.Frame(preview_frame)
        tree_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tree_frame, show="headings", selectmode="browse")
        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        self.scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill="y")
        self.scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill="x")
        self.tree.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        # Export
        export_frame = ttk.Labelframe(self.main_frame, text="Step 5: Export", padding=18)
        export_frame.pack(fill="x", padx=32, pady=16)
        ttk.Button(export_frame, text="Export Result to Excel", command=self.export_result, style="TButton").pack(pady=6)
        ttk.Button(export_frame, text="Download Resulted Excel File", command=self.download_result, style="TButton").pack(pady=6)

    def set_status(self, msg):
        self.status_var.set(msg)
        self.root.update_idletasks()

    def run_with_progress(self, func, *args, **kwargs):
        def wrapper():
            self.progress.pack()
            self.progress.start()
            try:
                func(*args, **kwargs)
            finally:
                self.progress.stop()
                self.progress.pack_forget()
        threading.Thread(target=wrapper).start()

    def load_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Excel files", "*.xlsx *.xls")])
        if files:
            # Allow adding to the list, not just replacing
            for f in files:
                if f not in self.files:
                    self.files.append(f)
                    self.file_listbox.insert(tk.END, f)
            self.set_status(f"{len(self.files)} file(s) loaded.")
            self.load_sheet_names()

    def clear_files(self):
        self.files = []
        self.dfs = []
        self.sheet_names = []
        self.file_listbox.delete(0, tk.END)
        self.sheet_combo['values'] = []
        self.col_listbox.delete(0, tk.END)
        self.clear_preview()
        self.set_status("Files cleared.")

    def load_sheet_names(self):
        if not self.files:
            return
        try:
            xl = pd.ExcelFile(self.files[0])
            self.sheet_names = xl.sheet_names
            self.sheet_combo['values'] = self.sheet_names
            if self.sheet_names:
                self.sheet_combo.current(0)
            self.set_status("Sheet names loaded.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read sheets: {e}")
            self.set_status("Failed to read sheets.")

    def load_sheet(self):
        if not self.files or not self.sheet_combo.get():
            messagebox.showwarning("Warning", "Please select files and a sheet.")
            return
        self.set_status("Loading sheets...")
        self.run_with_progress(self._load_sheet)

    def _load_sheet(self):
        self.dfs = []
        for f in self.files:
            try:
                df = pd.read_excel(f, sheet_name=self.sheet_combo.get())
                self.dfs.append(df)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load sheet from {f}: {e}")
                self.set_status("Failed to load sheet.")
                return
        self.col_listbox.delete(0, tk.END)
        for col in self.dfs[0].columns:
            self.col_listbox.insert(tk.END, col)
        self.clear_preview()
        self.preview_df(self.dfs[0])
        self.set_status("Sheet loaded.")

    def concat_columns(self):
        indices = self.col_listbox.curselection()
        if not indices:
            messagebox.showwarning("Warning", "Select columns to concatenate.")
            return
        col_names = [self.col_listbox.get(i) for i in indices]
        for i, df in enumerate(self.dfs):
            self.dfs[i]['Concatenated'] = df[col_names].astype(str).agg(' '.join, axis=1)
        self.result_df = pd.concat(self.dfs, ignore_index=True)
        messagebox.showinfo("Success", "Columns concatenated and merged across all sheets.")
        self.preview_df(self.result_df)
        self.set_status("Columns concatenated.")

    def find_unique(self):
        if len(self.dfs) < 2:
            messagebox.showwarning("Warning", "Need at least 2 files loaded for unique row comparison.")
            return

        select_win = tk.Toplevel(self.root)
        select_win.title("Select Columns for Unique Row Comparison")
        select_win.configure(bg="#232946")
        tk.Label(select_win, text="Select column from first sheet:", bg="#232946", fg="#eebbc3", font=("Segoe UI", 12)).pack(pady=(10, 2))
        col1_var = tk.StringVar()
        col1_combo = ttk.Combobox(select_win, textvariable=col1_var, values=list(self.dfs[0].columns), state="readonly", font=("Segoe UI", 11))
        col1_combo.pack(pady=4)
        tk.Label(select_win, text="Select column from second sheet:", bg="#232946", fg="#eebbc3", font=("Segoe UI", 12)).pack(pady=(10, 2))
        col2_var = tk.StringVar()
        col2_combo = ttk.Combobox(select_win, textvariable=col2_var, values=list(self.dfs[1].columns), state="readonly", font=("Segoe UI", 11))
        col2_combo.pack(pady=4)

        def on_ok():
            col1 = col1_var.get()
            col2 = col2_var.get()
            if not col1 or not col2:
                messagebox.showwarning("Warning", "Please select columns from both sheets.")
                return
            s1 = set(self.dfs[0][col1].astype(str))
            s2 = set(self.dfs[1][col2].astype(str))
            unique1 = self.dfs[0][~self.dfs[0][col1].astype(str).isin(s2)]
            unique2 = self.dfs[1][~self.dfs[1][col2].astype(str).isin(s1)]
            result = pd.concat([
                unique1.assign(_Source="Sheet 1"),
                unique2.assign(_Source="Sheet 2")
            ], ignore_index=True)
            self.result_df = result
            self.preview_df(self.result_df)
            select_win.destroy()
            messagebox.showinfo("Success", "Unique rows found and displayed.")
            self.set_status("Unique rows found.")

        ttk.Button(select_win, text="OK", command=on_ok, style="TButton").pack(pady=14)

    def vlookup(self):
        indices = self.col_listbox.curselection()
        if len(self.dfs) < 2 or not indices:
            messagebox.showwarning("Warning", "Need at least 2 files and select a column for VLOOKUP.")
            return
        col_name = self.col_listbox.get(indices[0])
        left = self.dfs[0]
        right = self.dfs[1]
        try:
            merged = pd.merge(left, right, on=col_name, how='left', suffixes=('_file1', '_file2'))
            self.result_df = merged
            messagebox.showinfo("Success", f"VLOOKUP completed on column '{col_name}'.")
            self.preview_df(self.result_df)
            self.set_status("VLOOKUP completed.")
        except Exception as e:
            messagebox.showerror("Error", f"VLOOKUP failed: {e}")
            self.set_status("VLOOKUP failed.")

    def export_result(self):
        if self.result_df is None:
            messagebox.showwarning("Warning", "No result to export.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file:
            try:
                self.result_df.to_excel(file, index=False)
                messagebox.showinfo("Success", f"Result exported to {file}")
                self.set_status(f"Result exported to {file}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
                self.set_status("Export failed.")

    def download_result(self):
        if self.result_df is None:
            messagebox.showwarning("Warning", "No result to download.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], title="Download Resulted Excel File")
        if file:
            try:
                self.result_df.to_excel(file, index=False)
                messagebox.showinfo("Success", f"Resulted Excel file downloaded to {file}")
                self.set_status(f"Resulted Excel file downloaded to {file}")
            except Exception as e:
                messagebox.showerror("Error", f"Download failed: {e}")
                self.set_status("Download failed.")

    def preview_df(self, df):
        self.clear_preview()
        if df is None or df.empty:
            return
        self.tree["columns"] = list(df.columns)
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="w")
        for _, row in df.head(100).iterrows():
            self.tree.insert("", "end", values=list(row))

    def clear_preview(self):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = []

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelToolApp(root)
    root.mainloop()