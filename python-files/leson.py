import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import customtkinter as ctk
import threading
import json
import os
from docxtpl import DocxTemplate

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DocumentGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Document Generator")
        self.geometry("800x600")
        self.minsize(700, 500)
        
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Title label
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Document Generator", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Description label
        self.desc_label = ctk.CTkLabel(
            self.main_frame,
            text="Enter JSON data below to generate Word documents",
            font=ctk.CTkFont(size=14)
        )
        self.desc_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # JSON input frame
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_rowconfigure(0, weight=1)
        
        # JSON input text area
        self.json_text = scrolledtext.ScrolledText(
            self.input_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg="#2b2b2b",
            fg="white",
            insertbackground="white"
        )
        self.json_text.grid(row=0, column=0, sticky="nsew")
        
        # Sample JSON data
        sample_data = '''[
  {
    "MainTopic": "Interest and Interest Rate",
    "section": "Simple Interest Calculations",
    "Objectives": "By the end of the lesson, learners will be able to distinguish between interest and interest rate, and calculate simple interest using the formula: Interest = Principal × Rate × Time.",
    "priorKnowledge": "Learners should be able to perform basic arithmetic operations, understand percentages, and have a basic knowledge of financial terms such as saving and borrowing.",
    "lessonContent": "Introduction to interest and interest rate: definition of key terms (principal, interest, interest rate, time period). Explanation that interest is the amount earned or charged in rands, while interest rate is the percentage used to calculate that amount. Worked examples showing how to calculate simple interest per year, per month, and over multiple years. Learners will practice calculations using real-life scenarios such as savings and loans.",
    "teacherActivity1": "Explain the difference between interest and interest rate using the example of R500 invested at 1.3% p.a. resulting in R6.50 interest earned.",
    "teacherActivity2": "Demonstrate how to calculate simple interest for one year and over multiple years using the formula and examples from the resource (e.g., R1 000 at 2.25% p.a.).",
    "teacherActivity3": "Guide learners through calculating monthly interest by dividing annual interest by 12, using the example of R22.50 ÷ 12.",
    "teacherActivity4": "Work through a problem where learners must determine the interest rate given the principal and interest earned (e.g., R80 interest on R1 600).",
    "learnerActivity1": "Listening attentively",
    "learnerActivity2": "Taking notes",
    "learnerActivity3": "Writing work"
  },
  {
    "MainTopic": "Banking, Loans and Investments",
    "section": "Interpreting Bank Statements",
    "Objectives": "By the end of the lesson, learners will be able to identify and interpret key features of a bank statement, distinguish between debit and credit transactions, and calculate totals such as deposits, bank charges, and closing balance.",
    "priorKnowledge": "Learners should understand basic financial transactions, the concept of income and expenses, and be able to perform addition and subtraction with decimal numbers.",
    "lessonContent": "Explanation of banking terminology: savings account, cheque account, debit/credit transactions, EFT, stop order, debit order, overdraft, and bank fees. Analysis of a sample bank statement showing opening balance, transactions (debits and credits), interest, fees, and closing balance. Learners will interpret the statement by answering questions on transaction types, total deposits, interest charged, and balance status.",
    "teacherActivity1": "Introduce bank statement components using the example of Mr. PP Jonathan’s statement, explaining terms like opening balance, debit, credit, and overdraft.",
    "teacherActivity2": "Walk through each transaction type (e.g., ATM withdrawal, salary deposit, stop order) and classify them as debit or credit.",
    "teacherActivity3": "Demonstrate how to calculate total deposits and total bank charges from the statement.",
    "teacherActivity4": "Explain how to determine whether the closing balance is a credit or debit and discuss implications.",
    "learnerActivity1": "Listening attentively",
    "learnerActivity2": "Taking notes",
    "learnerActivity3": "Writing work"
  }
]'''
        self.json_text.insert(tk.END, sample_data)
        
        # Button frame
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)
        
        # Generate button
        self.generate_button = ctk.CTkButton(
            self.button_frame,
            text="Generate Documents",
            command=self.start_generation,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.generate_button.grid(row=0, column=0, padx=20, pady=10)
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(self.main_frame)
        self.progress.set(0)
        self.progress.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Ready to generate documents",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # Bind Enter key to generate
        self.bind("<Return>", lambda event: self.start_generation())
    
    def validate_json(self):
        """Validate JSON input"""
        try:
            data = self.json_text.get("1.0", tk.END).strip()
            if not data:
                raise ValueError("Empty input")
            parsed = json.loads(data)
            if not isinstance(parsed, list):
                raise ValueError("JSON must be an array")
            return parsed
        except json.JSONDecodeError as e:
            messagebox.showerror("Invalid JSON", f"Invalid JSON format:\n{str(e)}")
            return None
        except ValueError as e:
            messagebox.showerror("Invalid Data", str(e))
            return None
    
    def generate_documents(self):
        """Main document generation function"""
        # Validate input
        context = self.validate_json()
        if not context:
            return
        
        # Check template file
        template_filename = "tpl.docx"
        if not os.path.exists(template_filename):
            messagebox.showerror(
                "Missing Template", 
                f"Template file '{template_filename}' not found in the current directory."
            )
            return
        
        # Load template
        try:
            doc = DocxTemplate(template_filename)
        except Exception as e:
            messagebox.showerror("Template Error", f"Failed to load template: {str(e)}")
            return
        
        # Generate documents
        success_count = 0
        for i, item in enumerate(context):
            try:
                doc.render(item)
                output_filename = f"filled_document_{i+1}.docx"
                doc.save(output_filename)
                success_count += 1
                self.update_status(f"Generated document {i+1}/{len(context)}")
                self.progress.set((i + 1) / len(context))
                self.update_idletasks()
            except Exception as e:
                self.update_status(f"Error generating document {i+1}: {str(e)}")
                messagebox.showwarning("Generation Warning", f"Failed to generate document {i+1}: {str(e)}")
        
        # Final message
        self.update_status(f"Completed! Generated {success_count}/{len(context)} documents.")
        self.progress.set(1)
        
        if success_count == len(context):
            messagebox.showinfo("Success", f"All {len(context)} documents generated successfully!")
        else:
            messagebox.showwarning(
                "Partial Success", 
                f"Generated {success_count}/{len(context)} documents successfully."
            )
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.configure(text=message)
    
    def start_generation(self):
        """Start generation in separate thread"""
        self.generate_button.configure(state="disabled")
        self.update_status("Starting document generation...")
        self.progress.set(0)
        
        # Run in separate thread to prevent UI freezing
        thread = threading.Thread(target=self.generate_documents)
        thread.daemon = True
        thread.start()
        
        # Check thread status
        def check_thread():
            if thread.is_alive():
                self.after(100, check_thread)
            else:
                self.generate_button.configure(state="normal")
                self.update_status("Generation complete")
        
        self.after(100, check_thread)

if __name__ == "__main__":
    app = DocumentGeneratorApp()
    app.mainloop()