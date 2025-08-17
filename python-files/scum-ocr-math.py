import math
from itertools import combinations
from typing import List, Tuple, Callable, Dict
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import re

# Constants
MAX_FUNCTIONS = 8
MAX_COMBINATIONS = 255
TOLERANCE = 0.5
TOTAL_FUNCTIONS = 16

class FunctionConfig:
    def __init__(self, operator='+', value=0, active=False, name=""):
        self.operator = operator
        self.value = value
        self.active = active
        self.name = name

# Initialize configurations
configs = [
    FunctionConfig(name="A"), FunctionConfig(name="B"), 
    FunctionConfig(name="C"), FunctionConfig(name="D"),
    FunctionConfig(name="E"), FunctionConfig(name="F"), 
    FunctionConfig(name="G"), FunctionConfig(name="H"),
    FunctionConfig(name="AA"), FunctionConfig(name="BB"), 
    FunctionConfig(name="CC"), FunctionConfig(name="DD"),
    FunctionConfig(name="EE"), FunctionConfig(name="FF"), 
    FunctionConfig(name="GG"), FunctionConfig(name="HH")
]

def generic_function(z: float, config: FunctionConfig) -> float:
    if not config.active:
        return z
    try:
        if config.operator == '+':
            return z + config.value
        elif config.operator == '-':
            return z - config.value
        elif config.operator == '*':
            return z * config.value
        elif config.operator == '/':
            return z / config.value if config.value != 0 else z
        return z
    except Exception as e:
        print(f"Error in {config.name}: {e}")
        return z

# Define all functions
def A(z): return generic_function(z, configs[0])
def B(z): return generic_function(z, configs[1])
def C(z): return generic_function(z, configs[2])
def D(z): return generic_function(z, configs[3])
def E(z): return generic_function(z, configs[4])
def F(z): return generic_function(z, configs[5])
def G(z): return generic_function(z, configs[6])
def H(z): return generic_function(z, configs[7])
def AA(z): return generic_function(z, configs[8])
def BB(z): return generic_function(z, configs[9])
def CC(z): return generic_function(z, configs[10])
def DD(z): return generic_function(z, configs[11])
def EE(z): return generic_function(z, configs[12])
def FF(z): return generic_function(z, configs[13])
def GG(z): return generic_function(z, configs[14])
def HH(z): return generic_function(z, configs[15])

functions1 = [A, B, C, D, E, F, G, H]
functions2 = [AA, BB, CC, DD, EE, FF, GG, HH]

class Combination:
    def __init__(self):
        self.indices = []
        self.count = 0
        self.name = ""

def generate_combinations() -> List[Combination]:
    combo_list = []
    for size in range(1, MAX_FUNCTIONS + 1):
        for indices in combinations(range(MAX_FUNCTIONS), size):
            combo = Combination()
            combo.indices = list(indices)
            combo.count = size
            combo.name = "".join(str(i + 1) for i in indices)
            combo_list.append(combo)
    return combo_list

def apply_combination(input_val: float, combo: Combination, func_set: List[Callable]) -> float:
    result = input_val
    for index in combo.indices:
        result = func_set[index](result)
    return result

def values_match(val1: float, val2: float) -> bool:
    return abs(val1 - val2) <= TOLERANCE

def test_combinations(input_val: float, target: float, combo_list: List[Combination], 
                     func_set: List[Callable], results_text: tk.Text = None) -> List[int]:
    matches = []
    for i, combo in enumerate(combo_list):
        result = apply_combination(input_val, combo, func_set)
        if values_match(result, target):
            matches.append(i)
            if results_text:
                results_text.insert(tk.END, f"{i} ")
                results_text.see(tk.END)
    return matches

def find_common_matches(matches1: List[int], matches2: List[int], 
                       combo_list: List[Combination], results_text: tk.Text = None) -> None:
    if results_text:
        results_text.insert(tk.END, "\n\nCommon Matches:\n")
    
    any_match = False
    for m1 in matches1:
        if m1 in matches2:
            if results_text:
                results_text.insert(tk.END, f"\nMatch at J={m1 + 1}:\n")
            
            included = [0] * MAX_FUNCTIONS
            for idx in combo_list[m1].indices:
                included[idx] = 1
            
            for num in range(MAX_FUNCTIONS):
                line = f"{num + 1} [{'✓' if included[num] else ' '}]\n"
                if results_text:
                    results_text.insert(tk.END, line)
            
            any_match = True
    
    if not any_match and results_text:
        results_text.insert(tk.END, "No common matches found.\n")

class TerminalStyleConfig:
    def __init__(self, root):
        self.root = root
        self.root.title("SCUM Math Solver")
        self.root.geometry("900x750")
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Consolas', 10))
        self.style.configure('TButton', font=('Consolas', 10))
        self.style.configure('TEntry', font=('Consolas', 10))
        
        self.create_widgets()
        self.setup_key_bindings()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.root.quit()
        self.root.destroy()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Input Parameters")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Input value
        ttk.Label(input_frame, text="Input Value:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.input_val = ttk.Entry(input_frame, width=15)
        self.input_val.grid(row=0, column=1, padx=5, pady=5)
        
        # Target values
        ttk.Label(input_frame, text="Target A:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.target1 = ttk.Entry(input_frame, width=15)
        self.target1.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Target B:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.target2 = ttk.Entry(input_frame, width=15)
        self.target2.grid(row=2, column=1, padx=5, pady=5)
        
        # Function configuration
        config_frame = ttk.LabelFrame(main_frame, text="Function Configuration")
        config_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left_frame = ttk.Frame(config_frame)
        left_frame.grid(row=0, column=0, padx=10, pady=5, sticky=tk.N)
        
        right_frame = ttk.Frame(config_frame)
        right_frame.grid(row=0, column=1, padx=10, pady=5, sticky=tk.N)
        
        self.terminal_entries = []
        
        # Left column (A-H)
        for i in range(8):
            label = ttk.Label(left_frame, text=f"{configs[i].name}:", width=4, anchor="e")
            label.grid(row=i, column=0, padx=(10, 0), pady=2, sticky=tk.E)
            
            entry = ttk.Entry(left_frame, width=10)
            entry.grid(row=i, column=1, padx=(0, 10), pady=2, sticky=tk.W)
            self.terminal_entries.append(entry)
        
        # Right column (AA-HH)
        for i in range(8, 16):
            label = ttk.Label(right_frame, text=f"{configs[i].name}:", width=4, anchor="e")
            label.grid(row=i-8, column=0, padx=(10, 0), pady=2, sticky=tk.E)
            
            entry = ttk.Entry(right_frame, width=10)
            entry.grid(row=i-8, column=1, padx=(0, 10), pady=2, sticky=tk.W)
            self.terminal_entries.append(entry)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Run Calculations", command=self.run_calculations).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset_fields).pack(side=tk.LEFT, padx=5)
        
        # Overlay controls
        ttk.Button(button_frame, text="Always on Top", command=self.toggle_always_on_top).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Compact Mode", command=self.toggle_compact_mode).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Exit", command=self.on_close).pack(side=tk.RIGHT, padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=20,
            font=('Consolas', 10)
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, padx=5, pady=5)
        
        self.terminal_entries[0].focus_set()
        
        # Initialize overlay state
        self.always_on_top = False
        self.compact_mode = False

    def setup_key_bindings(self):
        for i, entry in enumerate(self.terminal_entries):
            entry.bind('<Tab>', lambda e, idx=i: self.focus_next_entry(e, idx))
            entry.bind('<Return>', lambda e: self.run_calculations())

    def focus_next_entry(self, event, current_idx):
        next_idx = (current_idx + 1) % len(self.terminal_entries)
        self.terminal_entries[next_idx].focus_set()
        return "break"

    def run_calculations(self):
        try:
            # Update function configurations
            for i in range(TOTAL_FUNCTIONS):
                entry = self.terminal_entries[i]
                value = entry.get().strip()
                
                if value:
                    if len(value) > 1 and value[0] in '+-*/':
                        configs[i].operator = value[0]
                        configs[i].value = float(value[1:])
                        configs[i].active = True
                    else:
                        configs[i].operator = '+'
                        configs[i].value = float(value)
                        configs[i].active = True
                else:
                    configs[i].active = False
            
            # Get input values
            input_val = float(self.input_val.get())
            target1 = float(self.target1.get())
            target2 = float(self.target2.get())

            # Clear and prepare results
            self.results_text.delete(1.0, tk.END)
            self.status_var.set("Processing...")
            self.root.update()
            
            # Generate and test combinations
            combo_list = generate_combinations()
            
            self.results_text.insert(tk.END, "=== First Combination Set ===\n")
            matches1 = test_combinations(input_val, target1, combo_list, functions1, self.results_text)
            
            self.results_text.insert(tk.END, "\n\n=== Second Combination Set ===\n")
            matches2 = test_combinations(input_val, target2, combo_list, functions2, self.results_text)
            
            # Find common matches
            find_common_matches(matches1, matches2, combo_list, self.results_text)
            
            self.status_var.set("Done")
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid number: {str(e)}")
            self.status_var.set("Check your inputs")
        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed: {str(e)}")
            self.status_var.set("Error occurred")

    def reset_fields(self):
        self.input_val.delete(0, tk.END)
        self.target1.delete(0, tk.END)
        self.target2.delete(0, tk.END)
        
        for entry in self.terminal_entries:
            entry.delete(0, tk.END)
        
        self.results_text.delete(1.0, tk.END)
        self.status_var.set("Ready")
        self.terminal_entries[0].focus_set()

    def toggle_always_on_top(self):
        """Toggle always on top mode"""
        self.always_on_top = not self.always_on_top
        if self.always_on_top:
            self.root.attributes('-topmost', True)
            self.status_var.set("Always on top enabled - Window will stay above other apps")
        else:
            self.root.attributes('-topmost', False)
            self.status_var.set("Always on top disabled")

    def toggle_compact_mode(self):
        """Toggle compact overlay mode"""
        self.compact_mode = not self.compact_mode
        if self.compact_mode:
            # Make window smaller and semi-transparent
            self.root.geometry("400x600")
            self.root.attributes('-alpha', 0.8)
            self.status_var.set("Compact mode enabled - Smaller overlay window")
        else:
            # Restore normal size and opacity
            self.root.geometry("900x750")
            self.root.attributes('-alpha', 1.0)
            self.status_var.set("Compact mode disabled")

def main():
    try:
        root = tk.Tk()
        app = TerminalStyleConfig(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Application failed: {str(e)}")

if __name__ == "__main__":
    main()