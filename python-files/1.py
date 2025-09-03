import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d

class DataAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Data Analyzer - Stress-Strain Curve Analysis")
        self.root.geometry("1200x800")
        
        # Initialize variables
        self.file_path = ""
        self.x_column = None
        self.y_column = None
        self.data = None
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create control panel
        self.create_control_panel()
        
        # Create plot panel
        self.create_plot_panel()
        
        # Create result panel
        self.create_result_panel()
    
    def create_control_panel(self):
        """Create the control panel with file selection and settings"""
        control_frame = ttk.LabelFrame(self.main_frame, text="Control Panel", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File selection
        file_frame = ttk.Frame(control_frame)
        file_frame.pack(fill=tk.X, pady=(5, 5))
        
        ttk.Label(file_frame, text="Excel File:").pack(side=tk.LEFT)
        self.file_label = ttk.Label(file_frame, text="No file selected", foreground="blue")
        self.file_label.pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Button(file_frame, text="Browse...", command=self.load_file).pack(side=tk.RIGHT)
        
        # Column selection
        col_frame = ttk.Frame(control_frame)
        col_frame.pack(fill=tk.X, pady=(5, 5))
        
        ttk.Label(col_frame, text="X Column:").pack(side=tk.LEFT)
        self.x_combo = ttk.Combobox(col_frame, state="readonly", width=15)
        self.x_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(col_frame, text="Y Column:").pack(side=tk.LEFT, padx=(20, 0))
        self.y_combo = ttk.Combobox(col_frame, state="readonly", width=15)
        self.y_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Processing controls
        proc_frame = ttk.Frame(control_frame)
        proc_frame.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Button(proc_frame, text="Process Data", command=self.process_data).pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(proc_frame, text="Export Results", command=self.export_results).pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(proc_frame, text="Clear", command=self.clear_data).pack(side=tk.LEFT, padx=(5, 5))
    
    def create_plot_panel(self):
        """Create the plotting panel"""
        plot_frame = ttk.LabelFrame(self.main_frame, text="Plot", padding="10")
        plot_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_result_panel(self):
        """Create the results panel"""
        result_frame = ttk.LabelFrame(self.main_frame, text="Results", padding="10")
        result_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Results display
        self.results_text = tk.Text(result_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.results_text.pack(fill=tk.BOTH, expand=True)
    
    def load_file(self):
        """Load Excel file and populate column comboboxes"""
        self.file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if self.file_path:
            self.file_label.config(text=self.file_path.split("/")[-1])
            
            try:
                self.data = pd.read_excel(self.file_path)
                
                # Populate column comboboxes
                columns = list(self.data.columns)
                self.x_combo['values'] = columns
                self.y_combo['values'] = columns
                
                if len(columns) > 0:
                    self.x_combo.current(0)
                    self.y_combo.current(1)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
    
    def process_data(self):
        """Process the data and update the plot"""
        if self.data is None or not self.x_combo.get() or not self.y_combo.get():
            messagebox.showwarning("Warning", "Please select a file and columns first!")
            return
        
        try:
            # Get selected columns
            x_col = self.x_combo.get()
            y_col = self.y_combo.get()
            
            # Extract data
            x = self.data[x_col].dropna()
            y = self.data[y_col].dropna()
            
            # Remove duplicate x values
            df_unique = pd.DataFrame({x_col: x, y_col: y}).groupby(x_col).mean().reset_index()
            x_clean = df_unique[x_col].values
            y_clean = df_unique[y_col].values
            
            # Apply smoothing
            y_smooth = gaussian_filter1d(y_clean, sigma=2)
            
            # Create interpolation function
            interp_func = interp1d(x_clean, y_smooth, kind='cubic', bounds_error=False, fill_value='extrapolate')
            
            # Generate points for smooth curve
            x_new = np.linspace(x_clean.min(), x_clean.max(), 2000)
            y_new = interp_func(x_new)
            
            # Find peak
            peak_y = np.max(y_smooth)
            peak_x = x_clean[np.argmax(y_smooth)]
            
            # Calculate areas
            total_area = np.trapz(y_new, x_new)
            peak_idx = np.argmin(np.abs(x_new - peak_x))
            area_before_peak = np.trapz(y_new[:peak_idx+1], x_new[:peak_idx+1])
            area_after_peak = np.trapz(y_new[peak_idx:], x_new[peak_idx:])
            
            # Update plot
            self.ax.clear()
            self.ax.plot(x_new, y_new, 'b-', linewidth=2, label=f'Total Area: {total_area:.2f}')
            self.ax.axhline(peak_y, color='r', linestyle='--', label=f'Peak: {peak_y:.2f}')
            self.ax.plot(peak_x, peak_y, 'ro', markersize=6)
            self.ax.set_xlabel(x_col)
            self.ax.set_ylabel(y_col)
            self.ax.set_title('Stress-Strain Curve Analysis')
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.ax.legend()
            self.canvas.draw()
            
            # Update results
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Analysis Results:\n\n")
            self.results_text.insert(tk.END, f"Total Area Under Curve: {total_area:.2f}\n")
            self.results_text.insert(tk.END, f"Area Before Peak: {area_before_peak:.2f}\n")
            self.results_text.insert(tk.END, f"Area After Peak: {area_after_peak:.2f}\n")
            self.results_text.insert(tk.END, f"Peak Value: {peak_y:.2f} at {peak_x:.2f}\n")
            self.results_text.config(state=tk.DISABLED)
            
        except KeyboardInterrupt:
            messagebox.showinfo("Info", "Data processing was interrupted.")
        except Exception as e:
            messagebox.showerror("Processing Error", str(e))
    
    def export_results(self):
        """Export results to a text file"""
        if not hasattr(self, 'results_text') or not self.results_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "No results to export!")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                title="Save Results As"
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(self.results_text.get(1.0, tk.END))
                
                messagebox.showinfo("Success", f"Results exported to {file_path}")
                
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
    
    def clear_data(self):
        """Clear all data and reset the interface"""
        self.file_path = ""
        self.file_label.config(text="No file selected")
        self.data = None
        self.x_combo.set('')
        self.y_combo.set('')
        self.ax.clear()
        self.canvas.draw()
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = DataAnalyzerApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Program interrupted by user.")

if __name__ == "__main__":
    main()