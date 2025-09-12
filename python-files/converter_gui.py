import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import math

# Set appearance mode and theme
ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

class BitsByteConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Bits & Bytes Converter")
        self.root.geometry("480x400")
        
        # Variables
        self.conversion_type = ctk.StringVar(value="bytes_to_bits")
        self.amount_var = ctk.StringVar()
        
        # Configure grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create main frame with modern styling
        main_frame = ctk.CTkFrame(self.root, corner_radius=20)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title with modern typography
        title_label = ctk.CTkLabel(main_frame, text="⚡ Bits & Bytes Converter", 
                                  font=ctk.CTkFont(family="SF Pro Display", size=28, weight="bold"))
        title_label.grid(row=0, column=0, pady=(30, 40), sticky="ew")
        
        # Conversion type selection with modern radio buttons
        type_frame = ctk.CTkFrame(main_frame, corner_radius=15)
        type_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 25))
        type_frame.grid_columnconfigure(0, weight=1)
        
        type_title = ctk.CTkLabel(type_frame, text="Conversion Type", 
                                 font=ctk.CTkFont(size=16, weight="bold"))
        type_title.grid(row=0, column=0, pady=(20, 15))
        
        self.radio1 = ctk.CTkRadioButton(type_frame, text="📊 Bytes to Bits (× 8)", 
                                        variable=self.conversion_type, value="bytes_to_bits",
                                        font=ctk.CTkFont(size=14))
        self.radio1.grid(row=1, column=0, pady=8, sticky="w", padx=20)
        
        self.radio2 = ctk.CTkRadioButton(type_frame, text="🔢 Bits to Bytes (÷ 8)", 
                                        variable=self.conversion_type, value="bits_to_bytes",
                                        font=ctk.CTkFont(size=14))
        self.radio2.grid(row=2, column=0, pady=(8, 20), sticky="w", padx=20)
        
        # Amount input with modern styling
        input_frame = ctk.CTkFrame(main_frame, corner_radius=15)
        input_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 25))
        input_frame.grid_columnconfigure(0, weight=1)
        
        input_title = ctk.CTkLabel(input_frame, text="Enter Amount", 
                                  font=ctk.CTkFont(size=16, weight="bold"))
        input_title.grid(row=0, column=0, pady=(20, 10))
        
        self.amount_entry = ctk.CTkEntry(input_frame, textvariable=self.amount_var, 
                                        font=ctk.CTkFont(size=16), 
                                        placeholder_text="Enter number here...",
                                        height=45, corner_radius=10)
        self.amount_entry.grid(row=1, column=0, pady=(0, 20), padx=20, sticky="ew")
        
        # Modern convert button with gradient effect
        convert_btn = ctk.CTkButton(main_frame, text="🚀 Convert", command=self.convert,
                                   font=ctk.CTkFont(size=18, weight="bold"), 
                                   height=50, corner_radius=25,
                                   hover_color=("#3B82F6", "#1E40AF"))
        convert_btn.grid(row=3, column=0, pady=(0, 25), padx=30, sticky="ew")
        
        # Result display with modern card styling
        result_frame = ctk.CTkFrame(main_frame, corner_radius=15)
        result_frame.grid(row=4, column=0, sticky="ew", padx=30, pady=(0, 30))
        result_frame.grid_columnconfigure(0, weight=1)
        
        result_title = ctk.CTkLabel(result_frame, text="Result", 
                                   font=ctk.CTkFont(size=16, weight="bold"))
        result_title.grid(row=0, column=0, pady=(20, 10))
        
        self.result_label = ctk.CTkLabel(result_frame, text="💡 Enter an amount and click Convert", 
                                        font=ctk.CTkFont(size=14), 
                                        wraplength=380, justify="center")
        self.result_label.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # Bind Enter key to convert
        self.amount_entry.bind('<Return>', lambda event: self.convert())
        self.amount_entry.focus_set()
    
    def convert(self):
        try:
            amount_str = self.amount_var.get().strip()
            if not amount_str:
                messagebox.showerror("Error", "Please enter a number")
                return
                
            amount = float(amount_str)
            if amount < 0:
                messagebox.showerror("Error", "Please enter a positive number")
                return
                
            conversion_type = self.conversion_type.get()
            
            if conversion_type == "bits_to_bytes":
                result = amount / 8
                if result == int(result):
                    result_text = f"✨ {amount:g} bits = {int(result)} bytes"
                else:
                    result_text = f"✨ {amount:g} bits = {result:.6g} bytes"
            else:  # bytes_to_bits
                result = amount * 8
                if result == int(result):
                    result_text = f"🔥 {amount:g} bytes = {int(result)} bits"
                else:
                    result_text = f"🔥 {amount:g} bytes = {result:.6g} bits"
            
            self.result_label.configure(text=result_text)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            self.amount_entry.focus_set()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

def main():
    root = ctk.CTk()
    app = BitsByteConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()