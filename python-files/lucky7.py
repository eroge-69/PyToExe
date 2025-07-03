import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd

class LuckyDrawApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lucky Draw Application")

        # Try fullscreen on Windows; fallback to large window
        try:
            self.root.state('zoomed')  # Maximize (Windows only)
        except:
            self.root.geometry("1200x800")  # Fallback size

        self.data = pd.DataFrame(columns=["ID", "Name"])
        self.winner_list = []

        # --- Upload CSV ---
        tk.Button(root, text="Upload CSV", command=self.load_csv, width=20).pack(pady=10)

        # --- Manual Entry ---
        self.entry_frame = tk.Frame(root)
        self.entry_frame.pack(pady=10)

        tk.Label(self.entry_frame, text="Enter ID:", font=("Arial", 12)).grid(row=0, column=0, padx=5)
        self.id_entry = tk.Entry(self.entry_frame, width=25, font=("Arial", 12))
        self.id_entry.grid(row=0, column=1, padx=5)

        self.search_button = tk.Button(self.entry_frame, text="Find Name", command=self.find_name, width=15)
        self.search_button.grid(row=0, column=2, padx=5)

        # --- Display Name ---
        tk.Label(root, text="User Name:", font=("Arial", 12)).pack()
        self.name_var = tk.StringVar()
        self.name_display = tk.Label(root, textvariable=self.name_var, font=("Arial", 14), fg="blue")
        self.name_display.pack(pady=5)

        # --- Table Header ---
        tk.Label(root, text="Lucky Draw Winner List", font=("Arial", 14, "bold")).pack(pady=10)

        # --- Table + Scrollbar ---
        table_frame = tk.Frame(root)
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("No", "ID", "Name"), show="headings", height=20)
        self.tree.heading("No", text="No")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.column("No", width=60, anchor="center")
        self.tree.column("ID", width=150, anchor="center")
        self.tree.column("Name", width=500, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # --- Action Buttons ---
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=20)

        tk.Button(self.button_frame, text="Export as CSV", command=self.export_csv, width=20).grid(row=0, column=0, padx=10)
        tk.Button(self.button_frame, text="Copy Table", command=self.copy_to_clipboard, width=20).grid(row=0, column=1, padx=10)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                self.data = pd.read_csv(file_path)
                if "ID" not in self.data.columns or "Name" not in self.data.columns:
                    messagebox.showerror("Invalid File", "CSV must contain 'ID' and 'Name' columns.")
                else:
                    messagebox.showinfo("Success", "CSV data loaded successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def find_name(self):
        input_id = self.id_entry.get().strip()
        if not input_id:
            messagebox.showwarning("Input Error", "Please enter an ID.")
            return

        matched = self.data[self.data["ID"].astype(str) == input_id]
        if matched.empty:
            self.name_var.set("Not Found")
        else:
            name = matched.iloc[0]["Name"]
            self.name_var.set(name)

            if input_id in [item[0] for item in self.winner_list]:
                messagebox.showinfo("Duplicate", "This ID is already in the winner list.")
                return

            self.add_to_table(input_id, name)

    def add_to_table(self, id_val, name_val):
        index = len(self.winner_list) + 1
        self.tree.insert("", "end", values=(index, id_val, name_val))
        self.winner_list.append((id_val, name_val))

    def export_csv(self):
        if not self.winner_list:
            messagebox.showwarning("Export Error", "No data to export.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                df = pd.DataFrame(self.winner_list, columns=["ID", "Name"])
                df.insert(0, "No", range(1, len(df) + 1))
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Exported", f"Winner list exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Failed", str(e))

    def copy_to_clipboard(self):
        if not self.winner_list:
            messagebox.showwarning("Copy Error", "No data to copy.")
            return

        try:
            df = pd.DataFrame(self.winner_list, columns=["ID", "Name"])
            df.insert(0, "No", range(1, len(df)+1))
            text = df.to_string(index=False)
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            messagebox.showinfo("Copied", "Table copied to clipboard.")
        except Exception as e:
            messagebox.showerror("Copy Failed", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = LuckyDrawApp(root)
    root.mainloop()
