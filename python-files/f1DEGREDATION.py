import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
# Defining a new class: F1Tyre
# This class simulates the physical behaviour of a tyre depending on compound
# The variables I have been using to simulate this behaviour are :grip, wear, temperature, pressures, and puncture risk

class F1Tyre:
    def __init__(self, compound='Soft', initial_temp=90, initial_pressure=2.2):
        # tyre parameters
        self.compound = compound
        self.optimal_temp = 90         # optimal temp (oC)
        self.optimal_pressure = 2.2    # optimal pressure (bar)
        self.puncture_threshold = 0.85 # Puncture threshold (The maximum amount of wear before a puncture)
        self.punctured = False         # Puncture flag(Boolean value)

        # Specific behaviour of each tyre Compound (different wear rates and Temp sensitivities)
        if compound.lower() == 'soft':
            self.wear_rate = 0.025
            self.temp_sensitivity = 1.2
            self.base_lap_time = 87.0  # Softs is fastest base lap time for silverstone is 87 seconds
        elif compound.lower() == 'medium':
            self.wear_rate = 0.018
            self.temp_sensitivity = 1.0
            self.base_lap_time = 89.0
        else:# hard tyre
            self.wear_rate = 0.012
            self.temp_sensitivity = 0.8
            self.base_lap_time = 92.0
        # Initial values
        self.temperature = initial_temp
        self.pressure = initial_pressure
        self.wear = 0.0
        self.grip = 1.0

    # Called every lap to update tyre conditions and account for natural progression of the tyres 
    def update(self, driving_aggression=1.0, track_abrasion=1.0):
        #Checking to see if the tyre is Punctured
        if self.punctured:
            return self.get_status()

        # Temperature Update
        # Tyres tend to their individual optimum temperature
        #If the current temp is < optimal then the Tyre is warming up otherwise it is cooling 
        temp_change = (self.optimal_temp - self.temperature) * 0.1  
        # The more agressive the driver the more heat is generated (Hard cornering and braking)
        temp_change += driving_aggression * 2.5
        # Applying this to the individual compound (soft tyres reach their optimum temp faster than hardtyres hence the higher sensitivity definied in the f1 tyre class)
        self.temperature += temp_change * self.temp_sensitivity

        # Pressure adjustment (basic physics: hotter tyre = air expands = more pressure)
        # Formula: new pressure  =  old pressure * (1 + 0.0035 * change in temp)
        self.pressure *= (1 + (self.temperature - self.optimal_temp) * 0.0035)

        # Wear increments
        sliding_factor = max(0, 1.2 - self.grip) # more sliding = extra wear
        wear_increment = (self.wear_rate * driving_aggression * track_abrasion * (1 + sliding_factor))
        self.wear += wear_increment
         
        # If tyres are too worn = puncture
        if self.wear >= self.puncture_threshold:
            self.punctured = True
            self.grip = 0.0
            return self.get_status()

        # Grip calculation based on multiple factors
        wear_effect = max(0, 1 - self.wear)  # less tread = less grip
        temp_diff = abs(self.temperature - self.optimal_temp) # the further away from optimum temp = less grip
        temp_effect = max(0.1, 1 - (temp_diff / 100) ** 2)
        pressure_diff = abs(self.pressure - self.optimal_pressure)
        pressure_effect = max(0.1, 1 - pressure_diff / 2) # the further away from optimum pressure = less grip

        # Final grip product product of all effects
        self.grip = wear_effect * temp_effect * pressure_effect

        # Extra wear if tyre too hot or too cold
        if self.temperature > 120:
            self.wear += 0.02 * (self.temperature - 120) / 10
        elif self.temperature < 70:
            self.wear += 0.01 * (70 - self.temperature) / 10

        return self.get_status()
    # Returns current tyre status 
    def get_status(self):
        return {
            'compound': self.compound,
            'grip': round(self.grip, 4),
            'wear': round(self.wear, 4),
            'temperature': round(self.temperature, 1),
            'pressure': round(self.pressure, 3),
            'punctured': self.punctured
        }

    # Lap time calculation based on grip (lower grip slows lap)
    def get_lap_time(self):
        penalty = (1.0 - self.grip) * 10  
        puncture_penalty = 30 if self.punctured else 0
        wear_penalty = self.wear * 8
        temp_diff = abs(self.temperature - self.optimal_temp)
        temp_penalty = (temp_diff / 50) * 2
        total_time = self.base_lap_time + penalty + puncture_penalty + wear_penalty + temp_penalty
        return round(total_time, 2)
#Function to set theme for the UI
def set_f1_theme(root):
    style = ttk.Style(root)
    root.configure(bg="#15151a")
    style.theme_use('clam')
    style.configure("TLabel", background="#15151a", foreground="#ffd700", font=("Segoe UI", 11))
    style.configure("TButton", background="#ff1e00", foreground="white", font=("Segoe UI", 11, "bold"))
    style.map("TButton", background=[("active", "#cc1a00")])
    style.configure("TEntry", fieldbackground="#22222d", foreground="#ffd700")
    style.configure("TCombobox", fieldbackground="#22222d", background="#22222d", foreground="#ffd700")
    style.map("TCombobox", fieldbackground=[("readonly", "#22222d")], foreground=[("readonly", "#ffd700")])

# Controls entire program UI: inputs, text output, live plots, CSV export
class TyreSimulationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("F1 Tyre Simulation")
        set_f1_theme(root)
        # User input variables
        self.compound_var = tk.StringVar(value="Soft")
        self.laps_var = tk.IntVar(value=10)
        self.aggression_var = tk.DoubleVar(value=1.0)
        self.track_abrasion_var = tk.DoubleVar(value=1.0)
        
        # Store all simulation data
        self.simulation_results = []
        
        self.setup_gui()
        self.create_matplotlib_figures()

    #Function to allow data to be exported as CSV
    def download_csv(self):
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        filename = os.path.join(downloads_folder, "tyre_simulation_results.csv")
        if not self.simulation_results:
            messagebox.showinfo("No Results", "Run a simulation first!")
            return
        with open(filename, "w", newline="") as csvfile:
            fieldnames = ['lap', 'compound', 'grip', 'wear', 'temperature', 'pressure', 'punctured', 'lap_time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in self.simulation_results:
                writer.writerow(row)
        messagebox.showinfo("Download Complete", f"Results saved to:\n{filename}")
    
    # Create widgets for inputs/outputs
    def setup_gui(self):
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.grid(row=0, column=0, sticky="ew", columnspan=2)
        #Inouts
        ttk.Label(input_frame, text="Tyre Compound:").grid(row=0, column=0, sticky="w")
        compound_combobox = ttk.Combobox(input_frame, textvariable=self.compound_var, values=["Soft", "Medium", "Hard"], width=12)
        compound_combobox.grid(row=0, column=1, sticky="ew", padx=5)
        
        ttk.Label(input_frame, text="Number of Laps:").grid(row=1, column=0, sticky="w")
        ttk.Entry(input_frame, textvariable=self.laps_var, width=8).grid(row=1, column=1, sticky="ew", padx=5)
        
        ttk.Label(input_frame, text="Driving Aggression:").grid(row=2, column=0, sticky="w")
        ttk.Entry(input_frame, textvariable=self.aggression_var, width=8).grid(row=2, column=1, sticky="ew", padx=5)
        
        ttk.Label(input_frame, text="Track Abrasion (optional):").grid(row=3, column=0, sticky="w")
        ttk.Entry(input_frame, textvariable=self.track_abrasion_var, width=8).grid(row=3, column=1, sticky="ew", padx=5)
        #Buttons
        run_button = ttk.Button(input_frame, text="Run Simulation", command=self.run_simulation)
        run_button.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")
        
        download_button = ttk.Button(input_frame, text="Download CSV", command=self.download_csv)
        download_button.grid(row=5, column=0, columnspan=2, pady=5, sticky="ew")
        #Output Area
        self.output_text = tk.Text(self.root, wrap=tk.WORD, height=14, width=65, bg="#111118", fg="#ffd700", font=("Consolas", 10))
        self.output_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

    # Create Matplotlib figures for data , also puts in the colour scheme and axis titles 
    def create_matplotlib_figures(self):
        self.fig_frames, self.figs, self.axes, self.canvases = [], [], [], []

        colors = ['lime', 'orangered', 'skyblue', 'gold', 'magenta']
        titles = ['Grip per Lap', 'Wear per Lap', 'Temperature (C) per Lap', 'Pressure (bar) per Lap', 'Lap Time (s) per Lap']
        ylabels = ['Grip', 'Wear', 'Temperature (oC)', 'Pressure (bar)', 'Lap Time (s)']

        container = ttk.Frame(self.root)
        container.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)
        container.grid_rowconfigure((0, 1, 2), weight=1)
        container.grid_columnconfigure((0, 1), weight=1)
        
        # 5 subplots in 2x3 arrangement
        for i in range(5):
            frame = ttk.Frame(container)
            frame.grid(row=i//2, column=i%2, sticky="nsew", padx=5, pady=5)
            fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
            ax.set_title(titles[i], color=colors[i])
            ax.set_ylabel(ylabels[i])
            ax.set_xlabel("Lap")
            ax.grid(True, linestyle='--', alpha=0.4)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

            self.fig_frames.append(frame)
            self.figs.append(fig)
            self.axes.append(ax)
            self.canvases.append(canvas)
    
     # Update graphs after simulation
    def update_matplotlib_plots(self):
        if not self.simulation_results:
            for ax in self.axes:
                ax.cla()
                ax.grid(True, linestyle='--', alpha=0.4)
            for canvas in self.canvases:
                canvas.draw()
            return
        laps = [data['lap'] for data in self.simulation_results]
        metrics = ['grip', 'wear', 'temperature', 'pressure', 'lap_time']
        colors = ['lime', 'orangered', 'skyblue', 'gold', 'magenta']
        for i, metric in enumerate(metrics):
            self.axes[i].cla()
            values = [data[metric] for data in self.simulation_results]
            self.axes[i].plot(laps, values, color=colors[i], linewidth=2)
            self.axes[i].set_title(f"{metric.replace('_', ' ').capitalize()} per Lap", color=colors[i])
            ylabel = {
                'grip': 'Grip',
                'wear': 'Wear',
                'temperature': 'Temperature (oC)',
                'pressure': 'Pressure (bar)',
                'lap_time': 'Lap Time (s)'
            }
            self.axes[i].set_ylabel(ylabel[metric])
            self.axes[i].set_xlabel("Lap")
            self.axes[i].grid(True, linestyle='--', alpha=0.4)
            self.figs[i].tight_layout()
            self.canvases[i].draw()

    # Run simulation across user selected laps
    def run_simulation(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.simulation_results = []

        compound = self.compound_var.get()
        num_laps = self.laps_var.get()
        aggression = self.aggression_var.get()
        track_abrasion = self.track_abrasion_var.get()

        tyre = F1Tyre(compound=compound)

        self.output_text.insert(tk.END, "Tyre degradation simulation:\n\n")
        for lap in range(1, num_laps + 1):
            status = tyre.update(driving_aggression=aggression, track_abrasion=track_abrasion)
            lap_time = tyre.get_lap_time()
            #build lap report line
            status_msg = f"Lap {lap:2d}: Grip={status['grip']:.4f} Wear={status['wear']:.4f} "
            status_msg += f"Temp={status['temperature']:.1f}C Pressure={status['pressure']:.3f}bar LapTime={lap_time:.2f}s"
            if status['punctured']:
                status_msg += " [PUNCTURED]"
            self.output_text.insert(tk.END, status_msg + "\n")
            #Add to results
            row = status.copy()
            row['lap'] = lap
            row['lap_time'] = lap_time
            self.simulation_results.append(row)

            if status['punctured']:
                self.output_text.insert(tk.END, "\nTyre punctured! You are out of the race.\n")
                break

        self.output_text.config(state=tk.DISABLED)
        self.update_matplotlib_plots()

#Runs the final program 
if __name__ == "__main__":
    root = tk.Tk()
    root.state('zoomed')  # Full-screen start
    app = TyreSimulationGUI(root)
    root.mainloop()

