import tkinter as tk
import random

def generate_random_number():
    """QP set selesction for 3 sets"""
    random_num = random.randint(1, 3)
    result_label.config(text=f"Generated Set Number: {random_num}")

# Create the main window
root = tk.Tk()
root.title("QP set selesction for 3 sets randomly")
root.geometry("400x150") # Set window size

# Create a label to display the result
result_label = tk.Label(root, text="Click 'Generate' to select QP set randomly", font=("Arial", 14))
result_label.pack(pady=20)

# Create a button to trigger random number generation
generate_button = tk.Button(root, text="Generate", command=generate_random_number, font=("Arial", 12))
generate_button.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()