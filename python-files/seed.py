#!/usr/bin/env python3

import os

import tkinter as tk

from tkinter import ttk, messagebox, filedialog, simpledialog

import pandas as pd

from PIL import Image, ImageTk

 

THUMB_SIZE = 50  # thumbnail will be THUMB_SIZE x THUMB_SIZE pixels

 

class CategoryDialog(tk.Toplevel):

    def __init__(self, master, on_done):

        super().__init__(master)

        self.title("Enter Categories")

        self.categories = []

        self.on_done = on_done

 

        tk.Label(self, text="Enter a category:").pack(padx=10, pady=(10, 0))

        self.entry = tk.Entry(self)

        self.entry.pack(padx=10, pady=5, fill="x")

 

        btn_frame = tk.Frame(self)

        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Add", command=self.add_category).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Done", command=self.finish).pack(side="left", padx=5)

 

        self.protocol("WM_DELETE_WINDOW", self.finish)

        self.grab_set()

        self.entry.focus_set()

 

    def add_category(self):

        text = self.entry.get().strip()

        if not text:

            messagebox.showwarning("Warning", "Category cannot be empty.", parent=self)

        elif text in self.categories:

            messagebox.showwarning("Warning", "Category already added.", parent=self)

        else:

            self.categories.append(text)

            self.entry.delete(0, tk.END)

 

    def finish(self):

        if not self.categories:

            messagebox.showwarning("Warning", "Add at least one category.", parent=self)

            return

        self.grab_release()

        self.destroy()

        self.on_done(self.categories)

 

class SeedDialog(tk.Toplevel):

    def __init__(self, master, categories, on_done):

        super().__init__(master)

        self.title("Enter Seeds")

        self.categories = categories

        self.seed_data = {cat: [] for cat in categories}

        self.on_done = on_done

 

        tk.Label(self, text="Enter a seed name:").pack(padx=10, pady=(10, 0))

        self.entry = tk.Entry(self)

        self.entry.pack(padx=10, pady=5, fill="x")

 

        tk.Label(self, text="Select categories:").pack(padx=10, pady=(5,0))

        cb_frame = tk.Frame(self)

        cb_frame.pack(padx=10, pady=5, fill="x")

        self.vars = {}

        for cat in categories:

            var = tk.BooleanVar()

            cb = tk.Checkbutton(cb_frame, text=cat, variable=var)

            cb.pack(side="left", padx=2)

            self.vars[cat] = var

 

        btn_frame = tk.Frame(self)

        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Add", command=self.add_seed).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Done", command=self.finish).pack(side="left", padx=5)

 

        self.protocol("WM_DELETE_WINDOW", self.finish)

        self.grab_set()

        self.entry.focus_set()

 

    def add_seed(self):

        name = self.entry.get().strip()

        selected = [cat for cat, var in self.vars.items() if var.get()]

        if not name:

            messagebox.showwarning("Warning", "Seed name cannot be empty.", parent=self)

            return

        if not selected:

            messagebox.showwarning("Warning", "Select at least one category.", parent=self)

            return

 

        qty = simpledialog.askinteger(

            "Quantity",

            f"How many seeds of '{name}'?",

            parent=self,

            minvalue=1

        )

        if qty is None:

            return

 

        for cat in selected:

            self.seed_data[cat].append({

                "name": name,

                "quantity": qty,

                "thumbnail": "",

                "danger": "Unknown"

            })

        self.entry.delete(0, tk.END)

        for var in self.vars.values():

            var.set(False)

 

    def finish(self):

        self.grab_release()

        self.destroy()

        self.on_done(self.seed_data)

 

class DangerDialog(tk.Toplevel):

    def __init__(self, master, current="Unknown"):

        super().__init__(master)

        self.title("Set Danger Level")

        self.choice = None

        tk.Label(self, text="Select danger level:").pack(padx=10, pady=(10,0))

        self.var = tk.StringVar(value=current)

        for val in ("Poisonous", "Non-Poisonous", "Unknown"):

            tk.Radiobutton(self, text=val, variable=self.var, value=val).pack(anchor="w", padx=20)

        btn_frame = tk.Frame(self)

        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="OK", command=self.on_ok).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Cancel", command=self.on_cancel).pack(side="left", padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self.grab_set()

        self.focus_set()

 

    def on_ok(self):

        self.choice = self.var.get()

        self.grab_release()

        self.destroy()

 

    def on_cancel(self):

        self.grab_release()

        self.destroy()

 

class MainApplication(tk.Frame):

    def __init__(self, master, seed_data):

        super().__init__(master)

        self.master = master

        self.seed_data = seed_data

        self.photo_images = {}  # keep PhotoImage refs to avoid GC

        self.pack(fill="both", expand=True)

        self.create_widgets()

        self.populate_tree()

 

    def create_widgets(self):

        style = ttk.Style()

        style.configure("Treeview", rowheight=THUMB_SIZE + 10)

 

        self.tree = ttk.Treeview(self, columns=("Quantity", "Danger"), show="tree headings")

        self.tree.heading("#0", text="Seed Name / Category")

        self.tree.heading("Quantity", text="Qty")

        self.tree.heading("Danger", text="Danger Level")

        self.tree.column("Quantity", width=60, anchor="center")

        self.tree.column("Danger", width=100, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=(10,0))

 

        # Configure tags for coloring

        self.tree.tag_configure("Poisonous", background="red")

        self.tree.tag_configure("Non-Poisonous", background="green")

        self.tree.tag_configure("Unknown", background="yellow")

 

        btn_frame = tk.Frame(self)

        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Load",            command=self.load_file).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Add Category",    command=self.add_category).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Add Seed",        command=self.add_seed).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Edit Qty",        command=self.edit_quantity).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Delete Seed",     command=self.delete_seed).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Delete Cat",      command=self.delete_category).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Danger Level",    command=self.set_danger).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Thumbnail",       command=self.upload_thumbnail).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Save",            command=self.save_data).pack(side="left", padx=5)

 

    def populate_tree(self):

        self.tree.delete(*self.tree.get_children())

        self.photo_images.clear()

        for cat, seeds in self.seed_data.items():

            parent = self.tree.insert("", "end", text=cat, open=True)

            for seed in sorted(seeds, key=lambda x: x["name"]):

                opts = {

                    "text": seed["name"],

                    "values": (seed["quantity"], seed.get("danger", "Unknown"))

                }

                tag = seed.get("danger", "Unknown")

                if seed.get("thumbnail"):

                    try:

                        im = Image.open(seed["thumbnail"]).resize((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)

                        photo = ImageTk.PhotoImage(im)

                        self.photo_images[f"{cat}:{seed['name']}"] = photo

                        opts["image"] = photo

                    except Exception:

                        pass

                self.tree.insert(parent, "end", tags=(tag,), **opts)

 

    def set_danger(self):

        sel = self.tree.selection()

        if not sel:

            messagebox.showwarning("Warning", "Select a seed first.", parent=self.master)

            return

        item = sel[0]

        parent = self.tree.parent(item)

        if not parent:

            messagebox.showwarning("Warning", "Select a seed, not a category.", parent=self.master)

            return

        seed_name = self.tree.item(item, "text")

        cat = self.tree.item(parent, "text")

        current = next((s.get("danger") for s in self.seed_data[cat] if s["name"] == seed_name), "Unknown")

        dlg = DangerDialog(self.master, current=current)

        self.master.wait_window(dlg)

        if dlg.choice:

            for s in self.seed_data[cat]:

                if s["name"] == seed_name:

                    s["danger"] = dlg.choice

                    break

            self.populate_tree()

 

    def load_file(self):

        path = filedialog.askopenfilename(

            parent=self.master,

            title="Load Seed Bank",

            filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv")]

        )

        if not path:

            return

        ext = os.path.splitext(path)[1].lower()

        df = pd.read_csv(path) if ext == ".csv" else pd.read_excel(path)

        df = df.fillna("")

        new_data = {}

        for _, row in df.iterrows():

            cat = row["Category"]

            new_data.setdefault(cat, []).append({

                "name": row["Seed Name"],

                "quantity": int(row.get("Quantity") or 1),

                "thumbnail": row.get("Thumbnail", ""),

                "danger": row.get("Danger", "Unknown")

            })

        self.seed_data = new_data

        self.populate_tree()

 

    def upload_thumbnail(self):

        sel = self.tree.selection()

        if not sel:

            messagebox.showwarning("Warning", "Select a seed first.", parent=self.master)

            return

        item = sel[0]

        parent = self.tree.parent(item)

        if not parent:

            messagebox.showwarning("Warning", "Select a seed, not a category.", parent=self.master)

            return

        seed_name = self.tree.item(item, "text")

        cat = self.tree.item(parent, "text")

        path = filedialog.askopenfilename(

            parent=self.master,

            title="Select Thumbnail",

            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]

        )

        if path:

            for s in self.seed_data[cat]:

                if s["name"] == seed_name:

                    s["thumbnail"] = path

                    break

            self.populate_tree()

 

    def add_category(self):

        name = simpledialog.askstring("New Category", "Enter new category:", parent=self.master)

        if not name:

            return

        name = name.strip()

        if name in self.seed_data:

            messagebox.showwarning("Warning", f"Category '{name}' exists.", parent=self.master)

        else:

            self.seed_data[name] = []

            self.populate_tree()

 

    def add_seed(self):

        dlg = SeedDialog(self.master, list(self.seed_data.keys()), on_done=self._merge_new_seeds)

        self.master.wait_window(dlg)

 

    def _merge_new_seeds(self, new_data):

        for cat, seeds in new_data.items():

            self.seed_data.setdefault(cat, []).extend(seeds)

        self.populate_tree()

 

    def edit_quantity(self):

        sel = self.tree.selection()

        if not sel:

            messagebox.showwarning("Warning", "Select a seed first.", parent=self.master)

            return

        item = sel[0]

        parent = self.tree.parent(item)

        if not parent:

            messagebox.showwarning("Warning", "Select a seed, not a category.", parent=self.master)

            return

        seed_name = self.tree.item(item, "text")

        cat = self.tree.item(parent, "text")

        current = next((s["quantity"] for s in self.seed_data[cat] if s["name"] == seed_name), 1)

        qty = simpledialog.askinteger("Edit Quantity",

                                      f"Set new quantity for '{seed_name}':",

                                      initialvalue=current, minvalue=1, parent=self.master)

        if qty is None:

            return

        for s in self.seed_data[cat]:

            if s["name"] == seed_name:

                s["quantity"] = qty

        self.populate_tree()

 

    def delete_seed(self):

        sel = self.tree.selection()

        if not sel:

            messagebox.showwarning("Warning", "Select a seed first.", parent=self.master)

            return

        item = sel[0]

        parent = self.tree.parent(item)

        if not parent:

            messagebox.showwarning("Warning", "Select a seed, not a category.", parent=self.master)

            return

        seed_name = self.tree.item(item, "text")

        cat = self.tree.item(parent, "text")

        if messagebox.askyesno("Delete Seed", f"Delete '{seed_name}' from '{cat}'?", parent=self.master):

            self.seed_data[cat] = [s for s in self.seed_data[cat] if s["name"] != seed_name]

            self.populate_tree()

 

    def delete_category(self):

        sel = self.tree.selection()

        if not sel:

            messagebox.showwarning("Warning", "Select a category first.", parent=self.master)

            return

        item = sel[0]

        if self.tree.parent(item):

            messagebox.showwarning("Warning", "Select a category, not a seed.", parent=self.master)

            return

        cat = self.tree.item(item, "text")

        if messagebox.askyesno("Delete Category", f"Delete category '{cat}'?", parent=self.master):

            del self.seed_data[cat]

            self.populate_tree()

 

    def save_data(self):

        df = pd.DataFrame([

            {

                "Category": cat,

                "Seed Name": seed["name"],

                "Quantity": seed["quantity"],

                "Thumbnail": seed["thumbnail"],

                "Danger": seed.get("danger", "Unknown")

            }

            for cat, seeds in self.seed_data.items()

            for seed in sorted(seeds, key=lambda x: x["name"])

        ])

        path = filedialog.asksaveasfilename(

            parent=self.master,

            title="Save Seed Bank",

            defaultextension=".xlsx",

            filetypes=[("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")]

        )

        if not path:

            return

        ext = os.path.splitext(path)[1].lower()

        try:

            if ext == ".csv":

                df.to_csv(path, index=False)

            else:

                df.to_excel(path, index=False)

        except ModuleNotFoundError as e:

            if "openpyxl" in str(e):

                if messagebox.askyesno(

                    "OpenPyXL Missing",

                    "Saving to Excel requires openpyxl.\nSave as CSV instead?",

                    parent=self.master

                ):

                    csv_path = os.path.splitext(path)[0] + ".csv"

                    df.to_csv(csv_path, index=False)

                    messagebox.showinfo("Saved", f"Data saved to {csv_path}", parent=self.master)

        else:

            messagebox.showinfo("Saved", f"Data saved to {path}", parent=self.master)

 

def main():

    root = tk.Tk()

    root.title("Seed Categorizer")

    root.geometry("1000x600")  # wider to accommodate buttons

 

    def start_new():

        def after_cats(cats):

            def after_seeds(data):

                MainApplication(root, data)

            SeedDialog(root, cats, on_done=after_seeds)

        CategoryDialog(root, on_done=after_cats)

 

    def start():

        if messagebox.askyesno("Load or New?",

                               "Load existing seed bank file?\nYes: load file\nNo: create new",

                               parent=root):

            app = MainApplication(root, {})

            app.load_file()

        else:

            start_new()

 

    root.after(0, start)

    root.mainloop()

 

if __name__ == "__main__":

    main()

