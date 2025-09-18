import tkinter as tk
from tkinter import ttk, messagebox

class ArchplanKeygen:
    def __init__(self, root):
        self.root = root
        self.root.title('Archplan Code Generator 2026')
        self.root.geometry('500x400')
        self.root.configure(bg='#f0f0f0')
        
        self.create_widgets()
        self.apply_style()
        
    def create_widgets(self):
        # Input frame
        input_frame = ttk.LabelFrame(self.root, text='Input', padding=10)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(input_frame, text='Enter Key:').grid(row=0, column=0, sticky='w', pady=5)
        self.key_input = ttk.Entry(input_frame, width=50)
        self.key_input.grid(row=0, column=1, padx=5, pady=5)
        
        # Output frame
        output_frame = ttk.LabelFrame(self.root, text='Output', padding=10)
        output_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(output_frame, text='Generated Code:').grid(row=0, column=0, sticky='w', pady=5)
        self.result_output = ttk.Entry(output_frame, width=50, state='readonly')
        self.result_output.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(output_frame, text='AutoCAD Version:').grid(row=1, column=0, sticky='w', pady=5)
        self.autocad_output = ttk.Entry(output_frame, width=50, state='readonly')
        self.autocad_output.grid(row=1, column=1, padx=5, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.generate_button = ttk.Button(button_frame, text='Generate Code', command=self.generate_code)
        self.generate_button.pack(side='left', padx=5)
        
        clear_button = ttk.Button(button_frame, text='Clear', command=self.clear_fields)
        clear_button.pack(side='left', padx=5)
        
    def apply_style(self):
        style = ttk.Style()
        style.configure('TLabelframe', background='#f0f0f0')
        style.configure('TLabelframe.Label', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0')
        
    def generate_code(self):
        key = self.key_input.get().strip()
        
        # Validate input
        if not key:
            messagebox.showerror('Input Error', 'Please enter a key.')
            return
            
        if not key.isdigit():
            messagebox.showerror('Input Error', 'Key must contain only digits.')
            return
            
        if len(key) < 4:
            messagebox.showerror('Input Error', 'Key must be at least 4 digits long.')
            return
            
        try:
            # Step 1: Remove last 3 digits
            step1 = key[:-3]
            
            # Step 2: Subtract 1234 (this step is not shown)
            step2 = int(step1) - 1357
            
            # Step 3: Add 853306
            step3 = step2 + 853306
            
            # Display the result
            self.result_output.config(state='normal')
            self.result_output.delete(0, tk.END)
            self.result_output.insert(0, str(step3))
            self.result_output.config(state='readonly')
            
            # AutoCAD Version calculation
            last_two_digits = key[-2:]
            autocad_version = int(last_two_digits) / 2
            
            self.autocad_output.config(state='normal')
            self.autocad_output.delete(0, tk.END)
            self.autocad_output.insert(0, str(autocad_version))
            self.autocad_output.config(state='readonly')
            
        except Exception as e:
            messagebox.showerror('Error', f'An error occurred: {str(e)}')
            
    def clear_fields(self):
        self.key_input.delete(0, tk.END)
        
        self.result_output.config(state='normal')
        self.result_output.delete(0, tk.END)
        self.result_output.config(state='readonly')
        
        self.autocad_output.config(state='normal')
        self.autocad_output.delete(0, tk.END)
        self.autocad_output.config(state='readonly')

if __name__ == '__main__':
    root = tk.Tk()
    app = ArchplanKeygen(root)
    root.mainloop()