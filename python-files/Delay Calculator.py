import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class DelayCalculatorApp:
    def __init__(self, master):
        self.master = master
        master.title("EFG Delay Calculator")
        master.geometry("450x700") # Adjusted size for buttons

        self.microphones = []  # Start empty, will add dynamically
        self.microphone_counter = 0 # Counter for microphone names

        # Stores references to Entry widgets and result Labels
        # Structure: {'Microphone X': {'entry': entry_widget, 'result_label': result_label_widget, 'frame': item_frame}}
        self.microphone_widgets = {}

        self.create_widgets()
        self.initialize_microphones(20) # Add initial 20 microphones

    def create_widgets(self):
        # Top section for title and hint
        title_frame = ttk.Frame(self.master, padding="10")
        title_frame.pack(fill="x")

        ttk.Label(title_frame, text="Delay Calculator", font=("Arial", 16, "bold")).pack(pady=5)
        ttk.Label(title_frame, text="Please enter the distance in meters for each microphone.").pack(pady=2)
        ttk.Label(title_frame, text="Note: Decimal places for distances must be separated by a dot (e.g., 10.5).",
                  foreground="orange", font=("Arial", 9, "italic")).pack(pady=5)

        # Frame for microphone inputs (with scrollbar)
        input_frame = ttk.Frame(self.master, padding="10")
        input_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(input_frame)
        self.scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Controls (Plus/Minus Buttons)
        control_frame = ttk.Frame(self.master, padding="10")
        control_frame.pack(fill="x")

        style = ttk.Style()
        style.configure("Control.TButton", font=("Arial", 16, "bold"), width=3) # Larger font for symbols

        self.add_button = ttk.Button(control_frame, text="+", command=self.add_microphone, style="Control.TButton")
        self.add_button.pack(side="left", padx=5, expand=True)

        self.remove_button = ttk.Button(control_frame, text="-", command=self.remove_microphone, style="Control.TButton")
        self.remove_button.pack(side="right", padx=5, expand=True)

        # Calculate Button
        calculate_button = ttk.Button(self.master, text="Calculate", command=self.calculate_delays)
        calculate_button.pack(pady=10)

        # Greatest Distance Display
        self.max_dist_label = ttk.Label(self.master, text="Greatest Distance: 0.00 m", font=("Arial", 10, "bold"))
        self.max_dist_label.pack(pady=5)

    def add_microphone(self):
        self.microphone_counter += 1
        microphone_name = f"Microphone {self.microphone_counter}"
        self.microphones.append(microphone_name) # Add the name to the list

        # Create a frame for each microphone to make it easier to remove
        item_frame = ttk.Frame(self.scrollable_frame)
        item_frame.pack(fill="x", pady=2)

        label = ttk.Label(item_frame, text=f"{microphone_name}:")
        label.pack(side="left", padx=5)

        entry = ttk.Entry(item_frame, width=10)
        entry.pack(side="left", padx=5)

        result_label = ttk.Label(item_frame, text="0.00 ms")
        result_label.pack(side="right", padx=5)

        # Store all relevant widgets of the microphone
        self.microphone_widgets[microphone_name] = {
            'entry': entry,
            'result_label': result_label,
            'frame': item_frame # Store the frame to destroy it later
        }

        # Update scroll region and scroll to the end
        self.scrollable_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(1)

    def remove_microphone(self):
        if len(self.microphones) > 0:
            last_microphone_name = self.microphones.pop() # Remove the last name from the list
            if last_microphone_name in self.microphone_widgets:
                # Destroy the entire microphone frame
                self.microphone_widgets[last_microphone_name]['frame'].destroy()
                del self.microphone_widgets[last_microphone_name] # Remove from the dictionary

                # Update scroll region
                self.scrollable_frame.update_idletasks()
                self.canvas.config(scrollregion=self.canvas.bbox("all"))

                self.microphone_counter -= 1 # Decrement counter
                self.calculate_delays() # Recalculate results

    def initialize_microphones(self, count):
        for _ in range(count):
            self.add_microphone()

    def calculate_delays(self):
        distances_current_session = {} # Stores only currently valid distances
        greatest_distance = 0.0

        # Iterate over the list of microphones to read inputs
        for microphone_name in self.microphones:
            if microphone_name not in self.microphone_widgets:
                continue # Skip if the widget has already been removed

            entry_widget = self.microphone_widgets[microphone_name]['entry']
            try:
                distance_str = entry_widget.get()
                if not distance_str:
                    distance = 0.0
                else:
                    distance = float(distance_str)
                distances_current_session[microphone_name] = distance
                if distance > greatest_distance:
                    greatest_distance = distance
            except ValueError:
                messagebox.showerror("Error", f"Invalid input for {microphone_name}. Please enter a number.")
                return

        self.max_dist_label.config(text=f"Greatest Distance: {greatest_distance:.2f} m")

        # Reset all results before recalculating
        for microphone_name in self.microphone_widgets:
            self.microphone_widgets[microphone_name]['result_label'].config(text="0.00 ms")

        # Calculate and display delay times
        for microphone_name, distance in distances_current_session.items():
            difference = greatest_distance - distance
            delay_time_ms = difference / 0.343
            self.microphone_widgets[microphone_name]['result_label'].config(text=f"{delay_time_ms:.2f} ms")

# Start the application
if __name__ == "__main__":
    root = tk.Tk()
    app = DelayCalculatorApp(root)
    root.mainloop()