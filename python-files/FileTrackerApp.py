import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import platform
from datetime import datetime
import json

class FileTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Creator & Tracker")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        
        # Configuration
        self.base_filename = "file"
        self.file_extension = ".txt"
        self.output_folder = "created_files"
        self.tracking_file = "file_tracking.json"
        
        # Create output folder if it doesn't exist
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        # Load tracking data
        self.load_tracking_data()
        
        # Setup GUI
        self.setup_gui()
        
        # Update display
        self.update_file_count()
    
    def load_tracking_data(self):
        """Load file tracking data from JSON file"""
        try:
            if os.path.exists(self.tracking_file):
                with open(self.tracking_file, 'r') as f:
                    self.tracking_data = json.load(f)
            else:
                self.tracking_data = {"files": []}
        except:
            self.tracking_data = {"files": []}
    
    def save_tracking_data(self):
        """Save file tracking data to JSON file"""
        try:
            with open(self.tracking_file, 'w') as f:
                json.dump(self.tracking_data, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tracking data: {str(e)}")
    
    def setup_gui(self):
        """Setup the GUI elements"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="File Creator & Tracker", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # File creation section
        ttk.Label(main_frame, text="File Operations:", 
                 font=("Arial", 12, "bold")).grid(row=1, column=0, columnspan=2, 
                                                 sticky=tk.W, pady=(0, 10))
        
        # Create file button
        self.create_btn = ttk.Button(main_frame, text="Create File", 
                                    command=self.create_file, width=15)
        self.create_btn.grid(row=2, column=0, padx=(0, 10), pady=5, sticky=tk.W)
        
        # Open folder button
        self.open_folder_btn = ttk.Button(main_frame, text="Open Folder", 
                                         command=self.open_folder, width=15)
        self.open_folder_btn.grid(row=2, column=1, pady=5, sticky=tk.W)
        
        # File count section
        ttk.Label(main_frame, text="Statistics:", 
                 font=("Arial", 12, "bold")).grid(row=3, column=0, columnspan=2, 
                                                 sticky=tk.W, pady=(20, 10))
        
        # File count display
        count_frame = ttk.Frame(main_frame)
        count_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        count_frame.columnconfigure(1, weight=1)
        
        ttk.Label(count_frame, text="Total Files Created:").grid(row=0, column=0, sticky=tk.W)
        self.file_count_var = tk.StringVar(value="0")
        self.file_count_label = ttk.Label(count_frame, textvariable=self.file_count_var, 
                                         font=("Arial", 12, "bold"))
        self.file_count_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Current folder display
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        folder_frame.columnconfigure(1, weight=1)
        
        ttk.Label(folder_frame, text="Output Folder:").grid(row=0, column=0, sticky=tk.W)
        self.folder_path_var = tk.StringVar(value=os.path.abspath(self.output_folder))
        folder_path_label = ttk.Label(folder_frame, textvariable=self.folder_path_var, 
                                     foreground="blue", cursor="hand2")
        folder_path_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        folder_path_label.bind("<Button-1>", lambda e: self.open_folder())
        
        # File history section
        ttk.Label(main_frame, text="File History:", 
                 font=("Arial", 12, "bold")).grid(row=6, column=0, columnspan=2, 
                                                 sticky=tk.W, pady=(20, 10))
        
        # Create treeview for file history
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        # Treeview with scrollbar
        self.tree = ttk.Treeview(tree_frame, columns=("filename", "created"), show="headings", height=8)
        self.tree.heading("filename", text="Filename")
        self.tree.heading("created", text="Date Created")
        self.tree.column("filename", width=200)
        self.tree.column("created", width=200)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Refresh button
        refresh_btn = ttk.Button(main_frame, text="Refresh", command=self.refresh_display)
        refresh_btn.grid(row=8, column=0, columnspan=2, pady=(10, 0))
    
    def get_next_filename(self):
        """Get the next available filename in sequence"""
        counter = 1
        while True:
            if counter == 1:
                filename = f"{self.base_filename}{self.file_extension}"
            else:
                filename = f"{self.base_filename}{counter}{self.file_extension}"
            
            filepath = os.path.join(self.output_folder, filename)
            if not os.path.exists(filepath):
                return filename, filepath
            counter += 1
    
    def create_file(self):
        """Create a new file with sequential naming"""
        try:
            filename, filepath = self.get_next_filename()
            
            # Create the file with some default content
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            content = f"File created on: {current_time}\nFilename: {filename}\n\nThis file was created by File Creator & Tracker.\n"
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            # Update tracking data
            file_info = {
                "filename": filename,
                "filepath": filepath,
                "created_date": current_time,
                "full_path": os.path.abspath(filepath)
            }
            self.tracking_data["files"].append(file_info)
            self.save_tracking_data()
            
            # Update display
            self.update_file_count()
            self.update_file_history()
            
            # Show success message
            messagebox.showinfo("Success", f"File '{filename}' created successfully!\nLocation: {os.path.abspath(filepath)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create file: {str(e)}")
    
    def open_folder(self):
        """Open the output folder in the file explorer"""
        try:
            folder_path = os.path.abspath(self.output_folder)
            
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux and other Unix-like systems
                subprocess.run(["xdg-open", folder_path])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {str(e)}")
    
    def update_file_count(self):
        """Update the file count display"""
        count = len(self.tracking_data["files"])
        self.file_count_var.set(str(count))
    
    def update_file_history(self):
        """Update the file history treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add files to treeview (newest first)
        files = self.tracking_data["files"]
        for file_info in reversed(files):  # Show newest first
            self.tree.insert("", "end", values=(file_info["filename"], file_info["created_date"]))
    
    def refresh_display(self):
        """Refresh the display by checking actual files in folder"""
        try:
            # Get actual files in the folder
            actual_files = []
            if os.path.exists(self.output_folder):
                for filename in os.listdir(self.output_folder):
                    if filename.startswith(self.base_filename) and filename.endswith(self.file_extension):
                        filepath = os.path.join(self.output_folder, filename)
                        if os.path.isfile(filepath):
                            # Get file creation time
                            creation_time = os.path.getctime(filepath)
                            created_date = datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M:%S")
                            
                            file_info = {
                                "filename": filename,
                                "filepath": filepath,
                                "created_date": created_date,
                                "full_path": os.path.abspath(filepath)
                            }
                            actual_files.append(file_info)
            
            # Sort by filename
            actual_files.sort(key=lambda x: x["filename"])
            
            # Update tracking data
            self.tracking_data["files"] = actual_files
            self.save_tracking_data()
            
            # Update display
            self.update_file_count()
            self.update_file_history()
            
            messagebox.showinfo("Refresh Complete", f"Display updated. Found {len(actual_files)} files.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh display: {str(e)}")

def main():
    root = tk.Tk()
    app = FileTrackerApp(root)
    
    # Initialize the file history display
    app.update_file_history()
    
    root.mainloop()

if __name__ == "__main__":
    main()
