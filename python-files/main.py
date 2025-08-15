import tkinter as tk
from tkinter import ttk, messagebox

# === FIXTURE LIBRARY ===
fixture_library = {
    "PAR LED 7x10W": 7,
    "Moving Head Spot": 16,
    "Moving Head Beam": 18,
    "Wash 36x3W": 10,
    "Blinder 2x100W": 4,
    "Laser RGB": 12,
    "Strobe": 6
}

DMX_CHANNELS_PER_UNIVERSE = 512


class DMXOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("DMX Channel Organizer")

        # Variables
        self.universe_count = tk.IntVar(value=1)
        self.fixtures = []

        # === UI ===
        tk.Label(root, text="Number of Universes:").grid(row=0, column=0, padx=5, pady=5)
        self.universe_dropdown = ttk.Combobox(root, textvariable=self.universe_count, values=list(range(1, 11)), state="readonly")
        self.universe_dropdown.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Fixture Type:").grid(row=1, column=0, padx=5, pady=5)
        self.fixture_type_var = tk.StringVar()
        self.fixture_dropdown = ttk.Combobox(root, textvariable=self.fixture_type_var, values=list(fixture_library.keys()), state="readonly")
        self.fixture_dropdown.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(root, text="Add Fixture", command=self.add_fixture).grid(row=1, column=2, padx=5, pady=5)

        self.tree = ttk.Treeview(root, columns=("Type", "Universe", "Start", "End"), show="headings", height=12)
        self.tree.grid(row=2, column=0, columnspan=3, padx=5, pady=5)
        for col in ("Type", "Universe", "Start", "End"):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        tk.Button(root, text="Clear All", command=self.clear_all).grid(row=3, column=0, padx=5, pady=5)
        tk.Button(root, text="Exit", command=root.quit).grid(row=3, column=2, padx=5, pady=5)

    def add_fixture(self):
        fixture_type = self.fixture_type_var.get()
        if not fixture_type:
            messagebox.showwarning("Warning", "Please select a fixture type.")
            return

        channels_needed = fixture_library[fixture_type]

        # Calculate next available channel
        if not self.fixtures:
            universe, start_ch = 1, 1
        else:
            last_uni, last_end = self.fixtures[-1][1], self.fixtures[-1][3]
            if last_end + channels_needed <= DMX_CHANNELS_PER_UNIVERSE:
                universe, start_ch = last_uni, last_end + 1
            else:
                universe, start_ch = last_uni + 1, 1

        # Check if we exceed universe limit
        if universe > self.universe_count.get():
            messagebox.showerror("Error", "No more free universes available.")
            return

        end_ch = start_ch + channels_needed - 1
        self.fixtures.append((fixture_type, universe, start_ch, end_ch))
        self.tree.insert("", "end", values=(fixture_type, universe, start_ch, end_ch))

    def clear_all(self):
        self.fixtures.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)


if _name_ == "_main_":
    root = tk.Tk()
    app = DMXOrganizer(root)
    root.mainloop()
    