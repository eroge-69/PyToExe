import math
import tkinter as tk
from tkinter import ttk, messagebox

def mannings_flow(D, S, Q, n):
    """
    Calculate the percentage of pipe filled and flow velocity.
    
    Parameters:
    D : float - Pipe diameter (m)
    S : float - Slope (decimal)
    Q : float - Flow rate (m³/s)
    n : float - Manning's roughness coefficient
    
    Returns:
    percentage : float - Percentage of pipe filled
    velocity : float - Flow velocity (m/s)
    capacity : float - Full pipe capacity (m³/s)
    """
    # Helper function for Manning's equation
    def Q_calc(theta):
        A = (D**2 / 8) * (theta - math.sin(theta))
        if theta == 0:
            R = 0
        else:
            R = (D / 4) * (1 - math.sin(theta) / theta)
        return (1 / n) * A * (R ** (2/3)) * (S ** 0.5)
    
    # Compute half-full and full flow rates
    theta_half = math.pi
    Q_half = Q_calc(theta_half)
    Q_full = Q_calc(2 * math.pi)
    
    if Q > Q_full:
        return None, None, Q_full
    
    # Set bisection interval
    low, high = (0.01, math.pi) if Q <= Q_half else (math.pi, 2 * math.pi - 0.01)
    
    # Bisection method
    tol = 1e-6
    theta = (low + high) / 2
    for _ in range(100):
        Q_current = Q_calc(theta)
        
        if abs(Q_current - Q) < tol:
            break
        
        if Q_current < Q:
            low = theta
        else:
            high = theta
        
        theta = (low + high) / 2
    
    # Calculate results
    y = (D / 2) * (1 - math.cos(theta / 2))
    percentage = (y / D) * 100
    A = (D**2 / 8) * (theta - math.sin(theta))
    velocity = Q / A
    
    return percentage, velocity, Q_full

def calculate():
    try:
        # Get values from input fields
        D = float(entry_diameter.get())
        S = float(entry_slope.get()) / 100  # Convert % to decimal
        Q = float(entry_flow.get()) / 3600  # Convert m³/h to m³/s
        n = float(entry_manning.get())
        
        # Perform calculation
        percentage, velocity, capacity = mannings_flow(D, S, Q, n)
        
        if percentage is None:
            messagebox.showwarning("Capacity Exceeded", 
                                  f"Flow exceeds pipe capacity! Max flow: {capacity:.3f} m³/s")
            result_text.set(f"Flow exceeds pipe capacity!\nMax flow: {capacity:.3f} m³/s")
        else:
            # Update results display
            result_text.set(
                f"Pipe Fill Percentage: {percentage:.1f}%\n"
                f"Flow Velocity: {velocity:.3f} m/s\n"
                f"Full Pipe Capacity: {capacity:.3f} m³/s"
            )
            
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers in all fields")
        result_text.set("Please enter valid numbers")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        result_text.set("Calculation error")

# Create main window
root = tk.Tk()
root.title("Pipe Flow Calculator")
root.geometry("400x450")

# Create input frame
input_frame = ttk.LabelFrame(root, text="Pipe Parameters", padding=10)
input_frame.pack(padx=10, pady=10, fill="x")

# Input fields
ttk.Label(input_frame, text="Pipe Diameter (m):").grid(row=0, column=0, sticky="w", pady=5)
entry_diameter = ttk.Entry(input_frame)
entry_diameter.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
entry_diameter.insert(0, "0.321")

ttk.Label(input_frame, text="Slope (%):").grid(row=1, column=0, sticky="w", pady=5)
entry_slope = ttk.Entry(input_frame)
entry_slope.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
entry_slope.insert(0, "1.0")

ttk.Label(input_frame, text="Flow Rate (m³/h):").grid(row=2, column=0, sticky="w", pady=5)
entry_flow = ttk.Entry(input_frame)
entry_flow.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
entry_flow.insert(0, "400")

ttk.Label(input_frame, text="Manning's Roughness (n):").grid(row=3, column=0, sticky="w", pady=5)
entry_manning = ttk.Entry(input_frame)
entry_manning.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
entry_manning.insert(0, "0.013")

# Calculate button
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)
calculate_btn = ttk.Button(button_frame, text="Calculate", command=calculate)
calculate_btn.pack()

# Results display
result_frame = ttk.LabelFrame(root, text="Results", padding=10)
result_frame.pack(padx=10, pady=10, fill="both", expand=True)

result_text = tk.StringVar()
result_text.set("Enter values and click 'Calculate'")
result_label = ttk.Label(result_frame, textvariable=result_text, 
                         font=("Arial", 12), justify="left")
result_label.pack(fill="both", expand=True, padx=5, pady=5)

# Run the application
root.mainloop()
