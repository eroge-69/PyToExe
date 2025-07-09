import pandas as pd
import os
from tkinter import Tk, Label, StringVar, ttk, Entry, Button, Scrollbar, VERTICAL, HORIZONTAL, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate

def export_to_pdf(self, path):
    data = [list(self.df.columns)] + self.df.astype(str).values.tolist()

    pdf = SimpleDocTemplate(path, pagesize=letter)
    table = Table(data)

    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
    ])
    table.setStyle(style)

    pdf.build([table])


EXPECTED_COLS = {
    "EMPLOYEE NAME": "Employee Name",
    "REG": "REG",
    "OT1": "OT1",
    "OT2": "OT2",
    "VAC": "VAC",
    "HOL": "HOL",
    "SIC": "SIC",
    "OTH": "OTH",
    "TOTAL": "Total"
}


class TimecardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🕒 Timecard Summary Tool")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f0f0")

        Label(root, text="📄 Drag and Drop Timecard CSV File Here", font=("Arial", 14), bg="#f0f0f0").pack(pady=10)

        self.status_var = StringVar()
        Label(root, textvariable=self.status_var, wraplength=980, bg="#f0f0f0", fg="green").pack(pady=5)

        self.tree = None
        self.tree_frame = None
        self.df = None

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_file_drop)

        self.save_btn = Button(root, text="💾 Save Summary", command=self.save_output, state='disabled')
        self.save_btn.pack(pady=10)

    def on_file_drop(self, event):
        file_path = event.data.strip("{}")
        self.process_file(file_path)

    def process_file(self, file_path):
        try:
            df = pd.read_csv(file_path, skiprows=4)
            df.columns = df.columns.str.upper().str.strip()

            missing = [col for col in EXPECTED_COLS if col not in df.columns]
            if missing:
                self.status_var.set(f"❌ Missing columns: {', '.join(missing)}")
                return

            df = df[EXPECTED_COLS.keys()].rename(columns=EXPECTED_COLS)

            grouped = df.groupby("Employee Name", as_index=False).sum()
            
            # 🔽 Round all numeric columns to 2 decimal places
            for col in grouped.columns:
                if col != "Employee Name":
                    grouped[col] = grouped[col].round(2)
            
            # Separate TOTAL row (case-insensitive match)
            total_row = grouped[grouped["Employee Name"].str.upper() == "TOTAL"]
            grouped = grouped[grouped["Employee Name"].str.upper() != "TOTAL"]

            # Sort everyone else alphabetically
            grouped = grouped.sort_values("Employee Name").reset_index(drop=True)

            # Reattach TOTAL row at the end (if it exists)
            if not total_row.empty:
                grouped = pd.concat([grouped, total_row], ignore_index=True)

            grouped["Days Worked"] = ""

            self.df = grouped
            self.display_table()
            self.status_var.set(f"✅ Loaded {len(self.df)} employees. You can now enter days worked.")
            self.save_btn.config(state='normal')

        except Exception as e:
            self.status_var.set(f"❌ Error: {e}")

    def display_table(self):
        if self.tree_frame:
            self.tree_frame.destroy()

        self.tree_frame = ttk.Frame(self.root)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = list(self.df.columns)
        self.tree = ttk.Treeview(self.tree_frame, columns=cols, show='headings', height=20)

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')

        vsb = Scrollbar(self.tree_frame, orient=VERTICAL, command=self.tree.yview)
        hsb = Scrollbar(self.tree_frame, orient=HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        for _, row in self.df.iterrows():
            self.tree.insert("", "end", values=list(row))

        # Make Days Worked editable
        self.tree.bind('<Double-1>', self.edit_cell)

    def edit_cell(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        row_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        col_idx = int(col.replace("#", "")) - 1
        if self.tree["columns"][col_idx] != "Days Worked":
            return

        x, y, width, height = self.tree.bbox(row_id, col)
        value = self.tree.set(row_id, col)

        entry = Entry(self.tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()

        def on_focus_out(event):
            new_value = entry.get()
            self.tree.set(row_id, col, new_value)
            entry.destroy()

        entry.bind("<FocusOut>", on_focus_out)
        entry.bind("<Return>", lambda e: entry.master.focus())

    

    def export_to_pdf(self, path):
        data = [list(self.df.columns)] + self.df.astype(str).values.tolist()

        pdf = SimpleDocTemplate(path, pagesize=letter)
        table = Table(data)

        style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ])
        table.setStyle(style)

        pdf.build([table])

    def save_output(self):
        # Collect Days Worked from the Treeview
        for i, row_id in enumerate(self.tree.get_children()):
            values = self.tree.item(row_id)['values']
            self.df.at[i, 'Days Worked'] = values[-1]

        # File type selection dialog
        file_path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".pdf",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv")
            ],
            initialfile="Timecard_Summary"
        )

        if not file_path:
            self.status_var.set("❌ Save cancelled.")
            return  # user cancelled

        try:
            ext = os.path.splitext(file_path)[1].lower()

            if ext == ".csv":
                self.df.to_csv(file_path, index=False)
            elif ext == ".xlsx":
                self.df.to_excel(file_path, index=False, engine='openpyxl')
            elif ext == ".pdf":
                self.export_to_pdf(file_path)
            else:
                self.status_var.set("❌ Unsupported file format.")
                return

            self.status_var.set(f"✅ Summary saved to: {file_path}")

        except Exception as e:
            self.status_var.set(f"❌ Error saving file: {e}")

if __name__ == "__main__":
    from tkinter import _default_root
    if _default_root is not None:
        _default_root.destroy()
    root = TkinterDnD.Tk()
    app = TimecardApp(root)
    root.mainloop()
