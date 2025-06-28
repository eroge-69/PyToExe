import matplotlib.pyplot as plt
import tkinter as tk
import numpy as np

# Reference plotting values (already in 0-1 range)
reference_values = [0.081, 0.142, 0.191, 0.228, 0.355, 0.473, 0.586, 0.744, 0.928, 0.954]
reference_labels = [315, 250, 180, 140, 95, 72, 55, 42, 26, 17]

class TripleInputDialog(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Input Values")
        self.geometry("600x300")
        self.resizable(False, False)

        # ID input at the top
        tk.Label(self, text="Image ID:").pack(pady=(10, 0))
        self.id_entry = tk.Entry(self, width=30)
        self.id_entry.pack(pady=(0, 10))

        self.columns = ["Heart", "Artery", "Lung"]
        self.red_entries = []
        self.blue_entries = []

        frame = tk.Frame(self)
        frame.pack(pady=10)

        for i, col in enumerate(self.columns):
            col_frame = tk.Frame(frame)
            col_frame.grid(row=0, column=i+1, padx=5)  # Shift right by 1 for reference column

            tk.Label(col_frame, text=col, font=("Arial", 12, "bold")).pack()
            tk.Label(col_frame, text="Red (0-1, comma separated):").pack()
            red_entry = tk.Entry(col_frame, width=18)
            red_entry.pack()
            self.red_entries.append(red_entry)

            tk.Label(col_frame, text="Blue (0-1, comma separated):").pack()
            blue_entry = tk.Entry(col_frame, width=18)
            blue_entry.pack()
            self.blue_entries.append(blue_entry)

        # Reference column label
        ref_col_frame = tk.Frame(frame)
        ref_col_frame.grid(row=0, column=0, padx=5)
        tk.Label(ref_col_frame, text="Reference", font=("Arial", 12, "bold")).pack()
        tk.Label(ref_col_frame, text="(Fixed values)").pack()

        tk.Button(self, text="OK", command=self.on_ok).pack(pady=10)

        self.red_values = []
        self.blue_values = []
        self.result = False
        self.image_id = ""

    def on_ok(self):
        self.red_values = [entry.get() for entry in self.red_entries]
        self.blue_values = [entry.get() for entry in self.blue_entries]
        self.image_id = self.id_entry.get()
        self.result = True
        self.destroy()

def input_to_plotting_value(input_val):
    try:
        return -np.log((input_val - 27.619) / 448.608) / 5.453
    except Exception:
        return None

# Show the dialog
dialog = TripleInputDialog()
dialog.mainloop()

if dialog.result:
    try:
        # Parse values for each column
        red_values = []
        blue_values = []
        for red_str, blue_str in zip(dialog.red_values, dialog.blue_values):
            reds = []
            for v in red_str.split(","):
                v = v.strip()
                if v:
                    plotting_v = input_to_plotting_value(float(v))
                    if plotting_v is not None and 0 <= plotting_v <= 1:
                        reds.append(plotting_v)
            blues = []
            for v in blue_str.split(","):
                v = v.strip()
                if v:
                    plotting_v = input_to_plotting_value(float(v))
                    if plotting_v is not None and 0 <= plotting_v <= 1:
                        blues.append(plotting_v)
            red_values.append(reds)
            blue_values.append(blues)

        fig, ax = plt.subplots(figsize=(6, 6))
        col_positions = [0.18, 0.38, 0.55, 0.72]  # Add position for reference column
        # Plot reference values (flipped)
        for v, label in zip(reference_values, reference_labels):
            flipped_v = 1 - v
            ax.hlines(y=flipped_v, xmin=col_positions[0]-0.06, xmax=col_positions[0]+0.06, color='black', linewidth=4)
            # Add label to the left of the line
            ax.text(col_positions[0]-0.09, flipped_v, str(label), ha='right', va='center', fontsize=10)
        # Plot user input columns
        for i, (reds, blues) in enumerate(zip(red_values, blue_values)):
            for v in reds:
                flipped_v = 1 - v  # Flip the position
                ax.hlines(y=flipped_v, xmin=col_positions[i+1]-0.06, xmax=col_positions[i+1]+0.06, color='red', linewidth=4)
            for v in blues:
                flipped_v = 1 - v  # Flip the position
                ax.hlines(y=flipped_v, xmin=col_positions[i+1]-0.06, xmax=col_positions[i+1]+0.06, color='blue', linewidth=4)
            # Add column label
            ax.text(col_positions[i+1], -0.05, dialog.columns[i], ha='center', va='top', fontsize=12, fontweight='bold')
        # Add reference column label
        ax.text(col_positions[0], -0.05, "Reference", ha='center', va='top', fontsize=12, fontweight='bold')

        # Show image ID at the top
        if dialog.image_id:
            plt.title(f"ID: {dialog.image_id}", fontsize=14, pad=20)

        ax.set_ylim(0, 1)
        ax.set_xlim(0, 1)
        ax.axis('off')
        plt.show()
    except ValueError:
        print("Please enter valid numbers separated by commas.")
else:
    print("No input provided.")
