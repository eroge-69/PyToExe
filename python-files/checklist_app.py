import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

class ChecklistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Numbered Checklist Generator")
        self.root.geometry("600x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configuration file path
        self.config_file = "checklist_config.json"
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        self.style.configure('Button.TButton', font=('Arial', 10))
        self.style.configure('Checkbox.TCheckbutton', font=('Arial', 10))
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Numbered Checklist Generator", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        
        ttk.Label(input_frame, text="Start:").grid(row=0, column=0, padx=(0, 5))
        self.start_var = tk.StringVar(value="1")
        self.start_entry = ttk.Entry(input_frame, textvariable=self.start_var, width=8)
        self.start_entry.grid(row=0, column=1, padx=(0, 15))
        
        ttk.Label(input_frame, text="End:").grid(row=0, column=2, padx=(0, 5))
        self.end_var = tk.StringVar(value="63")
        self.end_entry = ttk.Entry(input_frame, textvariable=self.end_var, width=8)
        self.end_entry.grid(row=0, column=3, padx=(0, 15))
        
        generate_btn = ttk.Button(input_frame, text="Generate List", command=self.generate_list)
        generate_btn.grid(row=0, column=4)
        
        # Create a frame for the canvas and scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(list_frame, bg='white')
        self.scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        select_all_btn = ttk.Button(button_frame, text="Select All", command=self.select_all)
        select_all_btn.grid(row=0, column=0, padx=5)
        
        clear_all_btn = ttk.Button(button_frame, text="Clear All", command=self.clear_all)
        clear_all_btn.grid(row=0, column=1, padx=5)
        
        save_btn = ttk.Button(button_frame, text="Save to File", command=self.save_to_file)
        save_btn.grid(row=0, column=2, padx=5)
        
        load_btn = ttk.Button(button_frame, text="Load from File", command=self.load_from_file)
        load_btn.grid(row=0, column=3, padx=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=4, column=0, columnspan=3)
        
        # Initialize variables
        self.checkboxes = []
        self.checked_states = {}  # Dictionary to store checked states
        
        # Load previous configuration if exists
        self.load_config()
        
        # Generate initial list
        self.generate_list()
        
        # Load saved check states
        self.load_check_states()
        
        # Make the main frame expandable
        main_frame.rowconfigure(2, weight=1)
        
        # Setup auto-save when closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def load_config(self):
        """Load previous configuration if exists"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.start_var.set(config.get('start', '1'))
                    self.end_var.set(config.get('end', '63'))
                    self.checked_states = config.get('checked_states', {})
            except:
                # If file is corrupted, start fresh
                self.checked_states = {}
        
    def save_config(self):
        """Save current configuration"""
        config = {
            'start': self.start_var.get(),
            'end': self.end_var.get(),
            'checked_states': self.checked_states
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except:
            pass  # Silently fail if we can't save
        
    def on_closing(self):
        """Save configuration when closing the app"""
        self.save_check_states()
        self.save_config()
        self.root.destroy()
        
    def save_check_states(self):
        """Save current check states to dictionary"""
        for cb, var, number in self.checkboxes:
            self.checked_states[str(number)] = var.get()
        
    def load_check_states(self):
        """Load saved check states to checkboxes"""
        for cb, var, number in self.checkboxes:
            state = self.checked_states.get(str(number), False)
            var.set(state)
            self.update_checkbox_text(number, var)
        
    def generate_list(self):
        # Save current states before clearing
        self.save_check_states()
        
        # Clear existing checkboxes
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.checkboxes = []
        
        # Get range values
        try:
            start = int(self.start_var.get())
            end = int(self.end_var.get())
            
            if start > end:
                messagebox.showerror("Input Error", "Start value must be less than or equal to end value")
                return
                
            if end - start > 200:
                messagebox.showerror("Input Error", "Range too large. Please keep it under 200 items.")
                return
                
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers")
            return
        
        # Save configuration
        self.save_config()
        
        # Create checkboxes in 3 columns
        num_items = end - start + 1
        items_per_column = (num_items + 2) // 3  # Round up division
        
        for col in range(3):
            column_frame = ttk.Frame(self.scrollable_frame)
            column_frame.grid(row=0, column=col, padx=10, pady=5, sticky="nw")
            
            for i in range(items_per_column):
                idx = start + col * items_per_column + i
                if idx > end:
                    break
                    
                number_str = f"{idx:02d}"  # Format with leading zero
                var = tk.BooleanVar()
                
                # Create a frame for each checkbox to ensure proper alignment
                cb_frame = ttk.Frame(column_frame)
                cb_frame.pack(fill="x", pady=2)
                
                cb = ttk.Checkbutton(
                    cb_frame, 
                    text=f"{number_str} [ ]", 
                    variable=var,
                    command=lambda n=idx, v=var: self.update_checkbox_text(n, v),
                    style='Checkbox.TCheckbutton',
                    width=8
                )
                cb.pack(side="left")
                
                # Store the checkbox and its variable
                self.checkboxes.append((cb, var, idx))
        
        # Load saved check states
        self.load_check_states()
        
        self.status_var.set(f"Generated {num_items} items")
        
    def update_checkbox_text(self, number, var):
        # Find the checkbox that needs updating
        for cb, v, n in self.checkboxes:
            if n == number:
                number_str = f"{number:02d}"
                if var.get():
                    cb.config(text=f"{number_str} [X]")
                else:
                    cb.config(text=f"{number_str} [ ]")
                break
        # Auto-save the state
        self.checked_states[str(number)] = var.get()
        self.save_config()
    
    def select_all(self):
        for cb, var, number in self.checkboxes:
            var.set(True)
            self.update_checkbox_text(number, var)
    
    def clear_all(self):
        for cb, var, number in self.checkboxes:
            var.set(False)
            self.update_checkbox_text(number, var)
    
    def save_to_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w') as f:
                for cb, var, number in self.checkboxes:
                    number_str = f"{number:02d}"
                    status = "[X]" if var.get() else "[ ]"
                    f.write(f"{number_str} {status}\n")
                    
            self.status_var.set(f"Checklist saved to {file_path}")
            messagebox.showinfo("Success", "Checklist saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
            
    def load_from_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                
            # Clear current states
            for cb, var, number in self.checkboxes:
                var.set(False)
                self.update_checkbox_text(number, var)
                
            # Load states from file
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 2:
                    number_str = parts[0]
                    status = parts[1]
                    try:
                        number = int(number_str)
                        for cb, var, n in self.checkboxes:
                            if n == number:
                                var.set(status == "[X]")
                                self.update_checkbox_text(number, var)
                                break
                    except ValueError:
                        continue
                        
            self.status_var.set(f"Checklist loaded from {file_path}")
            messagebox.showinfo("Success", "Checklist loaded successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChecklistApp(root)
    root.mainloop()
