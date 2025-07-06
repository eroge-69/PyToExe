import tkinter as tk
from tkinter import filedialog, messagebox
import csv
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class WaterUseDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Water Use Dashboard")
        self.data = []
        self.recommended_usage = 135  # liters per day per person

        # Load button
        tk.Button(root, text="Load Water Usage File", command=self.load_file).grid(row=0, column=0, columnspan=3, pady=10)

        # Summary section
        self.summary_frame = tk.LabelFrame(root, text="Summary", padx=10, pady=10)
        self.summary_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.total_label = tk.Label(self.summary_frame, text="Total Usage: 0 L")
        self.avg_label = tk.Label(self.summary_frame, text="Average Usage: 0 L")
        self.max_label = tk.Label(self.summary_frame, text="Max Usage: 0 L")
        self.min_label = tk.Label(self.summary_frame, text="Min Usage: 0 L")
        self.recommend_label = tk.Label(self.summary_frame, text=f"Recommended: {self.recommended_usage} L/day")

        self.total_label.grid(row=0, column=0, padx=5, pady=2)
        self.avg_label.grid(row=0, column=1, padx=5, pady=2)
        self.max_label.grid(row=1, column=0, padx=5, pady=2)
        self.min_label.grid(row=1, column=1, padx=5, pady=2)
        self.recommend_label.grid(row=2, column=0, columnspan=2, pady=5)

        # Graph section
        self.figure = Figure(figsize=(6, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    def load_file(self):
        filepath = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])
        if not filepath:
            return

        try:
            self.data.clear()
            with open(filepath, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    usage = float(row['Usage'])
                    if usage > 0:
                        self.data.append(usage)

            if not self.data:
                raise ValueError("No valid data found.")
            self.update_dashboard()

        except Exception as e:
            messagebox.showerror("File Error", f"Could not read file:\n{e}")

    def update_dashboard(self):
        total = sum(self.data)
        avg = total / len(self.data)
        max_usage = max(self.data)
        min_usage = min(self.data)

        self.total_label.config(text=f"Total Usage: {total:.1f} L")
        self.avg_label.config(text=f"Average Usage: {avg:.1f} L")
        self.max_label.config(text=f"Max Usage: {max_usage:.1f} L")
        self.min_label.config(text=f"Min Usage: {min_usage:.1f} L")

        self.avg_label.config(fg="green" if avg <= self.recommended_usage else "red")

        # Plot
        self.ax.clear()
        self.ax.bar(range(1, len(self.data) + 1), self.data, color='skyblue')
        self.ax.axhline(self.recommended_usage, color='orange', linestyle='--', label="Recommended")
        self.ax.set_title("Daily Water Usage")
        self.ax.set_xlabel("Day")
        self.ax.set_ylabel("Liters")
        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = WaterUseDashboard(root)
    root.mainloop()
