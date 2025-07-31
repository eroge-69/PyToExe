import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class HVACStaticPressureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HVAC Static Pressure Calculator")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.duct_length = tk.DoubleVar(value=100)
        self.duct_diameter = tk.DoubleVar(value=12)
        self.airflow_rate = tk.DoubleVar(value=1000)
        self.friction_rate = tk.DoubleVar(value=0.1)
        self.system_components = []
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="HVAC Static Pressure Calculator", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="System Parameters", padding="10")
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Duct length
        ttk.Label(input_frame, text="Duct Length (ft):").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(input_frame, textvariable=self.duct_length, width=15).grid(row=0, column=1, pady=5, padx=(10,0))
        
        # Duct diameter
        ttk.Label(input_frame, text="Duct Diameter (in):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(input_frame, textvariable=self.duct_diameter, width=15).grid(row=1, column=1, pady=5, padx=(10,0))
        
        # Airflow rate
        ttk.Label(input_frame, text="Airflow Rate (CFM):").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(input_frame, textvariable=self.airflow_rate, width=15).grid(row=2, column=1, pady=5, padx=(10,0))
        
        # Friction rate
        ttk.Label(input_frame, text="Friction Rate (in WC/100ft):").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(input_frame, textvariable=self.friction_rate, width=15).grid(row=3, column=1, pady=5, padx=(10,0))
        
        # Component frame
        component_frame = ttk.LabelFrame(main_frame, text="System Components", padding="10")
        component_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Component listbox
        self.component_listbox = tk.Listbox(component_frame, height=8, width=30)
        self.component_listbox.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Component entry
        self.component_var = tk.StringVar()
        self.loss_var = tk.DoubleVar()
        ttk.Entry(component_frame, textvariable=self.component_var, width=20).grid(row=1, column=0, pady=2)
        ttk.Entry(component_frame, textvariable=self.loss_var, width=10).grid(row=1, column=1, pady=2, padx=(5,0))
        ttk.Label(component_frame, text="Component").grid(row=2, column=0)
        ttk.Label(component_frame, text="Loss (in WC)").grid(row=2, column=1)
        
        # Add component button
        ttk.Button(component_frame, text="Add Component", command=self.add_component).grid(row=3, column=0, columnspan=2, pady=5)
        
        # Remove component button
        ttk.Button(component_frame, text="Remove Selected", command=self.remove_component).grid(row=4, column=0, columnspan=2, pady=5)
        
        # Calculate button
        ttk.Button(main_frame, text="Calculate Static Pressure", command=self.calculate_pressure,
                  style="Accent.TButton").grid(row=2, column=0, columnspan=3, pady=20)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Results labels
        self.duct_loss_label = ttk.Label(results_frame, text="Duct Friction Loss: 0.00 in WC")
        self.duct_loss_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.component_loss_label = ttk.Label(results_frame, text="Component Losses: 0.00 in WC")
        self.component_loss_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.total_loss_label = ttk.Label(results_frame, text="Total Static Pressure: 0.00 in WC")
        self.total_loss_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        self.velocity_label = ttk.Label(results_frame, text="Air Velocity: 0.00 ft/min")
        self.velocity_label.grid(row=3, column=0, sticky=tk.W, pady=2)
        
        # Graph frame
        graph_frame = ttk.Frame(main_frame)
        graph_frame.grid(row=4, column=0, columnspan=3, pady=(20, 0), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Initial plot
        self.update_plot()
        
    def add_component(self):
        component = self.component_var.get().strip()
        loss = self.loss_var.get()
        
        if component and loss > 0:
            self.system_components.append((component, loss))
            self.component_listbox.insert(tk.END, f"{component}: {loss} in WC")
            self.component_var.set("")
            self.loss_var.set(0.0)
        else:
            messagebox.showwarning("Input Error", "Please enter valid component name and loss value.")
            
    def remove_component(self):
        selection = self.component_listbox.curselection()
        if selection:
            index = selection[0]
            self.component_listbox.delete(index)
            del self.system_components[index]
        else:
            messagebox.showwarning("Selection Error", "Please select a component to remove.")
            
    def calculate_pressure(self):
        try:
            # Get input values
            length = self.duct_length.get()
            diameter = self.duct_diameter.get()
            airflow = self.airflow_rate.get()
            friction_rate = self.friction_rate.get()
            
            # Calculate duct friction loss
            duct_loss = (length / 100) * friction_rate
            
            # Calculate component losses
            component_loss = sum(loss for _, loss in self.system_components)
            
            # Calculate total static pressure
            total_loss = duct_loss + component_loss
            
            # Calculate air velocity
            cross_sectional_area = 3.14159 * (diameter/24)**2  # Convert diameter to feet
            velocity = airflow / cross_sectional_area if cross_sectional_area > 0 else 0
            
            # Update result labels
            self.duct_loss_label.config(text=f"Duct Friction Loss: {duct_loss:.2f} in WC")
            self.component_loss_label.config(text=f"Component Losses: {component_loss:.2f} in WC")
            self.total_loss_label.config(text=f"Total Static Pressure: {total_loss:.2f} in WC")
            self.velocity_label.config(text=f"Air Velocity: {velocity:.0f} ft/min")
            
            # Update plot
            self.update_plot()
            
        except Exception as e:
            messagebox.showerror("Calculation Error", f"An error occurred: {str(e)}")
            
    def update_plot(self):
        # Clear the previous plot
        self.ax.clear()
        
        # Sample data for visualization
        components = [comp[0] for comp in self.system_components]
        losses = [comp[1] for comp in self.system_components]
        
        # Add duct loss
        components.insert(0, "Duct Friction")
        losses.insert(0, (self.duct_length.get() / 100) * self.friction_rate.get())
        
        # Create bar chart
        y_pos = np.arange(len(components))
        colors = ['#1f77b4' if i == 0 else '#ff7f0e' for i in range(len(components))]
        
        bars = self.ax.barh(y_pos, losses, color=colors)
        self.ax.set_yticks(y_pos)
        self.ax.set_yticklabels(components)
        self.ax.set_xlabel('Pressure Loss (in WC)')
        self.ax.set_title('Static Pressure Distribution')
        self.ax.grid(axis='x', alpha=0.3)
        
        # Add value labels on bars
        for i, (bar, loss) in enumerate(zip(bars, losses)):
            self.ax.text(loss + 0.01*max(losses), bar.get_y() + bar.get_height()/2, 
                        f'{loss:.2f}', va='center', ha='left')
        
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = HVACStaticPressureApp(root)
    root.mainloop()