#!/usr/bin/env python3
"""
Club dues tracker – persistent version (with in‑place status popup).
"""

import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox


# ----------------------------------------------------------------------
# Data model
# ----------------------------------------------------------------------
class Member:
    """Container for a club member."""

    def __init__(
        self, name: str, paid: bool = False, date_added: str | None = None
    ):
        self.name = name
        self.paid = paid
        self.date_added = date_added or datetime.now().strftime("%Y-%m-%d %H:%M")

    def __lt__(self, other: "Member") -> bool:
        """Sort key: unpaid → paid, then by name."""
        return (self.paid, self.name) < (other.paid, other.name)

    def to_dict(self):
        """Convert to JSON‑serialisable dictionary."""
        return {"name": self.name, "paid": self.paid, "date_added": self.date_added}

    @staticmethod
    def from_dict(d):
        """Create a Member instance from a dict."""
        return Member(d["name"], d.get("paid", False), d.get("date_added"))


# ----------------------------------------------------------------------
# GUI application
# ----------------------------------------------------------------------
class DuesTracker(tk.Tk):
    DATA_FILE = "members.json"

    def __init__(self):
        super().__init__()
        self.title("Masonic Club 101 Dues Tracker – By John Poulin")

        # Larger, resizable window
        self.geometry("850x600")  # width x height
        self.resizable(True, True)

        # Keep a reference to a possible in‑place edit frame
        self.edit_frame = None

        # ---- data -------------------------------------------------------
        self.members: list[Member] = []

        # ---- load data --------------------------------------------------
        self.load_data()

        # ---- UI ---------------------------------------------------------
        self.create_widgets()

        # ---- close handling --------------------------------------------
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ------------------------------------------------------------------
    # UI building helpers
    # ------------------------------------------------------------------
    def create_widgets(self):
        # Frame for list and scrollbar
        frame = ttk.Frame(self)
        frame.pack(padx=10, pady=5, fill="both", expand=True)

        # Treeview
        self.tree = ttk.Treeview(
            frame,
            columns=("name", "status", "date"),
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("name", text="Name")
        self.tree.heading("status", text="Due")
        self.tree.heading("date", text="Date Added")
        self.tree.column("name", width=250, anchor="w")
        self.tree.column("status", width=80, anchor="center")
        self.tree.column("date", width=180, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Bind double‑click for status edit
        self.tree.bind("<Double-1>", self.on_double_click)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=(0, 10))

        ttk.Button(btn_frame, text="Add member", command=self.add_member).pack(
            side="left", padx=5
        )
        ttk.Button(btn_frame, text="Remove member", command=self.remove_member).pack(
            side="left", padx=5
        )

        # Populate list
        self.refresh_tree()

    # ------------------------------------------------------------------
    # Data loading / saving
    # ------------------------------------------------------------------
    def load_data(self):
        """Read the JSON file, if it exists."""
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.members = [Member.from_dict(entry) for entry in data]
            except Exception as e:
                messagebox.showerror(
                    "Load error",
                    f"Could not load {self.DATA_FILE}.\n{e}",
                )
                self.members = []

    def save_data(self):
        """Write the current member list to the JSON file."""
        try:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump([m.to_dict() for m in self.members], f, indent=2)
        except Exception as e:
            messagebox.showerror(
                "Save error",
                f"Could not save {self.DATA_FILE}.\n{e}",
            )

    # ------------------------------------------------------------------
    # Data manipulation
    # ------------------------------------------------------------------
    def refresh_tree(self):
        """Clear and rebuild the treeview from the data list."""
        selected_item = self.tree.selection()
        self.tree.delete(*self.tree.get_children())
        for member in sorted(self.members):
            status_text = "Paid" if member.paid else "Unpaid"
            self.tree.insert(
                "",
                "end",
                iid=member.name,
                values=(member.name, status_text, member.date_added),
            )
        # Restore selection if still present
        if selected_item and selected_item[0] in [m.name for m in self.members]:
            self.tree.selection_set(selected_item)

    def add_member(self):
        """Prompt for a new member name and add to the list."""
        name = simpledialog.askstring(
            "Add Member", "Enter member name:", parent=self
        )
        if not name:  # Cancelled or empty
            return
        name = name.strip()
        if not name:
            messagebox.showerror("Invalid name", "Name cannot be empty.")
            return
        if any(m.name == name for m in self.members):
            messagebox.showerror("Duplicate name", f"Member '{name}' already exists.")
            return
        # New member gets the current timestamp
        self.members.append(Member(name=name, paid=False))
        self.refresh_tree()

    def remove_member(self):
        """Remove the currently selected member after confirmation."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Nothing selected", "Please select a member to remove.")
            return
        name = selected[0]
        if messagebox.askyesno("Confirm Delete", f"Delete member '{name}'?"):
            self.members = [m for m in self.members if m.name != name]
            self.refresh_tree()

    # ------------------------------------------------------------------
    # Edit status on double‑click (in‑place popup)
    # ------------------------------------------------------------------
    def on_double_click(self, event):
        """Show an in‑place popup to change the status."""
        item = self.tree.identify_row(event.y)
        if not item:
            return

        # Remove any existing edit frame
        if self.edit_frame:
            self.edit_frame.destroy()
            self.edit_frame = None

        member = next((m for m in self.members if m.name == item), None)
        if not member:
            return

        # Get the coordinates of the clicked row
        x, y, width, height = self.tree.bbox(item)
        if not (x or y):
            return

        # Create the small popup frame inside the tree widget
        self.edit_frame = tk.Frame(self.tree, bd=1, relief="solid")
        self.edit_frame.place(x=x, y=y, width=width, height=height)

        status_var = tk.StringVar(value="Paid" if member.paid else "Unpaid")
        combo = ttk.Combobox(
            self.edit_frame,
            textvariable=status_var,
            values=["Paid", "Unpaid"],
            state="readonly",
            width=10,
        )
        combo.pack(padx=1, pady=1)
        combo.focus()

        def update_and_destroy(event=None):
            new_paid = status_var.get() == "Paid"
            if new_paid != member.paid:
                member.paid = new_paid
                self.refresh_tree()
            if self.edit_frame:
                self.edit_frame.destroy()
                self.edit_frame = None

        # Pressing Return or losing focus updates and closes the popup
        combo.bind("<Return>", update_and_destroy)
        combo.bind("<FocusOut>", update_and_destroy)

    # ------------------------------------------------------------------
    # Close handling
    # ------------------------------------------------------------------
    def on_close(self):
        """Save and close the application."""
        self.save_data()
        self.destroy()


# ----------------------------------------------------------------------
# Run the app
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = DuesTracker()
    app.mainloop()
