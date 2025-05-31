import tkinter as tk
from tkinter import ttk

# Sample cause-effect data
data = {
    "IS1": {"cause": ["IS3", "High temperature"], "effect": ["IS2", "Shutdown system"]},
    "IS2": {"cause": ["IS1", "Manual override"], "effect": ["IS6"]},
    "IS3": {"cause": ["Sensor failure"], "effect": ["IS1"]},
    "IS4": {"cause": [], "effect": ["IS1"]},
    "IS5": {"cause": ["IS1"], "effect": ["Alarm triggered"]},
    "IS6": {"cause": ["IS2"], "effect": ["Report generated"]},
    "Manual override": {"cause": ["IS4"], "effect": ["IS2"]},
}

class ISExplorerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IS Cause and Effect Explorer")
        self.root.geometry("600x400")

        # Dropdown
        dropdown_frame = tk.Frame(root)
        dropdown_frame.pack(pady=10)

        tk.Label(dropdown_frame, text="Select IS Block:", font=('Arial', 12)).pack(side="left")
        self.selected_is = tk.StringVar()
        self.dropdown = ttk.Combobox(dropdown_frame, textvariable=self.selected_is, values=list(data.keys()), state="readonly")
        self.dropdown.pack(side="left", padx=10)
        self.dropdown.bind("<<ComboboxSelected>>", self.display_info)

        # Tables Frame
        tables_frame = tk.Frame(root)
        tables_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Cause Table
        self.cause_box = ttk.LabelFrame(tables_frame, labelanchor="n")
        self.cause_box.config(labelwidget=tk.Label(self.cause_box, text="Causes", font=('Arial', 25, 'bold')))
        self.cause_box.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.cause_tree = ttk.Treeview(self.cause_box, columns=("Item",), show="headings", selectmode="none", height=15)
        self.cause_tree.heading("Item", text="Cause Items")
        self.cause_tree.pack(fill="both", expand=True)
        self.cause_tree.bind("<ButtonRelease-1>", self.on_tree_click)

        # Effect Table
        self.effect_box = ttk.LabelFrame(tables_frame, labelanchor="n")
        self.effect_box.config(labelwidget=tk.Label(self.effect_box, text="Effects", font=('Arial', 25, 'bold')))
        self.effect_box.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.effect_tree = ttk.Treeview(self.effect_box, columns=("Item",), show="headings", selectmode="none", height=15)
        self.effect_tree.heading("Item", text="Effect Items")
        self.effect_tree.pack(fill="both", expand=True)
        self.effect_tree.bind("<ButtonRelease-1>", self.on_tree_click)

        # Apply alternating row colors
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
        if is_block not in data:
            return

        self.clear_tables()

        causes = data[is_block].get("cause", [])
        effects = data[is_block].get("effect", [])

        self.populate_table(self.cause_tree, causes)
        self.populate_table(self.effect_tree, effects)

    def populate_table(self, tree, items):
        for index, item in enumerate(items):
            is_clickable = item in data
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
        if item_text in data:
            self.selected_is.set(item_text)
            self.display_info()

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = ISExplorerApp(root)
    root.mainloop()
