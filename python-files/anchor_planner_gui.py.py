import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
from typing import Dict, List, Any

class MaUWBAnchorPlannerGUI:
    def __init__(self):
        self.current_plan = None
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the GUI"""
        self.root = tk.Tk()
        self.root.title("MaUWB Anchor Deployment Planner")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Create main frame with scrollbar
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="MaUWB Anchor Deployment Planner", 
                              font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Input Frame
        self.create_input_frame(main_frame)
        
        # Results Frame
        self.create_results_frame(main_frame)
        
        # Initially hide results
        self.results_frame.pack_forget()
    
    def create_input_frame(self, parent):
        """Create input controls"""
        input_frame = tk.Frame(parent, bg='#ffffff', relief=tk.RAISED, bd=2)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Input frame title
        input_title = tk.Label(input_frame, text="Configuration", 
                              font=('Arial', 14, 'bold'), bg='#ffffff', fg='#34495e')
        input_title.pack(pady=10)
        
        # Number of anchors
        anchors_frame = tk.Frame(input_frame, bg='#ffffff')
        anchors_frame.pack(pady=10)
        
        tk.Label(anchors_frame, text="Number of Anchors (1-200):", 
                font=('Arial', 11), bg='#ffffff').pack(side=tk.LEFT, padx=10)
        
        self.num_anchors_var = tk.StringVar(value="10")
        num_anchors_entry = tk.Entry(anchors_frame, textvariable=self.num_anchors_var, 
                                   font=('Arial', 11), width=10)
        num_anchors_entry.pack(side=tk.LEFT, padx=10)
        
        # PAN ID
        pan_frame = tk.Frame(input_frame, bg='#ffffff')
        pan_frame.pack(pady=10)
        
        tk.Label(pan_frame, text="PAN ID (0-255):", 
                font=('Arial', 11), bg='#ffffff').pack(side=tk.LEFT, padx=10)
        
        self.pan_id_var = tk.StringVar(value="100")
        pan_id_entry = tk.Entry(pan_frame, textvariable=self.pan_id_var, 
                               font=('Arial', 11), width=10)
        pan_id_entry.pack(side=tk.LEFT, padx=10)
        
        # Generate button
        generate_btn = tk.Button(input_frame, text="Generate Plan", 
                               command=self.generate_plan, 
                               font=('Arial', 12, 'bold'), 
                               bg='#3498db', fg='white', 
                               padx=20, pady=10, cursor='hand2')
        generate_btn.pack(pady=20)
    
    def create_results_frame(self, parent):
        """Create results display area"""
        self.results_frame = tk.Frame(parent, bg='#f0f0f0')
        
        # Results title
        results_title = tk.Label(self.results_frame, text="Deployment Plan Results", 
                                font=('Arial', 16, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        results_title.pack(pady=(0, 15))
        
        # Metrics frame
        self.create_metrics_frame()
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Anchor table tab
        self.create_anchor_table_tab()
        
        # Class distribution tab
        self.create_class_distribution_tab()
        
        # Arduino code tab
        self.create_arduino_code_tab()
        
        # Export buttons
        self.create_export_buttons()
    
    def create_metrics_frame(self):
        """Create summary metrics display"""
        metrics_frame = tk.Frame(self.results_frame, bg='#ffffff', relief=tk.RAISED, bd=2)
        metrics_frame.pack(fill=tk.X, pady=(0, 10))
        
        metrics_title = tk.Label(metrics_frame, text="Summary Metrics", 
                                font=('Arial', 12, 'bold'), bg='#ffffff')
        metrics_title.pack(pady=5)
        
        self.metrics_display = tk.Frame(metrics_frame, bg='#ffffff')
        self.metrics_display.pack(pady=10)
    
    def create_anchor_table_tab(self):
        """Create anchor assignments table"""
        table_frame = ttk.Frame(self.notebook)
        self.notebook.add(table_frame, text="Anchor Assignments")
        
        # Treeview for table
        columns = ('ID', 'Class', 'PAN ID', 'Code Define')
        self.anchor_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.anchor_tree.heading(col, text=col)
            self.anchor_tree.column(col, width=150, anchor=tk.CENTER)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.anchor_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.anchor_tree.xview)
        self.anchor_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack elements
        self.anchor_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_class_distribution_tab(self):
        """Create class distribution display"""
        dist_frame = ttk.Frame(self.notebook)
        self.notebook.add(dist_frame, text="Class Distribution")
        
        self.class_display = scrolledtext.ScrolledText(dist_frame, font=('Courier', 10), 
                                                      wrap=tk.WORD, height=20)
        self.class_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_arduino_code_tab(self):
        """Create Arduino code display"""
        code_frame = ttk.Frame(self.notebook)
        self.notebook.add(code_frame, text="Arduino Code")
        
        # Code display
        self.code_display = scrolledtext.ScrolledText(code_frame, font=('Courier', 10), 
                                                     wrap=tk.WORD, height=18)
        self.code_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Copy button
        copy_btn = tk.Button(code_frame, text="Copy Code", command=self.copy_code,
                           font=('Arial', 10), bg='#27ae60', fg='white', padx=15, pady=5)
        copy_btn.pack(pady=5)
    
    def create_export_buttons(self):
        """Create export buttons"""
        export_frame = tk.Frame(self.results_frame, bg='#f0f0f0')
        export_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(export_frame, text="Export to Text File", command=self.export_to_file,
                 font=('Arial', 10), bg='#e74c3c', fg='white', padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(export_frame, text="Export to JSON", command=self.export_to_json,
                 font=('Arial', 10), bg='#9b59b6', fg='white', padx=15, pady=5).pack(side=tk.LEFT, padx=5)
    
    def generate_plan(self):
        """Generate anchor deployment plan"""
        try:
            # Get input values
            num_anchors = int(self.num_anchors_var.get())
            pan_id = int(self.pan_id_var.get())
            
            # Validation
            if not (1 <= num_anchors <= 200):
                messagebox.showerror("Error", "Please enter a valid number of anchors (1-200)")
                return
            
            if not (0 <= pan_id <= 255):
                messagebox.showerror("Error", "Please enter a valid PAN ID (0-255)")
                return
            
            # Generate plan
            anchors = []
            class_distribution = {i: [] for i in range(8)}
            
            for anchor_id in range(num_anchors):
                anchor_class = anchor_id % 8
                
                anchor = {
                    'id': anchor_id,
                    'class': anchor_class,
                    'pan_id': pan_id,
                    'code_define': f'#define UWB_INDEX {anchor_id}'
                }
                
                anchors.append(anchor)
                class_distribution[anchor_class].append(anchor_id)
            
            self.current_plan = {
                'anchors': anchors,
                'class_distribution': class_distribution,
                'num_anchors': num_anchors,
                'pan_id': pan_id
            }
            
            # Display results
            self.display_results()
            
            # Show results frame
            self.results_frame.pack(fill=tk.BOTH, expand=True)
            
            messagebox.showinfo("Success", "Plan generated successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def display_results(self):
        """Display the generated plan results"""
        if not self.current_plan:
            return
        
        plan = self.current_plan
        
        # Update metrics
        self.update_metrics()
        
        # Update anchor table
        self.update_anchor_table()
        
        # Update class distribution
        self.update_class_distribution()
        
        # Update Arduino code
        self.update_arduino_code()
    
    def update_metrics(self):
        """Update summary metrics display"""
        # Clear existing metrics
        for widget in self.metrics_display.winfo_children():
            widget.destroy()
        
        plan = self.current_plan
        active_classes = len([arr for arr in plan['class_distribution'].values() if len(arr) > 0])
        max_tag_communication = min(8, active_classes)
        
        # Create metric boxes
        metrics = [
            ("Total Anchors", plan['num_anchors']),
            ("PAN ID", plan['pan_id']),
            ("Active Classes", active_classes),
            ("Max Tag Communication", max_tag_communication)
        ]
        
        for i, (label, value) in enumerate(metrics):
            metric_frame = tk.Frame(self.metrics_display, bg='#3498db', relief=tk.RAISED, bd=2)
            metric_frame.grid(row=0, column=i, padx=10, pady=5)
            
            value_label = tk.Label(metric_frame, text=str(value), font=('Arial', 16, 'bold'), 
                                  bg='#3498db', fg='white')
            value_label.pack(pady=5)
            
            label_label = tk.Label(metric_frame, text=label, font=('Arial', 10), 
                                  bg='#3498db', fg='white')
            label_label.pack(pady=(0, 5))
    
    def update_anchor_table(self):
        """Update anchor assignments table"""
        # Clear existing items
        for item in self.anchor_tree.get_children():
            self.anchor_tree.delete(item)
        
        # Add new items
        for anchor in self.current_plan['anchors']:
            self.anchor_tree.insert('', tk.END, values=(
                anchor['id'], anchor['class'], anchor['pan_id'], anchor['code_define']
            ))
    
    def update_class_distribution(self):
        """Update class distribution display"""
        self.class_display.delete(1.0, tk.END)
        
        content = "CLASS DISTRIBUTION ANALYSIS\n"
        content += "=" * 50 + "\n\n"
        
        for class_num in range(8):
            anchors_in_class = self.current_plan['class_distribution'][class_num]
            anchor_count = len(anchors_in_class)
            anchor_ids = ', '.join(map(str, anchors_in_class)) if anchors_in_class else 'None'
            
            content += f"Class {class_num}:\n"
            content += f"  • Count: {anchor_count} anchor(s)\n"
            content += f"  • IDs: {anchor_ids}\n"
            content += f"  • Usage: {'Active' if anchor_count > 0 else 'Inactive'}\n\n"
        
        self.class_display.insert(1.0, content)
    
    def update_arduino_code(self):
        """Update Arduino code display"""
        self.code_display.delete(1.0, tk.END)
        
        plan = self.current_plan
        code_examples = []
        examples_to_show = min(5, plan['num_anchors'])  # Show up to 5 examples
        
        code_examples.append("// MaUWB Anchor Configuration Examples")
        code_examples.append("// Copy and paste the relevant section for each anchor\n")
        
        for i in range(examples_to_show):
            anchor = plan['anchors'][i]
            code = f"// Anchor {anchor['id']} (Class {anchor['class']})\n"
            code += f"#define UWB_INDEX {anchor['id']}\n"
            code += f"#define PAN_INDEX {plan['pan_id']}\n"
            code += f"#define ANCHOR\n"
            code += f"#define UWB_TAG_COUNT 64\n"
            code_examples.append(code)
        
        if plan['num_anchors'] > 5:
            code_examples.append(f"// ... Continue with remaining anchor IDs {examples_to_show} to {plan['num_anchors'] - 1}")
            code_examples.append(f"// Follow the same pattern: UWB_INDEX = anchor_id")
        
        self.code_display.insert(1.0, '\n'.join(code_examples))
    
    def copy_code(self):
        """Copy Arduino code to clipboard"""
        try:
            code_text = self.code_display.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(code_text)
            messagebox.showinfo("Success", "Code copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy code: {str(e)}")
    
    def export_to_file(self):
        """Export plan to text file"""
        if not self.current_plan:
            messagebox.showwarning("Warning", "No plan to export. Generate a plan first.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Plan As"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    plan = self.current_plan
                    active_classes = len([arr for arr in plan['class_distribution'].values() if len(arr) > 0])
                    
                    f.write("MaUWB ANCHOR DEPLOYMENT PLAN\n")
                    f.write("=" * 40 + "\n\n")
                    f.write(f"Total Anchors: {plan['num_anchors']}\n")
                    f.write(f"PAN ID: {plan['pan_id']}\n")
                    f.write(f"Active Classes: {active_classes}\n\n")
                    
                    f.write("ANCHOR ASSIGNMENTS:\n")
                    f.write("-" * 30 + "\n")
                    for anchor in plan['anchors']:
                        f.write(f"ID: {anchor['id']}, Class: {anchor['class']}, {anchor['code_define']}\n")
                    
                    f.write(f"\nARDUINO CODE:\n")
                    f.write("-" * 20 + "\n")
                    f.write(self.code_display.get(1.0, tk.END))
                
                messagebox.showinfo("Success", f"Plan exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export file: {str(e)}")
    
    def export_to_json(self):
        """Export plan to JSON file"""
        if not self.current_plan:
            messagebox.showwarning("Warning", "No plan to export. Generate a plan first.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Plan As JSON"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.current_plan, f, indent=2)
                
                messagebox.showinfo("Success", f"Plan exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export JSON: {str(e)}")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


# Main execution
if __name__ == "__main__":
    print("Starting MaUWB Anchor Deployment Planner GUI...")
    app = MaUWBAnchorPlannerGUI()
    app.run()
