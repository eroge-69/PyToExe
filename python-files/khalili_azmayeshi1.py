
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pypdf import PdfMerger

class PDFMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("خلیلی آزمایشی1")
        self.selected_files = []

        self.tree = ttk.Treeview(root)
        self.tree.pack(side='left', fill='both', expand=True)
        self.tree.bind("<Double-1>", self.on_tree_select)

        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="left", fill="y")

        right_frame = tk.Frame(root)
        right_frame.pack(side='right', fill='y')

        self.listbox = tk.Listbox(right_frame, selectmode=tk.SINGLE)
        self.listbox.pack(pady=10)

        btn_up = tk.Button(right_frame, text="⬆ بالا", command=self.move_up)
        btn_up.pack(fill='x', padx=5)

        btn_down = tk.Button(right_frame, text="⬇ پایین", command=self.move_down)
        btn_down.pack(fill='x', padx=5)

        btn_merge = tk.Button(right_frame, text="ادغام فایل‌ها", command=self.merge_pdfs)
        btn_merge.pack(fill='x', padx=5, pady=20)

        btn_browse = tk.Button(right_frame, text="📂 انتخاب پوشه", command=self.browse_folder)
        btn_browse.pack(fill='x', padx=5)

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.tree.delete(*self.tree.get_children())
            self.insert_tree(folder_path)

    def insert_tree(self, parent_path, parent_node=""):
        for item in os.listdir(parent_path):
            full_path = os.path.join(parent_path, item)
            node = self.tree.insert(parent_node, "end", text=item, open=False)
            if os.path.isdir(full_path):
                self.insert_tree(full_path, node)
            elif item.endswith(".pdf"):
                self.tree.item(node, tags=("pdf",))
                self.tree.tag_bind("pdf", sequence="<Double-1>", callback=self.on_tree_select)

    def on_tree_select(self, event):
        item_id = self.tree.focus()
        path_parts = []
        while item_id:
            path_parts.insert(0, self.tree.item(item_id)["text"])
            item_id = self.tree.parent(item_id)
        file_path = os.path.join(*path_parts)
        if os.path.isfile(file_path) and file_path.endswith(".pdf"):
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                self.listbox.insert(tk.END, file_path)

    def move_up(self):
        idx = self.listbox.curselection()
        if idx and idx[0] > 0:
            i = idx[0]
            self.selected_files[i - 1], self.selected_files[i] = self.selected_files[i], self.selected_files[i - 1]
            self.update_listbox()
            self.listbox.select_set(i - 1)

    def move_down(self):
        idx = self.listbox.curselection()
        if idx and idx[0] < len(self.selected_files) - 1:
            i = idx[0]
            self.selected_files[i], self.selected_files[i + 1] = self.selected_files[i + 1], self.selected_files[i]
            self.update_listbox()
            self.listbox.select_set(i + 1)

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for file in self.selected_files:
            self.listbox.insert(tk.END, file)

    def merge_pdfs(self):
        if not self.selected_files:
            messagebox.showwarning("هشدار", "هیچ فایلی انتخاب نشده است.")
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if output_path:
            merger = PdfMerger()
            try:
                for file in self.selected_files:
                    merger.append(file)
                merger.write(output_path)
                merger.close()
                messagebox.showinfo("موفقیت", "فایل جدید با موفقیت ذخیره شد.")
            except Exception as e:
                messagebox.showerror("خطا", f"در هنگام ادغام خطایی رخ داد:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFMergerApp(root)
    root.geometry("800x500")
    root.mainloop()
