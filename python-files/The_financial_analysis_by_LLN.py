# lln_simulator.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import messagebox, filedialog

# --- Core Simulation Logic ---
def simulate_law_of_large_numbers(sample_sizes, uniform_low, uniform_high, normal_mean, normal_std):
    bernoulli_props = []
    normal_means = []
    for N in sample_sizes:
        N = int(N)
        bernoulli_data = np.random.uniform(uniform_low, uniform_high, N)
        bernoulli_props.append(np.mean(bernoulli_data))
        normal_data = np.random.normal(normal_mean, normal_std, N)
        normal_means.append(np.mean(normal_data))
    return bernoulli_props, normal_means
# --- Animation Plot ---
def animate_results(sample_sizes, bernoulli_props, normal_means, uniform_expected_mean, normal_expected_mean, interval):
    fig, axs = plt.subplots(1, 2, figsize=(14, 5))
    plt.suptitle('Law of Large Numbers Simulation (Animated)', fontsize=16, fontweight='bold')

    for ax in axs:
        ax.set_xscale('log')
        ax.grid(True)

    axs[0].set_title('Uniform Distribution Mean Convergence')
    axs[0].set_xlabel('Sample Size (log scale)')
    axs[0].set_ylabel('Sample Mean')
    axs[0].axhline(uniform_expected_mean, color='red', linestyle='--', label=f'Expected ≈ {uniform_expected_mean:.2f}')
    axs[0].legend()

    axs[1].set_title('Normal Distribution Mean Convergence')
    axs[1].set_xlabel('Sample Size (log scale)')
    axs[1].set_ylabel('Mean')
    axs[1].axhline(normal_expected_mean, color='red', linestyle='--', label=f'Expected ≈ {normal_expected_mean:.2f}')
    axs[1].legend()

    use_marker = len(sample_sizes) <= 1000
    bern_line, = axs[0].plot([], [], color='blue', marker='o' if use_marker else '')
    norm_line, = axs[1].plot([], [], color='green', marker='o' if use_marker else '')

    def update(frame):
        x = sample_sizes[:frame + 1]
        y1 = bernoulli_props[:frame + 1]
        y2 = normal_means[:frame + 1]

        axs[0].set_xlim(1, sample_sizes[-1] * 1.1)
        axs[1].set_xlim(1, sample_sizes[-1] * 1.1)
        axs[0].set_ylim(min(y1) - 0.05, max(y1) + 0.05)
        axs[1].set_ylim(min(y2) - 0.05, max(y2) + 0.05)

        bern_line.set_data(x, y1)
        norm_line.set_data(x, y2)

        return bern_line, norm_line

    ani = FuncAnimation(fig, update, frames=len(sample_sizes), interval=interval, repeat=False)
    plt.tight_layout()
    plt.show()

# --- Save to CSV ---
def save_to_csv(sample_sizes, bernoulli_props, normal_means):
    df = pd.DataFrame({
        'Sample Size': sample_sizes,
        'Uniform Mean': bernoulli_props,
        'Normal Mean': normal_means
    })
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if file_path:
        df.to_csv(file_path, index=False)
        messagebox.showinfo("Success", f"Results saved to:\n{file_path}")

# --- Optional GUI Entrypoint ---
def main():
    def run_simulation():
        try:
            steps = int(entry_steps.get())
            uniform_low = float(entry_uniform_low.get())
            uniform_high = float(entry_uniform_high.get())
            normal_mean = float(entry_normal_mean.get())
            normal_std = float(entry_normal_std.get())
        except:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values.")
            return

        sample_sizes = np.logspace(1, 6, num=steps)
        interval = max(30, min(300, int(5000 / steps)))
        uniform_expected = (uniform_low + uniform_high) / 2
        normal_expected = normal_mean

        bern, norm = simulate_law_of_large_numbers(sample_sizes, uniform_low, uniform_high, normal_mean, normal_std)
        save_to_csv(sample_sizes, bern, norm)
        animate_results(sample_sizes, bern, norm, uniform_expected, normal_expected, interval)

    root = tk.Tk()
    root.title("Law of Large Numbers Simulator")

    tk.Label(root, text="Number of Steps (default=50):").grid(row=0, column=0, sticky="e")
    entry_steps = tk.Entry(root)
    entry_steps.insert(0, "50")
    entry_steps.grid(row=0, column=1)

    tk.Label(root, text="Uniform Lower Bound (default=0):").grid(row=1, column=0, sticky="e")
    entry_uniform_low = tk.Entry(root)
    entry_uniform_low.insert(0, "0")
    entry_uniform_low.grid(row=1, column=1)

    tk.Label(root, text="Uniform Upper Bound (default=2):").grid(row=2, column=0, sticky="e")
    entry_uniform_high = tk.Entry(root)
    entry_uniform_high.insert(0, "2")
    entry_uniform_high.grid(row=2, column=1)

    tk.Label(root, text="Normal Mean (default=0):").grid(row=3, column=0, sticky="e")
    entry_normal_mean = tk.Entry(root)
    entry_normal_mean.insert(0, "0")
    entry_normal_mean.grid(row=3, column=1)

    tk.Label(root, text="Normal Std Dev (default=1):").grid(row=4, column=0, sticky="e")
    entry_normal_std = tk.Entry(root)
    entry_normal_std.insert(0, "1")
    entry_normal_std.grid(row=4, column=1)

    tk.Button(root, text="Run Simulation", command=run_simulation, bg="green", fg="white").grid(row=5, column=0, columnspan=2, pady=10)

    root.mainloop()

# Only run GUI if this file is executed directly
if __name__ == "__main__":
    main()
import pandas as pd

def Monthly_financial_data(filename):
    """
    Analyze monthly financial data for employees from an Excel file.
    
    Args:
        filename (str): Path to the Excel file containing monthly salary data
    """
    # Monthly fixed expenses (same for all employees)
    expenses = [8000, 9500, 7000, 9000, 10500, 8500,
                9000, 9500, 10000, 11000, 9500, 10500]

    # Month names (used for column access)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Read salary data from Excel file
    df = pd.read_excel(filename)

    # Analyze data for each employee
    for row in df.itertuples(index=False):
        employee = row.Employee
        revenue = [getattr(row, month) for month in months]
        total = sum(revenue)

        # Calculate monthly profit = Revenue - Expenses
        profit = [r - e for r, e in zip(revenue, expenses)]

        # Calculate profit after tax (30% tax)
        profit_after_tax = [round(p * 0.7, 2) for p in profit]

        # Calculate profit margin percentage for each month
        profit_margin = [round((p / r) * 100, 2) if r != 0 else 0 
                        for p, r in zip(profit_after_tax, revenue)]

        # Calculate average profit after tax
        average_pat = sum(profit_after_tax) / len(profit_after_tax)

        # Determine good and bad months
        good_months = [pat > average_pat for pat in profit_after_tax]
        bad_months = [not good for good in good_months]

        # Best and worst month
        max_pat = max(profit_after_tax)
        min_pat = min(profit_after_tax)
        best_month = months[profit_after_tax.index(max_pat)]
        worst_month = months[profit_after_tax.index(min_pat)]

        # Display results
        print(f"\n--- Financial Summary for {employee} ---")
        print("Revenue:", revenue)
        print("Expenses:", expenses)
        print("Profit:", profit)
        print("Profit After Tax:", profit_after_tax)
        print("Profit Margin (%):", profit_margin)
        print("Good Months:", [months[i] for i, val in enumerate(good_months) if val])
        print("Bad Months:", [months[i] for i, val in enumerate(bad_months) if val])
        print("Best Month:", best_month)
        print("Worst Month:", worst_month)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def analyze_employee_efficiency(
    num_employees=10,
    num_weeks=4,
    min_hours=35,
    max_hours=50,
    min_productivity=70,
    max_productivity=100,
    show_plots=True,
    show_bonus_analysis=True,
    export_to_csv=True,
    random_seed=None
):
    """
    Analyze employee work hours and productivity data with visualization and statistical analysis.
    
    Parameters:
    - num_employees: Number of employees to analyze
    - num_weeks: Number of weeks to track
    - min_hours: Minimum work hours per week
    - max_hours: Maximum work hours per week
    - min_productivity: Minimum productivity score
    - max_productivity: Maximum productivity score
    - show_plots: Whether to display visualizations
    - show_bonus_analysis: Whether to perform bonus analyses
    - export_to_csv: Whether to export results to CSV
    - random_seed: Seed for reproducible random results
    
    Returns:
    - DataFrame containing all analysis results
    """
    
    if random_seed is not None:
        np.random.seed(random_seed)
    
    # 1. Create data for working hours and productivity
    work_hours = np.random.randint(min_hours, max_hours+1, size=(num_employees, num_weeks))
    productivity = np.random.randint(min_productivity, max_productivity+1, size=(num_employees, num_weeks))
    
    # 2. Analyze data for Week 1 only
    df = pd.DataFrame({
        'Employee ID': np.arange(1, num_employees+1),
        'Week 1 Hours': work_hours[:, 0],
        'Week 1 Productivity': productivity[:, 0]
    })
    df.set_index('Employee ID', inplace=True)
    df['Efficiency'] = df['Week 1 Productivity'] / df['Week 1 Hours']
    
    # 3. Plot efficiency bar chart
    if show_plots:
        plt.figure(figsize=(10, 5))
        plt.bar(df.index, df['Efficiency'], color='teal')
        plt.title(f'Employee Efficiency in Week 1 (n={num_employees})')
        plt.xlabel('Employee ID')
        plt.ylabel('Productivity per Hour')
        plt.grid(True)
        plt.show()
    
    # 4. Reshape examples
    if num_employees * num_weeks == 40:  # Only works for default 10x4 case
        reshaped_C = work_hours.reshape((5, 8), order='C')
        reshaped_F = work_hours.reshape((5, 8), order='F')
        print("\nReshape (C-order):\n", reshaped_C)
        print("\nReshape (F-order):\n", reshaped_F)
    
    if show_bonus_analysis:
        # BONUS 1: Most efficient employee in Week 1
        top_eff = df['Efficiency'].idxmax()
        print(f"\nMost efficient employee in Week 1 is Employee {top_eff} with efficiency {df.loc[top_eff, 'Efficiency']:.2f}")
        
        # BONUS 2: Average efficiency across all weeks
        efficiency_all_weeks = productivity / work_hours
        avg_efficiency = efficiency_all_weeks.mean(axis=1)
        df['Avg Efficiency'] = avg_efficiency
        
        # BONUS 3: Employees with weekly improvement
        if num_weeks > 1:
            improvement_flags = np.all(np.diff(efficiency_all_weeks, axis=1) > 0, axis=1)
            df['Consistent Improvement'] = improvement_flags
        
        # BONUS 4: Correlation matrix
        corr_matrix = np.corrcoef(work_hours.flatten(), productivity.flatten())
        print("\nCorrelation matrix between work hours and productivity:\n", corr_matrix)
        
        # BONUS 5: Subplots for all employees' efficiency trends
        if show_plots and num_weeks > 1:
            weeks = [f'Week {i+1}' for i in range(num_weeks)]
            fig, axs = plt.subplots((num_employees+1)//2, 2, figsize=(15, num_employees*1.5))
            fig.suptitle(f'Efficiency Trends Over {num_weeks} Weeks (All Employees)', fontsize=16, y=1.02)
            
            for i in range(num_employees):
                row = i // 2
                col = i % 2
                axs[row, col].plot(weeks, efficiency_all_weeks[i], marker='o', color='royalblue')
                axs[row, col].set_title(f'Employee {i+1} Efficiency')
                axs[row, col].grid(True)
            
            plt.tight_layout()
            plt.show()
        
        # BONUS 6: Best average performer
        best_avg_id = df['Avg Efficiency'].idxmax()
        print(f"\nTop performer over {num_weeks} weeks: Employee {best_avg_id} with avg efficiency {df.loc[best_avg_id, 'Avg Efficiency']:.2f}")
    
    # BONUS 7: Export to CSV
    if export_to_csv:
        filename = f"employee_efficiency_report_{num_employees}emp_{num_weeks}wks.csv"
        df.to_csv(filename)
        print(f"\nData has been saved to {filename}")
    
    return df

# Example usage:
# analyze_employee_efficiency()  # Default parameters (10 employees, 4 weeks)
# analyze_employee_efficiency(num_employees=8, num_weeks=5, random_seed=42)  # Custom parameters
# results_df = analyze_employee_efficiency(show_plots=False)  # Get results without plots
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

def moving_average_transfer_function(N):
    """
    Returns numerator (b) and denominator (a) coefficients for N-point moving average filter.
    """
    b = np.ones(N) / N
    a = np.array([1])
    return b, a

def print_transfer_function_zdomain(N):
    try:
        if N is None or N <= 0:
            return "Invalid N value"
        result = f"H(z) = (1/{N}) * (1 - z^(-{N})) / (1 - z^(-1))"
        print("\nMoving Average Transfer Function (Z-domain):")
        print(result)
        return result
    except Exception as e:
        print(f"Error in z-domain transfer function: {str(e)}")
        return "Error calculating z-domain transfer function"

def print_transfer_function_Rdomain(N):
    try:
        if N is None or N <= 0:
            return "Invalid N value"
        result = f"H(s) = (1 - e^(-{N}s)) / ({N}s)"  # Laplace domain equivalent
        print("\nMoving Average Transfer Function (Real domain):")
        print(result)
        return result
    except Exception as e:
        print(f"Error in real domain transfer function: {str(e)}")
        return "Error calculating real domain transfer function"

def check_stability(b, a):
    """
    Checks filter stability (FIR moving average filter is always stable, but let's show zeros).
    """
    zeros = np.roots(b)
    poles = np.roots(a)
    print("\nFilter Zeros:", zeros)
    print("Filter Poles:", poles)
    # For stability, all poles must be inside the unit circle (for FIR, pole at 0)
    if np.all(np.abs(poles) < 1):
        print("✅ The system is STABLE: All poles are inside the unit circle.")
        return True
    else:
        print("❌ The system is UNSTABLE: Some poles are outside the unit circle.")
        return False

def plot_frequency_response(b, a, N):
    w, h = signal.freqz(b, a)
    plt.figure(figsize=(8, 4))
    plt.plot(w/np.pi, 20 * np.log10(np.abs(h)), color='red')
    plt.title(f'Moving Average Filter Frequency Response (N={N})')
    plt.xlabel('Normalized Frequency (×π rad/sample)')
    plt.ylabel('Magnitude (dB)')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Example: Import salary sequence from your LLN tab (replace with actual data)
    # For demonstration, generate random salary data
    N = 10  # Window size (can be set by user)
    num_salaries = 100
    salaries = np.random.normal(loc=15000, scale=2000, size=num_salaries)

    # 1. Print Transfer Function
   

    # 2. Get filter coefficients
    b, a = moving_average_transfer_function(N)

    # 3. Check stability
    stable = check_stability(b, a)

    # 4. If stable, show frequency response
    if stable:
        print("\nFrequency response of the stable moving average filter:")
        plot_frequency_response(b, a, N)
import numpy as np
import pandas as pd

def moving_average_transfer_function(N):
    b = np.ones(N) / N
    a = np.array([1])
    return b, a

def compute_fluctuation(filtered_salary):
    # Use standard deviation as a measure of fluctuation
    return np.std(filtered_salary)

def compare_excel_stability(file_paths, window_size=None):
    result = []
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for path in file_paths:
        df = pd.read_excel(path)
        salary_list = []
        for row in df.itertuples(index=False):
            salary_list.extend([getattr(row, month) for month in months if month in df.columns])
        salaries = np.array(salary_list)
        N = window_size if window_size is not None else min(12, len(salaries)) # default to 12 or min
        b, a = moving_average_transfer_function(N)
        filtered = np.convolve(salaries, b, mode='valid')
        fluctuation = compute_fluctuation(filtered)
        result.append({
            'file': path,
            'fluctuation': fluctuation,
            'filtered': filtered
        })
    # Sort by lowest fluctuation
    result.sort(key=lambda x: x['fluctuation'])
    return result
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

def moving_average_transfer_function(N):
    """
    Returns numerator (b) and denominator (a) coefficients for N-point moving average filter.
    """
    b = np.ones(N) / N
    a = np.array([1])
    return b, a

def print_transfer_function_zdomain(N):
    try:
        if N is None or N <= 0:
            return "Invalid N value"
        result = f"H(z) = (1/{N}) * (1 - z^(-{N})) / (1 - z^(-1))"
        print("\nMoving Average Transfer Function (Z-domain):")
        print(result)
        return result
    except Exception as e:
        print(f"Error in z-domain transfer function: {str(e)}")
        return "Error calculating z-domain transfer function"

def print_transfer_function_Rdomain(N):
    try:
        if N is None or N <= 0:
            return "Invalid N value"
        result = f"H(s) = (1 - e^(-{N}s)) / ({N}s)"  # Laplace domain equivalent
        print("\nMoving Average Transfer Function (Real domain):")
        print(result)
        return result
    except Exception as e:
        print(f"Error in real domain transfer function: {str(e)}")
        return "Error calculating real domain transfer function"

def check_stability(b, a):
    """
    Checks filter stability (FIR moving average filter is always stable, but let's show zeros).
    """
    zeros = np.roots(b)
    poles = np.roots(a)
    print("\nFilter Zeros:", zeros)
    print("Filter Poles:", poles)
    # For stability, all poles must be inside the unit circle (for FIR, pole at 0)
    if np.all(np.abs(poles) < 1):
        print("✅ The system is STABLE: All poles are inside the unit circle.")
        return True
    else:
        print("❌ The system is UNSTABLE: Some poles are outside the unit circle.")
        return False

def plot_frequency_response(b, a, N):
    w, h = signal.freqz(b, a)
    plt.figure(figsize=(8, 4))
    plt.plot(w/np.pi, 20 * np.log10(np.abs(h)), color='red')
    plt.title(f'Moving Average Filter Frequency Response (N={N})')
    plt.xlabel('Normalized Frequency (×π rad/sample)')
    plt.ylabel('Magnitude (dB)')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Example: Import salary sequence from your LLN tab (replace with actual data)
    # For demonstration, generate random salary data
    N = 10  # Window size (can be set by user)
    num_salaries = 100
    salaries = np.random.normal(loc=15000, scale=2000, size=num_salaries)

    # 1. Print Transfer Function
   

    # 2. Get filter coefficients
    b, a = moving_average_transfer_function(N)

    # 3. Check stability
    stable = check_stability(b, a)

    # 4. If stable, show frequency response
    if stable:
        print("\nFrequency response of the stable moving average filter:")
        plot_frequency_response(b, a, N)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from matplotlib.animation import FuncAnimation
from tkinter import font as tkfont
from scipy import signal
import seaborn as sns

from Law_of_large_Numbers import simulate_law_of_large_numbers

from salary_lln_transfer_function_analysis import (
    moving_average_transfer_function,
    print_transfer_function_Rdomain,
    print_transfer_function_zdomain,
    check_stability,
    plot_frequency_response
)
class LuxeFinancialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LUXURY Financial Analytics Suite")
        self.root.attributes('-fullscreen', True)
        # Red-black luxury scheme with gold tabs/buttons
        self.bg_color = "#171718"
        self.accent_color = "#FFD700"  # Gold for tabs/buttons
        self.button_color = "#FFD700"
        self.secondary_color = "#FF3B3F"  # Red for everything else
        self.text_color = "#FFFFFF"
        self.panel_color = "#232326"
        self.highlight_color = "#FF3B3F"
        self.line_color = "#FF3B3F"
        self.title_font = tkfont.Font(family="Helvetica", size=22, weight="bold")
        self.header_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.normal_font = tkfont.Font(family="Helvetica", size=11)
        self.root.configure(bg=self.bg_color)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        # Tab colors
        self.style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        self.style.configure('TNotebook.Tab', background=self.panel_color, foreground=self.text_color, padding=[25, 10], font=self.header_font)
        self.style.map('TNotebook.Tab', background=[('selected', self.accent_color)], foreground=[('selected', self.secondary_color)])
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        self.style.configure('TButton', background=self.button_color, foreground="#171718", font=self.normal_font, padding=8)
        self.style.map('TButton', background=[('active', self.secondary_color)], foreground=[('active', '#171718')])
        self.style.configure('TEntry', fieldbackground=self.panel_color, foreground=self.text_color, insertcolor=self.text_color, borderwidth=2)
        self.style.configure('Treeview', background=self.panel_color, foreground=self.text_color, fieldbackground=self.panel_color, borderwidth=0, font=self.normal_font)
        self.style.map('Treeview', background=[('selected', self.secondary_color)], foreground=[('selected', '#FFD700')])
        self.style.configure('Vertical.TScrollbar', background=self.panel_color, troughcolor=self.bg_color, bordercolor=self.bg_color, arrowcolor=self.text_color)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.salary_frame = ttk.Frame(self.notebook)
        self.lln_frame = ttk.Frame(self.notebook)
        self.lln_salary_frame = ttk.Frame(self.notebook)
        self.transfer_function_frame = ttk.Frame(self.notebook)
        self.transfer_comparator_frame = ttk.Frame(self.notebook)  
        self.stability_comparator_frame = ttk.Frame(self.notebook) 
        self.notebook.add(self.salary_frame, text="💰 Salary Analysis")
        self.notebook.add(self.lln_frame, text="📈 LLN Simulation")
        self.notebook.add(self.lln_salary_frame, text="📊 Salary LLN Analyzer")
        self.notebook.add(self.transfer_function_frame, text="🧮 Salary Transfer Function")
        self.notebook.add(self.transfer_comparator_frame, text="📶 Transfer Function Comparator")  
        self.notebook.add(self.stability_comparator_frame, text="📊 Stability Comparator")
        self.axs_lln = None
        self.animation = None
        self.employee_data = {}
        self.salary_data = None
        self.transfer_salary_data = None
        self.setup_salary_tab()
        self.setup_lln_tab()
        self.setup_lln_salary_tab()
        self.setup_transfer_function_tab()
        self.setup_transfer_comparator_tab()
        self.setup_stability_comparator_tab()
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, style='TLabel')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.stability_files = []
        self.stability_results = {}
        self.comparison_frame = None  # Add this in __init__
        self.add_logo()
        root.bind("<Escape>", lambda e: self.toggle_fullscreen())
        root.bind("<F11>", lambda e: self.toggle_fullscreen())
        root.bind("<Right>", self.next_tab)
        root.bind("<Left>", self.prev_tab)
        
    def toggle_fullscreen(self, event=None):
        is_fullscreen = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not is_fullscreen)

    def next_tab(self, event=None):
        try:
            current = self.notebook.index(self.notebook.select())
            next_index = (current + 1) % self.notebook.index("end")
            self.notebook.select(next_index)
        except Exception:
            pass

    def prev_tab(self, event=None):
        try:
            current = self.notebook.index(self.notebook.select())
            prev_index = (current - 1) % self.notebook.index("end")
            self.notebook.select(prev_index)
        except Exception:
            pass

    def add_logo(self):
        logo_frame = ttk.Frame(self.root, style='TFrame')
        logo_frame.pack(side=tk.TOP, fill=tk.X)
        logo_label = ttk.Label(logo_frame,
            text="LUXURY FINANCIAL ANALYTICS",
            font=self.title_font,
            foreground=self.button_color,
            background=self.bg_color)
        logo_label.pack(pady=18)

    def setup_salary_tab(self):
        main_frame = ttk.Frame(self.salary_frame, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=32, pady=32)
        input_frame = ttk.LabelFrame(main_frame, text="⚙️ Input Parameters", padding=(20, 14), style='TFrame')
        input_frame.pack(fill=tk.X, pady=(0, 22))
        file_row = ttk.Frame(input_frame, style='TFrame')
        file_row.pack(fill=tk.X, pady=7)
        ttk.Label(file_row, text="📂 Salary Excel File:", style='TLabel').pack(side=tk.LEFT, padx=6)
        self.file_entry = ttk.Entry(file_row, width=44, style='TEntry')
        self.file_entry.pack(side=tk.LEFT, padx=8, expand=True, fill=tk.X)
        browse_btn = ttk.Button(file_row, text="Browse", command=self.browse_file)
        browse_btn.pack(side=tk.LEFT, padx=8)
        expenses_row = ttk.Frame(input_frame, style='TFrame')
        expenses_row.pack(fill=tk.X, pady=7)
        ttk.Label(expenses_row, text="💸 Monthly Expenses (comma separated):", style='TLabel').pack(side=tk.LEFT, padx=6)
        self.expenses_entry = ttk.Entry(expenses_row, width=44, style='TEntry')
        self.expenses_entry.pack(side=tk.LEFT, padx=8, expand=True, fill=tk.X)
        self.expenses_entry.insert(0, "8000,9500,7000,9000,10500,8500,9000,9500,10000,11000,9500,10500")
        tax_row = ttk.Frame(input_frame, style='TFrame')
        tax_row.pack(fill=tk.X, pady=7)
        ttk.Label(tax_row, text="🏛️ Tax Rate (%):", style='TLabel').pack(side=tk.LEFT, padx=6)
        self.tax_entry = ttk.Entry(tax_row, width=12, style='TEntry')
        self.tax_entry.pack(side=tk.LEFT, padx=8)
        self.tax_entry.insert(0, "30")
        analyze_btn = ttk.Button(input_frame, text="🔍 Analyze Data", command=self.analyze_salaries, style='Accent.TButton')
        analyze_btn.pack(pady=13)
        reset_btn = ttk.Button(input_frame, text="🔄 Reset", command=lambda: self.reset_tab("salary"), style='Accent.TButton')
        reset_btn.pack(side=tk.RIGHT, padx=7)

        # Layout: Treeview and details on left, profit plot on right (responsive)
        results_frame = ttk.Frame(main_frame, style='TFrame')
        results_frame.pack(fill=tk.BOTH, expand=True)
        body_frame = ttk.Frame(results_frame, style='TFrame')
        body_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(body_frame, style='TFrame')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        tree_frame = ttk.Frame(left_frame, style='TFrame')
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 13))
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree = ttk.Treeview(tree_frame,
            columns=("Employee", "Total Revenue", "Avg Profit", "Best Month", "Worst Month"),
            show="headings",
            yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=self.tree.yview)
        self.tree.heading("Employee", text="👤 Employee")
        self.tree.heading("Total Revenue", text="💰 Total Revenue")
        self.tree.heading("Avg Profit", text="📊 Avg Profit")
        self.tree.heading("Best Month", text="⭐ Best Month")
        self.tree.heading("Worst Month", text="⚠️ Worst Month")
        self.tree.column("Employee", width=150)
        self.tree.column("Total Revenue", width=120, anchor=tk.E)
        self.tree.column("Avg Profit", width=120, anchor=tk.E)
        self.tree.column("Best Month", width=100, anchor=tk.CENTER)
        self.tree.column("Worst Month", width=100, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)
        detail_frame = ttk.LabelFrame(left_frame, text="📝 Employee Details",
            padding=14, style='TFrame')
        detail_frame.pack(fill=tk.BOTH, pady=(13, 0))
        self.detail_text = scrolledtext.ScrolledText(detail_frame,
            height=12,
            wrap=tk.WORD,
            bg=self.panel_color,
            fg=self.text_color,
            insertbackground=self.text_color,
            font=self.normal_font,
            borderwidth=0)
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        right_frame = ttk.Frame(body_frame, style='TFrame')
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        plot_label = ttk.Label(right_frame, text="📈 Profit Graph", font=self.header_font, background=self.panel_color, foreground=self.button_color)
        plot_label.pack(pady=10)
        self.fig_salary, self.ax_salary = plt.subplots(figsize=(12, 6))
        self.fig_salary.patch.set_facecolor(self.panel_color)
        self.ax_salary.set_facecolor(self.panel_color)
        for spine in self.ax_salary.spines.values():
            spine.set_color(self.secondary_color)
        self.ax_salary.tick_params(colors=self.text_color)
        self.ax_salary.title.set_color(self.button_color)
        self.ax_salary.xaxis.label.set_color(self.text_color)
        self.ax_salary.yaxis.label.set_color(self.text_color)
        self.canvas_salary = FigureCanvasTkAgg(self.fig_salary, right_frame)
        self.canvas_salary.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas_salary, right_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.bind("<<TreeviewSelect>>", self.show_employee_details)

    def setup_lln_tab(self):
        main_frame = ttk.Frame(self.lln_frame, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=32, pady=32)
        input_frame = ttk.LabelFrame(main_frame, text="⚙️ Simulation Parameters",
            padding=20, style='TFrame')
        input_frame.pack(fill=tk.X, pady=(0, 22))
        steps_row = ttk.Frame(input_frame, style='TFrame')
        steps_row.pack(fill=tk.X, pady=7)
        ttk.Label(steps_row, text="🔢 Number of Steps:", style='TLabel').pack(side=tk.LEFT, padx=8)
        self.steps_entry = ttk.Entry(steps_row, width=12, style='TEntry')
        self.steps_entry.pack(side=tk.LEFT, padx=8)
        self.steps_entry.insert(0, "50")
        uniform_frame = ttk.LabelFrame(input_frame, text="Uniform Distribution",
            padding=12, style='TFrame')
        uniform_frame.pack(fill=tk.X, pady=7)
        ttk.Label(uniform_frame, text="Low:", style='TLabel').grid(row=0, column=0, sticky=tk.W, padx=4)
        self.uniform_low_entry = ttk.Entry(uniform_frame, width=10, style='TEntry')
        self.uniform_low_entry.grid(row=0, column=1, padx=8, sticky=tk.W)
        self.uniform_low_entry.insert(0, "0")
        ttk.Label(uniform_frame, text="High:", style='TLabel').grid(row=0, column=2, sticky=tk.W, padx=6)
        self.uniform_high_entry = ttk.Entry(uniform_frame, width=10, style='TEntry')
        self.uniform_high_entry.grid(row=0, column=3, padx=8, sticky=tk.W)
        self.uniform_high_entry.insert(0, "2")
        normal_frame = ttk.LabelFrame(input_frame, text="Normal Distribution",
            padding=12, style='TFrame')
        normal_frame.pack(fill=tk.X, pady=7)
        ttk.Label(normal_frame, text="Mean:", style='TLabel').grid(row=0, column=0, sticky=tk.W, padx=4)
        self.normal_mean_entry = ttk.Entry(normal_frame, width=10, style='TEntry')
        self.normal_mean_entry.grid(row=0, column=1, padx=8, sticky=tk.W)
        self.normal_mean_entry.insert(0, "0")
        ttk.Label(normal_frame, text="Std Dev:", style='TLabel').grid(row=0, column=2, sticky=tk.W, padx=6)
        self.normal_std_entry = ttk.Entry(normal_frame, width=10, style='TEntry')
        self.normal_std_entry.grid(row=0, column=3, padx=8, sticky=tk.W)
        self.normal_std_entry.insert(0, "1")
        speed_row = ttk.Frame(input_frame, style='TFrame')
        speed_row.pack(fill=tk.X, pady=7)
        ttk.Label(speed_row, text="⏱️ Animation Speed:", style='TLabel').pack(side=tk.LEFT, padx=8)
        self.speed_slider = ttk.Scale(speed_row, from_=1, to=10, orient=tk.HORIZONTAL)
        self.speed_slider.pack(side=tk.LEFT, padx=8, expand=True, fill=tk.X)
        self.speed_slider.set(5)
        sim_btn = ttk.Button(input_frame, text="🚀 Run Simulation", command=self.run_simulation, style='Accent.TButton')
        sim_btn.pack(pady=16)
        reset_btn = ttk.Button(input_frame, text="🔄 Reset", command=lambda: self.reset_tab("lln"), style='Accent.TButton')
        reset_btn.pack(side=tk.RIGHT, padx=8)
        plot_frame = ttk.Frame(main_frame, style='TFrame')
        plot_frame.pack(fill=tk.BOTH, expand=True)
        self.fig_lln = plt.figure(figsize=(14, 5), facecolor=self.panel_color)
        self.axs_lln = self.fig_lln.subplots(1, 2)
        self.canvas_lln = FigureCanvasTkAgg(self.fig_lln, plot_frame)
        self.canvas_lln.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas_lln, plot_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_lln_salary_tab(self):
        main_frame = ttk.Frame(self.lln_salary_frame, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=32, pady=32)
        input_frame = ttk.LabelFrame(main_frame, text="⚙️ Salary LLN Parameters", padding=20, style='TFrame')
        input_frame.pack(fill=tk.X, pady=(0, 22))
        file_row = ttk.Frame(input_frame, style='TFrame')
        file_row.pack(fill=tk.X, pady=8)
        ttk.Label(file_row, text="📂 Salary Excel File:", style='TLabel').pack(side=tk.LEFT, padx=8)
        self.lln_salary_file_entry = ttk.Entry(file_row, width=44, style='TEntry')
        self.lln_salary_file_entry.pack(side=tk.LEFT, padx=8, expand=True, fill=tk.X)
        browse_btn = ttk.Button(file_row, text="Browse", command=self.browse_lln_salary_file)
        browse_btn.pack(side=tk.LEFT, padx=8)
        sim_btn = ttk.Button(input_frame, text="🚀 Run Salary LLN Simulation", command=self.run_salary_lln, style='Accent.TButton')
        sim_btn.pack(pady=16)
        reset_btn = ttk.Button(input_frame, text="🔄 Reset", command=lambda: self.reset_tab("lln_salary"), style='Accent.TButton')
        reset_btn.pack(side=tk.RIGHT, padx=8)
        stats_frame = ttk.LabelFrame(main_frame, text="📈 Salary Stats & LLN", padding=20, style='TFrame')
        stats_frame.pack(fill=tk.X, pady=(16, 0))
        self.lln_salary_stats_text = scrolledtext.ScrolledText(stats_frame, height=12, wrap=tk.WORD, bg=self.panel_color, fg=self.text_color, insertbackground=self.text_color, font=self.normal_font, borderwidth=0)
        self.lln_salary_stats_text.pack(fill=tk.X, expand=True)
        plot_frame = ttk.Frame(main_frame, style='TFrame')
        plot_frame.pack(fill=tk.BOTH, expand=True, pady=(16, 0))
        self.fig_lln_salary, self.ax_lln_salary = plt.subplots(figsize=(12, 5))
        self.fig_lln_salary.patch.set_facecolor(self.panel_color)
        self.ax_lln_salary.set_facecolor(self.panel_color)
        for spine in self.ax_lln_salary.spines.values():
            spine.set_color(self.secondary_color)
        self.ax_lln_salary.tick_params(colors=self.text_color)
        self.ax_lln_salary.title.set_color(self.button_color)
        self.ax_lln_salary.xaxis.label.set_color(self.text_color)
        self.ax_lln_salary.yaxis.label.set_color(self.text_color)
        self.canvas_lln_salary = FigureCanvasTkAgg(self.fig_lln_salary, plot_frame)
        self.canvas_lln_salary.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas_lln_salary, plot_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
            self.status_var.set(f"Selected file: {filename}")

    def browse_lln_salary_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if filename:
            self.lln_salary_file_entry.delete(0, tk.END)
            self.lln_salary_file_entry.insert(0, filename)
            self.status_var.set(f"Selected salary file for LLN: {filename}")

    def reset_tab(self, tab_name):
        try:
            if tab_name == "salary":
                self.file_entry.delete(0, tk.END)
                self.expenses_entry.delete(0, tk.END)
                self.expenses_entry.insert(0, "8000,9500,7000,9000,10500,8500,9000,9500,10000,11000,9500,10500")
                self.tax_entry.delete(0, tk.END)
                self.tax_entry.insert(0, "30")
                for item in self.tree.get_children():
                    self.tree.delete(item)
                self.detail_text.delete(1.0, tk.END)
                self.ax_salary.clear()
                self.ax_salary.set_facecolor(self.panel_color)
                self.canvas_salary.draw()
            elif tab_name == "lln":
                self.steps_entry.delete(0, tk.END)
                self.steps_entry.insert(0, "50")
                self.uniform_low_entry.delete(0, tk.END)
                self.uniform_low_entry.insert(0, "0")
                self.uniform_high_entry.delete(0, tk.END)
                self.uniform_high_entry.insert(0, "2")
                self.normal_mean_entry.delete(0, tk.END)
                self.normal_mean_entry.insert(0, "0")
                self.normal_std_entry.delete(0, tk.END)
                self.normal_std_entry.insert(0, "1")
                self.speed_slider.set(5)
                self.fig_lln.clf()
                self.axs_lln = self.fig_lln.subplots(1, 2)
                for ax in self.axs_lln:
                    ax.set_facecolor(self.panel_color)
                    for spine in ax.spines.values():
                        spine.set_color(self.secondary_color)
                    ax.tick_params(colors=self.text_color)
                    ax.title.set_color(self.button_color)
                    ax.xaxis.label.set_color(self.text_color)
                    ax.yaxis.label.set_color(self.text_color)
                self.canvas_lln.draw()
            elif tab_name == "lln_salary":
                self.lln_salary_file_entry.delete(0, tk.END)
                self.lln_salary_stats_text.delete(1.0, tk.END)
                self.ax_lln_salary.clear()
                self.ax_lln_salary.set_facecolor(self.panel_color)
                self.canvas_lln_salary.draw()
            elif tab_name == "transfer_comparator":
            # Reset transfer comparator tab
                if hasattr(self, 'transfer_comp_files'):
                    self.transfer_comp_files = []
                if hasattr(self, 'transfer_comp_files_var'):
                    self.transfer_comp_files_var.set("No files selected")
                if hasattr(self, 'transfer_comp_N_entry'):
                    self.transfer_comp_N_entry.delete(0, tk.END)
                    self.transfer_comp_N_entry.insert(0, "10")
                if hasattr(self, 'ax_transfer_comp'):
                    self.ax_transfer_comp.clear()
                    self.ax_transfer_comp.set_facecolor(self.panel_color)
                if hasattr(self, 'canvas_transfer_comp'):
                    self.canvas_transfer_comp.draw()
                if hasattr(self, 'transfer_comp_metrics_text'):
                    self.transfer_comp_metrics_text.delete(1.0, tk.END)
            elif tab_name == "stability":
                # Add this to clear stability files and results
                self.stability_files = []
                self.stability_results = {}
                self.stability_files_var.set("No files selected")
                self.stability_N_entry.delete(0, tk.END)
                self.stability_N_entry.insert(0, "10")
                for item in self.stability_tree.get_children():
                    self.stability_tree.delete(item)
                self.ax_stability.clear()
                self.ax_stability.set_facecolor(self.panel_color)
                self.canvas_stability.draw()

            self.status_var.set(f"{tab_name.capitalize()} tab reset to defaults")
        except Exception:
            self.status_var.set(f"{tab_name.capitalize()} tab reset to defaults (safe)")

    def analyze_salaries(self):
        filename = self.file_entry.get()
        try:
            if not filename:
                messagebox.showerror("Error", "Please select an Excel file")
                return
            if not os.path.exists(filename):
                messagebox.showerror("Error", "The specified file does not exist")
                return
            expenses = list(map(float, self.expenses_entry.get().split(',')))
            if len(expenses) != 12:
                messagebox.showerror("Error", "Please enter exactly 12 monthly expenses")
                return
            tax_rate = float(self.tax_entry.get()) / 100
            if not 0 <= tax_rate <= 1:
                messagebox.showerror("Error", "Tax rate must be between 0 and 100")
                return
            df = pd.read_excel(filename)
            if 'Employee' not in df.columns:
                messagebox.showerror("Error", "Excel file must contain an 'Employee' column")
                return
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.employee_data = {}
            for row in df.itertuples(index=False):
                employee = row.Employee
                revenue = [getattr(row, month) for month in months]
                total = sum(revenue)
                profit = [r - e for r, e in zip(revenue, expenses)]
                profit_after_tax = [round(p * (1 - tax_rate), 2) for p in profit]
                profit_margin = [round((p / r) * 100, 2) if r != 0 else 0 for p, r in zip(profit_after_tax, revenue)]
                average_pat = sum(profit_after_tax) / len(profit_after_tax)
                max_pat = max(profit_after_tax)
                min_pat = min(profit_after_tax)
                best_month = months[profit_after_tax.index(max_pat)]
                worst_month = months[profit_after_tax.index(min_pat)]
                self.employee_data[employee] = {
                    'revenue': revenue,
                    'expenses': expenses,
                    'profit': profit,
                    'profit_after_tax': profit_after_tax,
                    'profit_margin': profit_margin,
                    'average_pat': average_pat,
                    'best_month': best_month,
                    'worst_month': worst_month
                }
                self.tree.insert("", tk.END, values=(
                    employee,
                    f"${total:,.2f}",
                    f"${average_pat:,.2f}",
                    best_month,
                    worst_month
                ))
            if len(df) > 0:
                self.update_salary_plot(df.iloc[0].Employee)
            self.salary_data = df
            self.status_var.set("Salary analysis completed successfully")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error in salary analysis")

    def show_employee_details(self, event):
        try:
            selected = self.tree.focus()
            if selected:
                employee = self.tree.item(selected, 'values')[0]
                data = self.employee_data[employee]
                details = f"📊 Employee: {employee}\n\n"
                details += "Month\tRevenue\tExpense\tProfit\tAfter Tax\tMargin(%)\n"
                details += "-"*60 + "\n"
                for i, month in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                    details += f"{month}\t${data['revenue'][i]:.2f}\t${data['expenses'][i]:.2f}\t"
                    details += f"${data['profit'][i]:.2f}\t${data['profit_after_tax'][i]:.2f}\t"
                    details += f"{data['profit_margin'][i]:.2f}%\n"
                details += "\n"
                details += f"📈 Average Profit After Tax: ${data['average_pat']:.2f}\n"
                details += f"⭐ Best Month: {data['best_month']} (${max(data['profit_after_tax']):.2f})\n"
                details += f"⚠️ Worst Month: {data['worst_month']} (${min(data['profit_after_tax']):.2f})"
                self.detail_text.delete(1.0, tk.END)
                self.detail_text.insert(tk.END, details)
                self.update_salary_plot(employee)
        except Exception:
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(tk.END, "Error: Could not show details.")

    def update_salary_plot(self, employee):
        try:
            data = self.employee_data[employee]
            self.ax_salary.clear()
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            sns.set(style="darkgrid")
            self.ax_salary.plot(months, data['profit_after_tax'], color=self.secondary_color, marker='o', linestyle='-', label='Profit After Tax', linewidth=3)
            self.ax_salary.axhline(data['average_pat'], color=self.button_color, linestyle=':', linewidth=2, label=f'Avg Profit (${data["average_pat"]:.2f})')
            self.ax_salary.set_title(f"Profit After Tax ({employee})", color=self.button_color)
            self.ax_salary.set_xlabel("Month", color=self.text_color)
            self.ax_salary.set_ylabel("Profit After Tax ($)", color=self.text_color)
            self.ax_salary.legend(facecolor=self.panel_color, loc='upper left')
            self.ax_salary.set_facecolor(self.panel_color)
            for spine in self.ax_salary.spines.values():
                spine.set_color(self.secondary_color)
            self.ax_salary.tick_params(colors=self.text_color)
            self.ax_salary.title.set_color(self.button_color)
            self.ax_salary.xaxis.label.set_color(self.text_color)
            self.ax_salary.yaxis.label.set_color(self.text_color)
            self.fig_salary.tight_layout()
            self.canvas_salary.draw()
        except Exception:
            self.ax_salary.clear()
            self.ax_salary.set_title("Profit After Tax Graph (Error)", color=self.button_color)
            self.fig_salary.tight_layout()
            self.canvas_salary.draw()
    def setup_transfer_function_tab(self):
        main_frame = ttk.Frame(self.transfer_function_frame, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=32, pady=32)

        # SPLIT: Left side = formulas, details. Right side = filtered output graph.
        body_frame = ttk.Frame(main_frame, style='TFrame')
        body_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(body_frame, style='TFrame')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        input_frame = ttk.LabelFrame(left_frame, text="⚙️ Salary Transfer Function Parameters", padding=20, style='TFrame')
        input_frame.pack(fill=tk.X, pady=(0, 22))
        file_row = ttk.Frame(input_frame, style='TFrame')
        file_row.pack(fill=tk.X, pady=8)
        ttk.Label(file_row, text="📂 Salary Excel File:", style='TLabel').pack(side=tk.LEFT, padx=8)
        self.transfer_file_entry = ttk.Entry(file_row, width=44, style='TEntry')
        self.transfer_file_entry.pack(side=tk.LEFT, padx=8, expand=True, fill=tk.X)
        browse_btn = ttk.Button(file_row, text="Browse", command=self.browse_transfer_file)
        browse_btn.pack(side=tk.LEFT, padx=8)

        N_row = ttk.Frame(input_frame, style='TFrame')
        N_row.pack(fill=tk.X, pady=8)
        ttk.Label(N_row, text="🔢 Moving Average Window (N):", style='TLabel').pack(side=tk.LEFT, padx=8)
        self.transfer_N_entry = ttk.Entry(N_row, width=10, style='TEntry')
        self.transfer_N_entry.pack(side=tk.LEFT, padx=8)
        self.transfer_N_entry.insert(0, "10")

        sim_btn = ttk.Button(input_frame, text="🚀 Analyze Transfer Function", command=self.run_transfer_function_analysis, style='Accent.TButton')
        sim_btn.pack(pady=16)
        reset_btn = ttk.Button(input_frame, text="🔄 Reset", command=self.reset_transfer_tab, style='Accent.TButton')
        reset_btn.pack(side=tk.RIGHT, padx=8)

        stats_frame = ttk.LabelFrame(left_frame, text="📊 Transfer Function Details", padding=20, style='TFrame')
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=(16, 0))
        self.transfer_stats_text = scrolledtext.ScrolledText(stats_frame, height=16, wrap=tk.WORD, bg=self.panel_color, fg=self.text_color, insertbackground=self.text_color, font=self.normal_font, borderwidth=0)
        self.transfer_stats_text.pack(fill=tk.BOTH, expand=True)

        right_frame = ttk.Frame(body_frame, style='TFrame')
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        plot_label = ttk.Label(right_frame, text="📈 Filtered Salary Output (Moving Average)", font=self.header_font, background=self.panel_color, foreground=self.button_color)
        plot_label.pack(pady=10)
        self.fig_transfer, self.ax_transfer = plt.subplots(figsize=(12, 5))
        self.fig_transfer.patch.set_facecolor(self.panel_color)
        self.ax_transfer.set_facecolor(self.panel_color)
        for spine in self.ax_transfer.spines.values():
            spine.set_color(self.secondary_color)
        self.ax_transfer.tick_params(colors=self.text_color)
        self.ax_transfer.title.set_color(self.button_color)
        self.ax_transfer.xaxis.label.set_color(self.text_color)
        self.ax_transfer.yaxis.label.set_color(self.text_color)
        self.canvas_transfer = FigureCanvasTkAgg(self.fig_transfer, right_frame)
        self.canvas_transfer.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas_transfer, right_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
    def browse_transfer_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if filename:
            self.transfer_file_entry.delete(0, tk.END)
            self.transfer_file_entry.insert(0, filename)
            self.status_var.set(f"Selected file for transfer function: {filename}")
            try:
                df = pd.read_excel(filename)
                months = [m for m in df.columns if m in ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']]
                num_salaries = df.shape[0] * len(months)
                self.transfer_N_entry.delete(0, tk.END)
                self.transfer_N_entry.insert(0, str(num_salaries))
            except Exception:
                self.status_var.set("Could not auto-detect N from file")
    def reset_transfer_tab(self):
        self.transfer_file_entry.delete(0, tk.END)
        self.transfer_N_entry.delete(0, tk.END)
        self.transfer_N_entry.insert(0, "10")
        self.transfer_stats_text.delete(1.0, tk.END)
        self.ax_transfer.clear()
        self.ax_transfer.set_facecolor(self.panel_color)
        self.canvas_transfer.draw()
        self.status_var.set("Transfer Function tab reset to defaults")
    def run_transfer_function_analysis(self):
        filename = self.transfer_file_entry.get()
        try:
            N = int(self.transfer_N_entry.get())
            if not filename or not os.path.exists(filename):
                messagebox.showerror("Error", "Please select a valid Excel salary file")
                return
            df = pd.read_excel(filename)
            if "Employee" not in df.columns:
                messagebox.showerror("Error", "Excel file must contain an 'Employee' column")
                return
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            salaries = []
            for row in df.itertuples(index=False):
                salaries.extend([getattr(row, month) for month in months])
            salaries = np.array(salaries)
            self.transfer_salary_data = salaries

            # Print transfer function details to GUI (simulate print)
            output_lines = []
            import io
            import sys
            buf = io.StringIO()
            sys.stdout = buf
            tf_details = buf.getvalue()
            sys.stdout = sys.__stdout__
            output_lines.append(tf_details)

            b, a = moving_average_transfer_function(N)
            output_lines.append(f"\nFilter coefficients:\nb = {b}\na = {a}\n")

            buf = io.StringIO()
            sys.stdout = buf
            stable = check_stability(b, a)
            stability_details = buf.getvalue()
            sys.stdout = sys.__stdout__
            output_lines.append(stability_details)

            filtered_salaries = np.convolve(salaries, b, mode='valid')
            output_lines.append(f"\nFiltered salary sequence (first 10 shown): {filtered_salaries[:10]}\n")

            self.transfer_stats_text.delete(1.0, tk.END)
            self.transfer_stats_text.insert(tk.END, "\n".join(output_lines))

            # Show filtered salary output graph on right panel
            self.ax_transfer.clear()
            self.ax_transfer.plot(filtered_salaries, color=self.secondary_color, linewidth=2, label='Moving Average Salary')
            self.ax_transfer.set_title(f'Moving Average Salary Output (N={N})', color=self.button_color)
            self.ax_transfer.set_xlabel('Sample Index', color=self.text_color)
            self.ax_transfer.set_ylabel('Filtered Salary ($)', color=self.text_color)
            self.ax_transfer.legend(facecolor=self.panel_color)
            self.ax_transfer.set_facecolor(self.panel_color)
            for spine in self.ax_transfer.spines.values():
                spine.set_color(self.secondary_color)
            self.ax_transfer.tick_params(colors=self.text_color)
            self.ax_transfer.title.set_color(self.button_color)
            self.ax_transfer.xaxis.label.set_color(self.text_color)
            self.ax_transfer.yaxis.label.set_color(self.text_color)
            self.fig_transfer.tight_layout()
            self.canvas_transfer.draw()

            self.status_var.set("Transfer function analysis completed successfully")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error in transfer function analysis")
    def run_simulation(self):
        try:
            num_steps = int(self.steps_entry.get())
            uniform_low = float(self.uniform_low_entry.get())
            uniform_high = float(self.uniform_high_entry.get())
            normal_mean = float(self.normal_mean_entry.get())
            normal_std = float(self.normal_std_entry.get())
            speed = 11 - self.speed_slider.get()
            interval = max(30, min(300, int(5000 / num_steps * speed)))
            sample_sizes = np.logspace(1, 6, num=num_steps)
            uniform_expected_mean = (uniform_low + uniform_high) / 2
            normal_expected_mean = normal_mean
            bernoulli_props, normal_means = simulate_law_of_large_numbers(
                sample_sizes, uniform_low, uniform_high, normal_mean, normal_std)
            self.animate_lln_in_gui(sample_sizes, bernoulli_props, normal_means,
                uniform_expected_mean, normal_expected_mean, interval)
            self.status_var.set("LLN simulation completed successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Simulation error: {str(e)}")
            self.status_var.set("Error in simulation")

    def animate_lln_in_gui(self, sample_sizes, bernoulli_props, normal_means,
                          uniform_expected_mean, normal_expected_mean, interval):
        try:
            self.fig_lln.clf()
            self.axs_lln = self.fig_lln.subplots(1, 2)
            for ax in self.axs_lln:
                ax.set_facecolor(self.panel_color)
                for spine in ax.spines.values():
                    spine.set_color(self.secondary_color)
                ax.tick_params(colors=self.text_color)
                ax.title.set_color(self.button_color)
                ax.xaxis.label.set_color(self.text_color)
                ax.yaxis.label.set_color(self.text_color)
                ax.grid(True, alpha=0.35)
            self.axs_lln[0].set_xscale('log')
            self.axs_lln[1].set_xscale('log')
            self.axs_lln[0].set_title('Uniform Distribution Mean Convergence', color=self.button_color)
            self.axs_lln[0].set_xlabel('Sample Size (log scale)', color=self.text_color)
            self.axs_lln[0].set_ylabel('Sample Mean', color=self.text_color)
            self.axs_lln[0].axhline(uniform_expected_mean, color=self.button_color, linestyle='--', linewidth=2,
                                label=f'Expected ≈ {uniform_expected_mean:.2f}')
            self.axs_lln[0].legend(facecolor=self.panel_color)
            self.axs_lln[1].set_title('Normal Distribution Mean Convergence', color=self.button_color)
            self.axs_lln[1].set_xlabel('Sample Size (log scale)', color=self.text_color)
            self.axs_lln[1].set_ylabel('Sample Mean', color=self.text_color)
            self.axs_lln[1].axhline(normal_expected_mean, color=self.button_color, linestyle='--', linewidth=2,
                                label=f'Expected ≈ {normal_expected_mean:.2f}')
            self.axs_lln[1].legend(facecolor=self.panel_color)
            use_marker = len(sample_sizes) <= 1000
            uniform_line, = self.axs_lln[0].plot([], [], color=self.secondary_color, marker='o' if use_marker else '', linewidth=2)
            normal_line, = self.axs_lln[1].plot([], [], color=self.secondary_color, marker='o' if use_marker else '', linewidth=2)
            def update(frame):
                x = sample_sizes[:frame + 1]
                y1 = bernoulli_props[:frame + 1]
                y2 = normal_means[:frame + 1]
                self.axs_lln[0].set_xlim(1, sample_sizes[-1] * 1.1)
                self.axs_lln[1].set_xlim(1, sample_sizes[-1] * 1.1)
                y1_min, y1_max = min(y1), max(y1)
                y2_min, y2_max = min(y2), max(y2)
                self.axs_lln[0].set_ylim(y1_min - 0.05 * (y1_max - y1_min), y1_max + 0.05 * (y1_max - y1_min))
                self.axs_lln[1].set_ylim(y2_min - 0.05 * (y2_max - y2_min), y2_max + 0.05 * (y2_max - y2_min))
                uniform_line.set_data(x, y1)
                normal_line.set_data(x, y2)
                self.canvas_lln.draw()
                return uniform_line, normal_line
            self.animation = FuncAnimation(self.fig_lln, update, frames=len(sample_sizes), interval=interval, repeat=False)
            self.fig_lln.tight_layout()
            self.canvas_lln.draw()
        except Exception:
            self.fig_lln.clf()
            self.canvas_lln.draw()
    
# Do this (returning version):
    def print_transfer_function_zdomain_here(self,N):
        return print_transfer_function_zdomain(N)
    def print_transfer_function_Rdomain_here(self,N):
        return print_transfer_function_Rdomain(N)
    
    def run_salary_lln(self):
        filename = self.lln_salary_file_entry.get()
        try:
            if not filename or not os.path.exists(filename):
                messagebox.showerror("Error", "Please select a valid Excel salary file")
                return
                
            df = pd.read_excel(filename)
            if "Employee" not in df.columns:
                messagebox.showerror("Error", "Excel file must contain an 'Employee' column")
                return
                
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            salaries = []
            
            for row in df.itertuples(index=False):
                salaries.extend([getattr(row, month) for month in months])
                
            salaries = np.array(salaries)
            population_mean = np.mean(salaries)
            population_std = np.std(salaries)
            count = len(salaries)
            
            if count == 0:
                messagebox.showerror("Error", "No salary data found in the file")
                return
                
            self.lln_salary_stats_text.delete(1.0, tk.END)
            stats = f"Salary LLN Analysis\n"
            stats += f"Total Salary Samples: {count}\n"
            stats += f"Population Mean Salary: ${population_mean:,.2f}\n"
            stats += f"Population Std Dev: ${population_std:,.2f}\n"
            
            # Get transfer function strings
            z_domain = self.print_transfer_function_zdomain_here(count)
            real_domain = self.print_transfer_function_Rdomain_here(count)
            
            stats += f"\nTransfer function in z-domain:\n{z_domain}\n"
            stats += f"\nTransfer function in real domain:\n{real_domain}\n"
            
            # Add stability analysis
            try:
                N = 10  # Window size
                b, a = moving_average_transfer_function(N)
                stable = check_stability(b, a)
                stats += f"\nStability: {'STABLE' if stable else 'UNSTABLE'}\n"
                
                if stable:
                    stats += "Frequency response: Stable moving average filter\n"
            except Exception as e:
                stats += f"\nStability analysis error: {str(e)}\n"
            
            self.lln_salary_stats_text.insert(tk.END, stats)

            # Plot the LLN convergence
            sample_sizes = np.arange(1, count + 1)
            running_means = np.array([np.mean(salaries[:i]) for i in sample_sizes])
            self.ax_lln_salary.clear()
            self.ax_lln_salary.plot(sample_sizes, running_means, color=self.secondary_color, 
                                label="Sample Mean Salary", linewidth=2)
            self.ax_lln_salary.axhline(population_mean, color=self.button_color, 
                                    linestyle='--', linewidth=2, 
                                    label=f'Population Mean (${population_mean:,.2f})')
            self.ax_lln_salary.set_title('LLN: Salary Sample Mean Convergence', color=self.button_color)
            self.ax_lln_salary.set_xlabel('Sample Size (number of salary entries)', color=self.text_color)
            self.ax_lln_salary.set_ylabel('Mean Salary ($)', color=self.text_color)
            self.ax_lln_salary.grid(True, alpha=0.35)
            self.ax_lln_salary.legend(facecolor=self.panel_color)
            self.ax_lln_salary.set_facecolor(self.panel_color)
            
            for spine in self.ax_lln_salary.spines.values():
                spine.set_color(self.secondary_color)
                
            self.ax_lln_salary.tick_params(colors=self.text_color)
            self.ax_lln_salary.title.set_color(self.button_color)
            self.ax_lln_salary.xaxis.label.set_color(self.text_color)
            self.ax_lln_salary.yaxis.label.set_color(self.text_color)
            self.fig_lln_salary.tight_layout()
            self.canvas_lln_salary.draw()
            self.status_var.set("Salary LLN simulation completed successfully")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error in Salary LLN simulation")
    def setup_stability_comparator_tab(self):
        """Setup the Stability Comparator tab"""
        main_frame = ttk.Frame(self.stability_comparator_frame, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=32, pady=32)

        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="⚙️ Stability Comparator Parameters", padding=20, style='TFrame')
        input_frame.pack(fill=tk.X, pady=(0, 22))
        
        # File selection
        file_row = ttk.Frame(input_frame, style='TFrame')
        file_row.pack(fill=tk.X, pady=8)
        ttk.Label(file_row, text="📂 Select Excel Files:", style='TLabel').pack(side=tk.LEFT, padx=8)
        self.stability_files_var = tk.StringVar()
        self.stability_files_var.set("No files selected")
        files_label = ttk.Label(file_row, textvariable=self.stability_files_var, style='TLabel')
        files_label.pack(side=tk.LEFT, padx=8, expand=True, fill=tk.X)
        browse_btn = ttk.Button(file_row, text="Browse Files", command=self.browse_stability_files)
        browse_btn.pack(side=tk.LEFT, padx=8)
        
        # Parameters
        param_row = ttk.Frame(input_frame, style='TFrame')
        param_row.pack(fill=tk.X, pady=8)
        ttk.Label(param_row, text="🔢 Moving Average Window (N):", style='TLabel').pack(side=tk.LEFT, padx=8)
        self.stability_N_entry = ttk.Entry(param_row, width=10, style='TEntry')
        self.stability_N_entry.pack(side=tk.LEFT, padx=8)
        self.stability_N_entry.insert(0, "10")
        
        # Buttons
        btn_frame = ttk.Frame(input_frame, style='TFrame')
        btn_frame.pack(fill=tk.X, pady=16)
        compare_btn = ttk.Button(btn_frame, text="📊 Compare Stability", command=self.run_stability_comparison)
        compare_btn.pack(side=tk.LEFT, padx=8)
        reset_btn = ttk.Button(btn_frame, text="🔄 Reset", command=lambda: self.reset_tab("stability"))
        reset_btn.pack(side=tk.RIGHT, padx=8)
        
        # Results display - Treeview for file stability results
        results_frame = ttk.LabelFrame(main_frame, text="📈 Stability Results", padding=20, style='TFrame')
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(16, 0))
        
        # Create treeview with scrollbar
        tree_frame = ttk.Frame(results_frame, style='TFrame')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure columns
        columns = ("file", "stability_score", "stability_status")
        self.stability_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Define headings
        self.stability_tree.heading("file", text="📂 File Name")
        self.stability_tree.heading("stability_score", text="📊 Stability Score")
        self.stability_tree.heading("stability_status", text="✅ Stability Status")
        
        # Set column widths
        self.stability_tree.column("file", width=300, anchor=tk.W)
        self.stability_tree.column("stability_score", width=150, anchor=tk.CENTER)
        self.stability_tree.column("stability_status", width=150, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.stability_tree.yview)
        self.stability_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stability_tree.pack(fill=tk.BOTH, expand=True)
        
        # Plot for stability scores
        plot_frame = ttk.Frame(results_frame, style='TFrame')
        plot_frame.pack(fill=tk.BOTH, expand=True, pady=(16, 0))
        
        self.fig_stability = plt.figure(figsize=(12, 4), facecolor=self.panel_color)
        self.ax_stability = self.fig_stability.add_subplot(111)
        self.ax_stability.set_facecolor(self.panel_color)
        for spine in self.ax_stability.spines.values():
            spine.set_color(self.secondary_color)
        self.ax_stability.tick_params(colors=self.text_color)
        self.ax_stability.title.set_color(self.button_color)
        self.ax_stability.xaxis.label.set_color(self.text_color)
        self.ax_stability.yaxis.label.set_color(self.text_color)
        
        self.canvas_stability = FigureCanvasTkAgg(self.fig_stability, plot_frame)
        self.canvas_stability.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas_stability, plot_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    def browse_stability_files(self):
        filenames = filedialog.askopenfilenames(
            title="Select Salary Excel Files",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if filenames:
            self.stability_files = filenames
            count = len(filenames)
            self.stability_files_var.set(f"{count} file{'s' if count != 1 else ''} selected")
            self.status_var.set(f"Selected {count} files for stability comparison")

    def run_stability_comparison(self):
        if not hasattr(self, 'stability_files') or not self.stability_files:
            messagebox.showerror("Error", "Please select at least one Excel file")
            return
            
        try:
            N = int(self.stability_N_entry.get())
            if N <= 0:
                messagebox.showerror("Error", "Window size (N) must be a positive integer")
                return
                
            # Clear previous results
            for item in self.stability_tree.get_children():
                self.stability_tree.delete(item)
                
            # Run stability comparison
            self.stability_results = {}
            for file in self.stability_files:
                try:
                    df = pd.read_excel(file)
                    salaries = []
                    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    for col in months:
                        if col in df.columns:
                            salaries.extend(df[col].dropna().values)
                    
                    if not salaries:
                        stability_score = 0.0
                    else:
                        # Calculate stability metric (variance of moving average)
                        b = np.ones(N) / N
                        filtered = np.convolve(salaries, b, mode='valid')
                        stability_score = 1.0 - (np.std(filtered) / np.std(salaries))
                        stability_score = max(0, min(1, stability_score))
                    
                    self.stability_results[file] = {
                        'stability_score': stability_score,
                        'status': "Stable" if stability_score >= 0.7 else "Unstable"
                    }
                    
                    # Add to treeview
                    filename = os.path.basename(file)
                    self.stability_tree.insert("", tk.END, values=(
                        filename, 
                        f"{stability_score:.4f}", 
                        "Stable" if stability_score >= 0.7 else "Unstable"
                    ))
                    
                except Exception as e:
                    self.stability_results[file] = {
                        'stability_score': 0.0,
                        'status': f"Error: {str(e)}"
                    }
                    filename = os.path.basename(file)
                    self.stability_tree.insert("", tk.END, values=(
                        filename, 
                        "0.0000", 
                        f"Error: {str(e)}"
                    ))
            
            # Plot the stability scores
            self.plot_stability_results()
            
            self.status_var.set(f"Stability comparison completed for {len(self.stability_files)} files")
            
        except Exception as e:
            messagebox.showerror("Error", f"Stability comparison failed: {str(e)}")
            self.status_var.set("Error in stability comparison")

    def plot_stability_results(self):
        if not hasattr(self, 'stability_results') or not self.stability_results:
            return
            
        self.ax_stability.clear()
        
        # Prepare data for plotting
        filenames = [os.path.basename(f) for f in self.stability_results.keys()]
        scores = [data['stability_score'] for data in self.stability_results.values()]
        colors = [self.secondary_color if score >= 0.7 else self.highlight_color for score in scores]
        
        # Create bar plot
        x = np.arange(len(filenames))
        bars = self.ax_stability.bar(x, scores, color=colors, edgecolor=self.button_color, linewidth=1.5)
        
        # Add threshold line
        self.ax_stability.axhline(y=0.7, color=self.button_color, linestyle='--', linewidth=2, label='Stability Threshold (0.7)')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            self.ax_stability.text(bar.get_x() + bar.get_width()/2., height,
                                f'{height:.2f}', 
                                ha='center', va='bottom',
                                color=self.text_color, fontsize=9)
        
        # Configure plot
        self.ax_stability.set_title('Salary Data Stability Scores', color=self.button_color, fontsize=14)
        self.ax_stability.set_xlabel('Excel Files', color=self.text_color)
        self.ax_stability.set_ylabel('Stability Score', color=self.text_color)
        self.ax_stability.set_xticks(x)
        self.ax_stability.set_xticklabels(filenames, rotation=45, ha='right', fontsize=9, color=self.text_color)
        self.ax_stability.set_ylim(0, 1.05)
        self.ax_stability.legend(facecolor=self.panel_color, loc='upper right')
        self.ax_stability.grid(True, alpha=0.2, linestyle='--')
        
        # Set plot background
        self.ax_stability.set_facecolor(self.panel_color)
        self.fig_stability.tight_layout()
        self.canvas_stability.draw()
        
    # Add this method to fix the stability comparator tab functionality
    def run_stability_comparison(self):
        if not hasattr(self, 'stability_files') or not self.stability_files:
            messagebox.showerror("Error", "Please select at least one Excel file")
            return
            
        try:
            N = int(self.stability_N_entry.get())
            if N <= 0:
                messagebox.showerror("Error", "Window size (N) must be a positive integer")
                return
                
            # Clear previous results
            for item in self.stability_tree.get_children():
                self.stability_tree.delete(item)
                
            # Run stability comparison
            self.stability_results = {}
            for file in self.stability_files:
                try:
                    df = pd.read_excel(file)
                    salaries = []
                    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    for col in months:
                        if col in df.columns:
                            salaries.extend(df[col].dropna().values)
                    
                    if not salaries:
                        stability_score = 0.0
                    else:
                        # Calculate stability metric (variance of moving average)
                        b = np.ones(N) / N
                        filtered = np.convolve(salaries, b, mode='valid')
                        stability_score = 1.0 - (np.std(filtered) / np.std(salaries))
                        stability_score = max(0, min(1, stability_score))
                    
                    self.stability_results[file] = {
                        'stability_score': stability_score,
                        'status': "Stable" if stability_score >= 0.7 else "Unstable"
                    }
                    
                    # Add to treeview
                    filename = os.path.basename(file)
                    self.stability_tree.insert("", tk.END, values=(
                        filename, 
                        f"{stability_score:.4f}", 
                        "Stable" if stability_score >= 0.7 else "Unstable"
                    ))
                    
                except Exception as e:
                    self.stability_results[file] = {
                        'stability_score': 0.0,
                        'status': f"Error: {str(e)}"
                    }
                    filename = os.path.basename(file)
                    self.stability_tree.insert("", tk.END, values=(
                        filename, 
                        "0.0000", 
                        f"Error: {str(e)}"
                    ))
            
            # Plot the stability scores
            self.plot_stability_results()
    
            self.status_var.set(f"Stability comparison completed for {len(self.stability_files)} files")
        except Exception as e:
            messagebox.showerror("Error", f"Stability comparison failed: {str(e)}")
        self.status_var.set("Error in stability comparison")
    def setup_transfer_comparator_tab(self):
        """Setup the Transfer Function Comparator tab"""
        main_frame = ttk.Frame(self.transfer_comparator_frame, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=32, pady=32)

        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="⚙️ Transfer Function Comparator Parameters", 
                                    padding=20, style='TFrame')
        input_frame.pack(fill=tk.X, pady=(0, 22))
        
        # File selection
        file_row = ttk.Frame(input_frame, style='TFrame')
        file_row.pack(fill=tk.X, pady=8)
        ttk.Label(file_row, text="📂 Select Excel Files:", style='TLabel').pack(side=tk.LEFT, padx=8)
        self.transfer_comp_files_var = tk.StringVar()
        self.transfer_comp_files_var.set("No files selected")
        files_label = ttk.Label(file_row, textvariable=self.transfer_comp_files_var, style='TLabel')
        files_label.pack(side=tk.LEFT, padx=8, expand=True, fill=tk.X)
        browse_btn = ttk.Button(file_row, text="Browse Files", command=self.browse_transfer_comp_files)
        browse_btn.pack(side=tk.LEFT, padx=8)
        
        # Parameters
        param_row = ttk.Frame(input_frame, style='TFrame')
        param_row.pack(fill=tk.X, pady=8)
        ttk.Label(param_row, text="🔢 Moving Average Window (N):", style='TLabel').pack(side=tk.LEFT, padx=8)
        self.transfer_comp_N_entry = ttk.Entry(param_row, width=10, style='TEntry')
        self.transfer_comp_N_entry.pack(side=tk.LEFT, padx=8)
        self.transfer_comp_N_entry.insert(0, "10")
        
        # Buttons
        btn_frame = ttk.Frame(input_frame, style='TFrame')
        btn_frame.pack(fill=tk.X, pady=16)
        compare_btn = ttk.Button(btn_frame, text="📶 Compare Transfer Functions", 
                                command=self.run_transfer_comparison)
        compare_btn.pack(side=tk.LEFT, padx=8)
        reset_btn = ttk.Button(btn_frame, text="🔄 Reset", 
                              command=lambda: self.reset_tab("transfer_comparator"))
        reset_btn.pack(side=tk.RIGHT, padx=8)
        
        # Results display
        results_frame = ttk.LabelFrame(main_frame, text="📈 Transfer Function Comparison", 
                                     padding=20, style='TFrame')
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(16, 0))
        
        # Plot for transfer function outputs
        self.fig_transfer_comp = plt.figure(figsize=(12, 6), facecolor=self.panel_color)
        self.ax_transfer_comp = self.fig_transfer_comp.add_subplot(111)
        self.ax_transfer_comp.set_facecolor(self.panel_color)
        for spine in self.ax_transfer_comp.spines.values():
            spine.set_color(self.secondary_color)
        self.ax_transfer_comp.tick_params(colors=self.text_color)
        self.ax_transfer_comp.title.set_color(self.button_color)
        self.ax_transfer_comp.xaxis.label.set_color(self.text_color)
        self.ax_transfer_comp.yaxis.label.set_color(self.text_color)
        
        self.canvas_transfer_comp = FigureCanvasTkAgg(self.fig_transfer_comp, results_frame)
        self.canvas_transfer_comp.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas_transfer_comp, results_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Stability metrics display
        metrics_frame = ttk.Frame(results_frame, style='TFrame')
        metrics_frame.pack(fill=tk.X, pady=(10, 0))
        self.transfer_comp_metrics_text = scrolledtext.ScrolledText(metrics_frame, height=6, 
                                                                  wrap=tk.WORD, bg=self.panel_color, 
                                                                  fg=self.text_color, 
                                                                  insertbackground=self.text_color, 
                                                                  font=self.normal_font, 
                                                                  borderwidth=0)
        self.transfer_comp_metrics_text.pack(fill=tk.X, expand=True)

    def browse_transfer_comp_files(self):
        filenames = filedialog.askopenfilenames(
            title="Select Salary Excel Files",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if filenames:
            self.transfer_comp_files = filenames
            count = len(filenames)
            self.transfer_comp_files_var.set(f"{count} file{'s' if count != 1 else ''} selected")
            self.status_var.set(f"Selected {count} files for transfer function comparison")

    def run_transfer_comparison(self):
        if not hasattr(self, 'transfer_comp_files') or not self.transfer_comp_files:
            messagebox.showerror("Error", "Please select at least one Excel file")
            return
            
        try:
            N = int(self.transfer_comp_N_entry.get())
            if N <= 0:
                messagebox.showerror("Error", "Window size (N) must be a positive integer")
                return
                
            # Clear previous results
            self.ax_transfer_comp.clear()
            self.transfer_comp_metrics_text.delete(1.0, tk.END)
            
            # Prepare metrics report
            metrics_report = "Transfer Function Stability Metrics:\n"
            metrics_report += "=" * 50 + "\n"
            metrics_report += "File\t\t\tStability Score\t\tStatus\n"
            metrics_report += "-" * 50 + "\n"
            
            # Process each file - FIXED: Ensure we process ALL files
            stability_scores = {}
            colors = plt.cm.tab20(np.linspace(0, 1, len(self.transfer_comp_files)))
            
            for i, file in enumerate(self.transfer_comp_files):
                try:
                    # FIXED: More robust data extraction
                    df = pd.read_excel(file)
                    salaries = []
                    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    
                    # FIXED: Handle different column name formats
                    available_months = [col for col in df.columns if any(month.lower() in col.lower() for month in months)]
                    
                    if not available_months:
                        raise ValueError("No valid month columns found")
                    
                    for col in available_months:
                        salaries.extend(pd.to_numeric(df[col], errors='coerce').dropna().values)
                    
                    if len(salaries) < N:
                        raise ValueError(f"Not enough data points (need at least {N}, got {len(salaries)})")
                    
                    # Apply moving average filter
                    b = np.ones(N) / N
                    filtered = np.convolve(salaries, b, mode='valid')
                    
                    # Calculate stability metric
                    stability_score = 1.0 - (np.std(filtered) / np.std(salaries))
                    stability_score = max(0, min(1, stability_score))
                    status = "Stable" if stability_score >= 0.7 else "Unstable"
                    
                    # Plot the filtered output - FIXED: Ensure all plots are visible
                    filename = os.path.basename(file)
                    line, = self.ax_transfer_comp.plot(filtered, 
                                                    color=colors[i], 
                                                    linewidth=1.5,
                                                    alpha=0.8,  # Slightly transparent
                                                    label=f"{filename[:15]}... ({stability_score:.2f})")
                    
                    # Store stability score for sorting
                    stability_scores[file] = stability_score
                    
                    # Add to metrics report
                    filename_short = os.path.basename(file)[:20] + ("..." if len(os.path.basename(file)) > 20 else "")
                    metrics_report += f"{filename_short}\t{stability_score:.4f}\t\t{status}\n"
                    
                except Exception as e:
                    filename_short = os.path.basename(file)[:20] + ("..." if len(os.path.basename(file)) > 20 else "")
                    stability_scores[file] = 0.0
                    metrics_report += f"{filename_short}\tError: {str(e)}\n"
                    continue
            
            # Sort files by stability score (most stable first)
            sorted_files = sorted(stability_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Add sorted results to report
            metrics_report += "\nRanked by Stability:\n"
            metrics_report += "-" * 50 + "\n"
            for rank, (file, score) in enumerate(sorted_files, 1):
                filename_short = os.path.basename(file)[:20] + ("..." if len(os.path.basename(file)) > 20 else "")
                metrics_report += f"#{rank}: {filename_short} - Score: {score:.4f}\n"
            
            # Update metrics display
            self.transfer_comp_metrics_text.delete(1.0, tk.END)
            self.transfer_comp_metrics_text.insert(tk.END, metrics_report)
            
            # Configure plot - FIXED: Better plot formatting
            self.ax_transfer_comp.set_title(f'Filtered Salary Output Comparison (N={N})', 
                                        color=self.button_color, 
                                        fontsize=14)
            self.ax_transfer_comp.set_xlabel('Sample Index', color=self.text_color)
            self.ax_transfer_comp.set_ylabel('Filtered Salary ($)', color=self.text_color)
            
            # FIXED: Better legend placement and formatting
            legend = self.ax_transfer_comp.legend(
                facecolor=self.panel_color, 
                loc='upper right',
                bbox_to_anchor=(1.3, 1),
                fontsize=9
            )
            
            for text in legend.get_texts():
                text.set_color(self.text_color)
                
            self.ax_transfer_comp.grid(True, alpha=0.2, linestyle='--')
            
            # Set plot background
            self.ax_transfer_comp.set_facecolor(self.panel_color)
            self.fig_transfer_comp.tight_layout()
            
            # FIXED: Adjust figure size to accommodate legend
            self.fig_transfer_comp.set_size_inches(14, 6)
            self.canvas_transfer_comp.draw()
            
            self.status_var.set(f"Transfer function comparison completed for {len(self.transfer_comp_files)} files")          
        except Exception as e:
            messagebox.showerror("Error", f"Comparison failed: {str(e)}")
            self.status_var.set("Error in transfer function comparison")

    
if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap(default='finance_icon.ico')
    except:
        pass
    app = LuxeFinancialApp(root)
    root.eval('tk::PlaceWindow . center')
    root.mainloop()

