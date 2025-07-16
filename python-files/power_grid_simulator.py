# power_grid_simulator.py
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation
from warnings import warn
import os

plt.style.use('seaborn-v0_8')

class PowerGridSimulator:
    def __init__(self):
        """Initialize the simulator with default values"""
        self.results = None
        self.V_source = None
        self.R_transformer = None
        
    def simulate(self, V_source, R_transformer, load_resistances):
        """Core simulation engine with error checking"""
        self.V_source = V_source
        self.R_transformer = R_transformer
        self.results = []
        
        for i, R_load in enumerate(load_resistances):
            if R_load <= 0:
                raise ValueError(f"Load {i+1}: Resistance must be positive (got {R_load}Ω)")
                
            R_total = R_transformer + R_load
            I = V_source / R_total
            V_load = I * R_load
            P_load = V_load * I

            self.results.append({
                'Load #': i + 1,
                'R_load (Ω)': R_load,
                'Current (A)': I,
                'V_load (V)': V_load,
                'Power (W)': P_load,
                'Efficiency (%)': (P_load / (V_source * I)) * 100
            })
        
        return self.results
    
    def plot_results(self):
        """Dynamic plotting with multiple visualization types"""
        if not self.results:
            raise ValueError("No simulation results available. Run simulate() first.")
            
        fig = plt.figure(figsize=(min(14, len(self.results)*3), 10))
        loads = [r['Load #'] for r in self.results]
        
        # Voltage Distribution
        ax1 = plt.subplot(2, 2, 1)
        voltages = [r['V_load (V)'] for r in self.results]
        ax1.bar(loads, voltages, color='skyblue')
        ax1.set_title('Voltage Distribution')
        ax1.set_ylabel('Voltage (V)')
        ax1.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Power Delivery
        ax2 = plt.subplot(2, 2, 2)
        powers = [r['Power (W)'] for r in self.results]
        ax2.bar(loads, powers, color='salmon')
        if max(powers)/min(powers) > 100:  # Auto-detect log scale need
            ax2.set_yscale('log')
            ax2.set_ylabel('Power (W) - Log Scale')
        ax2.set_title('Power Delivery')
        ax2.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Efficiency Pie Chart
        ax3 = plt.subplot(2, 2, 3)
        efficiencies = [r['Efficiency (%)'] for r in self.results]
        ax3.pie(efficiencies, labels=[f"Load {l}" for l in loads], 
                autopct='%1.1f%%', startangle=90)
        ax3.set_title('Energy Efficiency')
        
        # 3D Power Visualization (New Feature)
        ax4 = plt.subplot(2, 2, 4, projection='3d')
        x = np.array(loads)
        y = np.array([r['Current (A)'] for r in self.results])
        z = np.array(powers)
        ax4.bar3d(x, np.zeros(len(x)), y, 1, 1, z, shade=True)
        ax4.set_title('3D Power Profile')
        ax4.set_xlabel('Load #')
        ax4.set_ylabel('Current (A)')
        ax4.set_zlabel('Power (W)')
        
        plt.suptitle(f'Power Grid Analysis | Source: {self.V_source}V, Transformer R: {self.R_transformer}Ω', y=1.02)
        plt.tight_layout()
        plt.show()
    
    def animate_power_flow(self):
        """Creates smooth power delivery animation"""
        if not self.results:
            raise ValueError("No simulation results available.")
            
        fig, ax = plt.subplots(figsize=(8, 4))
        x = np.arange(len(self.results))
        powers = [r['Power (W)'] for r in self.results]
        bars = ax.bar(x, [0]*len(x), color='salmon')
        
        def animate(i):
            for bar, power in zip(bars, powers):
                bar.set_height(power * (i/20))  # Gradual ramp
            ax.set_ylim(0, max(powers)*1.1)
            ax.set_title(f'Power Delivery Ramp-Up ({i*5}% of max)')
            return bars
        
        ani = FuncAnimation(fig, animate, frames=20, interval=50, blit=True)
        plt.show()
    
    def export_results(self, filename="grid_results"):
        """Exports to Excel and PDF with multiple formats"""
        if not self.results:
            raise ValueError("No results to export.")
            
        # Excel Export
        excel_file = f"{filename}.xlsx"
        try:
            with pd.ExcelWriter(excel_file) as writer:
                pd.DataFrame(self.results).to_excel(writer, sheet_name='Raw Data', index=False)
                
                summary = pd.DataFrame({
                    'Metric': ['Total Power', 'Avg Efficiency', 'Max Voltage'],
                    'Value': [
                        sum(r['Power (W)'] for r in self.results),
                        np.mean([r['Efficiency (%)'] for r in self.results]),
                        max([r['V_load (V)'] for r in self.results])
                    ],
                    'Unit': ['W', '%', 'V']
                })
                summary.to_excel(writer, sheet_name='Summary', index=False)
            
            print(f"✅ Excel report saved to {os.path.abspath(excel_file)}")
        except PermissionError:
            print(f"❌ Error: Could not save Excel file (is it open elsewhere?)")
        
        # PDF Export (requires matplotlib)
        pdf_file = f"{filename}.pdf"
        try:
            from matplotlib.backends.backend_pdf import PdfPages
            with PdfPages(pdf_file) as pdf:
                # Create summary figure
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.axis('off')
                plt.text(0.1, 0.9, f"Power Grid Simulation Report", fontsize=14)
                plt.text(0.1, 0.8, f"Source Voltage: {self.V_source} V", fontsize=10)
                plt.text(0.1, 0.7, f"Transformer R: {self.R_transformer} Ω", fontsize=10)
                plt.text(0.1, 0.6, f"Total Power: {sum(r['Power (W)'] for r in self.results):.2f} W", fontsize=10)
                pdf.savefig(fig)
                plt.close()
                
                # Add results table
                fig, ax = plt.subplots(figsize=(10, len(self.results)*0.5))
                ax.axis('off')
                table = ax.table(cellText=pd.DataFrame(self.results).values,
                                colLabels=pd.DataFrame(self.results).columns,
                                loc='center')
                table.auto_set_font_size(False)
                table.set_fontsize(8)
                pdf.savefig(fig)
                plt.close()
            
            print(f"✅ PDF report saved to {os.path.abspath(pdf_file)}")
        except ImportError:
            warn("PDF export requires matplotlib. Install with: pip install matplotlib")

def get_user_inputs():
    """Interactive input with validation and defaults"""
    print("\n🔌 POWER GRID SIMULATOR v2.0")
    print("Press Enter to use default values\n")
    
    try:
        V_source = float(input(f"Source voltage [V] (default 20000): ") or 20000)
        R_transformer = float(input(f"Transformer resistance [Ω] (default 0.05): ") or 0.05)
        
        n = int(input(f"Number of loads (default 3): ") or 3)
        load_resistances = []
        for i in range(n):
            while True:
                r = input(f"Load {i+1} resistance [Ω] (default {10**(i+1)}): ") or 10**(i+1)
                if float(r) > 0:
                    load_resistances.append(float(r))
                    break
                print("❌ Resistance must be positive!")
                
        return V_source, R_transformer, load_resistances
    
    except ValueError:
        print("❌ Invalid input. Using default values.")
        return 20000, 0.05, [10, 100, 1000]

if __name__ == "__main__":
    simulator = PowerGridSimulator()
    V, R, loads = get_user_inputs()
    
    try:
        results = simulator.simulate(V, R, loads)
        
        # Display results
        print("\n=== SIMULATION RESULTS ===")
        print(pd.DataFrame(results).to_string(index=False))
        
        # Visualizations
        simulator.plot_results()
        simulator.animate_power_flow()
        
        # Export
        simulator.export_results()
        
    except Exception as e:
        print(f"❌ Simulation failed: {str(e)}")
        