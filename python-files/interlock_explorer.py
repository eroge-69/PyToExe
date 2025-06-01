import tkinter as tk
from tkinter import ttk
import pandas as pd
from pathlib import Path

# Get the directory where the script is located
SCRIPT_DIR = Path(__file__).resolve().parent
CSV_FILENAME = "master_interlock.csv"
CSV_PATH = SCRIPT_DIR / CSV_FILENAME

# Create empty CSV in script directory if missing
def create_csv_if_missing(path=CSV_PATH):
    if not path.exists():
        df = pd.DataFrame(columns=["key", "cause", "effect", "remark"])
        df.to_csv(path, index=False)
        print(f"Created empty CSV, copy the master data")
    else:
        #print(f"CSV already exists: {path}")
        None

# Load and parse CSV into data dict
def build_is_data_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    df.dropna(how='all', inplace=True)

    data_dict = {}

    for _, row in df.iterrows():
        key = str(row['key']).strip()
        if not key:
            continue

        if key not in data_dict:
            data_dict[key] = {"cause": [], "effect": [], "remark": []}

        for col in ["cause", "effect", "remark"]:
            value = row.get(col)
            if pd.notna(value) and str(value).strip():
                data_dict[key][col].append(str(value).strip())

    return data_dict

# GUI App Class
class ISExplorerApp:
    def __init__(self, root, data):
        self.root = root
        self.root.title("IS Cause and Effect Explorer")
        self.root.geometry("800x600")
        self.data = data

        # Dropdown
        dropdown_frame = tk.Frame(root)
        dropdown_frame.pack(pady=10, fill="x")

        tk.Label(dropdown_frame, text="Select IS Block:", font=('Arial', 12)).pack(side="left")
        self.selected_is = tk.StringVar()
        self.dropdown = ttk.Combobox(dropdown_frame, textvariable=self.selected_is, values=list(self.data.keys()), state="readonly")
        self.dropdown.pack(side="left", padx=10, fill="x", expand=True)
        self.dropdown.bind("<<ComboboxSelected>>", self.display_info)

        if self.data:
            longest = max(len(str(k)) for k in self.data.keys())
            self.dropdown.config(width=longest)

        # Tables Frame
        tables_frame = tk.Frame(root)
        tables_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.cause_box = ttk.LabelFrame(tables_frame, labelanchor="n")
        self.cause_box.config(labelwidget=tk.Label(self.cause_box, text="Causes", font=('Arial', 18, 'bold')))
        self.cause_box.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.cause_tree = ttk.Treeview(self.cause_box, columns=("Item",), show="headings", selectmode="none", height=15)
        self.cause_tree.heading("Item", text="Cause Items")
        self.cause_tree.pack(fill="both", expand=True)
        self.cause_tree.bind("<ButtonRelease-1>", self.on_tree_click)

        self.effect_box = ttk.LabelFrame(tables_frame, labelanchor="n")
        self.effect_box.config(labelwidget=tk.Label(self.effect_box, text="Effects", font=('Arial', 18, 'bold')))
        self.effect_box.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.effect_tree = ttk.Treeview(self.effect_box, columns=("Item",), show="headings", selectmode="none", height=15)
        self.effect_tree.heading("Item", text="Effect Items")
        self.effect_tree.pack(fill="both", expand=True)
        self.effect_tree.bind("<ButtonRelease-1>", self.on_tree_click)

        # Remark Area
        self.remark_frame = tk.Frame(root)
        self.remark_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.remark_label = tk.Label(self.remark_frame, text="Remarks:", font=("Arial", 14, "bold"))
        self.remark_label.pack(anchor="w")

        self.remark_text = tk.Text(self.remark_frame, height=4, font=("Arial", 11), wrap="word")
        self.remark_text.pack(fill="x", expand=True)
        self.remark_text.config(state="disabled", bg="#f9f9f9")

        # Treeview Styling
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.map("Treeview", background=[('selected', '#cce6ff')])
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        self.cause_tree.tag_configure("odd", background="white")
        self.cause_tree.tag_configure("even", background="#f0f0f0")
        self.effect_tree.tag_configure("odd", background="white")
        self.effect_tree.tag_configure("even", background="#f0f0f0")

    def display_info(self, event=None):
        is_block = self.selected_is.get()
        if is_block not in self.data:
            return

        self.clear_tables()

        causes = self.data[is_block].get("cause", [])
        effects = self.data[is_block].get("effect", [])
        remarks = self.data[is_block].get("remark", [])

        self.populate_table(self.cause_tree, causes)
        self.populate_table(self.effect_tree, effects)

        self.remark_text.config(state="normal")
        self.remark_text.delete("1.0", tk.END)
        if remarks:
            self.remark_text.insert(tk.END, "\n".join(remarks))
        else:
            self.remark_text.insert(tk.END, "No remarks.")
        self.remark_text.config(state="disabled")

    def populate_table(self, tree, items):
        for index, item in enumerate(items):
            is_clickable = item in self.data
            tag = "clickable" if is_clickable else "static"
            color_tag = "even" if index % 2 == 0 else "odd"
            tree.insert("", "end", values=(item,), tags=(tag, color_tag))

        tree.tag_configure("clickable", foreground="blue", font=("Arial", 10, "underline"))
        tree.tag_configure("static", foreground="black", font=("Arial", 10))

    def clear_tables(self):
        for tree in [self.cause_tree, self.effect_tree]:
            for item in tree.get_children():
                tree.delete(item)

    def on_tree_click(self, event):
        tree = event.widget
        item_id = tree.identify_row(event.y)
        if not item_id:
            return
        item_text = tree.item(item_id, "values")[0]
        if item_text in self.data:
            self.selected_is.set(item_text)
            self.display_info()

# Main
if __name__ == "__main__":
    create_csv_if_missing(CSV_PATH)
    is_data = build_is_data_from_csv(CSV_PATH)
    root = tk.Tk()
    app = ISExplorerApp(root, is_data)
    root.mainloop()
