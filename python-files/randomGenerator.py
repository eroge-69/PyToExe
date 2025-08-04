import tkinter as tk
import random

def generate_sequence():
    try:
        # Get the input number from the entry widget
        input_number = int(entry.get())

        # Check if input is within the valid range
        if 0 <= input_number <= 18:
            # Generate the sequence (random numbers between 1 and 100)
            sequence = [random.randint(1, 100) for _ in range(input_number)]
            result_label.config(text=f"Generated Sequence: {sequence}")
        else:
            result_label.config(text="Please enter a number between 0 and 18.")
    except ValueError:
        result_label.config(text="Invalid input! Please enter an integer.")

# Create the main window
root = tk.Tk()
root.title("Random Sequence Generator")

# Add an input label and entry widget
input_label = tk.Label(root, text="Enter a number between 0 and 18:")
input_label.pack(pady=10)

entry = tk.Entry(root)
entry.pack(pady=5)

# Add a button to generate the sequence
generate_button = tk.Button(root, text="Generate Sequence", command=generate_sequence)
generate_button.pack(pady=10)

# Add a label to display the result
result_label = tk.Label(root, text="Generated Sequence will appear here.")
result_label.pack(pady=20)

# Run the GUI loop
root.mainloop()
