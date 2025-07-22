import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sympy

class GraphicalCalculator:
    def __init__(self, master):
        self.master = master
        master.title("Graphical Calculator")

        # Function Input
        self.function_label = tk.Label(master, text="Enter Function (e.g., sin(x), x**2):")
        self.function_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.function_entry = tk.Entry(master, width=50)
        self.function_entry.grid(row=0, column=1, padx=5, pady=5)
        self.function_entry.insert(0, "x") # Default function

        # X-range Input
        self.x_range_label = tk.Label(master, text="X-Range (min,max):")
        self.x_range_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.x_range_entry = tk.Entry(master, width=50)
        self.x_range_entry.grid(row=1, column=1, padx=5, pady=5)
        self.x_range_entry.insert(0, "-10,10") # Default range

        # Plot Button
        self.plot_button = tk.Button(master, text="Plot Function", command=self.plot_function)
        self.plot_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Matplotlib Figure and Canvas
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def plot_function(self):
        # This method will be implemented in the next step
        pass

# root = tk.Tk()
# calculator = GraphicalCalculator(root)
# root.mainloop()


# ... (previous code for GraphicalCalculator class)

    def plot_function(self):
        function_str = self.function_entry.get()
        x_range_str = self.x_range_entry.get()

        try:
            # Parse X-range
            x_min_str, x_max_str = x_range_str.split(',')
            x_min = float(x_min_str.strip())
            x_max = float(x_max_str.strip())

            if x_min >= x_max:
                messagebox.showerror("Invalid Range", "X-min must be less than X-max.")
                return

            # Generate x values
            x_vals = np.linspace(x_min, x_max, 400) # 400 points for a smooth curve

            # Use SymPy for symbolic evaluation
            x = sympy.Symbol('x')
            # Replace common functions to be compatible with sympy and numpy
            # This is a simplified approach, a more robust parser might be needed for complex cases
            function_expr = function_str.replace('sin', 'sympy.sin').replace('cos', 'sympy.cos')\
                                        .replace('tan', 'sympy.tan').replace('exp', 'sympy.exp')\
                                        .replace('log', 'sympy.log').replace('sqrt', 'sympy.sqrt')

            # Evaluate the function for each x value
            y_vals = []
            for val in x_vals:
                try:
                    # Evaluate the expression for the current x value
                    # We use sympy.N to get a numerical evaluation
                    y_val = sympy.N(eval(function_expr, {'x': val, 'sympy': sympy}))
                    y_vals.append(y_val)
                except (ValueError, TypeError, NameError, ZeroDivisionError) as e:
                    # Handle cases where the function is undefined for some x values (e.g., 1/x at x=0)
                    y_vals.append(np.nan) # Append NaN to break the line in the plot


            # Clear previous plot
            self.ax.clear()

            # Plot the function
            self.ax.plot(x_vals, y_vals, label=f'y = {function_str}')
            self.ax.set_xlabel("X-axis")
            self.ax.set_ylabel("Y-axis")
            self.ax.set_title("Function Plot")
            self.ax.grid(True)
            self.ax.legend()

            # Redraw the canvas
            self.canvas.draw()

        except ValueError:
            messagebox.showerror("Input Error", "Invalid input for function or x-range. Please use numerical values for range (e.g., -10,10) and valid mathematical expressions.")
        except SyntaxError:
            messagebox.showerror("Input Error", "Invalid function syntax. Please check your expression.")
        except Exception as e:
            messagebox.showerror("An Error Occurred", f"An unexpected error occurred: {e}")


            import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sympy

class GraphicalCalculator:
    def __init__(self, master):
        self.master = master
        master.title("Graphical Calculator")

        # Function Input
        self.function_label = tk.Label(master, text="Enter Function (e.g., sin(x), x**2):")
        self.function_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.function_entry = tk.Entry(master, width=50)
        self.function_entry.grid(row=0, column=1, padx=5, pady=5)
        self.function_entry.insert(0, "x") # Default function

        # X-range Input
        self.x_range_label = tk.Label(master, text="X-Range (min,max):")
        self.x_range_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.x_range_entry = tk.Entry(master, width=50)
        self.x_range_entry.grid(row=1, column=1, padx=5, pady=5)
        self.x_range_entry.insert(0, "-10,10") # Default range

        # Plot Button
        self.plot_button = tk.Button(master, text="Plot Function", command=self.plot_function)
        self.plot_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Matplotlib Figure and Canvas
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def plot_function(self):
        function_str = self.function_entry.get()
        x_range_str = self.x_range_entry.get()

        try:
            # Parse X-range
            x_min_str, x_max_str = x_range_str.split(',')
            x_min = float(x_min_str.strip())
            x_max = float(x_max_str.strip())

            if x_min >= x_max:
                messagebox.showerror("Invalid Range", "X-min must be less than X-max.")
                return

            # Generate x values
            x_vals = np.linspace(x_min, x_max, 400) # 400 points for a smooth curve

            # Use SymPy for symbolic evaluation
            x = sympy.Symbol('x')
            # Replace common functions to be compatible with sympy and numpy
            # This is a simplified approach, a more robust parser might be needed for complex cases
            function_expr = function_str.replace('sin', 'sympy.sin').replace('cos', 'sympy.cos')\
                                        .replace('tan', 'sympy.tan').replace('exp', 'sympy.exp')\
                                        .replace('log', 'sympy.log').replace('sqrt', 'sympy.sqrt')

            # Evaluate the function for each x value
            y_vals = []
            for val in x_vals:
                try:
                    # Evaluate the expression for the current x value
                    # We use sympy.N to get a numerical evaluation
                    y_val = sympy.N(eval(function_expr, {'x': val, 'sympy': sympy}))
                    y_vals.append(y_val)
                except (ValueError, TypeError, NameError, ZeroDivisionError) as e:
                    # Handle cases where the function is undefined for some x values (e.g., 1/x at x=0)
                    y_vals.append(np.nan) # Append NaN to break the line in the plot


            # Clear previous plot
            self.ax.clear()

            # Plot the function
            self.ax.plot(x_vals, y_vals, label=f'y = {function_str}')
            self.ax.set_xlabel("X-axis")
            self.ax.set_ylabel("Y-axis")
            self.ax.set_title("Function Plot")
            self.ax.grid(True)
            self.ax.legend()

            # Redraw the canvas
            self.canvas.draw()

        except ValueError:
            messagebox.showerror("Input Error", "Invalid input for function or x-range. Please use numerical values for range (e.g., -10,10) and valid mathematical expressions.")
        except SyntaxError:
            messagebox.showerror("Input Error", "Invalid function syntax. Please check your expression.")
        except Exception as e:
            messagebox.showerror("An Error Occurred", f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    calculator = GraphicalCalculator(root)
    root.mainloop()