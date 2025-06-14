import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

class ConditionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Condition Tracker")
        self.root.geometry("950x650")

        self.status_options = ["Pending", "Done", "Deferred"]
        self.data = []

        self.setup_widgets()

    def setup_widgets(self):
        # Search bar
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.root, textvariable=self.search_var, width=50)
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<KeyRelease>", self.refresh_list)

        # Form for adding a single condition
        form_frame = tk.Frame(self.root)
        form_frame.pack(pady=10)

        self.condition_entry = tk.Entry(form_frame, width=50)
        self.condition_entry.grid(row=0, column=0, padx=5)

        self.status_var = tk.StringVar(value="Pending")
        self.status_menu = ttk.Combobox(form_frame, textvariable=self.status_var, values=self.status_options, width=12)
        self.status_menu.grid(row=0, column=1, padx=5)

        add_btn = tk.Button(form_frame, text="Add Condition", command=self.add_condition)
        add_btn.grid(row=0, column=2, padx=5)

        bulk_btn = tk.Button(form_frame, text="Paste Multiple Conditions", command=self.open_bulk_paste_window)
        bulk_btn.grid(row=0, column=3, padx=5)

        # Condition list frame
        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(pady=10, fill="both", expand=True)

        # Save Button
        save_btn = tk.Button(self.root, text="Save Changes", command=self.save_to_excel)
        save_btn.pack(pady=5)

        # Export buttons
        export_frame = tk.Frame(self.root)
        export_frame.pack(pady=10)

        tk.Button(export_frame, text="Export Pending", command=lambda: self.export_to_excel("Pending")).grid(row=0, column=0, padx=10)
        tk.Button(export_frame, text="Export Deferred", command=lambda: self.export_to_excel("Deferred")).grid(row=0, column=1, padx=10)

        self.refresh_list()

    def add_condition(self):
        text = self.condition_entry.get().strip()
        status = self.status_var.get()
        if not text:
            messagebox.showwarning("Empty", "Please enter a condition.")
            return
        self.data.append({"Condition": text, "Status": status})
        self.condition_entry.delete(0, tk.END)
        self.status_var.set("Pending")
        self.refresh_list()

    def refresh_list(self, event=None):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        search_text = self.search_var.get().strip().lower()
        status_colors = {
            "Done": "light green",
            "Pending": "yellow",
            "Deferred": "light blue"
        }

        for index, item in enumerate(self.data):
            if search_text in item["Condition"].lower():
                row_frame = tk.Frame(self.list_frame)
                row_frame.pack(fill="x", padx=10, pady=2)

                cond_var = tk.StringVar(value=item["Condition"])
                status_var = tk.StringVar(value=item["Status"])

                cond_entry = tk.Entry(row_frame, textvariable=cond_var, width=50,
                                      bg=status_colors.get(item["Status"], "white"))
                cond_entry.pack(side="left", padx=5)

                status_menu = ttk.Combobox(row_frame, textvariable=status_var, values=self.status_options, width=12)
                status_menu.pack(side="left", padx=5)

                update_btn = tk.Button(row_frame, text="Update",
                                       command=lambda i=index, c=cond_var, s=status_var: self.update_condition(i, c, s))
                update_btn.pack(side="left", padx=5)

                delete_btn = tk.Button(row_frame, text="Delete", command=lambda i=index: self.delete_condition(i))
                delete_btn.pack(side="left", padx=5)

    def update_condition(self, index, cond_var, status_var):
        text = cond_var.get().strip()
        status = status_var.get()
        if not text:
            messagebox.showwarning("Empty", "Condition cannot be empty.")
            return
        self.data[index] = {"Condition": text, "Status": status}
        self.refresh_list()

    def delete_condition(self, index):
        del self.data[index]
        self.refresh_list()

    def export_to_excel(self, status_filter):
        df = pd.DataFrame(self.data)
        filtered = df[df["Status"] == status_filter]
        if filtered.empty:
            messagebox.showinfo("No Data", f"No {status_filter} conditions found.")
            return
        file_name = f"{status_filter}_Conditions.xlsx"
        filtered.to_excel(file_name, index=False)
        messagebox.showinfo("Exported", f"{file_name} saved.")

    def save_to_excel(self):
        if not self.data:
            messagebox.showinfo("No Data", "There are no conditions to save.")
            return

        df = pd.DataFrame(self.data)
        file_name = "conditions.xlsx"
        df.to_excel(file_name, index=False)
        messagebox.showinfo("Saved", f"All conditions have been saved to {file_name}.")

    def open_bulk_paste_window(self):
        bulk_window = tk.Toplevel(self.root)
        bulk_window.title("Paste Multiple Conditions")
        bulk_window.geometry("600x400")

        tk.Label(bulk_window, text="Paste one condition per line:").pack(pady=5)

        text_box = tk.Text(bulk_window, wrap=tk.WORD)
        text_box.pack(padx=10, pady=5, fill="both", expand=True)

        status_var = tk.StringVar(value="Pending")
        status_menu = ttk.Combobox(bulk_window, textvariable=status_var, values=self.status_options, width=15)
        status_menu.pack(pady=5)

        def add_bulk_conditions():
            text = text_box.get("1.0", tk.END).strip()
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if not lines:
                messagebox.showwarning("Empty", "No conditions to add.")
                return
            for line in lines:
                self.data.append({"Condition": line, "Status": status_var.get()})
            self.refresh_list()
            bulk_window.destroy()

        tk.Button(bulk_window, text="Add All", command=add_bulk_conditions).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = ConditionApp(root)
    root.mainloop()
