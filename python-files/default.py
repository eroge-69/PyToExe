import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import uuid

class JsonEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("עורך JSON ל־Kodi")
        self.root.geometry("1000x600")
        self.font = ("Arial", 14)
        self.data = []
        self.selected_category_index = None

        # 🔷 כפתורים עליונים
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="📂 טען קובץ", font=self.font, command=self.load_json).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="💾 שמור קובץ", font=self.font, command=self.save_json).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="➕ קטגוריה", font=self.font, command=self.add_category).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="✏️ ערוך קטגוריה", font=self.font, command=self.edit_category).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑️ מחק קטגוריה", font=self.font, command=self.delete_category).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="➕ אייטם", font=self.font, command=self.add_item).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="✏️ ערוך אייטם", font=self.font, command=self.edit_item_button).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑️ מחק אייטם", font=self.font, command=self.delete_item).pack(side=tk.LEFT, padx=5)

        # 🔷 רשימת קטגוריות
        self.category_list = tk.Listbox(root, width=30, font=self.font)
        self.category_list.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        self.category_list.bind("<<ListboxSelect>>", self.show_items)

        # 🔷 טבלת אייטמים
        style = ttk.Style()
        style.configure("Treeview.Heading", font=self.font)
        style.configure("Treeview", font=self.font, rowheight=30)

        self.tree = ttk.Treeview(root, columns=("label", "url", "time"), show="headings")
        self.tree.heading("label", text="label")
        self.tree.heading("url", text="url")
        self.tree.heading("time", text="time")

        self.tree.column("label", width=200, anchor=tk.CENTER)
        self.tree.column("url", width=400, anchor=tk.W)
        self.tree.column("time", width=100, anchor=tk.CENTER)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.edit_item)

    def load_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.refresh_categories()

    def save_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not path:
            return

        for category in self.data:
            def time_key(item):
                try:
                    return int(item["time"][:2]) * 60 + int(item["time"][3:5])
                except:
                    return 0
            category["items"] = sorted(category["items"], key=time_key)

        clean_data = []
        for category in self.data:
            clean_items = []
            for item in category["items"]:
                clean_item = {k: v for k, v in item.items() if k != "id"}
                clean_items.append(clean_item)
            clean_data.append({
                "label": category["label"],
                "items": clean_items
            })

        with open(path, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, indent=2, ensure_ascii=False)

        messagebox.showinfo("הצלחה", "הקובץ נשמר בלי מזהי ID ובסדר כרונולוגי!")

    def refresh_categories(self):
        self.category_list.delete(0, tk.END)
        for cat in self.data:
            self.category_list.insert(tk.END, cat["label"])

    def show_items(self, event):
        selection = self.category_list.curselection()
        if not selection:
            return
        self.selected_category_index = selection[0]
        items = self.data[self.selected_category_index]["items"]

        def time_key(item):
            try:
                return int(item["time"][:2]) * 60 + int(item["time"][3:5])
            except:
                return 0

        sorted_items = sorted(items, key=time_key)

        self.tree.delete(*self.tree.get_children())
        for item in sorted_items:
            self.tree.insert("", tk.END, values=(item["label"], item["url"], item["time"]))

    def add_category(self):
        new_cat = {"label": "קטגוריה חדשה", "items": []}
        self.data.append(new_cat)
        self.refresh_categories()

    def edit_category(self):
        selection = self.category_list.curselection()
        if not selection:
            messagebox.showwarning("שגיאה", "בחר קטגוריה לעריכה")
            return

        index = selection[0]
        current_label = self.data[index]["label"]

        win = tk.Toplevel(self.root)
        win.title("עריכת קטגוריה")
        win.geometry("300x150")

        tk.Label(win, text="שם חדש:", font=self.font).pack(pady=10)
        entry = tk.Entry(win, font=self.font)
        entry.pack(fill=tk.X, padx=10)
        entry.insert(0, current_label)

        def save():
            new_label = entry.get().strip()
            if new_label:
                self.data[index]["label"] = new_label
                self.refresh_categories()
                win.destroy()
            else:
                messagebox.showwarning("שגיאה", "השם לא יכול להיות ריק")

        tk.Button(win, text="💾 שמור", font=self.font, command=save).pack(pady=10)

    def delete_category(self):
        selection = self.category_list.curselection()
        if not selection:
            messagebox.showwarning("שגיאה", "בחר קטגוריה למחיקה")
            return

        index = selection[0]
        label = self.data[index]["label"]

        confirm = messagebox.askyesno("אישור מחיקה", f"האם למחוק את הקטגוריה '{label}' וכל האייטמים שבה?")
        if not confirm:
            return

        del self.data[index]
        self.selected_category_index = None
        self.refresh_categories()
        self.tree.delete(*self.tree.get_children())

    def add_item(self):
        selection = self.category_list.curselection()
        if not selection:
            messagebox.showwarning("שגיאה", "בחר קטגוריה קודם")
            return
        self.selected_category_index = selection[0]
        self.open_item_editor()

    def edit_item(self, event):
        self._edit_selected_item()

    def edit_item_button(self):
        self._edit_selected_item()

    def _edit_selected_item(self):
        selected = self.tree.selection()
        if not selected or self.selected_category_index is None:
            messagebox.showwarning("שגיאה", "בחר אייטם לעריכה")
            return
        values = self.tree.item(selected[0], "values")
        label, url, time = values
        items = self.data[self.selected_category_index]["items"]
        for i, item in enumerate(items):
            if item["label"] == label and item["url"] == url and item["time"] == time:
                self.open_item_editor(item, i)
                break

    def open_item_editor(self, item=None, index=None):
        if self.selected_category_index is None:
            messagebox.showwarning("שגיאה", "לא נבחרה קטגוריה")
            return

        win = tk.Toplevel(self.root)
        win.title("עריכת אייטם" if item else "אייטם חדש")
        win.geometry("500x300")

        tk.Label(win, text="label:", font=self.font).pack()
        label_entry = tk.Entry(win, font=self.font)
        label_entry.pack(fill=tk.X, padx=10)

        tk.Label(win, text="url:", font=self.font).pack()
        url_entry = tk.Entry(win, font=self.font)
        url_entry.pack(fill=tk.X, padx=10)

        tk.Label(win, text="time:", font=self.font).pack()
        time_entry = tk.Entry(win, font=self.font)
        time_entry.pack(fill=tk.X, padx=10)

        if item:
            label_entry.insert(0, item["label"])
            url_entry.insert(0, item["url"])
            time_entry.insert(0, item["time"])

        def add_context_menu(entry):
            menu = tk.Menu(entry, tearoff=0)
            menu.add_command(label="העתק", command=lambda: entry.event_generate("<<Copy>>"))
            menu.add_command(label="הדבק", command=lambda: entry.event_generate("<<Paste>>"))
            menu.add_command(label="גזור", command=lambda: entry.event_generate("<<Cut>>"))

            def show_menu(event):
                menu.tk_popup(event.x_root, event.y_root)

            entry.bind("<Button-3>", show_menu)
            entry.bind("<Control-c>", lambda e: entry.event_generate("<<Copy>>"))
            entry.bind("<Control-v>", lambda e: entry.event_generate("<<Paste>>"))
            entry.bind("<Control-x>", lambda e: entry.event_generate("<<Cut>>"))

        add_context_menu(label_entry)
        add_context_menu(url_entry)

        def save():
            label = label_entry.get().strip()
            url = url_entry.get().strip()
            time = time_entry.get().strip()

            if not time:
                used_times = set(i["time"] for i in self.data[self.selected_category_index]["items"])
                def format_time(minutes):
                    h = minutes // 60
                    m = minutes % 60
                    return f"{h:02d}:{m:02d}"
                for t in range(0, 24 * 60, 5):
                    candidate = format_time(t)
                    if candidate not in used_times:
                        time = candidate
                        break

            if not label:
                label = f"item_{time.replace(':', '_')}"

            new_item = {
                "label": label,
                "url": url,
                "time": time,
                "id": item["id"] if item and "id" in item else str(uuid.uuid4())
            }

            if item:
                self.data[self.selected_category_index]["items"][index] = new_item
            else:
                self.data[self.selected_category_index]["items"].append(new_item)

            self.show_items(None)
            win.destroy()

        tk.Button(win, text="💾 שמור", font=self.font, command=save).pack(pady=10)

    def delete_item(self):
        selected = self.tree.selection()
        if not selected or self.selected_category_index is None:
            messagebox.showwarning("שגיאה", "בחר אייטם למחיקה")
            return

        values = self.tree.item(selected[0], "values")
        label, url, time = values

        confirm = messagebox.askyesno("אישור מחיקה", f"האם למחוק את האייטם '{label}'?")
        if not confirm:
            return

        items = self.data[self.selected_category_index]["items"]
        for i, item in enumerate(items):
            if item["label"] == label and item["url"] == url and item["time"] == time:
                del items[i]
                break

        self.show_items(None)

# הפעלה
if __name__ == "__main__":
    root = tk.Tk()
    app = JsonEditorApp(root)
    root.mainloop()

