import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class FileCopierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Distributor")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        # Custom color scheme
        self.primary_color = "#4caf50"
        self.primary_hover = "#45a049"
        self.button_color = "#5c6bc0"
        self.button_hover = "#3f51b5"
        
        # Create style
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("Header.TLabel", background=self.primary_color, 
                             foreground="white", font=("Arial", 14, "bold"))
        self.style.configure("TButton", font=("Arial", 10), padding=5)
        self.style.configure("TCheckbutton", background="#f0f0f0", font=("Arial", 9))
        self.style.configure("TEntry", padding=5)
        
        # Create header
        header_frame = ttk.Frame(root)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_label = ttk.Label(header_frame, text="COPY TO SUBFOLDERS", style="Header.TLabel")
        header_label.pack(fill="x", ipady=10)
        
        # Create main content frame
        content_frame = ttk.Frame(root)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Source selection
        source_frame = ttk.Frame(content_frame)
        source_frame.pack(fill="x", pady=10)
        
        ttk.Label(source_frame, text="Source Item:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=2)
        
        self.source_type = tk.IntVar(value=0)
        ttk.Radiobutton(source_frame, text="File", variable=self.source_type, value=0).grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(source_frame, text="Folder", variable=self.source_type, value=1).grid(row=1, column=1, sticky="w")
        
        self.source_entry = ttk.Entry(source_frame, width=50)
        self.source_entry.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)
        
        browse_source_btn = tk.Button(
            source_frame, 
            text="Browse", 
            command=self.browse_source,
            bg=self.button_color,
            fg="white",
            activebackground=self.button_hover,
            activeforeground="white",
            bd=0,
            padx=10,
            font=("Arial", 9)
        )
        browse_source_btn.grid(row=2, column=3, padx=(5, 0))
        
        # Target selection
        target_frame = ttk.Frame(content_frame)
        target_frame.pack(fill="x", pady=10)
        
        ttk.Label(target_frame, text="Target Folder:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=2)
        
        self.target_entry = ttk.Entry(target_frame, width=50)
        self.target_entry.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)
        
        browse_target_btn = tk.Button(
            target_frame, 
            text="Browse", 
            command=self.browse_target,
            bg=self.button_color,
            fg="white",
            activebackground=self.button_hover,
            activeforeground="white",
            bd=0,
            padx=10,
            font=("Arial", 9)
        )
        browse_target_btn.grid(row=1, column=3, padx=(5, 0))
        
        # Options
        options_frame = ttk.Frame(content_frame)
        options_frame.pack(fill="x", pady=10)
        
        self.overwrite_var = tk.IntVar(value=0)
        overwrite_cb = ttk.Checkbutton(
            options_frame, 
            text="Overwrite existing items", 
            variable=self.overwrite_var
        )
        overwrite_cb.pack(anchor="w")
        
        # Status area
        status_frame = ttk.Frame(content_frame)
        status_frame.pack(fill="x", pady=(15, 5))
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground="#333")
        status_label.pack(side="left")
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode="determinate")
        self.progress.pack(fill="x", expand=True, padx=(10, 0))
        
        # Action buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill="x", pady=15)
        
        # Create a larger execute button with custom hover effects
        self.execute_btn = tk.Button(
            button_frame, 
            text="COPY TO SUBFOLDERS", 
            command=self.execute_copy,
            bg=self.primary_color,
            fg="white",
            activebackground=self.primary_hover,
            activeforeground="white",
            font=("Arial", 11, "bold"),
            bd=0,
            padx=30,
            pady=12,
            cursor="hand2"
        )
        self.execute_btn.pack(side="right", ipadx=5)
        
        # Add hover effect for execute button
        self.execute_btn.bind("<Enter>", lambda e: self.execute_btn.config(bg=self.primary_hover))
        self.execute_btn.bind("<Leave>", lambda e: self.execute_btn.config(bg=self.primary_color))
        
        # Configure grid weights
        source_frame.columnconfigure(0, weight=1)
        target_frame.columnconfigure(0, weight=1)
        
    def browse_source(self):
        if self.source_type.get() == 0:  # File
            path = filedialog.askopenfilename(title="Select Source File")
        else:  # Folder
            path = filedialog.askdirectory(title="Select Source Folder")
            
        if path:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, path)
            
    def browse_target(self):
        path = filedialog.askdirectory(title="Select Target Folder")
        if path:
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, path)
            
    def execute_copy(self):
        source = self.source_entry.get()
        target = self.target_entry.get()
        
        # Validation
        if not source or not target:
            messagebox.showerror("Error", "Both source and target paths must be selected")
            return
            
        if not os.path.exists(source):
            messagebox.showerror("Error", "Source path does not exist")
            return
            
        if self.source_type.get() == 0 and not os.path.isfile(source):
            messagebox.showerror("Error", "Selected source is not a file")
            return
            
        if self.source_type.get() == 1 and not os.path.isdir(source):
            messagebox.showerror("Error", "Selected source is not a folder")
            return
            
        if not os.path.isdir(target):
            messagebox.showerror("Error", "Target is not a valid directory")
            return
            
        # Get subfolders
        try:
            subfolders = [f.path for f in os.scandir(target) if f.is_dir()]
            if not subfolders:
                messagebox.showwarning("Warning", "No subfolders found in target directory")
                return
                
            total = len(subfolders)
            self.progress["maximum"] = total
            self.progress["value"] = 0
            self.status_var.set(f"Copying to {total} subfolders...")
            self.root.update()
            
            # Process each subfolder
            success_count = 0
            for i, folder in enumerate(subfolders, 1):
                try:
                    dest_path = os.path.join(folder, os.path.basename(source))
                    
                    # Handle existing items
                    if os.path.exists(dest_path):
                        if not self.overwrite_var.get():
                            continue
                        if os.path.isfile(dest_path):
                            os.remove(dest_path)
                        else:
                            shutil.rmtree(dest_path)
                    
                    # Copy based on source type
                    if self.source_type.get() == 0:  # File
                        shutil.copy2(source, folder)
                    else:  # Folder
                        shutil.copytree(source, dest_path)
                        
                    success_count += 1
                    
                except Exception as e:
                    print(f"Error copying to {folder}: {str(e)}")
                
                # Update progress
                self.progress["value"] = i
                self.status_var.set(f"Processing: {i}/{total} folders")
                self.root.update()
            
            # Show completion message
            self.status_var.set(f"Completed: Copied to {success_count}/{total} subfolders")
            messagebox.showinfo("Success", f"Successfully copied to {success_count} out of {total} subfolders")
            
        except Exception as e:
            messagebox.showerror("Error", f"Operation failed: {str(e)}")
            self.status_var.set("Error occurred")
            
        finally:
            self.progress["value"] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = FileCopierApp(root)
    root.mainloop()