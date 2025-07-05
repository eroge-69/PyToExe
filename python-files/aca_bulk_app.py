import tkinter as tk
from tkinter import ttk, messagebox
import os

class ACABulkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ACA Bulk Entry Application")
        self.data = []

        self.columns = ['A', 'B', 'C', 'D', 'E', 'F']
        self.tree = ttk.Treeview(root, columns=self.columns, show='headings')
        
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(fill='both', expand=True)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Row", command=self.add_row).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Generate TXT", command=self.export_txt).pack(side='left', padx=5)

        self.add_row()  # start with one row

    def add_row(self):
        row_idx = len(self.data)
        row = []

        def update_BF(*args):
            a = a_var.get()
            c = c_var.get()
            d = d_var.get()
            e = e_var.get()

            # B formula
            if c == "D":
                b_val = "400034101406010"
            elif a == "":
                b_val = ""
            elif len(a) == 6:
                b_val = "4000341030" + a
            else:
                b_val = "40003410" + a
            b_var.set(b_val)

            # F formula
            if e == "":
                f_var.set("")
            else:
                amount_str = ""
                try:
                    amount_str = f"{float(d):015.2f}"
                except:
                    amount_str = "00000000000000.00"
                f_val = f"{b_val} INR400034  {c}{amount_str}{e}"
                f_var.set(f_val)

        # Entry variables
        a_var = tk.StringVar()
        b_var = tk.StringVar()
        c_var = tk.StringVar()
        d_var = tk.StringVar()
        e_var = tk.StringVar()
        f_var = tk.StringVar()

        for var in (a_var, c_var, d_var, e_var):
            var.trace_add('write', update_BF)

        # Row UI
        frame = tk.Frame(self.tree)
        entries = []

        for idx, var in enumerate([a_var, b_var, c_var, d_var, e_var, f_var]):
            if self.columns[idx] == 'C':
                cb = ttk.Combobox(frame, textvariable=var, values=["C", "D"], width=10, state="readonly")
                cb.current(0)
                cb.grid(row=0, column=idx)
                entries.append(cb)
            elif self.columns[idx] in ['B', 'F']:
                entry = ttk.Entry(frame, textvariable=var, width=18, state="readonly")
                entry.grid(row=0, column=idx)
                entries.append(entry)
            else:
                entry = ttk.Entry(frame, textvariable=var, width=18)
                entry.grid(row=0, column=idx)
                entries.append(entry)

        self.tree.insert('', 'end', values=[""]*6, tags=(str(row_idx),))
        self.tree.set(str(row_idx), column='A', value=frame)
        self.tree.item(str(row_idx), tags=(frame,))

        self.data.append((a_var, b_var, c_var, d_var, e_var, f_var))

    def export_txt(self):
        lines = []
        for row in self.data:
            f_val = row[5].get()
            if f_val.strip():
                lines.append(f_val)

        try:
            with open("output.txt", "w") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("Success", "output.txt generated successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# Launch app
if __name__ == "__main__":
    root = tk.Tk()
    app = ACABulkApp(root)
    root.mainloop()
