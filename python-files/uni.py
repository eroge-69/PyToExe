import os
import ctypes
import tkinter as tk
from tkinter import filedialog
import shutil

class FileRemover:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("File Remover")
        
        self.label = tk.Label(self.window, text="Select file to remove:")
        self.label.pack()
        
        self.file_path = tk.StringVar()
        self.entry = tk.Entry(self.window, textvariable=self.file_path, width=50)
        self.entry.pack()
        
        self.browse_button = tk.Button(self.window, text="Browse", command=self.browse_file)
        self.browse_button.pack()
        
        self.remove_button = tk.Button(self.window, text="Remove", command=self.remove_file)
        self.remove_button.pack()
        
        self.result_label = tk.Label(self.window, text="")
        self.result_label.pack()

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        self.file_path.set(file_path)

    def remove_file(self):
        file_path = self.file_path.get()
        
        try:
            # Disable UAC prompt
            ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", 
                f"/c takeown /f \"{file_path}\" /r /d y", None, 1)
            
            # Remove read-only attribute
            os.system(f"attrib -r \"{file_path}\"")
            
            # Delete the file
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)
                
            self.result_label.config(text="File removed successfully!")
            
        except Exception as e:
            self.result_label.config(text=f"Error: {str(e)}")

if __name__ == "__main__":
    app = FileRemover()
    app.window.mainloop()