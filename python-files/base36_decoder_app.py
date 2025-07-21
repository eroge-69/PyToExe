#!/usr/bin/env python3
"""
Base 36 to ASCII Decoder Desktop Application
A simple GUI tool to decode base 36 strings to ASCII text
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys

class Base36DecoderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Base 36 to ASCII Decoder")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Base 36 to ASCII Decoder", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Input section
        ttk.Label(main_frame, text="Base 36 String:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.input_text = scrolledtext.ScrolledText(main_frame, height=4, width=50)
        self.input_text.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        decode_btn = ttk.Button(button_frame, text="Decode", command=self.decode_string)
        decode_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(button_frame, text="Clear All", command=self.clear_all)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        copy_btn = ttk.Button(button_frame, text="Copy Result", command=self.copy_result)
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        # Output section
        ttk.Label(main_frame, text="Decoded ASCII:").grid(row=4, column=0, sticky=tk.W, pady=(20, 5))
        
        self.output_text = scrolledtext.ScrolledText(main_frame, height=8, width=50, state=tk.DISABLED)
        self.output_text.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Details section
        ttk.Label(main_frame, text="Conversion Details:").grid(row=6, column=0, sticky=tk.W, pady=(20, 5))
        
        self.details_text = scrolledtext.ScrolledText(main_frame, height=6, width=50, state=tk.DISABLED)
        self.details_text.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Configure row weights for resizing
        main_frame.rowconfigure(5, weight=2)  # Output text gets more space
        main_frame.rowconfigure(7, weight=1)  # Details text gets some space
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to decode base 36 strings")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Bind Enter key to decode
        self.input_text.bind('<Control-Return>', lambda e: self.decode_string())
        
    def decode_string(self):
        """Decode the base 36 string in the input field"""
        input_string = self.input_text.get(1.0, tk.END).strip()
        
        if not input_string:
            messagebox.showwarning("Warning", "Please enter a base 36 string to decode")
            return
            
        # Clear previous results
        self.update_text_widget(self.output_text, "")
        self.update_text_widget(self.details_text, "")
        self.status_var.set("Decoding...")
        
        # Run decoding in a separate thread to prevent UI freezing
        threading.Thread(target=self._decode_worker, args=(input_string,), daemon=True).start()
        
    def _decode_worker(self, input_string):
        """Worker thread for decoding to prevent UI freezing"""
        try:
            # Validate input (base 36 should only contain 0-9 and a-z)
            valid_chars = set('0123456789abcdefghijklmnopqrstuvwxyz')
            if not all(c.lower() in valid_chars for c in input_string):
                self.root.after(0, lambda: self.show_error("Invalid base 36 string. Only characters 0-9 and a-z are allowed."))
                return
                
            # Convert base 36 to integer
            decimal_value = int(input_string.lower(), 36)
            
            # Calculate byte representation
            bit_length = decimal_value.bit_length()
            byte_length = (bit_length + 7) // 8
            
            # Convert to bytes (big-endian)
            byte_data = decimal_value.to_bytes(byte_length, byteorder='big')
            
            # Try different decoding approaches
            results = []
            
            # Method 1: Direct ASCII decoding
            try:
                ascii_result = byte_data.decode('ascii', errors='replace')
                clean_result = ''.join(chr(b) for b in byte_data if 32 <= b <= 126)
                results.append(("Big-endian (recommended)", ascii_result, clean_result))
            except Exception as e:
                results.append(("Big-endian", f"Error: {e}", ""))
            
            # Method 2: Little-endian
            try:
                byte_data_le = decimal_value.to_bytes(byte_length, byteorder='little')
                ascii_result_le = byte_data_le.decode('ascii', errors='replace')
                clean_result_le = ''.join(chr(b) for b in byte_data_le if 32 <= b <= 126)
                results.append(("Little-endian", ascii_result_le, clean_result_le))
            except Exception as e:
                results.append(("Little-endian", f"Error: {e}", ""))
            
            # Update UI in main thread
            self.root.after(0, lambda: self._update_results(input_string, decimal_value, byte_data, results))
            
        except ValueError as e:
            self.root.after(0, lambda: self.show_error(f"Invalid base 36 string: {e}"))
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Decoding error: {e}"))
    
    def _update_results(self, input_string, decimal_value, byte_data, results):
        """Update the UI with decoding results"""
        # Show the best result (usually big-endian)
        if results and results[0][2]:  # If we have a clean result
            best_result = results[0][2]
        elif results:
            best_result = results[0][1]
        else:
            best_result = "No readable result"
            
        self.update_text_widget(self.output_text, best_result)
        
        # Show details
        details = []
        details.append(f"Input: {input_string}")
        details.append(f"Decimal value: {decimal_value}")
        details.append(f"Byte length: {len(byte_data)} bytes")
        details.append(f"Hex representation: {byte_data.hex()}")
        details.append("")
        details.append("Decoding attempts:")
        
        for method, result, clean in results:
            details.append(f"\n{method}:")
            if clean and clean != result:
                details.append(f"  Full: {repr(result)}")
                details.append(f"  Clean: {clean}")
            else:
                details.append(f"  Result: {repr(result) if result else 'None'}")
        
        # Show byte breakdown for first few bytes
        details.append("\nFirst 20 bytes breakdown:")
        for i, b in enumerate(byte_data[:20]):
            char = chr(b) if 32 <= b <= 126 else f'[{b}]'
            details.append(f"  {i:2d}: {b:3d} → '{char}'")
        if len(byte_data) > 20:
            details.append(f"  ... and {len(byte_data) - 20} more bytes")
        
        self.update_text_widget(self.details_text, '\n'.join(details))
        self.status_var.set(f"Decoded successfully - {len(byte_data)} bytes")
    
    def show_error(self, message):
        """Show error message and update status"""
        messagebox.showerror("Decoding Error", message)
        self.status_var.set("Error occurred")
    
    def update_text_widget(self, widget, text):
        """Update a text widget (handles disabled state)"""
        widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        widget.insert(1.0, text)
        widget.config(state=tk.DISABLED)
    
    def clear_all(self):
        """Clear all input and output fields"""
        self.input_text.delete(1.0, tk.END)
        self.update_text_widget(self.output_text, "")
        self.update_text_widget(self.details_text, "")
        self.status_var.set("Cleared - ready for new input")
    
    def copy_result(self):
        """Copy the decoded result to clipboard"""
        result = self.output_text.get(1.0, tk.END).strip()
        if result:
            self.root.clipboard_clear()
            self.root.clipboard_append(result)
            self.status_var.set("Result copied to clipboard")
        else:
            messagebox.showinfo("Info", "No result to copy")

def main():
    root = tk.Tk()
    app = Base36DecoderApp(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()