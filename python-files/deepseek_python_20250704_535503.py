import os
import shutil
from tkinter import *
from tkinter import filedialog, messagebox

class FileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple File Manager")
        
        # Create UI elements
        self.tree = Frame(self.root)
        self.listbox = Listbox(self.root, width=100, height=30)
        self.scrollbar = Scrollbar(self.root)
        self.button_frame = Frame(self.root)
        
        # Buttons
        self.up_button = Button(self.button_frame, text="Up", command=self.up_directory)
        self.open_button = Button(self.button_frame, text="Open", command=self.open_file)
        self.delete_button = Button(self.button_frame, text="Delete", command=self.delete_file)
        self.new_folder_button = Button(self.button_frame, text="New Folder", command=self.create_folder)
        
        # Layout
        self.tree.pack(side=LEFT, fill=Y)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.button_frame.pack(fill=X)
        
        self.up_button.pack(side=LEFT)
        self.open_button.pack(side=LEFT)
        self.delete_button.pack(side=LEFT)
        self.new_folder_button.pack(side=LEFT)
        
        # Configure listbox
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)
        
        # Start in home directory
        self.current_dir = os.path.expanduser("~")
        self.update_list()
    
    def update_list(self):
        self.listbox.delete(0, END)
        self.listbox.insert(END, "../ (Parent Directory)")
        
        try:
            for item in sorted(os.listdir(self.current_dir)):
                full_path = os.path.join(self.current_dir, item)
                if os.path.isdir(full_path):
                    self.listbox.insert(END, f"{item}/ (Directory)")
                else:
                    self.listbox.insert(END, f"{item} (File)")
        except PermissionError:
            messagebox.showerror("Error", "Permission denied")
    
    def up_directory(self):
        parent = os.path.dirname(self.current_dir)
        if parent != self.current_dir:  # Check if not already at root
            self.current_dir = parent
            self.update_list()
    
    def open_file(self):
        selection = self.listbox.curselection()
        if not selection:
            return
            
        selected = self.listbox.get(selection[0])
        if selected.startswith("../"):
            self.up_directory()
            return
            
        # Extract filename from the displayed text
        filename = selected.split(" (")[0]
        full_path = os.path.join(self.current_dir, filename)
        
        if os.path.isdir(full_path):
            self.current_dir = full_path
            self.update_list()
        else:
            try:
                os.startfile(full_path)  # Windows
            except AttributeError:
                try:
                    subprocess.run(['xdg-open', full_path])  # Linux
                except:
                    subprocess.run(['open', full_path])  # macOS
    
    def delete_file(self):
        selection = self.listbox.curselection()
        if not selection:
            return
            
        selected = self.listbox.get(selection[0])
        if selected.startswith("../"):
            return
            
        filename = selected.split(" (")[0]
        full_path = os.path.join(self.current_dir, filename)
        
        if messagebox.askyesno("Confirm", f"Delete {filename}?"):
            try:
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)
                self.update_list()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def create_folder(self):
        folder_name = simpledialog.askstring("New Folder", "Enter folder name:")
        if folder_name:
            try:
                os.mkdir(os.path.join(self.current_dir, folder_name))
                self.update_list()
            except Exception as e:
                messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = Tk()
    app = FileManager(root)
    root.mainloop()