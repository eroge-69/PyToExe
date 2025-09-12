import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter

MOVES = {
    '+16': 16,
    '+13': 13,
    '+7': 7,
    '+2': 2,
    '-3': -3,
    '-6': -6,
    '-9': -9,
    '-15': -15
}

class AnvilOptimizerPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Anvil Optimizer Pro")
        self.root.geometry("600x500")
        self.setup_ui()
        
    def setup_ui(self):
        # Configure style
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TButton', padding=6, background='#4CAF50', foreground='white')
        style.configure('Header.TLabel', font=('Arial', 11, 'bold'))
        
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Target Score
        ttk.Label(main_frame, text="Target Score:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_target = ttk.Entry(main_frame, font=('Arial', 12))
        self.entry_target.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Final Hits Selection
        ttk.Label(main_frame, text="Number of Final Hits:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.hits_selector = ttk.Combobox(main_frame, values=[2, 3], state='readonly')
        self.hits_selector.current(1)  # Default to 3
        self.hits_selector.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.hits_selector.bind('<<ComboboxSelected>>', self.update_hits_entries)
        
        # Final hits entries
        self.final_hits_frame = ttk.Frame(main_frame)
        self.final_hits_frame.grid(row=2, column=0, columnspan=2, pady=10)
        self.entries = []
        self.create_hits_entries(3)
        
        # Calculate button
        self.btn_calc = ttk.Button(main_frame, text="Find Optimal Sequence", 
                                 command=self.calculate, style='TButton')
        self.btn_calc.grid(row=3, column=0, columnspan=2, pady=15)
        
        # Results display
        result_frame = ttk.LabelFrame(main_frame, text="Optimal Sequence", padding=15)
        result_frame.grid(row=4, column=0, columnspan=2, sticky=tk.NSEW, pady=10)
        
        self.result_text = tk.Text(result_frame, height=10, width=65, state='disabled',
                                 font=('Consolas', 10), bg='#fafafa', wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
    
    def create_hits_entries(self, count):
        for widget in self.final_hits_frame.winfo_children():
            widget.destroy()
        self.entries = []
        
        ttk.Label(self.final_hits_frame, text="Final Moves:").pack(side=tk.LEFT, padx=5)
        
        for i in range(count):
            entry = ttk.Combobox(self.final_hits_frame, 
                               values=list(MOVES.keys()), 
                               width=5, 
                               font=('Arial', 12),
                               state='readonly')
            entry.pack(side=tk.LEFT, padx=5)
            self.entries.append(entry)
    
    def update_hits_entries(self, event=None):
        try:
            new_count = int(self.hits_selector.get())
            self.create_hits_entries(new_count)
        except ValueError:
            pass
    
    def validate_inputs(self):
        try:
            target = int(self.entry_target.get())
            if target <= 0:
                raise ValueError("Target score must be positive")
            
            final_moves = [entry.get() for entry in self.entries if entry.get()]
            
            if len(final_moves) != int(self.hits_selector.get()):
                raise ValueError(f"Please select exactly {self.hits_selector.get()} final moves")
            
            for move in final_moves:
                if move not in MOVES:
                    raise ValueError(f"Invalid move: {move}")
            
            return target, final_moves
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return None, None

    def find_optimal_sequence(self, target, final_moves):
        final_sum = sum(MOVES[m] for m in final_moves)
        needed = target - final_sum
        
        if needed < 0:
            return None, "Final moves exceed target score"
        if needed == 0:
            return final_moves, None
        
        # Start with smallest number of moves
        for depth in range(1, 10):
            result = self.dfs(needed, depth, [])
            if result:
                return result + final_moves, None
        
        return None, "No solution found (tried up to 9 initial moves)"

    def dfs(self, remaining, depth, path):
        if depth == 0:
            return None if remaining != 0 else path
        
        # Try moves in order of absolute value (largest first)
        for move, value in sorted(MOVES.items(), key=lambda x: -abs(x[1])):
            new_remaining = remaining - value
            if new_remaining < 0 and value > 0:
                continue  # Skip positive moves that overshoot
                
            result = self.dfs(new_remaining, depth-1, path + [move])
            if result:
                return result
        return None

    def calculate(self):
        target, final_moves = self.validate_inputs()
        if target is None:
            return
        
        sequence, error = self.find_optimal_sequence(target, final_moves)
        
        if error:
            messagebox.showerror("Error", error)
            return
        
        self.display_result(sequence, target, final_moves)

    def display_result(self, sequence, target, final_moves):
        initial_moves = sequence[:-len(final_moves)]
        final_moves = sequence[-len(final_moves):]
        
        # Count move occurrences
        move_counts = Counter(sequence)
        
        # Prepare formatted output
        output = ["=== OPTIMAL SEQUENCE ===",
                 f"Total moves: {len(sequence)}",
                 f"Target score: {target}",
                 f"Calculated score: {sum(MOVES[m] for m in sequence)}",
                 "",
                 "MOVES BREAKDOWN:"]
        
        # Add move counts (sorted by absolute value)
        for move, value in sorted(MOVES.items(), key=lambda x: -abs(x[1])):
            if move_counts[move] > 0:
                times = "time" if move_counts[move] == 1 else "times"
                output.append(f"{move} x {move_counts[move]} {times}")
        
        # Add sequence visualization
        output.extend(["",
                     "SEQUENCE FLOW:",
                     " → ".join(sequence),
                     "",
                     f"Initial moves ({len(initial_moves)}): {' + '.join(str(MOVES[m]) for m in initial_moves)} = {sum(MOVES[m] for m in initial_moves)}",
                     f"Final moves ({len(final_moves)}): {' + '.join(str(MOVES[m]) for m in final_moves)} = {sum(MOVES[m] for m in final_moves)}"])
        
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "\n".join(output))
        self.result_text.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = AnvilOptimizerPro(root)
    root.mainloop()