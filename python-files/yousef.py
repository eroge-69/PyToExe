import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import math

# --- Tab 1: Variance & Std Dev ---
def calculate_variance_std():
    try:
        classes_text = class_entry.get()
        freq_text = freq_entry.get()

        classes = [c.strip() for c in classes_text.split(',')]
        freq = [float(f.strip()) for f in freq_text.split(',')]

        if len(classes) != len(freq):
            messagebox.showerror("Error", "Number of classes must equal number of frequencies.")
            return

        lower_bounds = []
        upper_bounds = []
        for cl in classes:
            parts = cl.split('-')
            if len(parts) != 2:
                messagebox.showerror("Error", f"Invalid class format: {cl}")
                return
            lower_bounds.append(float(parts[0]))
            upper_bounds.append(float(parts[1]))

        midpoints = [(l + u) / 2 for l, u in zip(lower_bounds, upper_bounds)]

        df = pd.DataFrame({
            'W (Kg)': classes,
            'f': freq,
            'x': midpoints
        })

        df['fx'] = df['f'] * df['x']
        mean_val = df['fx'].sum() / df['f'].sum()
        df['|x−x̄|'] = abs(df['x'] - mean_val)
        df['f|x−x̄|'] = df['f'] * df['|x−x̄|']
        df['f(x−x̄)²'] = df['f'] * (df['x'] - mean_val)**2

        for i in tree.get_children():
            tree.delete(i)

        for i, row in df.iterrows():
            tag = 'even' if i % 2 == 0 else 'odd'
            
            # Format values without .0 for integers
            f_val = int(row['f']) if row['f'] == int(row['f']) else row['f']
            x_val = int(row['x']) if row['x'] == int(row['x']) else round(row['x'], 2)
            fx_val = int(row['fx']) if row['fx'] == int(row['fx']) else round(row['fx'], 2)
            abs_val = int(row['|x−x̄|']) if row['|x−x̄|'] == int(row['|x−x̄|']) else round(row['|x−x̄|'], 2)
            fabs_val = int(row['f|x−x̄|']) if row['f|x−x̄|'] == int(row['f|x−x̄|']) else round(row['f|x−x̄|'], 2)
            fsq_val = int(row['f(x−x̄)²']) if row['f(x−x̄)²'] == int(row['f(x−x̄)²']) else round(row['f(x−x̄)²'], 3)
            
            tree.insert('', tk.END, values=(
                row['W (Kg)'],
                f_val,
                x_val,
                fx_val,
                abs_val,
                fabs_val,
                fsq_val
            ), tags=(tag,))

        total_f = df['f'].sum()
        total_fx = df['fx'].sum()
        total_fabs = df['f|x−x̄|'].sum()
        total_fsq = df['f(x−x̄)²'].sum()

        # Format totals without .0 for integers
        total_f_formatted = int(total_f) if total_f == int(total_f) else total_f
        total_fx_formatted = int(total_fx) if total_fx == int(total_fx) else round(total_fx, 2)
        total_fabs_formatted = int(total_fabs) if total_fabs == int(total_fabs) else round(total_fabs, 2)
        total_fsq_formatted = int(total_fsq) if total_fsq == int(total_fsq) else round(total_fsq, 3)

        tree.insert('', tk.END, values=(
            'Total', 
            total_f_formatted, 
            '', 
            total_fx_formatted,
            '', 
            total_fabs_formatted, 
            total_fsq_formatted
        ), tags=('total',))

        variance = total_fsq / total_f
        std_dev = math.sqrt(variance)

        # Format results without .0 for integers
        mean_val_formatted = int(mean_val) if mean_val == int(mean_val) else round(mean_val, 4)
        variance_formatted = int(variance) if variance == int(variance) else round(variance, 4)
        std_dev_formatted = int(std_dev) if std_dev == int(std_dev) else round(std_dev, 4)

        # Create centered formulas
        mean_formula = "          Σfx\n"
        mean_formula += "Mean (x̄) = ───\n"
        mean_formula += "           Σf"
        
        mean_calc = f"    {total_fx_formatted}\n"
        mean_calc += "  = ─────\n"
        mean_calc += f"    {total_f_formatted}"
        
        mean_result = f"  = {mean_val_formatted}"
        
        # Variance formula
        variance_formula = "          Σf(x−x̄)²\n"
        variance_formula += "Variance = ────────\n"
        variance_formula += "            Σf"
        
        variance_calc = f"    {total_fsq_formatted}\n"
        variance_calc += "  = ─────\n"
        variance_calc += f"    {total_f_formatted}"
        
        variance_result = f"  = {variance_formatted}"
        
        # Standard deviation
        std_dev_result = f"Std Dev = √Variance = √{variance_formatted} = {std_dev_formatted}"

        result_label.config(
            text=f"{mean_formula}\n\n{mean_calc}\n\n{mean_result}",
            font=('Courier New', 12)
        )

        steps_label.config(
            text=f"{variance_formula}\n\n{variance_calc}\n\n{variance_result}\n\n{std_dev_result}",
            font=('Courier New', 12)
        )

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# --- Tab 2: Mean / Median / Mode ---
def calculate_mean():
    try:
        numbers = [float(n.strip()) for n in numbers_entry.get().split(',')]
        n = len(numbers)
        sum_numbers = sum(numbers)
        mean_val = sum_numbers / n
        
        # Format numbers without .0 for integers
        formatted_numbers = []
        for num in numbers:
            if num == int(num):
                formatted_numbers.append(str(int(num)))
            else:
                formatted_numbers.append(str(num))
        
        numbers_str = " + ".join(formatted_numbers)
        
        # Format results without .0 for integers
        sum_formatted = int(sum_numbers) if sum_numbers == int(sum_numbers) else sum_numbers
        mean_formatted = int(mean_val) if mean_val == int(mean_val) else round(mean_val, 4)
        
        # Create perfectly centered display
        result_text = "          Σx\n"
        result_text += "Mean = ─────\n"
        result_text += "           n\n\n"
        
        result_text += f"({numbers_str})\n"
        result_text += "────────────\n"
        result_text += f"     {n}\n\n"
        
        result_text += f"  {sum_formatted}\n"
        result_text += "= ─────\n"
        result_text += f"    {n}\n\n"
        result_text += f"= {mean_formatted}"

        result_tab2.config(text=result_text, font=('Courier New', 14))

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def calculate_median():
    try:
        numbers = sorted([float(n.strip()) for n in numbers_entry.get().split(',')])
        n = len(numbers)
        
        # Format numbers without .0 for integers
        formatted_numbers = []
        for num in numbers:
            if num == int(num):
                formatted_numbers.append(int(num))
            else:
                formatted_numbers.append(num)
        
        if n % 2 == 1:
            median_val = formatted_numbers[n // 2]
            median_formatted = int(median_val) if median_val == int(median_val) else median_val
            
            result_text = f"Sorted numbers: {formatted_numbers}\n\n"
            result_text += f"Median = Middle value (position {n//2 + 1})\n\n"
            result_text += f"= {median_formatted}"
            
            result_tab2.config(text=result_text, font=('Courier New', 14))
        else:
            num1 = formatted_numbers[n//2 - 1]
            num2 = formatted_numbers[n//2]
            sum_val = num1 + num2
            median_val = sum_val / 2
            
            # Format numbers without .0 for integers
            num1_formatted = int(num1) if num1 == int(num1) else num1
            num2_formatted = int(num2) if num2 == int(num2) else num2
            sum_formatted = int(sum_val) if sum_val == int(sum_val) else sum_val
            median_formatted = int(median_val) if median_val == int(median_val) else median_val
            
            # Create perfectly centered display
            result_text = f"Sorted numbers: {formatted_numbers}\n\n"
            result_text += f"          {num1_formatted} + {num2_formatted}\n"
            result_text += f"Median = ─────────────────\n"
            result_text += f"                2\n\n"
            
            result_text += f"    {sum_formatted}\n"
            result_text += f"  = ─────\n"
            result_text += f"      2\n\n"
            result_text += f"  = {median_formatted}"

            result_tab2.config(text=result_text, font=('Courier New', 14))
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def calculate_mode():
    try:
        numbers = [float(n.strip()) for n in numbers_entry.get().split(',')]
        
        # Format numbers without .0 for integers
        formatted_numbers = []
        for num in numbers:
            if num == int(num):
                formatted_numbers.append(int(num))
            else:
                formatted_numbers.append(num)
        
        freq = {}
        for num in formatted_numbers:
            freq[num] = freq.get(num,0) + 1
        
        max_count = max(freq.values())
        modes = [k for k,v in freq.items() if v == max_count]
        
        frequency_text = "Frequencies:\n"
        for num, count in sorted(freq.items()):
            num_formatted = int(num) if num == int(num) else num
            frequency_text += f"  {num_formatted}: {count} time{'s' if count > 1 else ''}\n"
        
        if len(modes) == len(freq):
            result_tab2.config(
                text=f"{frequency_text}\n\nMode = No unique mode (all values appear equally)", 
                font=('Courier New', 14)
            )
        else:
            modes_formatted = [int(mode) if mode == int(mode) else mode for mode in modes]
            mode_str = ", ".join(map(str, modes_formatted))
            result_tab2.config(
                text=f"{frequency_text}\n\nMode = Most frequent value(s) = {mode_str}\n(appears {max_count} times)", 
                font=('Courier New', 14)
            )
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# --- Tab 3: All Formulas ---
def show_formulas():
    formulas_text = """    📊 STATISTICS FORMULAS 📊

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    📈 MEASURES OF CENTRAL TENDENCY:

    Mean (Arithmetic):
          Σx
    x̄ = ─────
           n

    Mean (Grouped Data):
          Σfx
    x̄ = ─────
          Σf

    Median (Ungrouped):
    If n is odd: Middle value
    If n is even: 
          (n/2)th + (n/2 + 1)th
    Med = ────────────────────
                   2

    Mode:
    Most frequent value(s)

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    📊 MEASURES OF DISPERSION:

    Variance (Population):
          Σ(x - x̄)²
    σ² = ──────────
              n

    Variance (Sample):
          Σ(x - x̄)²
    s² = ──────────
            n - 1

    Variance (Grouped Data):
          Σf(x - x̄)²
    σ² = ───────────
             Σf

    Standard Deviation:
    σ = √Variance

    Mean Absolute Deviation:
          Σ|x - x̄|
    MAD = ────────
             n

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    📐 OTHER IMPORTANT FORMULAS:

    Range:
    Range = Max - Min

    Coefficient of Variation:
          σ
    CV = ─── × 100%
          x̄

    Z-score:
          x - x̄
    z = ─────
           σ

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    📋 NOTATION:
    x̄ = Mean
    σ = Population Standard Deviation
    s = Sample Standard Deviation
    σ² = Population Variance
    s² = Sample Variance
    n = Number of observations
    f = Frequency
    Σ = Summation
    """
    
    # Clear and insert new text
    formulas_tab3.delete(1.0, tk.END)
    formulas_tab3.insert(1.0, formulas_text)

# --- GUI ---
root = tk.Tk()
root.title("Statistics Calculator")
root.geometry("1200x700")
root.configure(bg='#2C2F33')

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# --- Tab 1 ---
tab1 = tk.Frame(notebook, bg='#2C2F33')
notebook.add(tab1, text="Variance & Std Dev")

tk.Label(tab1, text="Enter Classes (e.g., 54-57,58-61,...):", bg='#2C2F33', fg='white', font=('Helvetica', 12)).pack(pady=2)
class_entry = tk.Entry(tab1, width=80)
class_entry.pack(pady=2)

tk.Label(tab1, text="Enter Frequencies (comma separated):", bg='#2C2F33', fg='white', font=('Helvetica', 12)).pack(pady=2)
freq_entry = tk.Entry(tab1, width=80)
freq_entry.pack(pady=2)

tk.Button(tab1, text="Calculate", command=calculate_variance_std, bg='#43B581', fg='white', font=('Helvetica', 12, 'bold')).pack(pady=8)

result_frame = tk.Frame(tab1, bg='#2C2F33')
result_frame.pack(fill=tk.X, pady=5)

# Create two columns for results
left_frame = tk.Frame(result_frame, bg='#2C2F33')
left_frame.pack(side=tk.LEFT, padx=20, expand=True)
right_frame = tk.Frame(result_frame, bg='#2C2F33')
right_frame.pack(side=tk.RIGHT, padx=20, expand=True)

result_label = tk.Label(left_frame, text="", bg='#2C2F33', fg='white', font=('Courier New', 12), justify='center')
result_label.pack(pady=2)
steps_label = tk.Label(right_frame, text="", bg='#2C2F33', fg='white', font=('Courier New', 12), justify='center')
steps_label.pack(pady=2)

columns = ('W (Kg)', 'f', 'x', 'fx', '|x−x̄|', 'f|x−x̄|', 'f(x−x̄)²')
tree = ttk.Treeview(tab1, columns=columns, show='headings', height=12)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=140, anchor='center')
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

style = ttk.Style()
style.theme_use('clam')
style.configure("Treeview",
                background="#1C1F26",
                foreground="white",
                fieldbackground="#1C1F26",
                rowheight=35,
                font=('Helvetica', 11))
style.map('Treeview', background=[('selected', '#7289DA')])
tree.tag_configure('even', background='#2C2F26')
tree.tag_configure('odd', background='#1C1F33')
tree.tag_configure('total', background='#3E4C59', font=('Helvetica', 11, 'bold'))

# --- Tab 2 ---
tab2 = tk.Frame(notebook, bg='#2C2F33')
notebook.add(tab2, text="Mean / Median / Mode")

tk.Label(tab2, text="Enter numbers (comma separated):", bg='#2C2F33', fg='white', font=('Helvetica', 12)).pack(pady=10)
numbers_entry = tk.Entry(tab2, width=50)
numbers_entry.pack(pady=5)

btn_frame = tk.Frame(tab2, bg='#2C2F33')
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Calculate Mean", command=calculate_mean, bg='#43B581', fg='white', font=('Helvetica', 12, 'bold')).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Calculate Median", command=calculate_median, bg='#7289DA', fg='white', font=('Helvetica', 12, 'bold')).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Calculate Mode", command=calculate_mode, bg='#FAA61A', fg='white', font=('Helvetica', 12, 'bold')).grid(row=0, column=2, padx=5)

# Create a centered frame for results in tab2
result_frame_tab2 = tk.Frame(tab2, bg='#2C2F33')
result_frame_tab2.pack(pady=20, fill=tk.BOTH, expand=True)

result_tab2 = tk.Label(result_frame_tab2, text="", bg='#2C2F33', fg='white', font=('Courier New', 14), justify='center')
result_tab2.pack(expand=True)

# --- Tab 3: All Formulas ---
tab3 = tk.Frame(notebook, bg='#2C2F33')
notebook.add(tab3, text="All Formulas")

# Create a scrollable frame for formulas
formulas_frame = tk.Frame(tab3, bg='#2C2F33')
formulas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Add scrollbar
scrollbar = tk.Scrollbar(formulas_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create text widget for formulas
formulas_tab3 = tk.Text(formulas_frame, bg='#2C2F33', fg='white', font=('Courier New', 11), 
                       yscrollcommand=scrollbar.set, wrap=tk.WORD, padx=10, pady=10)
formulas_tab3.pack(fill=tk.BOTH, expand=True)

scrollbar.config(command=formulas_tab3.yview)

# Show formulas when tab3 is selected
def on_tab3_selected(event):
    if notebook.index("current") == 2:  # Tab3 index
        show_formulas()

notebook.bind("<<NotebookTabChanged>>", on_tab3_selected)

# Show formulas initially
show_formulas()

root.mainloop()