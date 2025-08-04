import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import sys
from datetime import datetime

class LoopDataFormatter:
    def __init__(self, root):
        self.root = root
        self.root.title("🔄 Loop Data Formatter - Offline Version")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Set window icon and make it resizable
        self.root.resizable(True, True)
        self.root.minsize(800, 600)
        
        # Configure style
        self.setup_styles()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.rowconfigure(4, weight=1)
        
        # Create header
        self.create_header()
        
        # Create example section
        self.create_example_section()
        
        # Create input section
        self.create_input_section()
        
        # Create output section
        self.create_output_section()
        
        # Create buttons
        self.create_buttons()
        
        # Create status bar
        self.create_status_bar()
        
        # Load example data
        self.load_example_data()
        
        # Bind events
        self.bind_events()

    def setup_styles(self):
        """Configure custom styles for the application."""
        style = ttk.Style()
        
        # Configure main frame style
        style.configure('Main.TFrame', background='#ffffff')
        
        # Configure header style
        style.configure('Header.TLabel', 
                       font=('Segoe UI', 24, 'bold'), 
                       foreground='#333333',
                       background='#ffffff')
        
        # Configure subtitle style
        style.configure('Subtitle.TLabel', 
                       font=('Segoe UI', 12, 'italic'), 
                       foreground='#666666',
                       background='#ffffff')
        
        # Configure section header style
        style.configure('Section.TLabel', 
                       font=('Segoe UI', 14, 'bold'), 
                       foreground='#1976d2',
                       background='#ffffff')
        
        # Configure example box style
        style.configure('Example.TFrame', 
                       background='#e3f2fd',
                       relief='solid',
                       borderwidth=1)

    def create_header(self):
        """Create the application header."""
        header_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky=(tk.W, tk.E))
        
        # Title
        title_label = ttk.Label(header_frame, 
                               text="🔄 Loop Data Formatter", 
                               style='Header.TLabel')
        title_label.pack()
        
                # Subtitle
        subtitle_label = ttk.Label(header_frame, 
                                   text="Developed by AHK, with contribution from Manoj and GSK (DATS Team)", 
                                   style='Subtitle.TLabel')
        subtitle_label.pack()

    def create_example_section(self):
        """Create the example data section."""
        example_frame = ttk.Frame(self.main_frame, style='Example.TFrame', padding="15")
        example_frame.grid(row=1, column=0, columnspan=3, pady=(0, 20), sticky=(tk.W, tk.E))
        
        # Example title
        example_title = ttk.Label(example_frame, 
                                 text="📝 Example Input Format:", 
                                 style='Section.TLabel')
        example_title.pack(anchor=tk.W)
        
        # Example text
        example_text = tk.Text(example_frame, 
                              height=3, 
                              wrap=tk.WORD, 
                              font=('Courier New', 10),
                              bg='#f8f9fa',
                              relief='flat',
                              state='disabled')
        example_text.pack(fill=tk.X, pady=(5, 0))
        
        # Store reference
        self.example_text = example_text

    def create_input_section(self):
        """Create the input section."""
        # Input label
        input_label = ttk.Label(self.main_frame, 
                               text="📥 Input Data:", 
                               style='Section.TLabel')
        input_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        # Input text area
        self.input_text = scrolledtext.ScrolledText(
            self.main_frame,
            height=12,
            width=50,
            font=('Courier New', 10),
            wrap=tk.WORD,
            bg='#ffffff',
            relief='solid',
            borderwidth=1
        )
        self.input_text.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

    def create_output_section(self):
        """Create the output section."""
        # Output label
        output_label = ttk.Label(self.main_frame, 
                                text="📤 Formatted Output:", 
                                style='Section.TLabel')
        output_label.grid(row=2, column=2, sticky=tk.W, pady=(0, 5))
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(
            self.main_frame,
            height=12,
            width=50,
            font=('Courier New', 10),
            wrap=tk.WORD,
            bg='#f8f9fa',
            relief='solid',
            borderwidth=1,
            state='disabled'
        )
        self.output_text.grid(row=3, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))

    def create_buttons(self):
        """Create the control buttons."""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20, sticky=(tk.W, tk.E))
        
        # Process button
        self.process_btn = ttk.Button(
            button_frame,
            text="🚀 Format Data",
            command=self.process_data,
            style='Accent.TButton'
        )
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        self.clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Clear All",
            command=self.clear_all
        )
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Copy button
        self.copy_btn = ttk.Button(
            button_frame,
            text="📋 Copy Output",
            command=self.copy_output
        )
        self.copy_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Load file button
        self.load_file_btn = ttk.Button(
            button_frame,
            text="📁 Load File",
            command=self.load_file
        )
        self.load_file_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Save file button
        self.save_file_btn = ttk.Button(
            button_frame,
            text="💾 Save Output",
            command=self.save_output
        )
        self.save_file_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Load example button
        self.load_example_btn = ttk.Button(
            button_frame,
            text="📝 Load Example",
            command=self.load_example_data
        )
        self.load_example_btn.pack(side=tk.LEFT)

    def create_status_bar(self):
        """Create the status bar."""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_bar = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            relief='sunken',
            anchor=tk.W,
            padding=(5, 2)
        )
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

    def load_example_data(self):
        """Load example data into the input field."""
        example_data = """R280|DOWN LOOP2|38|1,2,3,4
R281|UP LOOP3|25|5,6,7,8,9
R282|SIDE LOOP4|12|10,11,12"""
        
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(1.0, example_data)
        
        # Update example display
        self.example_text.config(state='normal')
        self.example_text.delete(1.0, tk.END)
        self.example_text.insert(1.0, "R280|DOWN LOOP2|38|1,2,3,4")
        self.example_text.config(state='disabled')
        
        self.status_var.set("Example data loaded")

    def process_data(self):
        """Process the input data and display results."""
        try:
            # Get input data
            input_data = self.input_text.get(1.0, tk.END).strip()
            
            if not input_data:
                messagebox.showwarning("Warning", "Please enter some data to format.")
                return
            
            # Process the data
            result = self.format_loop_data(input_data)
            
            # Display results
            self.output_text.config(state='normal')
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(1.0, result)
            self.output_text.config(state='disabled')
            
            # Update status
            lines_processed = len([line for line in input_data.split('\n') if line.strip()])
            self.status_var.set(f"Processed {lines_processed} lines successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error occurred during processing")

    def format_loop_data(self, data):
        """Format the loop data according to the specified rules."""
        lines = data.strip().split("\n")
        result = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            parts = line.split("|", 3)
            if len(parts) == 4:
                loop_name = f"{parts[0]}|{parts[1]}"
                values = parts[3].split(",") if parts[3] else []
                actual_count = len(values)
                values_str = ",".join(values)
                result.append(f"{loop_name}|{actual_count}|{values_str}")
            else:
                result.append(f"❌ Line {line_num}: Malformed data - {line}")
        
        return "\n".join(result) if result else "No valid data to process."

    def clear_all(self):
        """Clear both input and output areas."""
        self.input_text.delete(1.0, tk.END)
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state='disabled')
        self.status_var.set("All data cleared")

    def copy_output(self):
        """Copy the output text to clipboard."""
        output_data = self.output_text.get(1.0, tk.END).strip()
        if output_data:
            self.root.clipboard_clear()
            self.root.clipboard_append(output_data)
            self.status_var.set("Output copied to clipboard")
        else:
            messagebox.showinfo("Info", "No output data to copy")

    def load_file(self):
        """Load data from a text file."""
        try:
            # Open file dialog
            file_path = filedialog.askopenfilename(
                title="Select Input File",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                # Read the file
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Load into input text area
                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(1.0, content)
                
                # Update status
                filename = os.path.basename(file_path)
                self.status_var.set(f"Loaded file: {filename}")
                
                # Auto-process the loaded data
                self.process_data()
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file: {str(e)}")
            self.status_var.set("Error loading file")

    def save_output(self):
        """Save the formatted output to a text file."""
        try:
            output_data = self.output_text.get(1.0, tk.END).strip()
            
            if not output_data:
                messagebox.showwarning("Warning", "No output data to save.")
                return
            
            # Generate default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"formatted_loop_data_{timestamp}.txt"
            
            # Open save file dialog
            file_path = filedialog.asksaveasfilename(
                title="Save Formatted Output",
                defaultextension=".txt",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ],
                initialvalue=default_filename
            )
            
            if file_path:
                # Save the file
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(output_data)
                
                # Update status
                filename = os.path.basename(file_path)
                self.status_var.set(f"Saved output to: {filename}")
                
                # Show success message
                messagebox.showinfo("Success", f"Output saved successfully to:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")
            self.status_var.set("Error saving file")

    def bind_events(self):
        """Bind keyboard and mouse events."""
        # Auto-process on Ctrl+Enter
        self.input_text.bind('<Control-Return>', lambda e: self.process_data())
        
        # File operations shortcuts
        self.root.bind('<Control-o>', lambda e: self.load_file())  # Ctrl+O to open file
        self.root.bind('<Control-s>', lambda e: self.save_output())  # Ctrl+S to save output
        
        # Auto-process on text change (optional - can be slow for large data)
        # self.input_text.bind('<KeyRelease>', lambda e: self.auto_process())

    def auto_process(self):
        """Auto-process data when input changes (debounced)."""
        # This is optional and can be slow for large datasets
        # Uncomment the binding in bind_events() if you want this feature
        pass

def main():
    """Main function to start the application."""
    root = tk.Tk()
    
    # Set application icon (if available)
    try:
        # You can add an icon file here if you have one
        # root.iconbitmap('icon.ico')
        pass
    except:
        pass
    
    app = LoopDataFormatter(root)
    
    # Center the window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main() 