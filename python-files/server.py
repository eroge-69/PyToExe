import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class CloudStorageApp:
    def __init__(self, root):
        self.root = root
        self.root.title('My Cloud Storage')
        self.root.geometry('700x400')

        # Storage folder (simulate cloud folder locally)
        self.storage_path = os.path.join(os.getcwd(), 'CloudStorage')
        os.makedirs(self.storage_path, exist_ok=True)

        # GUI Elements
        self.tree = ttk.Treeview(root, columns=('File Name', 'Size'), show='headings')
        self.tree.heading('File Name', text='File Name')
        self.tree.heading('Size', text='Size (KB)')
        self.tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text='Upload', command=self.upload_file).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text='Download', command=self.download_file).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(btn_frame, text='Delete', command=self.delete_file).pack(side=tk.LEFT, padx=5, pady=5)

        self.refresh_files()

    def refresh_files(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for file in os.listdir(self.storage_path):
            size_kb = os.path.getsize(os.path.join(self.storage_path, file)) // 1024
            self.tree.insert('', tk.END, values=(file, size_kb))

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            shutil.copy(file_path, self.storage_path)
            messagebox.showinfo('Success', 'File uploaded successfully!')
            self.refresh_files()

    def download_file(self):
        selected = self.tree.selection()
        if selected:
            file_name = self.tree.item(selected[0])['values'][0]
            save_path = filedialog.askdirectory()
            if save_path:
                shutil.copy(os.path.join(self.storage_path, file_name), save_path)
                messagebox.showinfo('Success', 'File downloaded successfully!')

    def delete_file(self):
        selected = self.tree.selection()
        if selected:
            file_name = self.tree.item(selected[0])['values'][0]
            os.remove(os.path.join(self.storage_path, file_name))
            messagebox.showinfo('Success', 'File deleted successfully!')
            self.refresh_files()

if __name__ == '__main__':
    root = tk.Tk()
    app = CloudStorageApp(root)
    root.mainloop()
